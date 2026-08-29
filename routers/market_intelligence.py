import os

from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# OLD / LEGACY SUPABASE DATABASE
#
# Market Intelligence continues to use the existing
# database where the market tables and RPC functions already
# exist.
#
# Project:
# xmdjdxwsvvdxwizokhgs
# ============================================================

LEGACY_SUPABASE_URL = (
    "https://xmdjdxwsvvdxwizokhgs.supabase.co"
)

LEGACY_SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not LEGACY_SUPABASE_KEY:
    raise Exception(
        "SUPABASE_KEY is missing in environment variables!"
    )


# ============================================================
# LEGACY SUPABASE CLIENT
# ============================================================

legacy_supabase = create_client(
    LEGACY_SUPABASE_URL,
    LEGACY_SUPABASE_KEY
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# MARKET INTELLIGENCE
#
# GET:
#
# /api/market-intelligence/{crop_slug}
#
# Example:
#
# /api/market-intelligence/beans
#
# Optional parameters:
#
# district
# market
# price_type
# supply_pressure
# storage_risk
#
# This calls:
#
# generate_market_recommendation(
#     p_crop_slug,
#     p_district,
#     p_market,
#     p_price_type,
#     p_supply_pressure,
#     p_storage_risk
# )
#
# from the OLD Supabase database.
# ============================================================

@router.get("/market-intelligence/{crop_slug}")
async def get_market_intelligence(
    crop_slug: str,

    district: str | None = Query(
        None,
        description="District used to select the market observation"
    ),

    market: str | None = Query(
        None,
        description="Market used to select the market observation"
    ),

    price_type: str | None = Query(
        None,
        description="Price type such as wholesale or retail"
    ),

    supply_pressure: str = Query(
        "unknown",
        description=(
            "Supply pressure: high, medium, low, or unknown"
        )
    ),

    storage_risk: str = Query(
        "unknown",
        description=(
            "Storage risk: high, medium, low, or unknown"
        )
    ),
):

    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    if not crop_slug or not crop_slug.strip():

        raise HTTPException(
            status_code=400,
            detail="Crop slug is required."
        )


    # ========================================================
    # NORMALIZE INPUTS
    # ========================================================

    crop_slug = crop_slug.strip().lower()

    district = (
        district.strip()
        if district and district.strip()
        else None
    )

    market = (
        market.strip()
        if market and market.strip()
        else None
    )

    price_type = (
        price_type.strip().lower()
        if price_type and price_type.strip()
        else None
    )

    supply_pressure = (
        supply_pressure.strip().lower()
        if supply_pressure
        else "unknown"
    )

    storage_risk = (
        storage_risk.strip().lower()
        if storage_risk
        else "unknown"
    )


    # ========================================================
    # NORMALIZE SUPPLY PRESSURE
    # ========================================================

    if supply_pressure not in (
        "high",
        "medium",
        "low",
        "unknown"
    ):

        supply_pressure = "unknown"


    # ========================================================
    # NORMALIZE STORAGE RISK
    # ========================================================

    if storage_risk not in (
        "high",
        "medium",
        "low",
        "unknown"
    ):

        storage_risk = "unknown"


    # ========================================================
    # CALL OLD DATABASE RPC
    #
    # IMPORTANT:
    #
    # We deliberately call the HIGH-LEVEL function
    # generate_market_recommendation().
    #
    # That function already:
    #
    # 1. Gets market price context
    # 2. Finds latest observation
    # 3. Finds previous observation
    # 4. Calculates price change
    # 5. Resolves trend
    # 6. Calculates recommendation score
    # 7. Generates explanation
    # 8. Saves recommendation
    # 9. Returns farmer-facing recommendation
    #
    # Therefore FastAPI does not duplicate any of
    # that business logic.
    # ========================================================

    try:

        response = (
            legacy_supabase
            .rpc(
                "generate_market_recommendation",
                {
                    "p_crop_slug": crop_slug,
                    "p_district": district,
                    "p_market": market,
                    "p_price_type": price_type,
                    "p_supply_pressure": supply_pressure,
                    "p_storage_risk": storage_risk,
                }
            )
            .execute()
        )

    except Exception as e:

        # ====================================================
        # LOG DATABASE ERROR
        # ====================================================

        print(
            "============================================================"
        )

        print(
            "MARKET INTELLIGENCE LEGACY DATABASE ERROR"
        )

        print(
            "============================================================"
        )

        print(
            f"Exception type: {type(e).__name__}"
        )

        print(
            f"Exception: {str(e)}"
        )

        print(
            f"Crop: {crop_slug}"
        )

        print(
            f"District: {district}"
        )

        print(
            f"Market: {market}"
        )

        print(
            f"Price type: {price_type}"
        )

        print(
            "============================================================"
        )


        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Market intelligence database request failed."
                ),
                "error_type": type(e).__name__,
                "error": str(e),
            }
        )


    # ========================================================
    # VALIDATE RESPONSE
    # ========================================================

    if response is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Market intelligence returned no database response."
            )
        )


    # ========================================================
    # DEBUG RESPONSE
    # ========================================================

    print(
        "============================================================"
    )

    print(
        "MARKET INTELLIGENCE LEGACY DATABASE RESPONSE"
    )

    print(
        "============================================================"
    )

    print(
        f"Response data type: "
        f"{type(response.data).__name__}"
    )

    print(
        f"Response data: {response.data}"
    )

    print(
        "============================================================"
    )


    # ========================================================
    # NO DATA
    # ========================================================

    if response.data is None:

        raise HTTPException(
            status_code=404,
            detail={
                "status": "no_market_data",
                "crop_slug": crop_slug,
                "district": district,
                "market": market,
                "price_type": price_type,
            }
        )


    # ========================================================
    # JSONB VALIDATION
    #
    # generate_market_recommendation() RETURNS jsonb.
    #
    # Supabase Python client normally converts this into
    # a Python dictionary.
    # ========================================================

    result = response.data


    if not isinstance(result, dict):

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Invalid market intelligence response."
                ),
                "response_type": type(result).__name__,
                "response": str(result),
            }
        )


    # ========================================================
    # RETURN TO FLUTTER
    # ========================================================

    return result
