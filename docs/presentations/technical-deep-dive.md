# Technical Deep Dive — Engineering Presentation

## Slide 1: Title

```
HEYJARVIS PATIENT RECAPTURE
Technical Architecture Deep Dive

Audience: Engineering Team, CTO, Technical Stakeholders
```

## Slide 2: System Overview

```
WHAT WE'RE BUILDING

A production-grade, multi-tenant, AI-augmented patient recapture system
for U.S. dental practices.

Key Characteristics:
• 24/7 AI availability
• HIPAA + TCPA compliant
• Multi-tenant with strict isolation
• Event-driven architecture
• Tool-verified AI (no hallucination)
• Holdout-based measurement
• Full observability

Scale Targets (Year 1):
• 50 clinics
• 50,000 patients
• 100K messages/month
• 10K conversations/month
• <200ms API p95 latency
• 99.9% uptime
```

## Slide 3: Technology Decisions

```
WHY THESE TECHNOLOGIES?

FastAPI (API)
  ✓ Async Python — natural fit for AI/ML
  ✓ Auto-generated OpenAPI docs
  ✓ Pydantic validation
  ✓ Great performance

PostgreSQL (Database)
  ✓ ACID for appointments (critical)
  ✓ JSONB for flexible data
  ✓ RLS for tenant isolation
  ✓ Mature, well-understood

Redis (Cache + Queue)
  ✓ Sub-millisecond latency
  ✓ Streams for queue (simpler than Kafka for V1)
  ✓ Pub/sub for real-time
  ✓ Can migrate to Kafka later

Anthropic Claude (LLM)
  ✓ Strong safety alignment
  ✓ Good instruction following
  ✓ Reliable API
  ✓ BAA available
  ✓ Good rate limits

Docker + Kubernetes (Infrastructure)
  ✓ Industry standard
  ✓ Auto-scaling
  ✓ Rolling updates
  ✓ Health checks

Terraform (IaC)
  ✓ Multi-cloud
  ✓ Reproducible infrastructure
  ✓ Team familiarity
```

## Slide 4: Database Architecture

```
DATABASE DESIGN

Primary Database: PostgreSQL (RDS)
├── Instance: db.r6g.2xlarge (8 vCPU, 64GB RAM)
├── Storage: 1TB gp3
├── Replicas: 2x db.r6g.xlarge
└── Backup: Daily full + hourly WAL

Key Design Decisions:

1. Row-Level Security (RLS)
   → Every table has tenant_id
   → RLS policies enforce tenant isolation
   → Cannot bypass from application code

2. JSONB for Flexibility
   → Integrations have varying schemas
   → AI context varies by conversation
   → Campaign configs are flexible
   → Still queryable and indexable

3. Audit Trail on Everything
   → audit_logs table captures all changes
   → Triggers on sensitive tables
   → Immutable (no updates/deletes)

4. Idempotency Keys
   → Every external action has idempotency_key
   → Prevents duplicate bookings
   → Prevents duplicate messages

5. Soft Deletes
   → deleted_at timestamp instead of DELETE
   → Maintains referential integrity
   → Enables data recovery
```

## Slide 5: State Machine — Patient Lifecycle

```
PATIENT STATE MACHINE

States: 20 defined states
Transitions: 40+ defined transitions
Rules: Invalid transitions rejected

Key States:
  NEW_LEAD → CONTACTED → ENGAGED → QUALIFIED → BOOKING_PENDING → BOOKED → CONFIRMED → COMPLETED

Failure States:
  LEAD_ABANDONED
  NO_RESPONSE
  CANCELLED
  NO_SHOW
  RESCHEDULE_PENDING
  OPTED_OUT
  SAFETY_ESCALATION
  HUMAN_HANDOFF

Why a State Machine?
  ✓ Deterministic behavior
  ✓ Prevents invalid transitions
  ✓ Easy to test
  ✓ Easy to debug
  ✓ Auditable
  ✓ Self-documenting

Implementation:
  State stored in recapture_opportunities.state
  Transitions validated in policy engine
  Invalid transitions logged and rejected
```

## Slide 6: Event-Driven Architecture

```
EVENT SYSTEM

Event Types: 40+ defined events
Event Format: Envelope with metadata + payload

Event Envelope:
{
  "event_id": "uuid",
  "event_type": "appointment.cancelled",
  "timestamp": "2025-10-01T14:30:00Z",
  "tenant_id": "clinic-uuid",
  "patient_id": "patient-uuid",
  "correlation_id": "trace-uuid",
  "source": "pms_sync",
  "idempotency_key": "unique-key",
  "payload": { ... event-specific data ... }
}

Event Flow:
  Producer → Queue → Consumer → Handler → Side Effects

Queue: Redis Streams (V1)
  Consumer Groups: One per event type
  Retry: Exponential backoff (3 retries)
  DLQ: After 3 failures → alert + manual review
  Idempotency: idempotency_key prevents duplicates

Example Event Flow:
  1. PMS webhook: appointment.cancelled
  2. API validates + adds to queue
  3. Campaign consumer picks up
  4. Evaluates eligibility (policy engine)
  5. If eligible → creates recapture_opportunity
  6. Schedules first outreach attempt
  7. Analytics consumer records metric
  8. Audit consumer logs event
```

## Slide 7: AI Architecture

```
AI SYSTEM DESIGN

Three-Tier Architecture:

TIER 0: Deterministic Rules
  Input: Event + patient data
  Process: Rule evaluation
  Output: Yes/No decision
  Cost: $0
  Used for: Consent, opt-out, frequency caps, safety patterns

TIER 1: Small LLM (Classification)
  Input: Patient message
  Process: Intent + safety classification
  Output: Structured intent, safety flags
  Cost: ~$0.01/call
  Used for: Intent classification, safety detection, reason extraction

TIER 2: Strong LLM (Generation)
  Input: Context + intent + verified data
  Process: Conversation + message generation
  Output: Personalized response
  Cost: ~$0.05/call
  Used for: Message generation, conversation responses

TIER 3: ML Models (Prediction)
  Input: Patient + campaign features
  Process: Gradient boosting prediction
  Output: Probability scores
  Cost: ~$0.001/prediction
  Used for: Conversion prediction, priority scoring, timing

Safety at Every Tier:
  Tier 0: Emergency keywords (deterministic)
  Tier 1: Safety classifier (AI-assisted)
  Tier 2: Output validation (deterministic)
  Tier 3: No safety concerns (only scoring)

No AI can:
  ✗ Bypass consent checks
  ✗ Override opt-out
  ✗ Bypass frequency caps
  ✗ Bypass quiet hours
  ✗ Fabricate appointments
  ✗ Fabricate insurance
  ✗ Diagnose
  ✗ Prescribe
```

## Slide 8: Tool Calling Architecture

```
TOOL CALLING DESIGN

Why Tools?
  AI needs current, verified data.
  Training data is stale.
  LLMs hallucinate when asked for specific info.

Tool Categories:

1. Read-Only Tools (No Confirmation)
   get_patient_info(patient_id)
   get_clinic_info(clinic_id)
   get_services(clinic_id)
   get_appointment_types()
   check_insurance_eligibility(patient_id, service_id)

2. Action Tools (Patient Confirmation Required)
   hold_appointment_slot(patient_id, slot_id)
   book_appointment(patient_id, slot_id)
   reschedule_appointment(appointment_id, new_slot)
   cancel_appointment(appointment_id, reason)

3. Admin Tools (Staff Only)
   create_staff_task(patient_id, task_type, notes)
   update_patient_notes(patient_id, notes)
   mark_opportunity_resolved(opportunity_id, outcome)

Tool Execution:
  AI → Tool Request → Validation → Execution → Result → AI Response

Safety:
  ✓ Tool allowlist (no arbitrary tool calling)
  ✓ Schema validation (correct arguments)
  ✓ Tenant scoping (can't access other clinics)
  ✓ Audit logging (every tool call logged)
  ✓ Patient confirmation (for booking tools)

Example Flow:
  Patient: "Can I book for today at 3pm?"
  AI: Calls check_availability(date="today", type="cleaning")
  Tool: Returns ["3:20 PM", "4:00 PM", "4:40 PM"]
  AI: "We have 3:20 PM available. Want me to book it?"
  Patient: "Yes"
  AI: Calls hold_slot(slot_id="3:20pm-123")
  AI: "I've held 3:20 PM for you. Confirming now..."
  AI: Calls book_appointment(patient_id, slot_id) → Success
  AI: "You're confirmed for today at 3:20 PM."
```

## Slide 9: Safety Architecture

```
SAFETY: MULTI-LAYERED DEFENSE

Layer 1: Pattern Matching (Deterministic)
  Keywords: emergency, bleeding, swelling, severe pain, knocked out
  Patterns: "can't breathe", "face is numb", "tooth fell out"
  Response: Immediate safety escalation

Layer 2: Policy Engine (Deterministic)
  Consent check: Can we contact this patient?
  Opt-out check: Has patient opted out?
  Frequency check: Have we messaged too much?
  Quiet hours: Is it appropriate to message now?

Layer 3: Safety Classifier (AI)
  Classifies message as: SAFE / NEEDS_ATTENTION / EMERGENCY
  Catches: "my tooth hurts" vs "I think I'm having a heart attack"
  Response: If EMERGENCY → safety escalation

Layer 4: Intent Classification (AI)
  Classifies: APPOINTMENT / CANCEL / RESCHEDULE / QUESTION / EMERGENCY
  Routes to appropriate handler
  Response: If EMERGENCY → safety escalation

Layer 5: Tool Validation (Deterministic)
  Validates tool arguments
  Ensures tenant scoping
  Logs all tool calls
  Response: Invalid tool call → reject

Layer 6: Output Validation (Deterministic)
  Checks for: Hallucination, medical claims, fabricated data
  Validates: Tool result consistency
  Response: Invalid → reject, use template

Layer 7: Human Review
  All safety events → human
  Uncertain cases → human
  Patient requests → human
```

## Slide 10: Multi-Tenant Architecture

```
TENANT ISOLATION

Mechanisms:

1. JWT-Based Tenant
   Token contains: tenant_id, user_id, roles
   Extracted at gateway
   Never trusted from client input

2. Row-Level Security (RLS)
   Every table has tenant_id
   PostgreSQL RLS enforces tenant filter
   Cannot bypass from application code

3. Tenant-Scoped Queries
   All queries include tenant_id
   Enforced at ORM level
   Tested with cross-tenant test cases

4. Separate Encryption
   Per-tenant encryption keys (future)
   Key rotation per tenant
  Damage containment if key compromised

5. Rate Limiting
   Per-tenant API rate limits
   Per-tenant AI rate limits
   Per-tenant SMS rate limits

6. Configuration Isolation
   Per-tenant message templates
   Per-tenant quiet hours
   Per-tenant escalation rules
   Per-tenant AI policies
```

## Slide 11: Integration Architecture

```
INTEGRATION: ADAPTER PATTERN

Abstract Interface:
  SchedulingProvider (abstract)
    ├── check_availability()
    ├── book_appointment()
    ├── cancel_appointment()
    ├── reschedule_appointment()
    └── get_appointment()

Concrete Implementations:
  OpenDentalProvider extends SchedulingProvider
  EaglesoftProvider extends SchedulingProvider
  DentrixProvider extends SchedulingProvider

Sync Strategy:
  • Full sync: Daily (all appointments, patients)
  • Incremental sync: Every 15 minutes (changes only)
  • Webhook: Real-time (appointment changes)

Conflict Resolution:
  1. PMS is source of truth
  2. Timestamp comparison (last write wins)
  3. Manual review for conflicts

Failure Handling:
  1. Retry with exponential backoff (3 retries)
  2. Fallback to cached data
  3. Alert if stale (>1 hour)
  4. Queue for retry if down
```

## Slide 12: Observability

```
OBSERVABILITY STACK

Logs (Structured JSON):
  • Every request logged with correlation_id
  • Every AI decision logged
  • Every tool call logged
  • Every event logged
  • PHI-safe (no PHI in logs unless required)

Metrics (Prometheus + Datadog):
  • System: latency, errors, throughput
  • Business: opportunities, responses, bookings
  • AI: requests, hallucinations, handoffs
  • Integration: success rate, latency

Traces (OpenTelemetry):
  • End-to-end request tracing
  • AI decision tracing
  • Tool call tracing
  • Integration call tracing

Alerts:
  Critical (PagerDuty):
    • Database down
    • SMS provider down
    • Safety event spike
    • Cross-tenant leak detected
    • Booking failure spike

  Warning (Slack):
    • Queue depth high
    • AI latency high
    • Error rate high
    • Opt-out spike

Dashboards:
  • Operations: System health
  • AI: Model performance
  • Business: Revenue, conversion
  • Compliance: Opt-outs, consent changes
```

## Slide 13: Cost Architecture

```
COST BREAKDOWN (50 Clinics, Monthly)

Infrastructure: $2,830
  • Compute (API + Workers): $1,275
  • Database: $1,300
  • Storage: $80
  • Queue: $100
  • Networking: $75

AI/LLM: $2,010
  • LLM API calls: $2,000
  • Embeddings: $10

Communications: $1,300
  • SMS (100K msgs): $1,250
  • Email (50K msgs): $50

Services: $950
  • Monitoring: $300
  • Logging: $100
  • PMS APIs: $200
  • Insurance APIs: $300
  • Error tracking: $50

Personnel: $82,500

TOTAL: $89,590/month

Cost per clinic: $1,792/month

Per-patient cost: $0.35/month

Optimization:
  • Tiered AI (rules first) → saves 70%
  • Caching (24h for static data) → saves 20%
  • Batch processing → saves 10%
  • Right-sizing → saves 15%

Optimized total: ~$50,000/month
```

## Slide 14: Security Architecture

```
SECURITY LAYERS

Network:
  ✓ VPC with private subnets
  ✓ Security groups (minimal open ports)
  ✓ WAF for API protection
  ✓ DDoS protection

Application:
  ✓ JWT authentication
  ✓ MFA for staff
  ✓ RBAC (role-based access)
  ✓ Rate limiting
  ✓ Input validation
  ✓ SQL injection prevention
  ✓ XSS prevention

Data:
  ✓ AES-256 at rest
  ✓ TLS 1.3 in transit
  • Per-tenant encryption keys (future)
  ✓ Key rotation
  ✓ Secrets in Vault

AI:
  ✓ Prompt injection detection
  ✓ Tool allowlist
  ✓ Output validation
  ✓ Tenant-scoped context

Monitoring:
  ✓ Audit logs (immutable)
  ✓ Anomaly detection
  ✓ Security alerts
  ✓ Regular penetration testing

Compliance:
  ✓ BAA with all vendors
  ✓ HIPAA policies documented
  ✓ Regular security reviews
  ✓ Incident response plan
```

## Slide 15: Testing Strategy

```
TESTING PYRAMID

        /\
       /E2E\     10 tests — Full user journeys
      /------\
     /Integr.\  50 tests — Component interactions
    /----------\
   /   Unit     \ 500+ tests — Individual functions
  /--------------\

AI-Specific Tests:
  • Safety test suite: 50+ test cases
  • Hallucination tests: 100+ test cases
  • Adversarial tests: 20+ attack vectors
  • Prompt regression: Every prompt change
  • Red team exercises: Monthly

Performance Tests:
  • Load: 10K concurrent conversations
  • Stress: 100K messages/hour
  • Endurance: 24-hour sustained load
  • Spike: Sudden traffic burst

Security Tests:
  • Penetration testing: Quarterly
  • Vulnerability scanning: Daily
  • Secret scanning: Every commit
  • Dependency scanning: Every PR
  • OWASP Top 10: All covered

Test Coverage Target: >90%
```
