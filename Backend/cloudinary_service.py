"""ShelfScan AI - Cloudinary Upload Service"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
import base64
import io
from config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


async def upload_image(image_bytes: bytes, store_id: str) -> str:
    """Upload shelf image to Cloudinary, return secure URL"""
    try:
        result = cloudinary.uploader.upload(
            image_bytes,
            folder=f"shelfscan/{store_id}",
            resource_type="image",
            tags=["shelfscan", "kirana", store_id],
            transformation=[
                {"width": 1280, "height": 960, "crop": "limit", "quality": "auto:good"}
            ]
        )
        return result["secure_url"]
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")


async def upload_audio(audio_bytes: bytes, scan_id: str) -> str:
    """Upload voice note audio to Cloudinary"""
    try:
        result = cloudinary.uploader.upload(
            audio_bytes,
            folder=f"shelfscan/audio/{scan_id}",
            resource_type="video",  # Cloudinary uses 'video' for audio files
            tags=["shelfscan", "voice_note", scan_id],
            format="mp3"
        )
        return result["secure_url"]
    except Exception as e:
        raise Exception(f"Cloudinary audio upload failed: {str(e)}")
