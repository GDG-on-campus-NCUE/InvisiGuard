# Data Model & Schema

**Feature**: Fixes & Polish
**Version**: 1.0

## Watermark Payload Structure

The watermark payload is embedded into the image's DCT coefficients. It is a binary stream constructed as follows:

| Field | Size | Type | Description |
|-------|------|------|-------------|
| **Header** | 24 bits | Fixed | ASCII string `[INV]` (`01011011 01001001 01001110 01010110 01011101`). Used to detect presence of watermark. |
| **Length** | 8 bits | Integer | Length of the data string in bytes (characters). Max length 255. |
| **Data** | Variable | String | The watermark text (ASCII). |

### Example

Text: "Test"

1.  **Header**: `[INV]` -> `01011011 01001001 01001110 01010110 01011101`
2.  **Length**: `4` -> `00000100`
3.  **Data**: `Test` -> `01010100 01100101 01110011 01110100`

**Total Bits**: 24 + 8 + 32 = 64 bits.

## Frontend State Model (`App.jsx`)

### Embed Tab State
-   `embedFile`: File object (Input image)
-   `embedText`: String (Watermark text)
-   `embedAlpha`: Float (Strength)
-   `embedResult`: Object (API response)

### Extract Tab State
-   `extractOriginal`: File object (Reference image)
-   `extractSuspect`: File object (Suspect image)
-   `extractResult`: Object (API response)

### Verify Tab State
-   `verifyFile`: File object (Suspect image)
-   `verifyResult`: Object (API response)
