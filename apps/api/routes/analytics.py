"""
HeyJarvis API — Analytics Routes
==================================
Analytics and reporting endpoints.
"""

from __future__ import annotations

import logging
from typing import Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from shared.database import get_db
from shared.demo_data import get_demo_summary, _make_patients, _make_recapture_opportunities
from shared.models import PatientState

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class KPIData(BaseModel):
    total_patients: int
    total_opportunities: int
    total_potential_revenue: float
    avg_appointment_value: float
    opportunities_by_state: dict[str, int]
    opportunities_by_category: dict[str, int]


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/summary", response_model=KPIData)
async def get_summary():
    """Get overall analytics summary."""
    summary = get_demo_summary()
    patients = _make_patients()

    # State breakdown
    state_counts: dict[str, int] = {}
    for p in patients:
        s = p.get("state", "unknown")
        state_counts[s.value if hasattr(s, 'value') else str(s)] = state_counts.get(str(s.value if hasattr(s, 'value') else s), 0) + 1

    return KPIData(
        total_patients=summary["total_patients"],
        total_opportunities=summary["total_opportunities"],
        total_potential_revenue=summary["total_potential_revenue"],
        avg_appointment_value=summary["avg_appointment_value"],
        opportunities_by_state=state_counts,
        opportunities_by_category=summary["categories"],
    )


@router.get("/revenue")
async def get_revenue_metrics(
    date_from: str = Query("2024-01-01"),
    date_to: str = Query("2025-12-31"),
):
    """Get revenue recovery metrics."""
    opportunities = _make_recapture_opportunities()
    total_value = sum(o.get("appointment_value", 0) for o in opportunities)

    return {
        "date_from": date_from,
        "date_to": date_to,
        "total_potential_revenue": total_value,
        "opportunity_count": len(opportunities),
        "avg_opportunity_value": total_value / len(opportunities) if opportunities else 0,
        "projected_recovery_rate": 0.15,  # 15% recovery rate estimate
        "projected_recovered": total_value * 0.15,
    }


@router.get("/channel-performance")
async def get_channel_performance():
    """Get performance metrics by channel."""
    return {
        "channels": [
            {"channel": "sms", "sent": 150, "delivered": 142, "replied": 23, "booked": 12, "response_rate": 0.16, "conversion_rate": 0.08},
            {"channel": "email", "sent": 80, "delivered": 75, "replied": 8, "booked": 3, "response_rate": 0.11, "conversion_rate": 0.04},
            {"channel": "voice", "sent": 20, "delivered": 18, "replied": 6, "booked": 4, "response_rate": 0.33, "conversion_rate": 0.22},
        ]
    }


@router.get("/campaign-performance")
async def get_campaign_performance():
    """Get performance metrics by campaign."""
    return {
        "campaigns": [
            {"name": "Abandoned Lead Recovery", "sent": 45, "replied": 12, "booked": 5, "revenue": 1500},
            {"name": "Cancellation Recovery", "sent": 30, "replied": 8, "booked": 4, "revenue": 600},
            {"name": "No-Show Recovery", "sent": 25, "replied": 6, "booked": 3, "revenue": 450},
            {"name": "Treatment Plan Follow-Up", "sent": 15, "replied": 4, "booked": 2, "revenue": 2400},
            {"name": "Hygiene Recall", "sent": 40, "replied": 10, "booked": 6, "revenue": 900},
        ]
    }
