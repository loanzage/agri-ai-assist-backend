from fastapi import APIRouter, Request
import stripe
import os

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()

    print("Webhook received")

    return {
        "status": "received"
    }
