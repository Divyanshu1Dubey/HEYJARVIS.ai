from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Any, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


# =============================================================================
# Enums
# =============================================================================

class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    ARCHIVED = "archived"


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    PROVIDER = "provider"
    READ_ONLY = "read_only"


class ChannelType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"
    WEB_CHAT = "web_chat"
    WHATSAPP = "whatsapp"
    PORTAL = "portal"


class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class ConsentType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"
    WHATSAPP = "whatsapp"


class ConsentMethod(str, Enum):
    SIGNED_FORM = "signed_form"
    ONLINE_FORM = "online_form"
    VERBAL_STAFF = "verbal_staff"
    VERBAL_DIGITAL = "verbal_digital"
    CHECKBOX = "checkbox"


class PatientState(str, Enum):
    NEW_LEAD = "new_lead"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    QUALIFIED = "qualified"
    BOOKING_PENDING = "booking_pending"
    BOOKED = "booked"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    LEAD_ABANDONED = "lead_abandoned"
    NO_RESPONSE = "no_response"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULE_PENDING = "reschedule_pending"
    TREATMENT_UNSCHEDULED = "treatment_unscheduled"
    RECALL_DUE = "recall_due"
    INACTIVE = "inactive"
    OPTED_OUT = "opted_out"
    DO_NOT_CONTACT = "do_not_contact"
    HUMAN_HANDOFF = "human_handoff"
    SAFETY_ESCALATION = "safety_escalation"
    INVALID_CONTACT = "invalid_contact"
    FAILED_DELIVERY = "failed_delivery"
    FAILED_INTEGRATION = "failed_integration"


class IntentType(str, Enum):
    BOOK_APPOINTMENT = "book_appointment"
    RESCHEDULE = "reschedule"
    CANCEL = "cancel"
    EMERGENCY = "emergency"
    INSURANCE_QUESTION = "insurance_question"
    PRICING_QUESTION = "pricing_question"
    SERVICE_QUESTION = "service_question"
    HOURS_QUESTION = "hours_question"
    LOCATION_QUESTION = "location_question"
    GENERAL_QUESTION = "general_question"
    HUMAN_HANDOFF = "human_handoff"
    OPT_OUT = "opt_out"
    UNKNOWN = "unknown"


class SafetyLevel(str, Enum):
    SAFE = "safe"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    PROHIBITED = "prohibited"


class HandoffReason(str, Enum):
    PATIENT_REQUESTED = "patient_requested"
    MEDICAL_QUESTION = "medical_question"
    EMERGENCY = "emergency"
    INSURANCE_DISPUTE = "insurance_dispute"
    COMPLAINT = "complaint"
    ANGRY_PATIENT = "angry_patient"
    LEGAL_THREAT = "legal_threat"
    PAYMENT_DISPUTE = "payment_dispute"
    LOW_CONFIDENCE = "low_confidence"
    INTEGRATION_FAILURE = "integration_failure"
    REPEATED_MISUNDERSTANDING = "repeated_misunderstanding"
    OUTSIDE_SCOPE = "outside_scope"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttemptStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    NO_RESPONSE = "no_response"
    PATIENT_REPLIED = "patient_replied"
    STOPPED = "stopped"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"
    IN_PROGRESS = "in_progress"


class CancellationReason(str, Enum):
    SCHEDULING_CONFLICT = "scheduling_conflict"
    PRICE = "price"
    INSURANCE = "insurance"
    FEAR_ANXIETY = "fear_anxiety"
    TRANSPORTATION = "transportation"
    TIMING = "timing"
    NO_EXPLANATION = "no_explanation"
    ILLNESS = "illness"
    WEATHER = "weather"
    OTHER = "other"


# =============================================================================
# Base Models
# =============================================================================

class HJBaseModel(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        extra="forbid",
    )


class TimestampedModel(HJBaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class IDModel(HJBaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


# =============================================================================
# Tenant
# =============================================================================

class Tenant(IDModel, TimestampedModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    status: TenantStatus = TenantStatus.ACTIVE
    settings: dict[str, Any] = Field(default_factory=dict)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        return re.sub(r"[^a-z0-9-]", "", v.lower())


# =============================================================================
# User / Staff
# =============================================================================

class User(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    email: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    role: UserRole = UserRole.STAFF
    is_active: bool = True
    last_login_at: Optional[datetime] = None
    password_hash: Optional[str] = None


# =============================================================================
# Clinic
# =============================================================================

class Clinic(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    name: str = Field(..., max_length=255)
    address_line1: str = Field(..., max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., max_length=20)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=255)
    timezone: str = Field(default="America/New_York")
    business_hours: dict[str, Any] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


# =============================================================================
# Patient
# =============================================================================

class Patient(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    clinic_id: uuid.UUID
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=20)
    timezone: str = Field(default="America/New_York")
    preferred_channel: Optional[ChannelType] = None
    state: PatientState = PatientState.NEW_LEAD
    last_contact_at: Optional[datetime] = None
    is_deleted: bool = False


# =============================================================================
# Consent
# =============================================================================

class Consent(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    patient_id: uuid.UUID
    consent_type: ConsentType
    method: ConsentMethod
    granted: bool
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    form_version: Optional[str] = None
    staff_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


# =============================================================================
# Communication Preferences
# =============================================================================

class CommunicationPreferences(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    patient_id: uuid.UUID
    channel: ChannelType
    enabled: bool = True
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    max_messages_per_day: int = Field(default=3, ge=0, le=20)
    max_messages_per_week: int = Field(default=10, ge=0, le=50)
    preferred_language: str = Field(default="en")
    do_not_contact: bool = False
    notes: Optional[str] = None


# =============================================================================
# Conversation
# =============================================================================

class Conversation(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    clinic_id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    channel: ChannelType
    state: PatientState = PatientState.NEW_LEAD
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    last_patient_message_at: Optional[datetime] = None
    last_ai_message_at: Optional[datetime] = None
    ai_handled: bool = False
    handoff_reason: Optional[HandoffReason] = None
    context: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Message
# =============================================================================

class Message(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    conversation_id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    direction: MessageDirection
    channel: ChannelType
    body: str = Field(..., max_length=5000)
    external_id: Optional[str] = None
    delivery_status: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Appointment
# =============================================================================

class Appointment(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    clinic_id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    provider_id: Optional[uuid.UUID] = None
    appointment_type: str = Field(..., max_length=100)
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=5, le=480)
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    cancellation_reason: Optional[CancellationReason] = None
    cancellation_notes: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    notes: Optional[str] = None
    external_id: Optional[str] = None
    source: str = Field(default="system")


# =============================================================================
# Treatment Plan
# =============================================================================

class TreatmentPlan(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    clinic_id: uuid.UUID
    patient_id: uuid.UUID
    provider_id: Optional[uuid.UUID] = None
    status: str = Field(default="proposed")
    total_estimated_cost: Optional[float] = None
    accepted_at: Optional[datetime] = None
    notes: Optional[str] = None


class TreatmentPlanItem(IDModel, TimestampedModel):
    treatment_plan_id: uuid.UUID
    tenant_id: uuid.UUID
    description: str = Field(..., max_length=500)
    tooth_number: Optional[str] = Field(None, max_length=10)
    estimated_cost: Optional[float] = None
    insurance_covered: Optional[float] = None
    patient_responsibility: Optional[float] = None
    status: str = Field(default="proposed")
    sort_order: int = Field(default=0)


# =============================================================================
# Campaign
# =============================================================================

class Campaign(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    clinic_id: uuid.UUID
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    recapture_type: str = Field(..., max_length=100)
    status: CampaignStatus = CampaignStatus.DRAFT
    is_active: bool = True
    max_attempts: int = Field(default=3, ge=1, le=10)
    cooldown_hours: int = Field(default=24, ge=0)
    daily_cap: int = Field(default=100, ge=1)
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    config: dict[str, Any] = Field(default_factory=dict)


class CampaignAttempt(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    campaign_id: uuid.UUID
    patient_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    attempt_number: int = Field(ge=1)
    status: AttemptStatus = AttemptStatus.PENDING
    channel: ChannelType
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    patient_replied_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Human Handoff
# =============================================================================

class HumanHandoff(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    clinic_id: uuid.UUID
    conversation_id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    assigned_to: Optional[uuid.UUID] = None
    reason: HandoffReason
    priority: str = Field(default="medium", pattern=r"^(low|medium|high|critical)$")
    status: str = Field(default="open")
    notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None


# =============================================================================
# Audit Log
# =============================================================================

class AuditLog(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    actor_type: str = Field(..., max_length=50)
    actor_id: Optional[uuid.UUID] = None
    action: str = Field(..., max_length=100)
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[uuid.UUID] = None
    changes: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# AI Decision
# =============================================================================

class AIDecision(IDModel, TimestampedModel):
    tenant_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None
    patient_id: Optional[uuid.UUID] = None
    decision_type: str = Field(..., max_length=100)
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    model_version: Optional[str] = None
    confidence: Optional[float] = None
    policy_override: bool = False
    executed: bool = False


# =============================================================================
# Event
# =============================================================================

class EventType(str, Enum):
    LEAD_CREATED = "lead.created"
    LEAD_CONTACTED = "lead.contacted"
    CONVERSATION_STARTED = "conversation.started"
    CONVERSATION_ABANDONED = "conversation.abandoned"
    APPOINTMENT_OFFERED = "appointment.offered"
    APPOINTMENT_BOOKED = "appointment.booked"
    APPOINTMENT_CANCELLED = "appointment.cancelled"
    APPOINTMENT_NO_SHOW = "appointment.no_show"
    APPOINTMENT_COMPLETED = "appointment.completed"
    TREATMENT_PLAN_CREATED = "treatment_plan.created"
    TREATMENT_PLAN_ACCEPTED = "treatment_plan.accepted"
    TREATMENT_PLAN_UNSCHEDULED = "treatment_plan.unscheduled"
    RECALL_DUE = "recall.due"
    PATIENT_INACTIVE = "patient.inactive"
    MESSAGE_SENT = "message.sent"
    MESSAGE_DELIVERED = "message.delivered"
    MESSAGE_FAILED = "message.failed"
    MESSAGE_REPLIED = "message.replied"
    PATIENT_OPTED_OUT = "patient.opted_out"
    HUMAN_HANDOFF_CREATED = "human_handoff.created"
    SAFETY_ESCALATION = "safety.escalation"
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_ATTEMPT_SENT = "campaign.attempt_sent"


class Event(HJBaseModel):
    event_type: EventType
    tenant_id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    conversation_id: Optional[uuid.UUID] = None
    appointment_id: Optional[uuid.UUID] = None
    campaign_id: Optional[uuid.UUID] = None
    correlation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(default="system")
    payload: dict[str, Any] = Field(default_factory=dict)
    security_classification: str = Field(default="phi")
    version: str = Field(default="1.0")
