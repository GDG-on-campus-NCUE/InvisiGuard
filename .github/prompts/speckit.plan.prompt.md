---
agent: speckit.plan
---

# /speckit.plan Prompt (InvisiGuard)

## Objective
制定 InvisiGuard 核心浮水印與幾何校正系統的技術實作計畫。此計畫需將 `/speckit.specify` 定義的功能需求轉化為具體的架構決策、API 介面定義與資料流設計，並確保符合 `.specify/memory/constitution.md` 中的架構原則。

## Technical Context
- **Frontend**: React 18 (Vite), Tailwind CSS, Axios, HTML5 Canvas (for pixel manipulation).
- **Backend**: Python 3.11+, FastAPI (Async), Uvicorn.
- **Core Libraries**: 
    - `opencv-python-headless` (幾何變換、ORB 特徵)
    - `numpy`, `scipy` (矩陣運算、DCT)
    - `invisible-watermark` (作為參考或基底，需封裝)
- **Infrastructure**: Docker (optional for deployment), Local filesystem for temp storage.

## Architecture Overview
採用前後端分離架構，透過 RESTful API 溝通。後端採用模組化設計，將視覺處理邏輯與 API 層解耦。

### 1. Backend Architecture (Python/FastAPI)
- **API Layer (`/api`)**: 處理 HTTP 請求、驗證參數、錯誤處理。
- **Service Layer (`/services`)**: 
    - `WatermarkService`: 協調嵌入與提取流程。
    - `AlignmentService`: 處理幾何校正邏輯。
- **Core Layer (`/core`)**:
    - `processor.py`: 圖像預處理（Resize, Grayscale）。
    - `embedding.py`: LoG Mask 生成、DCT 變換、位元嵌入。
    - `extraction.py`: DCT 提取、NCC 計算。
    - `geometry.py`: ORB 特徵提取、RANSAC Homography 計算、Warp Perspective。
- **Utils**: 圖像 I/O、格式轉換。

### 2. Frontend Architecture (React)
- **Components**:
    - `Dropzone`: 處理檔案上傳。
    - `ConfigPanel`: 調整 Alpha 強度、輸入文字。
    - `ComparisonView`: 實作 Side-by-Side 與 Diff Map (Canvas)。
    - `AttackSimulator`: 使用 CSS `transform` 模擬攻擊，並將 Canvas 匯出為圖片。
- **State Management**: React Context 或 Zustand (管理上傳狀態與結果)。
- **API Client**: 封裝 Axios 請求，處理 Multipart 上傳。

## Data Models & API Contracts

### API 1: Embed Watermark
- **Endpoint**: `POST /api/v1/embed`
- **Request (Multipart)**:
    - `file`: binary (image/jpeg, image/png)
    - `text`: string (max 32 chars)
    - `alpha`: float (0.1 - 5.0, default 1.0)
- **Response (JSON)**:
    ```json
    {
        "status": "success",
        "data": {
            "image_url": "/static/processed/...",
            "psnr": 42.5,
            "ssim": 0.98
        }
    }
    ```

### API 2: Extract Watermark
- **Endpoint**: `POST /api/v1/extract`
- **Request (Multipart)**:
    - `original_file`: binary (基準圖)
    - `suspect_file`: binary (待測截圖)
- **Response (JSON)**:
    ```json
    {
        "status": "success",
        "data": {
            "decoded_text": "Copyright 2025",
            "confidence": 0.95,
            "is_match": true,
            "debug_info": {
                "aligned_image_url": "/static/debug/...",
                "matches_found": 150
            }
        }
    }
    ```

## Implementation Phases

### Phase 1: Foundation & API Skeleton
1.  初始化 FastAPI 專案結構與 React Vite 專案。
2.  定義 API 路由與 Pydantic 模型。
3.  實作 `ImageProcessor` 進行基本的讀取與縮放。
4.  建立前後端連通測試 (Ping/Pong)。

### Phase 2: Core Watermarking (Embedding)
1.  實作 `LoG Mask` 生成演算法。
2.  實作 `DCT` 分塊與嵌入邏輯 (參考 `invisible-watermark`)。
3.  完成 `/embed` API 與前端上傳/預覽介面。
4.  前端實作 `Diff View` (Canvas pixel manipulation)。

### Phase 3: Geometric Correction (The "God of War" Module)
1.  實作 `ORB` 特徵提取與 `BFMatcher`。
2.  實作 `RANSAC` Homography 計算與 `warpPerspective`。
3.  整合校正邏輯至 `/extract` API。
4.  前端實作 `Attack Simulator` 與提取測試介面。

### Phase 4: Optimization & Polish
1.  優化 ORB 參數 (`nfeatures`, `scaleFactor`) 以提升匹配率。
2.  調整嵌入強度 $\alpha$ 與頻段選擇以平衡畫質與魯棒性。
3.  增加錯誤處理 (如：特徵點不足、檔案格式錯誤)。
4.  撰寫 API 文件 (Swagger/OpenAPI) 與使用說明。

## Constitution Check
- **Architecture**: 模組化設計 (Core vs Service vs API)，符合單一職責原則。
- **Readability**: Python 程式碼需遵循 PEP8，React 組件需功能單一。
- **Security**: 驗證上傳檔案類型與大小；不儲存原始圖片超過必要時間。
- **Testing**: 針對 Core 演算法 (DCT, Homography) 撰寫單元測試。

## Unknowns & Risks
- **Moiré Patterns**: 翻拍螢幕的波紋可能干擾 DCT 係數 -> 需保留調整頻段的彈性。
- **Performance**: Python 的圖像處理可能較慢 -> 需監控 API 響應時間，必要時使用 `concurrent.futures` 或 Celery。
