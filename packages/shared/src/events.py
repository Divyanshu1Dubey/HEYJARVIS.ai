"""
HeyJarvis Event Bus
===================
Internal event publishing and consumption.

Uses Redis pub/sub for simple cases.
Can be upgraded to Kafka for high-volume production.

Event flow:
  Producer → Event Bus → Consumer(s)
"""

from __future__ import annotations

import json
import uuid
import logging
from datetime import datetime
from typing import Any, Callable, Optional
from dataclasses import dataclass, field

from shared.models import Event, EventType
from shared.constants import REDIS_KEY_PREFIX

logger = logging.getLogger(__name__)


# =============================================================================
# Event
# =============================================================================

@dataclass
class HJEvent:
    """Internal event representation."""
    event_type: str
    tenant_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    patient_id: Optional[str] = None
    conversation_id: Optional[str] = None
    appointment_id: Optional[str] = None
    campaign_id: Optional[str] = None
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    idempotency_key: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "system"
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "tenant_id": self.tenant_id,
            "patient_id": self.patient_id,
            "conversation_id": self.conversation_id,
            "appointment_id": self.appointment_id,
            "campaign_id": self.campaign_id,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "payload": self.payload,
            "version": self.version,
        }


# =============================================================================
# Event Bus
# =============================================================================

class EventBus:
    """
    Internal event bus for decoupled communication between components.

    Uses Redis pub/sub for simple async messaging.
    Supports:
      - Publishing events
      - Subscribing to event types
      - Idempotency checking
      - Dead letter handling
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._subscribers: dict[str, list[Callable]] = {}
        self._idempotency_cache: set[str] = set()
        self._mock_mode = redis_client is None

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed to event: {event_type}")

    async def publish(self, event: HJEvent) -> bool:
        """
        Publish an event to the bus.

        Returns True if published, False if duplicate detected.
        """
        # Check idempotency
        idem_key = f"{REDIS_KEY_PREFIX}event:{event.idempotency_key}"
        if self.redis:
            exists = await self.redis.exists(idem_key)
            if exists:
                logger.warning(f"Duplicate event detected: {event.idempotency_key}")
                return False
            await self.redis.setex(idem_key, 86400, "1")  # 24h TTL

        # In mock mode, just log
        if self._mock_mode:
            logger.info(f"[EVENT BUS] {event.event_type} | tenant={event.tenant_id}")
            await self._dispatch(event)
            return True

        # Publish to Redis
        channel = f"{REDIS_KEY_PREFIX}events:{event.event_type}"
        await self.redis.publish(channel, json.dumps(event.to_dict()))

        await self._dispatch(event)
        return True

    async def _dispatch(self, event: HJEvent) -> None:
        """Dispatch event to subscribers."""
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Event handler error for {event.event_type}: {e}")


# =============================================================================
# Event Definitions
# =============================================================================

class EventDefinitions:
    """Central registry of all event types, producers, and consumers."""

    EVENTS = {
        EventType.LEAD_CREATED: {
            "producer": "api",
            "consumers": ["recapture-engine", "campaign-engine"],
            "description": "A new lead has been created (form, call, chat)",
        },
        EventType.LEAD_CONTACTED: {
            "producer": "worker",
            "consumers": ["analytics", "campaign-engine"],
            "description": "A lead has been contacted",
        },
        EventType.CONVERSATION_STARTED: {
            "producer": "api",
            "consumers": ["ai-engine", "analytics"],
            "description": "A new conversation has started",
        },
        EventType.CONVERSATION_ABANDONED: {
            "producer": "ai-engine",
            "consumers": ["recapture-engine", "analytics"],
            "description": "A conversation was abandoned",
        },
        EventType.APPOINTMENT_OFFERED: {
            "producer": "ai-engine",
            "consumers": ["analytics", "campaign-engine"],
            "description": "An appointment was offered to a patient",
        },
        EventType.APPOINTMENT_BOOKED: {
            "producer": "integrations",
            "consumers": ["analytics", "campaign-engine", "recapture-engine"],
            "description": "An appointment was successfully booked",
        },
        EventType.APPOINTMENT_CANCELLED: {
            "producer": "integrations",
            "consumers": ["recapture-engine", "analytics", "campaign-engine"],
            "description": "An appointment was cancelled",
        },
        EventType.APPOINTMENT_NO_SHOW: {
            "producer": "integrations",
            "consumers": ["recapture-engine", "analytics"],
            "description": "A patient did not show for appointment",
        },
        EventType.APPOINTMENT_COMPLETED: {
            "producer": "integrations",
            "consumers": ["analytics", "recapture-engine"],
            "description": "An appointment was completed",
        },
        EventType.TREATMENT_PLAN_CREATED: {
            "producer": "integrations",
            "consumers": ["recapture-engine"],
            "description": "A treatment plan was created",
        },
        EventType.TREATMENT_PLAN_ACCEPTED: {
            "producer": "integrations",
            "consumers": ["recapture-engine"],
            "description": "Patient accepted treatment plan",
        },
        EventType.TREATMENT_PLAN_UNSCHEDULED: {
            "producer": "recapture-engine",
            "consumers": ["campaign-engine"],
            "description": "Treatment plan not scheduled within timeframe",
        },
        EventType.RECALL_DUE: {
            "producer": "scheduler",
            "consumers": ["recapture-engine", "campaign-engine"],
            "description": "Patient is due for recall",
        },
        EventType.PATIENT_INACTIVE: {
            "producer": "scheduler",
            "consumers": ["recapture-engine", "campaign-engine"],
            "description": "Patient has become inactive",
        },
        EventType.MESSAGE_SENT: {
            "producer": "worker",
            "consumers": ["analytics"],
            "description": "A message was sent to a patient",
        },
        EventType.MESSAGE_DELIVERED: {
            "producer": "worker",
            "consumers": ["analytics"],
            "description": "A message was confirmed delivered",
        },
        EventType.MESSAGE_FAILED: {
            "producer": "worker",
            "consumers": ["analytics", "campaign-engine"],
            "description": "A message failed to deliver",
        },
        EventType.MESSAGE_REPLIED: {
            "producer": "api",
            "consumers": ["ai-engine", "campaign-engine", "analytics"],
            "description": "Patient replied to a message",
        },
        EventType.PATIENT_OPTED_OUT: {
            "producer": "worker",
            "consumers": ["campaign-engine", "recapture-engine"],
            "description": "Patient opted out of communications",
        },
        EventType.HUMAN_HANDOFF_CREATED: {
            "producer": "ai-engine",
            "consumers": ["notifications", "analytics"],
            "description": "A conversation was handed off to human staff",
        },
        EventType.SAFETY_ESCALATION: {
            "producer": "ai-engine",
            "consumers": ["notifications", "analytics"],
            "description": "A safety escalation was triggered",
        },
        EventType.CAMPAIGN_STARTED: {
            "producer": "scheduler",
            "consumers": ["analytics"],
            "description": "A campaign was started",
        },
        EventType.CAMPAIGN_ATTEMPT_SENT: {
            "producer": "worker",
            "consumers": ["analytics", "campaign-engine"],
            "description": "A campaign attempt was sent",
        },
    }

    @classmethod
    def get_event_info(cls, event_type: EventType) -> dict[str, Any]:
        """Get metadata for an event type."""
        return cls.EVENTS.get(event_type, {})

    @classmethod
    def get_consumers(cls, event_type: EventType) -> list[str]:
        """Get consumer services for an event type."""
        info = cls.EVENTS.get(event_type, {})
        return info.get("consumers", [])
