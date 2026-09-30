"""
HeyJarvis API Routes
=====================
Route aggregator.
"""

from fastapi import APIRouter

from apps.api.routes import auth, patients, conversations, messages, recapture, appointments, campaigns, analytics

__all__ = ["router"]

# Routes are included in main.py
__all__ = []
