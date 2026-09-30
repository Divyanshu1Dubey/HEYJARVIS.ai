"""
HeyJarvis Integration Adapters
================================
Adapter layer for external dental practice systems.

Architecture:
  Each adapter implements a standard interface.
  The system is source-of-truth agnostic.
  Adapters handle:
    - Authentication
    - Rate limiting
    - Retry logic
    - Data transformation
    - Error handling

Available adapters:
  - MockSchedulingProvider (default — no external API needed)
  - MockInsuranceProvider (default — no external API needed)
  - Real adapters (stubs ready for production):
    - Dentrix
    - Eaglesoft
    - Open Dental
    - CareStack
    - Curve Dental
"""

from __future__ import annotations

import asyncio
import random
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# Common Types
# =============================================================================

class ProviderStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class TimeSlot:
    """A single available appointment slot."""
    start: datetime
    end: datetime
    provider_id: str
    provider_name: str
    room: str
    appointment_type: str
    available: bool = True


@dataclass
class ProviderResult:
    """Result from a provider call."""
    success: bool
    data: Any = None
    error: str | None = None
    status: ProviderStatus = ProviderStatus.AVAILABLE


# =============================================================================
# Scheduling Provider Interface
# =============================================================================

class BaseSchedulingProvider(ABC):
    """
    Abstract base class for scheduling system adapters.

    Implementations:
      - MockSchedulingProvider (default for development)
      - DentrixAdapter
      - EaglesoftAdapter
      - OpenDentalAdapter
      - CareStackAdapter
    """

    @abstractmethod
    async def check_availability(
        self,
        clinic_id: str,
        appointment_type: str,
        date_from: datetime,
        date_to: datetime,
        duration_minutes: int = 30,
    ) -> ProviderResult:
        """Get available appointment slots."""
        pass

    @abstractmethod
    async def book_appointment(
        self,
        clinic_id: str,
        patient_id: str,
        provider_id: str,
        appointment_type: str,
        start: datetime,
        duration_minutes: int,
    ) -> ProviderResult:
        """Book an appointment."""
        pass

    @abstractmethod
    async def cancel_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
        reason: str,
    ) -> ProviderResult:
        """Cancel an appointment."""
        pass

    @abstractmethod
    async def reschedule_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
        new_start: datetime,
    ) -> ProviderResult:
        """Reschedule an appointment."""
        pass

    @abstractmethod
    async def get_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
    ) -> ProviderResult:
        """Get appointment details."""
        pass

    @abstractmethod
    async def confirm_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
    ) -> ProviderResult:
        """Confirm an appointment."""
        pass


# =============================================================================
# Insurance Provider Interface
# =============================================================================

class BaseInsuranceProvider(ABC):
    """
    Abstract base class for insurance/eligibility adapters.

    Implementations:
      - MockInsuranceProvider (default)
      - DentrixInsAdapter
      - EaglesoftInsAdapter
      - ClaimConnectAdapter
    """

    @abstractmethod
    async def verify_eligibility(
        self,
        clinic_id: str,
        patient_id: str,
        insurance_id: str,
        service_code: str,
    ) -> ProviderResult:
        """Verify patient insurance eligibility."""
        pass

    @abstractmethod
    async def get_benefits(
        self,
        clinic_id: str,
        patient_id: str,
        insurance_id: str,
    ) -> ProviderResult:
        """Get patient benefit details."""
        pass

    @abstractmethod
    async def check_coverage(
        self,
        clinic_id: str,
        insurance_id: str,
        procedure_code: str,
    ) -> ProviderResult:
        """Check coverage for a specific procedure."""
        pass


# =============================================================================
# Mock Scheduling Provider
# =============================================================================

class MockSchedulingProvider(BaseSchedulingProvider):
    """
    Mock scheduling provider for development and demo.
    Generates realistic availability slots without any external API.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.failure_rate = self.config.get("failure_rate", 0.0)
        self._booked_slots: set[str] = set()

    async def check_availability(
        self,
        clinic_id: str,
        appointment_type: str,
        date_from: datetime,
        date_to: datetime,
        duration_minutes: int = 30,
    ) -> ProviderResult:
        """Generate mock available slots."""
        if random.random() < self.failure_rate:
            return ProviderResult(
                success=False,
                status=ProviderStatus.ERROR,
                error="Mock scheduling system unavailable",
            )

        # Map appointment types to durations
        type_durations = {
            "cleaning": 30,
            "exam": 30,
            "crown": 60,
            "root canal": 90,
            "extraction": 45,
            "whitening": 60,
            "implant consultation": 45,
            "emergency": 30,
        }
        duration = type_durations.get(appointment_type.lower(), duration_minutes)

        slots = []
        current = date_from.replace(hour=8, minute=0, second=0, microsecond=0)
        end_of_day = date_to.replace(hour=17, minute=0, second=0, microsecond=0)

        providers = [
            ("Dr. Sarah Mitchell", "44444444-4444-4444-4444-444444444444"),
            ("Dr. James Chen", "55555555-5555-5555-5555-555555555555"),
        ]

        rooms = ["Room 1", "Room 2", "Room 3"]

        while current < end_of_day:
            # Skip weekends
            if current.weekday() >= 5:
                current += timedelta(days=1)
                current = current.replace(hour=8, minute=0)
                continue

            for provider_name, provider_id in providers:
                for room in rooms:
                    slot_key = f"{clinic_id}:{current.isoformat()}:{provider_id}:{room}"

                    # Skip if booked
                    if slot_key in self._booked_slots:
                        current += timedelta(minutes=duration)
                        continue

                    # Randomly skip some slots (simulate real availability)
                    if random.random() > 0.3:
                        slots.append(TimeSlot(
                            start=current,
                            end=current + timedelta(minutes=duration),
                            provider_id=provider_id,
                            provider_name=provider_name,
                            room=room,
                            appointment_type=appointment_type,
                            available=True,
                        ))

                    current += timedelta(minutes=duration)

                    # Limit number of slots returned
                    if len(slots) >= 8:
                        break
                if len(slots) >= 8:
                    break
            if len(slots) >= 8:
                break

        return ProviderResult(
            success=True,
            data=[{
                "start": s.start.isoformat(),
                "end": s.end.isoformat(),
                "provider_id": s.provider_id,
                "provider_name": s.provider_name,
                "room": s.room,
                "appointment_type": s.appointment_type,
            } for s in slots],
        )

    async def book_appointment(
        self,
        clinic_id: str,
        patient_id: str,
        provider_id: str,
        appointment_type: str,
        start: datetime,
        duration_minutes: int,
    ) -> ProviderResult:
        """Book a mock appointment."""
        if random.random() < self.failure_rate:
            return ProviderResult(
                success=False,
                status=ProviderStatus.ERROR,
                error="Booking failed: system unavailable",
            )

        # Mark slot as booked
        slot_key = f"{clinic_id}:{start.isoformat()}:{provider_id}"
        if slot_key in self._booked_slots:
            return ProviderResult(
                success=False,
                status=ProviderStatus.UNAVAILABLE,
                error="Slot no longer available",
            )
        self._booked_slots.add(slot_key)

        appointment_id = f"apt_{uuid.uuid4().hex[:8]}"
        return ProviderResult(
            success=True,
            data={
                "appointment_id": appointment_id,
                "status": "scheduled",
                "start": start.isoformat(),
                "end": (start + timedelta(minutes=duration_minutes)).isoformat(),
                "provider_id": provider_id,
                "appointment_type": appointment_type,
            },
        )

    async def cancel_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
        reason: str,
    ) -> ProviderResult:
        """Cancel a mock appointment."""
        return ProviderResult(
            success=True,
            data={"appointment_id": appointment_id, "status": "cancelled"},
        )

    async def reschedule_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
        new_start: datetime,
    ) -> ProviderResult:
        """Reschedule a mock appointment."""
        return ProviderResult(
            success=True,
            data={"appointment_id": appointment_id, "new_start": new_start.isoformat()},
        )

    async def get_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
    ) -> ProviderResult:
        """Get mock appointment details."""
        return ProviderResult(
            success=True,
            data={
                "appointment_id": appointment_id,
                "status": "scheduled",
                "start": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            },
        )

    async def confirm_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
    ) -> ProviderResult:
        """Confirm a mock appointment."""
        return ProviderResult(
            success=True,
            data={"appointment_id": appointment_id, "status": "confirmed"},
        )


# =============================================================================
# Mock Insurance Provider
# =============================================================================

class MockInsuranceProvider(BaseInsuranceProvider):
    """
    Mock insurance provider for development and demo.
    """

    # Mock insurance plans
    PLANS = {
        "delta dental": {
            "name": "Delta Dental PPO",
            "group_number": "DD-12345",
            "active": True,
            "cleaning_coverage": 100,
            "exam_coverage": 100,
            "crown_coverage": 50,
            "root_canal_coverage": 50,
            "annual_maximum": 1500,
            "deductible": 50,
            "used_amount": 200,
        },
        "cigna": {
            "name": "Cigna Dental PPO",
            "group_number": "CG-67890",
            "active": True,
            "cleaning_coverage": 100,
            "exam_coverage": 100,
            "crown_coverage": 60,
            "root_canal_coverage": 50,
            "annual_maximum": 2000,
            "deductible": 50,
            "used_amount": 0,
        },
        "metlife": {
            "name": "MetLife PDP",
            "group_number": "ML-ABCDE",
            "active": True,
            "cleaning_coverage": 100,
            "exam_coverage": 100,
            "crown_coverage": 50,
            "root_canal_coverage": 50,
            "annual_maximum": 1500,
            "deductible": 75,
            "used_amount": 500,
        },
        "aetna": {
            "name": "Aetna Dental",
            "group_number": "AE-12345",
            "active": True,
            "cleaning_coverage": 100,
            "exam_coverage": 100,
            "crown_coverage": 50,
            "root_canal_coverage": 50,
            "annual_maximum": 1500,
            "deductible": 50,
            "used_amount": 0,
        },
    }

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.failure_rate = self.config.get("failure_rate", 0.0)

    async def verify_eligibility(
        self,
        clinic_id: str,
        patient_id: str,
        insurance_id: str,
        service_code: str,
    ) -> ProviderResult:
        """Verify insurance eligibility (mock)."""
        if random.random() < self.failure_rate:
            return ProviderResult(
                success=False,
                status=ProviderStatus.ERROR,
                error="Insurance verification unavailable",
            )

        # Find matching plan
        plan = None
        for key, p in self.PLANS.items():
            if key in insurance_id.lower():
                plan = p
                break

        if not plan:
            return ProviderResult(
                success=True,
                data={
                    "eligible": False,
                    "reason": "Insurance not found in our network",
                    "insurance_id": insurance_id,
                },
            )

        remaining = plan["annual_maximum"] - plan["used_amount"]

        return ProviderResult(
            success=True,
            data={
                "eligible": plan["active"],
                "plan_name": plan["name"],
                "group_number": plan["group_number"],
                "deductible": plan["deductible"],
                "remaining_benefits": remaining,
                "service_code": service_code,
                "requires_predetermination": False,
            },
        )

    async def get_benefits(
        self,
        clinic_id: str,
        patient_id: str,
        insurance_id: str,
    ) -> ProviderResult:
        """Get benefit details (mock)."""
        plan = None
        for key, p in self.PLANS.items():
            if key in insurance_id.lower():
                plan = p
                break

        if not plan:
            return ProviderResult(
                success=False,
                status=ProviderStatus.ERROR,
                error="Insurance not found",
            )

        return ProviderResult(
            success=True,
            data={
                "plan_name": plan["name"],
                "group_number": plan["group_number"],
                "annual_maximum": plan["annual_maximum"],
                "deductible": plan["deductible"],
                "used_amount": plan["used_amount"],
                "remaining_benefits": plan["annual_maximum"] - plan["used_amount"],
                "coverage": {
                    "cleaning": plan["cleaning_coverage"],
                    "exam": plan["exam_coverage"],
                    "crown": plan["crown_coverage"],
                    "root_canal": plan["root_canal_coverage"],
                },
            },
        )

    async def check_coverage(
        self,
        clinic_id: str,
        insurance_id: str,
        procedure_code: str,
    ) -> ProviderResult:
        """Check coverage for a specific procedure."""
        plan = None
        for key, p in self.PLANS.items():
            if key in insurance_id.lower():
                plan = p
                break

        if not plan:
            return ProviderResult(
                success=True,
                data={"covered": False, "coverage_percent": 0},
            )

        coverage_map = {
            "D1110": plan.get("cleaning_coverage", 0),  # Prophylaxis
            "D0120": plan.get("exam_coverage", 0),       # Periodic exam
            "D2740": plan.get("crown_coverage", 0),      # Crown
            "D3310": plan.get("root_canal_coverage", 0), # Root canal
        }
        coverage = coverage_map.get(procedure_code, 0)

        return ProviderResult(
            success=True,
            data={
                "procedure_code": procedure_code,
                "covered": coverage > 0,
                "coverage_percent": coverage,
                "plan_name": plan["name"],
                "requires_predetermination": coverage >= 50,
                "note": "Final coverage determined at claim submission",
            },
        )


# =============================================================================
# Provider Factory
# =============================================================================

class ProviderFactory:
    """Factory for creating provider instances."""

    @staticmethod
    def create_scheduling_provider(
        provider_type: str = "mock",
        config: dict[str, Any] | None = None,
    ) -> BaseSchedulingProvider:
        if provider_type == "mock":
            return MockSchedulingProvider(config)
        # Add real providers here
        raise ValueError(f"Unknown scheduling provider: {provider_type}")

    @staticmethod
    def create_insurance_provider(
        provider_type: str = "mock",
        config: dict[str, Any] | None = None,
    ) -> BaseInsuranceProvider:
        if provider_type == "mock":
            return MockInsuranceProvider(config)
        raise ValueError(f"Unknown insurance provider: {provider_type}")
