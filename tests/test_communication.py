"""
Tests for communication providers.
"""

from __future__ import annotations

import pytest
from packages.shared.communication import MockCommunicationProvider, MessageResult, DeliveryStatus
from shared.models import ChannelType


class TestMockCommunicationProvider:
    """Test the mock communication provider."""

    @pytest.fixture
    def provider(self):
        return MockCommunicationProvider({"failure_rate": 0.0})

    @pytest.mark.asyncio
    async def test_send_sms_success(self, provider):
        result = await provider.send_sms(
            to="+1-512-555-0142",
            body="Hello from HeyJarvis!",
        )
        assert result.success is True
        assert result.external_id is not None
        assert result.status == DeliveryStatus.SENT

    @pytest.mark.asyncio
    async def test_send_email_success(self, provider):
        result = await provider.send_email(
            to="test@example.com",
            subject="Test",
            body="Hello",
        )
        assert result.success is True
        assert result.external_id is not None

    @pytest.mark.asyncio
    async def test_send_voice_success(self, provider):
        result = await provider.send_voice(
            to="+1-512-555-0142",
            message="Hello",
        )
        assert result.success is True

    @pytest.mark.asyncio
    async def test_delivery_status(self, provider):
        status = await provider.check_delivery_status("mock_sms_abc123")
        assert status == DeliveryStatus.DELIVERED

    @pytest.mark.asyncio
    async def test_failed_delivery_status(self, provider):
        status = await provider.check_delivery_status("mock_sms_failed_abc123")
        assert status == DeliveryStatus.FAILED
