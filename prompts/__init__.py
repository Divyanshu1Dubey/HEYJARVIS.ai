"""
HeyJarvis Prompt Specifications
=================================
All production prompts organized by use case.

Each prompt has:
- system: System prompt for the LLM
- user_template: Template for user message
- output_format: Expected output structure
- safety_notes: Critical safety reminders
"""

from .prompts import (
    INTENT_CLASSIFIER_SYSTEM,
    INTENT_CLASSIFIER_USER,
    SAFETY_CLASSIFIER_SYSTEM,
    SAFETY_CLASSIFIER_USER,
    MESSAGE_GENERATOR_SYSTEM,
    MESSAGE_GENERATOR_USER,
    CONVERSATION_SYSTEM,
    CONVERSATION_USER,
    RECAPTURE_REASON_SYSTEM,
    RECAPTURE_REASON_USER,
    HANDOFF_SUMMARIZER_SYSTEM,
    HANDOFF_SUMMARIZER_USER,
    NEXT_BEST_ACTION_SYSTEM,
    NEXT_BEST_ACTION_USER,
)

__all__ = [
    "INTENT_CLASSIFIER_SYSTEM",
    "INTENT_CLASSIFIER_USER",
    "SAFETY_CLASSIFIER_SYSTEM",
    "SAFETY_CLASSIFIER_USER",
    "MESSAGE_GENERATOR_SYSTEM",
    "MESSAGE_GENERATOR_USER",
    "CONVERSATION_SYSTEM",
    "CONVERSATION_USER",
    "RECAPTURE_REASON_SYSTEM",
    "RECAPTURE_REASON_USER",
    "HANDOFF_SUMMARIZER_SYSTEM",
    "HANDOFF_SUMMARIZER_USER",
    "NEXT_BEST_ACTION_SYSTEM",
    "NEXT_BEST_ACTION_USER",
]
