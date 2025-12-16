# Implementation Plan: Fix Core Functions (Embed, Extract, Verify)

**Branch**: `004-fix-core-functions` | **Date**: 2025年12月16日 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-fix-core-functions/spec.md`

**Note**: This plan addresses three critical bugs preventing core watermarking functions from working properly.

## Summary

This implementation plan addresses three high-priority issues preventing the InvisiGuard watermarking system from functioning:

1. **Embed Function Returns Status 400**: Users cannot embed watermarks due to API request failures
2. **Extract Tab Cannot Upload Images**: File upload state management conflicts prevent users from uploading images in the Extract tab
3. **Verify Function Cannot Extract Messages**: Blind verification fails to extract watermark text from images

The technical approach involves:
- Diagnosing and fixing frontend-backend communication issues for the Embed endpoint
- Refactoring React state management to separate file upload states across tabs
- Debugging and fixing the blind verification extraction logic, including DWT/QIM parameter consistency and payload parsing

## Technical Context

**Language/Version**: 
- Frontend: JavaScript (ES2020+), React 18.2
- Backend: Python 3.11+

**Primary Dependencies**: 
- Frontend: React 18, Vite 5.0, Axios 1.6, Tailwind CSS 3.4
- Backend: FastAPI 0.109, OpenCV (cv2) 4.9, NumPy 1.26, SciPy 1.12, PyWavelets 1.5, reedsolo 1.7

**Storage**: 
- Temporary file storage in `backend/static/processed/` and `backend/static/debug/`
- No persistent database required

**Testing**: 
- Frontend: Vitest, React Testing Library
- Backend: pytest with async support

**Target Platform**: 
- Development: localhost (frontend: 5173, backend: 8000)
- Browser: Chrome, Firefox, Safari (latest versions)
- OS: Cross-platform (Windows, macOS, Linux)

**Project Type**: Web application (frontend + backend)

**Performance Goals**: 
- Embed operation: < 5 seconds for 1080p images
- Extract operation: < 10 seconds for 1080p images
- Verify operation: < 10 seconds for 1080p images
- API response time: < 100ms for non-processing endpoints

**Constraints**: 
- File size limit: 10MB per upload
- Image resolution limit: 4K (3840x2160)
- Supported formats: PNG, JPG, JPEG only
- Maximum watermark text length: ~240 characters (with Reed-Solomon ECC overhead)

**Scale/Scope**: 
- Single-user development tool
- No concurrent user considerations needed
- 3 core endpoints to fix
- Focus on debugging existing implementation, not new features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Architecture Check ✅
- **Status**: PASS
- **Rationale**: Existing architecture maintains clear boundaries between API layer (`routes.py`), service layer (`watermark.py`), and core algorithms (`embedding.py`, `extraction.py`, `geometry.py`). This fix maintains the same structure.

### Error Handling Check ⚠️
- **Status**: NEEDS IMPROVEMENT
- **Current Issue**: Backend returns generic 400/500 errors without clear messages
- **Fix Required**: Add detailed error messages with suggestions (FR-005)
- **Action**: Enhance exception handling in all three endpoints

### Testing Check ⚠️
- **Status**: NEEDS IMPROVEMENT
- **Current Issue**: No unit test coverage for the three affected functions
- **Fix Required**: Add regression tests for Embed, Extract, and Verify
- **Action**: Create test cases for each acceptance scenario

### State Management Check ⚠️
- **Status**: NEEDS IMPROVEMENT  
- **Current Issue**: Frontend state pollution between Embed and Extract tabs
- **Fix Required**: Separate state variables for each tab (FR-003)
- **Action**: Refactor App.jsx to use independent state for each function

### Security Check ✅
- **Status**: PASS
- **Rationale**: Existing file type and size validation in place; no security regression expected from these fixes

### Summary
**Overall Status**: CONDITIONAL PASS - proceed with Phase 0, but address the three ⚠️ items during implementation

## Project Structure

### Documentation (this feature)

```text
specs/004-fix-core-functions/
├── plan.md              # This file (current)
├── research.md          # Phase 0: Root cause analysis
├── data-model.md        # Phase 1: Error response models
├── quickstart.md        # Phase 1: Testing guide
├── contracts/           # Phase 1: API error schemas
│   └── error-responses.yaml
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2: Detailed task breakdown (NOT created yet)
```

### Source Code (repository root)

```text
backend/
├── main.py                      # FastAPI entry point
├── src/
│   ├── api/
│   │   ├── routes.py           # [FIX] /v1/embed, /v1/extract, /v1/verify endpoints
│   │   └── schemas.py          # [FIX] Add error response models
│   ├── core/
│   │   ├── embedding.py        # [DEBUG] DWT/QIM embed logic, text_to_bits
│   │   ├── extraction.py       # [DEBUG] DWT/QIM extract logic, payload parsing
│   │   ├── geometry.py         # [CHECK] Blind alignment (sync template)
│   │   └── processor.py        # [CHECK] Image loading/validation
│   └── services/
│       └── watermark.py        # [FIX] Service orchestration layer
└── tests/
    ├── test_embed_fix.py       # [NEW] Regression tests for Embed 400
    ├── test_extract_fix.py     # [NEW] Tests for Extract workflow
    └── test_verify_fix.py      # [NEW] Tests for Verify extraction

frontend/
├── src/
│   ├── App.jsx                 # [FIX] State management refactor
│   ├── components/
│   │   ├── Dropzone.jsx        # [CHECK] File upload handling
│   │   ├── ConfigPanel.jsx     # [CHECK] Input validation
│   │   └── VerifyTab.jsx       # [CHECK] Verify UI
│   └── services/
│       └── api.js              # [CHECK] Axios config and error handling
└── tests/
    └── App.test.jsx            # [UPDATE] Add state isolation tests
```

**Structure Decision**: The existing web application structure (frontend + backend) is maintained. All fixes are in-place modifications to existing files, with new test files added to validate the fixes. No new directories or major restructuring required.

## Complexity Tracking

> **No violations** - This is a bug fix effort that maintains existing architectural patterns. No new complexity is introduced; the focus is on debugging and correcting existing implementations.

## Phase 0: Root Cause Analysis & Research

**Goal**: Diagnose the exact causes of the three reported issues through systematic investigation.

### Research Tasks

#### R001: Diagnose Embed 400 Error
**Investigation Areas**:
- Frontend FormData construction in `App.jsx::handleEmbed`
- Backend FastAPI parameter binding in `routes.py::embed_watermark`
- CORS and proxy configuration between Vite (5173) and FastAPI (8000)
- Content-Type header handling
- File format validation in `processor.py::load_image`

**Expected Findings**:
- Root cause of 400 error (likely: incorrect FormData field names, parameter validation failure, or CORS preflight issue)
- Whether the issue is frontend, backend, or configuration

**Deliverable**: `research.md` section documenting:
- Exact error message and stack trace
- Confirmed root cause
- Recommended fix approach

#### R002: Diagnose Extract Upload Issue
**Investigation Areas**:
- React state variable naming and scope in `App.jsx`
- File upload event handlers (`handleEmbedFileSelect` vs Extract handlers)
- State pollution between tabs (does Embed state affect Extract?)
- Dropzone component reuse and prop passing

**Expected Findings**:
- Identification of shared state variables causing conflicts
- Whether the issue is state management or component binding

**Deliverable**: `research.md` section documenting:
- State variable flow diagram
- Identified conflicts
- Proposed state refactoring strategy

#### R003: Diagnose Verify Extraction Failure
**Investigation Areas**:
- DWT/QIM parameter consistency between `embedding.py` and `extraction.py`
- Reed-Solomon encoding/decoding parameters (N_ECC_SYMBOLS, block size)
- Payload header and length byte parsing in `extraction.py::_parse_payload`
- Blind alignment logic in `geometry.py::detect_rotation_scale`
- Sync template embedding and detection

**Expected Findings**:
- Whether embed and extract use matching algorithm parameters
- Payload parsing bugs (header validation, length reading, UTF-8 decoding)
- Whether blind alignment is working correctly

**Deliverable**: `research.md` section documenting:
- Algorithm parameter comparison table
- Payload structure diagram
- Confirmed bugs and fix strategy

#### R004: Error Handling Best Practices
**Research Questions**:
- What HTTP status codes should be used for different error types?
- How to structure error responses with helpful messages?
- What client-side validation should occur before API calls?

**Expected Findings**:
- Standard error response schema
- Client-side validation rules
- User-friendly error message templates

**Deliverable**: `research.md` section with error handling guidelines

### Research Output: `research.md`
Structure:
```markdown
# Root Cause Analysis: Core Function Failures

## Issue 1: Embed 400 Error
### Symptoms
### Investigation Process
### Root Cause
### Recommended Fix

## Issue 2: Extract Upload Failure
### Symptoms
### Investigation Process  
### Root Cause
### Recommended Fix

## Issue 3: Verify Extraction Failure
### Symptoms
### Investigation Process
### Root Cause
### Recommended Fix

## Error Handling Standards
### HTTP Status Code Usage
### Error Response Schema
### Client-Side Validation Rules
```

## Phase 1: Design & Contracts

**Goal**: Define the corrected data models, API error contracts, and testing strategy based on Phase 0 findings.

**Prerequisites**: `research.md` must be complete with all root causes identified.

### Design Outputs

#### D001: Error Response Data Model (`data-model.md`)

**Purpose**: Standardize error responses across all three endpoints

**Entities**:

1. **ErrorResponse**
   - `status`: string (always "error")
   - `error_code`: string (e.g., "INVALID_IMAGE_FORMAT", "TEXT_REQUIRED")
   - `message`: string (user-friendly description)
   - `details`: object (optional, technical details)
   - `suggestion`: string (optional, what user should do next)

2. **ValidationError**
   - Extends ErrorResponse
   - `field`: string (which input field failed)
   - `value_provided`: string (what was sent)
   - `expected`: string (what format is required)

3. **ProcessingError**
   - Extends ErrorResponse
   - `stage`: string (which processing stage failed)
   - `recoverable`: boolean (can user retry?)

**Example Error Responses**:
```json
// Embed 400 - Invalid Alpha
{
  "status": "error",
  "error_code": "INVALID_ALPHA_RANGE",
  "message": "Alpha value must be between 0.1 and 5.0",
  "details": {"provided": 100, "min": 0.1, "max": 5.0},
  "suggestion": "Adjust the strength slider to a valid range"
}

// Extract - Missing File
{
  "status": "error",
  "error_code": "MISSING_FILE",
  "message": "Both original and suspect images are required",
  "details": {"missing": ["suspect_file"]},
  "suggestion": "Please upload both images before clicking Extract"
}

// Verify - No Watermark Detected
{
  "status": "success",
  "data": {
    "verified": false,
    "watermark_text": "",
    "confidence": 0.0,
    "message": "No Watermark Detected"
  }
}
```

**Deliverable**: `data-model.md` with complete error entity definitions

#### D002: API Error Contracts (`contracts/error-responses.yaml`)

**Purpose**: OpenAPI schema for standardized error responses

**Content**:
- Error response schema definitions
- Mapping of HTTP status codes to error types
- Example responses for each endpoint's error cases

**Structure**:
```yaml
components:
  schemas:
    ErrorResponse:
      type: object
      required: [status, error_code, message]
      properties:
        status: {type: string, enum: [error]}
        error_code: {type: string}
        message: {type: string}
        details: {type: object}
        suggestion: {type: string}
    
  responses:
    BadRequest:
      description: Invalid request parameters
      content:
        application/json:
          schema: {$ref: '#/components/schemas/ErrorResponse'}
          examples:
            invalid_alpha:
              value: {status: error, error_code: INVALID_ALPHA_RANGE, ...}
```

**Deliverable**: `contracts/error-responses.yaml` with complete OpenAPI schema

#### D003: Testing & Validation Quickstart (`quickstart.md`)

**Purpose**: Guide for testing the fixes and validating all three functions work correctly

**Content**:
1. **Setup Instructions**
   - Start backend: `cd backend && python main.py`
   - Start frontend: `cd frontend && npm run dev`
   - Verify health check: `curl http://localhost:8000/v1/health`

2. **Test Scenarios**
   - **Embed Test**: Upload `test_image.png`, text "Hello", alpha 1.0 → expect success
   - **Extract Test**: Upload original + rotated version → expect correct text
   - **Verify Test**: Upload watermarked image → expect verification success
   - **Error Tests**: Test all error cases (invalid format, empty text, etc.)

3. **Expected Behaviors**
   - All acceptance scenarios from spec.md
   - Edge case handling
   - Error message validation

4. **Regression Checklist**
   - [ ] Embed returns 200 (not 400) for valid inputs
   - [ ] Extract tab accepts two separate file uploads
   - [ ] Verify extracts correct text from watermarked images
   - [ ] All error messages are clear and actionable

**Deliverable**: `quickstart.md` with complete testing guide

### Design Validation

After completing D001-D003, update the **Constitution Check** section:
- ✅ Error Handling: Now provides clear, actionable error messages
- ✅ Testing: Regression test plan documented
- ✅ State Management: Refactoring strategy defined

## Phase 2: Task Breakdown (NOT PART OF /speckit.plan)

**Note**: Phase 2 task generation is handled by the `/speckit.tasks` command, which will:
- Break down each fix into atomic implementation tasks
- Assign task IDs and dependencies
- Map tasks to specific files and functions
- Define acceptance criteria for each task

This plan document stops after Phase 1 design completion. Execute `/speckit.tasks` next to generate the detailed task list.

## Implementation Notes

### Critical Path
1. **Phase 0 Research** → Identify all three root causes
2. **Phase 1 Design** → Define error contracts and test strategy
3. **Phase 2 Tasks** (via `/speckit.tasks`) → Generate granular task breakdown
4. **Implementation** (via `/speckit.implement`) → Execute fixes with validation

### Risk Mitigation
- **Risk**: Fixing one function breaks another
  - **Mitigation**: Comprehensive regression tests for all three functions
- **Risk**: DWT/QIM parameter mismatch not detected
  - **Mitigation**: Create parameter validation unit tests
- **Risk**: State refactoring introduces new bugs
  - **Mitigation**: Test state isolation between tabs

### Success Criteria Mapping
- **SC-001** (Embed success rate 100%) → Fix Issue 1
- **SC-002** (Extract upload 100%) → Fix Issue 2
- **SC-003** (Verify accuracy 85%+) → Fix Issue 3
- **SC-004** (Clear errors 100%) → Implement error models from Phase 1
- **SC-005** (All issues resolved) → Pass all regression tests

## Next Steps

1. ✅ **Completed**: Specification (`spec.md`) and Planning (`plan.md`)
2. ⏳ **Current**: Execute Phase 0 Research
   - Command: Continue with research task execution (part of `/speckit.plan`)
3. ⏳ **Next**: Execute Phase 1 Design
   - Generate `data-model.md`, `contracts/`, `quickstart.md`
4. ⏸️ **Pending**: Task Generation
   - Command: `/speckit.tasks` (separate step after this plan completes)
5. ⏸️ **Pending**: Implementation
   - Command: `/speckit.implement` (execute after tasks are defined)
