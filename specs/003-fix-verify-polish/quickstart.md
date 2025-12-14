# Quickstart: Testing Fixes & Polish

**Feature**: Fixes & Polish (Verify, Extract, Embed)

## Prerequisites
-   Backend running: `uvicorn src.main:app --reload`
-   Frontend running: `npm run dev`

## 1. Verify "Blind Verify" Fix
1.  Navigate to **Embed** tab.
2.  Upload an image and embed text "Secret123".
3.  Download the result.
4.  Navigate to **Verify (Blind)** tab.
5.  Upload the downloaded image.
6.  **Success**: Result shows "Secret123".
7.  Upload a random non-watermarked image.
8.  **Success**: Result shows "No Watermark Detected" (not random garbage).

## 2. Verify Extract Uploads
1.  Navigate to **Extract (With Original)** tab.
2.  Upload `ImageA.png` to "Original".
3.  Upload `ImageB.png` to "Suspect".
4.  Ensure both files are visible and distinct.
5.  Navigate to **Embed** tab and upload `ImageC.png`.
6.  Return to **Extract** tab.
7.  **Success**: "Original" is still `ImageA.png` (not overwritten by `ImageC.png`).

## 3. Verify Embed UX
1.  Navigate to **Embed** tab.
2.  Embed a watermark.
3.  **Success**: A "Download" button appears. Clicking it downloads the file.
4.  **Success**: The "Attack Simulator" section is NOT visible on this tab.
