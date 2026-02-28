"""
ShelfScan AI — Twilio WhatsApp Webhook Handler
================================================
Handles inbound WhatsApp messages (image shelf scans) and sends back Hindi voice notes.

Flow:
  1. Kirana owner sends shelf photo to ShelfScan WhatsApp number
  2. Twilio POSTs to /webhook/whatsapp
  3. We download the image, run the full AI pipeline
  4. Reply with the Hindi voice note URL via WhatsApp

Webhook URL to configure in Twilio Console:
  https://YOUR-RAILWAY-URL/webhook/whatsapp
  Method: HTTP POST
"""

import httpx
from typing import Optional
from config import settings


TWILIO_API_URL = "https://api.twilio.com/2010-04-01"


async def download_media(media_url: str, account_sid: str, auth_token: str) -> bytes:
    """Download media from Twilio (requires Basic Auth)"""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(media_url, auth=(account_sid, auth_token))
        if r.status_code != 200:
            raise Exception(f"Failed to download media: {r.status_code}")
        return r.content


async def send_whatsapp_text(
    to: str,
    body: str,
    from_number: str,
    account_sid: str,
    auth_token: str
) -> dict:
    """Send a WhatsApp text message via Twilio"""
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"{TWILIO_API_URL}/Accounts/{account_sid}/Messages.json",
            auth=(account_sid, auth_token),
            data={
                "From": f"whatsapp:{from_number}",
                "To": f"whatsapp:{to}",
                "Body": body,
            }
        )
        return r.json()


async def send_whatsapp_media(
    to: str,
    body: str,
    media_url: str,
    from_number: str,
    account_sid: str,
    auth_token: str
) -> dict:
    """Send a WhatsApp message with audio/media attachment via Twilio"""
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"{TWILIO_API_URL}/Accounts/{account_sid}/Messages.json",
            auth=(account_sid, auth_token),
            data={
                "From": f"whatsapp:{from_number}",
                "To": f"whatsapp:{to}",
                "Body": body,
                "MediaUrl": media_url,
            }
        )
        return r.json()


def build_processing_twiml() -> str:
    """Immediate acknowledgment TwiML while background pipeline runs"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>
    <Body>ShelfScan AI ne aapki shelf photo receive kar li! Analysis shuru ho raha hai... 30 seconds mein aapka report aayega.</Body>
  </Message>
</Response>"""
