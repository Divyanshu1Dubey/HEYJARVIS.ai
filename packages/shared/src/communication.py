"""
HeyJarvis Communication Package
================================
Mock communication providers for development and demo.
No paid services required. Swap in real providers (Twilio, Postmark, etc.)
by changing the provider config — the interface stays the same.
"""

from __future__ import annotations

import uuid
import random
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from enum import Enum

from shared.models import ChannelType, MessageDirection

logger = logging.getLogger(__name__)


# =============================================================================
# Data Types
# =============================================================================

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


@dataclass
class MessageResult:
    """Result of a message send attempt."""
    success: bool
    external_id: Optional[str] = None
    status: DeliveryStatus = DeliveryStatus.PENDING
    error: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "external_id": self.external_id,
            "status": self.status.value,
            "error": self.error,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "metadata": self.metadata,
        }


# =============================================================================
# Base Provider
# =============================================================================

class BaseCommunicationProvider:
    """Base class for all communication providers."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.mock_mode = self.config.get("mock_mode", True)

    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        raise NotImplementedError

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        raise NotImplementedError

    async def send_voice(
        self,
        to: str,
        message: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        raise NotImplementedError

    async def send_whatsapp(
        self,
        to: str,
        body: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        raise NotImplementedError

    async def check_delivery_status(self, external_id: str) -> DeliveryStatus:
        raise NotImplementedError


# =============================================================================
# Mock Provider (Default — No Paid Services Needed)
# =============================================================================

class MockCommunicationProvider(BaseCommunicationProvider):
    """
    Mock provider that simulates message delivery without any external API calls.
    Perfect for development, demos, and testing.

    Simulates:
    - SMS delivery with realistic timing
    - Occasional failures (configurable)
    - Delivery receipts
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.failure_rate = self.config.get("failure_rate", 0.0)
        self.delivery_delay_seconds = self.config.get("delivery_delay", 1)

    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        """Simulate sending an SMS."""
        external_id = f"mock_sms_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        logger.info(f"[MOCK SMS] To: {to} | Body: {body[:50]}...")

        # Simulate occasional failure
        if random.random() < self.failure_rate:
            return MessageResult(
                success=False,
                external_id=external_id,
                status=DeliveryStatus.FAILED,
                error="Mock delivery failure",
                sent_at=now,
            )

        return MessageResult(
            success=True,
            external_id=external_id,
            status=DeliveryStatus.SENT,
            sent_at=now,
            metadata={"mock": True, "to": to, "from": from_number},
        )

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        """Simulate sending an email."""
        external_id = f"mock_email_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        logger.info(f"[MOCK EMAIL] To: {to} | Subject: {subject}")

        if random.random() < self.failure_rate:
            return MessageResult(
                success=False,
                external_id=external_id,
                status=DeliveryStatus.FAILED,
                error="Mock delivery failure",
                sent_at=now,
            )

        return MessageResult(
            success=True,
            external_id=external_id,
            status=DeliveryStatus.SENT,
            sent_at=now,
            metadata={"mock": True, "to": to, "from": from_email},
        )

    async def send_voice(
        self,
        to: str,
        message: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        """Simulate placing a voice call."""
        external_id = f"mock_voice_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        logger.info(f"[MOCK VOICE] To: {to} | Message: {message[:50]}...")

        return MessageResult(
            success=True,
            external_id=external_id,
            status=DeliveryStatus.SENT,
            sent_at=now,
            metadata={"mock": True, "call_duration": random.randint(30, 120)},
        )

    async def send_whatsapp(
        self,
        to: str,
        body: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        """Simulate sending a WhatsApp message."""
        external_id = f"mock_wa_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        logger.info(f"[MOCK WHATSAPP] To: {to} | Body: {body[:50]}...")

        return MessageResult(
            success=True,
            external_id=external_id,
            status=DeliveryStatus.SENT,
            sent_at=now,
            metadata={"mock": True, "to": to},
        )

    async def check_delivery_status(self, external_id: str) -> DeliveryStatus:
        """Simulate checking delivery status."""
        if "failed" in external_id:
            return DeliveryStatus.FAILED
        return DeliveryStatus.DELIVERED


# =============================================================================
# Twilio Provider (Stub — Swap In When Ready)
# =============================================================================

class TwilioCommunicationProvider(BaseCommunicationProvider):
    """
    Real Twilio provider. Configure with real credentials to activate.

    pip install twilio
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.mock_mode = True  # Default to mock until configured

        if not self.mock_mode and config:
            try:
                from twilio.rest import Client
                self.client = Client(
                    config.get("account_sid"),
                    config.get("auth_token"),
                )
                self.from_number = config.get("from_number")
                self.mock_mode = False
            except ImportError:
                logger.warning("twilio package not installed, falling back to mock mode")
                self.mock_mode = True

    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        if self.mock_mode:
            return await MockCommunicationProvider().send_sms(to, body, from_number, metadata)

        try:
            message = self.client.messages.create(
                to=to,
                from_=from_number or self.from_number,
                body=body,
            )
            return MessageResult(
                success=True,
                external_id=message.sid,
                status=DeliveryStatus.SENT,
                sent_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Twilio SMS error: {e}")
            return MessageResult(
                success=False,
                error=str(e),
                status=DeliveryStatus.FAILED,
            )

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        if self.mock_mode:
            return await MockCommunicationProvider().send_email(to, subject, body, from_email, metadata)
        # Implement with Postmark/SendGrid
        return MessageResult(success=False, error="Email provider not configured")

    async def send_voice(
        self,
        to: str,
        message: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        if self.mock_mode:
            return await MockCommunicationProvider().send_voice(to, message, from_number, metadata)
        return MessageResult(success=False, error="Voice provider not configured")

    async def send_whatsapp(
        self,
        to: str,
        body: str,
        from_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResult:
        if self.mock_mode:
            return await MockCommunicationProvider().send_whatsapp(to, body, from_number, metadata)
        return MessageResult(success=False, error="WhatsApp provider not configured")

    async def check_delivery_status(self, external_id: str) -> DeliveryStatus:
        if self.mock_mode:
            return await MockCommunicationProvider().check_delivery_status(external_id)
        return DeliveryStatus.SENT


# =============================================================================
# Provider Factory
# =============================================================================

def get_communication_provider(channel: ChannelType, config: dict[str, Any] | None = None) -> BaseCommunicationProvider:
    """
    Factory function to get the appropriate communication provider.

    For now, returns Mock provider for all channels.
    Swap in real providers when credentials are available.
    """
    if config is None:
        config = {}

    # In production, select based on channel and tenant config
    # For now, always return mock
    return MockCommunicationProvider(config)
