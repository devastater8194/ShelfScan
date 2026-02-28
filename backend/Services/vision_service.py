"""
ShelfScan AI - Gemini Vision Service
Analyzes shelf images using Google Gemini 1.5 Pro Vision
Returns structured JSON with product detection, stock levels, facing analysis
"""
import google.generativeai as genai
import json
import base64
import re
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


VISION_PROMPT = """
You are ShelfScan AI Vision — an expert retail shelf analyst for Indian kirana stores.

Analyze this shelf image in detail and return a structured JSON response.

Detect EVERY product visible on the shelf. For each product identify:
- Product name (exact brand + product, e.g. "Parle-G Biscuits", "Maggi 2-Minute Noodles", "Tata Salt")
- Brand name
- Category (Biscuits, Beverages, Dairy, Staples, Snacks, Cleaning, Personal Care, etc.)
- Stock level: "critical" (0-2 units or empty), "low" (3-5 units), "ok" (6-15 units), "overstocked" (16+ units)
- Quantity estimate (number of visible units)
- Facing correct: true if product faces forward properly, false if turned sideways/backwards
- Shelf position: "top", "middle", "bottom", "eye_level"
- Any visible price tag

Also provide:
- Overall shelf health score (0-100)
- Top 3 urgent restock needs
- Shelf organization quality: "poor", "average", "good", "excellent"
- Empty shelf sections detected
- Incorrect facing count

Return ONLY valid JSON in this exact structure (no markdown, no explanation):
{
  "products": [
    {
      "name": "Parle-G Biscuits",
      "brand": "Parle",
      "category": "Biscuits",
      "stock_level": "ok",
      "quantity": 8,
      "facing_correct": true,
      "shelf_position": "eye_level",
      "price_visible": "₹10"
    }
  ],
  "shelf_health_score": 75,
  "critical_count": 2,
  "low_count": 3,
  "ok_count": 8,
  "overstocked_count": 1,
  "empty_sections": 2,
  "facing_issues": 1,
  "organization_quality": "average",
  "top_restock_urgent": ["Tata Salt", "Maggi Noodles", "Dettol Soap"],
  "summary": {
    "total_products": 14,
    "total_skus": 10,
    "shelf_coverage": 70,
    "categories_detected": ["Biscuits", "Beverages", "Staples"]
  },
  "raw_observations": "Brief description of what is visible on the shelf"
}
"""


async def analyze_shelf_image(image_url: str, image_bytes: bytes) -> dict:
    """
    Use Gemini 1.5 Pro Vision to analyze a kirana shelf image
    Returns structured product detection data
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Convert bytes to base64 for Gemini
        image_data = {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(image_bytes).decode("utf-8")
        }

        response = model.generate_content(
            [VISION_PROMPT, image_data],
            generation_config=genai.GenerationConfig(
                temperature=0.1,  # Low temp for accurate detection
                max_output_tokens=4096
            )
        )

        raw_text = response.text.strip()

        # Clean JSON from response (remove markdown if present)
        raw_text = re.sub(r"```json\n?", "", raw_text)
        raw_text = re.sub(r"```\n?", "", raw_text)
        raw_text = raw_text.strip()

        vision_data = json.loads(raw_text)
        vision_data["image_url"] = image_url
        return vision_data

    except json.JSONDecodeError:
        # Fallback: try to extract JSON from response
        try:
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        # Return minimal valid structure
        return _fallback_vision_data(image_url)

    except Exception as e:
        raise Exception(f"Gemini Vision analysis failed: {str(e)}")


def _fallback_vision_data(image_url: str) -> dict:
    """Fallback structure if vision parsing fails"""
    return {
        "products": [],
        "shelf_health_score": 0,
        "critical_count": 0,
        "low_count": 0,
        "ok_count": 0,
        "overstocked_count": 0,
        "empty_sections": 0,
        "facing_issues": 0,
        "organization_quality": "unknown",
        "top_restock_urgent": [],
        "summary": {"total_products": 0, "total_skus": 0, "shelf_coverage": 0, "categories_detected": []},
        "raw_observations": "Image analysis failed - please retry",
        "image_url": image_url
    }
