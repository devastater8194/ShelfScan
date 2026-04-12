# import requests
# import cloudinary
# import cloudinary.uploader
# import tempfile

# # 🔴 YOUR KEYS
# API_KEY = "sk_574c1a309ced6c83a08ca57169e88046016d78f8c6e1da27"
# VOICE_ID = "tA6LGZpsqStKtSaGiXND"  # Use free voice like Rachel

# cloudinary.config(
#     cloud_name="df2dny7v9",
#     api_key="349891514141967",
#     api_secret="W4_husqYofEr_hX2mXsVXdlpJvU"
# )

# def generate_voice(text):
#     url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

#     headers = {
#         "xi-api-key": API_KEY,
#         "Content-Type": "application/json"
#     }

#     # ✅ FREE MODEL
#     data = {
#         "text": text,
#         "model_id": "eleven_monolingual_v1"
#     }

#     response = requests.post(url, json=data, headers=headers)

#     if response.status_code != 200:
#         print("Voice error:", response.text)
#         raise Exception("Voice generation failed")

#     # ✅ Save temp file
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
#     with open(temp_file.name, "wb") as f:
#         f.write(response.content)

#     # ✅ Upload to Cloudinary (PUBLIC URL)
#     result = cloudinary.uploader.upload(
#         temp_file.name,
#         resource_type="video"  # IMPORTANT
#     )
#     return result["secure_url"]

# #     return result["secure_url"]
# from gtts import gTTS
# import cloudinary
# import cloudinary.uploader
# import tempfile

# # 🔴 Cloudinary config (same as before)
# cloudinary.config(
#     cloud_name="df2dny7v9",
#     api_key="349891514141967",
#     api_secret="W4_husqYofEr_hX2mXsVXdlpJvU"
# )

# def generate_voice(text):
#     # ✅ Generate voice (English or Hindi)
#     tts = gTTS(text=text, lang='hi')   # change to 'hi' for Hindi

#     # Save temp file
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
#     tts.save(temp_file.name)

#     # Upload to Cloudinary (public URL)
#     result = cloudinary.uploader.upload(
#         temp_file.name,
#         resource_type="video"
#     )

#     return result["secure_url"]
from gtts import gTTS
import cloudinary
import cloudinary.uploader
import tempfile

cloudinary.config(
    cloud_name="df2dny7v9",
    api_key="349891514141967",
    api_secret="W4_husqYofEr_hX2mXsVXdlpJvU"
)

def generate_voice(text):
    text = text.strip()

    print("🗣️ Voice input text:", text)

    # ✅ Hindi voice
    tts = gTTS(text=text, lang='hi')

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)

    result = cloudinary.uploader.upload(
        temp_file.name,
        resource_type="video"
    )

    return result["secure_url"]