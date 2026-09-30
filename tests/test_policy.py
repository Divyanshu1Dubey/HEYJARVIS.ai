"""
Tests for the policy engine.
"""

from __future__ import annotations

import pytest
from packages.policy.policy_engine import PolicyEngine, PolicyResult, PolicyDecision
from packages.policy.safety import SafetyClassifier, SafetyResult
from shared.models import ConsentType, ConsentMethod, ChannelType, PatientState, HandoffReason
from shared.constants import SMS_OPT_OUT_KEYWORDS


class TestPolicyEngine:
    """Test the policy engine."""

    def test_check_opt_out_no_db(self):
        engine = PolicyEngine(db_session=None, redis_client=None)
        result = engine.check_opt_out("tenant-1", "patient-1")
        assert result.decision == PolicyDecision.DENY
        assert "No database" in result.reason

    def test_check_frequency_cap_no_db(self):
        engine = PolicyEngine(db_session=None, redis_client=None)
        result = engine.check_frequency_cap("tenant-1", "patient-1", ChannelType.SMS)
        assert result.decision == PolicyDecision.DENY

    def test_evaluate_outreach_no_db(self):
        engine = PolicyEngine(db_session=None, redis_client=None)
        result = engine.evaluate_outreach(
            tenant_id="tenant-1",
            patient_id="patient-1",
            channel=ChannelType.SMS,
        )
        assert result.decision == PolicyDecision.DENY


class TestSafetyClassifier:
    """Test the safety classifier."""

    def test_safe_message(self):
        classifier = SafetyClassifier()
        result = classifier.classify("I'd like to schedule a cleaning")
        assert result.level.value == "safe"
        assert not result.requires_human

    def test_emergency_bleeding(self):
        classifier = SafetyClassifier()
        result = classifier.classify("I have severe bleeding that won't stop")
        assert result.level.value == "emergency"
        assert result.requires_human
        assert result.escalation_reason == HandoffReason.EMERGENCY

    def test_emergency_cant_breathe(self):
        classifier = SafetyClassifier()
        result = classifier.classify("I can't breathe, my face is swelling")
        assert result.level.value == "emergency"
        assert result.requires_human

    def test_urgent_broken_tooth(self):
        classifier = SafetyClassifier()
        result = classifier.classify("I broke my front tooth")
        assert result.level.value == "urgent"
        assert result.requires_human

    def test_medical_advice_diagnose(self):
        classifier = SafetyClassifier()
        result = classifier.classify("Can you diagnose my tooth pain?")
        assert result.level.value == "prohibited"
        assert result.requires_human
        assert result.escalation_reason == HandoffReason.MEDICAL_QUESTION

    def test_medical_advice_prescribe(self):
        classifier = SafetyClassifier()
        result = classifier.classify("Can you prescribe antibiotics for my infection?")
        assert result.level.value == "prohibited"
        assert result.requires_human

    def test_urgent_severe_pain(self):
        classifier = SafetyClassifier()
        result = classifier.classify("I have unbearable pain in my tooth")
        assert result.level.value == "urgent"

    def test_empty_message(self):
        classifier = SafetyClassifier()
        result = classifier.classify("")
        assert result.level.value == "safe"
        assert not result.requires_human
