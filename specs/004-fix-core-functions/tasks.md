# Tasks: Fix Core Functions (Embed, Extract, Verify)

**Feature**: 004-fix-core-functions  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Research**: [research.md](research.md)  
**Status**: `43/56` Tasks Completed (Core implementation complete, testing phase pending)

**Input**: Design documents from `/specs/004-fix-core-functions/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/error-responses.yaml

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup & Shared Infrastructure

**Goal**: Prepare error handling infrastructure and validation utilities

- [X] T001 Create ErrorResponse Pydantic models in backend/src/api/schemas.py
- [X] T002 [P] Create client-side validation helpers in frontend/src/utils/validation.js
- [X] T003 [P] Add backend logging configuration in backend/src/utils/logger.py

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Fix configuration issues that block all three functions

- [X] T004 Review and verify Vite proxy configuration in frontend/vite.config.js
- [X] T005 Review and verify CORS configuration in backend/main.py

## Phase 3: User Story 1 - Fix Embed Function (Priority: P1)

**Goal**: Resolve Status 400 error in watermark embedding workflow

**Independent Test**: Upload PNG, enter "Hello World", alpha 1.0 → expect success (no 400)

**Story Tasks**:

### Backend Fixes
- [X] T006 [US1] Remove/fix Content-Type header handling in backend/src/api/routes.py::embed_watermark
- [X] T007 [US1] Add input validation for file type in backend/src/api/routes.py::embed_watermark
- [X] T008 [US1] Add input validation for text field (non-empty, trimmed) in backend/src/api/routes.py::embed_watermark
- [X] T009 [US1] Add input validation for alpha range (0.1-5.0) in backend/src/api/routes.py::embed_watermark
- [X] T010 [US1] Implement structured error responses with error codes in backend/src/api/routes.py::embed_watermark
- [X] T011 [P] [US1] Add error logging with context in backend/src/api/routes.py::embed_watermark

### Frontend Fixes
- [X] T012 [US1] Remove manual Content-Type header from Axios request in frontend/src/App.jsx::handleEmbed
- [X] T013 [P] [US1] Add client-side file type validation in frontend/src/App.jsx::handleEmbed
- [X] T014 [P] [US1] Add client-side file size validation (<10MB) in frontend/src/App.jsx::handleEmbed
- [X] T015 [P] [US1] Add client-side text validation (non-empty) in frontend/src/App.jsx::handleEmbed
- [X] T016 [P] [US1] Add client-side alpha validation (0.1-5.0) in frontend/src/App.jsx::handleEmbed
- [X] T017 [US1] Improve error message display (replace generic alert) in frontend/src/App.jsx::handleEmbed

## Phase 4: User Story 2 - Fix Extract Upload (Priority: P1)

**Goal**: Ensure Extract tab can upload two separate images independently

**Independent Test**: Switch to Extract tab, upload two different images → both show previews

**Story Tasks**:

### Frontend UI Enhancements
- [X] T018 [US2] Add file preview for extractOriginal in frontend/src/App.jsx (Extract tab rendering)
- [X] T019 [P] [US2] Add file preview for extractSuspect in frontend/src/App.jsx (Extract tab rendering)
- [X] T020 [P] [US2] Add filename display for uploaded files in frontend/src/App.jsx (Extract tab)
- [X] T021 [P] [US2] Add success checkmarks (✓) when files uploaded in frontend/src/App.jsx (Extract tab)
- [X] T022 [US2] Add helper text explaining Original vs Suspect in frontend/src/App.jsx (Extract tab)
- [X] T023 [US2] Disable Extract button when files missing, show validation message in frontend/src/App.jsx

### State Management Verification
- [X] T024 [P] [US2] Add console logging to verify state independence in frontend/src/App.jsx::handleExtractOriginalSelect
- [X] T025 [P] [US2] Add console logging to verify state independence in frontend/src/App.jsx::handleExtractSuspectSelect
- [X] T026 [US2] Verify state isolation when switching between tabs in frontend/src/App.jsx

## Phase 5: User Story 3 - Fix Verify Extraction (Priority: P1)

**Goal**: Enable blind verification to correctly extract watermark text

**Independent Test**: Embed "SecretMessage123" → download → verify → expect exact text match

**Story Tasks**:

### Algorithm Parameter Validation
- [X] T027 [US3] Create algorithm parameter constants in backend/src/core/embedding.py (WAVELET, LEVEL, DELTA)
- [X] T028 [P] [US3] Create matching algorithm parameter constants in backend/src/core/extraction.py
- [X] T029 [US3] Add parameter validation check on module import in backend/src/core/__init__.py
- [X] T030 [P] [US3] Add parameter logging in embed method in backend/src/core/embedding.py::embed_watermark_dwt_qim
- [X] T031 [P] [US3] Add parameter logging in extract method in backend/src/core/extraction.py::extract_watermark_dwt_qim

### Payload Parsing Fixes
- [X] T032 [US3] Enhance payload parsing with detailed error messages in backend/src/core/extraction.py::_parse_payload
- [X] T033 [US3] Add header validation with clear error for invalid header in backend/src/core/extraction.py::_parse_payload
- [X] T034 [US3] Add length validation (bounds checking) in backend/src/core/extraction.py::_parse_payload
- [X] T035 [US3] Add UTF-8 decoding error handling in backend/src/core/extraction.py::_parse_payload
- [X] T036 [P] [US3] Add payload parsing test with known good data in backend/tests/test_payload.py

### Blind Alignment Improvements
- [X] T037 [US3] Add error handling for sync template detection failure in backend/src/core/extraction.py::extract_with_blind_alignment
- [X] T038 [US3] Add fallback logic when alignment fails in backend/src/core/extraction.py::extract_with_blind_alignment
- [X] T039 [P] [US3] Add detailed logging for geometry detection in backend/src/core/extraction.py::extract_with_blind_alignment

### Reed-Solomon Decoding
- [X] T040 [US3] Add try-catch for ReedSolomonError in backend/src/core/extraction.py::_decode_rs_stream
- [X] T041 [US3] Return "No Watermark Detected" instead of crash on RS failure in backend/src/core/extraction.py::_decode_rs_stream

### API Error Handling
- [X] T042 [US3] Implement structured error responses in backend/src/api/routes.py::verify_watermark
- [X] T043 [P] [US3] Add validation for image file in backend/src/api/routes.py::verify_watermark

## Phase 6: Testing & Validation

**Goal**: Ensure all three issues are resolved with comprehensive tests

### Regression Tests
- [ ] T044 Create embed regression test in backend/tests/test_embed_fix.py
- [ ] T045 Create extract regression test in backend/tests/test_extract_fix.py
- [ ] T046 Create verify regression test in backend/tests/test_verify_fix.py

### Integration Tests
- [ ] T047 Test full cycle: embed → download → verify in backend/tests/test_full_cycle.py
- [ ] T048 [P] Test error cases for all three endpoints in backend/tests/test_error_cases.py

### Manual Testing
- [ ] T049 Execute quickstart.md test suite for Embed (Test Suite 1)
- [ ] T050 Execute quickstart.md test suite for Extract (Test Suite 2)
- [ ] T051 Execute quickstart.md test suite for Verify (Test Suite 3)
- [ ] T052 Verify all regression checklist items in quickstart.md

## Phase 7: Polish & Documentation

**Goal**: Improve user experience and finalize documentation

- [ ] T053 Add inline error messages (replace alerts) in frontend/src/App.jsx
- [ ] T054 [P] Add loading state indicators for all three functions in frontend/src/App.jsx
- [ ] T055 [P] Update API documentation with new error codes in backend/openapi.yaml
- [ ] T056 Update README.md with troubleshooting section

## Dependencies

### Critical Path
1. **Phase 1 & 2** (Setup) must complete before user story phases
2. **US1 (Embed)** is independent of US2 and US3
3. **US2 (Extract)** is independent of US1 and US3
4. **US3 (Verify)** depends on US1 (need working embed to test verify)
5. **Phase 6 (Testing)** requires all three user stories complete
6. **Phase 7 (Polish)** can run in parallel with testing

### User Story Dependencies
- **US1 (Embed)**: No dependencies, can start immediately after Phase 2
- **US2 (Extract)**: Independent, can run in parallel with US1
- **US3 (Verify)**: Soft dependency on US1 (need embedded images to test), but can implement fixes in parallel

### Task-Level Dependencies
- T027-T028 must complete before T029 (parameter validation check)
- T032-T035 must complete before T036 (payload parsing tests)
- T006-T011 (backend fixes) can run in parallel with T012-T017 (frontend fixes)
- T018-T023 (UI enhancements) are independent and parallelizable
- T027-T043 (Verify fixes) have internal dependencies but can run parallel to US1/US2

## Parallel Execution Examples

### Scenario 1: Two Developers (Backend + Frontend)
**Dev 1 (Backend)**:
- Phase 1: T001, T003 (schemas + logging)
- US1: T006-T011 (embed backend fixes)
- US3: T027-T043 (verify algorithm fixes)

**Dev 2 (Frontend)**:
- Phase 1: T002 (validation helpers)
- US1: T012-T017 (embed frontend fixes)
- US2: T018-T026 (extract UI enhancements)

### Scenario 2: Single Developer (Sequential by Story)
**Sprint 1 (US1 - Embed)**:
- Day 1: Phase 1 & 2 (T001-T005) + US1 Backend (T006-T011)
- Day 2: US1 Frontend (T012-T017) + Manual testing

**Sprint 2 (US2 - Extract)**:
- Day 3: US2 UI (T018-T023) + State verification (T024-T026)
- Day 4: Manual testing + fixes

**Sprint 3 (US3 - Verify)**:
- Day 5: Algorithm params (T027-T031) + Payload parsing (T032-T036)
- Day 6: Alignment + RS fixes (T037-T043) + API updates
- Day 7: Manual testing

**Sprint 4 (Polish)**:
- Day 8: Testing phase (T044-T052)
- Day 9: Polish phase (T053-T056)

### Scenario 3: Parallel Implementation (All Stories at Once)
**Week 1**:
- Mon: Phase 1 & 2 (T001-T005)
- Tue-Wed: US1, US2, US3 backend fixes in parallel (T006-T011, T027-T043)
- Thu-Fri: US1, US2 frontend fixes in parallel (T012-T023, T026)

**Week 2**:
- Mon-Tue: Testing phase (T044-T052)
- Wed-Thu: Polish phase (T053-T056)
- Fri: Full regression and sign-off

## Implementation Strategy

### MVP Approach
**Minimum Viable Product** = US1 (Embed) working
- Users can at least embed watermarks successfully
- Provides immediate value even if Extract/Verify still broken
- Tasks: T001-T017, T044, T049

**Increment 2** = US1 + US2 (Embed + Extract)
- Users can embed and extract with original image
- Covers most common workflow
- Tasks: Add T018-T026, T045, T050

**Full Feature** = US1 + US2 + US3 (All Fixed)
- All three functions working as specified
- Complete solution
- Tasks: Add T027-T056

### Incremental Delivery
Each user story can be:
- **Implemented independently**: US2 doesn't need US1 code
- **Tested independently**: quickstart.md has separate test suites
- **Deployed independently**: Can merge US1 fixes while US2/US3 in progress
- **Demonstrated independently**: Can show stakeholders working Embed even if Extract/Verify pending

### Quality Gates
- [ ] After US1: Run Test Suite 1 from quickstart.md → 100% pass
- [ ] After US2: Run Test Suite 2 from quickstart.md → 100% pass
- [ ] After US3: Run Test Suite 3 from quickstart.md → 100% pass
- [ ] Before merge: All regression tests pass (T044-T048)
- [ ] Before merge: Full quickstart.md checklist complete (T049-T052)

## Task Estimation

| Phase | Task Count | Estimated Time | Complexity |
|-------|-----------|----------------|------------|
| Phase 1: Setup | 3 tasks | 1-2 hours | Low |
| Phase 2: Foundational | 2 tasks | 30 min | Low |
| Phase 3: US1 (Embed) | 12 tasks | 4-6 hours | Medium |
| Phase 4: US2 (Extract) | 9 tasks | 3-4 hours | Low-Medium |
| Phase 5: US3 (Verify) | 17 tasks | 8-12 hours | High |
| Phase 6: Testing | 9 tasks | 6-8 hours | Medium |
| Phase 7: Polish | 4 tasks | 2-3 hours | Low |
| **Total** | **56 tasks** | **24-36 hours** | **Mixed** |

**Note**: Estimates are for a single developer working sequentially. Parallel execution can reduce wall-clock time significantly.

## Success Criteria Mapping

| Spec Success Criteria | Tasks | Validation |
|----------------------|-------|------------|
| **SC-001**: Embed success 100% | T006-T017 | T044, T049 |
| **SC-002**: Extract upload 100% | T018-T026 | T045, T050 |
| **SC-003**: Verify accuracy 85%+ | T027-T043 | T046, T051 |
| **SC-004**: Clear errors 100% | T001, T006-T011, T017, T042 | T048 |
| **SC-005**: All issues resolved | T001-T056 | T052 (full checklist) |

## Notes

- **Tests are included** because the spec mentions comprehensive testing requirements
- **All tasks follow strict checklist format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- **Tasks are organized by user story** for independent implementation
- **Parallel opportunities clearly marked** with [P] tag
- **Each user story is independently testable** per spec requirements
- **Critical fixes prioritized**: US1 and US3 are highest priority (P1), US2 is UX improvement

**Next Step**: Execute `/speckit.implement` to begin implementation with automated task tracking
