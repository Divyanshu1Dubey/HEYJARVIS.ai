"""
Tests for the AI engine.
"""

from __future__ import annotations

import pytest
from packages.ai.ai_engine import LLMClient, IntentClassifier, MessageGenerator, IntentResult


class TestLLMClient:
    """Test the LLM client."""

    def test_mock_mode(self):
        client = LLMClient()  # No API key = mock mode
        result = client.complete("Hello", max_tokens=50)
        assert "content" in result
        assert "usage" in result
        assert "model" in result

    def test_mock_intent_classification(self):
        client = LLMClient()
        result = client.complete("classify intent: I want to book", max_tokens=50)
        assert "intent" in result["content"].lower() or "general" in result["content"].lower()


class TestIntentClassifier:
    """Test intent classification."""

    def setUp(self):
        self.llm = LLMClient()
        self.clf = IntentClassifier(llm_client=self.llm)

    def test_book_appointment(self):
        clf = IntentClassifier(llm_client=LLMClient())
        result = clf.classify("I want to book an appointment")
        assert result.intent.value == "book_appointment"
        assert result.confidence > 0

    def test_cancel_appointment(self):
        clf = IntentClassifier(llm_client=LLMClient())
        result = clf.classify("I need to cancel my appointment")
        assert result.intent.value == "cancel"

    def test_insurance_question(self):
        clf = IntentClassifier(llm_client=LLMClient())
        result = clf.classify("Do you accept Delta Dental?")
        assert result.intent.value == "insurance_question"
        assert "insurance" in result.entities

    def test_hours_question(self):
        clf = IntentClassifier(llm_client=LLMClient())
        result = clf.classify("What are your hours?")
        assert result.intent.value == "hours_question"

    def test_human_handoff(self):
        clf = IntentClassifier(llm_client=LLMClient())
        result = clf.classify("Can I speak to a real person?")
        assert result.intent.value == "human_handoff"

    def test_opt_out(self):
        clf = IntentClassifier(llm_client=LLMClient())
        result = clf.classify("STOP")
        assert result.intent.value == "opt_out"

    def test_empty_message(self):
        clf = IntentClassifier(llm_client=LLMClient())
        result = clf.classify("")
        assert result.intent.value == "unknown"
        assert result.confidence == 0.0


class TestMessageGenerator:
    """Test message generation."""

    def setUp(self):
        self.generator = MessageGenerator(llm_client=LLMClient())

    def test_lead_abandoned_template(self):
        result = self.generator.generate_message(
            recapture_type="lead_abandoned",
            patient={"first_name": "John", "last_name": "Doe"},
            clinic={"name": "Test Dental", "phone": "555-0142"},
            channel=ChannelType.SMS,
        )
        assert "John" in result.message
        assert "Test Dental" in result.message
        assert result.channel == ChannelType.SMS

    def test_cancelled_template(self):
        result = self.generator.generate_message(
            recapture_type="cancelled_scheduling",
            patient={"first_name": "Jane"},
            clinic={"name": "Test Dental", "phone": "555-0142"},
            channel=ChannelType.SMS,
        )
        assert "Jane" in result.message

    def test_unknown_template_falls_back(self):
        result = self.generator.generate_message(
            recapture_type="unknown_type",
            patient={"first_name": "Test"},
            clinic={"name": "Test Dental", "phone": "555-0142"},
            channel=ChannelType.SMS,
        )
        # Should return empty or fallback for unknown type
        assert result.requires_review or len(result.message) == 0
