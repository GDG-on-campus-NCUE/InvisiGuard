from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from src.api.schemas import (
    WatermarkResponse, ExtractionResponse, WatermarkResponseData, 
    ExtractionResponseData, VerificationResponse, VerificationResponseData,
    ErrorResponse, ValidationError, ProcessingError
)
from src.core.processor import ImageProcessor
from src.services.watermark import WatermarkService
from src.utils.logger import get_logger, log_request_context, log_error_with_context, log_validation_error, log_success_with_metrics
import time

router = APIRouter()
watermark_service = WatermarkService()
logger = get_logger(__name__)

# Allowed file types
ALLOWED_CONTENT_TYPES = ["image/png", "image/jpeg", "image/jpg"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALPHA_MIN = 0.1
ALPHA_MAX = 5.0

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "InvisiGuard API"}

@router.post("/embed", response_model=WatermarkResponse)
async def embed_watermark(
    file: UploadFile = File(...),
    text: str = Form(...),
    alpha: float = Form(1.0)
):
    start_time = time.time()
    
    # Log request context
    log_request_context(
        logger, 
        "/v1/embed",
        file_name=file.filename,
        file_type=file.content_type,
        text_length=len(text),
        alpha=alpha
    )
    
    try:
        # T007: Validate file type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            log_validation_error(logger, "file", file.content_type, f"One of {ALLOWED_CONTENT_TYPES}")
            error = ValidationError(
                error_code="INVALID_FILE_FORMAT",
                message="Only PNG and JPG images are supported",
                field="file",
                value_provided=file.content_type,
                expected=f"One of: {', '.join(ALLOWED_CONTENT_TYPES)}",
                suggestion="Please convert your image to PNG or JPG format and try again"
            )
            return JSONResponse(status_code=400, content=error.dict())
        
        # T008: Validate text field (non-empty, trimmed)
        if not text or text.strip() == "":
            log_validation_error(logger, "text", text, "Non-empty string")
            error = ValidationError(
                error_code="EMPTY_WATERMARK_TEXT",
                message="Watermark text cannot be empty",
                field="text",
                value_provided=text,
                expected="Non-empty string",
                suggestion="Please enter the text you want to embed as a watermark"
            )
            return JSONResponse(status_code=400, content=error.dict())
        
        # T009: Validate alpha range (0.1-5.0)
        if alpha < ALPHA_MIN or alpha > ALPHA_MAX:
            log_validation_error(logger, "alpha", alpha, f"Float between {ALPHA_MIN} and {ALPHA_MAX}")
            error = ValidationError(
                error_code="INVALID_ALPHA_RANGE",
                message=f"Alpha value must be between {ALPHA_MIN} and {ALPHA_MAX}",
                field="alpha",
                value_provided=alpha,
                expected=f"Float between {ALPHA_MIN} and {ALPHA_MAX}",
                suggestion=f"Adjust the strength slider to a value between {ALPHA_MIN} and {ALPHA_MAX}"
            )
            return JSONResponse(status_code=400, content=error.dict())
        
        # T006: Load image (Content-Type handling is automatic via FastAPI/Starlette)
        try:
            image = await ImageProcessor.load_image(file)
        except Exception as e:
            log_error_with_context(
                logger,
                "IMAGE_DECODE_ERROR",
                "Could not decode the uploaded image",
                e,
                file_name=file.filename,
                file_type=file.content_type
            )
            # T010: Structured error response
            error = ProcessingError(
                error_code="IMAGE_DECODE_ERROR",
                message="Could not decode the uploaded image",
                stage="image_loading",
                recoverable=False,
                details={
                    "file_name": file.filename,
                    "content_type": file.content_type
                },
                suggestion="The image file may be corrupted. Try uploading a different image"
            )
            return JSONResponse(status_code=400, content=error.dict())
        
        # Process watermark embedding
        try:
            result = await watermark_service.embed(image, text.strip(), alpha)
        except ValueError as e:
            # T011: Error logging with context
            log_error_with_context(
                logger,
                "WATERMARK_EMBEDDING_FAILED",
                "Watermark embedding failed",
                e,
                text_length=len(text),
                alpha=alpha
            )
            error = ProcessingError(
                error_code="WATERMARK_EMBEDDING_FAILED",
                message="Failed to embed watermark into image",
                stage="watermark_embedding",
                recoverable=True,
                details={"error_message": str(e)},
                suggestion="Try adjusting the alpha (strength) value or using a different image"
            )
            return JSONResponse(status_code=500, content=error.dict())
        except Exception as e:
            log_error_with_context(
                logger,
                "INTERNAL_SERVER_ERROR",
                "Unexpected error during watermark embedding",
                e,
                text_length=len(text),
                alpha=alpha
            )
            error = ProcessingError(
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred while embedding the watermark",
                stage="watermark_embedding",
                recoverable=True,
                technical_details=str(e),
                suggestion="Please try again. If the problem persists, contact support"
            )
            return JSONResponse(status_code=500, content=error.dict())
        
        # Log success
        duration_ms = (time.time() - start_time) * 1000
        log_success_with_metrics(
            logger,
            "embed",
            {
                "psnr": result.get("psnr"),
                "ssim": result.get("ssim"),
                "duration_ms": duration_ms
            }
        )
        
        return WatermarkResponse(
            status="success",
            data=WatermarkResponseData(**result)
        )
        
    except Exception as e:
        # Catch-all for unexpected errors
        log_error_with_context(logger, "UNEXPECTED_ERROR", "Unhandled exception in embed endpoint", e)
        error = ErrorResponse(
            error_code="UNEXPECTED_ERROR",
            message="An unexpected error occurred",
            suggestion="Please try again or contact support if the problem persists"
        )
        return JSONResponse(status_code=500, content=error.dict())

@router.post("/extract", response_model=ExtractionResponse)
async def extract_watermark(
    original_file: UploadFile = File(...),
    suspect_file: UploadFile = File(...)
):
    try:
        # Load images
        original = await ImageProcessor.load_image(original_file)
        suspect = await ImageProcessor.load_image(suspect_file)
        
        # Process
        result = await watermark_service.extract(original, suspect)
        
        return ExtractionResponse(
            status="success",
            data=ExtractionResponseData(
                decoded_text=result["extracted_text"],
                confidence=1.0 if result["status"] == "aligned" else 0.5,
                is_match=True,
                debug_info=None
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify", response_model=VerificationResponse)
async def verify_watermark(
    image: UploadFile = File(...)
):
    start_time = time.time()
    
    # Log request context
    log_request_context(
        logger,
        "/v1/verify",
        file_name=image.filename,
        file_type=image.content_type
    )
    
    try:
        # T043: Validate image file
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            log_validation_error(logger, "image", image.content_type, f"One of {ALLOWED_CONTENT_TYPES}")
            error = ValidationError(
                error_code="INVALID_FILE_FORMAT",
                message="Only PNG and JPG images are supported",
                field="image",
                value_provided=image.content_type,
                expected=f"One of: {', '.join(ALLOWED_CONTENT_TYPES)}",
                suggestion="Please convert your image to PNG or JPG format and try again"
            )
            return JSONResponse(status_code=400, content=error.dict())
        
        # Load image
        try:
            suspect = await ImageProcessor.load_image(image)
        except Exception as e:
            log_error_with_context(
                logger,
                "IMAGE_DECODE_ERROR",
                "Could not decode the uploaded image",
                e,
                file_name=image.filename,
                file_type=image.content_type
            )
            # T042: Structured error response
            error = ProcessingError(
                error_code="IMAGE_DECODE_ERROR",
                message="Could not decode the uploaded image",
                stage="image_loading",
                recoverable=False,
                details={
                    "file_name": image.filename,
                    "content_type": image.content_type
                },
                suggestion="The image file may be corrupted. Try uploading a different image"
            )
            return JSONResponse(status_code=400, content=error.dict())
        
        # Process verification
        try:
            result = await watermark_service.verify(suspect)
        except ValueError as e:
            log_error_with_context(
                logger,
                "WATERMARK_VERIFICATION_FAILED",
                "Watermark verification failed",
                e,
                file_name=image.filename
            )
            # T042: Structured error response
            error = ProcessingError(
                error_code="WATERMARK_VERIFICATION_FAILED",
                message="Failed to verify watermark in image",
                stage="watermark_verification",
                recoverable=True,
                details={"error_message": str(e)},
                suggestion="The image may not contain a watermark, or it may be too damaged to extract"
            )
            return JSONResponse(status_code=500, content=error.dict())
        except Exception as e:
            log_error_with_context(
                logger,
                "INTERNAL_SERVER_ERROR",
                "Unexpected error during watermark verification",
                e,
                file_name=image.filename
            )
            error = ProcessingError(
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred during verification",
                stage="watermark_verification",
                recoverable=True,
                technical_details=str(e),
                suggestion="Please try again. If the problem persists, contact support"
            )
            return JSONResponse(status_code=500, content=error.dict())
        
        # Log success
        duration_ms = (time.time() - start_time) * 1000
        log_success_with_metrics(
            logger,
            "verify",
            {
                "verified": result.get("verified"),
                "confidence": result.get("confidence"),
                "duration_ms": duration_ms
            }
        )
        
        return VerificationResponse(
            status="success",
            data=VerificationResponseData(**result)
        )
        
    except Exception as e:
        # Catch-all for unexpected errors
        log_error_with_context(logger, "UNEXPECTED_ERROR", "Unhandled exception in verify endpoint", e)
        error = ErrorResponse(
            error_code="UNEXPECTED_ERROR",
            message="An unexpected error occurred",
            suggestion="Please try again or contact support if the problem persists"
        )
        return JSONResponse(status_code=500, content=error.dict())
