"""
Logging configuration for InvisiGuard backend
Provides structured logging with context for debugging
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import json

# Configure logging format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Setup application-wide logging configuration
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Get logger for this application
    logger = logging.getLogger("invisiguard")
    logger.setLevel(numeric_level)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"invisiguard.{name}")

def log_request_context(logger: logging.Logger, endpoint: str, **kwargs):
    """
    Log API request context with structured data
    
    Args:
        logger: Logger instance
        endpoint: API endpoint being called
        **kwargs: Additional context (file_size, text_length, etc.)
    """
    context = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        **kwargs
    }
    logger.info(f"Request: {endpoint}", extra={"context": context})

def log_processing_stage(logger: logging.Logger, stage: str, duration_ms: Optional[float] = None, **kwargs):
    """
    Log processing stage with timing information
    
    Args:
        logger: Logger instance
        stage: Processing stage name (e.g., "image_loading", "dwt_transform")
        duration_ms: Duration in milliseconds
        **kwargs: Additional context
    """
    context = {
        "stage": stage,
        "duration_ms": duration_ms,
        **kwargs
    }
    logger.debug(f"Stage: {stage} {f'({duration_ms}ms)' if duration_ms else ''}", extra={"context": context})

def log_error_with_context(
    logger: logging.Logger,
    error_code: str,
    message: str,
    exception: Optional[Exception] = None,
    **kwargs
):
    """
    Log error with full context for debugging
    
    Args:
        logger: Logger instance
        error_code: Machine-readable error code
        message: Human-readable error message
        exception: Exception object if available
        **kwargs: Additional error context
    """
    context = {
        "error_code": error_code,
        "message": message,
        "exception_type": type(exception).__name__ if exception else None,
        "exception_message": str(exception) if exception else None,
        **kwargs
    }
    
    log_message = f"Error: {error_code} - {message}"
    if exception:
        logger.error(log_message, exc_info=exception, extra={"context": context})
    else:
        logger.error(log_message, extra={"context": context})

def log_validation_error(logger: logging.Logger, field: str, value: Any, expected: str):
    """
    Log validation error with field details
    
    Args:
        logger: Logger instance
        field: Field name that failed validation
        value: Value that was provided
        expected: Expected value format/range
    """
    logger.warning(
        f"Validation failed: {field}",
        extra={
            "context": {
                "field": field,
                "value_provided": value,
                "expected": expected
            }
        }
    )

def log_success_with_metrics(logger: logging.Logger, operation: str, metrics: Dict[str, Any]):
    """
    Log successful operation with metrics
    
    Args:
        logger: Logger instance
        operation: Operation name (e.g., "embed", "extract", "verify")
        metrics: Performance metrics (psnr, ssim, confidence, etc.)
    """
    logger.info(
        f"Success: {operation}",
        extra={
            "context": {
                "operation": operation,
                "metrics": metrics
            }
        }
    )

# Initialize default logger
default_logger = setup_logging()
