from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/detect-disease")
async def detect_disease(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Image received successfully"
    }
