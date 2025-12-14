# Research & Technical Decisions

## Technology Stack Selection

### Backend: Python + FastAPI
- **Decision**: Use Python 3.11+ with FastAPI.
- **Rationale**: Python is the standard for Computer Vision (OpenCV, NumPy, SciPy). FastAPI provides high-performance async support for I/O bound operations and automatic OpenAPI documentation.
- **Alternatives Considered**: 
    - Flask/Django: Less performant for async, heavier (Django).
    - Node.js/Go: Lack of mature CV/Scientific libraries compared to Python ecosystem.

### Frontend: React + Vite
- **Decision**: React 18 with Vite build tool.
- **Rationale**: Rich ecosystem for interactive UI. Vite offers fast dev server.
- **Key Libraries**: 
    - Tailwind CSS for rapid styling.
    - HTML5 Canvas for client-side pixel manipulation (Diff Map, Attack Simulator).

### Core Algorithms
- **Watermarking**: DCT (Discrete Cosine Transform) with HVS (Human Visual System) masking.
    - **Rationale**: DCT is robust against compression. HVS masking (Laplacian) ensures invisibility in smooth areas and robustness in textured areas.
- **Geometric Correction**: ORB + RANSAC + Homography.
    - **Rationale**: "God of War" requirement. ORB is fast and patent-free. RANSAC handles outliers effectively. Homography corrects perspective distortion from screen capture.

## Unknowns & Risks Resolution

### Moiré Patterns
- **Risk**: Screen capture introduces Moiré patterns that affect frequency coefficients.
- **Mitigation**: 
    - Avoid high-frequency bands in DCT.
    - Use mid-frequency bands (e.g., ZigZag 10-20).
    - Implement redundant coding (Repetition Code).

### Performance
- **Risk**: CV operations (ORB, Warp) are CPU intensive.
- **Mitigation**: 
    - Use `opencv-python-headless` for smaller footprint.
    - Resize images before feature extraction to speed up ORB.
    - Use FastAPI `BackgroundTasks` if processing takes too long (though for this MVP, synchronous response is preferred for UX).

### Security
- **Risk**: Malicious file uploads.
- **Mitigation**: 
    - Validate MIME types (magic numbers).
    - Limit file size.
    - Process images in memory or temp storage with auto-cleanup.
