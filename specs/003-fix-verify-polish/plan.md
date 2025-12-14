# Implementation Plan: Fixes & Polish (Verify, Extract, Embed)

**Branch**: `003-fix-verify-polish` | **Date**: 2025-12-15 | **Spec**: [specs/003-fix-verify-polish/spec.md](spec.md)
**Input**: Feature specification from `/specs/003-fix-verify-polish/spec.md`

## Summary

This feature addresses critical usability and reliability issues identified after the v002 release. The primary technical change is the introduction of a structured payload (Header + Length + Data) for the blind verification process to eliminate "garbage" output. Additionally, it fixes state management bugs in the React frontend (Extract tab uploads) and improves the Embed tab UX by adding a download button and removing the misplaced Attack Simulator.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), Node.js/React 18 (Frontend)
**Primary Dependencies**: FastAPI, OpenCV, NumPy, SciPy (Backend); Vite, Tailwind (Frontend)
**Storage**: Local filesystem (temp storage)
**Testing**: pytest (Backend), Manual UI testing (Frontend)
**Target Platform**: Web Browser (Localhost)
**Project Type**: Web Application (FastAPI + React)
**Performance Goals**: Verification < 2s
**Constraints**: Must not break existing functionality.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Architecture**: Adheres to modular design. Payload logic confined to `core/embedding.py` and `core/extraction.py`. Frontend state fixes confined to `App.jsx`.
- **Readability**: Code will be PEP8 compliant.
- **Security**: Input validation remains in place.
- **Testing**: New unit tests for payload encoding/decoding.

## Project Structure

### Documentation (this feature)

```text
specs/003-fix-verify-polish/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── core/
│   │   ├── embedding.py  # Update: Add header/length logic
│   │   └── extraction.py # Update: Add header detection logic
│   └── api/              # No changes expected
└── tests/
    └── test_payload.py   # New: Test payload structure

frontend/
├── src/
│   ├── App.jsx           # Update: Fix state, remove AttackSim, add Download
│   └── components/       # No changes expected
```

**Structure Decision**: Modifying existing files in `backend/src/core` and `frontend/src`. Adding one new test file.

## Complexity Tracking

N/A - Changes are low complexity and localized.
