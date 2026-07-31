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
# REQUEST MODEL FOR LUGANDA EXPLANATION
# =====================================================


class LugandaRequest(BaseModel):

    crop: str

    disease: str

    symptoms: str = ""

    causes: str = ""

    treatment: str = ""

    prevention: str = ""





# =====================================================
# DISEASE DETECTION ENDPOINT
# =====================================================


@router.post("/detect-disease")
async def detect_disease(
        image: UploadFile = File(...)
):


    """
    Detect crop diseases using:

    Gemini Vision
    +
    Supabase Knowledge Base
    +
    Save History

    """



    # =========================
    # VALIDATE IMAGE
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
            "Invalid image. Please upload a clear crop photo."

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
    # PARSE JSON
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


            "symptoms":
            diagnosis_raw,


            "causes":
            "",


            "treatment":
            "",


            "recommendations":
            "",


            "prevention":
            ""

        }





    crop = diagnosis.get(
        "crop",
        ""
    )


    disease = diagnosis.get(
        "disease",
        ""
    )





    # =========================
    # LOW CONFIDENCE MESSAGE
    # =========================


    if diagnosis.get(
        "confidence",
        ""
    ).lower() == "low":



        diagnosis["recommendations"] += (

            "\n\nPlease upload a clearer image "
            "showing affected leaves or fruits."

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
            "Knowledge base error:",
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



            "recommendations":
            row.get(
                "recommendations"
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
            )


        }).execute()



    except Exception as e:


        print(
            "History save failed:",
            e
        )







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
        "Disease analysis completed."

    }








# =====================================================
# LUGANDA EXPLANATION ENDPOINT
# =====================================================


@router.post("/luganda-explanation")
async def luganda_explanation(
        request: LugandaRequest
):


    """
    Generate full Luganda agricultural explanation
    using Gemini AI.
    """



    explanation = generate_luganda_explanation(


        disease=request.disease,


        crop=request.crop,


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
