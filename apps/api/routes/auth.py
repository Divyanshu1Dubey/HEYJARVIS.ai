"""
HeyJarvis API — Auth Routes
============================
Simple API key authentication for development.
Production will use OAuth2/JWT with proper user management.
"""

from __future__ import annotations

import secrets
import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from shared.models import User, UserRole, TenantStatus
from shared.database import get_db
from sqlalchemy import text as sa_text

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, Any]


class APIKeyRequest(BaseModel):
    tenant_slug: str = Field(..., max_length=100)


class APIKeyResponse(BaseModel):
    api_key: str
    tenant_id: str


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db=Depends(get_db)):
    """
    Login with email/password.
    In development, accepts any non-empty credentials for the demo tenant.
    """
    # In production: verify password hash, issue JWT
    # For demo: accept any login for demo users
    demo_emails = ["admin@brightsmile.example.com", "staff@brightsmile.example.com"]

    if request.email not in demo_emails:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Generate a simple API key
    api_key = f"hj_{secrets.token_urlsafe(32)}"

    return LoginResponse(
        access_token=api_key,
        user={
            "email": request.email,
            "role": "admin" if "admin" in request.email else "staff",
            "tenant_id": "00000000-0000-0000-0000-000000000001",
        },
    )


@router.post("/api-key", response_model=APIKeyResponse)
async def create_api_key(request: APIKeyRequest):
    """
    Create an API key for a tenant.
    Used for webhook authentication and SDK access.
    """
    # In production: verify tenant, create scoped API key
    api_key = f"hj_{secrets.token_urlsafe(32)}"

    return APIKeyResponse(
        api_key=api_key,
        tenant_id="00000000-0000-0000-0000-000000000001",  # Demo tenant
    )


@router.get("/demo")
async def get_demo_info():
    """
    Get demo clinic information for the frontend.
    No authentication required for demo mode.
    """
    from shared.demo_data import get_demo_tenant, get_demo_clinic, get_demo_summary

    tenant = get_demo_tenant()
    clinic = get_demo_clinic()
    summary = get_demo_summary()

    return {
        "tenant": tenant,
        "clinic": clinic,
        "summary": summary,
        "mode": "demo",
    }
