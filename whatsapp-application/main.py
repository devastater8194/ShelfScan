from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import Response
import requests

from services.cloudinary_service import upload_image
from services.vision import analyze_image
from services.voice import generate_voice
from services.twilio_service import send_whatsapp_audio, ACCOUNT_SID, AUTH_TOKEN

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Server is running"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()

    from_number = form.get("From")
    media_url = form.get("MediaUrl0")

    print("Incoming message from:", from_number)
    print("Media URL:", media_url)

    if not media_url:
        return twiml_response("📸 Please send a shelf image")

    background_tasks.add_task(process_pipeline, from_number, media_url)

    return twiml_response("🔍 Analyzing your shelf...")


def twiml_response(message):
    return Response(
        content=f"""
<Response>
    <Message>{message}</Message>
</Response>
""",
        media_type="application/xml"
    )


async def process_pipeline(from_number, media_url):
    try:
        print("🚀 Starting pipeline...")

        # ✅ STEP 1: Download image
        response = requests.get(
            media_url,
            auth=(ACCOUNT_SID, AUTH_TOKEN)
        )

        if response.status_code != 200:
            raise Exception("❌ Failed to download image")

        print("Content-Type:", response.headers.get("Content-Type"))

        image_bytes = response.content

        if not image_bytes or len(image_bytes) < 100:
            raise Exception("❌ Invalid or empty image received")

        print("✅ Image downloaded, size:", len(image_bytes))

        # ✅ STEP 2: Upload to Cloudinary
        image_url = upload_image(image_bytes)
        print("✅ Uploaded to Cloudinary:", image_url)

        # ✅ STEP 3: Gemini AI
        result_text = analyze_image(image_url)
        print("✅ Gemini response received")

        # 🔥 STEP 3.5: CLEAN TEXT (VERY IMPORTANT)
        if not result_text or len(result_text.strip()) == 0:
            result_text = "Shelf looks moderately stocked. Consider restocking popular items."

        result_text = result_text.strip()
        result_text = result_text.replace("*", "")
        result_text = result_text.replace("#", "")

        print("🧹 Cleaned text:", result_text)

        # ✅ STEP 4: Voice generation
        audio_url = generate_voice(result_text)
        print("✅ Voice generated:", audio_url)

        # ✅ STEP 5: Send WhatsApp reply
        send_whatsapp_audio(from_number, audio_url, result_text)
        print("✅ Message sent to WhatsApp")

    except Exception as e:
        print("❌ ERROR in pipeline:", e)