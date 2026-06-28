from fastapi import APIRouter
from database import supabase

router = APIRouter()

# =========================
# BUY CROP API
# =========================
@router.post("/buy-crop")
async def buy_crop(data: dict):

    # calculate total price
    total_price = data["quantity"] * data["price_per_unit"]

    # create order
    order = supabase.table("marketplace_orders").insert({
        "buyer_id": data["buyer_id"],
        "listing_id": data["listing_id"],
        "farmer_id": data["farmer_id"],
        "crop": data["crop"],
        "quantity": data["quantity"],
        "total_price": total_price,
        "status": "pending"
    }).execute()

    return {
        "message": "Order placed",
        "order": order.data
    }
