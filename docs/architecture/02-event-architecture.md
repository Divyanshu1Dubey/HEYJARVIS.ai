# Event-Driven Architecture
## Complete Event Catalog & Bus Design

**Document:** 02 of 20  
**Purpose:** Defines every event in the system, its producer, payload, consumers, idempotency, and delivery guarantees.

---

## 1. Event Bus Architecture

### Design Principles

1. **Events are the source of truth.** All state changes are events. No state mutation happens without an event.
2. **Eventual consistency is acceptable within SLA.** The system does not require immediate consistency between components — eventual consistency within seconds is sufficient.
3. **Idempotent by design.** Every event has an idempotency key. Consumers must handle duplicate delivery gracefully.
4. **Tenant-scoped.** Every event carries `tenant_id`. Every consumer filters by tenant.
5. **Ordering is best-effort.** For most events, ordering within a patient context matters. We use partition keys to maintain ordering where it matters (appointment events, message sequences).

### Technology Selection

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Message broker | Redis Streams → Kafka (migration path) | Redis for initial scale; Kafka when throughput exceeds 10K events/sec |
| Task queue | Celery + Redis | Already in codebase |
| Scheduled events | Celery Beat + custom scheduler | Delay/schedule outreach |
| Dead letter | Redis DLQ stream | Failed event handling |

**Migration path:**
- Phase 1: Redis Streams + Celery (current, sufficient for ~1K dental practices)
- Phase 2: Add Kafka for high-volume event streams (appointment events at scale)
- Phase 3: Event sourcing for patient state — full audit trail from events

### Event Flow

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   PRODUCER  │────▶│  EVENT BUS   │────▶│   CONSUMER(S)  │
│             │     │  (Redis)     │     │                │
│ - API       │     │ - Pub/Sub    │     │ - Recapture    │
│ - Worker    │     │ - Streams    │     │ - Campaign     │
│ - Integrations│   │ - DLQ        │     │ - Analytics    │
│ - Scheduler │     │ - Idempotency│     │ - AI Engine    │
└─────────────┘     └──────────────┘     └────────────────┘
```

---

## 2. Event Schema (Common)

Every event follows this envelope:

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "tenant_id": "uuid",
  "patient_id": "uuid",
  "conversation_id": "uuid (nullable)",
  "appointment_id": "uuid (nullable)",
  "campaign_id": "uuid (nullable)",
  "correlation_id": "uuid",
  "idempotency_key": "string",
  "timestamp": "ISO-8601",
  "source": "api | worker | integration | scheduler | ai-engine",
  "version": "1.0",
  "payload": { ... }
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | UUID | Unique event identifier |
| `event_type` | string | Dot-separated type (e.g., `lead.created`) |
| `tenant_id` | UUID | Which dental practice |
| `patient_id` | UUID | Which patient |
| `conversation_id` | UUID | Related conversation (nullable) |
| `appointment_id` | UUID | Related appointment (nullable) |
| `campaign_id` | UUID | Related campaign (nullable) |
| `correlation_id` | UUID | Groups related events (e.g., one patient interaction) |
| `idempotency_key` | string | Dedup key — producer-generated, unique per logical event |
| `timestamp` | ISO-8601 | When the event occurred (not when published) |
| `source` | string | Which component produced this |
| `version` | string | Event schema version |
| `payload` | object | Event-specific data (see below) |

### Security Classification

| Event Category | Contains PHI | Retention |
|---------------|-------------|-----------|
| Patient events | Yes | 7 years |
| Message events | Yes (content) | 7 years |
| Appointment events | Yes | 7 years |
| Campaign events | No (aggregate) | 3 years |
| System events | No | 1 year |
| Audit events | Yes | 7 years |

---

## 3. Complete Event Catalog

### 3.1 Lead Events

#### `lead.created`

**Producer:** API (webhook from website, form submission)  
**Trigger:** Patient submits lead form or starts chat  
**Consumers:** Recapture Engine, Campaign Engine, Analytics  
**Idempotency key:** `lead:{source}:{external_id}`

```json
{
  "source": "web_form | web_chat | phone | referral | landing_page",
  "external_id": "string — ID from source system",
  "lead_data": {
    "first_name": "string",
    "last_name": "string",
    "email": "string | null",
    "phone": "string | null",
    "service_interest": "string | null",
    "message": "string | null",
    "referrer": "string | null",
    "landing_page": "string | null",
    "utm_source": "string | null",
    "utm_medium": "string | null",
    "utm_campaign": "string | null"
  },
  "consent_sms": "boolean",
  "consent_email": "boolean",
  "consent_voice": "boolean",
  "consent_method": "form | verbal | implicit | none",
  "consent_timestamp": "ISO-8601 | null"
}
```

#### `lead.contacted`

**Producer:** Worker (outreach dispatcher)  
**Trigger:** First outreach message sent and delivered  
**Consumers:** Analytics, Campaign Engine  
**Idempotency key:** `lead_contacted:{patient_id}:{campaign_id}`

```json
{
  "channel": "sms | email | voice",
  "method": "automated | manual",
  "attempt_number": 1,
  "message_id": "uuid",
  "scheduled_at": "ISO-8601",
  "sent_at": "ISO-8601"
}
```

#### `lead.disqualified`

**Producer:** AI Engine or Staff  
**Trigger:** Lead determined not viable  
**Consumers:** Campaign Engine (suppress), Analytics  
**Idempotency key:** `lead_disqualified:{patient_id}`

```json
{
  "reason": "out_of_service_area | not_interested | invalid_contact | other",
  "reason_detail": "string | null",
  "determined_by": "ai | staff",
  "staff_id": "uuid | null"
}
```

### 3.2 Conversation Events

#### `conversation.started`

**Producer:** API  
**Trigger:** Patient initiates or AI initiates conversation  
**Consumers:** AI Engine, Analytics  
**Idempotency key:** `conv_started:{patient_id}:{channel}` (dedup by patient+channel per 24h)

```json
{
  "channel": "sms | web_chat | email | voice",
  "initiator": "patient | ai | staff",
  "initial_intent": "string | null",
  "context": {
    "previous_state": "string",
    "recapture_type": "string | null",
    "campaign_id": "uuid | null"
  }
}
```

#### `conversation.abandoned`

**Producer:** AI Engine  
**Trigger:** Patient stops responding, conversation times out  
**Consumers:** Recapture Engine (trigger recovery), Analytics  
**Idempotency key:** `conv_abandoned:{conversation_id}`

```json
{
  "conversation_id": "uuid",
  "last_patient_message_at": "ISO-8601",
  "last_ai_message_at": "ISO-8601",
  "turns_count": "integer",
  "abandonment_reason": "patient_stopped_responding | timeout | patient_disconnected | ai_error",
  "last_intent": "string | null",
  "booking_attempted": "boolean",
  "appointment_offered": "boolean"
}
```

#### `conversation.handoff`

**Producer:** AI Engine  
**Trigger:** AI escalates to human  
**Consumers:** Notifications, Analytics, Staff Queue  
**Idempotency key:** `handoff:{conversation_id}`

```json
{
  "conversation_id": "uuid",
  "handoff_reason": "patient_request | medical_question | emergency | complaint | complex_treatment | legal_threat | other",
  "ai_summary": "string — concise summary for staff",
  "patient_sentiment": "neutral | frustrated | anxious | angry | urgent",
  "last_messages": [
    {"role": "patient|ai", "text": "string", "timestamp": "ISO-8601"}
  ],
  "priority": "low | medium | high | urgent",
  "assigned_to": "uuid | null — staff member if auto-assigned"
}
```

#### `conversation.resumed`

**Producer:** Staff / AI  
**Trigger:** Conversation resumes after handoff  
**Consumers:** Analytics  
**Idempotency key:** `conv_resumed:{conversation_id}`

```json
{
  "conversation_id": "uuid",
  "resumed_by": "staff | ai | patient",
  "staff_id": "uuid | null",
  "resolution": "string | null"
}
```

### 3.3 Message Events

#### `message.sent`

**Producer:** Worker (message dispatcher)  
**Trigger:** Message dispatched to provider  
**Consumers:** Analytics, Delivery Tracker  
**Idempotency key:** `msg_sent:{message_id}`

```json
{
  "message_id": "uuid",
  "channel": "sms | email | voice",
  "direction": "outbound",
  "to": "string — E.164 for SMS, email for email",
  "from": "string | null",
  "body_preview": "string — first 200 chars for analytics (PHI-safe)",
  "body_length": "integer",
  "template_id": "uuid | null",
  "template_variables": "object | null",
  "personalized": "boolean",
  "external_id": "string — provider's message ID",
  "sent_at": "ISO-8601"
}
```

#### `message.delivered`

**Producer:** Worker (delivery webhook)  
**Trigger:** Provider confirms delivery  
**Consumers:** Analytics  
**Idempotency key:** `msg_delivered:{external_id}`

```json
{
  "message_id": "uuid",
  "external_id": "string",
  "delivered_at": "ISO-8601",
  "delivery_status": "delivered | read | failed | bounced"
}
```

#### `message.failed`

**Producer:** Worker (delivery webhook or timeout)  
**Trigger:** Provider reports failure  
**Consumers:** Campaign Engine (retry decision), Analytics  
**Idempotency key:** `msg_failed:{message_id}`

```json
{
  "message_id": "uuid",
  "external_id": "string | null",
  "failure_reason": "invalid_number | bounced | blocked | timeout | provider_error | opted_out",
  "failed_at": "ISO-8601",
  "retry_count": "integer"
}
```

#### `message.replied`

**Producer:** API (webhook from provider)  
**Trigger:** Patient replies  
**Consumers:** AI Engine, Campaign Engine, Analytics  
**Idempotency key:** `msg_replied:{external_reply_id}`

```json
{
  "message_id": "uuid — the original message being replied to",
  "reply_text": "string — patient's reply",
  "reply_channel": "sms | email | voice",
  "external_reply_id": "string",
  "received_at": "ISO-8601",
  "intent": "string | null — AI-classified",
  "sentiment": "string | null"
}
```

#### `patient.opted_out`

**Producer:** Worker (keyword detection)  
**Trigger:** STOP keyword, patient request, or staff action  
**Consumers:** Campaign Engine (suppress all), Recapture Engine (suppress), Analytics  
**Idempotency key:** `optout:{patient_id}`

```json
{
  "patient_id": "uuid",
  "opt_out_reason": "patient_request | stop_keyword | staff_action | bounced | complaint",
  "opted_out_at": "ISO-8601",
  "opted_out_by": "patient | ai | staff",
  "channels_affected": ["sms", "email", "voice"],
  "can_reopt_in": "boolean — true for patient opt-out, false for staff DNC"
}
```

### 3.4 Appointment Events

#### `appointment.offered`

**Producer:** AI Engine or Staff  
**Trigger:** System offers a specific time slot  
**Consumers:** Analytics, Campaign Engine  
**Idempotency key:** `apt_offered:{patient_id}:{slot_start}`

```json
{
  "appointment_type": "string",
  "provider_id": "uuid",
  "provider_name": "string",
  "start": "ISO-8601",
  "end": "ISO-8601",
  "room": "string | null",
  "offered_at": "ISO-8601",
  "offered_by": "ai | staff",
  "hold_expires_at": "ISO-8601 — hold slot expiration"
}
```

#### `appointment.booked`

**Producer:** Integrations (PMS webhook or API call)  
**Trigger:** Appointment successfully scheduled  
**Consumers:** Analytics, Campaign Engine, Recapture Engine, Notifications  
**Idempotency key:** `apt_booked:{external_appointment_id}`

```json
{
  "appointment_id": "uuid",
  "external_id": "string — PMS appointment ID",
  "appointment_type": "string",
  "provider_id": "uuid",
  "provider_name": "string",
  "start": "ISO-8601",
  "end": "ISO-8601",
  "room": "string",
  "status": "scheduled | confirmed | completed | cancelled | no_show",
  "booked_at": "ISO-8601",
  "booked_via": "online | phone | ai | staff",
  "recapture_attributed": "boolean",
  "recapture_campaign_id": "uuid | null"
}
```

#### `appointment.cancelled`

**Producer:** Integrations (PMS webhook)  
**Trigger:** Appointment cancelled  
**Consumers:** Recapture Engine (trigger), Analytics, Campaign Engine  
**Idempotency key:** `apt_cancelled:{appointment_id}`

```json
{
  "appointment_id": "uuid",
  "cancelled_at": "ISO-8601",
  "cancelled_by": "patient | staff | clinic",
  "cancellation_reason": "schedule_conflict | price | insurance | fear | transportation | timing | no_explanation | other",
  "cancellation_reason_detail": "string | null",
  "time_until_appointment": "string — how far in future the apt was",
  "previous_cancellations": "integer — count of prior cancellations by this patient",
  "provider_notified": "boolean"
}
```

#### `appointment.confirmed`

**Producer:** Integrations or AI  
**Trigger:** Patient confirms appointment  
**Consumers:** Analytics  
**Idempotency key:** `apt_confirmed:{appointment_id}`

```json
{
  "appointment_id": "uuid",
  "confirmed_at": "ISO-8601",
  "confirmed_by": "patient | ai | staff",
  "confirmation_channel": "sms | email | voice | web"
}
```

#### `appointment.no_show`

**Producer:** Integrations (PMS webhook)  
**Trigger:** Patient marked as no-show  
**Consumers:** Recapture Engine, Analytics  
**Idempotency key:** `apt_no_show:{appointment_id}`

```json
{
  "appointment_id": "uuid",
  "no_show_at": "ISO-8601",
  "provider_id": "uuid",
  "appointment_type": "string",
  "patient_history": {
    "total_no_shows": "integer",
    "previous_no_shows": "integer",
    "total_visits": "integer",
    "cancellation_rate": "float"
  }
}
```

#### `appointment.completed`

**Producer:** Integrations (PMS webhook)  
**Trigger:** Appointment marked complete  
**Consumers:** Analytics, Recapture Engine (trigger recall scheduling)  
**Idempotency key:** `apt_completed:{appointment_id}`

```json
{
  "appointment_id": "uuid",
  "completed_at": "ISO-8601",
  "provider_id": "uuid",
  "appointment_type": "string",
  "procedure_codes": ["string — CDT codes"],
  "next_recall_due": "ISO-8601 | null",
  "treatment_plan_created": "boolean",
  "treatment_plan_id": "uuid | null",
  "revenue": "decimal | null"
}
```

#### `appointment_hold.expired`

**Producer:** Worker (scheduled job)  
**Trigger:** Appointment hold slot expires  
**Consumers:** Campaign Engine, Recapture Engine  
**Idempotency key:** `hold_expired:{hold_id}`

```json
{
  "hold_id": "uuid",
  "patient_id": "uuid",
  "appointment_type": "string",
  "provider_id": "uuid",
  "start": "ISO-8601",
  "expired_at": "ISO-8601"
}
```

### 3.5 Treatment Plan Events

#### `treatment_plan.created`

**Producer:** Integrations (PMS webhook)  
**Trigger:** Treatment plan created in PMS  
**Consumers:** Recapture Engine  
**Idempotency key:** `tx_plan:{external_treatment_plan_id}`

```json
{
  "treatment_plan_id": "uuid",
  "external_id": "string",
  "patient_id": "uuid",
  "provider_id": "uuid",
  "created_at": "ISO-8601",
  "total_cost": "decimal",
  "insurance_estimate": "decimal | null",
  "patient_estimate": "decimal | null",
  "items": [
    {
      "procedure_code": "string — CDT code",
      "description": "string",
      "cost": "decimal",
      "insurance_coverage": "decimal | null",
      "tooth": "string | null"
    }
  ],
  "services": ["crown | root_canal | implant | orthodontic | extraction | cleaning | filling | other"],
  "estimated_visits": "integer"
}
```

#### `treatment_plan.accepted`

**Producer:** Integrations or AI  
**Trigger:** Patient accepts treatment plan  
**Consumers:** Recapture Engine (monitor for scheduling)  
**Idempotency key:** `tx_accepted:{treatment_plan_id}`

```json
{
  "treatment_plan_id": "uuid",
  "patient_id": "uuid",
  "accepted_at": "ISO-8601",
  "accepted_by": "patient | staff",
  "first_treatment_scheduled": "boolean",
  "first_treatment_appointment_id": "uuid | null",
  "financing_discussed": "boolean"
}
```

#### `treatment_plan.unscheduled`

**Producer:** Recapture Engine (scheduled job)  
**Trigger:** Treatment plan accepted but no appointment within 14 days  
**Consumers:** Campaign Engine (trigger campaign)  
**Idempotency key:** `tx_unscheduled:{treatment_plan_id}`

```json
{
  "treatment_plan_id": "uuid",
  "patient_id": "uuid",
  "days_since_acceptance": "integer",
  "total_cost": "decimal",
  "services": ["string"],
  "barriers_identified": ["cost | fear | timing | insurance | transportation | other | unknown"]
}
```

### 3.6 Recall Events

#### `recall.due`

**Producer:** Scheduler (cron job)  
**Trigger:** Patient's recall period has elapsed  
**Consumers:** Recapture Engine, Campaign Engine  
**Idempotency key:** `recall:{patient_id}:{recall_type}`

```json
{
  "patient_id": "uuid",
  "recall_type": "hygiene | periodic_exam | continuing_care | post_treatment",
  "last_visit_date": "ISO-8601",
  "last_visit_type": "string",
  "days_overdue": "integer",
  "provider_id": "uuid | null",
  "service_code": "string | null"
}
```

#### `patient.inactive`

**Producer:** Scheduler (cron job)  
**Trigger:** No visits for 12 months  
**Consumers:** Recapture Engine, Campaign Engine  
**Idempotency key:** `inactive:{patient_id}`

```json
{
  "patient_id": "uuid",
  "last_visit_date": "ISO-8601",
  "months_inactive": "integer",
  "last_visit_type": "string",
  "total_lifetime_visits": "integer",
  "total_lifetime_value": "decimal",
  "reason_if_known": "string | null"
}
```

### 3.7 Campaign Events

#### `campaign.started`

**Producer:** Campaign Engine  
**Trigger:** Campaign begins execution  
**Consumers:** Analytics  
**Idempotency key:** `campaign:{campaign_id}`

```json
{
  "campaign_id": "uuid",
  "campaign_type": "lead_recapture | cancellation | no_show | treatment | recall | reactivation",
  "recapture_type": "string — specific taxonomy code",
  "target_count": "integer — number of patients enrolled",
  "started_at": "ISO-8601",
  "schedule": {
    "max_attempts": "integer",
    "attempt_interval_hours": "integer",
    "channels": ["string"],
    "start_time": "string — HH:MM",
    "end_time": "string — HH:MM",
    "quiet_days": ["string — day names"]
  }
}
```

#### `campaign.attempt_sent`

**Producer:** Worker  
**Trigger:** Campaign outreach attempt sent  
**Consumers:** Analytics, Recapture Engine  
**Idempotency key:** `campaign_attempt:{campaign_id}:{patient_id}:{attempt_number}`

```json
{
  "campaign_id": "uuid",
  "patient_id": "uuid",
  "attempt_number": "integer",
  "channel": "sms | email | voice",
  "message_id": "uuid",
  "sent_at": "ISO-8601",
  "template_id": "uuid",
  "personalization_hash": "string — for comparing template variants"
}
```

#### `campaign.completed`

**Producer:** Campaign Engine  
**Trigger:** Campaign finishes (all patients processed)  
**Consumers:** Analytics  
**Idempotency key:** `campaign_done:{campaign_id}`

```json
{
  "campaign_id": "uuid",
  "completed_at": "ISO-8601",
  "stats": {
    "targeted": "integer",
    "contacted": "integer",
    "responded": "integer",
    "booked": "integer",
    "opted_out": "integer",
    "failed": "integer",
    "response_rate": "float",
    "booking_rate": "float"
  }
}
```

### 3.8 AI Decision Events

#### `ai.decision`

**Producer:** AI Engine  
**Trigger:** AI makes a decision (classification, scoring, message selection)  
**Consumers:** Analytics, Audit  
**Idempotency key:** `ai_decision:{conversation_id}:{decision_type}:{timestamp}`

```json
{
  "conversation_id": "uuid | null",
  "patient_id": "uuid",
  "decision_type": "intent_classification | safety_classification | recapture_scoring | message_selection | channel_selection | handoff_decision",
  "input": {
    "message": "string | null — the input message if applicable",
    "context_keys": ["string"]
  },
  "output": {
    "intent": "string | null",
    "confidence": "float | null",
    "entities": "object | null",
    "risk_score": "float | null",
    "recommended_channel": "string | null",
    "recommended_action": "string | null"
  },
  "model": {
    "name": "string — model identifier",
    "version": "string",
    "tier": "keyword | llm_fast | llm_full"
  },
  "latency_ms": "integer",
  "tokens_used": "integer | null",
  "requires_human": "boolean",
  "timestamp": "ISO-8601"
}
```

#### `ai.action`

**Producer:** AI Engine  
**Trigger:** AI executes an action (tool call, state change)  
**Consumers:** Analytics, Audit  
**Idempotency key:** `ai_action:{conversation_id}:{action_type}:{timestamp}`

```json
{
  "conversation_id": "uuid",
  "patient_id": "uuid",
  "action_type": "tool_call | state_change | message_send | handoff",
  "tool_name": "string | null",
  "tool_arguments": "object | null — redacted for PHI",
  "result": "object | null — success/failure",
  "requires_confirmation": "boolean",
  "confirmed": "boolean | null",
  "timestamp": "ISO-8601"
}
```

### 3.9 Integration Events

#### `integration.sync`

**Producer:** Integration Worker  
**Trigger:** Periodic sync with external system  
**Consumers:** Analytics  
**Idempotency key:** `sync:{integration_type}:{clinic_id}:{sync_timestamp}`

```json
{
  "integration_type": "scheduling | insurance | patient_data | communication",
  "clinic_id": "uuid",
  "sync_type": "full | incremental",
  "started_at": "ISO-8601",
  "completed_at": "ISO-8601",
  "records_synced": "integer",
  "errors": ["string"],
  "success": "boolean"
}
```

#### `integration.webhook`

**Producer:** API (webhook endpoint)  
**Trigger:** External system sends webhook  
**Consumers:** Varies by webhook type  
**Idempotency key:** `webhook:{source}:{source_event_id}`

```json
{
  "source": "pms | telephony | chat | form",
  "source_event_id": "string — dedup from source",
  "event_type": "string",
  "received_at": "ISO-8601",
  "verified": "boolean — HMAC verified",
  "raw_payload": "object | null — stored for audit"
}
```

### 3.10 Safety & Audit Events

#### `safety.escalation`

**Producer:** Safety Classifier  
**Trigger:** Emergency or prohibited content detected  
**Consumers:** Notifications (immediate), Analytics  
**Idempotency key:** `safety:{conversation_id}:{timestamp}`

```json
{
  "conversation_id": "uuid",
  "patient_id": "uuid",
  "escalation_level": "urgent | emergency",
  "trigger_type": "emergency_keyword | medical_advice | threat | abusive | other",
  "trigger_content": "string — the content that triggered (PHI — redact in logs)",
  "escalation_reason": "string",
  "recommended_action": "call_911 | call_patient | staff_handoff | other",
  "detected_at": "ISO-8601"
}
```

#### `audit.log`

**Producer:** All components  
**Trigger:** Any auditable action  
**Consumers:** Audit store (write-only)  
**Idempotency key:** `audit:{correlation_id}`

```json
{
  "actor": {
    "type": "patient | staff | ai | system",
    "id": "uuid | null",
    "name": "string | null",
    "role": "string | null"
  },
  "action": "string — verb describing the action",
  "resource_type": "string",
  "resource_id": "uuid | null",
  "changes": {
    "before": "object | null",
    "after": "object | null"
  },
  "ip_address": "string | null — for staff actions",
  "user_agent": "string | null",
  "success": "boolean",
  "error": "string | null",
  "timestamp": "ISO-8601"
}
```

---

## 4. Deduplication & Idempotency

### Producer-Side Idempotency Keys

Every event producer generates its own idempotency key:

| Event | Idempotency Key Pattern | Scope |
|-------|------------------------|-------|
| `lead.created` | `lead:{source}:{external_id}` | Per lead source |
| `lead.contacted` | `lead_contacted:{patient_id}:{campaign_id}` | Per patient per campaign |
| `appointment.booked` | `apt_booked:{external_id}` | Per external appointment |
| `message.sent` | `msg_sent:{message_id}` | Per message |
| `message.replied` | `msg_replied:{external_reply_id}` | Per external reply |
| `patient.opted_out` | `optout:{patient_id}` | Per patient |
| `safety.escalation` | `safety:{conversation_id}:{timestamp}` | Per conversation per minute |

### Consumer-Side Dedup

The event bus maintains an idempotency cache (Redis SET with TTL):

1. On publish, check if `idempotency_key` exists in cache.
2. If exists → reject as duplicate, log warning.
3. If not → store key, publish event.
4. TTL: 24 hours for most events, 7 days for state transitions.

### Duplicate Detection Strategy

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Producer   │────▶│  Idempotency │────▶│  Redis Cache    │
│             │     │  Check       │     │  (24h TTL)      │
│             │     │              │     │                 │
│             │     │  Key exists? │────▶│  SET key = 1    │
│             │     │  YES → reject│     │                 │
│             │     │  NO → publish│     │                 │
└─────────────┘     └──────────────┘     └─────────────────┘
```

### Handling Provider Webhook Duplicates

External systems (PMS, Twilio) may send duplicate webhooks. Our webhook handler:
1. Checks `idempotency_key` first (from source event ID).
2. If processed → returns 200 OK without reprocessing.
3. If not processed → processes and stores idempotency key.

---

## 5. Retry & Error Handling

### Retry Strategy

| Event Category | Retry Count | Backoff | DLQ After |
|---------------|-------------|---------|-----------|
| Lead events | 3 | Exponential (1m, 5m, 30m) | 1 hour |
| Message events | 3 | Exponential (30s, 5m, 30m) | 2 hours |
| Appointment events | 5 | Exponential (10s, 1m, 5m, 30m, 2h) | 4 hours |
| Integration events | 5 | Exponential (30s, 2m, 10m, 1h, 4h) | 8 hours |
| AI events | 2 | Exponential (5s, 30s) | 15 minutes |
| Safety events | 0 (no retry — immediate human) | N/A | N/A |

### Dead Letter Queue

Events that exhaust retries go to the DLQ:
1. Alert the on-call engineer.
2. Store the event payload for manual review.
3. Provide a replay mechanism.
4. DLQ events are reviewed within 4 business hours.

### Failed Event Handling

For `appointment.cancelled` events that fail to process:
- The recapture engine MUST eventually see the event or the patient will not get recovery outreach.
- If DLQ processing detects a missed cancellation event, it triggers an immediate recapture eligibility scan for that patient.

---

## 6. Event Ordering Guarantees

### Within-Order Events

The following events MUST be processed in order per patient:

| Event Group | Ordering Requirement |
|-------------|---------------------|
| Message sequence (sent → delivered → replied) | Strict order per conversation |
| Appointment lifecycle (offered → booked → confirmed → completed/cancelled) | Strict order per appointment |
| State transitions | Strict order per patient |
| Campaign attempts | Order per patient (attempt 1 before attempt 2) |

### Implementation

Redis Streams consumer groups with partition key = `patient_id` ensure that all events for a given patient are processed by the same consumer instance in order. For Kafka, use `patient_id` as the partition key.

---

## 7. Event Versioning

Event schemas evolve. We handle this with:

1. **Schema version in event envelope:** Each event carries `"version": "1.0"`.
2. **Backward-compatible additions only:** New fields may be added, existing fields never removed or renamed.
3. **Consumer tolerance:** Consumers ignore unknown fields.
4. **Migration events:** For breaking changes, publish a migration event with both old and new formats.

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-15 | Initial schema |

---

## 8. Consumer Specifications

### Recapture Engine Consumer

**Subscribes to:**
- `lead.created`, `lead.contacted`, `lead.disqualified`
- `conversation.abandoned`, `conversation.handoff`
- `appointment.cancelled`, `appointment.no_show`, `appointment_hold.expired`
- `treatment_plan.accepted`, `treatment_plan.unscheduled`
- `recall.due`, `patient.inactive`
- `message.replied`, `message.failed`
- `patient.opted_out`
- `appointment.booked`, `appointment.completed`

**Actions on each event:**
1. Update patient state (via state machine).
2. Evaluate recapture eligibility (via decision engine).
3. If eligible, create `recapture_opportunity` record.
4. Queue opportunity for scoring.
5. If scoring above threshold, enroll in campaign.

### Campaign Engine Consumer

**Subscribes to:**
- `campaign.started`
- `campaign.attempt_sent`
- `message.delivered`, `message.failed`, `message.replied`
- `patient.opted_out`
- `appointment.booked`, `appointment.cancelled`

**Actions:**
1. Track campaign progress.
2. Schedule next attempt based on interval.
3. Suppress opted-out patients.
4. Adjust messaging based on response.
5. Complete campaign when all patients processed.

### Analytics Consumer

**Subscribes to:**
- All events (read-only, async)

**Actions:**
1. Aggregate metrics.
2. Update dashboards.
3. Feed ML training data.

### AI Engine Consumer

**Subscribes to:**
- `conversation.started`, `message.replied`
- `lead.created`, `lead.contacted`

**Actions:**
1. Process incoming messages.
2. Classify intent.
3. Generate responses.
4. Call tools.
5. Publish `ai.decision` and `ai.action` events.
