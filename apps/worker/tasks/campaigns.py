"""
HeyJarvis Worker — Campaign Tasks
=====================================
Background tasks for campaign execution.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta
from typing import Any

from celery import shared_task

from shared.demo_data import _make_recapture_opportunities, _make_patients, _make_campaigns
from shared.communication import get_communication_provider, MessageResult
from shared.ai_engine import MessageGenerator
from shared.models import ChannelType

logger = logging.getLogger(__name__)


# =============================================================================
# Campaign Execution
# =============================================================================

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_due_messages(self):
    """
    Scan for and send all due campaign messages.

    Runs every minute via Celery Beat.
    """
    logger.info("Scanning for due campaign messages...")

    opportunities = _make_recapture_opportunities()
    patients = {p["id"]: p for p in _make_patients()}
    campaigns = {c["recapture_type"]: c for c in _make_campaigns()}

    sent_count = 0
    failed_count = 0

    for opp in opportunities:
        if opp.get("status") != "pending":
            continue

        # Check if we should send
        patient = patients.get(opp["patient_id"])
        if not patient:
            continue

        recapture_type = opp.get("recapture_type", "lead_abandoned")
        campaign = campaigns.get(recapture_type)
        if not campaign or not campaign.get("is_active"):
            continue

        # Check attempt count
        attempt_count = opp.get("attempt_count", 0)
        if attempt_count >= campaign.get("max_attempts", 3):
            continue

        # Generate message
        generator = MessageGenerator()
        clinic = {"name": "Bright Smile Dental", "phone": "(512) 555-0142"}

        result = generator.generate_message(
            recapture_type=recapture_type,
            patient=patient,
            clinic=clinic,
            channel=ChannelType.SMS,
        )

        if not result.message:
            continue

        # Send message (mock)
        provider = get_communication_provider(ChannelType.SMS)
        phone = patient.get("phone", "+1-512-555-0000")

        try:
            # In production, this would be awaited in an async context
            import asyncio
            send_result: MessageResult = asyncio.get_event_loop().run_until_complete(
                provider.send_sms(to=phone, body=result.message)
            )

            if send_result.success:
                sent_count += 1
                logger.info(f"Sent message to {patient['first_name']} ({recapture_type})")
            else:
                failed_count += 1
                logger.error(f"Failed to send to {patient['first_name']}: {send_result.error}")

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            failed_count += 1

    logger.info(f"Campaign run complete: {sent_count} sent, {failed_count} failed")
    return {"sent": sent_count, "failed": failed_count}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_single_message(self, patient_id: str, recapture_type: str, channel: str = "sms"):
    """
    Send a single outreach message to a patient.

    This is called when a specific outreach is triggered.
    """
    logger.info(f"Sending {channel} message to {patient_id} for {recapture_type}")

    patients = {p["id"]: p for p in _make_patients()}
    patient = patients.get(patient_id)

    if not patient:
        logger.error(f"Patient not found: {patient_id}")
        return {"success": False, "error": "Patient not found"}

    generator = MessageGenerator()
    clinic = {"name": "Bright Smile Dental", "phone": "(512) 555-0142"}

    result = generator.generate_message(
        recapture_type=recapture_type,
        patient=patient,
        clinic=clinic,
        channel=ChannelType(channel),
    )

    if not result.message:
        return {"success": False, "error": "Message generation failed"}

    # Send
    provider = get_communication_provider(ChannelType(channel))
    phone = patient.get("phone", "+1-512-555-0000")

    try:
        import asyncio
        send_result = asyncio.get_event_loop().run_until_complete(
            provider.send_sms(to=phone, body=result.message)
        )

        if send_result.success:
            logger.info(f"Message sent to {patient['first_name']}: {result.message[:50]}...")
            return {
                "success": True,
                "external_id": send_result.external_id,
                "message": result.message[:100],
            }
        else:
            return {"success": False, "error": send_result.error}

    except Exception as e:
        logger.error(f"Send error: {e}")
        self.retry(exc=e)
        return {"success": False, "error": str(e)}


@shared_task
def process_reply(patient_id: str, message_body: str, channel: str = "sms"):
    """
    Process an incoming patient reply.

    This triggers:
      1. Safety check
      2. Intent classification
      3. Conversation update
      4. AI response generation (if appropriate)
      5. Campaign state update
    """
    logger.info(f"Processing reply from {patient_id}: {message_body[:50]}...")

    from shared.safety import SafetyClassifier
    from shared.ai_engine import IntentClassifier, MessageGenerator, LLMClient
    from shared.models import ChannelType

    # Safety check
    safety = SafetyClassifier()
    safety_result = safety.classify(message_body)

    if safety_result.requires_human:
        logger.warning(f"Safety escalation required for patient {patient_id}")
        return {
            "action": "escalate",
            "reason": safety_result.escalation_reason.value if safety_result.escalation_reason else "safety",
            "response": "Let me connect you with our team right away.",
        }

    # Intent classification
    llm = LLMClient()
    intent_clf = IntentClassifier(llm_client=llm)
    intent = intent_clf.classify(message_body)

    # Handle opt-out
    if intent.intent.value == "opt_out":
        return {
            "action": "opt_out",
            "intent": "opt_out",
            "response": "You've been removed from our messages. Reply START if you change your mind.",
        }

    # Generate response
    generator = MessageGenerator(llm_client=llm)
    patients = _make_patients()
    patient = next((p for p in patients if p["id"] == patient_id), {})
    clinic = {"name": "Bright Smile Dental", "phone": "(512) 555-0142"}

    result = generator.generate_conversation_response(
        user_message=message_body,
        conversation_context={"patient_replied": True},
        patient=patient,
        clinic=clinic,
    )

    return {
        "action": "respond",
        "intent": intent.intent.value,
        "requires_human": intent.requires_human,
        "response": result.message,
    }


@shared_task
def detect_opportunities():
    """
    Scan for new recapture opportunities.

    Runs every 30 minutes.
    Looks for:
      - New abandoned leads
      - Recent cancellations
      - No-shows
      - Unscheduled treatment plans
      - Overdue recalls
    """
    logger.info("Scanning for recapture opportunities...")
    # In production, this would query the database for:
    # 1. Leads with no activity for X hours
    # 2. Cancelled appointments
    # 3. No-shows
    # 4. Treatment plans not scheduled
    # 5. Overdue recalls

    opportunities = _make_recapture_opportunities()
    new_opportunities = [o for o in opportunities if o.get("status") == "pending"]

    logger.info(f"Found {len(new_opportunities)} recapture opportunities")
    return {"opportunities_found": len(new_opportunities)}


@shared_task
def check_recalls():
    """
    Check for patients due for recall.

    Runs daily at 6 AM.
    """
    logger.info("Checking for due recalls...")
    # In production, query for patients whose next recall date has passed
    return {"recalls_found": 0}
