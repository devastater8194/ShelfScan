"""
ShelfScan AI - ElevenLabs Hindi Voice Note Service
Converts Decider's Hindi text to natural voice note
Uploads to Cloudinary and returns URL
"""
import httpx
import io
from config import settings
from services.cloudinary_service import upload_audio  # noqa: E402


async def generate_hindi_voice(hindi_text: str, store_name: str, scan_id: str) -> tuple[str, int]:
    """
    Generate Hindi voice note via ElevenLabs
    Returns (audio_url, duration_seconds)
    """
    try:
        # ElevenLabs TTS API
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": settings.ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg"
                },
                json={
                    "text": hindi_text,
                    "model_id": "eleven_multilingual_v2",  # Supports Hindi
                    "voice_settings": {
                        "stability": 0.6,
                        "similarity_boost": 0.8,
                        "style": 0.3,
                        "use_speaker_boost": True
                    }
                }
            )

            if response.status_code != 200:
                raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

            audio_bytes = response.content

            # Estimate duration (roughly 150 words per minute for Hindi speech)
            word_count = len(hindi_text.split())
            estimated_seconds = max(5, int((word_count / 150) * 60))

            # Upload to Cloudinary
            audio_url = await upload_audio(audio_bytes, scan_id)

            return audio_url, estimated_seconds

    except Exception as e:
        # Return placeholder if voice generation fails
        print(f"Voice generation failed: {e}")
        return "", 0


async def generate_voice_direct(hindi_text: str) -> bytes:
    """Generate voice and return raw bytes (for streaming)"""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": settings.ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg"
                },
                json={
                    "text": hindi_text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.6,
                        "similarity_boost": 0.8,
                        "style": 0.3,
                        "use_speaker_boost": True
                    }
                }
            )
            if response.status_code == 200:
                return response.content
            return b""
    except:
        return b""
