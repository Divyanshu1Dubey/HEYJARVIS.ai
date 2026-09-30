"""
HeyJarvis SDK Package
=====================
Client SDK for external integrations and white-label embedding.

Provides:
  - API client for REST endpoints
  - Event publisher
  - Webhook handler utilities
  - Type definitions matching the API
"""

from __future__ import annotations

from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum

import httpx


# =============================================================================
# Types
# =============================================================================

class EventType(str, Enum):
    LEAD_CREATED = "lead.created"
    LEAD_CONTACTED = "lead.contacted"
    CONVERSATION_STARTED = "conversation.started"
    CONVERSATION_ABANDONED = "conversation.abandoned"
    APPOINTMENT_OFFERED = "appointment.offered"
    APPOINTMENT_BOOKED = "appointment.booked"
    APPOINTMENT_CANCELLED = "appointment.cancelled"
    APPOINTMENT_NO_SHOW = "appointment.no_show"
    APPOINTMENT_COMPLETED = "appointment.completed"
    TREATMENT_PLAN_CREATED = "treatment_plan.created"
    TREATMENT_PLAN_ACCEPTED = "treatment_plan.accepted"
    TREATMENT_PLAN_UNSCHEDULED = "treatment_plan.unscheduled"
    RECALL_DUE = "recall.due"
    PATIENT_INACTIVE = "patient.inactive"
    MESSAGE_SENT = "message.sent"
    MESSAGE_DELIVERED = "message.delivered"
    MESSAGE_FAILED = "message.failed"
    MESSAGE_REPLIED = "message.replied"
    PATIENT_OPTED_OUT = "patient.opted_out"
    HUMAN_HANDOFF_CREATED = "human_handoff.created"
    SAFETY_ESCALATION = "safety.escalation"
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_ATTEMPT_SENT = "campaign.attempt_sent"


@dataclass
class Event:
    """Event to publish to the HeyJarvis system."""
    event_type: EventType
    tenant_id: str
    patient_id: Optional[str] = None
    conversation_id: Optional[str] = None
    appointment_id: Optional[str] = None
    payload: dict[str, Any] = None
    idempotency_key: Optional[str] = None

    def __post_init__(self):
        if self.payload is None:
            self.payload = {}


@dataclass
class Patient:
    """Patient data for SDK usage."""
    id: str
    tenant_id: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[str] = None


# =============================================================================
# SDK Client
# =============================================================================

class HeyJarvisClient:
    """
    Client for integrating with HeyJarvis.

    Usage:
        client = HeyJarvisClient(
            api_key="your-api-key",
            base_url="http://localhost:8000",
        )

        # Publish an event
        await client.publish_event(Event(
            event_type=EventType.LEAD_CREATED,
            tenant_id="tenant-id",
            patient_id="patient-id",
            payload={"source": "website_form"},
        ))

        # Send a message
        await client.send_message(
            patient_id="patient-id",
            channel="sms",
            body="Hello!",
        )
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def publish_event(self, event: Event) -> dict[str, Any]:
        """Publish an event to HeyJarvis."""
        response = await self._client.post(
            "/api/v1/events",
            json={
                "event_type": event.event_type.value,
                "tenant_id": event.tenant_id,
                "patient_id": event.patient_id,
                "conversation_id": event.conversation_id,
                "appointment_id": event.appointment_id,
                "payload": event.payload,
                "idempotency_key": event.idempotency_key,
            },
        )
        response.raise_for_status()
        return response.json()

    async def send_message(
        self,
        patient_id: str,
        channel: str,
        body: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Send a message to a patient."""
        response = await self._client.post(
            "/api/v1/messages",
            json={
                "patient_id": patient_id,
                "channel": channel,
                "body": body,
                "conversation_id": conversation_id,
            },
        )
        response.raise_for_status()
        return response.json()

    async def get_patient(self, patient_id: str) -> dict[str, Any]:
        """Get patient details."""
        response = await self._client.get(f"/api/v1/patients/{patient_id}")
        response.raise_for_status()
        return response.json()

    async def create_opportunity(
        self,
        patient_id: str,
        recapture_type: str,
        reason: str,
    ) -> dict[str, Any]:
        """Create a recapture opportunity."""
        response = await self._client.post(
            "/api/v1/recapture/opportunities",
            json={
                "patient_id": patient_id,
                "recapture_type": recapture_type,
                "reason": reason,
            },
        )
        response.raise_for_status()
        return response.json()

    async def get_opportunities(
        self,
        tenant_id: str,
        status: str = "pending",
        limit: int = 25,
    ) -> dict[str, Any]:
        """Get recapture opportunities."""
        response = await self._client.get(
            "/api/v1/recapture/opportunities",
            params={"tenant_id": tenant_id, "status": status, "limit": limit},
        )
        response.raise_for_status()
        return response.json()

    async def get_analytics(self, tenant_id: str, date_from: str, date_to: str) -> dict[str, Any]:
        """Get analytics for a date range."""
        response = await self._client.get(
            "/api/v1/analytics/summary",
            params={
                "tenant_id": tenant_id,
                "date_from": date_from,
                "date_to": date_to,
            },
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "HeyJarvisClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
