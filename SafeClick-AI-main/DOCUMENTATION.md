# ThreatSense AI — Complete Project Documentation

> **For Students**: This document explains every file in the project, what it does, and how the pieces fit together. Read this before diving into the code!

---

## 📂 Project Structure Overview

```
ThreatSense-AI/
│
├── .env.local                ← Secret API keys (never commit this!)
├── .gitignore                ← Tells Git which files to ignore
├── README.md                 ← Project introduction
├── INSTALL.md                ← Setup & installation guide
├── DOCUMENTATION.md          ← This file — you are here!
├── firestore.rules           ← Firebase security rules
│
├── backend/                  ← 🐍 Python FastAPI server (Gemini AI)
│   ├── __init__.py
│   ├── main.py               ← App entry point
│   ├── config.py              ← Environment variable loader
│   ├── requirements.txt       ← Python dependencies
│   ├── models/                ← Data shapes (Pydantic)
│   │   ├── __init__.py
│   │   ├── analysis.py        ← Analysis request/response models
│   │   └── chat.py            ← Chat request/response models
│   ├── routers/               ← API endpoint definitions
│   │   ├── __init__.py
│   │   ├── analyze.py         ← POST /api/analyze
│   │   ├── chat.py            ← POST /api/chat
│   │   └── daily_briefing.py  ← GET  /api/daily-briefing
│   └── services/              ← Business logic layer
│       ├── __init__.py
│       ├── gemini_service.py  ← Shared Gemini AI client
│       ├── threat_detector.py ← URL/email/message risk analysis
│       ├── chatbot_service.py ← Conversational AI logic
│       ├── briefing_service.py← Daily cybersecurity briefing
│       └── url_analyzer.py    ← URL-specific risk checks
│
├── frontend/                 ← 🌐 Pure HTML/CSS/JS (no frameworks!)
│   ├── index.html             ← Login page
│   ├── dashboard.html         ← Main app dashboard
│   ├── css/
│   │   └── styles.css         ← Complete design system
│   ├── js/
│   │   ├── firebase-config.js ← Firebase initialization
│   │   ├── auth.js            ← Authentication logic
│   │   ├── ai-manager.js      ← Backend API + fallback manager
│   │   ├── puter-ai.js        ← Puter.js AI wrapper (fallback)
│   │   └── app.js             ← Dashboard orchestrator
│   └── assets/
│       ├── bg.png             ← Background image
│       └── icon.png           ← App icon/logo
│
└── docs/                     ← 📖 Additional documentation
    ├── blueprint.md           ← Architecture blueprint
    └── backend.json           ← API endpoint reference
```

---

## 🏗️ Architecture — How It All Works

```
┌─────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                       │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │ Login    │───▶│  Dashboard   │───▶│ AI Operations:    │  │
│  │ Page     │    │  (main app)  │    │ • Analyze URL     │  │
│  │          │    │              │    │ • Analyze Email   │  │
│  │ Firebase │    │ app.js wires │    │ • Analyze Message │  │
│  │ Auth     │    │ everything   │    │ • Chat with AI    │  │
│  └──────────┘    └──────────────┘    │ • Daily Briefing  │  │
│                                      └────────┬──────────┘  │
└───────────────────────────────────────────────┼─────────────┘
                                                │
                        ai-manager.js routes all requests
                                                │
                    ┌───────────────────────────┼──────────┐
                    │        TRY BACKEND FIRST  ▼          │
                    │  ┌─────────────────────────────────┐ │
                    │  │   Python FastAPI (port 8001)    │ │
                    │  │   Uses Google Gemini AI API     │ │
                    │  └──────────────┬──────────────────┘ │
                    │                 │                     │
                    │    If fails (quota/error/offline)     │
                    │                 │                     │
                    │                 ▼                     │
                    │  ┌─────────────────────────────────┐ │
                    │  │   Puter.js (fallback)           │ │
                    │  │   Free cloud AI — no API key!   │ │
                    │  └─────────────────────────────────┘ │
                    └──────────────────────────────────────┘
```

**Key Concept**: Every AI request goes to the **Python backend first** (which uses Google's Gemini AI). If that fails for any reason (API quota exhausted, server down, network error), it **automatically falls back** to Puter.js — a free cloud AI that works directly in the browser. The user never sees the difference.

---

## 📁 File-by-File Explanation

---

### Root Files

| File | What It Does |
|------|-------------|
| **`.env.local`** | Stores secret API keys (Gemini API key, Firebase config). **Never share or commit this file!** It's loaded by `backend/config.py` at startup. |
| **`.gitignore`** | Lists files Git should ignore (e.g., `__pycache__/`, `.env.local`, `node_modules/`). Prevents secrets and build artifacts from being committed. |
| **`README.md`** | The project's public-facing introduction. Shows up on GitHub as the landing page. |
| **`INSTALL.md`** | Step-by-step setup instructions for new developers. |
| **`firestore.rules`** | Firebase Firestore security rules. Defines who can read/write data in the database. Written in Firebase's custom rules language. |

---

### Backend — `backend/`

The backend is built with **FastAPI** (a modern Python web framework) and uses **Google Gemini AI** for intelligent analysis.

---

#### `backend/main.py` — The Entry Point

```python
# This is where the server starts!
app = FastAPI(title="ThreatSense AI Backend")
```

**What it does:**
- Creates the FastAPI application
- Adds **CORS middleware** so the frontend (running on a different port) can call the API
- Registers 3 API route groups: `/api/analyze`, `/api/chat`, `/api/daily-briefing`
- Provides a health check at `GET /` → `{"status": "ok"}`

**How to run it:**
```bash
python -m uvicorn backend.main:app --port 8001
```

**Student Tip:** CORS (Cross-Origin Resource Sharing) is a browser security feature. Without it, `localhost:5500` (frontend) can't call `localhost:8001` (backend) because they're different "origins."

---

#### `backend/config.py` — Environment Configuration

```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash-lite-001"
```

**What it does:**
- Loads the `.env.local` file from the project root
- Exports `GEMINI_API_KEY` (your Google AI key) and `GEMINI_MODEL` (which Gemini model to use)

**Student Tip:** Never hardcode API keys in your code! Always use environment variables. The `python-dotenv` library reads `.env.local` files automatically.

---

#### `backend/requirements.txt` — Python Dependencies

Lists the Python packages needed:
- `fastapi` — The web framework
- `uvicorn` — ASGI server that runs FastAPI
- `google-genai` — Google's Gemini AI SDK
- `python-dotenv` — Loads `.env` files

**Install them with:** `pip install -r backend/requirements.txt`

---

#### `backend/models/` — Data Models (Pydantic)

These define the **shape of data** flowing through the API.

| File | Purpose |
|------|---------|
| **`analysis.py`** | Defines `AnalysisRequest` (what the frontend sends) and `AnalysisResponse` (what the backend returns: classification, risk_score, reasons, recommendation) |
| **`chat.py`** | Defines `ChatRequest` (message + conversation history) and `ChatResponse` (the AI's reply) |

**Student Tip:** Pydantic models give you **automatic validation**. If the frontend sends bad data (e.g., missing a required field), FastAPI returns a clear 422 error — you don't need to write validation code yourself!

---

#### `backend/routers/` — API Endpoints

These define the **URL paths** the frontend can call.

| File | Endpoint | Method | What Happens |
|------|----------|--------|-------------|
| **`analyze.py`** | `/api/analyze` | POST | Receives text → calls `threat_detector` service → returns risk analysis JSON |
| **`chat.py`** | `/api/chat` | POST | Receives message + history → calls `chatbot_service` → returns AI reply |
| **`daily_briefing.py`** | `/api/daily-briefing` | GET | No input needed → calls `briefing_service` → returns markdown briefing |

**Student Tip:** In FastAPI, **routers** are like mini-apps. Each file handles one area of functionality, keeping the code organized. They're registered in `main.py` with `app.include_router()`.

---

#### `backend/services/` — Business Logic

This is where the **real work** happens. Routers are thin — they just call services.

| File | What It Does |
|------|-------------|
| **`gemini_service.py`** | Creates a shared Gemini AI client. All other services import `get_gemini_client()` from here instead of creating their own — this follows the **Singleton pattern**. |
| **`threat_detector.py`** | The core analysis engine. Sends the user's URL/email/message to Gemini AI with a carefully crafted **system prompt** that makes the AI return structured JSON with `classification`, `risk_score`, `reasons`, and `recommendation`. |
| **`chatbot_service.py`** | Manages AI conversations. Sends the full message history to Gemini AI so it has context. Uses a **system prompt** that tells the AI to be a cybersecurity expert. |
| **`briefing_service.py`** | Generates a daily cybersecurity threat briefing. Asks Gemini AI to produce a markdown-formatted summary of current threats. |
| **`url_analyzer.py`** | Performs additional URL-specific checks (domain reputation, suspicious patterns) before sending to the AI. |

**Student Tip:** The **Services pattern** separates "what endpoint to call" (routers) from "how to do the work" (services). This means you can change the AI provider (e.g., switch from Gemini to GPT-4) by editing only the services — the routers stay the same!

---

### Frontend — `frontend/`

The frontend is built with **pure HTML, CSS, and vanilla JavaScript** — no React, no npm, no build step. Just open the files in a browser!

---

#### `frontend/index.html` — Login Page

**What it does:**
- Glassmorphism-styled login card
- Email + password sign-in form
- Sign-up option for new users
- "Continue as Guest" anonymous login
- Uses Firebase Authentication

**Student Tip:** Firebase Auth handles all the security (password hashing, session tokens, etc.) for you. You just call `signInWithEmailAndPassword()` and Firebase does the rest!

---

#### `frontend/dashboard.html` — Main Application

**What it does (700+ lines):**
- **Header** — Logo, user info (avatar + email), sign-out button
- **Daily Briefing** — Accordion panel that lazy-loads cybersecurity intel
- **Analysis Panel** — 3-tab interface (URL / Email / Message) with input forms
- **Results Panel** — Shows classification badge, risk score bar, reasons list, recommendation
- **Chatbot** — Full chat interface with message history, image upload, speech-to-text
- **Footer** — Copyright info

The HTML loads all 5 JavaScript modules and includes every icon as **inline SVG** (no external icon library needed).

**Student Tip:** The page uses a **loading overlay** that hides the app until Firebase confirms the user is logged in. This prevents a flash of unauthenticated content.

---

#### `frontend/css/styles.css` — Design System

**What it does (~700 lines):**
- **CSS Custom Properties** (variables) for colors, spacing, border-radius — change one variable to restyle the entire app
- **Dark theme** using HSL color tokens
- **Glassmorphism** effects (frosted glass cards with `backdrop-filter: blur()`)
- **Component classes**: buttons, badges, inputs, cards, tabs, accordions, progress bars
- **Responsive grid** for the analysis panel (stacks on mobile, side-by-side on desktop)
- **Chat bubble** styles with avatar, user/assistant color coding
- **Award-winning markdown prose** — card-style list items, accented headings, glassmorphic code blocks
- **Animations** — shimmer loading skeletons, typing indicator dots, bubble entrance

**Student Tip:** The design system uses **HSL color format** (`hsl(217, 91%, 60%)`) because it's easier to create harmonious color palettes. You can generate lighter/darker shades by just changing the lightness value!

---

#### `frontend/js/firebase-config.js` — Firebase Setup

```javascript
const firebaseConfig = {
    apiKey: "...",
    authDomain: "...",
    projectId: "...",
    // ...
};
firebase.initializeApp(firebaseConfig);
```

**What it does:**
- Initializes Firebase with the project's config
- Creates the `auth` object used everywhere
- Firebase config values are **public by design** — security comes from Firestore rules, not from hiding these keys

---

#### `frontend/js/auth.js` — Authentication Module

**What it does:**
- **Sign In**: `signInWithEmailAndPassword(auth, email, password)`
- **Sign Up**: `createUserWithEmailAndPassword(auth, email, password)`
- **Anonymous Login**: `signInAnonymously(auth)`
- **Auth State Listener**: Redirects to `dashboard.html` if logged in, or to `index.html` if not
- **Form Validation**: Checks for valid email format, minimum password length, shows error messages
- **Loading States**: Disables buttons and shows spinners during authentication

**Student Tip:** The `onAuthStateChanged()` observer is the **single source of truth** for login status. It fires whenever the user logs in, logs out, or when the page loads. All routing decisions go through this one function!

---

#### `frontend/js/ai-manager.js` — The Traffic Controller ⭐

This is the **most important file** for understanding the architecture.

```javascript
const aiManager = {
    async chat(messages) {
        try {
            // 1. Try the Python backend first
            const res = await fetch(`${BACKEND_URL}/chat`, { ... });
            return { text: data.reply };
        } catch (err) {
            // 2. If backend fails, use Puter.js
            return this._fallbackChat(messages);
        }
    }
}
```

**What it does:**
- Provides 3 methods: `chat()`, `analyze()`, `getBriefing()`
- Each method follows the **same pattern**:
  1. Try the Python backend API (`localhost:8001`)
  2. If it fails for ANY reason → fall back to Puter.js
- Console logs show which path was taken (🔵 backend, ⚠️ fallback)

**Student Tip:** This is the **Facade pattern** — `app.js` calls `aiManager.chat()` without caring whether the response comes from Gemini or Puter.js. The complexity is hidden behind a simple interface!

---

#### `frontend/js/puter-ai.js` — Puter.js AI Wrapper

**What it does:**
- Wraps the Puter.js cloud AI library (loaded via CDN in the HTML)
- Provides `chatWithPuter(messages)` for conversational AI
- Provides `analyzeWithPuter(text)` for security analysis
- Uses `gpt-4o-mini` model through Puter's free AI service
- Parses the AI's JSON response for analysis results

**Student Tip:** Puter.js is a **free, no-API-key-needed** AI service that runs in the browser. It's perfect as a fallback because it requires zero configuration. The trade-off is that you have less control over the model.

---

#### `frontend/js/app.js` — Dashboard Orchestrator ⭐

**What it does (~540 lines):**
This is the **brain of the frontend** — it wires up every interactive element:

1. **Header** — Displays user email/avatar, handles sign-out
2. **Tabs** — Switches between URL/Email/Message analysis forms
3. **Analysis** — Submits text to `aiManager.analyze()`, renders results with classification badge, risk score progress bar, reasons list, and recommendation card
4. **Chatbot** — Full chat system:
   - Message sending via `aiManager.chat()`
   - Chat bubble rendering with markdown support
   - Image upload (converts to base64)
   - Speech-to-text using the Web Speech API
   - Typing indicator animation
5. **Daily Briefing** — Lazy-loads on accordion open via `aiManager.getBriefing()`, renders markdown
6. **Markdown Renderer** — Custom regex-based converter that turns markdown into styled HTML (headings, bold, code blocks, lists, links, etc.)

**Student Tip:** The entire file is wrapped in an **IIFE** (Immediately Invoked Function Expression): `(function() { ... })()`. This prevents all variables from leaking into the global scope — a common pattern in vanilla JS apps!

---

### Other Files

| File | Purpose |
|------|---------|
| **`docs/blueprint.md`** | High-level architecture document describing design decisions |
| **`docs/backend.json`** | API endpoint reference in JSON format |
| **`frontend/assets/bg.png`** | Dark-themed background image used on the login page |
| **`frontend/assets/icon.png`** | ThreatSense AI logo/icon shown in the header |

---

## 🔑 Key Concepts for Students

### 1. Backend-First with Fallback
Every AI call tries the **Python backend** (Gemini AI) first. If it fails, it falls back to **Puter.js** (free browser AI). This ensures the app **never breaks** even if the API quota runs out.

### 2. Separation of Concerns
- **Routers** define the API surface (URLs)
- **Services** contain the business logic (AI calls)
- **Models** define data shapes (validation)
- **Frontend JS modules** each handle one concern (auth, AI, UI)

### 3. No Build Step
The frontend is pure HTML/CSS/JS. No npm, no webpack, no build process. Just serve the `frontend/` folder with any HTTP server and it works.

### 4. Firebase for Auth Only
Firebase handles authentication (login/signup) but the AI work is done by the Python backend and Puter.js. Firebase config keys are public — security comes from Firestore rules.

### 5. Design System Approach
All styles use CSS custom properties (variables). Change `--primary` in one place and the entire app's color scheme updates. This is how professional design systems work.

---

## 🚀 How to Run

```bash
# 1. Install Python dependencies
pip install -r backend/requirements.txt

# 2. Start the backend (port 8001)
python -m uvicorn backend.main:app --port 8001

# 3. Start the frontend (port 5500)
python -m http.server 5500 --directory frontend

# 4. Open in browser
# → http://localhost:5500
```

---

## 🧪 API Quick Reference

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `GET /` | GET | — | `{"status": "ok"}` |
| `POST /api/analyze` | POST | `{"message": "..."}` | `{"classification": "SAFE/SUSPICIOUS/MALICIOUS", "risk_score": 0-100, "reasons": [...], "recommendation": "..."}` |
| `POST /api/chat` | POST | `{"message": "...", "history": [...]}` | `{"reply": "..."}` |
| `GET /api/daily-briefing` | GET | — | `{"briefing": "...markdown..."}` |
