from fastapi import APIRouter, UploadFile, File
from PIL import Image
import io

router = APIRouter()


@router.post("/detect-disease")
async def detect_disease(image: UploadFile = File(...)):
    # Read uploaded image
    contents = await image.read()

    # Open image using Pillow
    img = Image.open(io.BytesIO(contents))

    # Get image dimensions
    width, height = img.size

    return {
        "filename": image.filename,
        "content_type": image.content_type,
        "width": width,
        "height": height
    }
