from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from src.api.schemas import WatermarkResponse, ExtractionResponse

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "InvisiGuard API"}

# Placeholders for future endpoints
@router.post("/embed", response_model=WatermarkResponse)
async def embed_watermark(
    file: UploadFile = File(...),
    text: str = Form(...),
    alpha: float = Form(1.0)
):
    # TODO: Implement embedding logic
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/extract", response_model=ExtractionResponse)
async def extract_watermark(
    original_file: UploadFile = File(...),
    suspect_file: UploadFile = File(...)
):
    # TODO: Implement extraction logic
    raise HTTPException(status_code=501, detail="Not implemented")
