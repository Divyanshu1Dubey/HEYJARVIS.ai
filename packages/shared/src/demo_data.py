"""
HeyJarvis Mock Data & Demo Clinic
==================================
Provides demo data for development and demonstration purposes.
Includes a fully seeded demo clinic with realistic patients, appointments,
conversations, treatment plans, and recapture opportunities.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from shared.models import (
    # Core models
    PatientState, ChannelType, ConsentType, ConsentMethod,
    AppointmentStatus, CancellationReason, CampaignStatus,
    UserRole, TenantStatus, CommunicationPreferences,
    # Event types
    EventType,
)

# =============================================================================
# Demo Clinic Configuration
# =============================================================================

DEMO_CLINIC = {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "Bright Smile Dental",
    "address": "123 Main Street, Suite 100",
    "city": "Austin",
    "state": "TX",
    "zip": "78701",
    "phone": "(512) 555-0142",
    "email": "info@brightsmile.example.com",
    "timezone": "America/Chicago",
    "business_hours": {
        "monday": {"open": "08:00", "close": "17:00"},
        "tuesday": {"open": "08:00", "close": "17:00"},
        "wednesday": {"open": "08:00", "close": "17:00"},
        "thursday": {"open": "08:00", "close": "17:00"},
        "friday": {"open": "08:00", "close": "16:00"},
        "saturday": {"open": "09:00", "close": "13:00"},
        "sunday": None,
    },
}

DEMO_TENANT = {
    "id": "00000000-0000-0000-0000-000000000001",
    "name": "Bright Smile Dental Group",
    "slug": "bright-smile",
    "status": TenantStatus.ACTIVE,
    "settings": {
        "default_channel": ChannelType.SMS.value,
        "enable_web_chat": True,
        "enable_sms": True,
        "enable_email": True,
        "enable_voice": False,
        "enable_whatsapp": False,
        "ai_autopilot": False,  # Human review required
        "require_confirmation_for_booking": True,
        "max_ai_confidence_for_autonomous_action": 0.85,
    },
}

DEMO_ADMIN = {
    "id": "22222222-2222-2222-2222-222222222222",
    "email": "admin@brightsmile.example.com",
    "first_name": "Dr. Sarah",
    "last_name": "Mitchell",
    "role": UserRole.OWNER,
}

DEMO_STAFF = {
    "id": "33333333-3333-3333-3333-333333333333",
    "email": "staff@brightsmile.example.com",
    "first_name": "Maria",
    "last_name": "Gonzalez",
    "role": UserRole.STAFF,
}


# =============================================================================
# Demo Providers
# =============================================================================

DEMO_PROVIDERS = [
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "name": "Dr. Sarah Mitchell",
        "specialty": "General Dentistry",
        "npi": "1234567890",
        "is_active": True,
    },
    {
        "id": "55555555-5555-5555-5555-555555555555",
        "name": "Dr. James Chen",
        "specialty": "Orthodontics",
        "npi": "0987654321",
        "is_active": True,
    },
]


# =============================================================================
# Demo Services
# =============================================================================

DEMO_SERVICES = [
    {"id": "66666666-6666-6666-6666-666666666661", "name": "Dental Cleaning", "duration_minutes": 30, "category": "preventive"},
    {"id": "66666666-6666-6666-6666-666666666662", "name": "Dental Exam", "duration_minutes": 30, "category": "preventive"},
    {"id": "66666666-6666-6666-6666-666666666663", "name": "Crown / Cap", "duration_minutes": 60, "category": "restorative"},
    {"id": "66666666-6666-6666-6666-666666666664", "name": "Root Canal", "duration_minutes": 90, "category": "endodontic"},
    {"id": "66666666-6666-6666-6666-666666666665", "name": "Tooth Extraction", "duration_minutes": 45, "category": "oral_surgery"},
    {"id": "66666666-6666-6666-6666-666666666666", "name": "Teeth Whitening", "duration_minutes": 60, "category": "cosmetic"},
    {"id": "66666666-6666-6666-6666-666666666667", "name": "Implant Consultation", "duration_minutes": 45, "category": "implant"},
    {"id": "66666666-6666-6666-6666-666666666668", "name": "Emergency Visit", "duration_minutes": 30, "category": "emergency"},
]


# =============================================================================
# Demo Patients
# =============================================================================

def _patient_id(index: int) -> str:
    return str(uuid.UUID(int=index, version=4)).replace("-", "")[:36]

def _make_patients() -> list[dict[str, Any]]:
    """Generate demo patients across different recapture categories."""
    now = datetime.utcnow()
    base_time = now - timedelta(days=30)

    patients = [
        # ── LEAD RECAPTURE ─────────────────────────────────────────────
        {
            "id": _patient_id(0x1001),
            "first_name": "James",
            "last_name": "Wilson",
            "phone": "+1-512-555-0101",
            "email": "james.wilson@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.LEAD_ABANDONED,
            "recapture_category": "lead_abandoned",
            "recapture_reason": "Submitted contact form but never booked",
            "lead_created_at": base_time - timedelta(days=14),
            "last_contact_at": None,
            "notes": "Interested in teeth whitening. Submitted form at 10pm.",
            "appointment_value": 300.00,
        },
        {
            "id": _patient_id(0x1002),
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "phone": "+1-512-555-0102",
            "email": "emily.r@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.LEAD_ABANDONED,
            "recapture_category": "web_chat_abandoned",
            "recapture_reason": "Started web chat about implants, disconnected",
            "lead_created_at": base_time - timedelta(days=7),
            "last_contact_at": None,
            "notes": "Asked about implant costs. Chat disconnected mid-conversation.",
            "appointment_value": 3500.00,
        },
        {
            "id": _patient_id(0x1003),
            "first_name": "Michael",
            "last_name": "Thompson",
            "phone": "+1-512-555-0103",
            "email": "mthompson@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.NO_RESPONSE,
            "recapture_category": "missed_call",
            "recapture_reason": "Called after hours, left message, never returned",
            "lead_created_at": base_time - timedelta(days=5),
            "last_contact_at": None,
            "notes": "Left voicemail about emergency tooth pain.",
            "appointment_value": 200.00,
        },

        # ── CANCELLATION RECAPTURE ─────────────────────────────────────
        {
            "id": _patient_id(0x2001),
            "first_name": "Sarah",
            "last_name": "Johnson",
            "phone": "+1-512-555-0201",
            "email": "sarah.j@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.CANCELLED,
            "recapture_category": "cancelled_scheduling",
            "recapture_reason": "Cancelled due to work meeting conflict",
            "lead_created_at": base_time - timedelta(days=20),
            "last_contact_at": now - timedelta(days=3),
            "notes": "Wants to reschedule cleaning. Available weekday mornings.",
            "appointment_value": 150.00,
        },
        {
            "id": _patient_id(0x2002),
            "first_name": "David",
            "last_name": "Martinez",
            "phone": "+1-512-555-0202",
            "email": "dmartinez@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.CANCELLED,
            "recapture_category": "cancelled_price",
            "recapture_reason": "Cancelled crown appointment due to cost concern",
            "lead_created_at": base_time - timedelta(days=25),
            "last_contact_at": None,
            "notes": "Has Delta Dental. May need payment plan discussion.",
            "appointment_value": 1200.00,
        },
        {
            "id": _patient_id(0x2003),
            "first_name": "Lisa",
            "last_name": "Anderson",
            "phone": "+1-512-555-0203",
            "email": "lisa.a@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.CANCELLED,
            "recapture_category": "cancelled_fear",
            "recapture_reason": "Cancelled root canal due to anxiety",
            "lead_created_at": base_time - timedelta(days=10),
            "last_contact_at": None,
            "notes": "Very nervous about dental work. Needs sedation discussion.",
            "appointment_value": 1500.00,
        },

        # ── NO-SHOW RECAPTURE ──────────────────────────────────────────
        {
            "id": _patient_id(0x3001),
            "first_name": "Robert",
            "last_name": "Taylor",
            "phone": "+1-512-555-0301",
            "email": "rtaylor@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.NO_SHOW,
            "recapture_category": "first_no_show",
            "recapture_reason": "No-showed for first visit, never rebooked",
            "lead_created_at": base_time - timedelta(days=18),
            "last_contact_at": None,
            "notes": "Forgot appointment. Responsive to SMS.",
            "appointment_value": 150.00,
        },
        {
            "id": _patient_id(0x3002),
            "first_name": "Jennifer",
            "last_name": "Brown",
            "phone": "+1-512-555-0302",
            "email": "jbrown@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.NO_SHOW,
            "recapture_category": "repeat_no_show",
            "recapture_reason": "Second no-show, needs personal outreach",
            "lead_created_at": base_time - timedelta(days=35),
            "last_contact_at": None,
            "notes": "Transportation issues. Needs phone call from staff.",
            "appointment_value": 150.00,
        },

        # ── TREATMENT RECAPTURE ────────────────────────────────────────
        {
            "id": _patient_id(0x4001),
            "first_name": "William",
            "last_name": "Davis",
            "phone": "+1-512-555-0401",
            "email": "wdavis@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.TREATMENT_UNSCHEDULED,
            "recapture_category": "treatment_plan_created",
            "recapture_reason": "Treatment plan accepted but crown not scheduled",
            "lead_created_at": base_time - timedelta(days=30),
            "last_contact_at": None,
            "notes": "Needs crown on #30. Estimate $1,200. Has Aetna.",
            "appointment_value": 1200.00,
        },
        {
            "id": _patient_id(0x4002),
            "first_name": "Amanda",
            "last_name": "White",
            "phone": "+1-512-555-0402",
            "email": "awhite@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.TREATMENT_UNSCHEDULED,
            "recapture_category": "treatment_plan_accepted",
            "recapture_reason": "Accepted treatment plan but never scheduled root canal",
            "lead_created_at": base_time - timedelta(days=45),
            "last_contact_at": None,
            "notes": "Experiencing pain. Needs urgent scheduling.",
            "appointment_value": 1500.00,
        },
        {
            "id": _patient_id(0x4003),
            "first_name": "Christopher",
            "last_name": "Lee",
            "phone": "+1-512-555-0403",
            "email": "clee@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.TREATMENT_UNSCHEDULED,
            "recapture_category": "multi_visit_stalled",
            "recapture_reason": "Partial treatment completed, remaining visits not scheduled",
            "lead_created_at": base_time - timedelta(days=60),
            "last_contact_at": None,
            "notes": "Had first root canal session. Needs second session scheduled.",
            "appointment_value": 800.00,
        },

        # ── RECALL / REACTIVATION ──────────────────────────────────────
        {
            "id": _patient_id(0x5001),
            "first_name": "Jessica",
            "last_name": "Garcia",
            "phone": "+1-512-555-0501",
            "email": "jgarcia@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.RECALL_DUE,
            "recapture_category": "hygiene_recall_overdue",
            "recapture_reason": "6 months overdue for hygiene recall",
            "lead_created_at": base_time - timedelta(days=180),
            "last_contact_at": None,
            "notes": "Regular patient. Last cleaning was 6 months ago.",
            "appointment_value": 150.00,
        },
        {
            "id": _patient_id(0x5002),
            "first_name": "Daniel",
            "last_name": "Martinez",
            "phone": "+1-512-555-0502",
            "email": "dmartinez2@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.INACTIVE,
            "recapture_category": "inactive_patient",
            "recapture_reason": "No visit in 18 months",
            "lead_created_at": base_time - timedelta(days=540),
            "last_contact_at": None,
            "notes": "Former regular patient. Moved to different area.",
            "appointment_value": 200.00,
        },
        {
            "id": _patient_id(0x5003),
            "first_name": "Ashley",
            "last_name": "Robinson",
            "phone": "+1-512-555-0503",
            "email": "arobinson@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.RECALL_DUE,
            "recapture_category": "periodic_exam_overdue",
            "recapture_reason": "12 month exam overdue",
            "lead_created_at": base_time - timedelta(days=365),
            "last_contact_at": None,
            "notes": "Needs X-rays and exam. Has Cigna dental.",
            "appointment_value": 175.00,
        },

        # ── BOOKING RECAPTURE ──────────────────────────────────────────
        {
            "id": _patient_id(0x6001),
            "first_name": "Kevin",
            "last_name": "Clark",
            "phone": "+1-512-555-0601",
            "email": "kclark@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.BOOKING_PENDING,
            "recapture_category": "booking_flow_abandoned",
            "recapture_reason": "Selected time slot but never confirmed booking",
            "lead_created_at": base_time - timedelta(days=2),
            "last_contact_at": None,
            "notes": "Selected Friday 3pm slot for cleaning. Slot expired.",
            "appointment_value": 150.00,
        },
        {
            "id": _patient_id(0x6002),
            "first_name": "Michelle",
            "last_name": "Lewis",
            "phone": "+1-512-555-0602",
            "email": "mlewis@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.BOOKING_PENDING,
            "recapture_category": "patient_hesitant",
            "recapture_reason": "Said 'I'll think about it' for implant consultation",
            "lead_created_at": base_time - timedelta(days=5),
            "last_contact_at": None,
            "notes": "Needs financing information before committing.",
            "appointment_value": 3500.00,
        },

        # ── POST-VISIT OPPORTUNITIES ───────────────────────────────────
        {
            "id": _patient_id(0x7001),
            "first_name": "Brian",
            "last_name": "Walker",
            "phone": "+1-512-555-0701",
            "email": "bwalker@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.COMPLETED,
            "recapture_category": "post_visit_follow_up",
            "recapture_reason": "Recent cleaning, discuss whitening option",
            "lead_created_at": base_time - timedelta(days=1),
            "last_contact_at": None,
            "notes": "Dentist mentioned whitening during visit. Patient interested.",
            "appointment_value": 300.00,
        },

        # ── INSURANCE / FINANCIAL ──────────────────────────────────────
        {
            "id": _patient_id(0x8001),
            "first_name": "Rachel",
            "last_name": "Harris",
            "phone": "+1-512-555-0801",
            "email": "rharris@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.BOOKING_PENDING,
            "recapture_category": "insurance_question",
            "recapture_reason": "Asked about insurance coverage, no response",
            "lead_created_at": base_time - timedelta(days=4),
            "last_contact_at": None,
            "notes": "Has MetLife. Needs benefit verification for crown.",
            "appointment_value": 1200.00,
        },

        # ── AFTER-HOURS / MISSED OPPORTUNITIES ─────────────────────────
        {
            "id": _patient_id(0x9001),
            "first_name": "Steven",
            "last_name": "King",
            "phone": "+1-512-555-0901",
            "email": "sking@example.com",
            "timezone": "America/Chicago",
            "state": PatientState.LEAD_ABANDONED,
            "recapture_category": "after_hours_lead",
            "recapture_reason": "Submitted form at 9pm, no one responded until morning",
            "lead_created_at": base_time - timedelta(days=1),
            "last_contact_at": None,
            "notes": "Requested Saturday appointment for emergency.",
            "appointment_value": 200.00,
        },
    ]

    # Add timestamps
    for p in patients:
        p["tenant_id"] = DEMO_TENANT["id"]
        p["clinic_id"] = DEMO_CLINIC["id"]
        p["created_at"] = base_time - timedelta(days=30)
        p["updated_at"] = p.get("last_contact_at") or p["created_at"]

    return patients


def _make_consents() -> list[dict[str, Any]]:
    """Generate demo consents for all patients."""
    patients = _make_patients()
    consents = []
    now = datetime.utcnow()

    for p in patients:
        # SMS consent
        consents.append({
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "patient_id": p["id"],
            "consent_type": ConsentType.SMS,
            "method": ConsentMethod.VERBAL_DIGITAL,
            "granted": True,
            "granted_at": p["created_at"],
            "revoked_at": None,
            "ip_address": "192.168.1.1",
            "user_agent": "Demo/1.0",
        })
        # Email consent
        if p.get("email"):
            consents.append({
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT["id"],
                "patient_id": p["id"],
                "consent_type": ConsentType.EMAIL,
                "method": ConsentMethod.ONLINE_FORM,
                "granted": True,
                "granted_at": p["created_at"],
                "revoked_at": None,
                "ip_address": "192.168.1.1",
                "user_agent": "Demo/1.0",
            })

    return consents


def _make_comm_prefs() -> list[dict[str, Any]]:
    """Generate demo communication preferences."""
    patients = _make_patients()
    prefs = []

    for p in patients:
        prefs.append({
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "patient_id": p["id"],
            "channel": ChannelType.SMS,
            "enabled": True,
            "quiet_hours_start": "21:00",
            "quiet_hours_end": "08:00",
            "max_messages_per_day": 3,
            "max_messages_per_week": 10,
            "preferred_language": "en",
            "do_not_contact": False,
        })

    return prefs


def _make_appointments() -> list[dict[str, Any]]:
    """Generate demo appointments (past cancelled/no-show + upcoming)."""
    patients = _make_patients()
    now = datetime.utcnow()
    appointments = []

    # Cancelled appointments
    for p in patients:
        if p["state"] in (PatientState.CANCELLED, PatientState.NO_SHOW):
            past = now - timedelta(days=7)
            appointments.append({
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT["id"],
                "clinic_id": DEMO_CLINIC["id"],
                "patient_id": p["id"],
                "provider_id": DEMO_PROVIDERS[0]["id"],
                "appointment_type": "Dental Cleaning",
                "scheduled_at": past,
                "duration_minutes": 30,
                "status": AppointmentStatus.CANCELLED if p["state"] == PatientState.CANCELLED else AppointmentStatus.NO_SHOW,
                "cancellation_reason": CancellationReason.SCHEDULING_CONFLICT if p["state"] == PatientState.CANCELLED else None,
                "source": "system",
            })

    # Upcoming appointments (for active patients)
    for i, p in enumerate(patients[:3]):
        future = now + timedelta(days=i + 1, hours=14)
        appointments.append({
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "clinic_id": DEMO_CLINIC["id"],
            "patient_id": p["id"],
            "provider_id": DEMO_PROVIDERS[0]["id"],
            "appointment_type": "Dental Cleaning",
            "scheduled_at": future,
            "duration_minutes": 30,
            "status": AppointmentStatus.SCHEDULED,
            "source": "system",
        })

    return appointments


def _make_treatment_plans() -> list[dict[str, Any]]:
    """Generate demo treatment plans."""
    patients = _make_patients()
    now = datetime.utcnow()
    plans = []

    for p in patients:
        if p["state"] == PatientState.TREATMENT_UNSCHEDULED:
            plans.append({
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT["id"],
                "clinic_id": DEMO_CLINIC["id"],
                "patient_id": p["id"],
                "provider_id": DEMO_PROVIDERS[0]["id"],
                "status": "accepted" if "accepted" in p.get("recapture_reason", "") else "proposed",
                "total_estimated_cost": p.get("appointment_value", 0),
                "accepted_at": now - timedelta(days=14) if "accepted" in p.get("recapture_reason", "") else None,
                "created_at": now - timedelta(days=21),
            })

    return plans


def _make_conversations() -> list[dict[str, Any]]:
    """Generate demo conversations."""
    patients = _make_patients()
    now = datetime.utcnow()
    conversations = []

    for p in patients[:5]:  # Just a few demo conversations
        conversations.append({
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "clinic_id": DEMO_CLINIC["id"],
            "patient_id": p["id"],
            "channel": ChannelType.SMS,
            "state": p["state"],
            "started_at": now - timedelta(days=3),
            "last_patient_message_at": now - timedelta(hours=2),
            "last_ai_message_at": now - timedelta(hours=2),
            "ai_handled": True,
            "context": {"recapture_category": p.get("recapture_category")},
        })

    return conversations


def _make_messages() -> list[dict[str, Any]]:
    """Generate demo messages."""
    messages = []
    conversations = _make_conversations()
    now = datetime.utcnow()

    # Demo message exchanges
    sample_exchanges = [
        {
            "patient_msg": "Hi, I submitted a form about teeth whitening but never heard back.",
            "ai_msg": "Hi! Welcome to Bright Smile Dental. Thanks for reaching out about teeth whitening! We have openings this week. Would you like me to check availability?",
        },
        {
            "patient_msg": "I need to cancel my appointment, too expensive.",
            "ai_msg": "I understand cost is a concern. We offer several payment options including CareCredit and in-house payment plans. Let me connect you with our billing team to discuss options that work for you.",
        },
        {
            "patient_msg": "I broke my tooth and have a wedding Saturday.",
            "ai_msg": "I'm sorry about your tooth! We can see you today. We accept Delta Dental — Mission can see you today at 3:20 PM, well before Saturday. Would you like me to book that for you?",
        },
    ]

    for i, conv in enumerate(conversations):
        if i < len(sample_exchanges):
            exchange = sample_exchanges[i]
            messages.append({
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT["id"],
                "conversation_id": conv["id"],
                "patient_id": conv["patient_id"],
                "direction": "inbound",
                "channel": ChannelType.SMS,
                "body": exchange["patient_msg"],
                "sent_at": now - timedelta(hours=3),
            })
            messages.append({
                "id": str(uuid.uuid4()),
                "tenant_id": DEMO_TENANT["id"],
                "conversation_id": conv["id"],
                "patient_id": conv["patient_id"],
                "direction": "outbound",
                "channel": ChannelType.SMS,
                "body": exchange["ai_msg"],
                "sent_at": now - timedelta(hours=3, minutes=-1),
            })

    return messages


def _make_recapture_opportunities() -> list[dict[str, Any]]:
    """Generate demo recapture opportunities from patients."""
    patients = _make_patients()
    now = datetime.utcnow()
    opportunities = []

    for p in patients:
        opportunities.append({
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "clinic_id": DEMO_CLINIC["id"],
            "patient_id": p["id"],
            "recapture_type": p.get("recapture_category", "unknown"),
            "reason": p.get("recapture_reason", ""),
            "state": p["state"],
            "priority_score": 50.0,
            "conversion_probability": 0.3,
            "recommended_channel": ChannelType.SMS.value,
            "appointment_value": p.get("appointment_value", 0),
            "detected_at": p.get("lead_created_at", now),
            "last_attempt_at": None,
            "attempt_count": 0,
            "status": "pending",
            "metadata": {
                "notes": p.get("notes", ""),
            },
        })

    return opportunities


def _make_campaigns() -> list[dict[str, Any]]:
    """Generate demo campaigns."""
    now = datetime.utcnow()
    return [
        {
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "clinic_id": DEMO_CLINIC["id"],
            "name": "Abandoned Lead Recovery",
            "description": "Re-engage patients who submitted forms but never booked",
            "recapture_type": "lead_abandoned",
            "status": CampaignStatus.ACTIVE,
            "is_active": True,
            "max_attempts": 3,
            "cooldown_hours": 24,
            "daily_cap": 50,
            "start_at": now - timedelta(days=7),
            "end_at": None,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "clinic_id": DEMO_CLINIC["id"],
            "name": "Cancellation Recovery",
            "description": "Recover cancelled appointments with reschedule offers",
            "recapture_type": "cancelled",
            "status": CampaignStatus.ACTIVE,
            "is_active": True,
            "max_attempts": 2,
            "cooldown_hours": 48,
            "daily_cap": 30,
            "start_at": now - timedelta(days=3),
            "end_at": None,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "clinic_id": DEMO_CLINIC["id"],
            "name": "No-Show Recovery",
            "description": "Re-engage patients who missed appointments",
            "recapture_type": "no_show",
            "status": CampaignStatus.ACTIVE,
            "is_active": True,
            "max_attempts": 3,
            "cooldown_hours": 24,
            "daily_cap": 30,
            "start_at": now - timedelta(days=5),
            "end_at": None,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "clinic_id": DEMO_CLINIC["id"],
            "name": "Treatment Plan Follow-Up",
            "description": "Follow up on accepted treatment plans not yet scheduled",
            "recapture_type": "treatment_unscheduled",
            "status": CampaignStatus.ACTIVE,
            "is_active": True,
            "max_attempts": 2,
            "cooldown_hours": 72,
            "daily_cap": 20,
            "start_at": now - timedelta(days=10),
            "end_at": None,
        },
        {
            "id": str(uuid.uuid4()),
            "tenant_id": DEMO_TENANT["id"],
            "clinic_id": DEMO_CLINIC["id"],
            "name": "Hygiene Recall",
            "description": "Reactivate patients overdue for cleaning",
            "recapture_type": "recall_due",
            "status": CampaignStatus.ACTIVE,
            "is_active": True,
            "max_attempts": 2,
            "cooldown_hours": 168,  # 1 week
            "daily_cap": 40,
            "start_at": now - timedelta(days=14),
            "end_at": None,
        },
    ]


# =============================================================================
# Seed Function
# =============================================================================

def get_demo_tenant() -> dict[str, Any]:
    return DEMO_TENANT


def get_demo_clinic() -> dict[str, Any]:
    return DEMO_CLINIC


def get_demo_admin() -> dict[str, Any]:
    return DEMO_ADMIN


def get_demo_staff() -> dict[str, Any]:
    return DEMO_STAFF


def seed_demo_data() -> dict[str, list[dict[str, Any]]]:
    """
    Returns all demo data for seeding the database.
    Call this from your seed script or migration.
    """
    return {
        "tenants": [DEMO_TENANT],
        "clinics": [DEMO_CLINIC],
        "users": [DEMO_ADMIN, DEMO_STAFF],
        "providers": DEMO_PROVIDERS,
        "services": DEMO_SERVICES,
        "patients": _make_patients(),
        "consents": _make_consents(),
        "communication_preferences": _make_comm_prefs(),
        "appointments": _make_appointments(),
        "treatment_plans": _make_treatment_plans(),
        "conversations": _make_conversations(),
        "messages": _make_messages(),
        "recapture_opportunities": _make_recapture_opportunities(),
        "campaigns": _make_campaigns(),
    }


def get_demo_summary() -> dict[str, Any]:
    """Get a summary of the demo data for dashboard display."""
    patients = _make_patients()
    opportunities = _make_recapture_opportunities()

    categories: dict[str, int] = {}
    total_value = 0.0
    for p in patients:
        cat = p.get("recapture_category", "other")
        categories[cat] = categories.get(cat, 0) + 1
        total_value += p.get("appointment_value", 0)

    return {
        "clinic": DEMO_CLINIC["name"],
        "total_patients": len(patients),
        "total_opportunities": len(opportunities),
        "categories": categories,
        "total_potential_revenue": total_value,
        "avg_appointment_value": total_value / len(patients) if patients else 0,
    }
