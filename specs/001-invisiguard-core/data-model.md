# Data Models

## Entities

### WatermarkRequest
Represents a request to embed a watermark into an image.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| file | File | Yes | JPEG, PNG; Max 10MB | The source image. |
| text | String | Yes | Max 32 chars | The text to embed. ASCII only recommended. |
| alpha | Float | No | 0.1 - 5.0 (Default: 1.0) | Embedding strength. Higher = more robust but less invisible. |

### WatermarkResponse
The result of the embedding process.

| Field | Type | Description |
|---|---|---|
| image_url | String | URL to the processed image. |
| psnr | Float | Peak Signal-to-Noise Ratio. Measure of quality (typical > 35dB). |
| ssim | Float | Structural Similarity Index. Measure of similarity (typical > 0.9). |

### ExtractionRequest
Represents a request to extract a watermark from a suspect image, using an original image for alignment.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| original_file | File | Yes | JPEG, PNG | The original image (ground truth) for geometric alignment. |
| suspect_file | File | Yes | JPEG, PNG | The suspect image (e.g., screenshot, photo). |

### ExtractionResponse
The result of the extraction process.

| Field | Type | Description |
|---|---|---|
| decoded_text | String | The extracted text. |
| confidence | Float | Confidence score (0.0 - 1.0) based on bit matching rate. |
| is_match | Boolean | True if confidence > threshold (e.g., 0.85). |
| debug_info | Object | Contains details like `aligned_image_url`, `matches_found`. |

## Validation Rules

1.  **File Type**: Only `image/jpeg` and `image/png` are supported.
2.  **File Size**: Maximum 10MB to prevent DoS.
3.  **Text Length**: Maximum 32 characters. Longer text requires more bits, reducing robustness or requiring larger image area.
4.  **Alpha**: Must be positive. Values > 5.0 degrade image quality significantly.
