import os
from dotenv import load_dotenv

load_dotenv()

NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")
# Kept for future use, but not used in MVP
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Kept for future use, but not used in MVP
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

AI_PROVIDER = os.getenv("AI_PROVIDER")
AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL")
AI_MODEL = os.getenv("AI_MODEL")

if not NEON_DATABASE_URL:
    raise ValueError("NEON_DATABASE_URL not set in .env file")
if not AI_API_KEY:
    raise ValueError("AI_API_KEY not set in .env file")
