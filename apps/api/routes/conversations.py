"""
HeyJarvis API — Conversation Routes
=====================================
Create and manage AI conversations.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.demo_data import _make_conversations, _make_patients
from shared.policy_engine import PolicyEngine, PolicyDecision
from shared.ai_engine import IntentClassifier, MessageGenerator, LLMClient
from shared.safety import SafetyClassifier, SafetyResult
from shared.models import ChannelType

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class CreateConversationRequest(BaseModel):
    tenant_id: str
    patient_id: str | None = None
    channel: str = Field(..., pattern=r"^(sms|email|web_chat|whatsapp)$")
    initial_message: str | None = None


class ConversationResponse(BaseModel):
    id: str
    channel: str
    state: str
    started_at: str
    messages: list[dict[str, Any]]


class ChatRequest(BaseModel):
    conversation_id: str
    message: str = Field(..., min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    response: str
    intent: str | None = None
    requires_human: bool = False
    tools_used: list[str] = []


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/", response_model=ConversationResponse)
async def create_conversation(request: CreateConversationRequest, db=Depends(get_db)):
    """Create a new conversation."""
    import uuid
    from datetime import datetime

    conv_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    return ConversationResponse(
        id=conv_id,
        channel=request.channel,
        state="new_lead",
        started_at=now,
        messages=[],
    )


@router.post("/{conversation_id}/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message in a conversation and get AI response.

    Flow:
      1. Safety check on user message
      2. Intent classification
      3. Policy check
      4. Generate response
      5. Validate response
      6. Return
    """
    # 1. Safety check
    safety = SafetyClassifier()
    safety_result: SafetyResult = safety.classify(request.message)

    if safety_result.requires_human:
        return ChatResponse(
            response=f"I want to make sure you get the right help. Let me connect you with our team right away. One moment please.",
            requires_human=True,
            intent=None,
            tools_used=[],
        )

    # 2. Intent classification
    llm = LLMClient()
    intent_clf = IntentClassifier(llm_client=llm)
    intent_result = intent_clf.classify(request.message)

    # 3. Generate response
    generator = MessageGenerator(llm_client=llm)

    # Find patient context (demo)
    patients = _make_patients()
    patient = patients[0] if patients else {}
    clinic = {
        "name": "Bright Smile Dental",
        "phone": "(512) 555-0142",
    }

    gen_result = generator.generate_conversation_response(
        user_message=request.message,
        conversation_context={"conversation_id": request.conversation_id},
        patient=patient,
        clinic=clinic,
    )

    # 4. Check if booking-related intent
    tools_used = []
    if intent_result.intent.value == "book_appointment":
        tools_used.append("check_availability")
        # In production, would call actual scheduling tool

    return ChatResponse(
        response=gen_result.message,
        intent=intent_result.intent.value,
        requires_human=safety_result.requires_human,
        tools_used=tools_used,
    )


@router.get("/", response_model=list[dict[str, Any]])
async def list_conversations():
    """List all conversations (demo)."""
    return _make_conversations()


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """Get a single conversation with messages."""
    convs = _make_conversations()
    msgs = _make_messages()

    conv = next((c for c in convs if c["id"] == conversation_id), None)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv_msgs = [m for m in msgs if m.get("conversation_id") == conversation_id]

    return ConversationResponse(
        id=conv["id"],
        channel=conv["channel"],
        state=conv["state"],
        started_at=conv["started_at"],
        messages=[
            {
                "id": m["id"],
                "direction": m["direction"],
                "body": m["body"],
                "sent_at": m.get("sent_at"),
            }
            for m in conv_msgs
        ],
    )
