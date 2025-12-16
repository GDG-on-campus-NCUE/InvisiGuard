# Data Model: Fix Core Functions

**Feature**: 004-fix-core-functions
**Date**: 2025年12月16日  
**Phase**: 1 - Design  
**Prerequisites**: [research.md](research.md) completed

## Overview

This document defines the data models for standardized error responses and enhanced request/response structures for the three fixed endpoints: `/v1/embed`, `/v1/extract`, and `/v1/verify`.

## Error Response Models

### ErrorResponse (Base)

**Purpose**: Standard structure for all error responses across the API

**Fields**:
- `status` (string, required): Always "error" for error responses
- `error_code` (string, required): Machine-readable error identifier (uppercase snake_case)
- `message` (string, required): Human-readable description of the error
- `details` (object, optional): Additional context specific to the error type
- `suggestion` (string, optional): Actionable guidance for the user

**Example**:
```json
{
  "status": "error",
  "error_code": "INVALID_FILE_FORMAT",
  "message": "Only PNG and JPG images are supported",
  "details": {
    "provided_type": "image/webp",
    "supported_types": ["image/png", "image/jpeg"]
  },
  "suggestion": "Please convert your image to PNG or JPG format and try again"
}
```

### ValidationError

**Purpose**: Specific error type for input validation failures

**Extends**: ErrorResponse

**Additional Fields**:
- `field` (string, required): Name of the field that failed validation
- `value_provided` (any, optional): The invalid value that was submitted
- `expected` (string, required): Description of the expected format/range

**Example**:
```json
{
  "status": "error",
  "error_code": "INVALID_ALPHA_RANGE",
  "message": "Alpha value must be between 0.1 and 5.0",
  "field": "alpha",
  "value_provided": 100.0,
  "expected": "Float between 0.1 and 5.0",
  "suggestion": "Adjust the strength slider to a value between 0.1 and 5.0"
}
```

### ProcessingError

**Purpose**: Error occurred during image/watermark processing

**Extends**: ErrorResponse

**Additional Fields**:
- `stage` (string, required): Which processing stage failed (e.g., "image_loading", "watermark_embedding", "extraction")
- `recoverable` (boolean, required): Whether the operation can be retried
- `technical_details` (string, optional): Stack trace or technical error message (for debugging)

**Example**:
```json
{
  "status": "error",
  "error_code": "IMAGE_DECODE_ERROR",
  "message": "Could not decode the uploaded image",
  "stage": "image_loading",
  "recoverable": false,
  "details": {
    "file_size": 1234567,
    "content_type": "image/jpeg"
  },
  "suggestion": "The image file may be corrupted. Try uploading a different image"
}
```

## Request Models

### EmbedRequest

**Endpoint**: `POST /v1/embed`  
**Content-Type**: `multipart/form-data`

**Fields**:
- `file` (binary, required): Image file to embed watermark into
  - Supported formats: PNG, JPG, JPEG
  - Max size: 10MB
  - Max resolution: 4K (3840x2160)
- `text` (string, required): Watermark text to embed
  - Min length: 1 character (after trimming whitespace)
  - Max length: ~240 characters (limited by Reed-Solomon + image capacity)
  - Encoding: UTF-8
- `alpha` (float, optional): Embedding strength
  - Range: 0.1 to 5.0
  - Default: 1.0
  - Higher values = stronger watermark, more visible

**Validation Rules**:
- File type must be in `['image/png', 'image/jpeg', 'image/jpg']`
- File size must be < 10,485,760 bytes (10MB)
- Text must not be empty or only whitespace
- Alpha must be within [0.1, 5.0] range

### ExtractRequest

**Endpoint**: `POST /v1/extract`  
**Content-Type**: `multipart/form-data`

**Fields**:
- `original_file` (binary, required): Original image used as reference for geometric alignment
  - Same format/size constraints as EmbedRequest.file
- `suspect_file` (binary, required): Image to extract watermark from (may be transformed)
  - Same format/size constraints as EmbedRequest.file

**Validation Rules**:
- Both files must be provided
- Both files must be valid images
- Files can have different resolutions (alignment will handle this)

### VerifyRequest

**Endpoint**: `POST /v1/verify`  
**Content-Type**: `multipart/form-data`

**Fields**:
- `image` (binary, required): Image to verify and extract watermark from (no original needed)
  - Same format/size constraints as EmbedRequest.file

**Validation Rules**:
- File must be provided
- File must be a valid image

## Response Models

### EmbedResponse (Success)

**HTTP Status**: 200 OK

**Structure**:
```json
{
  "status": "success",
  "data": {
    "image_url": "/static/processed/abc123.png",
    "signal_map_url": "/static/processed/signal_abc123.png",
    "psnr": 42.5,
    "ssim": 0.98,
    "metadata": {
      "original_size": [1920, 1080],
      "watermarked_size": [1920, 1080],
      "text_length": 12,
      "alpha_used": 1.0
    }
  }
}
```

**Fields**:
- `status`: Always "success"
- `data.image_url`: Relative URL to download watermarked image
- `data.signal_map_url`: Relative URL to view watermark strength heatmap
- `data.psnr`: Peak Signal-to-Noise Ratio (quality metric, higher = better)
- `data.ssim`: Structural Similarity Index (closer to 1.0 = more similar to original)
- `data.metadata`: Additional embedding information

### ExtractResponse (Success)

**HTTP Status**: 200 OK

**Structure**:
```json
{
  "status": "success",
  "data": {
    "decoded_text": "Copyright 2025",
    "confidence": 0.95,
    "is_match": true,
    "metadata": {
      "alignment_status": "aligned",
      "matches_found": 150,
      "rotation_detected": 15.3,
      "scale_detected": 0.95
    }
  }
}
```

**Fields**:
- `status`: Always "success"
- `data.decoded_text`: Extracted watermark text
- `data.confidence`: Confidence score (0.0 to 1.0)
- `data.is_match`: Whether extraction was successful
- `data.metadata`: Geometric transformation details

### VerifyResponse (Success)

**HTTP Status**: 200 OK

**Structure** (watermark found):
```json
{
  "status": "success",
  "data": {
    "verified": true,
    "watermark_text": "SecretMessage123",
    "confidence": 1.0,
    "metadata": {
      "rotation_detected": 0.0,
      "scale_detected": 1.0,
      "sync_template_found": true
    }
  }
}
```

**Structure** (no watermark):
```json
{
  "status": "success",
  "data": {
    "verified": false,
    "watermark_text": "",
    "confidence": 0.0,
    "metadata": {
      "message": "No Watermark Detected",
      "reason": "Sync template not found"
    }
  }
}
```

**Fields**:
- `status`: Always "success" (even if no watermark found - it's not an error)
- `data.verified`: Boolean indicating if watermark was successfully extracted
- `data.watermark_text`: Extracted text (empty string if not found)
- `data.confidence`: Confidence in the result
- `data.metadata`: Diagnostic information

## Error Codes Reference

### Client Errors (4xx)

| Error Code | HTTP Status | Trigger | User Action |
|-----------|-------------|---------|-------------|
| `INVALID_FILE_FORMAT` | 400 | Unsupported image format | Convert to PNG/JPG |
| `FILE_TOO_LARGE` | 400 | File exceeds 10MB | Resize or compress image |
| `EMPTY_TEXT` | 400 | Watermark text is blank | Enter text |
| `TEXT_TOO_LONG` | 400 | Text exceeds max length | Shorten text |
| `INVALID_ALPHA_RANGE` | 400 | Alpha < 0.1 or > 5.0 | Adjust slider |
| `MISSING_FILE` | 400 | Required file not uploaded | Upload file |
| `MISSING_ORIGINAL_FILE` | 400 | Extract: original not provided | Upload original image |
| `MISSING_SUSPECT_FILE` | 400 | Extract: suspect not provided | Upload suspect image |

### Server Errors (5xx)

| Error Code | HTTP Status | Trigger | User Action |
|-----------|-------------|---------|-------------|
| `IMAGE_DECODE_ERROR` | 500 | Cannot decode image bytes | Try different image |
| `WATERMARK_EMBED_FAILED` | 500 | Embedding algorithm error | Retry or report bug |
| `WATERMARK_EXTRACT_FAILED` | 500 | Extraction algorithm error | Retry or report bug |
| `GEOMETRY_ALIGNMENT_FAILED` | 500 | Cannot align images | Check images are related |
| `INTERNAL_ERROR` | 500 | Unexpected server error | Report to support |

## State Management Models (Frontend)

### App State Structure

```javascript
// Embed Tab State
const embedState = {
  file: File | null,           // Uploaded image file
  text: string,                // Watermark text input
  alpha: number,               // Embedding strength (0.1 - 5.0)
  loading: boolean,            // Request in progress
  result: EmbedResult | null,  // API response data
  originalPreview: string | null, // Blob URL for preview
  error: string | null         // Error message
}

// Extract Tab State
const extractState = {
  originalFile: File | null,   // Original image file
  suspectFile: File | null,    // Suspect image file
  loading: boolean,
  result: ExtractResult | null,
  originalPreview: string | null,
  suspectPreview: string | null,
  error: string | null
}

// Verify Tab State (managed by VerifyTab component)
const verifyState = {
  file: File | null,
  loading: boolean,
  result: VerifyResult | null,
  preview: string | null,
  error: string | null
}
```

**Key Principle**: Each tab has completely independent state variables to prevent pollution.

### State Isolation Rules

1. **No Shared File State**: `embedState.file` is separate from `extractState.originalFile`
2. **Tab Switching Preserves State**: Switching tabs does NOT clear state (user can switch back)
3. **Result Clearing**: Uploading a new file clears previous results
4. **Error Handling**: Errors are stored in state and displayed inline, not just in alerts

## Validation Helpers (Frontend)

```javascript
// File validation
function validateImageFile(file) {
  const validTypes = ['image/png', 'image/jpeg', 'image/jpg']
  const maxSize = 10 * 1024 * 1024 // 10MB
  
  if (!file) {
    return { valid: false, error: 'Please select a file' }
  }
  
  if (!validTypes.includes(file.type)) {
    return { 
      valid: false, 
      error: `Invalid format. Please upload PNG or JPG (got ${file.type})` 
    }
  }
  
  if (file.size > maxSize) {
    return { 
      valid: false, 
      error: `File too large. Maximum size is 10MB (got ${(file.size / 1024 / 1024).toFixed(2)}MB)` 
    }
  }
  
  return { valid: true }
}

// Text validation
function validateWatermarkText(text) {
  const trimmed = text.trim()
  const maxLength = 240
  
  if (trimmed.length === 0) {
    return { valid: false, error: 'Watermark text cannot be empty' }
  }
  
  if (trimmed.length > maxLength) {
    return { 
      valid: false, 
      error: `Text too long. Maximum ${maxLength} characters (currently ${trimmed.length})` 
    }
  }
  
  return { valid: true, value: trimmed }
}

// Alpha validation
function validateAlpha(alpha) {
  const min = 0.1
  const max = 5.0
  
  if (isNaN(alpha)) {
    return { valid: false, error: 'Alpha must be a number' }
  }
  
  if (alpha < min || alpha > max) {
    return { 
      valid: false, 
      error: `Alpha must be between ${min} and ${max} (got ${alpha})` 
    }
  }
  
  return { valid: true }
}
```

## Summary

This data model establishes:

1. **Standardized Error Responses**: All errors follow the same structure with clear codes and messages
2. **Validated Request Structures**: Clear requirements for each endpoint's input
3. **Comprehensive Response Models**: Well-defined success responses with metadata
4. **State Isolation**: Frontend state management that prevents cross-tab pollution
5. **Client-Side Validation**: Pre-flight checks to catch errors before API calls

These models will be implemented in:
- Backend: `backend/src/api/schemas.py` (Pydantic models)
- Backend: `backend/src/api/routes.py` (validation logic)
- Frontend: `frontend/src/App.jsx` (state management and validation)
- Frontend: `frontend/src/services/api.js` (error handling)

**Next Steps**: Create OpenAPI contract (`contracts/error-responses.yaml`) and testing guide (`quickstart.md`)
