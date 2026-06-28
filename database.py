import os
from dotenv import load_dotenv
from supabase import create_client

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

# =========================
# SUPABASE CONFIG
# =========================
SUPABASE_URL = "https://xmdjdxwsvvdxwizokhgs.supabase.co"

# 🔐 Secure key from environment (PRODUCTION SAFE)
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY:
    raise Exception("SUPABASE_KEY is missing in environment variables!")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# STRIPE CONFIG (NEW ADDITION)
# =========================
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

if not STRIPE_SECRET_KEY:
    print("⚠️ WARNING: STRIPE_SECRET_KEY not found in environment")

if not STRIPE_PUBLISHABLE_KEY:
    print("⚠️ WARNING: STRIPE_PUBLISHABLE_KEY not found in environment")
