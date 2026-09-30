"""
HeyJarvis API Application
=========================
FastAPI application with all routes, middleware, and startup logic.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.models import TenantStatus
from shared.database import init_db, get_db, engine
from shared.demo_data import seed_demo_data, get_demo_tenant, get_demo_clinic

logger = logging.getLogger(__name__)


# =============================================================================
# Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    logger.info("Starting HeyJarvis API...")
    init_db()
    logger.info("Database initialized")

    # Seed demo data if empty
    from sqlalchemy import text as sa_text
    with engine.connect() as conn:
        result = conn.execute(sa_text("SELECT COUNT(*) FROM tenants"))
        count = result.scalar()
        if count == 0:
            logger.info("Seeding demo data...")
            seed_demo_data()
            logger.info("Demo data seeded")

    logger.info("HeyJarvis API ready")
    yield
    # Shutdown
    logger.info("Shutting down HeyJarvis API...")


# =============================================================================
# App
# =============================================================================

app = FastAPI(
    title="HeyJarvis Patient Recapture API",
    description="AI-powered patient recapture and revenue recovery for dental practices",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"},
    )


# =============================================================================
# Health
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "heyjarvis-api", "version": "0.1.0"}


@app.get("/health/ready")
async def readiness_check():
    """Readiness check — verifies database connection."""
    try:
        from sqlalchemy import text as sa_text
        with engine.connect() as conn:
            conn.execute(sa_text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "not ready", "error": str(e)})


# =============================================================================
# Include Routes
# =============================================================================

from apps.api.routes import patients, conversations, messages, recapture, appointments, analytics, campaigns, auth

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["conversations"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(recapture.router, prefix="/api/v1/recapture", tags=["recapture"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["appointments"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["campaigns"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
