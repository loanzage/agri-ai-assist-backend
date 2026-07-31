from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from PIL import Image
import io
import json


from ai_service import (
    detect_crop_disease,
    generate_luganda_explanation
)


from database import supabase



router = APIRouter()





# =====================================================
# LUGANDA REQUEST MODEL
# =====================================================

class LugandaRequest(BaseModel):

    crop: str

    disease: str

    symptoms: str = ""

    causes: str = ""

    treatment: str = ""

    prevention: str = ""





# =====================================================
# DISEASE DETECTION
# =====================================================

@router.post("/detect-disease")
async def detect_disease(
        image: UploadFile = File(...)
):


    """
    Gemini Vision Crop Diagnosis

    Includes:

    - Smart diagnosis JSON
    - Knowledge base lookup
    - Scan history saving
    """



    # =========================
    # IMAGE VALIDATION
    # =========================


    try:

        contents = await image.read()


        img = Image.open(
            io.BytesIO(contents)
        )


        img.verify()


        img = Image.open(
            io.BytesIO(contents)
        )


    except Exception:


        return {

            "success": False,

            "message":
            "Invalid image. Upload a clear crop image."

        }





    # =========================
    # GEMINI VISION
    # =========================


    diagnosis_raw = detect_crop_disease(
        img
    )



    diagnosis_raw = (

        diagnosis_raw

        .replace(
            "```json",
            ""
        )

        .replace(
            "```",
            ""
        )

        .strip()

    )





    # =========================
    # JSON PARSE
    # =========================


    try:


        diagnosis = json.loads(
            diagnosis_raw
        )


    except Exception:


        diagnosis = {


            "crop":
            "Unknown",


            "status":
            "Uncertain",


            "disease":
            "Unknown",


            "confidence":
            "Low",


            "severity":
            "Unknown",


            "symptoms":
            diagnosis_raw,


            "causes":
            "",


            "treatment":
            "",


            "prevention":
            "",


            "recovery_time":
            "",


            "estimated_cost":
            ""

        }





    crop = diagnosis.get(
        "crop",
        "Unknown"
    )


    disease = diagnosis.get(
        "disease",
        "Unknown"
    )





    # =========================
    # LOW CONFIDENCE WARNING
    # =========================


    if diagnosis.get(
        "confidence",
        ""
    ).lower() == "low":


        diagnosis["treatment"] += (

            "\n\nUpload a clearer image "
            "showing affected leaves, fruits or stem."

        )







    # =========================
    # KNOWLEDGE BASE SEARCH
    # =========================


    rows = []



    try:


        if crop:


            response = (

                supabase

                .table(
                    "knowledge_base"
                )

                .select("*")

                .ilike(
                    "crop",
                    f"%{crop}%"
                )

                .execute()

            )


            rows.extend(
                response.data or []
            )





        if disease:


            response = (

                supabase

                .table(
                    "knowledge_base"
                )

                .select("*")

                .ilike(
                    "topic",
                    f"%{disease}%"
                )

                .execute()

            )


            rows.extend(
                response.data or []
            )



    except Exception as e:


        print(
            "Knowledge Base Error:",
            e
        )








    # =========================
    # REMOVE DUPLICATES
    # =========================


    unique_rows = []


    seen = set()



    for row in rows:


        key = (

            row.get("crop"),

            row.get("topic")

        )


        if key not in seen:


            seen.add(key)


            unique_rows.append(row)






    # =========================
    # FORMAT KNOWLEDGE BASE
    # =========================


    knowledge_base = []



    for row in unique_rows:


        knowledge_base.append({

            "crop":
            row.get("crop"),


            "topic":
            row.get("topic"),


            "causes":
            row.get(
                "causes_or_details"
            ),


            "treatment":
            row.get(
                "recommendations"
            ),


            "prevention":
            row.get(
                "prevention"
            ),


            "risk":
            row.get(
                "risk_level"
            )


        })







    # =========================
    # SAVE HISTORY
    # =========================


    try:


        supabase.table(
            "disease_history"
        ).insert({


            "user_id":
            "anonymous",


            "image_url":
            f"uploaded/{image.filename}",


            "crop":
            crop,


            "disease":
            disease,


            "confidence":
            diagnosis.get(
                "confidence",
                "Low"
            ),


        }).execute()



    except Exception as e:


        print(
            "History save failed:",
            e
        )








    # =========================
    # FINAL RESPONSE
    # =========================


    return {


        "success":
        True,


        "filename":
        image.filename,


        "diagnosis":
        diagnosis,



        "knowledge_base":
        knowledge_base,



        "source":
        "Gemini Vision + Agri AI Knowledge Base",



        "message":
        "Smart crop diagnosis completed."

    }








# =====================================================
# LUGANDA EXPLANATION ENDPOINT
# =====================================================


@router.post("/luganda-explanation")
async def luganda_explanation(
        request: LugandaRequest
):


    """
    Generate complete Luganda explanation
    from Gemini AI.
    """



    explanation = generate_luganda_explanation(


        crop=request.crop,


        disease=request.disease,


        symptoms=request.symptoms,


        causes=request.causes,


        treatment=request.treatment,


        prevention=request.prevention


    )



    return {


        "success":
        True,


        "language":
        "Luganda",


        "explanation":
        explanation


    }
