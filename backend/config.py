"""ShelfScan AI — Configuration (All API Keys Pre-Configured)"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    SUPABASE_URL: str = "https://qdnwfrbxxfshvuchencs.supabase.co"
    SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFkbndmcmJ4eGZzaHZ1Y2hlbmNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIxODQ3OTksImV4cCI6MjA4Nzc2MDc5OX0.KgetXytfa6VFUouWCFWvlG6kgaNQZKjPIx3R3mtdCjY"
    GEMINI_API_KEY: str = "AIzaSyBqs0CV4MROjYy3q64ffS2xszO6bIjprZw"

    CLOUDINARY_CLOUD_NAME: str = "df2dny7v9"
    CLOUDINARY_API_KEY: str = "349891514141967"
    CLOUDINARY_API_SECRET: str = "W4_husqYofEr_hX2mXsVXdlpJvU"

    ELEVENLABS_API_KEY: str = "sk_d1e022c2253af9e1a950edbd61094a923d7ed7991a297d00"
    ELEVENLABS_VOICE_ID: str = "qsz5tTEjPvsiIJZIpM8S"

    TWILIO_ACCOUNT_SID: str = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.environ.get("TWILIO_WHATSAPP_NUMBER", "+14155238886")

    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

    TOGETHER_API_KEY: str = os.environ.get("TOGETHER_API_KEY", "")

    COHERE_API_KEY: str = os.environ.get("COHERE_API_KEY", "")

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True


settings = Settings()
