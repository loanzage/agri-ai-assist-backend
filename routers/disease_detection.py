from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/detect-disease")
async def detect_disease(image: UploadFile = File(...)):
    return {
        "filename": image.filename,
        "content_type": image.content_type
    }
