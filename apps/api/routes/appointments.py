"""
HeyJarvis API — Appointment Routes
=====================================
Appointment management endpoints.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.integrations import ProviderFactory
from shared.demo_data import get_demo_clinic
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class AvailabilityRequest(BaseModel):
    clinic_id: str
    appointment_type: str = Field(..., max_length=100)
    date_from: str
    date_to: str
    duration_minutes: int = Field(default=30, ge=5, le=480)


class AvailabilitySlot(BaseModel):
    start: str
    end: str
    provider_id: str
    provider_name: str
    room: str
    appointment_type: str


class AvailabilityResponse(BaseModel):
    slots: list[AvailabilitySlot]
    count: int


class BookAppointmentRequest(BaseModel):
    clinic_id: str
    patient_id: str
    provider_id: str
    appointment_type: str = Field(..., max_length=100)
    start: str
    duration_minutes: int = Field(default=30, ge=5, le=480)


class BookAppointmentResponse(BaseModel):
    success: bool
    appointment_id: str | None = None
    status: str
    error: str | None = None


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/availability", response_model=AvailabilityResponse)
async def check_availability(request: AvailabilityRequest):
    """
    Check appointment availability.

    Uses the scheduling provider adapter.
    """
    provider = ProviderFactory.create_scheduling_provider("mock")

    date_from = datetime.fromisoformat(request.date_from)
    date_to = datetime.fromisoformat(request.date_to)

    result = await provider.check_availability(
        clinic_id=request.clinic_id,
        appointment_type=request.appointment_type,
        date_from=date_from,
        date_to=date_to,
        duration_minutes=request.duration_minutes,
    )

    if not result.success:
        raise HTTPException(status_code=503, detail=result.error)

    return AvailabilityResponse(
        slots=[
            AvailabilitySlot(
                start=s["start"],
                end=s["end"],
                provider_id=s["provider_id"],
                provider_name=s["provider_name"],
                room=s["room"],
                appointment_type=s["appointment_type"],
            )
            for s in result.data
        ],
        count=len(result.data),
    )


@router.post("/book", response_model=BookAppointmentResponse)
async def book_appointment(request: BookAppointmentRequest):
    """
    Book an appointment.

    IMPORTANT: In production, this requires:
      1. Policy check (consent, frequency caps)
      2. Slot hold (prevent double-booking)
      3. Actual booking via scheduling provider
      4. Confirmation message
      5. Event emission
    """
    provider = ProviderFactory.create_scheduling_provider("mock")
    start = datetime.fromisoformat(request.start)

    result = await provider.book_appointment(
        clinic_id=request.clinic_id,
        patient_id=request.patient_id,
        provider_id=request.provider_id,
        appointment_type=request.appointment_type,
        start=start,
        duration_minutes=request.duration_minutes,
    )

    if not result.success:
        return BookAppointmentResponse(
            success=False,
            status="failed",
            error=result.error,
        )

    return BookAppointmentResponse(
        success=True,
        appointment_id=result.data["appointment_id"],
        status=result.data["status"],
    )


@router.get("/providers")
async def list_providers(clinic_id: str):
    """List available providers at a clinic."""
    return {
        "clinic_id": clinic_id,
        "providers": [
            {"id": "44444444-4444-4444-4444-444444444444", "name": "Dr. Sarah Mitchell", "specialty": "General Dentistry"},
            {"id": "55555555-5555-5555-5555-555555555555", "name": "Dr. James Chen", "specialty": "Orthodontics"},
        ],
    }


@router.get("/services")
async def list_services(clinic_id: str):
    """List available services at a clinic."""
    from shared.demo_data import DEMO_SERVICES
    return {"clinic_id": clinic_id, "services": DEMO_SERVICES}
