from fastapi import APIRouter
from pydantic import BaseModel

from ai_service import generate_luganda_explanation


router = APIRouter()


class LugandaRequest(BaseModel):
    disease: str
    crop: str = ""
    language: str = "Luganda"



@router.post("/luganda-explanation")
def luganda_explanation(
    request: LugandaRequest
):

    explanation = generate_luganda_explanation(
        disease=request.disease,
        crop=request.crop
    )


    return {
        "language": "Luganda",
        "explanation": explanation
    }
