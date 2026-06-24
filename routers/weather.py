from fastapi import APIRouter
from database import supabase

router = APIRouter()


# Get all weather alerts
@router.get("/weather-alerts")
async def get_weather_alerts():
    response = (
        supabase
        .table("weather_alerts")
        .select("*")
        .execute()
    )

    return response.data


# Get weather alerts for a region
@router.get("/weather-alerts/{region}")
async def get_region_weather(region: str):
    response = (
        supabase
        .table("weather_alerts")
        .select("*")
        .ilike("region", region)
        .execute()
    )

    return response.data
