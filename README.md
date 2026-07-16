# StadiumAI

**FIFA World Cup 2026 — AI-Powered Stadium Operations & Fan Experience Platform**

![CI](https://img.shields.io/badge/CI-Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Overview

StadiumAI is a real-time AI concierge platform for the FIFA World Cup 2026. It combines Google Gemini AI, spatial navigation, crowd analytics, incident dispatch, and multilingual translation into a single integrated system.

## Architecture

```
┌──────────────┐     HTTPS/REST     ┌──────────────────┐     SQLAlchemy     ┌──────────┐
│   React PWA  │ ◄────────────────► │   FastAPI Backend │ ◄───────────────► │  SQLite  │
│  TypeScript  │                    │   Python 3.12    │                    │   DB     │
└──────────────┘                    └──────────────────┘                    └──────────┘
       │                                    │
       │ Service Worker                     │ Gemini API
       ▼                                    ▼
  Offline Cache                      ┌──────────────┐
  Workbox                            │ Google Gemini │
                                     │     AI       │
                                     └──────────────┘
```

## Features

| Category | Capabilities |
|----------|-------------|
| **AI Chat** | Gemini-powered concierge with tool calling (navigation, crowd, transport, incidents, waste, accessibility, match stats) |
| **Navigation** | Dijkstra-based pathfinding with crowd-aware routing and accessibility mode |
| **Crowd Analytics** | Real-time density tracking, trend analysis, risk assessment |
| **Incident Dispatch** | AI-classified incident reporting with priority routing |
| **Translation** | Multilingual translation with cultural context |
| **Transport** | Transit routing with traffic levels and mode comparison |
| **Sustainability** | Waste classification and nearest-bin location |
| **Accessibility** | Elevator/ramp/wait-time information |
| **PWA** | Offline support, background sync, service worker |

## Project Structure

```
stadium-ai-anti/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment settings
│   │   ├── dependencies.py      # Rate limiting, DB sessions
│   │   ├── data/                # Stadium graph, mock data
│   │   ├── models/              # SQLAlchemy models, Pydantic schemas
│   │   ├── routers/             # API endpoint handlers (12 routers)
│   │   ├── services/            # Business logic (LLM, navigation, crowd, etc.)
│   │   └── utils/               # Pathfinder algorithm
│   ├── tests/                   # 163 pytest tests, 95%+ coverage
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client, IndexedDB, sync
│   │   └── lib/                 # UI utilities
│   └── package.json
└── .github/workflows/ci.yml    # CI/CD pipeline
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-pro"

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | System health check |
| GET | `/api/v1/health/db` | Database connectivity |
| GET | `/api/v1/health/ai` | Gemini configuration status |
| POST | `/api/v1/chat/` | AI concierge chat |
| POST | `/api/v1/translate/` | Multilingual translation |
| GET | `/api/v1/navigate` | Stadium navigation |
| GET | `/api/v1/crowd/all` | Crowd density heatmap |
| POST | `/api/v1/incidents/` | Report incident |
| GET | `/api/v1/transport` | Transit options |
| GET | `/api/v1/match/current` | Live match data |
| POST | `/api/v1/sustainability/waste` | Waste classification |
| GET | `/api/v1/accessibility` | Accessibility services |
| POST | `/api/v1/users/session` | Create user session |
| GET | `/api/v1/users/{id}/history` | Chat history |
| GET | `/api/v1/admin/dashboard` | Admin dashboard |
| GET | `/api/v1/admin/incidents` | Incident list |
| PATCH | `/api/v1/admin/incidents/{id}` | Update incident |
| GET | `/api/v1/admin/crowd/analytics` | Crowd analytics |
| GET | `/api/v1/admin/staff` | Staff listing |
| POST | `/api/v1/admin/announcements` | Broadcast announcement |
| GET | `/api/v1/admin/analytics/usage` | API usage analytics |

## Testing

```bash
cd backend
python -m pytest tests/ --cov=app --cov-report=term-missing -v

cd frontend
npx vitest run
```

## Security

- Per-route rate limiting (chat: 20/min, navigation: 50/min, incidents: 10/min, general: 100/min)
- Security headers (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy)
- CORS with strict origins
- Pydantic input validation on all endpoints
- No hardcoded secrets

## Deployment

### Frontend (Vercel)

```bash
cd frontend
npm run build
vercel deploy --prod
```

### Backend (Railway / Render)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `GEMINI_MODEL` | Yes | Gemini model name (e.g., `gemini-pro`) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
| `RATE_LIMIT_PER_MINUTE` | No | Default rate limit (default: 100) |
| `SECURITY_HEADERS_ENABLED` | No | Enable security headers (default: true) |

## License

MIT
