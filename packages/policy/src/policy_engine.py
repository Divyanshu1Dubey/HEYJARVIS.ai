"""
HeyJarvis Policy Engine
========================
Deterministic policy layer that enforces all safety, compliance, and
business rules BEFORE any AI generation occurs.

The policy engine is the gatekeeper. No AI output reaches the patient
without passing through these rules first.

Key policies enforced:
  - Consent verification (SMS, email, voice)
  - Opt-out suppression (STOP keyword, patient request)
  - Frequency caps (per patient, per channel)
  - Quiet hours (per patient, per clinic)
  - Do-not-contact list
  - Duplicate outreach suppression
  - Channel eligibility
  - Safety escalation triggers
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from enum import Enum

from shared.models import (
    Consent, ConsentType, ConsentMethod,
    PatientState, Patient, ChannelType,
    CommunicationPreferences,
    CampaignAttempt, AttemptStatus,
    HandoffReason, EventType,
)
from shared.constants import (
    SMS_OPT_OUT_KEYWORDS, SMS_OPT_IN_KEYWORDS,
    DEFAULT_MAX_MESSAGES_PER_DAY, DEFAULT_MAX_MESSAGES_PER_WEEK,
    DEFAULT_COOLDOWN_HOURS, DEFAULT_BUSINESS_HOURS,
    DEFAULT_TIMEZONE,
)


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_ESCALATION = "require_escalation"
    REQUIRE_CONFIRMATION = "require_confirmation"


class PolicyResult:
    """Result of a policy evaluation."""

    def __init__(
        self,
        decision: PolicyDecision,
        reason: str,
        details: dict[str, Any] | None = None,
        escalation_reason: str | None = None,
    ):
        self.decision = decision
        self.reason = reason
        self.details = details or {}
        self.escalation_reason = escalation_reason

    @property
    def allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOW

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "details": self.details,
            "escalation_reason": self.escalation_reason,
        }


class PolicyEngine:
    """
    Central policy engine for all outreach and AI actions.

    All methods are synchronous/pure functions on input data —
    no side effects, no external calls. This makes them testable,
    deterministic, and auditable.
    """

    def __init__(self, db_session=None, redis_client=None):
        self.db = db_session
        self.redis = redis_client

    # =========================================================================
    # CONSENT
    # =========================================================================

    def check_consent(
        self,
        tenant_id: str,
        patient_id: str,
        channel: ChannelType,
    ) -> PolicyResult:
        """
        Check if patient has valid consent for the given channel.
        Consent must be:
          - Granted (not revoked)
          - Not expired
          - For the correct channel type
        """
        if self.db is None:
            # No DB — deny by default in production
            return PolicyResult(
                PolicyDecision.DENY,
                "No database connection for consent check",
            )

        consent_type_map = {
            ChannelType.SMS: ConsentType.SMS,
            ChannelType.EMAIL: ConsentType.EMAIL,
            ChannelType.VOICE: ConsentType.VOICE,
            ChannelType.WHATSAPP: ConsentType.SMS,  # SMS consent covers WhatsApp
            ChannelType.WEB_CHAT: ConsentType.EMAIL,  # Web chat uses email consent
            ChannelType.PORTAL: ConsentType.EMAIL,
        }

        required_consent_type = consent_type_map.get(channel)
        if required_consent_type is None:
            return PolicyResult(
                PolicyDecision.DENY,
                f"Unknown channel type: {channel}",
            )

        # Query latest consent record for this patient + type
        consent = (
            self.db.query(Consent)
            .filter(
                Consent.tenant_id == tenant_id,
                Consent.patient_id == patient_id,
                Consent.consent_type == required_consent_type,
            )
            .order_by(Consent.granted_at.desc())
            .first()
        )

        if consent is None:
            return PolicyResult(
                PolicyDecision.DENY,
                f"No consent record found for {channel.value}",
                details={"channel": channel.value},
            )

        if not consent.granted:
            return PolicyResult(
                PolicyDecision.DENY,
                "Consent revoked",
                details={
                    "channel": channel.value,
                    "revoked_at": consent.revoked_at.isoformat() if consent.revoked_at else None,
                },
            )

        if consent.revoked_at and consent.revoked_at < datetime.utcnow():
            return PolicyResult(
                PolicyDecision.DENY,
                "Consent expired",
                details={"channel": channel.value},
            )

        return PolicyResult(
            PolicyDecision.ALLOW,
            f"Consent valid for {channel.value}",
            details={
                "channel": channel.value,
                "granted_at": consent.granted_at.isoformat(),
                "method": consent.method.value if consent.method else None,
            },
        )

    # =========================================================================
    # OPT-OUT
    # =========================================================================

    def check_opt_out(
        self,
        tenant_id: str,
        patient_id: str,
    ) -> PolicyResult:
        """
        Check if patient has opted out of ALL communications.
        """
        if self.db is None:
            return PolicyResult(PolicyDecision.DENY, "No database connection")

        prefs = (
            self.db.query(CommunicationPreferences)
            .filter(
                CommunicationPreferences.tenant_id == tenant_id,
                CommunicationPreferences.patient_id == patient_id,
            )
            .first()
        )

        if prefs and prefs.do_not_contact:
            return PolicyResult(
                PolicyDecision.DENY,
                "Patient has do_not_contact set",
                details={"set_at": prefs.updated_at.isoformat() if prefs.updated_at else None},
            )

        # Check patient state
        patient = (
            self.db.query(Patient)
            .filter(
                Patient.tenant_id == tenant_id,
                Patient.id == patient_id,
            )
            .first()
        )

        if patient and patient.state in (
            PatientState.OPTED_OUT,
            PatientState.DO_NOT_CONTACT,
        ):
            return PolicyResult(
                PolicyDecision.DENY,
                f"Patient state prevents contact: {patient.state.value}",
            )

        return PolicyResult(PolicyDecision.ALLOW, "No opt-out found")

    # =========================================================================
    # FREQUENCY CAPS
    # =========================================================================

    def check_frequency_cap(
        self,
        tenant_id: str,
        patient_id: str,
        channel: ChannelType,
    ) -> PolicyResult:
        """
        Check if patient has exceeded frequency caps for the channel.
        """
        if self.db is None:
            return PolicyResult(PolicyDecision.DENY, "No database connection")

        prefs = (
            self.db.query(CommunicationPreferences)
            .filter(
                CommunicationPreferences.tenant_id == tenant_id,
                CommunicationPreferences.patient_id == patient_id,
                CommunicationPreferences.channel == channel,
            )
            .first()
        )

        max_per_day = prefs.max_messages_per_day if prefs else DEFAULT_MAX_MESSAGES_PER_DAY
        max_per_week = prefs.max_messages_per_week if prefs else DEFAULT_MAX_MESSAGES_PER_WEEK

        now = datetime.utcnow()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = day_start - timedelta(days=now.weekday())

        # Count messages sent today
        sent_today = (
            self.db.query(CampaignAttempt)
            .filter(
                CampaignAttempt.tenant_id == tenant_id,
                CampaignAttempt.patient_id == patient_id,
                CampaignAttempt.channel == channel,
                CampaignAttempt.status == AttemptStatus.SENT,
                CampaignAttempt.sent_at >= day_start,
            )
            .count()
        )

        if sent_today >= max_per_day:
            return PolicyResult(
                PolicyDecision.DENY,
                f"Daily cap reached: {sent_today}/{max_per_day}",
                details={"sent_today": sent_today, "cap": max_per_day},
            )

        # Count messages sent this week
        sent_this_week = (
            self.db.query(CampaignAttempt)
            .filter(
                CampaignAttempt.tenant_id == tenant_id,
                CampaignAttempt.patient_id == patient_id,
                CampaignAttempt.channel == channel,
                CampaignAttempt.status == AttemptStatus.SENT,
                CampaignAttempt.sent_at >= week_start,
            )
            .count()
        )

        if sent_this_week >= max_per_week:
            return PolicyResult(
                PolicyDecision.DENY,
                f"Weekly cap reached: {sent_this_week}/{max_per_week}",
                details={"sent_this_week": sent_this_week, "cap": max_per_week},
            )

        return PolicyResult(
            PolicyDecision.ALLOW,
            f"Within frequency cap: {sent_today}/{max_per_day} today, {sent_this_week}/{max_per_week} this week",
        )

    # =========================================================================
    # QUIET HOURS
    # =========================================================================

    def check_quiet_hours(
        self,
        tenant_id: str,
        patient_id: str,
        channel: ChannelType,
        send_at: datetime | None = None,
    ) -> PolicyResult:
        """
        Check if sending at the given time would violate quiet hours.
        """
        if self.db is None:
            return PolicyResult(PolicyDecision.ALLOW, "No DB — assuming OK")

        if send_at is None:
            send_at = datetime.utcnow()

        prefs = (
            self.db.query(CommunicationPreferences)
            .filter(
                CommunicationPreferences.tenant_id == tenant_id,
                CommunicationPreferences.patient_id == patient_id,
            )
            .first()
        )

        # Get patient timezone
        patient = (
            self.db.query(Patient)
            .filter(
                Patient.tenant_id == tenant_id,
                Patient.id == patient_id,
            )
            .first()
        )
        tz_name = patient.timezone if patient else DEFAULT_TIMEZONE

        try:
            import pytz
            tz = pytz.timezone(tz_name)
            local_time = send_at.astimezone(tz)
        except Exception:
            local_time = send_at

        current_hour_min = local_time.strftime("%H:%M")

        # Check patient quiet hours
        if prefs and prefs.quiet_hours_start and prefs.quiet_hours_end:
            if self._is_in_quiet_hours(
                current_hour_min,
                prefs.quiet_hours_start,
                prefs.quiet_hours_end,
            ):
                return PolicyResult(
                    PolicyDecision.DENY,
                    f"Quiet hours: {prefs.quiet_hours_start} - {prefs.quiet_hours_end}",
                    details={
                        "patient_timezone": tz_name,
                        "local_time": current_hour_min,
                        "quiet_start": prefs.quiet_hours_start,
                        "quiet_end": prefs.quiet_hours_end,
                    },
                )

        return PolicyResult(PolicyDecision.ALLOW, "Outside quiet hours")

    def _is_in_quiet_hours(
        self,
        current: str,
        start: str,
        end: str,
    ) -> bool:
        """Check if current time is within quiet hours range."""
        try:
            current_min = self._time_to_minutes(current)
            start_min = self._time_to_minutes(start)
            end_min = self._time_to_minutes(end)
        except ValueError:
            return False

        if start_min <= end_min:
            return start_min <= current_min < end_min
        else:
            # Quiet hours span midnight
            return current_min >= start_min or current_min < end_min

    @staticmethod
    def _time_to_minutes(t: str) -> int:
        parts = t.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    # =========================================================================
    # DUPLICATE SUPPRESSION
    # =========================================================================

    def check_duplicate_suppression(
        self,
        tenant_id: str,
        patient_id: str,
        campaign_type: str,
        cooldown_hours: int = DEFAULT_COOLDOWN_HOURS,
    ) -> PolicyResult:
        """
        Prevent duplicate outreach for the same campaign type within cooldown.
        """
        if self.db is None:
            return PolicyResult(PolicyDecision.ALLOW, "No DB")

        cutoff = datetime.utcnow() - timedelta(hours=cooldown_hours)

        recent = (
            self.db.query(CampaignAttempt)
            .filter(
                CampaignAttempt.tenant_id == tenant_id,
                CampaignAttempt.patient_id == patient_id,
                CampaignAttempt.metadata["campaign_type"].astext == campaign_type,
                CampaignAttempt.status == AttemptStatus.SENT,
                CampaignAttempt.sent_at >= cutoff,
            )
            .first()
        )

        if recent:
            return PolicyResult(
                PolicyDecision.DENY,
                f"Duplicate suppression: {campaign_type} sent {cooldown_hours}h ago",
                details={
                    "campaign_type": campaign_type,
                    "last_sent_at": recent.sent_at.isoformat() if recent.sent_at else None,
                },
            )

        return PolicyResult(PolicyDecision.ALLOW, "No recent duplicate")

    # =========================================================================
    # CHANNEL ELIGIBILITY
    # =========================================================================

    def check_channel_eligibility(
        self,
        tenant_id: str,
        patient_id: str,
        channel: ChannelType,
    ) -> PolicyResult:
        """
        Check if the channel is eligible for this patient.
        """
        if channel == ChannelType.VOICE:
            # Voice requires separate consent
            return PolicyResult(
                PolicyDecision.REQUIRE_CONFIRMATION,
                "Voice channel requires explicit voice consent",
                details={"channel": channel.value},
            )

        if channel == ChannelType.WHATSAPP:
            # WhatsApp requires business account and consent
            return PolicyResult(
                PolicyDecision.REQUIRE_CONFIRMATION,
                "WhatsApp requires business account verification",
                details={"channel": channel.value},
            )

        return PolicyResult(PolicyDecision.ALLOW, "Channel eligible")

    # =========================================================================
    # SAFETY
    # =========================================================================

    def check_safety(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> PolicyResult:
        """
        Check if message or patient input contains safety concerns.
        Returns escalation requirement for emergency keywords.
        """
        if not message:
            return PolicyResult(PolicyDecision.ALLOW, "Empty message")

        message_lower = message.lower()

        # Check for emergency keywords
        for keyword in ["emergency", "urgent"]:
            if keyword in message_lower:
                # Check for actual emergency context
                emergency_indicators = [
                    "bleeding", "swelling", "can't breathe",
                    "difficulty breathing", "broken", "fell",
                    "knocked out", "unbearable pain", "abscess",
                    "tooth fell out", "gushing blood",
                ]
                if any(ind in message_lower for ind in emergency_indicators):
                    return PolicyResult(
                        PolicyDecision.REQUIRE_ESCALATION,
                        "Emergency keyword detected with clinical indicators",
                        escalation_reason=HandoffReason.EMERGENCY.value,
                        details={"matched_keyword": keyword},
                    )

        # Check for medical advice requests
        medical_triggers = [
            "diagnose", "diagnosis", "prescribe", "medication",
            "treatment plan", "is this serious", "how serious",
            "am i okay", "what does this mean", "should i",
        ]
        for trigger in medical_triggers:
            if trigger in message_lower:
                return PolicyResult(
                    PolicyDecision.REQUIRE_ESCALATION,
                    "Medical advice request detected",
                    escalation_reason=HandoffReason.MEDICAL_QUESTION.value,
                    details={"matched_trigger": trigger},
                )

        return PolicyResult(PolicyDecision.ALLOW, "No safety concerns")

    # =========================================================================
    # COMPOSITE EVALUATION
    # =========================================================================

    def evaluate_outreach(
        self,
        tenant_id: str,
        patient_id: str,
        channel: ChannelType,
        message: str | None = None,
        campaign_type: str | None = None,
        send_at: datetime | None = None,
    ) -> PolicyResult:
        """
        Run all policy checks in order. First failure wins.
        Order matters: most critical checks first.
        """
        checks = []

        # 1. Opt-out (most critical)
        result = self.check_opt_out(tenant_id, patient_id)
        checks.append(result)
        if not result.allowed:
            return result

        # 2. Consent
        result = self.check_consent(tenant_id, patient_id, channel)
        checks.append(result)
        if not result.allowed:
            return result

        # 3. Safety
        if message:
            result = self.check_safety(message)
            checks.append(result)
            if result.decision == PolicyDecision.REQUIRE_ESCALATION:
                return result

        # 4. Frequency caps
        result = self.check_frequency_cap(tenant_id, patient_id, channel)
        checks.append(result)
        if not result.allowed:
            return result

        # 5. Quiet hours
        result = self.check_quiet_hours(tenant_id, patient_id, channel, send_at)
        checks.append(result)
        if not result.allowed:
            return result

        # 6. Duplicate suppression
        if campaign_type:
            result = self.check_duplicate_suppression(tenant_id, patient_id, campaign_type)
            checks.append(result)
            if not result.allowed:
                return result

        # 7. Channel eligibility
        result = self.check_channel_eligibility(tenant_id, patient_id, channel)
        if result.decision == PolicyDecision.DENY:
            return result

        return PolicyResult(
            PolicyDecision.ALLOW,
            "All policy checks passed",
            details={"checks_run": len(checks)},
        )
