from twilio.rest import Client

ACCOUNT_SID = "ACab776956e11ff45f3306e1debe3ac12f"
AUTH_TOKEN = "0882bab4520f1b2bfbe65667164f1fcc"
FROM_NUMBER = "whatsapp:+14155238886"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp_audio(to, audio_url, text):
    message = client.messages.create(
        from_=FROM_NUMBER,
        to=to,
        body=text,
        media_url=[audio_url] if audio_url else None
    )