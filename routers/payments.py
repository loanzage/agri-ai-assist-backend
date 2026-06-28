from fastapi import APIRouter
from services.payment_service import create_checkout_session

router = APIRouter()


@router.post("/create-payment")
async def create_payment(data: dict):

    url = create_checkout_session(
        amount=data["amount"],
        product_name=data["product_name"]
    )

    return {"checkout_url": url}
