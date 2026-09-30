"""
HeyJarvis Shared Package
========================
Shared models, constants, and utilities.
"""

from .models import (
    # Enums
    PatientState, IntentType, SafetyLevel, ChannelType, MessageDirection,
    ConsentType, ConsentMethod, UserRole, TenantStatus, HandoffReason,
    CampaignStatus, AttemptStatus, AppointmentStatus, CancellationReason,
    EventType,
    # Base models
    HJBaseModel, TimestampedModel, IDModel,
    # Entity models
    Tenant, User, Clinic, Patient, Consent, CommunicationPreferences,
    Conversation, Message, Appointment, TreatmentPlan, TreatmentPlanItem,
    Campaign, CampaignAttempt, HumanHandoff, AuditLog, AIDecision, Event,
)
from .constants import (
    DEFAULT_TENANT_SLIDDEN,
    DEFAULT_MAX_MESSAGES_PER_DAY,
    DEFAULT_MAX_MESSAGES_PER_WEEK,
    DEFAULT_COOLDOWN_HOURS,
    EMERGENCY_KEYWORDS,
    MEDICAL_ADVICE_TRIGGERS,
    SMS_OPT_OUT_KEYWORDS,
    SMS_OPT_IN_KEYWORDS,
)
from .database import get_db, init_db, drop_all_tables, reset_db
from .events import EventBus, HJEvent, EventDefinitions
from .integrations import (
    ProviderFactory,
    BaseSchedulingProvider,
    BaseInsuranceProvider,
    MockSchedulingProvider,
    MockInsuranceProvider,
)
from .communication import (
    get_communication_provider,
    BaseCommunicationProvider,
    MockCommunicationProvider,
    MessageResult,
)
from .demo_data import seed_demo_data, get_demo_tenant, get_demo_clinic, get_demo_summary

__all__ = [
    # Models
    "PatientState", "IntentType", "SafetyLevel", "ChannelType", "MessageDirection",
    "ConsentType", "ConsentMethod", "UserRole", "TenantStatus", "HandoffReason",
    "CampaignStatus", "AttemptStatus", "AppointmentStatus", "CancellationReason", "EventType",
    "HJBaseModel", "TimestampedModel", "IDModel",
    "Tenant", "User", "Clinic", "Patient", "Consent", "CommunicationPreferences",
    "Conversation", "Message", "Appointment", "TreatmentPlan", "TreatmentPlanItem",
    "Campaign", "CampaignAttempt", "HumanHandoff", "AuditLog", "AIDecision", "Event",
    # Constants
    "DEFAULT_MAX_MESSAGES_PER_DAY", "DEFAULT_MAX_MESSAGES_PER_WEEK", "DEFAULT_COOLDOWN_HOURS",
    "EMERGENCY_KEYWORDS", "MEDICAL_ADVICE_TRIGGERS", "SMS_OPT_OUT_KEYWORDS", "SMS_OPT_IN_KEYWORDS",
    # Database
    "get_db", "init_db", "drop_all_tables", "reset_db",
    # Events
    "EventBus", "HJEvent", "EventDefinitions",
    # Integrations
    "ProviderFactory", "BaseSchedulingProvider", "BaseInsuranceProvider",
    "MockSchedulingProvider", "MockInsuranceProvider",
    # Communication
    "get_communication_provider", "BaseCommunicationProvider", "MockCommunicationProvider", "MessageResult",
    # Demo data
    "seed_demo_data", "get_demo_tenant", "get_demo_clinic", "get_demo_summary",
]
