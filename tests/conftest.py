"""
Pytest configuration and shared fixtures.
"""

from __future__ import annotations

import pytest
import asyncio
from typing import AsyncGenerator


# ---------------------------------------------------------------------------
# Event loop
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Mock database
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    """Provide a mock database session."""
    class MockDB:
        def __init__(self):
            self.data: dict = {}
            self.committed = []

        def add(self, obj):
            self.data[id(obj)] = obj

        def commit(self):
            self.committed.append(list(self.data.values()))

        def query(self, model):
            return MockQuery(self, model)

        def get(self, model, pk):
            return self.data.get(pk)

        def delete(self, obj):
            self.data.pop(id(obj), None)

    class MockQuery:
        def __init__(self, db, model):
            self.db = db
            self.model = model
            self._filters = []
            self._limit_val = None

        def filter(self, *conditions):
            self._filters.extend(conditions)
            return self

        def first(self):
            for obj in self.db.data.values():
                if isinstance(obj, self.model):
                    return obj
            return None

        def all(self):
            return [obj for obj in self.db.data.values() if isinstance(obj, self.model)]

        def limit(self, n):
            self._limit_val = n
            return self

    return MockDB()


# ---------------------------------------------------------------------------
# Mock Redis
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_redis():
    """Provide a mock Redis client."""
    class MockRedis:
        def __init__(self):
            self.store: dict = {}

        async def get(self, key):
            return self.store.get(key)

        async def set(self, key, value, ex=None):
            self.store[key] = value
            return True

        async def delete(self, key):
            return self.store.pop(key, None) is not None

        async def incr(self, key):
            val = int(self.store.get(key, 0)) + 1
            self.store[key] = str(val)
            return val

        async def expire(self, key, seconds):
            return True

    return MockRedis()


# ---------------------------------------------------------------------------
# Mock Anthropic client
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_anthropic_client():
    """Provide a mock Anthropic client."""
    class MockMessage:
        content = [{"type": "text", "text": '{"intent": "general_question", "confidence": 0.9, "urgency": "normal"}'}]
        stop_reason = "end_turn"
        usage = {"input_tokens": 100, "output_tokens": 50}

    class MockClient:
        def messages(self, **kwargs):
            return MockMessage()

    return MockClient()


# ---------------------------------------------------------------------------
# Policy engine fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def policy_engine(mock_db, mock_redis):
    """Provide a policy engine with mock dependencies."""
    from packages.policy.policy_engine import PolicyEngine
    return PolicyEngine(db_session=mock_db, redis_client=mock_redis)


# ---------------------------------------------------------------------------
# Safety classifier fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def safety_classifier():
    """Provide a safety classifier instance."""
    from packages.policy.safety import SafetyClassifier
    return SafetyClassifier()


# ---------------------------------------------------------------------------
# LLM client fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def llm_client():
    """Provide an LLM client in mock mode."""
    from packages.ai.ai_engine import LLMClient
    return LLMClient()


# ---------------------------------------------------------------------------
# Message generator fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def message_generator(llm_client):
    """Provide a message generator."""
    from packages.ai.ai_engine import MessageGenerator
    return MessageGenerator(llm_client=llm_client)
