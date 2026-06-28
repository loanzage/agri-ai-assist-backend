from fastapi import APIRouter, UploadFile, File
from PIL import Image
import io
import json

from ai_service import detect_crop_disease
from database import supabase

router = APIRouter()


@router.post("/detect-disease")
async def detect_disease(image: UploadFile = File(...)):

    # =========================
    # STEP 1: READ IMAGE
    # =========================
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))

    # =========================
    # STEP 2: GEMINI VISION ANALYSIS
    # =========================
    diagnosis_raw = detect_crop_disease(img)

    # =========================
    # STEP 3: SAFE JSON PARSE
    # =========================
    try:
        diagnosis = json.loads(diagnosis_raw)
    except Exception:
        diagnosis = {
            "crop": "Unknown",
            "disease": "Unknown",
            "confidence": "Low",
            "symptoms": diagnosis_raw,
            "causes": "",
            "recommendations": "",
            "prevention": ""
        }

    # =========================
    # STEP 4: SUPABASE RAG LOOKUP
    # =========================
    crop = diagnosis.get("crop", "")
    disease = diagnosis.get("disease", "")

    # Try crop match first
    kb_response = (
        supabase
        .table("knowledge_base")
        .select("*")
        .ilike("crop", crop)
        .execute()
    )

    rows = kb_response.data or []

    # fallback → disease match
    if not rows:
        kb_response = (
            supabase
            .table("knowledge_base")
            .select("*")
            .ilike("topic", disease)
            .execute()
        )
        rows = kb_response.data or []

    # =========================
    # STEP 5: FORMAT KNOWLEDGE BASE
    # =========================
    knowledge_base = []

    for r in rows:
        knowledge_base.append({
            "crop": r.get("crop"),
            "topic": r.get("topic"),
            "causes": r.get("causes_or_details"),
            "recommendations": r.get("recommendations"),
            "risk": r.get("risk_level")
        })

    # =========================
    # STEP 6: OPTIONAL IMAGE PATH
    # =========================
    image_url = f"uploaded/{image.filename}"

    # =========================
    # STEP 7: SAVE TO HISTORY TABLE
    # =========================
    supabase.table("disease_history").insert({
        "user_id": "anonymous",  # later replace with auth
        "image_url": image_url,
        "crop": crop,
        "disease": disease,
        "confidence": diagnosis.get("confidence", "Low")
    }).execute()

    # =========================
    # STEP 8: FINAL RESPONSE
    # =========================
    return {
        "filename": image.filename,
        "diagnosis": diagnosis,
        "knowledge_base": knowledge_base
        }
