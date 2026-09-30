"""
HeyJarvis Prompt Index
======================
Index of all prompts with descriptions.
"""

PROMPTS = {
    "intent_classifier": {
        "file": "prompts/prompts.py",
        "description": "Classifies patient message intent",
        "model": "claude-3-5-haiku",
        "temperature": 0.1,
        "max_tokens": 200,
        "safety_level": "low",
    },
    "safety_classifier": {
        "file": "prompts/prompts.py",
        "description": "Detects emergency/safety concerns in patient messages",
        "model": "claude-3-5-haiku",
        "temperature": 0.0,
        "max_tokens": 150,
        "safety_level": "critical",
    },
    "message_generator": {
        "file": "prompts/prompts.py",
        "description": "Generates personalized outreach messages",
        "model": "claude-3-5-sonnet",
        "temperature": 0.3,
        "max_tokens": 300,
        "safety_level": "high",
    },
    "conversation_response": {
        "file": "prompts/prompts.py",
        "description": "Generates AI responses in patient conversations",
        "model": "claude-3-5-sonnet",
        "temperature": 0.3,
        "max_tokens": 400,
        "safety_level": "critical",
    },
    "recapture_reason_classifier": {
        "file": "prompts/prompts.py",
        "description": "Classifies why a patient didn't convert",
        "model": "claude-3-5-haiku",
        "temperature": 0.1,
        "max_tokens": 200,
        "safety_level": "low",
    },
    "handoff_summarizer": {
        "file": "prompts/prompts.py",
        "description": "Summarizes conversation for staff handoff",
        "model": "claude-3-5-haiku",
        "temperature": 0.2,
        "max_tokens": 300,
        "safety_level": "medium",
    },
    "next_best_action": {
        "file": "prompts/prompts.py",
        "description": "Determines next action for patient outreach",
        "model": "claude-3-5-haiku",
        "temperature": 0.1,
        "max_tokens": 200,
        "safety_level": "medium",
    },
}
