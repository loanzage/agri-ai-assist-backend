from fastapi import FastAPI

from routers.ask_ai import router as ai_router
from routers.farmers import router as farmers_router
from routers.market import router as market_router
from routers.weather import router as weather_router
from routers.chat import router as chat_router

app = FastAPI(
title="Agri AI Assist API",
version="1.0.0"
)

AI Router

app.include_router(ai_router, prefix="/api", tags=["AI"])

Farmers Router

app.include_router(farmers_router, prefix="/api", tags=["Farmers"])

Market Router

app.include_router(market_router, prefix="/api", tags=["Market"])

Weather Router

app.include_router(weather_router, prefix="/api", tags=["Weather"])

Chat Router

app.include_router(chat_router, prefix="/api", tags=["Chat"])

@app.get("/")
def root():
return {
"message": "Agri AI Assist Backend Running",
"status": "healthy"
}