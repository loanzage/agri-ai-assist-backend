from fastapi import APIRouter
from database import supabase

router = APIRouter()

@router.post("/list-crop")
async def list_crop(data: dict):

    response = supabase.table("crop_listings").insert({
        "farmer_id": data["farmer_id"],
        "crop": data["crop"],
        "quantity": data["quantity"],
        "price_per_unit": data["price_per_unit"],
        "location": data.get("location", ""),
        "status": "available"
    }).execute()

    return {"message": "Crop listed successfully"}
