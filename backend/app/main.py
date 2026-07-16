"""FastAPI application entry point for StadiumAI Backend API."""
from __future__ import annotations

import time
import uuid
import datetime
import logging
from collections.abc import Callable
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Base
from app.models.database import engine, SessionLocal, get_db
from app.data.mock_generators import seed_database
from app.services.llm_service import check_gemini_configured

from app.routers import (
    chat, navigation, crowd, incidents, translate,
    transport, match, sustainability, accessibility,
    notifications, admin, users,
)
from typing import Annotated

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("stadium_ai")

app = FastAPI(
    title="StadiumAI Backend API",
    description="Operations & Fan Experience GenAI Concierge Service for FIFA World Cup 2026",
    version="1.0.0",
)

START_TIME = time.time()

SECURITY_HEADERS: dict[str, str] = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Lightweight middleware that injects static security headers into every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        response = await call_next(request)
        if settings.SECURITY_HEADERS_ENABLED:
            for key, value in SECURITY_HEADERS.items():
                response.headers[key] = value
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that adds request_id, trace_id, and latency logging to every request."""

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:16])
        trace_id = request.headers.get("X-Trace-ID", uuid.uuid4().hex[:12])

        request.state.request_id = request_id
        request.state.trace_id = trace_id

        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"

        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            "%s %s -> %d (%.1fms) req=%s trace=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
            trace_id,
        )

        return response


# CORS — strict origins only, no wildcard
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if not origins:
    origins = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database tables, seed mock data, and validate Gemini config on startup."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Seeding initial mock datasets...")
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception:
        logger.exception("Error seeding database")
    finally:
        db.close()

    check_gemini_configured()


@app.get("/api/v1/health", tags=["system"])
def get_system_health():
    """Return basic system health status with uptime and version."""
    uptime = time.time() - START_TIME
    return {
        "status": "ok",
        "uptime": round(uptime, 2),
        "version": "1.0.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.get("/api/v1/health/db", tags=["system"])
def get_db_health(db: Annotated[Session, Depends(get_db)]):
    """Verify database connectivity by executing a simple query."""
    start = time.time()
    try:
        db.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000
        return {
            "status": "healthy",
            "connection_pool": 1,
            "latency_ms": round(latency, 2),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database health check failed: {e!s}",
        ) from e


@app.get("/api/v1/health/ai", tags=["system"])
def get_ai_health():
    """Check Gemini configuration status (no external API call)."""
    api_key = settings.GEMINI_API_KEY.strip()
    model_name = settings.GEMINI_MODEL.strip()

    if not api_key:
        return {
            "status": "unconfigured",
            "provider": "Google Gemini",
            "details": "GEMINI_API_KEY environment variable is missing or empty.",
        }

    return {
        "status": "configured",
        "provider": "Google Gemini",
        "model": model_name,
        "last_response_time_ms": 0.0,
        "quota_remaining": None,
    }


app.include_router(chat.router)
app.include_router(navigation.router)
app.include_router(crowd.router)
app.include_router(incidents.router)
app.include_router(translate.router)
app.include_router(transport.router)
app.include_router(match.router)
app.include_router(sustainability.router)
app.include_router(accessibility.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(users.router)
