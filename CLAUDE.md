# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**말투 번역기 (Style Translator)** — An AI-powered translation service that rewrites text in different speech styles (formal, casual, SNS) using Google Gemini API. FastAPI backend + React/Vite frontend.

## Development Commands

### Backend

```bash
cd backend
source venv/bin/activate          # activate virtualenv
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs` (Swagger UI).

Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run lint
npm run build
```

## Architecture

### Backend (`backend/`)

- **`main.py`** — FastAPI app with three endpoints:
  - `GET /health` — checks API key configuration
  - `GET /styles` — returns `{key: label}` map from `STYLES`
  - `POST /translate` — takes `{text, target_lang, style}`, builds a system prompt with style description + few-shot examples, calls Gemini, returns `{translated, style}`
- **`styles.py`** — Single source of truth: the `STYLES` dict. Each entry has `label` (shown in UI), `description` (injected into system prompt), and `examples` (few-shot pairs). **Adding a style here automatically exposes it in the frontend dropdown** via `/styles`.
- **`.env`** — Must contain `GEMINI_API_KEY`. The client is initialized at module load; if the key is missing, `/translate` returns HTTP 500.

The translation prompt is built in `_build_system_prompt()`: it injects `target_lang`, `style_def["description"]`, and the few-shot `examples` into a Korean-language system instruction.

Model: `gemini-3.5-flash`, temperature 0.3, max 1024 output tokens.

### Frontend (`frontend/src/App.jsx`)

Single-component React app. On mount, fetches `/styles` to populate the style dropdown (falls back to `FALLBACK_STYLES` if the backend is down). The `handleTranslate` function POSTs to `/translate` with `{text, target_lang, style}`.

API base URL is hardcoded to `http://localhost:8000` — update for production deployment.

CORS is currently locked to `http://localhost:5173` in `main.py` — update for production.

## Adding a New Translation Style

Edit `backend/styles.py` and add an entry to `STYLES`:

```python
"your_key": {
    "label": "UI에 표시될 이름",
    "description": "시스템 프롬프트에 들어갈 스타일 설명",
    "examples": [
        {"source": "원문 예시", "target": "스타일 적용 번역 예시"},
    ],
},
```

No other changes needed — the frontend picks it up automatically via `/styles`.
