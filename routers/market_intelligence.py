from fastapi import APIRouter, HTTPException, Query

from database import supabase


router = APIRouter()


# ============================================================
# MARKET INTELLIGENCE
#
# GET:
# /api/market-intelligence/{crop_slug}
#
# This backend uses the existing Supabase client from
# database.py.
#
# database.py is currently connected to:
#
# https://xmdjdxwsvvdxwizokhgs.supabase.co
#
# The actual Market Intelligence calculations remain inside
# Supabase PostgreSQL functions.
#
# ============================================================


@router.get("/market-intelligence/{crop_slug}")
async def get_market_intelligence(
    crop_slug: str,

    district: str | None = Query(
        None,
        description="Optional farmer district"
    ),

    market: str | None = Query(
        None,
        description="Optional market"
    ),

    price_type: str | None = Query(
        None,
        description="Optional price type"
    ),

    supply_pressure: str = Query(
        "unknown",
        description="Supply pressure: high, medium, low, or unknown"
    ),

    storage_risk: str = Query(
        "unknown",
        description="Storage risk: high, medium, low, or unknown"
    ),
):

    # ========================================================
    # VALIDATE CROP
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
        if district
        else None
    )

    market = (
        market.strip()
        if market
        else None
    )

    price_type = (
        price_type.strip().lower()
        if price_type
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
    # VALIDATE SUPPLY PRESSURE
    # ========================================================

    if supply_pressure not in {
        "high",
        "medium",
        "low",
        "unknown"
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid supply pressure. "
                "Use high, medium, low, or unknown."
            )
        )


    # ========================================================
    # VALIDATE STORAGE RISK
    # ========================================================

    if storage_risk not in {
        "high",
        "medium",
        "low",
        "unknown"
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid storage risk. "
                "Use high, medium, low, or unknown."
            )
        )


    # ========================================================
    # CALL EXISTING SUPABASE FUNCTION
    #
    # IMPORTANT:
    #
    # We call the HIGH-LEVEL function:
    #
    # generate_market_recommendation()
    #
    # It internally calls:
    #
    # get_market_price_context()
    # resolve_market_trend()
    # calculate_market_recommendation()
    # generate_market_explanation()
    #
    # ========================================================

    try:

        response = (
            supabase
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

        print(
            "============================================================"
        )

        print(
            "MARKET INTELLIGENCE RPC ERROR"
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
            "============================================================"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Market intelligence RPC failed.",
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
                "Market intelligence returned no response."
            )
        )


    print(
        "============================================================"
    )

    print(
        "MARKET INTELLIGENCE RESPONSE"
    )

    print(
        "============================================================"
    )

    print(
        f"Response type: {type(response.data).__name__}"
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
    # ========================================================

    result = response.data

    if not isinstance(result, dict):

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Invalid Market Intelligence response."
                ),
                "response_type": type(result).__name__,
                "response": str(result),
            }
        )


    # ========================================================
    # SUPABASE FUNCTION REPORTED NO DATA
    # ========================================================

    if result.get("status") == "no_market_data":

        raise HTTPException(
            status_code=404,
            detail=result
        )


    # ========================================================
    # RETURN TO FLUTTER
    # ========================================================

    return result
