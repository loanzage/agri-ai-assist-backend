from fastapi import APIRouter
from database import supabase

router = APIRouter()

Get all weather alerts

@router.get("/weather-alerts")
async def get_weather_alerts():

response = (
    supabase
    .table("weather_alerts")
    .select("*")
    .execute()
)

return response.data

Get weather alerts for a specific district

@router.get("/weather-alerts/{district}")
async def get_district_weather_alerts(district: str):

response = (
    supabase
    .table("weather_alerts")
    .select("*")
    .ilike("district", district)
    .execute()
)

return response.data