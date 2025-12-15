# InvisiGuard

**InvisiGuard** is a robust invisible watermarking system designed to protect digital images against screen capture ("analog hole"), rotation, scaling, and cropping attacks. It combines **Frequency Domain (DCT)** embedding with **Human Visual System (HVS)** masking and **Geometric Correction (ORB+RANSAC)** to ensure watermark survivability and invisibility.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)

## 🌟 Key Features

- **Invisible Embedding**: Uses Discrete Cosine Transform (DCT) and Laplacian-based HVS masking to hide text in image textures, minimizing visual distortion.
- **Robust Extraction (With Original)**: Recovers watermarks from distorted images (screenshots, photos of screens) by aligning them with the original image using ORB feature matching and RANSAC homography.
- **Blind Verification**: Detects and reads watermarks without the original image (using a structured payload with `[INV]` header), supporting basic rotation/scaling correction.
- **Attack Simulation**: Built-in frontend tools to simulate attacks (Rotation, Scaling, Perspective Warp) and verify robustness instantly.
- **Interactive UI**: React-based dashboard with real-time difference maps, side-by-side comparison, and detailed signal analysis (PSNR, SSIM).

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, OpenCV, NumPy, SciPy.
- **Frontend**: React 18 (Vite), Tailwind CSS, Axios.
- **Algorithms**: DCT (Discrete Cosine Transform), ORB (Oriented FAST and Rotated BRIEF), RANSAC, Laplacian of Gaussian (LoG).

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher

### 1. Backend Setup

```bash
cd backend
# Create virtual environment (optional but recommended)
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
# Server will start at http://localhost:8000
```

### 2. Frontend Setup

```bash
cd frontend
# Install dependencies
npm install

# Start development server
npm run dev
# App will open at http://localhost:5173
```

## 📖 Usage Guide

### 1. Embed Watermark
1.  Navigate to the **Embed Watermark** tab.
2.  Upload an image (JPEG/PNG).
3.  Enter the text to embed (e.g., "Copyright 2025").
4.  Adjust **Strength (Alpha)** if needed (Higher = more robust but more visible).
5.  Click **Embed** and wait for processing.
6.  Click "Download" to directly download the watermarked image (no new tab).

### 2. Extract (With Original)
*Use this mode for maximum robustness against severe geometric distortion (e.g., angled photos).*
1.  Navigate to the **Extract (With Original)** tab.
2.  Upload the **Original Image** (Reference).
3.  Upload the **Suspect Image** (Screenshot or distorted version).
4.  Click **Extract Watermark**.
5.  The system will align the images and decode the text.

### 3. Verify (Blind)
*Use this mode for quick checks when the original image is not available.*
1.  Navigate to the **Verify (Blind)** tab.
2.  Upload the **Suspect Image**.
3.  Click **Verify**.
4.  The system attempts to detect the `[INV]` header and decode the payload.

## 📚 API Documentation

Once the backend is running, interactive documentation is available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core Endpoints
- `POST /api/v1/embed`: Embed text into an image.
- `POST /api/v1/extract`: Extract watermark using an original reference image (Alignment enabled).
- `POST /api/v1/verify`: Blind extraction without reference image.

## 🤖 Spec Kit Integration

This project uses **Spec Kit** for AI-driven development.

- **`/speckit.specify`**: Define new requirements.
- **`/speckit.plan`**: Generate technical plans.
- **`/speckit.tasks`**: Create implementation checklists.
- **`/speckit.implement`**: Execute code changes.

---

## 🇹🇼 專案架構與設計 (Project Architecture)

### 核心流程 (Pipeline)

1.  **感知層 (Perceptual Layer)**:
    -   利用 **Laplacian Filter** 計算圖像的紋理複雜度。
    -   生成 **HVS Mask**，在紋理複雜區域增強嵌入強度，平滑區域減弱強度，平衡隱蔽性與魯棒性。

2.  **嵌入層 (Embedding Layer)**:
    -   將圖像轉換為 YUV 色彩空間（僅處理 Y 通道）。
    -   進行 $8 \times 8$ 分塊 **DCT 變換**。
    -   將浮水印資訊（含 `[INV]` 標頭與長度位元）調變至中頻係數。

3.  **防禦層 (Defense Layer)**:
    -   **幾何校正 (Alignment)**: 使用 **ORB** 特徵點匹配與 **RANSAC** 算法計算單應性矩陣 (Homography)。
    -   **逆透視變換 (Un-warping)**: 將變形的截圖還原為正視圖，確保 DCT 網格對齊。

### 專案結構

```text
InvisiGuard/
├── backend/
│   ├── src/
│   │   ├── api/            # FastAPI Routes
│   │   ├── core/           # Core Algorithms
│   │   │   ├── embedding.py    # DCT & HVS Logic
│   │   │   ├── extraction.py   # Decoding Logic
│   │   │   └── geometry.py     # ORB & RANSAC Alignment
│   │   └── main.py         # App Entry Point
│   └── tests/              # Pytest Suites
├── frontend/
│   ├── src/
│   │   ├── components/     # React Components (Dropzone, ComparisonView)
│   │   ├── services/       # API Client
│   │   └── App.jsx         # Main UI Logic
│   └── index.html
└── specs/                  # Spec Kit Documentation
```

