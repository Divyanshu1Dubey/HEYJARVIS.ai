"""
HeyJarvis API — Recapture Routes
==================================
Recapture opportunity management and campaign execution.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.demo_data import _make_recapture_opportunities, _make_campaigns, get_demo_summary, _make_patients
from shared.policy_engine import PolicyEngine, PolicyDecision
from shared.models import ChannelType

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class OpportunityResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    recapture_type: str
    reason: str
    state: str
    priority_score: float
    conversion_probability: float
    recommended_channel: str
    appointment_value: float | None
    detected_at: str
    attempt_count: int
    status: str


class OpportunityListResponse(BaseModel):
    opportunities: list[OpportunityResponse]
    total: int
    page: int
    page_size: int


class SummaryResponse(BaseModel):
    clinic: str
    total_patients: int
    total_opportunities: int
    categories: dict[str, int]
    total_potential_revenue: float
    avg_appointment_value: float


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/opportunities", response_model=OpportunityListResponse)
async def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    recapture_type: str | None = Query(None),
):
    """List all recapture opportunities."""
    opportunities = _make_recapture_opportunities()
    patients = _make_patients()
    patient_map = {p["id"]: p for p in patients}

    # Filter by type
    if recapture_type:
        opportunities = [o for o in opportunities if o.get("recapture_type") == recapture_type]

    # Enrich with patient names
    enriched = []
    for o in opportunities:
        patient = patient_map.get(o["patient_id"], {})
        enriched.append({
            **o,
            "patient_name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}",
        })

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_items = enriched[start:end]

    return OpportunityListResponse(
        opportunities=[
            OpportunityResponse(
                id=o["id"],
                patient_id=o["patient_id"],
                patient_name=o.get("patient_name", ""),
                recapture_type=o.get("recapture_type", ""),
                reason=o.get("reason", ""),
                state=o.get("state", ""),
                priority_score=o.get("priority_score", 0),
                conversion_probability=o.get("conversion_probability", 0),
                recommended_channel=o.get("recommended_channel", "sms"),
                appointment_value=o.get("appointment_value"),
                detected_at=o.get("detected_at", ""),
                attempt_count=o.get("attempt_count", 0),
                status=o.get("status", "pending"),
            )
            for o in page_items
        ],
        total=len(enriched),
        page=page,
        page_size=page_size,
    )


@router.get("/opportunities/summary", response_model=SummaryResponse)
async def get_summary():
    """Get recapture summary for the dashboard."""
    summary = get_demo_summary()
    return SummaryResponse(**summary)


@router.get("/opportunities/types")
async def get_recapture_types():
    """Get all recapture opportunity types with counts."""
    opportunities = _make_recapture_opportunities()
    types: dict[str, int] = {}
    for o in opportunities:
        t = o.get("recapture_type", "other")
        types[t] = types.get(t, 0) + 1

    return {"types": [{"type": k, "count": v} for k, v in sorted(types.items(), key=lambda x: -x[1])]}


@router.post("/opportunities/{opportunity_id}/attempt")
async def create_attempt(opportunity_id: str):
    """Create a new outreach attempt for an opportunity."""
    return {
        "opportunity_id": opportunity_id,
        "status": "created",
        "message": "Attempt created. In production, this would trigger campaign execution.",
    }


@router.get("/campaigns")
async def list_campaigns():
    """List all recapture campaigns."""
    campaigns = _make_campaigns()
    return {"campaigns": campaigns}


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details."""
    campaigns = _make_campaigns()
    campaign = next((c for c in campaigns if c["id"] == campaign_id), None)
    if not campaign:
        return {"error": "Campaign not found"}
    return campaign
