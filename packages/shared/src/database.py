"""
HeyJarvis Database Setup
========================
Database initialization, session management, and seeding.

Supports:
  - PostgreSQL with SQLAlchemy 2.0
  - Row-Level Security (RLS)
  - Alembic migrations
  - Demo data seeding
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from sqlalchemy.pool import NullPool

from shared.models import (
    Tenant, User, Clinic, Patient, Consent, CommunicationPreferences,
    Conversation, Message, Appointment, TreatmentPlan, TreatmentPlanItem,
    Campaign, CampaignAttempt, HumanHandoff, AuditLog, AIDecision,
)

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://heyjarvis:heyjarvis_dev@localhost:5432/heyjarvis",
)

# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Context Manager
# ---------------------------------------------------------------------------

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a raw session (use with FastAPI Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all tables."""
    # Import all models so they're registered with SQLAlchemy
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """Drop all tables (DANGEROUS — only for testing)."""
    Base.metadata.drop_all(bind=engine)


def reset_db() -> None:
    """Drop and recreate all tables."""
    drop_all_tables()
    init_db()


# ---------------------------------------------------------------------------
# RLS Setup
# ---------------------------------------------------------------------------

def enable_rls(connection) -> None:
    """
    Enable Row-Level Security on all tenant-scoped tables.
    This ensures tenants can only see their own data.
    """
    tables = [
        "users", "clinics", "patients", "consents",
        "communication_preferences", "conversations", "messages",
        "appointments", "treatment_plans", "treatment_plan_items",
        "campaigns", "campaign_attempts", "human_handoffs",
        "ai_decisions",
    ]

    for table in tables:
        connection.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))

        # Policy: tenant can only see their own rows
        connection.execute(text(f"""
            CREATE POLICY tenant_isolation ON {table}
            FOR ALL
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
        """))

    connection.commit()


def set_tenant_context(connection, tenant_id: str) -> None:
    """Set the tenant context for RLS."""
    connection.execute(text(f"SET app.current_tenant_id = '{tenant_id}'"))


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def seed_demo_data() -> None:
    """Populate the database with demo data."""
    from shared.demo_data import seed_demo_data as get_demo_data
    from datetime import datetime, timezone

    with get_db() as db:
        # Seed tenants and clinics
        demo_data = get_demo_data()

        for tenant_data in demo_data["tenants"]:
            tenant = Tenant(**tenant_data)
            db.add(tenant)

        for clinic_data in demo_data["clinics"]:
            clinic = Clinic(**clinic_data)
            db.add(clinic)

        for user_data in demo_data["users"]:
            user = User(
                **user_data,
                password_hash=None,  # Demo — no password
            )
            db.add(user)

        # Seed patients
        for p in demo_data["patients"]:
            patient = Patient(**p)
            db.add(patient)

        # Seed consents
        for c in demo_data["consents"]:
            consent = Consent(**c)
            db.add(consent)

        # Seed communication preferences
        for cp in demo_data["communication_preferences"]:
            prefs = CommunicationPreferences(**cp)
            db.add(prefs)

        # Seed appointments
        for apt in demo_data["appointments"]:
            appointment = Appointment(**apt)
            db.add(appointment)

        # Seed conversations
        for conv in demo_data["conversations"]:
            conversation = Conversation(**conv)
            db.add(conversation)

        # Seed messages
        for msg in demo_data["messages"]:
            message = Message(**msg)
            db.add(message)

        # Seed recapture opportunities
        for opp in demo_data["recapture_opportunities"]:
            db.add(opp)

        # Seed campaigns
        for camp in demo_data["campaigns"]:
            campaign = Campaign(**camp)
            db.add(campaign)

        db.commit()

    print("Demo data seeded successfully!")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Tables created.")

    # Seed demo data
    seed_demo_data()
    print("Done! Run: uvicorn apps.api.main:app --reload")
