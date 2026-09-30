"""
HeyJarvis Worker
================
Celery worker for background tasks.

Tasks:
  - Campaign execution
  - Message sending
  - Opportunity detection
  - Recapture scoring
  - Analytics aggregation
  - Scheduled reports
"""

from __future__ import annotations

import logging
import os
from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://heyjarvis:heyjarvis_dev@localhost:5432/heyjarvis")

app = Celery(
    "heyjarvis",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "apps.worker.tasks.campaigns",
        "apps.worker.tasks.recapture",
        "apps.worker.tasks.analytics",
    ],
)

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# ---------------------------------------------------------------------------
# Beat Schedule
# ---------------------------------------------------------------------------

app.conf.beat_schedule = {
    "detect-recapture-opportunities": {
        "task": "apps.worker.tasks.recapture.detect_opportunities",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "send-campaign-messages": {
        "task": "apps.worker.tasks.campaigns.send_due_messages",
        "schedule": crontab(minute="*"),  # Every minute
    },
    "aggregate-analytics": {
        "task": "apps.worker.tasks.analytics.aggregate_daily",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
    "check-recalls": {
        "task": "apps.worker.tasks.recapture.check_recalls",
        "schedule": crontab(hour=6, minute=0),  # 6 AM daily
    },
}

if __name__ == "__main__":
    app.start()
