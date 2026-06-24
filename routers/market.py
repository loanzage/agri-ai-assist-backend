from fastapi import APIRouter
from database import supabase

router = APIRouter()

# Get all market prices
@router.get("/market-prices")
async def get_market_prices():
    response = (
        supabase
        .table("market_prices")
        .select("*")
        .execute()
    )

    return response.data


# Get market prices for a specific crop
@router.get("/market-prices/{crop}")
async def get_crop_market_price(crop: str):
    response = (
        supabase
        .table("market_prices")
        .select("*")
        .ilike("crop", crop)
        .execute()
    )

    return response.data
