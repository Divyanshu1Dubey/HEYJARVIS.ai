"""
HeyJarvis API — Patient Routes
================================
Patient CRUD operations and patient timeline.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.demo_data import seed_demo_data, _make_patients, get_demo_tenant

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class PatientResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    phone: str | None = None
    email: str | None = None
    state: str
    timezone: str
    notes: str | None = None
    appointment_value: float | None = None


class PatientListResponse(BaseModel):
    patients: list[PatientResponse]
    total: int
    page: int
    page_size: int


class PatientTimelineResponse(BaseModel):
    patient: PatientResponse
    events: list[dict[str, Any]]


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    state: str | None = Query(None),
    db=Depends(get_db),
):
    """List all patients with optional filtering."""
    # Ensure demo data exists
    from sqlalchemy import text as sa_text
    with db.bind.connect() as conn:
        result = conn.execute(sa_text("SELECT COUNT(*) FROM patients"))
        count = result.scalar()
        if count == 0:
            seed_demo_data()

    # Get patients from demo data (in production, query DB)
    all_patients = _make_patients()
    tenant_id = get_demo_tenant()["id"]

    # Filter by state
    if state:
        from shared.models import PatientState
        try:
            state_enum = PatientState(state)
            all_patients = [p for p in all_patients if p.get("state") == state_enum]
        except ValueError:
            pass

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_patients = all_patients[start:end]

    return PatientListResponse(
        patients=[
            PatientResponse(
                id=p["id"],
                first_name=p["first_name"],
                last_name=p["last_name"],
                phone=p.get("phone"),
                email=p.get("email"),
                state=p.get("state", "new_lead"),
                timezone=p.get("timezone", "America/Chicago"),
                notes=p.get("notes"),
                appointment_value=p.get("appointment_value"),
            )
            for p in page_patients
        ],
        total=len(all_patients),
        page=page,
        page_size=page_size,
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str, db=Depends(get_db)):
    """Get a single patient by ID."""
    from sqlalchemy import text as sa_text
    with db.bind.connect() as conn:
        result = conn.execute(
            sa_text("SELECT * FROM patients WHERE id = :id"),
            {"id": patient_id},
        )
        row = result.mappings().first()

    if not row:
        # Check demo data
        patients = _make_patients()
        for p in patients:
            if p["id"] == patient_id:
                return PatientResponse(
                    id=p["id"],
                    first_name=p["first_name"],
                    last_name=p["last_name"],
                    phone=p.get("phone"),
                    email=p.get("email"),
                    state=p.get("state", "new_lead"),
                    timezone=p.get("timezone", "America/Chicago"),
                    notes=p.get("notes"),
                    appointment_value=p.get("appointment_value"),
                )
        raise HTTPException(status_code=404, detail="Patient not found")

    return PatientResponse(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        phone=row.get("phone"),
        email=row.get("email"),
        state=row.get("state", "new_lead"),
        timezone=row.get("timezone", "America/Chicago"),
        notes=row.get("notes"),
    )


@router.get("/{patient_id}/timeline", response_model=PatientTimelineResponse)
async def get_patient_timeline(patient_id: str, db=Depends(get_db)):
    """Get the full timeline for a patient."""
    # Get patient
    patient = await get_patient(patient_id, db)

    # Build timeline events (in production: query events table)
    from shared.demo_data import _make_conversations, _make_messages
    conversations = _make_conversations()
    messages = _make_messages()

    events = []

    # Add conversations
    for conv in conversations:
        if conv.get("patient_id") == patient_id:
            events.append({
                "type": "conversation",
                "timestamp": conv.get("started_at", ""),
                "data": {
                    "channel": conv.get("channel"),
                    "state": conv.get("state"),
                    "ai_handled": conv.get("ai_handled"),
                },
            })

    # Add messages
    for msg in messages:
        if msg.get("patient_id") == patient_id:
            events.append({
                "type": "message",
                "timestamp": msg.get("sent_at", ""),
                "data": {
                    "direction": msg.get("direction"),
                    "channel": msg.get("channel"),
                    "body": msg.get("body", "")[:200],
                },
            })

    # Sort by timestamp
    events.sort(key=lambda e: e.get("timestamp", ""))

    return PatientTimelineResponse(patient=patient, events=events)
