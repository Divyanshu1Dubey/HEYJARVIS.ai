"""
HeyJarvis API — Campaign Routes
=================================
Campaign management and execution endpoints.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.demo_data import _make_campaigns

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class CampaignResponse(BaseModel):
    id: str
    name: str
    description: str | None
    recapture_type: str
    status: str
    max_attempts: int
    cooldown_hours: int
    daily_cap: int
    is_active: bool


class CampaignListResponse(BaseModel):
    campaigns: list[CampaignResponse]
    total: int


class CreateCampaignRequest(BaseModel):
    tenant_id: str
    clinic_id: str
    name: str = Field(..., max_length=255)
    description: str | None = None
    recapture_type: str = Field(..., max_length=100)
    max_attempts: int = Field(default=3, ge=1, le=10)
    cooldown_hours: int = Field(default=24, ge=0)
    daily_cap: int = Field(default=100, ge=1)


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=CampaignListResponse)
async def list_campaigns():
    """List all campaigns."""
    campaigns = _make_campaigns()
    return CampaignListResponse(
        campaigns=[
            CampaignResponse(
                id=c["id"],
                name=c["name"],
                description=c.get("description"),
                recapture_type=c["recapture_type"],
                status=c["status"],
                max_attempts=c["max_attempts"],
                cooldown_hours=c["cooldown_hours"],
                daily_cap=c["daily_cap"],
                is_active=c["is_active"],
            )
            for c in campaigns
        ],
        total=len(campaigns),
    )


@router.post("/", response_model=CampaignResponse)
async def create_campaign(request: CreateCampaignRequest):
    """Create a new recapture campaign."""
    import uuid
    from datetime import datetime
    from shared.models import CampaignStatus

    campaign_id = str(uuid.uuid4())
    now = datetime.utcnow()

    campaign = {
        "id": campaign_id,
        "tenant_id": request.tenant_id,
        "clinic_id": request.clinic_id,
        "name": request.name,
        "description": request.description,
        "recapture_type": request.recapture_type,
        "status": CampaignStatus.DRAFT,
        "is_active": False,
        "max_attempts": request.max_attempts,
        "cooldown_hours": request.cooldown_hours,
        "daily_cap": request.daily_cap,
        "start_at": now,
        "end_at": None,
    }

    return CampaignResponse(
        id=campaign["id"],
        name=campaign["name"],
        description=campaign.get("description"),
        recapture_type=campaign["recapture_type"],
        status=campaign["status"],
        max_attempts=campaign["max_attempts"],
        cooldown_hours=campaign["cooldown_hours"],
        daily_cap=campaign["daily_cap"],
        is_active=campaign["is_active"],
    )


@router.post("/{campaign_id}/start")
async def start_campaign(campaign_id: str):
    """Start a campaign."""
    return {"campaign_id": campaign_id, "status": "started"}


@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Pause a running campaign."""
    return {"campaign_id": campaign_id, "status": "paused"}


@router.post("/{campaign_id}/stop")
async def stop_campaign(campaign_id: str):
    """Stop a campaign."""
    return {"campaign_id": campaign_id, "status": "stopped"}
