from fastapi import FastAPI


# =========================
# ROUTERS IMPORTS
# =========================

from routers.ask_ai import router as ai_router
from routers.chat import router as chat_router
from routers.farmers import router as farmers_router
from routers.market import router as market_router
from routers.market_intelligence import router as market_intelligence_router
from routers.weather import router as weather_router
from routers.disease_detection import router as disease_router
from routers.coffee_grading import router as coffee_grading_router
from routers.marketplace import router as marketplace_router
from routers.payments import router as payment_router
from routers.webhooks import router as webhook_router


# =========================
# LUGANDA ROUTER
# =========================

from routers.luganda import router as luganda_router


# =========================
# ACCOUNT MANAGEMENT ROUTER
# =========================

from routers.account import router as account_router


# =========================
# APP INIT
# =========================

app = FastAPI(

    title="Agri AI Assist API",

    version="1.0.0"

)


# =========================
# ROUTERS
# =========================


# =========================================================
# AI CHAT
# =========================================================

app.include_router(

    ai_router,

    prefix="/api",

    tags=["AI"]

)


# =========================================================
# CHAT HISTORY
# =========================================================

app.include_router(

    chat_router,

    prefix="/api",

    tags=["Chat"]

)


# =========================================================
# FARMERS
# =========================================================

app.include_router(

    farmers_router,

    prefix="/api",

    tags=["Farmers"]

)


# =========================================================
# MARKET
# =========================================================

app.include_router(

    market_router,

    prefix="/api",

    tags=["Market"]

)


# =========================================================
# MARKET INTELLIGENCE
#
# AI-powered crop price analysis and
# farmer selling recommendations.
#
# This router retrieves market intelligence
# from the legacy Supabase database configured
# inside routers/market_intelligence.py.
# =========================================================

app.include_router(

    market_intelligence_router,

    prefix="/api",

    tags=["Market Intelligence"]

)


# =========================================================
# WEATHER
# =========================================================

app.include_router(

    weather_router,

    prefix="/api",

    tags=["Weather"]

)


# =========================================================
# DISEASE DETECTION
# =========================================================

app.include_router(

    disease_router,

    prefix="/api",

    tags=["Disease Detection"]

)

# =========================================================
# COFFEE BEAN VISUAL GRADING
# =========================================================

app.include_router(
    coffee_grading_router,
    prefix="/api",
    tags=["Coffee Grading"]
)


# =========================================================
# MARKETPLACE
# =========================================================

app.include_router(

    marketplace_router,

    prefix="/api",

    tags=["Marketplace"]

)


# =========================================================
# PAYMENTS
# =========================================================

app.include_router(

    payment_router,

    prefix="/api",

    tags=["Payments"]

)


# =========================================================
# WEBHOOKS
# =========================================================

app.include_router(

    webhook_router,

    prefix="/api",

    tags=["Webhooks"]

)


# =========================================================
# LUGANDA AI EXPLANATION
# =========================================================

app.include_router(

    luganda_router,

    prefix="/api",

    tags=["Translation"]

)


# =========================================================
# ACCOUNT MANAGEMENT
# =========================================================

app.include_router(

    account_router,

    prefix="/api",

    tags=["Account"]

)


# =========================
# ROOT CHECK
# =========================

@app.get("/")

def root():

    return {

        "message":
        "Agri AI Assist Backend Running",

        "status":
        "healthy"

    }
