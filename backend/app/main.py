import time
import datetime
import logging
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import Config, DB, and Routers
from app.config import settings
from app.models import Base
from app.models.database import engine, SessionLocal, get_db
from app.data.mock_generators import seed_database
from app.services.analytics_service import AnalyticsService

# Import all routers
from app.routers import (
    chat, navigation, crowd, incidents, translate,
    transport, match, sustainability, accessibility,
    notifications, admin, users
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stadium_ai")

app = FastAPI(
    title="StadiumAI Backend API",
    description="Operations & Fan Experience GenAI Concierge Service for FIFA World Cup 2026",
    version="1.0.0"
)

# Start time for uptime calculation
START_TIME = time.time()

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_records = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        current_time = time.time()
        
        if client_ip in self.ip_records:
            self.ip_records[client_ip] = [t for t in self.ip_records[client_ip] if current_time - t < self.window_seconds]
        else:
            self.ip_records[client_ip] = []
            
        if len(self.ip_records[client_ip]) >= self.max_requests:
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
            
        self.ip_records[client_ip].append(current_time)
        return await call_next(request)

# CORS configuration
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip() and o.strip() != "*"]
if not origins:
    origins = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, max_requests=settings.RATE_LIMIT_PER_MINUTE)

# Middleware for measuring response latency and logging analytics
@app.middleware("http")
async def log_analytics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency_ms = (time.time() - start) * 1000

    path = request.url.path
    # Ignore health checks, docs, and schema definitions
    if path.startswith("/api/v1") and not "/health" in path:
        db = SessionLocal()
        try:
            user_id = request.headers.get("X-User-ID") or request.query_params.get("user_id")
            analytics = AnalyticsService(db)
            analytics.log_request(
                endpoint=path,
                method=request.method,
                status_code=response.status_code,
                latency_ms=latency_ms,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"Failed to log request analytics: {e}")
        finally:
            db.close()

    return response

# Startup Lifecycle
@app.on_event("startup")
def startup_event():
    # 1. Initialize DB tables
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed mock data
    logger.info("Seeding initial mock datasets...")
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()

    # 3. Check Gemini configurations (non-blocking warning logs)
    from app.services.llm_service import check_gemini_configured
    check_gemini_configured()

# Health Endpoints
@app.get("/api/v1/health", tags=["system"])
def get_system_health():
    uptime = time.time() - START_TIME
    return {
        "status": "ok",
        "uptime": round(uptime, 2),
        "version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health/db", tags=["system"])
def get_db_health(db: Session = Depends(get_db)):
    start = time.time()
    try:
        # Run a simple query to assert DB connectivity
        db.execute("SELECT 1")
        latency = (time.time() - start) * 1000
        return {
            "status": "healthy",
            "connection_pool": 1,
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database health check failed: {str(e)}"
        )

@app.get("/api/v1/health/ai", tags=["system"])
def get_ai_health():
    """
    Checks if Gemini is configured.
    If GEMINI_API_KEY is missing, returns status: unconfigured.
    No external API call is made during health check (lazy validation).
    """
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", "").strip()
    
    if not api_key:
        return {
            "status": "unconfigured",
            "provider": "Google Gemini",
            "details": "GEMINI_API_KEY environment variable is missing or empty."
        }
    
    return {
        "status": "configured",
        "provider": "Google Gemini",
        "model": model_name,
        "last_response_time_ms": 0.0,  # lazy check, not making call
        "quota_remaining": None
    }

# Register Routers
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
