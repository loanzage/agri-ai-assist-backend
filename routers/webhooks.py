from fastapi import APIRouter, Request, HTTPException
import stripe
import os

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()

    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")

    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # =========================
    # PAYMENT COMPLETED
    # =========================
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        print("✅ PAYMENT SUCCESSFUL")
        print("Session ID:", session["id"])
        print("Customer:", session.get("customer"))
        print("Amount:", session["amount_total"])

    return {
        "status": "success"
    }
