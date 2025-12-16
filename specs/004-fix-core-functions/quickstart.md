# Quickstart Testing Guide: Fix Core Functions

**Feature**: 004-fix-core-functions  
**Date**: 2025年12月16日  
**Purpose**: Step-by-step guide to test all three fixed functions and validate the bug fixes

## Prerequisites

### Required Software
- Python 3.11+ with pip
- Node.js 18+ with npm
- Git (to switch branches)

### Required Dependencies

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
```

### Test Images
Prepare the following test images in `test-assets/` folder:
- `test_image.png` - Clean 1080p image (no watermark)
- `test_image.jpg` - JPEG version
- `invalid.webp` - WebP format (for error testing)
- `large_image.png` - Image > 10MB (for error testing)

## Setup Instructions

### 1. Start Backend Server

```bash
cd backend
python main.py
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verification**:
```bash
curl http://localhost:8000/v1/health
# Should return: {"status":"ok","service":"InvisiGuard API"}
```

### 2. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

**Expected Output**:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 3. Open Application

Navigate to: http://localhost:5173/

**Expected**: 
- Page loads successfully
- "System Online" indicator shows green
- Three tabs visible: "Embed Watermark", "Extract (With Original)", "Verify (Blind)"

---

## Test Scenarios

### Test Suite 1: Fix Embed 400 Error ✅

#### Test 1.1: Basic Embed (PNG)

**Steps**:
1. Click "Embed Watermark" tab
2. Drag & drop `test_image.png` into upload zone
3. Enter text: "Hello World"
4. Set alpha slider to 1.0
5. Click "Embed Watermark" button

**Expected Result**:
- ✅ **No 400 error**
- ✅ Status "System Online" remains green
- ✅ Loading spinner appears briefly
- ✅ Result displays with side-by-side comparison
- ✅ PSNR and SSIM metrics shown
- ✅ "Download Watermarked Image" button appears

**Failure Indicators**:
- ❌ Alert: "Error embedding watermark"
- ❌ Browser console shows 400 status
- ❌ Network tab shows Content-Type with no boundary

**If Failed**: Check that frontend does NOT manually set `Content-Type: multipart/form-data` header

#### Test 1.2: Basic Embed (JPG)

**Steps**: Same as 1.1, but use `test_image.jpg`

**Expected**: Same success as 1.1

#### Test 1.3: Invalid Format Error

**Steps**:
1. Try to upload `invalid.webp`

**Expected**:
- ✅ Error message: "Invalid format. Please upload PNG or JPG"
- ✅ Alert shown before API call (client-side validation)

#### Test 1.4: Empty Text Error

**Steps**:
1. Upload valid image
2. Leave text field empty (or only spaces)
3. Click "Embed Watermark"

**Expected**:
- ✅ Error message: "Watermark text cannot be empty"
- ✅ Alert shown before API call

#### Test 1.5: Invalid Alpha Error

**Steps**:
1. Upload valid image
2. Enter text
3. Manually set alpha to -1 or 100 (via browser DevTools console if slider prevents it)
4. Click "Embed Watermark"

**Expected**:
- ✅ Client-side validation prevents invalid values
- ✅ OR backend returns 400 with clear error message

#### Test 1.6: File Too Large Error

**Steps**:
1. Try to upload `large_image.png` (>10MB)

**Expected**:
- ✅ Error message: "File too large. Maximum size is 10MB"
- ✅ Alert shown before API call

#### Test 1.7: Download Functionality

**Steps**:
1. Complete a successful embed
2. Click "Download Watermarked Image" button

**Expected**:
- ✅ Image downloads directly (filename: `watermarked_image.png`)
- ✅ **No new browser tab opens**
- ✅ Downloaded image is valid and can be opened

---

### Test Suite 2: Fix Extract Upload Issue ✅

#### Test 2.1: Independent File Upload

**Steps**:
1. Go to "Embed Watermark" tab
2. Upload and embed `test_image.png` with text "Original"
3. Download the watermarked image (save as `watermarked.png`)
4. Switch to "Extract (With Original)" tab
5. Upload `test_image.png` as "Original Image"
6. Upload `watermarked.png` as "Suspect Image"

**Expected Result**:
- ✅ Both upload zones accept files independently
- ✅ Preview images show for both uploads
- ✅ Filenames displayed correctly
- ✅ Extract state is NOT affected by Embed state
- ✅ Green checkmark "✓ Original image loaded" appears
- ✅ Green checkmark "✓ Suspect image loaded" appears

**Failure Indicators**:
- ❌ Uploading original overwrites suspect (or vice versa)
- ❌ No preview images shown
- ❌ Upload zones look disabled or non-interactive
- ❌ Files from Embed tab auto-populate in Extract tab

#### Test 2.2: Missing File Validation

**Steps**:
1. Upload only Original Image (not Suspect)
2. Click "Extract Watermark"

**Expected**:
- ✅ Button is disabled (gray)
- ✅ Error message: "Please upload both images before extracting"

#### Test 2.3: Successful Extraction

**Steps**:
1. Upload both images (original + watermarked)
2. Click "Extract Watermark"

**Expected**:
- ✅ Loading spinner appears
- ✅ Result displays extracted text: "Original"
- ✅ Confidence score shown
- ✅ No errors

#### Test 2.4: State Isolation Between Tabs

**Steps**:
1. Embed watermark in "Embed Watermark" tab
2. Switch to "Extract (With Original)" tab (should be blank)
3. Upload files for extraction
4. Switch back to "Embed Watermark" tab
5. Switch to "Extract (With Original)" again

**Expected**:
- ✅ Extract tab does NOT show files from Embed tab
- ✅ Extract tab REMEMBERS its own uploaded files when switching back
- ✅ Each tab maintains independent state

---

### Test Suite 3: Fix Verify Extraction Failure ✅

#### Test 3.1: Verify Embedded Watermark (Unmodified)

**Steps**:
1. Go to "Embed Watermark" tab
2. Upload `test_image.png`, embed text "SecretMessage123", alpha 1.0
3. Download watermarked image (save as `watermarked_secret.png`)
4. Go to "Verify (Blind)" tab
5. Upload `watermarked_secret.png`
6. Click "Verify Watermark"

**Expected Result**:
- ✅ **NO 400 or 500 error**
- ✅ Status shows: "Verified: ✓"
- ✅ Extracted text: "SecretMessage123"
- ✅ Confidence: 1.0 or close to 1.0
- ✅ No garbled characters or random text

**Failure Indicators**:
- ❌ Empty text returned
- ❌ Garbled text (e.g., "���" or random characters)
- ❌ Error: "No Watermark Detected" (for a clearly watermarked image)
- ❌ Error: "Reed-Solomon decoding failed"

**If Failed**:
- Check DWT/QIM parameters match between embed and extract
- Check payload parsing logic (header "INV", length byte)
- Check UTF-8 encoding/decoding
- Add logging to see exact bytes extracted

#### Test 3.2: Verify with No Watermark

**Steps**:
1. Upload original `test_image.png` (no watermark) to Verify tab
2. Click "Verify Watermark"

**Expected**:
- ✅ Status shows: "Verified: ✗"
- ✅ Message: "No Watermark Detected"
- ✅ Confidence: 0.0
- ✅ **No crash or error**

#### Test 3.3: Verify with Rotation

**Steps**:
1. Create watermarked image as in 3.1
2. Open watermarked image in image editor
3. Rotate 15 degrees
4. Save as `watermarked_rotated.png`
5. Upload to Verify tab

**Expected**:
- ✅ Sync template detects rotation
- ✅ Geometry corrected automatically
- ✅ Extracted text: "SecretMessage123"
- ✅ Metadata shows: "rotation_detected: 15.0"

**Note**: This test may fail if:
- Sync template not embedded correctly
- Blind alignment algorithm has bugs
- Rotation exceeds ±45° threshold

#### Test 3.4: Verify with Scale

**Steps**:
1. Create watermarked image
2. Resize to 70% or 130% scale
3. Save and upload to Verify tab

**Expected**:
- ✅ Scale detected and corrected
- ✅ Text extracted successfully

---

## Regression Checklist

After all fixes are implemented, verify:

### Embed Function
- [ ] PNG images embed successfully (no 400 error)
- [ ] JPG images embed successfully
- [ ] Invalid formats show clear error messages
- [ ] Empty text shows clear error message
- [ ] Invalid alpha shows clear error message
- [ ] Large files (>10MB) show clear error message
- [ ] Download button works (no new tab)
- [ ] PSNR and SSIM metrics displayed
- [ ] Signal map generated

### Extract Function
- [ ] Can upload two separate files independently
- [ ] Preview images display correctly
- [ ] State does NOT pollute from Embed tab
- [ ] Missing file shows clear validation message
- [ ] Extract button disabled until both files uploaded
- [ ] Successful extraction shows text and confidence
- [ ] Geometric alignment works for rotated/scaled images

### Verify Function
- [ ] Embedded watermark extracted correctly (exact text match)
- [ ] No watermark returns "No Watermark Detected" (not an error)
- [ ] No garbled characters or random text
- [ ] UTF-8 text handled correctly
- [ ] Rotated images verified successfully (±30°)
- [ ] Scaled images verified successfully (70%-130%)
- [ ] Reed-Solomon decoding works
- [ ] Payload header "INV" validated
- [ ] Length byte parsed correctly

### Error Handling
- [ ] All error messages are clear and actionable
- [ ] No generic "Error embedding watermark" messages
- [ ] Frontend validates inputs before API calls
- [ ] Backend returns structured error responses
- [ ] HTTP status codes used correctly (400 vs 500)
- [ ] Error suggestions provided

### UI/UX
- [ ] Loading spinners show during processing
- [ ] Buttons disabled during loading
- [ ] Tab switching preserves state
- [ ] File upload zones are clearly labeled
- [ ] Preview images display for all tabs
- [ ] Success indicators (✓) show after upload

---

## Debugging Tips

### If Embed Still Returns 400

1. **Check Browser DevTools Network Tab**:
   - Look at the `/api/v1/embed` request
   - Check Headers → Request Headers
   - Verify `Content-Type: multipart/form-data; boundary=----WebKit...` (boundary MUST be present)
   - If boundary is missing, frontend is still manually setting Content-Type

2. **Check Backend Logs**:
   ```bash
   # In backend terminal
   # Look for Python tracebacks or FastAPI validation errors
   ```

3. **Test with cURL**:
   ```bash
   curl -X POST http://localhost:8000/v1/embed \
     -F "file=@test_image.png" \
     -F "text=TestText" \
     -F "alpha=1.0"
   ```
   If this works but frontend doesn't, issue is definitely in frontend.

### If Extract Upload Doesn't Work

1. **Check React State**:
   - Open browser DevTools → React Developer Tools
   - Inspect `App` component
   - Check `extractOriginal` and `extractSuspect` state values
   - Switch tabs and verify state persists

2. **Add Console Logging**:
   ```javascript
   const handleExtractOriginalSelect = (file) => {
     console.log('[Extract] Original selected:', file?.name)
     setExtractOriginal(file)
   }
   ```

### If Verify Extraction Fails

1. **Enable Verbose Logging**:
   ```python
   # In backend/src/core/extraction.py
   def extract_with_blind_alignment(self, suspect):
       print("[VERIFY] Starting blind extraction")
       rotation, scale = detect_rotation_scale(suspect)
       print(f"[VERIFY] Detected: rotation={rotation}, scale={scale}")
       # ... rest of code
   ```

2. **Test Embed/Extract Cycle**:
   ```python
   # backend/tests/test_blind_verify.py
   pytest backend/tests/test_blind_verify.py -v -s
   ```

3. **Check Parameter Consistency**:
   ```python
   # Compare these values:
   # embedding.py: WatermarkEmbedder.WAVELET, LEVEL, DELTA
   # extraction.py: WatermarkExtractor.WAVELET, LEVEL, DELTA
   # They MUST match exactly
   ```

---

## Expected Test Results Summary

| Test Case | Expected Outcome | Pass Criteria |
|-----------|------------------|---------------|
| Embed PNG | Success, image downloaded | No 400 error |
| Embed JPG | Success, image downloaded | No 400 error |
| Embed Invalid Format | Clear error message | Client-side validation |
| Embed Empty Text | Clear error message | Client-side validation |
| Extract Two Files | Both files upload independently | Previews show |
| Extract Missing File | Button disabled, error message | Validation works |
| Extract Successful | Text extracted correctly | Matches embedded text |
| Verify Watermarked | Text extracted, verified=true | Exact text match |
| Verify No Watermark | "No Watermark Detected", verified=false | No crash |
| Verify Rotated | Text extracted, rotation detected | Sync template works |

**Success Rate Target**: 100% (all test cases pass)

---

## Post-Fix Validation

After implementing all fixes, run the full regression test:

1. **Start fresh** (clear browser cache, restart servers)
2. **Run all 3 test suites** in order
3. **Check all items** in Regression Checklist
4. **Document any failures** with screenshots and console logs
5. **Verify Success Criteria** from `spec.md` are met

**Sign-off**: All three reported issues (Embed 400, Extract upload, Verify extraction) are resolved when all tests pass.

---

**Phase 1 Status**: ✅ COMPLETE  
**Next Step**: Execute `/speckit.tasks` to generate detailed implementation tasks
