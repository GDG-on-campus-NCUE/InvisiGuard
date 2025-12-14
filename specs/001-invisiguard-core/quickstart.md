# Quickstart Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- Git

## Backend Setup (FastAPI)

1.  **Navigate to backend directory**:
    ```bash
    cd backend
    ```

2.  **Create virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run server**:
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    API docs available at `http://localhost:8000/docs`.

## Frontend Setup (React)

1.  **Navigate to frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Run development server**:
    ```bash
    npm run dev
    ```
    App available at `http://localhost:5173`.

## Usage

1.  Open the frontend app.
2.  Go to "Embed" tab. Upload an image and enter text. Click "Embed".
3.  Download the watermarked image.
4.  Take a screenshot or use "Attack Simulator" to distort the image.
5.  Go to "Extract" tab. Upload the original image and the distorted image.
6.  Click "Extract" to see the recovered text and alignment visualization.
