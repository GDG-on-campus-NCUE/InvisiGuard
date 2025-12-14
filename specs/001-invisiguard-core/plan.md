# Implementation Plan: InvisiGuard Core

**Branch**: `001-invisiguard-core` | **Date**: 2025-12-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Develop a robust invisible watermarking system ("InvisiGuard") that integrates HVS masking, DCT embedding, and geometric correction (ORB+RANSAC) to survive screen capture attacks. The system will consist of a Python FastAPI backend for core processing and a React frontend for user interaction and attack simulation.

## Technical Context

**Language/Version**: Python 3.11+, Node.js 18+
**Primary Dependencies**: FastAPI, OpenCV (headless), NumPy, SciPy, React, Vite, Tailwind CSS
**Storage**: Local filesystem (temp storage for processing)
**Testing**: pytest (Backend), Vitest (Frontend)
**Target Platform**: Web (Dockerized deployment optional)
**Project Type**: web
**Performance Goals**: Embedding < 1s, Extraction < 2s (including geometric correction)
**Constraints**: Must handle 1080p+ images, robust against 45-degree rotation and perspective distortion.
**Scale/Scope**: MVP with core functionality.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Architecture**: Modular design (Core/Service/API) aligns with Principle I.
- **Readability**: Python PEP8 and React functional components align with Principle IV.
- **Security**: Input validation (MIME type, size) aligns with Principle IX.
- **Testing**: Unit tests for algorithms align with Principle VII.

## Project Structure

### Documentation (this feature)

```text
specs/001-invisiguard-core/
├── plan.md              # This file
├── research.md          # Technical decisions
├── data-model.md        # Entities and validation
├── quickstart.md        # Setup guide
├── contracts/           # OpenAPI specs
│   └── openapi.yaml
└── tasks.md             # To be generated
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/             # FastAPI routers
│   ├── core/            # Core algorithms (DCT, ORB, HVS)
│   ├── services/        # Business logic
│   └── utils/           # Helpers
├── tests/
│   ├── unit/
│   └── integration/
├── main.py              # App entry point
└── requirements.txt

frontend/
├── src/
│   ├── components/      # React components
│   ├── hooks/           # Custom hooks
│   ├── services/        # API client
│   └── App.jsx
├── public/
└── vite.config.js
```

**Structure Decision**: Option 2 (Web application) selected due to clear separation of concerns between heavy computational backend and interactive frontend.

## Complexity Tracking

N/A - No unjustified complexity.
