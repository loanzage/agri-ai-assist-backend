from fastapi import APIRouter
import stripe
import os

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@router.post("/create-payment")
async def create_payment(data: dict):

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": data["product_name"],
                },
                "unit_amount": int(data["amount"] * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="https://your-app.com/success",
        cancel_url="https://your-app.com/cancel",
    )

    return {"checkout_url": session.url}
