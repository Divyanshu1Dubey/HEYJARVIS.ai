# Recovery Decision Engine
## Deterministic Policy Layer

**Document:** 03 of 20  
**Purpose:** Defines the complete policy pipeline that determines whether a patient should receive outreach, before any AI or ML logic runs.

---

## 1. Core Principle

**The policy engine runs FIRST. It is the gatekeeper. No outreach happens without passing every policy check. The LLM never overrides any policy decision.**

The policy engine answers the question: **"Should we contact this patient right now?"**

If the answer is "no," the system does not contact the patient. No message is generated. No AI reasoning is invoked for outreach. The decision and its reason are logged for audit.

---

## 2. Policy Check Pipeline

Outreach is evaluated through a sequential pipeline of checks. If any check fails, outreach is denied and the process stops.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    OUTREACH REQUEST RECEIVED                         │
│              (from recapture engine, campaign, or AI)                │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 1: Patient State Valid?                                       │
│  Is the patient in a recapture-eligible state?                       │
│  ── FAIL → DENY (state_not_eligible)                                 │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 2: Opt-Out / DNC Status?                                      │
│  Has the patient opted out or is on do-not-contact?                  │
│  ── FAIL → DENY (opted_out)                                          │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 3: Channel Consent?                                           │
│  Does the patient have consent for the requested channel?            │
│  ── FAIL → DENY (no_consent) — try alternative channel              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 4: Frequency Cap?                                             │
│  Has the patient received too many messages recently?                │
│  ── FAIL → DENY (frequency_cap) — schedule for later                │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 5: Quiet Hours?                                               │
│  Is it within the patient's quiet hours?                             │
│  ── FAIL → DENY (quiet_hours) — schedule for after quiet period     │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 6: Business Hours?                                            │
│  Is the clinic open?                                                 │
│  ── FAIL → DENY (outside_business_hours) — schedule for next open   │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 7: Duplicate Suppression?                                     │
│  Has a similar outreach already been sent recently?                  │
│  ── FAIL → DENY (duplicate_suppression)                              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 8: Safety Check?                                              │
│  Does the patient's recent communication indicate a safety issue?     │
│  ── FAIL → ESCALATE (safety_escalation)                              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 9: Recapture Attempt Limit?                                   │
│  Has this patient exceeded max attempts for this recapture type?     │
│  ── FAIL → DENY (max_attempts_exceeded)                              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 10: Staff Override / Manual Suppression?                      │
│  Has staff suppressed outreach for this patient?                     │
│  ── FAIL → DENY (staff_suppressed)                                   │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CHECK 11: Tenant Configuration?                                     │
│  Does the clinic allow this type of outreach?                        │
│  ── FAIL → DENY (clinic_policy)                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ PASS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│              ✅ ALL CHECKS PASSED — OUTREACH APPROVED                │
│              Proceed to message generation and dispatch               │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Policy Check Details

### CHECK 1: Patient State Valid

**Purpose:** Ensure the patient is in a state that is eligible for outreach.

**Logic:**
```python
RECAPTURE_ELIGIBLE_STATES = {
    PatientState.LEAD_ABANDONED,
    PatientState.NO_RESPONSE,
    PatientState.CANCELLED,
    PatientState.NO_SHOW,
    PatientState.TREATMENT_UNSCHEDULED,
    PatientState.RESCHEDULE_PENDING,
    PatientState.RECALL_DUE,
    PatientState.INACTIVE,
    PatientState.LONG_TERM_INACTIVE,  # Limited
}

NON_ELIGIBLE_STATES = {
    PatientState.OPTED_OUT,
    PatientState.DO_NOT_CONTACT,
    PatientState.DEACTIVATED,
    PatientState.BOOKED,
    PatientState.CONFIRMED,
    PatientState.COMPLETED,
    PatientState.HUMAN_HANDOFF,
    PatientState.SAFETY_ESCALATION,
    PatientState.CAMPAIGN_ACTIVE,
}

def check_state_valid(patient) -> PolicyResult:
    if patient.state in NON_ELIGIBLE_STATES:
        return PolicyResult.DENY("patient_not_eligible", f"Patient is in {patient.state}")
    if patient.state not in RECAPTURE_ELIGIBLE_STATES:
        return PolicyResult.DENY("state_not_recapture_target", f"State {patient.state} is not a recapture target")
    return PolicyResult.PASS()
```

**Special cases:**
- `LONG_TERM_INACTIVE`: Requires fresh consent verification before outreach. If no recent consent, mark as `DENY` with reason `consent_expired`.
- `RESCHEDULE_PENDING`: Only reschedule-related messages allowed. No general outreach.

---

### CHECK 2: Opt-Out / DNC Status

**Purpose:** Ensure the patient has not requested to stop communications.

**Logic:**
```python
def check_opt_out(tenant_id, patient_id) -> PolicyResult:
    # Check global opt-out
    opt_out = db.query(OptOut).filter(
        OptOut.patient_id == patient_id,
        OptOut.tenant_id == tenant_id,
    ).first()

    if opt_out:
        if opt_out.channels:  # Partial opt-out
            return PolicyResult.DENY("opted_out", f"Patient opted out of: {opt_out.channels}")
        else:  # Full opt-out
            return PolicyResult.DENY("opted_out", "Patient opted out of all communications")

    # Check do-not-contact list
    dnc = db.query(DoNotContact).filter(
        DoNotContact.patient_id == patient_id,
        DoNotContact.tenant_id == tenant_id,
    ).first()

    if dnc:
        return PolicyResult.DENY("do_not_contact", f"DNC reason: {dnc.reason}")

    return PolicyResult.PASS()
```

**Opt-out keyword detection (SMS):**
```python
SMS_OPT_OUT_PATTERN = re.compile(r'\b(STOP|STOPALL|UNSUBSCRIBE|CANCEL|END|QUIT)\b', re.IGNORECASE)
SMS_OPT_IN_PATTERN = re.compile(r'\b(START|YES|UNSTOP)\b', re.IGNORECASE)

def process_incoming_sms(message_body):
    if SMS_OPT_OUT_PATTERN.search(message_body):
        # Immediately opt out patient
        create_opt_out(patient_id, reason="stop_keyword", channels=["sms"])
        publish(EventType.PATIENT_OPTED_OUT, ...)
        return OPT_OUT_ACTION
    elif SMS_OPT_IN_PATTERN.search(message_body):
        # Re-enable SMS
        remove_opt_out(patient_id, channel="sms")
        return OPT_IN_ACTION
```

**Critical:** Opt-out processing happens BEFORE any other message handling. When a STOP keyword is detected, no further AI processing occurs for that message.

---

### CHECK 3: Channel Consent

**Purpose:** Ensure the patient has given consent for the communication channel.

**Consent model:**
```
ConsentRecord:
  patient_id: uuid
  channel: sms | email | voice | whatsapp
  consent_given: boolean
  consent_method: explicit_form | verbal | implicit | none
  consent_timestamp: datetime
  consent_expires: datetime | null
  ip_address: string | null  # For digital consent
  recording_url: string | null  # For verbal consent
```

**Consent rules:**
| Channel | Consent Required | TCPA Requirement |
|---------|-----------------|-----------------|
| SMS | Explicit written or verbal | Required — prior express written consent for marketing, prior express consent for informational |
| Email | Implicit for transactional, explicit for marketing | CAN-SPAM — clear opt-out, accurate headers |
| Voice (automated) | Explicit written | TCPA — prior express written consent for autodialed calls |
| Voice (live agent) | Implicit for appointment-related | TCPA — consent implied for appointment reminders |
| WhatsApp | Explicit | Meta requires opt-in |
| Website chat | Implicit (patient initiated) | Patient initiates = consent for that session |

**Consent expiry:**
- SMS marketing consent: 2 years (recommended) or until revoked
- SMS informational: No expiry (appointment reminders, recalls)
- Email marketing: 2 years or until revoked
- Voice automated: 2 years or until revoked

**Check logic:**
```python
def check_channel_consent(patient_id, channel, message_type) -> PolicyResult:
    consent = db.query(Consent).filter(
        Consent.patient_id == patient_id,
        Consent.channel == channel,
    ).first()

    if not consent or not consent.consent_given:
        return PolicyResult.DENY("no_consent", f"No {channel} consent on file")

    if consent.consent_expires and consent.consent_expires < now():
        return PolicyResult.DENY("consent_expired", f"{channel} consent expired {consent.consent_expires}")

    # Informational messages (recalls, appointment confirmations) have broader consent
    if message_type == "informational":
        return PolicyResult.PASS()

    # Marketing/recapture messages require explicit marketing consent
    if message_type == "marketing" and consent.consent_method in ("implicit", "none"):
        return PolicyResult.DENY("insufficient_consent", "Marketing messages require explicit consent")

    return PolicyResult.PASS()
```

---

### CHECK 4: Frequency Cap

**Purpose:** Prevent over-messaging patients.

**Default caps (overridable per tenant):**
```python
DEFAULT_MAX_MESSAGES_PER_DAY = 3     # All channels combined
DEFAULT_MAX_MESSAGES_PER_WEEK = 10   # All channels combined
DEFAULT_MAX_MESSAGES_PER_MONTH = 15  # All channels combined
DEFAULT_COOLDOWN_HOURS = 24          # Minimum hours between messages of same type
DEFAULT_COOLDOWN_AFTER_REPLY = 4     # Hours after patient replies before next outreach
```

**Per-recapture-type caps:**
```python
RECAPTURE_TYPE_ATTEMPT_LIMITS = {
    "lead_abandoned": 3,
    "booking_abandoned": 2,
    "cancellation": 3,
    "no_show": 2,
    "treatment_unscheduled": 4,
    "recall": 2,
    "inactive": 2,
    "long_term_inactive": 1,
}
```

**Check logic:**
```python
def check_frequency_cap(patient_id, channel, recapture_type) -> PolicyResult:
    now = datetime.utcnow()

    # Count messages in rolling windows
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    daily_count = db.query(Message).filter(
        Message.patient_id == patient_id,
        Message.direction == "outbound",
        Message.sent_at >= day_ago,
    ).count()

    weekly_count = db.query(Message).filter(
        Message.patient_id == patient_id,
        Message.direction == "outbound",
        Message.sent_at >= week_ago,
    ).count()

    if daily_count >= MAX_MESSAGES_PER_DAY:
        return PolicyResult.DENY("daily_cap", f"Patient has received {daily_count} messages today")

    if weekly_count >= MAX_MESSAGES_PER_WEEK:
        return PolicyResult.DENY("weekly_cap", f"Patient has received {weekly_count} messages this week")

    # Check recapture-type-specific attempt limit
    attempt_count = db.query(CampaignAttempt).filter(
        CampaignAttempt.patient_id == patient_id,
        CampaignAttempt.recapture_type == recapture_type,
        CampaignAttempt.created_at >= thirty_days_ago,
    ).count()

    max_attempts = RECAPTURE_TYPE_ATTEMPT_LIMITS.get(recapture_type, 3)
    if attempt_count >= max_attempts:
        return PolicyResult.DENY("max_attempts", f"Max {max_attempts} attempts for {recapture_type}")

    # Cooldown check — has it been long enough since last attempt of this type?
    last_attempt = db.query(CampaignAttempt).filter(
        CampaignAttempt.patient_id == patient_id,
        CampaignAttempt.recapture_type == recapture_type,
    ).order_by(CampaignAttempt.created_at.desc()).first()

    if last_attempt:
        hours_since = (now - last_attempt.created_at).total_seconds() / 3600
        if hours_since < DEFAULT_COOLDOWN_HOURS:
            return PolicyResult.DENY("cooldown", f"Cooldown: {DEFAULT_COOLDOWN_HOURS - hours_since:.1f}h remaining")

    return PolicyResult.PASS()
```

---

### CHECK 5: Quiet Hours

**Purpose:** Respect patient's local time and preferred contact times.

**Default quiet hours:**
```python
DEFAULT_QUIET_HOURS_START = "21:00"  # 9 PM
DEFAULT_QUIET_HOURS_END = "09:00"    # 9 AM
DEFAULT_QUIET_DAYS = []               # No quiet days by default
```

**Per-tenant and per-patient overrides:**
```python
CommunicationPreferences:
  patient_id: uuid
  preferred_channel: sms | email | voice
  preferred_time_start: "HH:MM"  # e.g., "10:00"
  preferred_time_end: "HH:MM"    # e.g., "20:00"
  timezone: string               # IANA timezone
  quiet_hours_start: "HH:MM | null"
  quiet_hours_end: "HH:MM | null"
  do_not_disturb: boolean
```

**Check logic:**
```python
def check_quiet_hours(patient_id, channel, scheduled_time) -> PolicyResult:
    prefs = db.query(CommunicationPreferences).filter(
        CommunicationPreferences.patient_id == patient_id
    ).first()

    # Patient timezone
    tz = pytz.timezone(prefs.timezone or DEFAULT_TIMEZONE)
    local_time = scheduled_time.astimezone(tz)

    # Check do-not-disturb
    if prefs.do_not_disturb:
        return PolicyResult.DENY("do_not_disturb", "Patient has DND enabled")

    # Check quiet hours (in patient's local time)
    quiet_start = prefs.quiet_hours_start or DEFAULT_QUIET_HOURS_START
    quiet_end = prefs.quiet_hours_end or DEFAULT_QUIET_HOURS_END

    current_time = local_time.strftime("%H:%M")

    if _is_in_quiet_hours(current_time, quiet_start, quiet_end):
        # Don't deny — reschedule to next allowed time
        next_allowed = _next_allowed_time(local_time, quiet_start, quiet_end)
        return PolicyResult.RESCHEDULE(next_allowed, "quiet_hours")

    # Check preferred contact window
    if prefs.preferred_time_start and prefs.preferred_time_end:
        if not _is_in_window(current_time, prefs.preferred_time_start, prefs.preferred_time_end):
            next_allowed = _next_allowed_time(local_time, prefs.preferred_time_start, prefs.preferred_time_end)
            return PolicyResult.RESCHEDULE(next_allowed, "outside_preferred_hours")

    return PolicyResult.PASS()

def _is_in_quiet_hours(current, start, end):
    """Check if current time is in quiet hours, handling overnight ranges."""
    if start > end:  # Overnight (e.g., 21:00 to 09:00)
        return current >= start or current <= end
    else:
        return start <= current <= end
```

**Reschedule behavior:** When quiet hours or preferred time blocks outreach, the policy engine does NOT deny — it returns a `RESCHEDULE` result with the next allowed time. The campaign engine reschedules the attempt.

---

### CHECK 6: Business Hours

**Purpose:** Don't send outreach outside clinic operating hours unless it's explicitly allowed.

**Logic:**
```python
def check_business_hours(clinic_id, scheduled_time) -> PolicyResult:
    clinic = db.query(Clinic).get(clinic_id)
    hours = clinic.business_hours or DEFAULT_BUSINESS_HOURS

    tz = pytz.timezone(clinic.timezone or DEFAULT_TIMEZONE)
    local_time = scheduled_time.astimezone(tz)

    weekday = local_time.strftime("%A").lower()
    day_hours = hours.get(weekday)

    if day_hours is None:
        # Clinic closed this day
        return PolicyResult.RESCHEDULE(next_open_day(clinic), "clinic_closed")

    current_time = local_time.strftime("%H:%M")
    if current_time < day_hours["open"] or current_time > day_hours["close"]:
        return PolicyResult.RESCHEDULE(next_open_time(clinic), "outside_business_hours")

    return PolicyResult.PASS()
```

**Exception:** Informational messages (appointment confirmations, recall reminders) may be sent outside business hours if the patient has opted into after-hours notifications.

---

### CHECK 7: Duplicate Suppression

**Purpose:** Don't send the same or similar outreach multiple times.

**Logic:**
```python
def check_duplicate_suppression(patient_id, recapture_type, channel) -> PolicyResult:
    # Check if same recapture type was already attempted with same channel recently
    recent = db.query(CampaignAttempt).filter(
        CampaignAttempt.patient_id == patient_id,
        CampaignAttempt.recapture_type == recapture_type,
        CampaignAttempt.channel == channel,
        CampaignAttempt.created_at >= thirty_days_ago,
    ).first()

    if recent:
        # Suppress same channel for same type within 14 days
        days_since = (now() - recent.created_at).days
        if days_since < 14:
            return PolicyResult.DENY("duplicate_suppression", f"Same {channel} outreach for {recapture_type} sent {days_since}d ago")

    # Check if any outreach was sent in last 24 hours regardless of type
    last_any = db.query(CampaignAttempt).filter(
        CampaignAttempt.patient_id == patient_id,
        CampaignAttempt.created_at >= one_day_ago,
    ).first()

    if last_any:
        return PolicyResult.DENY("recent_outreach", "Outreach sent within last 24h")

    return PolicyResult.PASS()
```

---

### CHECK 8: Safety Check

**Purpose:** Detect if the patient has communicated something that requires immediate human attention.

**Logic:**
```python
def check_safety(patient_id, conversation_id) -> PolicyResult:
    # Get recent patient messages
    recent_messages = db.query(Message).filter(
        Message.patient_id == patient_id,
        Message.direction == "inbound",
        Message.created_at >= one_hour_ago,
    ).all()

    for msg in recent_messages:
        safety_result = safety_classifier.classify(msg.content)

        if safety_result.level == SafetyLevel.EMERGENCY:
            # IMMEDIATE escalation — no outreach
            publish(EventType.SAFETY_ESCALATION, {
                "patient_id": patient_id,
                "conversation_id": conversation_id,
                "escalation_level": "emergency",
                "trigger_content": msg.content,
                "recommended_action": "call_911",
            })
            return PolicyResult.ESCALATE("emergency", "Immediate safety escalation")

        elif safety_result.level == SafetyLevel.URGENT:
            publish(EventType.SAFETY_ESCALATION, {
                "patient_id": patient_id,
                "conversation_id": conversation_id,
                "escalation_level": "urgent",
                "trigger_content": msg.content,
                "recommended_action": "staff_handoff",
            })
            return PolicyResult.ESCALATE("urgent", "Urgent — staff must handle")

        elif safety_result.level == SafetyLevel.PROHIBITED:
            # Medical advice question — handoff but continue limited outreach
            return PolicyResult.ESCALATE("prohibited", "Medical question — handoff to staff")

    return PolicyResult.PASS()
```

**Safety classifier triggers (from constants):**
```python
EMERGENCY_KEYWORDS = [
    "emergency", "urgent", "bleeding", "swelling", "broken tooth",
    "knocked out", "tooth fell out", "unbearable pain", "can't breathe",
    "difficulty breathing", "severe pain", "abscess", "fever", "pus",
]

MEDICAL_ADVICE_TRIGGERS = [
    "diagnose", "diagnosis", "prescribe", "medication",
    "what should i do", "is this serious", "how serious",
    "am i okay", "what does this mean",
]
```

---

### CHECK 9: Recapture Attempt Limit

**Purpose:** Don't keep trying patients who have already been contacted enough.

**Logic:**
```python
def check_attempt_limit(patient_id, recapture_type) -> PolicyResult:
    # Check attempts across ALL channels for this recapture type
    attempts = db.query(CampaignAttempt).filter(
        CampaignAttempt.patient_id == patient_id,
        CampaignAttempt.recapture_type == recapture_type,
        CampaignAttempt.created_at >= ninety_days_ago,
    ).all()

    max_attempts = RECAPTURE_TYPE_ATTEMPT_LIMITS.get(recapture_type, 3)

    if len(attempts) >= max_attempts:
        return PolicyResult.DENY("max_attempts", f"Max {max_attempts} attempts reached for {recapture_type}")

    # Check overall attempts across all recapture types
    total_attempts = db.query(CampaignAttempt).filter(
        CampaignAttempt.patient_id == patient_id,
        CampaignAttempt.created_at >= ninety_days_ago,
    ).count()

    if total_attempts >= 10:
        return PolicyResult.DENY("overall_cap", "Patient has received 10+ outreach attempts")

    return PolicyResult.PASS()
```

---

### CHECK 10: Staff Override

**Purpose:** Allow staff to manually suppress outreach for specific patients.

**Logic:**
```python
def check_staff_override(patient_id) -> PolicyResult:
    override = db.query(StaffOverride).filter(
        StaffOverride.patient_id == patient_id,
        StaffOverride.active == True,
    ).first()

    if override:
        return PolicyResult.DENY(
            "staff_suppressed",
            f"Suppressed by staff: {override.reason}",
            override.staff_id
        )

    return PolicyResult.PASS()
```

**StaffOverride table:**
```sql
staff_overrides:
  id: uuid PK
  tenant_id: uuid NOT NULL
  patient_id: uuid NOT NULL
  staff_id: uuid NOT NULL
  reason: text
  active: boolean DEFAULT true
  expires_at: timestamp | null
  created_at: timestamp
```

---

### CHECK 11: Tenant Configuration

**Purpose:** Respect clinic-specific policies.

**Logic:**
```python
def check_tenant_config(tenant_id, recapture_type, channel) -> PolicyResult:
    config = db.query(TenantConfig).filter(
        TenantConfig.tenant_id == tenant_id
    ).first()

    # Check if clinic has disabled this recapture type
    disabled_types = config.disabled_recapture_types or []
    if recapture_type in disabled_types:
        return PolicyResult.DENY("clinic_disabled", f"Clinic has disabled {recapture_type} outreach")

    # Check if clinic has disabled this channel
    disabled_channels = config.disabled_channels or []
    if channel in disabled_channels:
        return PolicyResult.DENY("channel_disabled", f"Clinic has disabled {channel}")

    # Check clinic's message volume limits
    if config.max_daily_outreach and _get_daily_count(tenant_id) >= config.max_daily_outreach:
        return PolicyResult.DENY("tenant_daily_cap", "Clinic daily outreach limit reached")

    return PolicyResult.PASS()
```

---

## 4. Policy Result Types

```python
class PolicyResult:
    """Result of a policy check."""

    @staticmethod
    def PASS() -> "PolicyResult":
        return PolicyResult("pass", None, None)

    @staticmethod
    def DENY(reason: str, detail: str, actor_id: uuid = None) -> "PolicyResult":
        return PolicyResult("deny", reason, detail, actor_id)

    @staticmethod
    def RESCHEDULE(scheduled_time: datetime, reason: str) -> "PolicyResult":
        return PolicyResult("reschedule", reason, scheduled_time=scheduled_time)

    @staticmethod
    def ESCALATE(level: str, detail: str) -> "PolicyResult":
        return PolicyResult("escalate", level, detail)

    def __init__(self, decision: str, reason: str, detail: str = None, actor_id: uuid = None, scheduled_time: datetime = None):
        self.decision = decision  # "pass" | "deny" | "reschedule" | "escalate"
        self.reason = reason
        self.detail = detail
        self.actor_id = actor_id
        self.scheduled_time = scheduled_time
```

---

## 5. Policy Engine API

```python
class PolicyEngine:
    """Complete policy evaluation engine."""

    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client

    def evaluate_outreach(self, tenant_id, patient_id, channel, recapture_type,
                          scheduled_time=None, conversation_id=None) -> PolicyEvaluation:
        """
        Run all policy checks and return a complete evaluation.

        Returns:
            PolicyEvaluation with:
              - decision: "approve" | "deny" | "reschedule" | "escalate"
              - denied_reasons: list of denial reasons
              - reschedule_time: datetime | None
              - escalation: dict | None
              - checks_run: dict of check name → result
        """
        patient = self._get_patient(patient_id)
        if not patient:
            return PolicyEvaluation.deny("patient_not_found")

        checks = {}

        # Check 1: State validity
        result = self._check_state_valid(patient)
        checks["state_valid"] = result
        if result.decision != "pass":
            return PolicyEvaluation.from_check_result(result, checks)

        # Check 2: Opt-out
        result = self._check_opt_out(tenant_id, patient_id)
        checks["opt_out"] = result
        if result.decision != "pass":
            return PolicyEvaluation.from_check_result(result, checks)

        # Check 3: Channel consent
        result = self._check_channel_consent(patient_id, channel, recapture_type)
        checks["channel_consent"] = result
        if result.decision != "pass":
            return PolicyEvaluation.from_check_result(result, checks)

        # Check 4: Frequency cap
        result = self._check_frequency_cap(patient_id, channel, recapture_type)
        checks["frequency_cap"] = result
        if result.decision != "pass":
            return PolicyEvaluation.from_check_result(result, checks)

        # Check 5: Quiet hours
        check_time = scheduled_time or datetime.utcnow()
        result = self._check_quiet_hours(patient_id, channel, check_time)
        checks["quiet_hours"] = result
        if result.decision == "deny":
            return PolicyEvaluation.from_check_result(result, checks)
        elif result.decision == "reschedule":
            return PolicyEvaluation.reschedule(result.scheduled_time, checks)

        # Check 6: Business hours
        result = self._check_business_hours(tenant_id, check_time)
        checks["business_hours"] = result
        if result.decision == "deny":
            return PolicyEvaluation.from_check_result(result, checks)
        elif result.decision == "reschedule":
            return PolicyEvaluation.reschedule(result.scheduled_time, checks)

        # Check 7: Duplicate suppression
        result = self._check_duplicate_suppression(patient_id, recapture_type, channel)
        checks["duplicate_suppression"] = result
        if result.decision != "pass":
            return PolicyEvaluation.from_check_result(result, checks)

        # Check 8: Safety (only if there's an active conversation)
        if conversation_id:
            result = self._check_safety(patient_id, conversation_id)
            checks["safety"] = result
            if result.decision == "escalate":
                return PolicyEvaluation.escalate(result, checks)
            elif result.decision == "deny":
                return PolicyEvaluation.from_check_result(result, checks)

        # Check 9: Attempt limit
        result = self._check_attempt_limit(patient_id, recapture_type)
        checks["attempt_limit"] = result
        if result.decision != "pass":
            return PolicyEvaluation.from_check_result(result, checks)

        # Check 10: Staff override
        result = self._check_staff_override(patient_id)
        checks["staff_override"] = result
        if result.decision != "pass":
            return PolicyEvaluation.from_check_result(result, checks)

        # Check 11: Tenant config
        result = self._check_tenant_config(tenant_id, recapture_type, channel)
        checks["tenant_config"] = result
        if result.decision != "pass":
            return PolicyEvaluation.from_check_result(result, checks)

        # All checks passed
        return PolicyEvaluation.approve(checks)
```

---

## 6. Audit Logging for Policy Decisions

Every policy evaluation is logged:

```python
class PolicyAuditLog:
    policy_evaluation_id: uuid
    tenant_id: uuid
    patient_id: uuid
    recapture_type: string
    channel: string
    scheduled_time: datetime
    decision: string  # approve | deny | reschedule | escalate
    denied_reasons: list
    reschedule_time: datetime | null
    checks_run: json
    evaluated_at: datetime
    evaluated_by: string  # "system" | "ai" | "staff"
```

**This log is critical for:**
- Compliance review (HIPAA audit)
- Dispute resolution (patient says they were over-contacted)
- Model training (features for ML models)
- Business analytics (which policies are blocking most outreach)

---

## 7. Policy Override Rules

The following are the ONLY circumstances under which outreach may proceed despite a policy check:

| Check | Override Allowed | Who Can Override | Conditions |
|-------|-----------------|------------------|------------|
| Frequency cap | Yes | Staff only | Documented reason, logged |
| Quiet hours | Yes | Staff only | Urgent matter only |
| Duplicate suppression | Yes | Staff only | Different message purpose |
| Attempt limit | Yes | Staff only | Escalated approval |
| Opt-out | **NO** | **NO ONE** | Patient must re-opt-in |
| Safety | **NO** | **NO ONE** | Safety always wins |
| Tenant config | No | Tenant admin | Config change, not per-patient |
| Staff override | N/A | Staff | This IS the override mechanism |

**Rule: No LLM output may override any policy decision. Policy is deterministic code.**
