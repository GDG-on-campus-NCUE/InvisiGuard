from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class WatermarkResponseData(BaseModel):
    image_url: str
    psnr: float
    ssim: float

class WatermarkResponse(BaseModel):
    status: str = "success"
    data: WatermarkResponseData

class ExtractionDebugInfo(BaseModel):
    aligned_image_url: Optional[str] = None
    matches_found: Optional[int] = None

class ExtractionResponseData(BaseModel):
    decoded_text: str
    confidence: float
    is_match: bool
    debug_info: Optional[ExtractionDebugInfo] = None

class ExtractionResponse(BaseModel):
    status: str = "success"
    data: ExtractionResponseData
