from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Error Response Models
class ErrorResponse(BaseModel):
    """Standard error response structure for all API errors"""
    status: str = "error"
    error_code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    suggestion: Optional[str] = Field(None, description="Actionable guidance for the user")

class ValidationError(ErrorResponse):
    """Error response for input validation failures"""
    field: str = Field(..., description="Field that failed validation")
    value_provided: Optional[Any] = Field(None, description="Invalid value submitted")
    expected: str = Field(..., description="Expected format/range description")

class ProcessingError(ErrorResponse):
    """Error response for image/watermark processing failures"""
    stage: str = Field(..., description="Processing stage that failed")
    recoverable: bool = Field(..., description="Whether operation can be retried")
    technical_details: Optional[str] = Field(None, description="Technical error details for debugging")

class WatermarkResponseData(BaseModel):
    image_url: str
    signal_map_url: Optional[str] = None
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

class VerificationMetadata(BaseModel):
    rotation_detected: float
    scale_detected: float
    geometry_corrected: bool

class VerificationResponseData(BaseModel):
    verified: bool
    watermark_text: Optional[str]
    confidence: float
    metadata: Optional[VerificationMetadata] = None

class VerificationResponse(BaseModel):
    status: str = "success"
    data: VerificationResponseData
