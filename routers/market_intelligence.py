import os
from datetime import datetime
from zoneinfo import ZoneInfo

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

LEGACY_SUPABASE_KEY = os.getenv("LEGACY_SUPABASE_KEY")


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

# ============================================================
# HISTORICAL MARKET DATA
#
# These endpoints read historical World Bank RTFP data
# from the legacy Supabase database.
#
# They do not modify or replace live market intelligence.
# Supported crops: maize, beans, sorghum.
# ============================================================

HISTORICAL_SUPPORTED_CROPS = {
    "maize",
    "beans",
    "sorghum",
}


def validate_historical_crop(crop_slug: str) -> str:
    crop = crop_slug.strip().lower()

    if crop not in HISTORICAL_SUPPORTED_CROPS:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported historical crop.",
                "supported_crops": sorted(
                    HISTORICAL_SUPPORTED_CROPS
                ),
            },
        )

    return crop


# ============================================================
# GET HISTORICAL MARKETS
#
# GET /api/historical-markets/{crop_slug}
#
# Returns market coverage and dataset freshness metadata.
# ============================================================

@router.get("/historical-markets/{crop_slug}")
async def get_historical_markets(crop_slug: str):

    crop_slug = validate_historical_crop(crop_slug)

    try:
        response = (
            legacy_supabase
            .rpc(
                "get_historical_market_list",
                {
                    "p_crop_slug": crop_slug,
                },
            )
            .execute()
        )

    except Exception as e:
        print(
            "HISTORICAL MARKET LIST ERROR:",
            type(e).__name__,
            str(e),
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve historical market data.",
        )

    data = response.data

    if data is None:
        data = []

    if not isinstance(data, list):
        raise HTTPException(
            status_code=502,
            detail="Invalid historical market list response.",
        )

    return {
        "status": "success",
        "crop_slug": crop_slug,
        "count": len(data),
        "markets": data,
    }


# ============================================================
# GET HISTORICAL MARKET PRICE SERIES
#
# GET /api/historical-market-series/{crop_slug}/{market_geo_id}
#
# Returns historical monthly reference prices and metadata.
# ============================================================

@router.get(
    "/historical-market-series/{crop_slug}/{market_geo_id}"
)
async def get_historical_market_series(
    crop_slug: str,
    market_geo_id: str,
):

    crop_slug = validate_historical_crop(crop_slug)

    market_geo_id = market_geo_id.strip()

    if (
        not market_geo_id.startswith("gid_")
        or not market_geo_id[4:].isalnum()
        or len(market_geo_id) > 100
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid market_geo_id.",
        )

    try:
        response = (
            legacy_supabase
            .rpc(
                "get_historical_market_price_series",
                {
                    "p_crop_slug": crop_slug,
                    "p_market_geo_id": market_geo_id,
                },
            )
            .execute()
        )

    except Exception as e:
        print(
            "HISTORICAL MARKET SERIES ERROR:",
            type(e).__name__,
            str(e),
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve historical price series.",
        )

    data = response.data

    if data is None:
        data = []

    if not isinstance(data, list):
        raise HTTPException(
            status_code=502,
            detail="Invalid historical price series response.",
        )

    return {
        "status": "success",
        "crop_slug": crop_slug,
        "market_geo_id": market_geo_id,
        "count": len(data),
        "observations": data,
        "data_type": "historical_reference_estimates",
        "warning": (
            "Historical reference estimates are not current "
            "farm-gate market quotations."
        ),
    }


# ============================================================
# COFFEE MARKET PRICES
#
# GET /api/coffee-market-prices
# GET /api/coffee-market-prices?grade=kiboko
#
# Reads official MAAIF coffee farm-gate observations.
# Does not use the World Bank historical reference dataset.
# ============================================================

@router.get("/coffee-market-prices")
async def get_coffee_market_prices(
    grade: str | None = Query(
        None,
        description="Optional coffee grade: faq, kiboko, arabica_parchment, drugar",
    ),
    limit: int = Query(
        90,
        ge=1,
        le=365,
        description="Maximum observations returned per grade",
    ),
):
    coffee_grades = {
        "faq": "FAQ",
        "kiboko": "Kiboko",
        "arabica_parchment": "Arabica Parchment",
        "drugar": "Drugar",
    }

    requested_grade = grade.strip().lower() if grade else None

    if requested_grade and requested_grade not in coffee_grades:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported coffee grade.",
                "supported_grades": list(coffee_grades.keys()),
            },
        )

    selected_grades = (
        [requested_grade]
        if requested_grade
        else list(coffee_grades.keys())
    )

    try:
        source_response = (
            legacy_supabase
            .table("market_price_sources")
            .select(
                "name,organization,source_url,source_type,"
                "update_frequency,reliability_score,is_active,max_age_days"
            )
            .eq("name", "MAAIF Coffee")
            .maybe_single()
            .execute()
        )

        source = source_response.data

        if not source:
            raise HTTPException(
                status_code=503,
                detail="MAAIF Coffee source is not registered.",
            )

        # Read all available observations in pages, so the distinct-date
        # count is not limited to the observations returned to the UI.
        all_rows = []
        page_start = 0
        page_size = 1000

        while True:
            response = (
                legacy_supabase
                .table("market_price_observations")
                .select(
                    "grade,price,min_price,max_price,currency,unit,"
                    "observed_date,confidence,is_estimated,trend,notes,"
                    "source_url,market,district,region"
                )
                .eq("crop_slug", "coffee")
                .eq("source_name", "MAAIF Coffee")
                .eq("price_type", "farm_gate_weekly")
                .order("observed_date", desc=True)
                .range(page_start, page_start + page_size - 1)
                .execute()
            )

            batch = response.data or []
            all_rows.extend(batch)

            if len(batch) < page_size:
                break

            page_start += page_size

        today = datetime.now(
            ZoneInfo("Africa/Kampala")
        ).date()

        max_age_days = int(source.get("max_age_days") or 3)
        source_active = bool(source.get("is_active"))

        def serialize_observation(row):
            return {
                "grade": row.get("grade"),
                "price": row.get("price"),
                "min_price": row.get("min_price"),
                "max_price": row.get("max_price"),
                "currency": row.get("currency") or "UGX",
                "unit": row.get("unit") or "kg",
                "observed_date": row.get("observed_date"),
                "confidence": row.get("confidence"),
                "is_estimated": row.get("is_estimated"),
                "trend": row.get("trend"),
                "notes": row.get("notes"),
                "market": row.get("market"),
                "district": row.get("district"),
                "region": row.get("region"),
                "source_url": row.get("source_url"),
            }

        grade_results = []

        for grade_key in selected_grades:
            grade_rows = [
                row for row in all_rows
                if row.get("grade") == grade_key
                and row.get("observed_date")
            ]

            grade_rows.sort(
                key=lambda row: str(row.get("observed_date")),
                reverse=True,
            )

            distinct_dates = {
                str(row["observed_date"])
                for row in grade_rows
            }

            latest_row = grade_rows[0] if grade_rows else None

            age_days = None
            freshness = "unavailable"

            if latest_row:
                latest_date = datetime.strptime(
                    str(latest_row["observed_date"])[:10],
                    "%Y-%m-%d",
                ).date()

                age_days = (today - latest_date).days

                if age_days < 0:
                    freshness = "future_dated"
                elif not source_active:
                    freshness = "source_inactive"
                elif age_days > max_age_days:
                    freshness = "stale"
                else:
                    freshness = "fresh"

            elif not source_active:
                freshness = "source_inactive"

            trend_eligible = len(distinct_dates) >= 8

            # Return the most recent observations in chronological order
            # for charting. Keep the full distinct-date count separately.
            displayed_rows = list(reversed(grade_rows[:limit]))

            grade_results.append({
                "grade": grade_key,
                "label": coffee_grades[grade_key],
                "latest": (
                    serialize_observation(latest_row)
                    if latest_row else None
                ),
                "age_days": age_days,
                "freshness": freshness,
                "observation_count": len(grade_rows),
                "distinct_report_dates": len(distinct_dates),
                "trend_eligible": trend_eligible,
                "trend_status": (
                    "eligible_for_analysis"
                    if trend_eligible
                    else "insufficient_distinct_dates"
                ),
                "trend": (
                    latest_row.get("trend")
                    if trend_eligible and latest_row
                    else None
                ),
                "score": None,
                "score_status": "not_available_until_calibrated",
                "observations": [
                    serialize_observation(row)
                    for row in displayed_rows
                ],
            })

        return {
            "status": "success",
            "crop_slug": "coffee",
            "price_type": "farm_gate_weekly",
            "description": (
                "Weekly farm-gate price ranges published in MAAIF "
                "coffee market reports. These are not daily spot "
                "quotations or wholesale/export prices."
            ),
            "source": {
                "name": source.get("name"),
                "organization": source.get("organization"),
                "source_url": source.get("source_url"),
                "source_type": source.get("source_type"),
                "update_frequency": source.get("update_frequency"),
                "reliability_score": source.get("reliability_score"),
                "is_active": source_active,
                "max_age_days": max_age_days,
            },
            "currency": "UGX",
            "unit": "kg",
            "minimum_distinct_dates_for_trend": 8,
            "grades": grade_results,
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(
            "COFFEE MARKET PRICES ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve coffee market prices.",
        )

