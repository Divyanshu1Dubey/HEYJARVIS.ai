# Event Model — Complete Event Architecture

## EM.1 Design Principles

1. Every important action is an event
2. Events are immutable once written
3. Events carry all context needed to reconstruct state
4. Events are the source of truth for analytics and audit
5. Event consumers are decoupled from producers
6. Events are idempotent (idempotency key prevents duplicates)

## EM.2 Event Naming Convention

```
<domain>.<action>[.<detail>]

Examples:
  lead.created
  appointment.cancelled
  message.sent
  patient.opted_out
  recapture.opportunity_created
```

## EM.3 Complete Event Catalog

### Domain: Lead

| Event | Producer | Description |
|-------|----------|-------------|
| `lead.created` | Web form / Chat | New lead submitted |
| `lead.contacted` | Campaign engine | First outreach sent to lead |
| `lead.responded` | Message service | Lead replied to outreach |
| `lead.converted` | Booking engine | Lead booked appointment |
| `lead.expired` | Eligibility engine | Lead opportunity expired |
| `lead.suppressed` | Policy engine | Lead suppressed from outreach |

**Payload:**
```json
{
  "event_id": "uuid",
  "event_type": "lead.created",
  "timestamp": "2025-10-01T14:30:00Z",
  "tenant_id": "clinic_uuid",
  "patient_id": "patient_uuid or null",
  "correlation_id": "conv_uuid",
  "source_system": "website|chat|phone|form",
  "idempotency_key": "form_submission_hash",
  "security_classification": "phi",
  "payload": {
    "lead_source": "website_form",
    "service_interest": "teeth_whitening",
    "referral_source": "google",
    "utm_campaign": "fall_promo_2025",
    "form_fields": {
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+15551234567",
      "email": "john@example.com",
      "preferred_contact": "sms",
      "insurance": "Delta Dental"
    }
  },
  "downstream_consumers": ["eligibility_engine", "campaign_engine", "analytics"],
  "retry_strategy": "none"
}
```

### Domain: Conversation

| Event | Producer | Description |
|-------|----------|-------------|
| `conversation.started` | Conversation API | New conversation created |
| `conversation.message_received` | Message service | Patient message received |
| `conversation.message_sent` | AI Agent | AI message sent |
| `conversation.intent_classified` | Intent Engine | Patient intent determined |
| `conversation.safety_flagged` | Safety Classifier | Safety concern detected |
| `conversation.handoff_created` | Handoff Service | Handoff to human created |
| `conversation.handoff_resolved` | Staff Dashboard | Handoff resolved |
| `conversation.ended` | Conversation API | Conversation ended |
| `conversation.abandoned` | Timeout Service | Patient abandoned chat |

### Domain: Appointment

| Event | Producer | Description |
|-------|----------|-------------|
| `appointment.offered` | AI Agent | Appointment slot offered to patient |
| `appointment.booked` | Booking Engine | Appointment booked (confirmed by PMS) |
| `appointment.confirmed` | Confirmation Service | Confirmation sent to patient |
| `appointment.cancelled` | PMS / Patient / AI | Appointment cancelled |
| `appointment.rescheduled` | Booking Engine | Appointment rescheduled |
| `appointment.no_show` | PMS / Timeout | Patient no-showed |
| `appointment.completed` | PMS | Appointment completed |
| `appointment.hold.created` | Booking Engine | Temporary hold created |
| `appointment.hold.expired` | Hold Service | Hold expired without booking |

**Payload (appointment.cancelled):**
```json
{
  "event_type": "appointment.cancelled",
  "payload": {
    "appointment_id": "uuid",
    "cancelled_by": "patient|staff|ai|system",
    "cancellation_reason": "schedule_conflict|price|insurance|fear|transportation|other",
    "cancellation_notes": "Patient has work meeting",
    "cancelled_at": "2025-10-01T10:00:00Z",
    "original_time": "2025-10-02T14:00:00Z",
    "provider_id": "uuid",
    "service_id": "uuid",
    "reschedule_offered": true
  }
}
```

### Domain: Treatment Plan

| Event | Producer | Description |
|-------|----------|-------------|
| `treatment_plan.created` | PMS | Treatment plan created by provider |
| `treatment_plan.accepted` | Patient / Staff | Patient accepted treatment plan |
| `treatment_plan.declined` | Patient / Staff | Patient declined treatment plan |
| `treatment_plan.item.scheduled` | Booking Engine | Treatment item scheduled |
| `treatment_plan.item.completed` | PMS | Treatment item completed |
| `treatment_plan.unscheduled` | Eligibility Engine | Treatment plan has unscheduled items |

### Domain: Recapture

| Event | Producer | Description |
|-------|----------|-------------|
| `recapture.opportunity_created` | Event Processor | New recapture opportunity identified |
| `recapture.opportunity.eligible` | Eligibility Engine | Opportunity deemed eligible |
| `recapture.opportunity.suppressed` | Policy Engine | Opportunity suppressed |
| `recapture.attempt.started` | Campaign Engine | Outreach attempt started |
| `recapture.attempt.sent` | Message Service | Outreach message sent |
| `recapture.attempt.delivered` | Delivery Service | Message delivered |
| `recapture.attempt.failed` | Delivery Service | Message delivery failed |
| `recapture.attempt.responded` | Message Service | Patient responded |
| `recapture.attempt.completed` | Campaign Engine | Attempt cycle completed |
| `recapture.campaign.completed` | Campaign Engine | All campaign steps completed |

### Domain: Communication

| Event | Producer | Description |
|-------|----------|-------------|
| `message.sent` | Message Service | Message sent to provider |
| `message.delivered` | Provider webhook | Provider confirms delivery |
| `message.read` | Provider webhook | Message read (if available) |
| `message.failed` | Provider webhook | Message delivery failed |
| `message.bounced` | Provider webhook | Email bounced |
| `message.replied` | Message Service | Patient replied |
| `message.opted_out` | Provider webhook | Patient opted out via channel |

### Domain: Patient

| Event | Producer | Description |
|-------|----------|-------------|
| `patient.opted_out` | Patient / Message Service | Patient opted out of communications |
| `patient.re_opted_in` | Patient / Staff | Patient re-opted in |
| `patient.contact_updated` | Staff / Integration | Contact info changed |
| `patient.consent.updated` | Consent Service | Consent status changed |
| `patient.inactive` | Eligibility Engine | Patient marked inactive |
| `patient.recall.due` | Recall Engine | Recall appointment due |

### Domain: AI

| Event | Producer | Description |
|-------|----------|-------------|
| `ai.decision.made` | AI Agent | AI made a decision |
| `ai.tool.called` | AI Agent | AI called a tool |
| `ai.tool.result` | Tool Service | Tool returned result |
| `ai.response.generated` | AI Agent | AI generated a response |
| `ai.response.validated` | Validator | Response passed validation |
| `ai.response.rejected` | Validator | Response failed validation |
| `ai.handoff.triggered` | AI Agent | AI triggered handoff |
| `ai.classification.intent` | Classifier | Intent classified |
| `ai.classification.safety` | Classifier | Safety classified |

### Domain: Integration

| Event | Producer | Description |
|-------|----------|-------------|
| `integration.sync.started` | Sync Service | Sync with external system started |
| `integration.sync.completed` | Sync Service | Sync completed |
| `integration.sync.failed` | Sync Service | Sync failed |
| `integration.webhook.received` | Webhook Handler | External webhook received |
| `integration.webhook.processed` | Webhook Handler | Webhook processed |
| `integration.webhook.failed` | Webhook Handler | Webhook processing failed |
| `integration.api.called` | Adapter | External API called |
| `integration.api.error` | Adapter | External API returned error |

### Domain: System

| Event | Producer | Description |
|-------|----------|-------------|
| `system.worker.started` | Worker | Worker process started |
| `system.worker.stopped` | Worker | Worker process stopped |
| `system.job.started` | Job Runner | Background job started |
| `system.job.completed` | Job Runner | Job completed |
| `system.job.failed` | Job Runner | Job failed |
| `system.job.retried` | Job Runner | Job retried |
| `system.alert.triggered` | Monitor | Alert triggered |

## EM.4 Event Processing Guarantees

### Idempotency
Every event has a unique `idempotency_key`. Event handlers must:
1. Check if event already processed (by idempotency key)
2. If processed: skip
3. If not processed: process and record

```python
async def handle_event(event):
    if await is_processed(event.idempotency_key):
        logger.info(f"Event already processed: {event.idempotency_key}")
        return

    async with transaction():
        await process_event(event)
        await mark_processed(event.idempotency_key)
```

### Ordering
- Events within a conversation are ordered by timestamp
- Cross-conversation events: eventual consistency acceptable
- Critical sequences (offer → book) use version checks, not event ordering

### Retry
- Transient failures: exponential backoff (1s, 2s, 4s, 8s, max 30s)
- Max retries: 5
- After max retries: move to dead-letter queue
- DLQ: manual review required, auto-alert to ops

### Dead Letter Queue
```json
{
  "original_event": { ... },
  "failure_reason": "...",
  "retry_count": 5,
  "last_retry_at": "2025-10-01T15:00:00Z",
  "requires_manual_action": true
}
```

## EM.5 Event Schema Validation

All events are validated against JSON schemas on ingestion:
```python
from pydantic import BaseModel, ValidationError

class BaseEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    tenant_id: str
    idempotency_key: str
    security_classification: str

# Reject invalid events at ingestion
try:
    event = BaseEvent(**raw_event)
except ValidationError as e:
    await send_to_dlq(raw_event, str(e))
    raise
```

## EM.6 Event Storage

Events are stored in:
1. **Primary:** PostgreSQL (events table) for transactional queries
2. **Archive:** S3 (Parquet) for analytics and long-term retention
3. **Hot cache:** Redis for recent event lookups

Retention:
- PostgreSQL: 90 days (hot)
- S3: 7 years (compliance requirement)
- Redis: 7 days (LRU eviction)
