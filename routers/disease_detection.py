from fastapi import APIRouter

router = APIRouter()

@router.get("/detect-disease")
async def test():
    return {
        "status": "Disease Detection API Working"
    }
