"""
HeyJarvis Worker — Recapture Tasks
=====================================
Recapture detection and scoring tasks.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from celery import shared_task

from shared.demo_data import _make_patients, _make_appointments
from shared.models import PatientState, AppointmentStatus

logger = logging.getLogger(__name__)


@shared_task
def score_patient(patient_id: str) -> dict[str, Any]:
    """
    Score a patient for recapture priority.

    Factors:
      - Time since last contact
      - Appointment value
      - Previous engagement
      - Recapture type
      - Patient state
    """
    patients = {p["id"]: p for p in _make_patients()}
    patient = patients.get(patient_id)

    if not patient:
        return {"error": "Patient not found"}

    # Simple scoring (production uses ML model)
    base_score = 50.0

    # Boost for high-value appointments
    value = patient.get("appointment_value", 0)
    if value > 1000:
        base_score += 20
    elif value > 500:
        base_score += 10

    # Boost for recent activity
    last_contact = patient.get("last_contact_at")
    if last_contact is None:
        base_score += 15  # Never contacted — good opportunity
    else:
        days_since = (datetime.utcnow() - last_contact).days
        if days_since > 14:
            base_score += 10

    # Cap at 100
    score = min(base_score, 100.0)

    return {
        "patient_id": patient_id,
        "priority_score": score,
        "factors": {
            "appointment_value": value,
            "state": patient.get("state"),
            "last_contact_days": (datetime.utcnow() - last_contact).days if last_contact else None,
        },
    }


@shared_task
def batch_score_patients(patient_ids: list[str]) -> dict[str, Any]:
    """Score multiple patients in batch."""
    results = []
    for pid in patient_ids:
        result = score_patient(pid)
        results.append(result)
    return {"scored": len(results), "results": results}
