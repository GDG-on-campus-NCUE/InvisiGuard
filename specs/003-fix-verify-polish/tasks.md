# Tasks: Fixes & Polish (Verify, Extract, Embed)

**Feature Branch**: `003-fix-verify-polish`
**Spec**: [specs/003-fix-verify-polish/spec.md](spec.md)
**Status**: In Progress

## Phase 1: Setup
*Goal: Prepare environment for fixes.*

- [x] T001 Verify backend environment and dependencies are installed

## Phase 2: User Story 1 - Reliable Blind Verification
*Goal: Ensure Verify function returns accurate text or "No Watermark" instead of garbage.*
*Priority: P1*

### Tests
- [x] T002 [US1] Create unit tests for payload structure in backend/tests/test_payload.py

### Implementation
- [x] T003 [US1] Implement `text_to_bits` with `[INV]` header and length byte in backend/src/core/embedding.py
- [x] T004 [US1] Implement `bits_to_text` with header validation and length reading in backend/src/core/extraction.py
- [x] T005 [US1] Update `WatermarkEmbedder.embed_watermark_dct` to use new bit generation in backend/src/core/embedding.py
- [x] T006 [US1] Update `WatermarkExtractor.extract_watermark_dct` to handle "No Watermark Detected" case in backend/src/core/extraction.py

## Phase 3: User Story 2 - Embed Tab Usability
*Goal: Improve Embed tab workflow by adding download and removing distractions.*
*Priority: P2*

### Implementation
- [x] T007 [US2] Add "Download Watermarked Image" button to Embed tab results in frontend/src/App.jsx (direct client-side download; no new tab)
- [x] T008 [US2] Remove `AttackSimulator` component from Embed tab conditional rendering in frontend/src/App.jsx

## Phase 4: User Story 3 - Fix Extract Uploads
*Goal: Fix state conflict between Embed and Extract file inputs.*
*Priority: P2*

### Implementation
- [x] T009 [US3] Refactor `App.jsx` state to separate `embedFile`, `extractOriginal`, and `extractSuspect` in frontend/src/App.jsx
- [x] T010 [US3] Create distinct file upload handlers (`handleEmbedUpload`, `handleExtractOriginal`, `handleExtractSuspect`) in frontend/src/App.jsx
- [x] T011 [US3] Update Extract tab UI to use new state variables and handlers in frontend/src/App.jsx

## Phase 5: User Story 4 - UI Clarity
*Goal: Clarify the difference between Extract and Verify tabs.*
*Priority: P3*

### Implementation
- [x] T012 [US4] Rename tabs to "Embed Watermark", "Extract (With Original)", and "Verify (Blind)" in frontend/src/App.jsx
- [x] T013 [US4] Add helper text/tooltips explaining the difference between Extract and Verify in frontend/src/App.jsx

## Phase 6: Polish & Verification
*Goal: Ensure all fixes work together.*

- [x] T014 Run full regression test: Embed -> Download -> Verify (Blind) -> Success (validate file is downloaded directly and no new tab/window opened)
- [x] T015 Run full regression test: Extract (Original + Suspect) -> Success

## Dependencies
- US1 (Backend) is independent of US2, US3, US4 (Frontend).
- US3 (State Refactor) should be done before US2/US4 to avoid merge conflicts in `App.jsx`, though they can be parallelized if careful.

## Parallel Execution Examples
- **Backend Dev**: Work on T002-T006 (US1).
- **Frontend Dev**: Work on T009-T011 (US3), then T007-T008 (US2).

## Implementation Strategy
1.  **Backend First**: Fix the core verification logic (US1) as it's the highest priority bug.
2.  **Frontend Refactor**: Fix the state management (US3) to stop the upload bugs.
3.  **Frontend Polish**: Apply the UX improvements (US2, US4).
