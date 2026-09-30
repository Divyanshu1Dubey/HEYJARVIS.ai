"""
Shared constants for the HeyJarvis system.
"""


# Tenant
DEFAULT_TENANT_SLUG = "default"

# Pagination
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100

# Frequency caps (defaults, overridable per tenant)
DEFAULT_MAX_MESSAGES_PER_DAY = 3
DEFAULT_MAX_MESSAGES_PER_WEEK = 10
DEFAULT_COOLDOWN_HOURS = 24

# Campaign
DEFAULT_MAX_CAMPAIGN_ATTEMPTS = 3
DEFAULT_ATTEMPT_INTERVAL_HOURS = 24

# Safety
EMERGENCY_KEYWORDS = [
    "emergency",
    "urgent",
    "bleeding",
    "swelling",
    "broken tooth",
    "knocked out",
    "tooth fell out",
    "unbearable pain",
    "can't breathe",
    "difficulty breathing",
    "severe pain",
    "abscess",
    "fever",
    "pus",
]

MEDICAL_ADVICE_TRIGGERS = [
    "diagnose",
    "diagnosis",
    "prescribe",
    "medication",
    "treatment plan",
    "what should i do",
    "is this serious",
    "how serious",
    "am i okay",
    "what does this mean",
]

# Opt-out keywords (SMS)
SMS_OPT_OUT_KEYWORDS = ["stop", "stopall", "unsubscribe", "cancel", "end", "quit"]
SMS_OPT_IN_KEYWORDS = ["start", "yes", "unstop"]

# Rate limiting
LLM_REQUESTS_PER_MINUTE = 60
LLM_TOKENS_PER_MINUTE = 100000

# Timeouts (seconds)
LLM_TIMEOUT = 30
TOOL_CALL_TIMEOUT = 10
SCHEDULING_API_TIMEOUT = 5
SMS_TIMEOUT = 10
EMAIL_TIMEOUT = 10

# Booking hold duration (seconds)
APPOINTMENT_HOLD_DURATION = 300  # 5 minutes

# Message limits
MAX_MESSAGE_LENGTH = 5000
MAX_CONVERSATION_TURNS = 50

# Security
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Database
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30

# Redis
REDOM_KEY_PREFIX = "hj:"
REDIS_TTL_SHORT = 300  # 5 minutes
REDIS_TTL_MEDIUM = 3600  # 1 hour
REDIS_TTL_LONG = 86400  # 24 hours

# Event types
EVENT_TYPES = {
    "lead.created",
    "lead.contacted",
    "conversation.started",
    "conversation.abandoned",
    "appointment.offered",
    "appointment.booked",
    "appointment.cancelled",
    "appointment.no_show",
    "appointment.completed",
    "treatment_plan.created",
    "treatment_plan.accepted",
    "treatment_plan.unscheduled",
    "recall.due",
    "patient.inactive",
    "message.sent",
    "message.delivered",
    "message.failed",
    "message.replied",
    "patient.opted_out",
    "human_handoff.created",
    "safety.escalation",
    "campaign.started",
    "campaign.attempt_sent",
}

# Supported languages
SUPPORTED_LANGUAGES = ["en", "es"]

# Default timezone
DEFAULT_TIMEZONE = "America/New_York"

# Business hours (default, overridable per clinic)
DEFAULT_BUSINESS_HOURS = {
    "monday": {"open": "08:00", "close": "17:00"},
    "tuesday": {"open": "08:00", "close": "17:00"},
    "wednesday": {"open": "08:00", "close": "17:00"},
    "thursday": {"open": "08:00", "close": "17:00"},
    "friday": {"open": "08:00", "close": "17:00"},
    "saturday": {"open": "09:00", "close": "13:00"},
    "sunday": None,
}
