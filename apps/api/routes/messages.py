"""
HeyJarvis API — Message Routes
================================
Send and receive messages, get conversation history.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.demo_data import _make_conversations, _make_messages
from shared.communication import get_communication_provider, MessageResult
from shared.policy_engine import PolicyEngine, PolicyDecision
from shared.models import ChannelType

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class SendMessageRequest(BaseModel):
    tenant_id: str
    patient_id: str
    channel: str = Field(..., pattern=r"^(sms|email|voice|web_chat|whatsapp)$")
    body: str = Field(..., min_length=1, max_length=5000)
    conversation_id: str | None = None


class SendMessageResponse(BaseModel):
    success: bool
    external_id: str | None = None
    status: str
    error: str | None = None


class MessageResponse(BaseModel):
    id: str
    direction: str
    channel: str
    body: str
    sent_at: str | None = None


class ConversationMessagesResponse(BaseModel):
    conversation_id: str
    messages: list[MessageResponse]


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, db=Depends(get_db)):
    """
    Send a message to a patient.

    Flow:
      1. Check policy (consent, opt-out, frequency caps, quiet hours)
      2. Validate message content
      3. Send via communication provider
      4. Record in database
      5. Emit event
    """
    # 1. Policy check
    policy = PolicyEngine(db_session=db)
    channel = ChannelType(request.channel)

    result = policy.evaluate_outreach(
        tenant_id=request.tenant_id,
        patient_id=request.patient_id,
        channel=channel,
        message=request.body,
    )

    if result.decision == PolicyDecision.DENY:
        return SendMessageResponse(
            success=False,
            status="denied",
            error=result.reason,
        )

    if result.decision == PolicyDecision.REQUIRE_ESCALATION:
        return SendMessageResponse(
            success=False,
            status="escalation_required",
            error=result.escalation_reason or result.reason,
        )

    # 2. Send via provider
    provider = get_communication_provider(channel)
    send_result: MessageResult = await provider.send_sms(
        to="+1-512-555-0142",  # In production: get from patient record
        body=request.body,
    )

    # 3. Record in database (in production)
    # In demo mode, just return the result
    return SendMessageResponse(
        success=send_result.success,
        external_id=send_result.external_id,
        status=send_result.status.value,
        error=send_result.error,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationMessagesResponse)
async def get_conversation_messages(conversation_id: str):
    """Get all messages in a conversation."""
    all_messages = _make_messages()
    all_conversations = _make_conversations()

    # Verify conversation exists
    conv = next((c for c in all_conversations if c["id"] == conversation_id), None)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Filter messages
    conv_messages = [
        m for m in all_messages
        if m.get("conversation_id") == conversation_id
    ]

    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        messages=[
            MessageResponse(
                id=m["id"],
                direction=m["direction"],
                channel=m["channel"],
                body=m["body"],
                sent_at=m.get("sent_at", ""),
            )
            for m in conv_messages
        ],
    )


@router.post("/inbound")
async def receive_inbound_message(
    channel: str,
    from_number: str,
    body: str,
    tenant_id: str | None = None,
):
    """
    Webhook endpoint for receiving inbound messages.

    This is called by:
      - Twilio webhook (SMS)
      - Email provider webhook
      - Chat widget
      - WhatsApp webhook
    """
    logger.info(f"Inbound message: channel={channel}, from={from_number}, body={body[:100]}")

    # In production:
    # 1. Identify patient by phone/email
    # 2. Create or find conversation
    # 3. Store message
    # 4. Emit event
    # 5. Trigger AI processing

    return {"status": "received", "channel": channel}
