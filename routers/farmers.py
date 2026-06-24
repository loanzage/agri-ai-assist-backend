from fastapi import APIRouter
from database import supabase
from schemas import FarmerCreate

router = APIRouter()

Get all farmers

@router.get("/farmers")
async def get_farmers():

response = (
    supabase
    .table("farmers")
    .select("*")
    .execute()
)

return response.data

Get one farmer by ID

@router.get("/farmers/{farmer_id}")
async def get_farmer(farmer_id: int):

response = (
    supabase
    .table("farmers")
    .select("*")
    .eq("id", farmer_id)
    .execute()
)

return response.data

Create a farmer

@router.post("/farmers")
async def create_farmer(data: FarmerCreate):

response = (
    supabase
    .table("farmers")
    .insert({
        "name": data.name,
        "region": data.region,
        "farm_size": data.farm_size,
        "crops": data.crops
    })
    .execute()
)

return response.data
