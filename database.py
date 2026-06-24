import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from .env (local only)
load_dotenv()

# Supabase Project URL (your project)
SUPABASE_URL = "https://xmdjdxwsvvdxwizokhgs.supabase.co"

# IMPORTANT:
# NEVER hardcode this in production — use Render ENV VAR instead
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Fallback (ONLY for local testing if env missing)
if not SUPABASE_KEY:
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtZGpkeHdzdnZkeHdpem9raGdzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3NDU4MzEsImV4cCI6MjA5NzMyMTgzMX0.-An0J3CYpp_BPn1twy5lmZsCIPMIUJAcQ8FnpkHsM9U"

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
