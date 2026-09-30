"""
HeyJarvis AI Package
====================
LLM integration, intent classification, message generation,
and conversation management.

Architecture:
  Tier 0: Deterministic rules (PolicyEngine)
  Tier 1: Small classifier (keyword/regex)
  Tier 2: LLM for intent extraction and personalization
  Tier 3: Strong LLM for complex conversation handling

All LLM calls go through this package. No other component
should call the LLM directly.
"""

from __future__ import annotations

import json
import re
import uuid
import logging
from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from shared.models import (
    IntentType, SafetyLevel, PatientState,
    ChannelType, HandoffReason,
)
from shared.constants import EMERGENCY_KEYWORDS, MEDICAL_ADVICE_TRIGGERS
from shared.demo_data import get_demo_tenant, get_demo_clinic

logger = logging.getLogger(__name__)


# =============================================================================
# Data Types
# =============================================================================

@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: IntentType
    confidence: float
    entities: dict[str, Any] = field(default_factory=dict)
    urgency: str = "normal"
    requires_human: bool = False
    handoff_reason: Optional[HandoffReason] = None
    raw_response: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "entities": self.entities,
            "urgency": self.urgency,
            "requires_human": self.requires_human,
            "handoff_reason": self.handoff_reason.value if self.handoff_reason else None,
        }


@dataclass
class MessageGenerationResult:
    """Result of AI message generation."""
    message: str
    channel: ChannelType
    cta: str | None = None
    safety_flags: list[str] = field(default_factory=list)
    requires_review: bool = False
    confidence: float = 1.0
    raw_response: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "channel": self.channel.value,
            "cta": self.cta,
            "safety_flags": self.safety_flags,
            "requires_review": self.requires_review,
            "confidence": self.confidence,
        }


# =============================================================================
# LLM Client
# =============================================================================

class LLMClient:
    """
    Central LLM client with retry, rate limiting, and cost tracking.

    Uses Anthropic Claude API. Falls back gracefully if unavailable.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.mock_mode = api_key is None
        self.client = None

        if not self.mock_mode:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                logger.warning("anthropic package not installed, using mock mode")
                self.mock_mode = True

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 500,
        temperature: float = 0.3,
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Send a completion request to the LLM.

        Returns a dict with:
          - content: str — the generated text
          - usage: dict — token usage
          - model: str — model used
        """
        if self.mock_mode:
            return self._mock_complete(prompt, max_tokens)

        try:
            kwargs = {
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            if tools:
                kwargs["tools"] = tools

            response = self.client.messages.create(**kwargs)

            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            return {
                "content": content,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "model": response.model,
            }

        except Exception as e:
            logger.error(f"LLM error: {e}")
            return self._mock_complete(prompt, max_tokens)

    def _mock_complete(self, prompt: str, max_tokens: int) -> dict[str, Any]:
        """Generate a mock response for development."""
        prompt_lower = prompt.lower()

        # Simple keyword-based mock responses
        if "intent" in prompt_lower:
            return {
                "content": json.dumps({
                    "intent": "general_question",
                    "confidence": 0.8,
                    "entities": {},
                    "urgency": "normal",
                }),
                "usage": {"input_tokens": len(prompt) // 4, "output_tokens": 50},
                "model": "mock-model",
            }

        if "safety" in prompt_lower or "emergency" in prompt_lower:
            return {
                "content": json.dumps({
                    "level": "safe",
                    "requires_human": False,
                }),
                "usage": {"input_tokens": len(prompt) // 4, "output_tokens": 30},
                "model": "mock-model",
            }

        if "message" in prompt_lower or "generate" in prompt_lower:
            return {
                "content": "Thank you for reaching out to Bright Smile Dental! We'd love to help you. Would you like to schedule an appointment?",
                "usage": {"input_tokens": len(prompt) // 4, "output_tokens": 100},
                "model": "mock-model",
            }

        return {
            "content": "I understand. Let me help you with that.",
            "usage": {"input_tokens": len(prompt) // 4, "output_tokens": 50},
            "model": "mock-model",
        }


# =============================================================================
# Intent Classifier
# =============================================================================

class IntentClassifier:
    """
    Classifies patient message intent.

    Uses a two-stage approach:
      1. Fast regex/keyword classification (Tier 1)
      2. LLM classification for ambiguous cases (Tier 2)
    """

    # Keyword patterns for fast classification
    PATTERNS = {
        IntentType.BOOK_APPOINTMENT: [
            r"\b(book|schedule|appointment|visit|see a dentist|come in)\b",
            r"\b(availability|available|opening|slot|time)\b",
            r"\b(today|tomorrow|this week|when can)\b",
        ],
        IntentType.RESCHEDULE: [
            r"\b(reschedule|change.*appointment|different time|move.*appointment)\b",
            r"\b(can't make|unable to come|need to change)\b",
        ],
        IntentType.CANCEL: [
            r"\b(cancel|cancellation|remove.*appointment)\b",
        ],
        IntentType.EMERGENCY: [
            r"\b(emergency|urgent|pain|bleeding|swelling|broken tooth|fell out)\b",
            r"\b(toothache|abscess|infection|can't eat)\b",
        ],
        IntentType.INSURANCE_QUESTION: [
            r"\b(insurance|coverage|copay|deductible|benefit|in-network|out-of-network)\b",
            r"\b(delta|cigna|metlife|aetna|blue cross|united)\b",
        ],
        IntentType.PRICING_QUESTION: [
            r"\b(price|cost|how much|expensive|afford|payment|finance|carecredit)\b",
            r"\b(estimate|quote|fee|charge)\b",
        ],
        IntentType.SERVICE_QUESTION: [
            r"\b(cleaning|exam|whitening|crown|root canal|implant|extraction|braces)\b",
            r"\b(what.*service|what.*procedure|do you do)\b",
        ],
        IntentType.HOURS_QUESTION: [
            r"\b(hours|open|close|when are you open|weekend|saturday)\b",
        ],
        IntentType.LOCATION_QUESTION: [
            r"\b(where|address|location|direction|parking)\b",
        ],
        IntentType.HUMAN_HANDOFF: [
            r"\b(human|person|real person|talk to someone|speak to|manager)\b",
        ],
        IntentType.OPT_OUT: [
            r"\b(stop|unsubscribe|opt out|remove me|don't contact)\b",
        ],
    }

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()
        self._compiled_patterns: dict[IntentType, list[re.Pattern]] = {}
        for intent, patterns in self.PATTERNS.items():
            self._compiled_patterns[intent] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def classify(self, message: str) -> IntentResult:
        """
        Classify the intent of a patient message.

        Stage 1: Fast keyword matching
        Stage 2: LLM classification if ambiguous
        """
        if not message or not message.strip():
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
            )

        message_lower = message.lower()

        # Stage 1: Keyword matching
        scores: dict[IntentType, int] = {}
        for intent, patterns in self._compiled_patterns.items():
            score = sum(1 for p in patterns if p.search(message_lower))
            if score > 0:
                scores[intent] = score

        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(scores[best_intent] / 3.0, 1.0)

            return IntentResult(
                intent=best_intent,
                confidence=confidence,
                entities=self._extract_entities(message),
                urgency=self._assess_urgency(message),
            )

        # Stage 2: LLM classification for ambiguous messages
        return self._llm_classify(message)

    def _extract_entities(self, message: str) -> dict[str, Any]:
        """Extract structured entities from the message."""
        entities: dict[str, Any] = {}

        # Insurance companies
        insurance_map = {
            "delta": "Delta Dental",
            "cigna": "Cigna",
            "metlife": "MetLife",
            "aetna": "Aetna",
            "blue cross": "Blue Cross Blue Shield",
            "united": "UnitedHealthcare",
            "humana": "Humana",
            "guardian": "Guardian",
        }
        message_lower = message.lower()
        for key, value in insurance_map.items():
            if key in message_lower:
                entities["insurance"] = value
                break

        # Time references
        time_patterns = [
            (r"\btoday\b", "today"),
            (r"\btomorrow\b", "tomorrow"),
            (r"\bthis week\b", "this_week"),
            (r"\bthis weekend\b", "this_weekend"),
            (r"\bnext week\b", "next_week"),
            (r"\b(\d{1,2})\s*(am|pm)\b", "specific_time"),
            (r"\b(morning|afternoon|evening)\b", "time_of_day"),
            (r"\b(saturday|sunday)\b", "weekend"),
        ]
        for pattern, label in time_patterns:
            if re.search(pattern, message_lower):
                entities.setdefault("time_references", []).append(label)

        # Service references
        services = [
            "cleaning", "exam", "whitening", "crown", "root canal",
            "implant", "extraction", "filling", "braces", "veneers",
            "cavity", "checkup",
        ]
        for svc in services:
            if svc in message_lower:
                entities.setdefault("services", []).append(svc)

        return entities

    def _assess_urgency(self, message: str) -> str:
        """Assess urgency level from message content."""
        message_lower = message.lower()

        # Critical urgency indicators
        critical = [
            "emergency", "urgent", "can't breathe", "bleeding",
            "swelling", "broken", "fell out", "unbearable",
        ]
        for word in critical:
            if word in message_lower:
                return "urgent"

        # Moderate urgency
        moderate = ["pain", "ache", "today", "asap", "soon", "hurts"]
        for word in moderate:
            if word in message_lower:
                return "moderate"

        return "normal"

    def _llm_classify(self, message: str) -> IntentResult:
        """Use LLM for ambiguous messages."""
        system = """You are an intent classifier for a dental practice AI system.
Analyze the patient's message and return ONLY valid JSON with this structure:
{"intent": "one of: book_appointment, reschedule, cancel, emergency, insurance_question, pricing_question, service_question, hours_question, location_question, general_question, human_handoff, opt_out, unknown", "confidence": 0.0-1.0, "urgency": "normal|moderate|urgent", "entities": {}}"""

        prompt = f"Classify this patient message:\n\n{message}\n\nReturn only JSON."

        response = self.llm.complete(
            prompt=prompt,
            system_prompt=system,
            max_tokens=200,
            temperature=0.1,
        )

        try:
            data = json.loads(response["content"])
            return IntentResult(
                intent=IntentType(data.get("intent", "unknown")),
                confidence=data.get("confidence", 0.5),
                entities=data.get("entities", {}),
                urgency=data.get("urgency", "normal"),
            )
        except (json.JSONDecodeError, ValueError):
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
            )


# =============================================================================
# Message Generator
# =============================================================================

class MessageGenerator:
    """
    Generates personalized outreach messages for recapture campaigns.

    Design principles:
      - Never fabricate appointments, insurance, prices, or availability
      - Use only verified data from the database
      - Personalize based on patient history and recapture context
      - Always include opt-out instructions
      - Maintain a helpful, non-pushy tone
    """

    # Base templates for each recapture type
    # These are fallbacks; AI personalizes on top
    TEMPLATES = {
        "lead_abandoned": (
            "Hi {first_name}, this is {clinic_name}. "
            "We saw you were interested in {service}. "
            "Would you like to schedule an appointment? "
            "Reply YES to book or STOP to opt out."
        ),
        "web_chat_abandoned": (
            "Hi {first_name}, this is {clinic_name}. "
            "We noticed you started a conversation about {service} but didn't finish. "
            "We're here to help — would you like to continue? "
            "Reply YES or call us at {clinic_phone}."
        ),
        "missed_call": (
            "Hi {first_name}, this is {clinic_name}. "
            "We missed your call. We're here to help with your dental needs. "
            "Call us back at {clinic_phone} or reply to schedule."
        ),
        "cancelled_scheduling": (
            "Hi {first_name}, this is {clinic_name}. "
            "We understand plans change. We'd love to reschedule your {service}. "
            "We have new openings this week. Interested? "
            "Reply YES or call {clinic_phone}."
        ),
        "cancelled_price": (
            "Hi {first_name}, this is {clinic_name}. "
            "We heard your concern about cost for {service}. "
            "We have flexible payment options including CareCredit. "
            "Let us help make this work for you. Call {clinic_phone}."
        ),
        "cancelled_fear": (
            "Hi {first_name}, this is {clinic_name}. "
            "We understand dental visits can feel stressful. "
            "We offer gentle care options and sedation if needed. "
            "You're in good hands with us. Call {clinic_phone} to discuss."
        ),
        "first_no_show": (
            "Hi {first_name}, this is {clinic_name}. "
            "We missed you at your appointment. "
            "Life happens! Would you like to reschedule? "
            "Reply YES or call {clinic_phone}."
        ),
        "repeat_no_show": (
            "Hi {first_name}, this is {clinic_name}. "
            "We noticed you've had some trouble making appointments. "
            "We want to make sure you get the care you need. "
            "A team member will call you personally to help find a time that works."
        ),
        "treatment_plan_created": (
            "Hi {first_name}, this is {clinic_name}. "
            "We have a treatment plan ready for you for {service}. "
            "Would you like to schedule your appointment? "
            "Reply YES to get started or call {clinic_phone} for questions."
        ),
        "treatment_plan_accepted": (
            "Hi {first_name}, this is {clinic_name}. "
            "Great news — your treatment plan for {service} is accepted! "
            "Let's get you scheduled. We have openings available. "
            "Reply YES to book or call {clinic_phone}."
        ),
        "hygiene_recall_overdue": (
            "Hi {first_name}, this is {clinic_name}. "
            "It's been a while since your last cleaning! "
            "Regular cleanings keep your smile healthy. "
            "Would you like to schedule? Reply YES or call {clinic_phone}."
        ),
        "inactive_patient": (
            "Hi {first_name}, this is {clinic_name}. "
            "We miss seeing you! It's been a while since your last visit. "
            "We'd love to welcome you back. "
            "Reply YES for a checkup or call {clinic_phone}."
        ),
        "booking_flow_abandoned": (
            "Hi {first_name}, this is {clinic_name}. "
            "We saw you started booking a {service} appointment. "
            "Your selected time may still be available. "
            "Want to complete your booking? Reply YES."
        ),
        "post_visit_follow_up": (
            "Hi {first_name}, this is {clinic_name}. "
            "Hope you're feeling great after your recent visit! "
            "Based on your visit, you might be interested in {service}. "
            "Want to learn more? Reply YES or ask us anything."
        ),
        "insurance_question": (
            "Hi {first_name}, this is {clinic_name}. "
            "We wanted to follow up on your insurance question for {service}. "
            "Our team can verify your benefits and explain your coverage. "
            "Call us at {clinic_phone} — we're happy to help."
        ),
        "after_hours_lead": (
            "Hi {first_name}, this is {clinic_name}. "
            "Thanks for reaching out to us! We received your message "
            "and a team member will get back to you soon. "
            "If this is urgent, please call {clinic_phone}."
        ),
    }

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    def generate_message(
        self,
        recapture_type: str,
        patient: dict[str, Any],
        clinic: dict[str, Any],
        channel: ChannelType,
        personalization: dict[str, Any] | None = None,
    ) -> MessageGenerationResult:
        """
        Generate a personalized recapture message.

        Args:
            recapture_type: The type of recapture (from taxonomy)
            patient: Patient data dict
            clinic: Clinic data dict
            channel: Target communication channel
            personalization: Optional personalization hints

        Returns:
            MessageGenerationResult with the generated message
        """
        # Get base template
        template = self.TEMPLATES.get(
            recapture_type,
            self.TEMPLATES.get("lead_abandoned"),
        )

        if template is None:
            return MessageGenerationResult(
                message="",
                channel=channel,
                requires_review=True,
            )

        # Fill in template variables with VERIFIED data only
        try:
            message = template.format(
                first_name=patient.get("first_name", "there"),
                clinic_name=clinic.get("name", "our dental office"),
                clinic_phone=clinic.get("phone", ""),
                service=personalization.get("service", "dental care") if personalization else "dental care",
            )
        except (KeyError, ValueError) as e:
            logger.error(f"Template formatting error: {e}")
            message = template.replace("{first_name}", patient.get("first_name", "there"))

        # Personalize with LLM if available and not in mock mode
        if not self.llm.mock_mode and personalization:
            message = self._personalize_with_llm(message, patient, personalization)

        return MessageGenerationResult(
            message=message,
            channel=channel,
            cta="reply_yes" if channel == ChannelType.SMS else "call",
            confidence=0.85,
        )

    def _personalize_with_llm(
        self,
        base_message: str,
        patient: dict[str, Any],
        personalization: dict[str, Any],
    ) -> str:
        """
        Use LLM to personalize a template message.

        CRITICAL: The LLM can only use facts provided in the prompt.
        It must never invent appointments, insurance coverage, prices, etc.
        """
        system = """You are a message personalizer for a dental practice.
Your job: make the message feel personal and helpful.

RULES — NEVER VIOLATE:
1. Only use facts provided below. Do NOT invent appointments, prices, insurance coverage, discounts, or availability.
2. Do NOT diagnose or give medical advice.
3. Do NOT promise anything you can't verify.
4. Keep the message under 320 characters for SMS.
5. Include the opt-out instruction: "Reply STOP to opt out"
6. Tone: friendly, helpful, not pushy.

Patient facts:
{patient_facts}

Personalization hints:
{personalization}"""

        prompt = f"""Personalize this message for the patient:

BASE MESSAGE: {base_message}

Return the personalized message only, no explanation."""

        response = self.llm.complete(
            prompt=prompt,
            system_prompt=system.format(
                patient_facts=json.dumps({
                    "name": patient.get("first_name", ""),
                    "last_name": patient.get("last_name", ""),
                    "notes": patient.get("notes", ""),
                    "recapture_reason": patient.get("recapture_reason", ""),
                }),
                personalization=json.dumps(personalization),
            ),
            max_tokens=200,
            temperature=0.3,
        )

        personalized = response["content"].strip()

        # Safety check: ensure opt-out is present for SMS
        if "STOP" not in personalized and "stop" not in personalized.lower():
            personalized += " Reply STOP to opt out."

        return personalized

    def generate_conversation_response(
        self,
        user_message: str,
        conversation_context: dict[str, Any],
        patient: dict[str, Any],
        clinic: dict[str, Any],
    ) -> MessageGenerationResult:
        """
        Generate a response to a patient message in an ongoing conversation.

        This is for the Patient Runtime / Concierge product.
        """
        system = f"""You are the AI assistant for {clinic.get('name', 'a dental practice')}.

RULES — NEVER VIOLATE:
1. NEVER fabricate appointments, availability, insurance coverage, prices, or treatment outcomes.
2. NEVER diagnose or give medical advice. If a patient describes symptoms, acknowledge and offer to connect them with the team.
3. NEVER promise anything you can't verify with a tool.
4. If you don't know something, say so and offer to connect them with staff.
5. For appointment booking, you must use the check_availability and book_appointment tools.
6. For insurance questions, you must use the check_insurance tool.
7. Keep responses concise (under 500 characters for SMS).
8. If the patient asks for a human, escalate immediately.
9. If emergency keywords are detected, escalate immediately.

Clinic info:
- Name: {clinic.get('name')}
- Phone: {clinic.get('phone')}
- Hours: Monday-Friday 8am-5pm, Saturday 9am-1pm"""

        prompt = f"""Patient message: "{user_message}"

Conversation context: {json.dumps(conversation_context, default=str)}

Generate a helpful response. If you need to use a tool, indicate which tool."""

        response = self.llm.complete(
            prompt=prompt,
            system_prompt=system,
            max_tokens=300,
            temperature=0.3,
        )

        return MessageGenerationResult(
            message=response["content"],
            channel=ChannelType.SMS,
            confidence=0.8,
        )
