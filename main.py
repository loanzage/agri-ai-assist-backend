from fastapi import FastAPI

# =========================
# ROUTERS IMPORTS
# =========================
from routers.ask_ai import router as ai_router
from routers.chat import router as chat_router
from routers.farmers import router as farmers_router
from routers.market import router as market_router
from routers.weather import router as weather_router
from routers.disease_detection import router as disease_router

# ✅ NEW: Marketplace router (ADDED)
from routers.marketplace import router as marketplace_router


# =========================
# APP INIT
# =========================
app = FastAPI(
    title="Agri AI Assist API",
    version="1.0.0"
)


# =========================
# ROUTER REGISTRATION
# =========================

# AI Chat
app.include_router(ai_router, prefix="/api", tags=["AI"])

# Chat History
app.include_router(chat_router, prefix="/api", tags=["Chat"])

# Farmers
app.include_router(farmers_router, prefix="/api", tags=["Farmers"])

# Market Prices
app.include_router(market_router, prefix="/api", tags=["Market"])

# Weather
app.include_router(weather_router, prefix="/api", tags=["Weather"])

# Disease Detection
app.include_router(disease_router, prefix="/api", tags=["Disease Detection"])

# ✅ NEW: Marketplace System
app.include_router(marketplace_router, prefix="/api", tags=["Marketplace"])


# =========================
# ROOT CHECK
# =========================
@app.get("/")
def root():
    return {
        "message": "Agri AI Assist Backend Running",
        "status": "healthy"
    }
