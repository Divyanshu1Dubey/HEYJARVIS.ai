"""
HeyJarvis Worker — Analytics Tasks
=====================================
Analytics aggregation tasks.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def aggregate_daily():
    """Aggregate daily analytics."""
    logger.info("Aggregating daily analytics...")
    return {"status": "complete", "date": datetime.utcnow().isoformat()}


@shared_task
def generate_report(report_type: str, date_from: str, date_to: str) -> dict[str, Any]:
    """Generate an analytics report."""
    logger.info(f"Generating {report_type} report from {date_from} to {date_to}")
    return {
        "report_type": report_type,
        "date_from": date_from,
        "date_to": date_to,
        "generated_at": datetime.utcnow().isoformat(),
    }
