from fastapi import FastAPI

# routers
from routers.ask_ai import router as ai_router
from routers_chat import router as chat_router
from routers_farmers import router as farmers_router
from routers_market import router as market_router
from routers_weather import router as weather_router

app = FastAPI(title="AI Router API")

# include routers
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(farmers_router, prefix="/farmers", tags=["Farmers"])
app.include_router(market_router, prefix="/market", tags=["Market"])
app.include_router(weather_router, prefix="/weather", tags=["Weather"])


@app.get("/")
def root():
    return {"message": "API is running"}
