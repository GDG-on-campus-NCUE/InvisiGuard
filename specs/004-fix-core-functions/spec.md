# Feature Specification: Fix Core Functions (Embed, Extract, Verify)

**Feature Branch**: `004-fix-core-functions`  
**Created**: 2025年12月16日  
**Status**: Draft  
**Input**: User description: "發現問題：1. 我發現我在使用嵌入浮水印的功能的時候會有 Status 400 的問題，需要確認專案現在存在的問題。2. 我發現我無法在提取功能中上傳圖片。3. 我無法在盲測功能中將圖片中的訊息提取出來。期望行為：能夠正常的使用三個主要的功能。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fix Embed Function (Priority: P1)

當用戶嘗試嵌入浮水印時，系統會返回 Status 400 錯誤，導致無法完成浮水印嵌入流程。用戶需要能夠正常上傳圖片、輸入文字、調整強度參數，並成功獲得嵌入浮水印的圖片。

**Why this priority**: 嵌入功能是整個系統的核心入口，如果無法嵌入浮水印，後續的提取和驗證功能都無法測試。這是最高優先級的問題。

**Independent Test**: 可以通過上傳一張測試圖片（例如 1080p PNG/JPG）、輸入測試文字（例如 "TEST123"）、設定 alpha 值為 1.0，點擊嵌入按鈕，系統應返回嵌入後的圖片而非 400 錯誤。

**Acceptance Scenarios**:

1. **Given** 用戶在 Embed 標籤頁，**When** 拖放一張 PNG 圖片、輸入文字 "Hello World"、alpha 設為 1.0，並點擊 Embed 按鈕，**Then** 系統在 3 秒內返回成功訊息，顯示嵌入後的圖片與原圖對比視圖。
2. **Given** 用戶使用 JPG 格式圖片（品質 90），**When** 執行嵌入操作，**Then** 系統正確處理並返回嵌入結果，不會因格式問題返回 400 錯誤。
3. **Given** 後端 API `/v1/embed` 接收到有效的 multipart/form-data 請求，**When** 處理過程中發生錯誤（例如圖片損壞），**Then** 返回清楚的錯誤訊息（例如 "Invalid image format"）而非通用 500 錯誤。
4. **Given** 前端發送嵌入請求，**When** alpha 值超出合理範圍（例如 -1 或 100），**Then** 系統返回驗證錯誤並提示有效範圍（0.1 - 5.0）。

---

### User Story 2 - Fix Extract Function File Upload (Priority: P1)

用戶無法在提取功能（Extract Tab）中上傳圖片，可能是由於檔案狀態管理衝突或上傳元件錯誤。用戶需要能夠分別上傳原始圖片和可疑圖片，並正常執行提取流程。

**Why this priority**: 提取功能是核心功能之一，如果無法上傳檔案，則整個提取流程無法使用。與嵌入功能同等重要。

**Independent Test**: 可以在 Extract 標籤頁中分別上傳兩張圖片（原始圖與經過攻擊的圖片），觀察是否正常顯示預覽並能點擊 Extract 按鈕。

**Acceptance Scenarios**:

1. **Given** 用戶切換到 Extract 標籤頁，**When** 在 "Original Image" 區域拖放圖片 A，在 "Suspect Image" 區域拖放圖片 B，**Then** 兩個上傳區域分別顯示正確的預覽圖，且不會互相覆蓋。
2. **Given** 用戶在 Embed 標籤頁上傳了圖片，**When** 切換到 Extract 標籤頁，**Then** Extract 標籤頁的上傳區域是空白的，不會自動帶入 Embed 的圖片（避免狀態污染）。
3. **Given** 用戶在 Extract 標籤頁上傳了兩張圖片，**When** 點擊 Extract 按鈕，**Then** 系統正確發送請求到 `/v1/extract`，並顯示提取結果。
4. **Given** 用戶嘗試只上傳一張圖片（缺少另一張），**When** 點擊 Extract 按鈕，**Then** 系統顯示提示訊息 "Please upload both original and suspect images"。

---

### User Story 3 - Fix Blind Verification (Priority: P1)

用戶無法在盲測功能（Verify Tab）中成功提取圖片中的浮水印訊息，系統可能返回空值或錯誤。用戶需要能夠上傳一張含有浮水印的圖片（無需原圖），並正確提取出嵌入的文字。

**Why this priority**: 盲驗證是此專案的核心創新功能，如果無法正常工作，則失去了相較於傳統方法的優勢。

**Independent Test**: 可以使用 Embed 功能嵌入一張浮水印圖片後，直接在 Verify 標籤頁上傳該圖片（不提供原圖），系統應能提取出嵌入的文字。

**Acceptance Scenarios**:

1. **Given** 用戶已在 Embed 標籤頁嵌入文字 "SecretMessage123" 到圖片並下載，**When** 在 Verify 標籤頁上傳該圖片，**Then** 系統在 5 秒內返回 "SecretMessage123" 且 verified 狀態為 true。
2. **Given** 用戶上傳一張未包含浮水印的普通圖片，**When** 執行盲驗證，**Then** 系統返回 "No Watermark Detected" 且 verified 狀態為 false，不會返回亂碼或崩潰。
3. **Given** 用戶上傳一張經過旋轉 15 度的浮水印圖片，**When** 執行盲驗證，**Then** 系統利用同步模板自動校正幾何變形，並成功提取浮水印。
4. **Given** 後端 `/v1/verify` 端點接收到圖片，**When** 同步模板檢測失敗（例如圖片被嚴重裁剪），**Then** 返回清楚的錯誤訊息 "Synchronization template not detected"。

---

### Edge Cases

- **格式支援**: 系統應明確支援 PNG、JPG、JPEG 格式，對於 WebP、TIFF 等格式應返回友善的不支援訊息，而非 400 錯誤。
- **檔案大小**: 當用戶上傳超大圖片（例如 8K 解析度）時，系統應提示 "Image too large, please use images under 4K resolution"。
- **空白輸入**: 當用戶在 Embed 時輸入空白文字或僅空格時，系統應返回驗證錯誤 "Watermark text cannot be empty"。
- **特殊字元**: 當嵌入文字包含 emoji 或 Unicode 字元時，系統應能正確編碼與解碼，或明確說明僅支援 ASCII。
- **並發請求**: 當用戶快速連續點擊 Embed 按鈕時，系統應防止重複請求（disable 按鈕或顯示 loading 狀態）。
- **網路中斷**: 當 API 請求失敗時（例如後端未啟動），前端應顯示友善的錯誤訊息 "Cannot connect to server. Please check if backend is running."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統 MUST 正確處理來自前端的 multipart/form-data 請求，包含 file、text、alpha 三個欄位。
- **FR-002**: 系統 MUST 在 `/v1/embed` 端點驗證輸入參數（text 非空、alpha 在 0.1-5.0 範圍內、檔案格式為 PNG/JPG）。
- **FR-003**: 前端 Extract 標籤頁 MUST 使用獨立的狀態變數管理 `extractOriginal` 和 `extractSuspect`，不與 Embed 標籤頁的 `file` 變數衝突。
- **FR-004**: 系統 MUST 在 `/v1/verify` 端點實現盲驗證邏輯，無需接收原始圖片參數。
- **FR-005**: 後端 MUST 返回清楚的錯誤訊息，包含錯誤類型與建議操作（例如 `{"status": "error", "detail": "Invalid image format. Supported: PNG, JPG"}`）。
- **FR-006**: 前端 MUST 在檔案上傳時進行本地驗證（檔案類型、大小），在發送請求前提示用戶錯誤。
- **FR-007**: 系統 MUST 在 Embed 完成後提供下載按鈕，點擊時直接下載圖片（使用 blob URL），不開啟新分頁。
- **FR-008**: 系統 MUST 在所有三個功能中顯示 loading 狀態（spinner 或進度條），並在請求期間 disable 操作按鈕。
- **FR-009**: 系統 MUST 確保 DWT/QIM 嵌入與提取參數一致（例如 delta 值、wavelet 類型、分解層級）。
- **FR-010**: 系統 MUST 在盲驗證失敗時返回 `"No Watermark Detected"` 而非崩潰或返回亂碼。

### Key Entities *(include if feature involves data)*

- **EmbedRequest**: 包含 `file` (圖片檔案)、`text` (浮水印文字)、`alpha` (嵌入強度) 三個欄位
- **ExtractRequest**: 包含 `original_file` (原始圖片) 和 `suspect_file` (可疑圖片) 兩個欄位
- **VerifyRequest**: 包含 `image` (待驗證圖片) 一個欄位
- **ErrorResponse**: 包含 `status` ("error")、`detail` (錯誤描述)、`suggestion` (建議操作，可選) 欄位

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 使用者能在 10 秒內完成嵌入流程（上傳圖片 → 輸入文字 → 點擊 Embed → 獲得結果），成功率達 100%（無 400 錯誤）。
- **SC-002**: 使用者能正確上傳兩張圖片到 Extract 標籤頁，且不受 Embed 標籤頁狀態影響，上傳成功率達 100%。
- **SC-003**: 使用者能在 Verify 標籤頁正確提取浮水印文字，對於未經幾何變形的圖片，提取準確率達 100%；對於旋轉 ±30 度或縮放 70%-130% 的圖片，提取準確率達 85% 以上。
- **SC-004**: 系統在遇到錯誤時（格式不支援、參數無效、圖片損壞），100% 的情況下返回清楚的錯誤訊息，而非通用的 400/500 錯誤碼。
- **SC-005**: 使用者報告的三個核心問題（Embed 400 錯誤、Extract 無法上傳、Verify 無法提取）全部解決，回歸測試通過率達 100%。

## Assumptions

- 後端 FastAPI 伺服器運行在 `http://localhost:8000`，前端 Vite 開發伺服器運行在 `http://localhost:5173`，proxy 配置正確。
- 使用者已安裝所有必要的 Python 依賴（OpenCV, NumPy, SciPy, PyWavelets, reedsolo 等）。
- 使用者的瀏覽器支援現代 JavaScript 功能（async/await、FormData、Blob）。
- 嵌入與提取使用相同的演算法配置（DWT 層級、QIM delta、Reed-Solomon 糾錯參數）。

## Dependencies & Constraints

- **前端**: React 18, Vite 5, Axios
- **後端**: FastAPI, OpenCV (cv2), NumPy, SciPy, PyWavelets, reedsolo
- **網路**: 需要前後端同時運行，且 Vite proxy 正確轉發 `/api` 請求到後端
- **效能**: 嵌入與提取操作應在合理時間內完成（嵌入 < 5 秒，提取 < 10 秒，驗證 < 10 秒，針對 1080p 圖片）
- **相容性**: 支援 Chrome, Firefox, Safari 最新版本

## Notes

- 此次修復聚焦於讓三個核心功能恢復正常運作，不涉及新功能開發。
- 需要特別注意 React 狀態管理，避免不同標籤頁之間的狀態污染。
- 後端錯誤處理應遵循 REST API 最佳實踐，返回標準的 HTTP 狀態碼與 JSON 錯誤訊息。
- 建議在修復過程中添加更多的日誌輸出（前端 console.log、後端 logging），方便未來除錯。
- 如果發現演算法層級的 bug（例如 DWT/QIM 實現錯誤），可能需要參考原始論文或開源實現進行修正。
