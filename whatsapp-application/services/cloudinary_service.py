import cloudinary
import cloudinary.uploader
import tempfile

cloudinary.config(
    cloud_name="df2dny7v9",
    api_key="349891514141967",
    api_secret="W4_husqYofEr_hX2mXsVXdlpJvU"
)

def upload_image(image_bytes):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

    with open(temp_file.name, "wb") as f:
        f.write(image_bytes)

    result = cloudinary.uploader.upload(
        temp_file.name,
        resource_type="auto"
    )

    return result["secure_url"]