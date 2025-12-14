# Phase 0: Research & Decisions

**Feature**: Fixes & Polish (Verify, Extract, Embed)
**Date**: 2025-12-15

## 1. Garbage Decoding in Verify

**Problem**: The current `Verify` function extracts bits from every 8x8 block in the image and converts them to ASCII. Since most blocks contain noise or image data, this results in a stream of random characters.

**Research**:
-   **Current Implementation**: `extraction.py` iterates over all blocks, extracts bits, and converts to string.
-   **Solution**: Implement a structured payload with a **Header/Preamble**.
    -   **Header**: A unique bit sequence (e.g., `[INV]` in ASCII) to identify the start of the message.
    -   **Length**: A fixed-width field (e.g., 8 bits) indicating the length of the message.
    -   **Data**: The actual watermark text.
-   **Algorithm**:
    1.  Extract bits from the image.
    2.  Scan the bit stream for the Header sequence.
    3.  If found, read the next 8 bits to get Length `L`.
    4.  Read the next `L * 8` bits to get the message.
    5.  If Header not found, return "No Watermark Detected".

**Decision**: Use `[INV]` (3 bytes) as the header. Structure: `[Header: 24 bits][Length: 8 bits][Data: Variable]`.

## 2. Extract Tab Upload Conflict

**Problem**: Uploading a file in the Embed tab automatically sets it as the "Original" for the Extract tab. This "convenience" feature causes confusion and state overwrites when the user actually wants to use the Extract tab with different files.

**Research**:
-   **Code**: `App.jsx` -> `handleFileSelect` updates both `file` (Embed) and `extractOriginal` (Extract).
-   **Solution**: Decouple the handlers.
    -   `Embed` tab should have its own `handleEmbedUpload`.
    -   `Extract` tab should have two separate uploaders: `handleExtractOriginal` and `handleExtractSuspect`.

**Decision**: Remove the auto-set convenience. Create distinct handlers for each input.

## 3. Embed Tab UX

**Problem**:
1.  No easy way to download the result.
2.  Attack Simulator is cluttering the Embed tab.

**Research**:
-   **Download**: The API returns a URL (`/static/...`). We can add a simple `<a href="..." download>` button.
-   **Attack Simulator**: It is currently rendered in the Embed tab (likely below the fold of my previous read).

**Decision**:
-   Add a "Download Watermarked Image" button next to the result.
-   Remove `<AttackSimulator />` from the Embed tab conditional rendering block.

## 4. UI Clarity

**Problem**: Users confuse "Extract" and "Verify".

**Decision**:
-   Rename tabs in UI:
    -   "Embed" -> "Embed Watermark"
    -   "Extract" -> "Extract (With Original)"
    -   "Verify" -> "Verify (Blind)"
-   Add tooltips or helper text explaining the difference.
