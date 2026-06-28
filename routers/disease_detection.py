from fastapi import APIRouter, UploadFile, File
from PIL import Image
import io

from ai_service import detect_crop_disease

router = APIRouter()


@router.post("/detect-disease")
async def detect_disease(image: UploadFile = File(...)):

    # Read uploaded image
    contents = await image.read()

    # Open image using Pillow
    img = Image.open(io.BytesIO(contents))

    # Analyze image with Gemini Vision
    diagnosis = detect_crop_disease(img)

    return {
        "filename": image.filename,
        "content_type": image.content_type,
        "diagnosis": diagnosis
    }
