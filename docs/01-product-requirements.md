# Product Requirements — HeyJarvis Patient Recapture System

## PR.1 Document Purpose

This document defines what HeyJarvis Patient Recapture is, what it must do, and what it must NOT do. It serves as the binding specification for engineering, design, and QA.

## PR.2 What It Is

HeyJarvis Patient Recapture is an AI-augmented system that identifies dental patients who failed to complete a desired action (book, confirm, show up, continue treatment, return for recall) and executes personalized, compliant, safe outreach to recover the relationship and the appointment.

It is NOT:
- A generic chatbot
- A marketing spam tool
- A patient engagement dashboard
- An EHR replacement

It IS:
- A deterministic eligibility engine with AI augmentation
- A compliance-first patient communication system
- A revenue recovery tool designed for dental practices
- A safety-first healthcare communication platform

## PR.3 Core Product Principles

1. **Safety before conversion.** Every safety rule is deterministic and cannot be overridden by AI.
2. **Rules before AI.** Policy and eligibility are always determined by rules. AI only personalizes within approved boundaries.
3. **External systems are sources of truth.** The AI never fabricates appointments, insurance, or availability. It queries real systems.
4. **No unsupported claims.** AI must never claim an action occurred unless the backend confirms it.
5. **Human override always exists.** Every AI action can be reviewed, overridden, or blocked by staff.
6. **Patient trust > revenue optimization.** Aggressive tactics that risk patient trust are prohibited.
7. **Explainable by default.** Every outreach decision can be explained to the practice, the patient, and a regulator.
8. **PHI minimization.** Only the minimum necessary patient data is used at each step.

## PR.4 Functional Requirements

### FR-1: Opportunity Identification
The system MUST automatically detect recapture opportunities from:
- Lead form submissions without booking
- Abandoned booking flows
- Appointments offered but not confirmed
- Appointments cancelled
- No-shows
- Treatment plans created but unscheduled
- Overdue recalls
- Inactive patients
- Missed calls
- After-hours leads
- Unresolved contact requests

### FR-2: Eligibility Determination
For each opportunity, the system MUST evaluate:
- Patient opt-out status
- Consent for the communication channel
- Frequency caps (per patient, per channel, per campaign)
- Time since last contact
- Practice quiet hours and business hours
- Patient timezone
- Duplicate detection (no double outreach for same opportunity)
- Staff manually marked as "do not pursue"
- Prior campaign membership

### FR-3: Patient Communication
The system MUST:
- Generate personalized, contextually relevant messages
- Use only verified, structured data for personalization
- Never fabricate names, dates, appointments, insurance coverage, prices, or availability
- Include clear opt-out instructions in every outreach
- Respect quiet hours (configurable per practice)
- Adapt message to patient's language preference
- Track delivery status
- Handle patient responses
- Support multi-step campaign sequences with configurable delays

### FR-4: Booking and Scheduling
The system MUST:
- Query real scheduling systems for availability
- Hold slots temporarily before booking
- Confirm booking through the practice management system
- Never confirm a booking that hasn't been verified by the PMS
- Handle scheduling conflicts gracefully
- Support rescheduling and cancellation
- Create confirmation messages for patients

### FR-5: Safety and Escalation
The system MUST:
- Classify patient messages for safety concerns before any other processing
- Escalate emergency-like symptoms to human staff immediately
- Never diagnose, prescribe, or give clinical advice
- Recognize when it doesn't know and defer to human staff
- Log all safety escalations with full context
- Provide deterministic emergency response protocols

### FR-6: Human Handoff
The system MUST:
- Detect situations requiring human intervention
- Create handoff records with full conversation context
- Notify appropriate staff via configurable channels
- Resume AI conversation when handoff is resolved
- Track handoff SLA and resolution time

### FR-7: Campaign Management
The system MUST support:
- Pre-built and custom campaign templates
- Configurable entry conditions
- Configurable step sequences with delays
- Frequency caps and cooldown periods
- Stop conditions (booked, declined, opted out, handoff, etc.)
- A/B testing variants
- Campaign pause/resume

### FR-8: Analytics and Reporting
The system MUST provide:
- Recapture rate by category, campaign, clinic
- Revenue recovered
- Response rate
- Conversion rate
- Booking completion rate
- AI containment rate
- Human handoff rate and reason breakdown
- Channel performance
- Campaign performance
- Time-to-book metrics
- Opt-out rate
- Patient satisfaction signals

### FR-9: Staff Dashboard
The system MUST provide:
- Overview of active opportunities
- Conversation inbox with patient context
- Human handoff queue with priority
- Campaign management
- Analytics views
- Patient timeline
- Integration health status
- Suppression/consent management

### FR-10: Multi-Channel Support
The system MUST support:
- SMS (primary)
- Email
- Website chat
- Voice (V2)
- WhatsApp (V2, where legally permitted)

Each channel has its own:
- Consent requirements
- Rate limits
- Delivery tracking
- Opt-out mechanism
- Best-use cases

## PR.5 Non-Functional Requirements

### NFR-1: Security
- All data encrypted at rest (AES-256) and in transit (TLS 1.3)
- Row-level security for multi-tenancy
- RBAC with least privilege
- PHI never exposed in logs
- Audit logs for every patient-facing action
- Secrets managed in vault, never in code or env vars

### NFR-2: Compliance
- HIPAA BAA with all subprocessors handling PHI
- TCPA-compliant SMS (consent, opt-out, timing)
- CAN-SPAM compliant email
- State-specific healthcare communication rules where applicable
- Data retention policies
- Patient data deletion support

### NFR-3: Reliability
- 99.9% uptime for API (measured monthly)
- 99.5% message delivery (excluding provider outages)
- Webhook deduplication (idempotent processing)
- Graceful degradation when subsystems fail
- No false booking confirmations

### NFR-4: Performance
- AI response time < 5 seconds (p95)
- Message delivery < 30 seconds (p95)
- Dashboard load < 2 seconds (p95)
- API response time < 200ms (p95)

### NFR-5: Scalability
- Support 200+ dental practices
- 1M+ patients in system
- 100K+ messages per day
- 10K+ concurrent conversations
- Horizontal scaling for workers

### NFR-6: Observability
- Structured logging with correlation IDs
- Metrics for every critical operation
- Distributed tracing for AI conversations
- Alerting on safety events, booking errors, integration failures
- Dashboards for clinical, technical, and business metrics

## PR.6 What The V1 Product MUST NOT Do

The V1 product SHALL NOT:
1. Diagnose dental conditions
2. Prescribe treatment or medication
3. Make clinical recommendations beyond approved triage/escalation
4. Book appointments without PMS confirmation
5. Guarantee insurance coverage
6. Fabricate any patient-facing information
7. Send messages without consent verification
8. Contact opted-out patients
9. Exceed frequency caps
10. Message outside quiet hours
11. Bypass human escalation for safety events
12. Allow AI to override deterministic policy rules
13. Store PHI in LLM prompts or context beyond what's necessary
14. Share patient data across clinic boundaries
15. Auto-send messages without human review for new campaigns (V1)
16. Initiate voice calls (V1 — SMS and chat only)
17. Process credit card payments
18. Access or modify EHR/EMR clinical records directly
19. Schedule appointments without patient confirmation
20. Claim an action completed unless confirmed by the source system

## PR.7 Success Metrics

| Metric | Target (V1) | Target (V2) | Measurement |
|--------|------------|------------|-------------|
| Booking conversion rate | >15% | >20% | Bookings / outreach attempts |
| Response rate | >20% | >30% | Responses / messages sent |
| Revenue recovered per clinic | >$2K/mo | >$5K/mo | Billing data |
| AI containment rate | >80% | >90% | AI resolved / total |
| Safety escalation accuracy | >99% | >99.5% | Correct / total safety events |
| Handoff accuracy | >90% | >95% | Appropriate handoffs / total |
| Opt-out rate | <0.3% | <0.2% | Opt-outs / messages sent |
| Complaint rate | <0.5% | <0.3% | Complaints / messages sent |
| False booking rate | 0 | 0 | False bookings / total bookings |
| Cross-tenant leakage | 0 | 0 | Incidents |
| Response time (AI) | <5s p95 | <3s p95 | AI response latency |
| Staff time saved | >50% | >70% | Manual follow-up hours |
