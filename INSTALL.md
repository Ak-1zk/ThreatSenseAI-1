# ThreatSense AI - Installation & Startup Guide

This document provides step-by-step instructions to install, configure, and run the **ThreatSense AI** application locally.

## Prerequisites

Ensure you have the following installed on your system:
-   **Node.js** (v18 or higher)
-   **Python** (3.9 or higher)
-   **Git**

## 1. Clone the Repository

```bash
git clone <repository-url>
cd ThreatSense-AI
```

## 2. Backend Setup (Python)

The backend handles AI processing using FastAPI and Google Gemini.

1.  **Navigate to the project root:**
    ```bash
    cd ThreatSense-AI
    ```

2.  **Install Python Dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Configure Environment Variables:**
    -   Create a file named `.env.local` in the root directory (`ThreatSense-AI/.env.local`).
    -   Add your Google Gemini API Key:
        ```ini
        GEMINI_API_KEY=your_actual_api_key_here
        ```

4.  **Start the Backend Server:**
    Run the following command to start the backend on port **8001**:
    ```bash
    python -m uvicorn backend.main:app --port 8001
    ```
    *You should see output indicating the server is running at `http://127.0.0.1:8001`.*

## 3. Frontend Setup (Next.js)

The frontend provides the user interface and communicates with the backend.

1.  **Open a new terminal window** (keep the backend running in the first one).

2.  **Navigate to the project root:**
    ```bash
    cd ThreatSense-AI
    ```

3.  **Install Node.js Dependencies:**
    ```bash
    npm install
    ```

4.  **Start the Frontend Development Server:**
    ```bash
    npm run dev
    ```
    *This will start the frontend on port **9002** (or 3000 if configured differently).*

## 4. Access the Application

Open your browser and navigate to:
**http://localhost:9002**

## Troubleshooting

-   **Backend Port Conflict**: If port 8001 is in use, you can change the port in the start command, but you must also update `src/lib/ai-manager.ts` in the frontend code to match.
-   **Gemini Quota Exceeded**: If you see a 500 error or "Resource Exhausted", the application will automatically fallback to **Puter.js** (client-side AI) to ensure continued functionality.
-   **Ghost Processes**: If you cannot start the backend, check for old processes running on port 8001 or 8000 and terminate them using Task Manager or `taskkill`.
