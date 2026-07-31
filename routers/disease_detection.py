from fastapi import APIRouter, UploadFile, File
from PIL import Image
import io
import json

from ai_service import detect_crop_disease
from database import supabase

router = APIRouter()


@router.post("/detect-disease")
async def detect_disease(image: UploadFile = File(...)):
    """
    Detect crop diseases using Gemini Vision
    + Local Knowledge Base (RAG)
    + Save scan history
    """

    # =========================
    # STEP 1: VALIDATE IMAGE
    # =========================

    try:
        contents = await image.read()

        img = Image.open(io.BytesIO(contents))
        img.verify()

        img = Image.open(io.BytesIO(contents))

    except Exception:
        return {
            "success": False,
            "message": "Invalid image uploaded. Please upload a clear crop image."
        }

    # =========================
    # STEP 2: GEMINI VISION
    # =========================

    diagnosis_raw = detect_crop_disease(img)

    # Remove markdown if Gemini returns ```json
    diagnosis_raw = (
        diagnosis_raw
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

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

    crop = diagnosis.get("crop", "").strip()
    disease = diagnosis.get("disease", "").strip()

    # =========================
    # STEP 4: LOW CONFIDENCE CHECK
    # =========================

    confidence = diagnosis.get(
        "confidence",
        "Low"
    ).lower()

    if confidence == "low":

        diagnosis["recommendations"] = (
            diagnosis.get("recommendations", "")
            + "\n\nPlease upload a clearer close-up image of the affected leaves, stem, fruit or entire plant."
        )

    # =========================
    # STEP 5: SUPABASE RAG LOOKUP
    # =========================

    rows = []

    try:

        # Search crop

        if crop:

            response = (
                supabase
                .table("knowledge_base")
                .select("*")
                .ilike("crop", f"%{crop}%")
                .execute()
            )

            rows.extend(response.data or [])

        # Search disease/topic

        if disease:

            response = (
                supabase
                .table("knowledge_base")
                .select("*")
                .ilike("topic", f"%{disease}%")
                .execute()
            )

            rows.extend(response.data or [])

    except Exception as e:

        print("SUPABASE LOOKUP ERROR:", e)

    # =========================
    # REMOVE DUPLICATES
    # =========================

    unique_rows = []

    seen = set()

    for r in rows:

        key = (
            r.get("crop"),
            r.get("topic")
        )

        if key not in seen:

            seen.add(key)

            unique_rows.append(r)

    # =========================
    # STEP 6: FORMAT KNOWLEDGE
    # =========================

    knowledge_base = []

    for r in unique_rows:

        knowledge_base.append({

            "crop":
                r.get("crop"),

            "topic":
                r.get("topic"),

            "causes":
                r.get("causes_or_details"),

            "recommendations":
                r.get("recommendations"),

            "risk":
                r.get("risk_level")

        })

    # =========================
    # STEP 7: SAVE HISTORY
    # =========================

    image_url = f"uploaded/{image.filename}"

    try:

        supabase.table(
            "disease_history"
        ).insert({

            "user_id":
                "anonymous",

            "image_url":
                image_url,

            "crop":
                crop,

            "disease":
                disease,

            "confidence":
                diagnosis.get(
                    "confidence",
                    "Low"
                )

        }).execute()

    except Exception as e:

        print("History save failed:", e)

    # =========================
    # STEP 8: FINAL RESPONSE
    # =========================

    return {

        "success": True,

        "filename":
            image.filename,

        "diagnosis":
            diagnosis,

        "knowledge_base":
            knowledge_base,

        "source":
            "Gemini Vision + Local Knowledge Base",

        "message":
            "Disease analysis completed successfully."

    }
