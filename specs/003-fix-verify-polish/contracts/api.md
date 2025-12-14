# API Contracts

**Version**: 1.1 (No changes to signature, internal logic update)

## Endpoints

### POST /api/v1/embed
Embeds a watermark into an image.

**Request (Multipart/Form-Data)**
- `file`: File (Image)
- `text`: String (Watermark text)
- `alpha`: Float (Strength, default 1.0)

**Response (JSON)**
```json
{
  "status": "success",
  "data": {
    "image_url": "/static/processed/...",
    "psnr": 42.5,
    "ssim": 0.98
  }
}
```

### POST /api/v1/extract
Extracts watermark using original image as reference.

**Request (Multipart/Form-Data)**
- `original_file`: File
- `suspect_file`: File

**Response (JSON)**
```json
{
  "status": "success",
  "data": {
    "decoded_text": "Secret123",
    "confidence": 0.95,
    "is_match": true
  }
}
```

### POST /api/v1/verify
Extracts watermark blindly (no reference).

**Request (Multipart/Form-Data)**
- `suspect_file`: File

**Response (JSON)**
```json
{
  "status": "success",
  "data": {
    "decoded_text": "Secret123", // Or "No Watermark Detected"
    "confidence": 0.85,
    "metadata": {
        "rotation_detected": 0,
        "scale_detected": 1.0
    }
  }
}
```
