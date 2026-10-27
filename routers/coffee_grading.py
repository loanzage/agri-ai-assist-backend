"""Coffee bean visual grading endpoint for preliminary AI screening."""
import io
import json
import logging
import os
import re
import time
from collections import defaultdict, deque
from threading import Lock
from typing import List

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from ai_service import model
from database import auth_supabase

router = APIRouter()
logger = logging.getLogger(__name__)
MAX_IMAGES = 5
MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 25_000_000
_RATE_WINDOW_SECONDS = 600
_RATE_LIMIT = 10
_RATE_LOCK = Lock()
_USER_REQUESTS = defaultdict(deque)


def _check_user_rate_limit(user_id: str) -> None:
    """Best-effort in-process rate guard; deployments should also monitor Gemini usage."""
    now = time.monotonic()
    with _RATE_LOCK:
        timestamps = _USER_REQUESTS[user_id]
        while timestamps and now - timestamps[0] >= _RATE_WINDOW_SECONDS:
            timestamps.popleft()
        if len(timestamps) >= _RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Coffee grading request limit reached. Please try again in a few minutes.")
        timestamps.append(now)


def _parse_report(text: str) -> dict:
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        value = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=502, detail="AI returned an unreadable grading report. Please retry.")
    if not isinstance(value, dict):
        raise HTTPException(status_code=502, detail="AI returned an unexpected report format. Please retry.")
    return value


def _prepare_image(data: bytes, filename: str) -> Image.Image:
    if not data:
        raise HTTPException(status_code=400, detail=f"{filename}: image is empty.")
    try:
        with Image.open(io.BytesIO(data)) as check:
            check.verify()
        with Image.open(io.BytesIO(data)) as opened:
            width, height = opened.size
            if width < 1 or height < 1 or width * height > MAX_PIXELS:
                raise HTTPException(status_code=413, detail=f"{filename}: image dimensions are too large.")
            opened.load()
            image = opened.convert("RGB")
            image.thumbnail((1600, 1600))
            return image
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(status_code=400, detail=f"{filename}: invalid image. Use a clear JPG, PNG, or WEBP photo.")


def _safe_grade(report: dict) -> None:
    raw = str(report.get("overall_grade", "")).strip().lower()
    if raw == "a":
        report["overall_grade"] = "A (preliminary visual estimate)"
    elif raw == "b":
        report["overall_grade"] = "B (preliminary visual estimate)"
    elif raw == "c":
        report["overall_grade"] = "C (preliminary visual estimate)"
    else:
        report["overall_grade"] = "Unable to grade from these images"
    confidence = str(report.get("confidence", "Low")).strip().capitalize()
    report["confidence"] = confidence if confidence in {"High", "Medium", "Low"} else "Low"


@router.get("/grade-coffee/health")
def coffee_grading_health():
    configured = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "service": "coffee-grading",
        "status": "ready" if configured else "needs_configuration",
        "model": "gemini-2.5-flash",
        "gemini_configured": configured,
        "grading_type": "preliminary visual screening only",
    }


@router.post("/grade-coffee")
async def grade_coffee(
    images: List[UploadFile] = File(..., description="One to five photos of one coffee sample"),
    lang: str = Form("english"),
    authorization: str | None = Header(default=None),
):
    """Assess visible coffee sample characteristics with the existing Gemini Vision model."""
    if not 1 <= len(images) <= MAX_IMAGES:
        raise HTTPException(status_code=422, detail="Upload between 1 and 5 images of the same sample.")
    language = lang.strip().lower()
    if language not in {"english", "en", "luganda", "lg"}:
        raise HTTPException(status_code=422, detail="Language must be English or Luganda.")
    language = "Luganda" if language in {"luganda", "lg"} else "English"

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Sign in before using coffee grading.")
    access_token = authorization[len("Bearer "):].strip()
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing access token.")
    if auth_supabase is None:
        raise HTTPException(
            status_code=503,
            detail="Coffee grading authentication is not configured on the server.",
        )
    try:
        user_response = auth_supabase.auth.get_user(access_token)
        user = user_response.user
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired sign-in session. Please sign in again.",
        )
    if user is None:
        raise HTTPException(status_code=401, detail="Authenticated user not found.")
    _check_user_rate_limit(str(user.id))

    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="AI grading is not configured. Set GEMINI_API_KEY in the backend environment.")

    pil_images = []
    try:
        for upload in images:
            filename = upload.filename or "coffee-image"
            data = await upload.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise HTTPException(status_code=413, detail=f"{filename}: each image must be 10 MB or smaller.")
            pil_images.append(_prepare_image(data, filename))

        language_instruction = (
            "Write explanatory text in simple Luganda. Keep JSON keys and overall_grade values in English."
            if language == "Luganda"
            else "Write explanatory text in clear English for a Ugandan farmer."
        )
        prompt = f"""
You are Agri AI Assist's coffee-bean visual screening assistant for Ugandan farmers and cooperatives.
Assess the SAME coffee sample across all attached images.

{language_instruction}

Be conservative and truthful. This is preliminary visual assessment only, not official UCDA, UNBS, export, or buyer certification. Photographs cannot establish moisture percentage, cup/flavour quality, screen size, exact variety, chemical residues, mycotoxins, or regulatory compliance. Never invent measurements, defect counts, scores, certification, market prices, or safety claims. Do not guess Robusta vs Arabica from an ordinary photograph; choose mixed/uncertain unless the image contains reliable distinguishing evidence.
If beans are not clearly visible, the sample is not recognisably coffee, or photo quality is poor, choose overall_grade "Unable to grade" and confidence "Low". Do not claim mould or contamination are absent; describe only what is visible.
Use A/B/C as qualitative visual categories only: A means relatively clean and uniform in the supplied views; B means mixed visible quality or some defects; C means multiple/prominent visible defects or poor uniformity. These are not trade-grade classes.

Return ONLY valid JSON with these keys:
{{
  "sample_type": "green/unroasted, dried cherry/parchment, roasted, or unable to determine",
  "coffee_type": "Robusta, Arabica, mixed/uncertain, or unable to determine",
  "overall_grade": "A, B, C, or Unable to grade",
  "confidence": "High, Medium, or Low",
  "visual_quality_summary": "brief summary of visible evidence",
  "visible_defects": [{{"defect": "visible defect or concern", "severity": "low, medium, high, or not assessable", "evidence": "what is actually visible"}}],
  "bean_uniformity": "good, fair, poor, or not assessable",
  "visible_foreign_matter": "observed, not observed in visible areas, or not assessable",
  "mould_or_insect_damage": "observed, suspected, not visible in supplied views, or not assessable",
  "limitations": ["attributes that cannot be confirmed from photos"],
  "recommended_next_steps": ["practical checking or improvement steps"],
  "grading_basis": "preliminary visual screening only"
}}
Return JSON only.
"""
        response = model.generate_content(
            [prompt, *pil_images],
            generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
        )
        report = _parse_report(getattr(response, "text", "") or "")
        _safe_grade(report)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Coffee grading Gemini request failed")
        raise HTTPException(status_code=502, detail="AI grading could not complete the request. Please retry shortly.")
    finally:
        for upload in images:
            await upload.close()

    report["grading_basis"] = (
        "Preliminary visual screening from images only. Not a certified UCDA, UNBS, export, or buyer grade. Confirm commercial quality using physical defect counting, suitable moisture measurement, and cupping by a qualified grader."
        if language == "English"
        else "Okukebera okw'obulabi okuva ku bifaananyi byokka; si kigero ekikakasiddwa ekya UCDA, UNBS, ebifulumizibwa ebweru oba omuguzi. Kakasa omutindo ng'ebikyamu bibaliddwa, obunnyogovu bupimiddwa, era coffee egezeseddwa omukugu."
    )
    return {
        "success": True,
        "language": language.lower(),
        "images_analyzed": len(pil_images),
        "report": report,
        "source": "Gemini Vision â€” preliminary visual screening",
        "message": "Coffee visual screening completed. This is not a certified commercial grade.",
    }