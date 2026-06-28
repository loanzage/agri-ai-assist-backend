import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# STRIPE CONFIG
# =========================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
