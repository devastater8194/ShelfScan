from pydantic import BaseModel, validator
from typing import Optional
import re


class StoreRegister(BaseModel):
    owner_name: str
    whatsapp_number: str
    store_name: str
    city: str
    pincode: str
    address: Optional[str] = None
    store_type: str = "kirana"
    monthly_sales_volume: Optional[str] = None
    num_shelves: Optional[int] = None
    primary_language: str = "hindi"
    product_categories: Optional[str] = None
    gst_number: Optional[str] = None
    referral_code: Optional[str] = None

    @validator("whatsapp_number")
    def validate_phone(cls, v):
        clean = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^(\+91|91)?[6-9]\d{9}$", clean):
            raise ValueError("Invalid Indian WhatsApp number")
        digits = re.sub(r"[^\d]", "", clean)
        if len(digits) == 10:
            return "+91" + digits
        if len(digits) == 12 and digits.startswith("91"):
            return "+" + digits
        return v

    @validator("pincode")
    def validate_pincode(cls, v):
        if not re.match(r"^\d{6}$", v):
            raise ValueError("Pincode must be 6 digits")
        return v


class ScanRequest(BaseModel):
    store_id: str
    image_url: Optional[str] = None


class DebateRound(BaseModel):
    agent: str
    agent_type: str
    output: str
    reasoning: Optional[str] = None


class ProductDetected(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    stock_level: str  # critical, low, ok, overstocked
    quantity: Optional[int] = None
    facing_correct: bool = True
    shelf_position: Optional[str] = None
