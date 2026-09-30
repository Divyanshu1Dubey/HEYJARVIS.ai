"""
HeyJarvis Safety Classifier
============================
Lightweight classifier for detecting safety-relevant content in patient messages.

This is a rules-first system with optional ML augmentation.
In V1, it uses keyword/regex patterns. In V2+, it can use a small classifier.

Key classifications:
  - SAFE: Normal patient message, proceed normally
  - URGENT: Patient needs to be seen soon (same day)
  - EMERGENCY: Patient needs immediate care
  - PROHIBITED: Patient is asking for something outside AI scope

Design principles:
  - High sensitivity: Better to over-escalate than miss an emergency
  - Low false negative rate for emergencies
  - Never minimize patient symptoms
  - Deterministic patterns first, ML second
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from shared.constants import (
    EMERGENCY_KEYWORDS,
    MEDICAL_ADVICE_TRIGGERS,
)
from shared.models import SafetyLevel, HandoffReason


@dataclass
class SafetyResult:
    """Result of safety classification."""
    level: SafetyLevel
    matched_patterns: list[str] = field(default_factory=list)
    escalation_reason: Optional[HandoffReason] = None
    confidence: float = 1.0
    requires_human: bool = False
    recommended_response: str = "proceed"

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "matched_patterns": self.matched_patterns,
            "escalation_reason": self.escalation_reason.value if self.escalation_reason else None,
            "confidence": self.confidence,
            "requires_human": self.requires_human,
            "recommended_response": self.recommended_response,
        }


class SafetyClassifier:
    """
    Classifies patient messages for safety.

    Uses a tiered approach:
      1. Pattern matching (deterministic)
      2. LLM classification (for ambiguous cases)
    """

    # Pattern definitions with their classifications
    PATTERNS = [
        # EMERGENCY patterns — must have additional clinical indicator
        (
            SafetyLevel.EMERGENCY,
            re.compile(
                r"(bleeding|swollen|abscess|pus|infection|fever|chills)"
                r".{0,50}"
                r"(won't stop|gush|severe|spreading|face|breath)",
                re.IGNORECASE,
            ),
            HandoffReason.EMERGENCY,
        ),
        (
            SafetyLevel.EMERGENCY,
            re.compile(
                r"(tooth.{0,5}(fell out|knocked out|broken off|avulsed|loose))",
                re.IGNORECASE,
            ),
            HandoffReason.EMERGENCY,
        ),
        (
            SafetyLevel.EMERGENCY,
            re.compile(
                r"(can't|cannot).{0,10}breathe",
                re.IGNORECASE,
            ),
            HandoffReason.EMERGENCY,
        ),
        # URGENT patterns
        (
            SafetyLevel.URGENT,
            re.compile(
                r"(severe|extreme|unbearable|worst).{0,20}(pain|ache|throbbing)",
                re.IGNORECASE,
            ),
            HandoffReason.PATIENT_REQUESTED,
        ),
        (
            SafetyLevel.URGENT,
            re.compile(
                r"(broken|cracked|chipped).{0,20}(tooth|teeth)",
                re.IGNORECASE,
            ),
            HandoffReason.PATIENT_REQUESTED,
        ),
        # MEDICAL ADVICE — must escalate
        (
            SafetyLevel.PROHIBITED,
            re.compile(
                r"(diagnose|diagnosis|prescribe|medication|treatment plan)"
                r".{0,30}(me|this|my|should)",
                re.IGNORECASE,
            ),
            HandoffReason.MEDICAL_QUESTION,
        ),
        (
            SafetyLevel.PROHIBITED,
            re.compile(
                r"(is this serious|how serious|am i okay|what does this mean|should i take)",
                re.IGNORECASE,
            ),
            HandoffReason.MEDICAL_QUESTION,
        ),
    ]

    def classify(self, message: str) -> SafetyResult:
        """
        Classify a patient message for safety concerns.
        """
        if not message or not message.strip():
            return SafetyResult(SafetyLevel.SAFE)

        message_lower = message.lower()
        matched_patterns = []

        # Check patterns in order (emergency first)
        for level, pattern, escalation_reason in self.PATTERNS:
            if pattern.search(message):
                matched_patterns.append(pattern.pattern[:80])
                if level == SafetyLevel.EMERGENCY:
                    return SafetyResult(
                        level=level,
                        matched_patterns=matched_patterns,
                        escalation_reason=escalation_reason,
                        requires_human=True,
                        recommended_response="immediate_escalation",
                    )
                elif level == SafetyLevel.URGENT:
                    return SafetyResult(
                        level=level,
                        matched_patterns=matched_patterns,
                        escalation_reason=escalation_reason,
                        requires_human=True,
                        recommended_response="urgent_booking",
                    )
                elif level == SafetyLevel.PROHIBITED:
                    return SafetyResult(
                        level=level,
                        matched_patterns=matched_patterns,
                        escalation_reason=escalation_reason,
                        requires_human=True,
                        recommended_response="escalation",
                    )

        return SafetyResult(
            level=SafetyLevel.SAFE,
            matched_patterns=[],
            recommended_response="proceed",
        )

    def classify_llm(self, message: str, llm_client) -> SafetyResult:
        """
        Use LLM for ambiguous cases where patterns aren't enough.
        Called only when pattern matching returns SAFE but message is long/complex.
        """
        # In V1, we skip LLM safety classification
        # V2+ will add this for better coverage
        return self.classify(message)
