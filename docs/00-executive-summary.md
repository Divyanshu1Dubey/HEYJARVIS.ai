# HeyJarvis Patient Recapture System — Complete Product Architecture & Implementation Specification

**Version:** 1.0  
**Date:** 2026-09-30  
**Status:** Specification Draft  
**Classification:** Confidential — HeyJarvis.ai Internal

---

## Document Index

| # | Document | Description |
|---|----------|-------------|
| 00 | Executive Summary | Product vision, value proposition, market positioning |
| 01 | Product Requirements | Functional and non-functional requirements |
| 02 | User Personas | Dental practice staff, patients, administrators |
| 03 | Use Cases | All recapture scenarios and workflows |
| 04 | Recapture Taxonomy | Complete classification of recapture opportunities |
| 05 | Event Model | Event-driven architecture specification |
| 06 | State Machine | Patient/opportunity state machine design |
| 07 | System Architecture | Complete system architecture |
| 08 | Data Architecture | Data flow, storage, and architecture |
| 09 | Database Schema | Complete relational schema |
| 10 | API Specification | REST API and event API design |
| 11 | Integration Architecture | Dental system integration adapter design |
| 12 | AI Architecture | LLM, ML, and rules engine design |
| 13 | Model Training Plan | ML model training strategy |
| 14 | Dataset Specification | Training and evaluation datasets |
| 15 | LLM Prompt Specification | Production prompt templates |
| 16 | Safety Policy | Medical safety boundaries and policies |
| 17 | Human Handoff | Escalation and human-in-the-loop design |
| 18 | Compliance | HIPAA, TCPA, and regulatory requirements |
| 19 | Security | Security architecture and controls |
| 20 | Threat Model | Security threat model |
| 21 | Red Team Plan | AI red-team testing plan |
| 22 | Evaluation Framework | Model and system evaluation |
| 23 | Testing Strategy | Complete testing approach |
| 24 | Observability | Monitoring, logging, and alerting |
| 25 | Incident Response | Incident response procedures |
| 26 | Disaster Recovery | DR and backup strategy |
| 27 | Cost Model | Cost analysis and optimization |
| 28 | Analytics | Analytics and KPI design |
| 29 | Experimentation | A/B testing and experimentation |
| 30 | UI/UX Specification | Staff dashboard and patient UX |
| 31 | Runbooks | Operational runbooks |
| 32 | Deployment | Deployment architecture |
| 33 | Rollout Plan | Phased rollout strategy |
| 34 | Implementation Roadmap | MVP to production roadmap |

Supporting:
- ADRs (Architecture Decision Records)
- Diagrams (architecture, data flow, sequence, state, ERD)
- 100+ Scenarios catalog
- Failure Mode Analysis (FMEA)
- Production Readiness Checklist

---

# PART A — EXECUTIVE PRODUCT VISION

## A.1 What Is HeyJarvis Patient Recapture?

HeyJarvis Patient Recapture is an AI-powered, event-driven system that sits between a dental practice and its patients, continuously identifying patients who have dropped out of the appointment funnel and autonomically or semi-autonomically re-engaging them to recover lost revenue.

It is NOT a chatbot.
It is NOT a marketing automation tool.
It is NOT a generic customer engagement platform.

It is a **clinical-adjacent, revenue-recovery operating system** for dental practices that:

1. Listens to every patient interaction event across all channels
2. Classifies why each patient dropped out
3. Determines whether, when, and how to re-engage
4. Generates personalized, policy-compliant outreach
5. Executes through the right channel (SMS, email, voice, staff task)
6. Schedules, reschedules, or books appointments when patients respond
7. Hands off to staff when AI confidence is low or safety requires it
8. Learns from every outcome to improve future decisions

## A.2 The Problem We Solve

Dental practices lose 20-40% of potential revenue to patient dropout at various stages of the appointment journey:

- **Leads who never book:** A patient fills out a website form asking about Invisalign, gets no response within hours, and calls a competitor.
- **Appointment abandoners:** A patient selects a time slot online but never confirms. The slot goes unused.
- **Cancellations that become permanent losses:** A patient cancels due to a scheduling conflict and is never recontacted.
- **No-shows who never reschedule:** After a no-show, some practices send a single text. Many patients need personalized re-engagement.
- **Treatment plans that stall:** A dentist presents a \$3,000 treatment plan. The patient says "I'll think about it." Nobody follows up systematically.
- **Recall patients who drift away:** Overdue hygiene patients represent preventive care gaps and revenue loss.

The practice staff is too busy with in-office patients to systematically follow up. Manual follow-up is inconsistent, delayed, and poorly prioritized.

## A.3 Our Solution

HeyJarvis Patient Recapture replaces inconsistent manual follow-up with:

- **Continuous monitoring** of every patient touchpoint
- **Intelligent prioritization** of which patients to contact and when
- **Personalized outreach** that respects patient preferences and consent
- **Deterministic safety** — rules that never get overridden by AI
- **Seamless scheduling** — AI can book and reschedule through PMS integrations
- **Staff augmentation** — AI handles the 80%, staff handles the 20% that needs human judgment
- **Full auditability** — every decision, message, and outcome is logged and explainable

## A.4 Core Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Practice Owner** | Recovered revenue, reduced staff burden, measurable ROI |
| **Front Desk Staff** | AI handles routine follow-up, staff focuses on in-office patients and complex cases |
| **Dentist** | Treatment plans get completed, patients get care they need |
| **Patient** | Timely, relevant, respectful communication — feels like the practice cares |
| **Compliance Officer** | Full audit trail, consent management, HIPAA-aligned architecture |
| **IT Administrator** | Reliable integrations, no hallucinated data, deterministic behavior |

## A.5 What This System Is NOT

| NOT This | Why |
|----------|-----|
| A marketing chatbot | No broadcast campaigns, no lead-gen funnels |
| A patient engagement platform | Not designed for education content or wellness programs |
| A telemedicine system | No diagnosis, no treatment advice, no prescribing |
| A CRM replacement | Integrates with existing practice systems, doesn't replace them |
| A generic AI assistant | Purpose-built for dental recapture with clinical safety boundaries |
| An outbound spam engine | Strict frequency caps, suppression lists, consent-first design |

## A.6 North Star Metrics

| Metric | Target (V1) | Target (Mature) |
|--------|-------------|-----------------|
| Revenue recovered per practice/month | \$2,000+ | \$8,000+ |
| Booking recovery rate (from outreach) | 15-25% | 30-40% |
| AI containment rate (no human needed) | 80%+ | 90%+ |
| False positive rate (wrong patient contacted) | < 1% | < 0.5% |
| Patient opt-out rate | < 2% | < 1% |
| Patient complaint rate | < 0.5% | < 0.2% |
| Average time to re-engage | < 2 hours | < 30 minutes |

---

# PART B — EXACT PRODUCT DEFINITION

## B.1 Product Statement

HeyJarvis Patient Recapture is a deterministic-first, AI-augmented system for dental practices that identifies patients who have dropped out of the appointment lifecycle, makes intelligent decisions about re-engagement, executes personalized outreach through appropriate channels, and recovers appointments and revenue while maintaining strict clinical safety and regulatory compliance boundaries.

## B.2 What V1 Must NOT Do

**Hard boundaries for V1:**

1. **Must NOT diagnose** — No medical diagnosis under any circumstances
2. **Must NOT prescribe** — No medication or treatment recommendations
3. **Must NOT independently assess clinical severity** — Emergency signals trigger human escalation only
4. **Must NOT book appointments without PMS confirmation** — External system is source of truth
5. **Must NOT fabricate insurance information** — Insurance status comes from verified API data only
6. **Must NOT claim actions that didn't happen** — Booking must be confirmed by external system
7. **Must NOT bypass opt-out** — Opt-out is inviolable, enforced by policy engine before any AI processing
8. **Must NOT generate arbitrary messages** — All messages use approved templates with structured data
9. **Must NOT learn in production without validation** — No model updates without offline evaluation
10. **Must NOT contact patients outside consent and policy boundaries** — Enforced by policy engine

## B.3 System Identity

The system identifies itself to patients as:
- Brand: HeyJarvis (practice name optionally added)
- Role: AI assistant helping connect patients with the dental practice
- Capability: Answer questions, help with scheduling, facilitate communication
- Limitation: Not a medical professional, not a substitute for clinical advice

The system identifies itself to practice staff as:
- An AI-powered recapture engine
- Operating within configured safety and compliance boundaries
- Providing full audit trail and explainability for all decisions

## B.4 Minimum Production-Safe Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PATIENT CHANNELS                               │
│  SMS ◄──► Email ◄──► Web Chat ◄──► Voice ◄──► Patient Portal       │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    COMMUNICATION ADAPTER LAYER                        │
│  SMS Gateway │ Email Service │ Chat Widget │ Voice Gateway            │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                         API GATEWAY                                   │
│         Auth │ Rate Limit │ Validation │ Tenant Isolation             │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                      EVENT INGESTION BUS                              │
│              Event Broker │ Schema Validation │ Dedup                  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  POLICY       │    │  RECAPTURE      │    │  CONVERSATION   │
│  ENGINE       │    │  ENGINE         │    │  ENGINE         │
│  (Rules)      │    │  (ML + Rules)   │    │  (LLM + Tools)  │
└───────┬───────┘    └────────┬────────┘    └────────┬────────┘
        │                     │                       │
        ▼                     ▼                       ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Suppression  │    │  Scoring        │    │  Intent         │
│  Consent      │    │  Priority       │    │  Tools          │
│  Safety       │    │  Channel Select │    │  Validation     │
│  Frequency    │    │  Timing         │    │  Memory         │
│  Quiet Hours  │    │  Strategy       │    │  Handoff        │
└───────┬───────┘    └────────┬────────┘    └────────┬────────┘
        │                     │                       │
        └─────────────────────┼───────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    MESSAGE GENERATION                                │
│           Template Engine │ Personalization │ Validation              │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    EXECUTION & DELIVERY                              │
│           Message Queue │ Channel Dispatch │ Delivery Tracking        │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  PRACTICE     │    │  ANALYTICS      │    │  STAFF          │
│  SYSTEMS      │    │  ENGINE         │    │  DASHBOARD      │
│  (PMS/EHR)    │    │  (Events + ML)  │    │  (Web App)      │
└───────────────┘    └─────────────────┘    └─────────────────┘
```

## B.5 What Should Be Deterministic

| Component | Deterministic? | Reason |
|-----------|---------------|--------|
| Opt-out enforcement | **YES** | Legal requirement, no exceptions |
| Suppression list checks | **YES** | Prevents spam, patient trust |
| Consent verification | **YES** | TCPA/HIPAA requirement |
| Quiet hour enforcement | **YES** | Legal and patient trust |
| Frequency cap enforcement | **YES** | Prevents spam |
| Booking confirmation | **YES** | External system is source of truth |
| Insurance verification | **YES** | Use API data only, never LLM |
| Appointment availability | **YES** | Query PMS, never hallucinate |
| Safety escalation triggers | **YES** | Patient safety |
| Tenant isolation | **YES** | Data security |
| Audit logging | **YES** | Compliance |
| Payment processing | **N/A** | Not in V1 scope |
| Identity verification | **YES** | Security |

## B.6 Where AI/ML Is Used

| Use Case | Technology | Confidence Required |
|----------|-----------|---------------------|
| Intent classification | LLM (small) | Medium |
| Recapture reason classification | LLM (small) | Medium |
| Urgency detection | LLM + rules | High |
| Message personalization | LLM | Medium |
| Conversation understanding | LLM | Medium |
| Recapture priority scoring | Gradient Boosting | High |
| Conversion probability | Calibrated classifier | High |
| Optimal contact time | Survival model | Medium |
| Response prediction | Logistic regression | Medium |
| Next-best-action selection | Rules + ranked model | High |
| Message quality scoring | LLM judge | Medium |
| Safety classification | LLM + rules | High |

## B.7 What Data Should Be Collected

**Always collected (with consent):**
- Patient contact events (inbound/outbound, channel, timestamp)
- Appointment history (created, modified, cancelled, completed, no-show)
- Communication preferences (channel, frequency, language)
- Consent records (when, how, what for)
- Outreach outcomes (delivered, opened, clicked, replied, booked, opted-out)
- AI decisions (what was decided, why, confidence)
- Staff actions (handoffs, overrides, notes)

**Collected with explicit consent:**
- Insurance information
- Treatment plan details
- Financial/coverage estimates
- Clinical notes from practice

**Never collected:**
- Full credit card numbers (use tokenized payments through PMS)
- Clinical diagnosis by AI
- Patient SSN (unless practice PMS requires it)
- Unnecessary PHI in AI prompts

## B.8 What Should Be Evaluated Before Real Patients

| Evaluation | Pass Criteria |
|------------|---------------|
| Safety regression suite | 100% pass — zero safety violations |
| LLM hallucination rate | < 0.5% on evaluation set |
| Wrong-patient contact rate | 0% in evaluation (test with synthetic identities) |
| Opt-out enforcement | 100% — zero violations in test |
| Booking confirmation | 100% — zero unconfirmed booking claims |
| Integration failure handling | Graceful degradation tested |
| Cross-tenant data leakage | Zero leaks in security tests |
| Prompt injection resistance | All adversarial prompts blocked |
| Message template validation | 100% compliance |
| Human handoff SLA | Within configured thresholds |
| Webhook idempotency | No duplicate processing |

---

# PART C — USER JOURNEYS

## C.1 Dental Practice Staff Journeys

### C.1.1 Front Desk Manager — Daily Operations

**Persona:** Sarah, 38, Office Manager at a 3-provider general dentistry practice. 8 years experience. Manages 2 front desk staff. Concerned about missed revenue and staff burnout.

**Morning routine:**
1. Opens HeyJarvis dashboard
2. Reviews overnight recapture queue (patients who abandoned leads, missed calls)
3. Sees 12 opportunities prioritized by revenue impact
4. Approves top 5 for AI autonomous outreach
5. Assigns 3 complex cases (insurance dispute, angry patient, elderly patient) to staff

**During the day:**
1. Receives notification: AI handed off a patient who asked about medication
2. Takes over conversation via dashboard
3. Resolves and marks as "handled"
4. Reviews AI performance metrics

**End of day:**
1. Reviews campaign performance
2. Sees 8 appointments recovered this week = ~\$4,200 in recovered revenue
3. Adjusts campaign settings for next week

### C.1.2 Dentist — Treatment Plan Follow-up

**Persona:** Dr. Patel, 45, Practice Owner. Concerned about treatment acceptance rates. Wants patients to get needed care without being pushy.

**Workflow:**
1. Completes exam, creates treatment plan in PMS
2. Treatment plan automatically appears in HeyJarvis as recapture opportunity
3. AI generates personalized follow-up sequence
4. Dr. Patel reviews and approves AI messages
5. AI sends follow-up at optimal time based on patient engagement history
6. Patient responds with questions
7. AI answers using verified clinic information, offers to schedule
8. Patient books appointment
9. Dr. Patel sees completed treatment in dashboard

### C.1.3 Front Desk Staff — Handoff Response

**Persona:** Maria, 24, Front Desk. Handles phones, check-ins, and patient questions. Often overwhelmed during morning rush.

**Workflow:**
1. Receives push notification: "New patient handoff — elderly patient confused about appointment"
2. Clicks notification, sees full conversation context
3. Patient has been waiting 3 minutes
4. Maria picks up phone, has full context of what patient discussed with AI
5. Resolves issue efficiently
6. Marks handoff as resolved

## C.2 Patient Journeys

### C.2.1 Abandoned Lead — Website Form

**Patient:** Jennifer, 32. New to the area. Submitted inquiry form about teeth whitening at 9 PM. Never heard back.

**Journey:**
1. Jennifer submits form on practice website at 9:00 PM
2. `lead.created` event fires
3. HeyJarvis stores lead, queues for next-business-day contact
4. Next morning at 10:00 AM (within quiet hours, after 9 AM):
   - AI checks: consent exists, not suppressed, frequency cap not exceeded
   - AI generates: "Hi Jennifer! Thanks for your interest in teeth whitening. We'd love to help! Are you still looking to schedule?"
5. Jennifer receives SMS at 10:02 AM
6. Jennifer replies: "Yes! How much does it cost?"
7. AI retrieves verified pricing from clinic data: "\$350 for in-office Zoom Whitening"
8. Jennifer: "Can I book for next Tuesday?"
9. AI checks availability, offers slot
10. Jennifer confirms
11. Appointment booked, confirmation sent
12. Practice gets new patient appointment

### C.2.2 Cancelled Patient — Reschedule

**Patient:** Robert, 58. Long-time patient. Cancelled root canal due to work conflict. No follow-up from practice.

**Journey:**
1. Robert cancels via SMS link at 2:00 PM Tuesday
2. `appointment.cancelled` event fires with reason "scheduling_conflict"
3. Policy engine: eligible for recapture (not opted out, not staff-owned)
4. AI determines: reschedule offer appropriate
5. Waits 2 hours (not immediately — gives patient time)
6. At 4:15 PM: "Hi Robert, sorry we couldn't see you Tuesday. We have openings Thursday at 2 PM or Friday at 10 AM. Would either work?"
7. Robert replies: "Thursday works"
8. AI books appointment
9. Confirmation sent

### C.2.3 No-Show — Recover

**Patient:** Maria, 41. No-showed for hygiene appointment. Second no-show in 6 months.

**Journey:**
1. Appointment time passes, no arrival
2. `appointment.no_show` event fires
3. Policy engine: repeat no-show, flag for staff awareness
4. AI sends message at 2:00 PM: "Hi Maria, we missed you today! Everything okay? We'd love to reschedule."
5. Maria replies: "I totally forgot, so sorry!"
6. AI: "No problem! We have openings tomorrow at 10 AM or 3 PM."
7. Maria: "10 AM works"
8. AI reschedules
9. Staff notified: "Maria — repeat no-show rescheduled for tomorrow 10 AM"

### C.2.4 Treatment Plan Stall

**Patient:** David, 45. Recommended crown at \$1,200. Said "I'll think about it." 3 weeks passed.

**Journey:**
1. Treatment plan created in PMS
2. `treatment_plan.created` event fires
3. AI monitors: no appointment scheduled within 7 days
4. Day 7: "Hi David, following up on your treatment plan for tooth #14. Do you have any questions we can help with?"
5. David: "Is it covered by insurance?"
6. AI checks insurance API: "Your insurance covers 50% after deductible. Estimated out-of-pocket: \$600. We can verify exact coverage before proceeding."
7. David: "Let me verify with my insurance first"
8. AI: "Of course! We'll send the estimate to your email. Feel free to reach out when you're ready."
9. AI schedules follow-up in 14 days
10. Day 21: "Hi David, checking in. Did you have a chance to review the estimate?"
11. David: "Yes, let's book it"
12. AI schedules crown appointment

### C.2.5 Overdue Recall

**Patient:** Susan, 67. Last hygiene visit was 14 months ago. Due for 6-month recall.

**Journey:**
1. Recall due date passes
2. `recall.due` event fires
3. AI checks: last contact, patient preference, no upcoming appointments
4. Sends: "Hi Susan! It's been a while since your last cleaning. Would you like to schedule your 6-month checkup?"
5. Susan replies: "My husband passed away recently. Can we wait a few months?"
6. AI detects sensitive situation → HUMAN HANDOFF
7. Staff member calls personally, expresses condolences, offers to call back in 3 months
8. AI sets recall reminder for 3 months out
9. Interaction marked: sensitivity flag, do not auto-contact for 90 days

### C.2.6 Emergency Signal — Safety Escalation

**Patient:** Unknown number. Texts: "My tooth is throbbing and my face is swollen I can't breathe right"

**Journey:**
1. Message received via web chat
2. Intent engine classifies: URGENT + POSSIBLE EMERGENCY
3. Safety policy engine triggers: DETECTED_KEYWORDS = [swelling, can't breathe, throbbing]
4. IMMEDIATE HUMAN HANDOFF
5. System response: "Based on what you're describing, we recommend you seek immediate medical attention. If this is an emergency, please call 911 or go to the nearest emergency room. Our office will call you shortly."
6. Staff notified: EMERGENCY — immediate callback required
7. Staff calls within 2 minutes
8. Conversation flagged: clinical safety event
9. No automated outreach after safety event

---

# PART D — RECAPTURE TAXONOMY

## D.1 Complete Recapture Opportunity Taxonomy

### Category A: Lead Recapture

| Opportunity ID | Name | Trigger Event | Entry Condition | Urgency |
|----------------|------|---------------|-----------------|---------|
| A1 | Website Lead — No Response | `lead.created` + no reply within X hours | Lead submitted form, no inbound communication | Medium |
| A2 | Web Chat Abandoned | `conversation.abandoned` | Patient started chat, no resolution, left | High |
| A3 | Phone Lead — Missed Call | `call.missed` | Inbound call during hours, no callback | High |
| A4 | Phone Lead — After Hours | `call.after_hours` | Inbound call outside hours | Medium |
| A5 | Service Inquiry — No Book | `service_inquiry.created` + no booking | Patient asked about specific service, no appointment | Medium |
| A6 | Price Inquiry — No Book | `price_inquiry.created` + no booking | Patient requested pricing, no appointment | Low-Medium |
| A7 | Insurance Inquiry — No Book | `insurance_inquiry.created` + no booking | Patient asked about insurance, no appointment | Medium |
| A8 | Availability Inquiry — No Book | `availability_inquiry.created` + no booking | Patient asked about availability, no appointment | Medium |

### Category B: Booking Recapture

| Opportunity ID | Name | Trigger Event | Entry Condition | Urgency |
|----------------|------|---------------|-----------------|---------|
| B1 | Booking Flow Abandoned | `booking_flow.abandoned` | Started booking, didn't complete | High |
| B2 | Slot Offered — Not Accepted | `appointment.offered` + no response | Slot offered, patient didn't accept within X minutes | Medium |
| B3 | Slot Selected — Not Confirmed | `appointment.hold_expired` | Slot held, hold expired without booking | Medium |
| B4 | "I'll Think About It" | `booking.deferred` | Patient explicitly deferred decision | Medium |
| B5 | "I'll Call Back" — No Call | `booking.deferred` + no callback | Patient said they'd call, didn't within 24h | Medium |
| B6 | Silent Drop-off | `conversation.silent` + X hours no response | Active conversation, patient stopped responding | Medium |

### Category C: Cancellation Recapture

| Opportunity ID | Name | Trigger Event | Entry Condition | Urgency |
|----------------|------|---------------|-----------------|---------|
| C1 | Cancellation — Scheduling Conflict | `appointment.cancelled` (reason=scheduling) | Patient cancelled, reschedule likely | High |
| C2 | Cancellation — Price Concern | `appointment.cancelled` (reason=price) | Cost barrier, address before rebook | Medium |
| C3 | Cancellation — Insurance Uncertainty | `appointment.cancelled` (reason=insurance) | Insurance confusion, verify coverage | Medium |
| C4 | Cancellation — Fear/Anxiety | `appointment.cancelled` (reason=anxiety) | Dental anxiety, gentle re-engagement | Low |
| C5 | Cancellation — Transportation | `appointment.cancelled` (reason=transportation) | Access barrier, offer alternatives | Medium |
| C6 | Cancellation — Timing | `appointment.cancelled` (reason=timing) | Wrong time, offer different slot | High |
| C7 | Cancellation — No Reason | `appointment.cancelled` (reason=none) | Unknown reason, gentle check-in | Medium |
| C8 | Short-Notice Cancellation | `appointment.cancelled` (< 24h before) | Last-minute, harder to reschedule | Medium |

### Category D: No-Show Recapture

| Opportunity ID | Name | Trigger Event | Entry Condition | Urgency |
|----------------|------|---------------|-----------------|---------|
| D1 | First No-Show | `appointment.no_show` (count=1) | First occurrence | Medium |
| D2 | Repeat No-Show | `appointment.no_show` (count>=2) | Second+ occurrence, flag for staff | High |
| D3 | No-Show — No Reschedule | `appointment.no_show` + 24h no reschedule | Didn't reschedule within 24h | High |
| D4 | No-Show — Unreachable | `no_show` + contact_failed | Could not reach patient | High |

### Category E: Treatment Recapture

| Opportunity ID | Name | Trigger Event | Entry Condition | Urgency |
|----------------|------|---------------|-----------------|---------|
| E1 | Treatment Plan — No Appointment | `treatment_plan.accepted` + no appointment | Accepted plan, never scheduled | High |
| E2 | Treatment Plan — Not Accepted | `treatment_plan.created` + no response | Presented plan, no response in X days | Medium |
| E3 | Treatment — Partially Complete | `appointment.completed` + remaining items | Multi-visit treatment, items remain | High |
| E4 | Crown/Implant Not Scheduled | Procedure type in plan, no appointment | High-value procedure stalled | High |
| E5 | Root Canal Not Scheduled | Procedure type in plan, no appointment | Urgent procedure, potential emergency | High |
| E6 | Orthodontic Not Scheduled | Procedure type in plan, no appointment | Long-term treatment, gentle follow-up | Low |
| E7 | Periodontal Not Scheduled | Procedure type in plan, no appointment | Health-critical, address concerns | High |
| E8 | Cosmetic Not Scheduled | Procedure type in plan, no appointment | Optional, respect autonomy | Low |
| E9 | Treatment Estimate Sent — No Response | `estimate.sent` + no response | Financial document sent, no reply | Medium |

### Category F: Recall / Reactivation

| Opportunity ID | Name | Trigger Event | Entry Condition | Urgency |
|----------------|------|---------------|-----------------|---------|
| F1 | Overdue Hygiene Recall | `recall.due` (type=hygiene) | Past due for cleaning | Medium |
| F2 | Overdue Periodic Exam | `recall.due` (type=exam) | Past due for exam | Medium |
| F3 | Inactive Patient — 6 Months | `patient.inactive` (6mo) | No visit in 6 months | Low |
| F4 | Inactive Patient — 12 Months | `patient.inactive` (12mo) | No visit in 12 months | Medium |
| F5 | Inactive Patient — 24+ Months | `patient.inactive` (24mo) | No visit in 24+ months | Low |
| F6 | Post-Treatment No Return | `treatment.completed` + no recall due | Treatment done, no follow-up visit | Medium |
| F7 | Continuing Care Gap | `appointment.completed` + no next scheduled | Visited but no future appointment | Medium |

### Category G: Post-Visit Opportunities

| Opportunity ID | Name | Trigger Event | Entry Condition | Urgency |
|----------------|------|---------------|-----------------|---------|
| G1 | Post-Visit Follow-up Needed | `appointment.completed` | Treatment required follow-up discussion | Low |
| G2 | Recall Scheduling | `appointment.completed` | Natural time to schedule next visit | Low |
| G3 | Review Request | `appointment.completed` (positive signal) | Satisfied patient, appropriate timing | Low |

### Category H: Missed Operational Opportunities

| Opportunity ID | Name | Trigger Event | Entry Condition | Urgency |
|----------------|------|---------------|-----------------|---------|
| H1 | Missed Call — No Voicemail | `call.missed` (no voicemail) | Missed during hours, no message | High |
| H2 | After-Hours Lead | `lead.after_hours` | Submitted outside business hours | High |
| H3 | Weekend Lead | `lead.weekend` | Submitted on weekend | High |
| H4 | Unresolved Contact Request | `contact_request.created` + X hours unresolved | Patient requested contact, none made | High |
| H5 | Staff Task Incomplete | `staff_task.created` + not completed | Follow-up task assigned, not done | Medium |
| H6 | Insurance Verification Pending | `insurance.verification_pending` + X days | Verification started but incomplete | Medium |

---

# PART E — COMPLETE SYSTEM ARCHITECTURE

## E.1 Architecture Principles

1. **Rules before AI** — Deterministic policy gates all AI decisions
2. **AI never becomes source of truth** — External systems own appointments and patient records
3. **Never claim actions that didn't happen** — Only confirmed actions are communicated
4. **LLM cannot bypass authorization** — All tool calls go through authorization layer
5. **Minimize PHI exposure** — PHI only where needed, redacted in logs
6. **Every AI action explainable** — Full audit trail for all decisions
7. **Every external action idempotent** — No duplicate side effects
8. **Every critical workflow has fallback** — Graceful degradation everywhere
9. **Human override always exists** — Staff can take over any conversation
10. **Safety beats conversion** — Patient safety always overrides business goals

## E.2 Complete System Architecture

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                           PATIENT-FACING CHANNELS                            ║
║  SMS ◄─────── Email ◄─────── Web Chat ◄─────── Voice ◄─────── Portal      ║
╚══════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CHANNEL ADAPTER LAYER                                 ║
║  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    ║
║  │ SMS GW   │  │ Email    │  │ Chat     │  │ Voice    │  │ Portal   │    ║
║  │ Adapter  │  │ Adapter  │  │ Adapter  │  │ Adapter  │  │ Adapter  │    ║
║  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    ║
╚═══════┼─────────────┼─────────────┼─────────────┼─────────────┼───────────╝
        │             │             │             │             │
        ▼             ▼             ▼             ▼             ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                           API GATEWAY                                        ║
║  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   ║
║  │ Auth       │  │ Rate       │  │ Tenant     │  │ Request            │   ║
║  │ (JWT +     │  │ Limiting   │  │ Resolution │  │ Validation         │   ║
║  │  API Key)  │  │            │  │            │  │                    │   ║
║  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────────────┘   ║
╚════════┼───────────────┼───────────────┼───────────────┼──────────────────╝
         │               │               │               │
         ▼               ▼               ▼               ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                        EVENT INGESTION LAYER                                 ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │                    Event Broker (Redis Streams / Kafka)               │   ║
║  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   ║
║  │  │ Schema      │  │ Event       │  │ Dedup       │  │ Dead Letter │ │   ║
║  │  │ Validator   │  │ Router      │  │ Filter      │  │ Queue       │ │   ║
║  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
         │
         ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                    POLICY ENGINE (FIRST — BEFORE EVERYTHING)                ║
║  ┌──────────────────────────────────────────────────────────────────────┐  ║
║  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────────┐ │  ║
║  │  │ Opt-out    │ │ Consent    │ │ Suppression│ │ Frequency        │ │  ║
║  │  │ Check      │ │ Check      │ │ List Check │ │ Cap Check        │ │  ║
║  │  └────────────┘ └────────────┘ └────────────┘ └──────────────────┘ │  ║
║  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────────┐ │  ║
║  │  │ Quiet      │ │ Timezone   │ │ Clinic     │ │ Tenant           │ │  ║
║  │  │ Hours      │ │ Check      │ │ Hours      │ │ Isolation        │ │  ║
║  │  └────────────┘ └────────────┘ └────────────┘ └──────────────────┘ │  ║
║  └──────────────────────────────────────────────────────────────────────┘  ║
║  OUTPUT: CAN_PROCEED (bool) + VIOLATIONS (list)                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
         │
         ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RECAPTURE DECISION ENGINE                                 ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │  Opportunity Detection                                                 │   ║
║  │  State Machine Transition → Create Opportunity                         │   ║
║  └──────────────────────────┬───────────────────────────────────────────┘   ║
║                              ▼                                              ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │  Scoring Engine                                                        │   ║
║  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────┐     │   ║
║  │  │ Priority Score │  │ Conversion     │  │ Response Probability │     │   ║
║  │  │ (0-100)       │  │ Probability    │  │ (0-1)               │     │   ║
║  │  └────────────────┘  └────────────────┘  └──────────────────────┘     │   ║
║  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────┐     │   ║
║  │  │ Risk Score     │  │ Channel Fit    │  │ Optimal Timing      │     │   ║
║  │  │ (0-100)       │  │ Score          │  │ Prediction          │     │   ║
║  │  └────────────────┘  └────────────────┘  └──────────────────────┘     │   ║
║  └──────────────────────────┬───────────────────────────────────────────┘   ║
║                              ▼                                              ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │  Next-Best-Action Selector                                             │   ║
║  │  CONTACT_NOW | WAIT | ASK_QUESTION | OFFER_BOOKING |                  │   ║
║  │  SEND_REMINDER | CREATE_TASK | ESCALATE | SUPPRESS | END              │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
         │
         ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MESSAGE GENERATION ENGINE                                ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │  1. Select approved template (tenant-specific)                         │   ║
║  │  2. Fill with verified structured data (NO LLM for facts)              │   ║
║  │  3. LLM personalization (within template constraints)                  │   ║
║  │  4. Validation layer (prohibited claims, formatting)                   │   ║
║  │  5. Policy re-check before send                                        │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
         │
         ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CONVERSATION ENGINE (when patient replies)               ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────────┐  │   ║
║  │  │ Intent     │  │ Safety     │  │ Retrieval  │  │ Tool Gateway  │  │   ║
║  │  │ Classifier │  │ Classifier │  │ (RAG)      │  │               │  │   ║
║  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └───────┬───────┘  │   ║
║  │        │               │               │                   │          │   ║
║  │        ▼               ▼               ▼                   ▼          │   ║
║  │  ┌──────────────────────────────────────────────────────────────────┐ │   ║
║  │  │              LLM Conversation Agent                               │ │   ║
║  │  │  System Prompt + Patient Context + Tool Results + Safety Policy   │ │   ║
║  │  └──────────────────────────┬───────────────────────────────────────┘ │   ║
║  │                             ▼                                          │   ║
║  │  ┌──────────────────────────────────────────────────────────────────┐ │   ║
║  │  │              Response Validation Layer                            │ │   ║
║  │  │  Hallucination check │ Policy check │ Tool consistency │ Format  │ │   ║
║  │  └──────────────────────────┬───────────────────────────────────────┘ │   ║
║  └─────────────────────────────┼─────────────────────────────────────────┘   ║
║                                ▼                                             ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │  Tool Execution (if needed)                                           │   ║
║  │  check_availability() → hold_slot() → book_appointment()             │   ║
║  │  Each tool: auth check → execute → validate → audit                   │   ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
         │
         ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                    EXTERNAL SYSTEMS INTEGRATION                              ║
║  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   ║
║  │ Practice   │  │ Insurance  │  │ SMS/Email  │  │ Analytics /        │   ║
║  │ Mgmt Sys   │  │ Verifier   │  │ Provider   │  │ Data Warehouse     │   ║
║  │ (PMS)      │  │            │  │            │  │                    │   ║
║  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
         │
         ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                    STAFF DASHBOARD & OPERATIONS                              ║
║  ┌──────────────────────────────────────────────────────────────────────┐   ║
║  │  Recapture Queue │ Conversations │ Handoffs │ Campaigns │ Analytics    │   ║
║  │  Patient Timeline │ AI Decisions │ Settings │ Compliance │ Integrations  │  ║
║  └──────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## E.3 Core Design Decisions

### Decision 1: Monorepo Architecture
**Rationale:** Single repository with clear module boundaries. Easier CI/CD, shared types, unified deployment. Appropriate for a team of 5-20 engineers.

### Decision 2: PostgreSQL as Primary Data Store
**Rationale:** ACID guarantees critical for appointments and financial data. Row-level security for multi-tenancy. Rich query capability for analytics. No need for separate OLTP and OLAP at V1 scale.

### Decision 3: Redis Streams for Event Bus (V1), Migrate to Kafka at Scale
**Rationale:** Redis Streams is simpler, sufficient for 1000s of practices. Kafka adds operational complexity. Migrate when throughput justifies it.

### Decision 4: Anthropic Claude as Primary LLM
**Rationale:** Strong instruction-following, good safety characteristics, tool-use support, reasonable pricing. Fallback to other providers via abstraction layer.

### Decision 5: Python Backend (FastAPI) + TypeScript Frontend
**Rationale:** Python for ML/AI integration, FastAPI for async performance. TypeScript for type-safe frontend. Industry standard, large talent pool.

### Decision 6: Celery + Redis for Async Workers
**Rationale:** Proven Python async framework. Good enough for V1. Can migrate to Temporal for complex workflows later.

### Decision 7: No ML Models in V1
**Rationale:** Rules-first approach. Add ML scoring after collecting 3+ months of outcome data. Prevents premature optimization.

---

# PART F — EVENT ARCHITECTURE

## F.1 Event Schema Standard

Every event in the system follows this structure:

```json
{
  "event_id": "uuid-v4",
  "event_type": "string",
  "event_version": "1",
  "timestamp": "2026-09-30T14:32:00Z",
  "tenant_id": "uuid-v4",
  "patient_id": "uuid-v4 | null",
  "conversation_id": "uuid-v4 | null",
  "appointment_id": "uuid-v4 | null",
  "opportunity_id": "uuid-v4 | null",
  "correlation_id": "uuid-v4",
  "idempotency_key": "string",
  "source_system": "string",
  "source_event_id": "string | null",
  "payload": {},
  "security_classification": "PUBLIC | INTERNAL | CONFIDENTIAL | PHI",
  "retention_days": 2555,
  "created_at": "2026-09-30T14:32:00Z",
  "processed_at": "2026-09-30T14:32:01Z | null"
}
```

## F.2 Complete Event Catalog

### F.2.1 Patient Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `patient.created` | Integration adapter | New patient in PMS | Profile service, consent service |
| `patient.updated` | Integration adapter | Patient record changed | Profile service, conversation context |
| `patient.inactive` | Scheduled job | No visit > threshold days | Recall engine, reactivation campaigns |
| `patient.opted_out` | Policy engine / channel | Patient opts out | Suppression service, ALL channels |
| `patient.opted_in` | Consent flow | Patient consents | Enable eligible channels |
| `patient.contact_preference_updated` | Patient / staff | Preference change | Channel selection, scheduling |

### F.2.2 Lead Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `lead.created` | Web form / chat | Form submitted, chat started | Lead processing, recapture engine |
| `lead.contacted` | Communication service | Outreach sent | Analytics, next action selector |
| `lead.contact_attempted` | Communication service | First attempt | Timing engine, frequency tracker |
| `lead.engaged` | Conversation engine | Patient responded | Qualification, booking flow |
| `lead.disqualified` | Policy engine | Failed eligibility check | Suppression, analytics |
| `lead.converted` | Booking service | Appointment booked | Revenue tracking, analytics |

### F.2.3 Conversation Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `conversation.started` | Channel adapter | First message | Conversation service, AI agent |
| `conversation.message_received` | Channel adapter | Inbound message | Intent classifier, AI agent |
| `conversation.message_sent` | Communication service | Outbound message | Delivery tracking, analytics |
| `conversation.intent_detected` | Intent engine | Intent classified | Next-best-action, tool routing |
| `conversation.tool_called` | AI agent | Tool invocation | Tool service, audit log |
| `conversation.tool_result` | Tool service | Tool response | AI agent, validation |
| `conversation.handoff_created` | Safety / AI agent | Human needed | Staff queue, notification |
| `conversation.handoff_accepted` | Staff | Staff takes over | Conversation routing |
| `conversation.handoff_resolved` | Staff | Issue resolved | Analytics, satisfaction |
| `conversation.ended` | Any | Conversation closed | Analytics, summarization |
| `conversation.abandoned` | Timeout | No response X minutes | Recapture trigger |
| `conversation.safety_escalation` | Safety classifier | Safety signal | Immediate handoff, alert |

### F.2.4 Appointment Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `appointment.created` | PMS adapter | New appointment booked | Confirmation, reminders |
| `appointment.modified` | PMS adapter | Appointment changed | Notification, re-reminder |
| `appointment.cancelled` | PMS adapter / AI | Cancellation | Recapture engine, slot release |
| `appointment.no_show` | PMS adapter | Patient didn't arrive | No-show recapture |
| `appointment.completed` | PMS adapter | Visit completed | Recall scheduling, follow-up |
| `appointment.hold_created` | Booking service | Slot reserved | Expiry timer, hold tracker |
| `appointment.hold_expired` | Scheduled job | Hold time expired | Slot release, notification |
| `appointment.reminder_sent` | Reminder service | Reminder triggered | Delivery tracking |
| `appointment.reminder_confirmed` | Patient response | Patient confirmed | Status update |
| `appointment.slot_offered` | AI agent | Slot presented | Offer tracker, expiry |

### F.2.5 Treatment Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `treatment_plan.created` | PMS adapter | Plan created in system | Treatment recapture monitor |
| `treatment_plan.presented` | Practice staff | Shown to patient | Follow-up timer |
| `treatment_plan.accepted` | Patient / AI | Patient agreed | Scheduling trigger |
| `treatment_plan.rejected` | Patient | Patient declined | Reason logging, follow-up |
| `treatment_plan.unscheduled` | Scheduled job | No appointment after X days | Recapture trigger |
| `treatment_plan.item.completed` | PMS adapter | Procedure done | Next item trigger |
| `treatment_plan.item.stalled` | Scheduled job | Item not scheduled | Recapture trigger |
| `estimate.sent` | PMS adapter | Estimate provided to patient | Follow-up timer |
| `estimate.viewed` | Portal | Patient viewed estimate | Engagement signal |

### F.2.6 Communication Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `message.sent` | Communication service | Message dispatched | Delivery tracker, analytics |
| `message.delivered` | Channel provider | Delivery confirmed | Analytics, next action |
| `message.failed` | Channel provider | Delivery failed | Retry logic, alerting |
| `message.opened` | Email provider | Email opened | Engagement tracking |
| `message.clicked` | Email provider | Link clicked | Click tracking, conversion |
| `message.replied` | Channel adapter | Patient replied | Conversation engine |
| `message.opted_out` | Channel provider | Opt-out received | Immediate suppression |
| `message.bounced` | Email provider | Hard bounce | Address correction, suppression |

### F.2.7 Campaign Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `campaign.created` | Staff / API | Campaign configured | Scheduler |
| `campaign.started` | Scheduler | Campaign activated | Execution engine |
| `campaign.opportunity_enrolled` | Eligibility engine | Patient enrolled | Sequence executor |
| `campaign.attempt.started` | Sequence executor | Outreach attempt begins | Communication service |
| `campaign.attempt.completed` | Communication service | Attempt finished (any outcome) | Analytics, next step |
| `campaign.attempt.replied` | Conversation engine | Patient responded | Conversation engine |
| `campaign.opportunity.completed` | State machine | Final state reached | Analytics, ROI calc |
| `campaign.opportunity.suppressed` | Policy engine | Suppressed mid-campaign | Analytics, eligibility audit |

### F.2.8 Integration Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `integration.connected` | Integration service | Connection established | Health monitoring |
| `integration.disconnected` | Integration service | Connection lost | Alerting, fallback |
| `integration.sync.started` | Sync service | Sync initiated | Progress tracking |
| `integration.sync.completed` | Sync service | Sync finished | Cache invalidation |
| `integration.sync.failed` | Sync service | Sync error | Alerting, retry |
| `integration.webhook.received` | Webhook handler | Inbound webhook | Event processing |
| `integration.webhook.duplicate` | Dedup filter | Duplicate detected | Alerting, dedup metrics |
| `integration.pms.outage` | Health checker | PMS unreachable | Degraded mode alert |

### F.2.9 AI Decision Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `ai.decision.scored` | Scoring engine | Score computed | Next-best-action, campaign |
| `ai.decision.action_selected` | NBA engine | Action chosen | Executor, audit log |
| `ai.decision.message_generated` | Message generator | Message produced | Validation, delivery |
| `ai.decision.validated` | Validation layer | Validation result | Executor, metrics |
| `ai.decision.executed` | Executor | Action performed | Analytics, state machine |
| `ai.decision.handoff_triggered` | Safety / AI | Handoff needed | Staff queue |
| `ai.decision.fallback_used` | Fallback handler | AI failed, rule used | Model monitoring |
| `ai.decision.override` | Staff | Human override | Model monitoring, learning |

### F.2.10 Human Handoff Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `handoff.created` | AI / Safety | Handoff initiated | Staff queue, notification |
| `handoff.assigned` | Staff / Auto | Assigned to staff member | Assignment tracking |
| `handoff.accepted` | Staff | Staff takes ownership | SLA timer starts |
| `handoff.resolved` | Staff | Issue resolved | Analytics, satisfaction |
| `handoff.sla_breached` | SLA monitor | Time limit exceeded | Escalation, alerting |
| `handoff.escalated` | Staff / SLA | Needs higher-level staff | Management alert |

### F.2.11 Consent & Compliance Events

| Event | Producer | Trigger | Downstream Consumers |
|-------|----------|---------|---------------------|
| `consent.granted` | Consent flow | Patient consents | Enable channel |
| `consent.revoked` | Patient / Staff | Consent withdrawn | Disable channel, suppression |
| `consent.expired` | Scheduled job | Consent period ended | Re-consent flow |
| `suppression.added` | Staff / Opt-out | Patient suppressed | ALL outreach checkers |
| `suppression.removed` | Staff | Suppression lifted | Re-enable eligible outreach |
| `data.deletion_requested` | Patient (GDPR/CCPA) | Deletion request | Deletion workflow |
| `data.accessed` | Any system | PHI accessed | Audit log |
| `audit.log.created` | Audit middleware | Any significant action | Compliance reporting |

## F.3 Event Flow Example: Complete Patient Journey

```
Patient submits website form
    │
    ▼
[Web Server] ──► POST /api/v1/leads ──► publish(lead.created)
    │
    ▼
[Event Consumer: Lead Service]
    │  1. Validate event
    │  2. Create patient record (or link existing)
    │  3. Create lead record
    │  4. Check consent status
    │  5. Trigger eligibility check
    │
    ▼
[Policy Engine]
    │  1. Check opt-out → No
    │  2. Check consent → SMS: yes, Email: yes, Voice: no
    │  3. Check suppression → No
    │  4. Check frequency cap → Within limits
    │  5. Check quiet hours → Not in quiet hours
    │  RESULT: CAN_PROCEED
    │
    ▼
[Recapture Engine]
    │  1. Create opportunity: LEAD_ABANDONED
    │  2. Calculate scores:
    │     - priority_score: 72 (new lead, service inquiry)
    │     - conversion_probability: 0.35
    │     - recommended_channel: SMS (highest consent)
    │     - recommended_time: now (new lead urgency)
    │  3. Select action: CONTACT_NOW
    │
    ▼
[Message Generator]
    │  1. Select template: "new_lead_followup"
    │  2. Fill verified data:
    │     - patient_first_name: "Jennifer"
    │     - service_inquired: "Teeth Whitening"
    │     - clinic_phone: "(555) 123-4567"
    │     - clinic_hours: "Mon-Fri 8am-5pm"
    │  3. LLM personalization (within template)
    │  4. Validate output
    │  5. Final message: "Hi Jennifer! Thanks for your interest...
    │
    ▼
[Communication Service]
    │  1. Check idempotency (has this been sent?)
    │  2. Send via SMS provider
    │  3. Publish: message.sent
    │  4. Update: lead.contacted = true
    │
    ▼
[SMS Provider] ──► Delivery confirmation ──► publish(message.delivered)
    │
    ▼
[Patient receives SMS]
    │
    ▼
[Patient replies]
    │
    ▼
[Channel Adapter] ──► publish(conversation.message_received)
    │
    ▼
[Conversation Engine]
    │  1. Load conversation context
    │  2. Classify intent: PRICING_QUESTION
    │  3. Safety check: No concerns
    │  4. Retrieve clinic data: pricing for Zoom Whitening
    │  5. LLM generates response with verified data
    │  6. Validate response
    │  7. Send response
    │
    ▼
[Patient: "Can I book for Tuesday?"]
    │
    ▼
[Conversation Engine]
    │  1. Intent: BOOKING_REQUEST
    │  2. Call check_availability(date="next Tuesday")
    │  3. Return: [10:00 AM, 2:00 PM, 4:00 PM]
    │  4. LLM: "We have 10 AM, 2 PM, and 4 PM available..."
    │
    ▼
[Patient: "2 PM works"]
    │
    ▼
[Conversation Engine]
    │  1. Call hold_slot(datetime="2026-10-06T14:00:00")
    │  2. Slot held (5 min expiry)
    │  3. LLM: "Let me book that for you... [confirms details]"
    │  4. Call book_appointment(hold_id)
    │  5. PMS confirms booking
    │  6. Publish: appointment.booked
    │  7. Send confirmation SMS
```

---

# PART G — STATE MACHINE

## G.1 Opportunity State Machine

```
                        ┌─────────────┐
                        │  CREATED    │
                        └──────┬──────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │ ELIGIBLE │   │SUPPRESSED│   │ INELIGIBLE   │
        └────┬─────┘   └──────────┘   └──────────────┘
             │
             ▼
      ┌────────────┐
      │ QUEUED     │ ← Scheduled for outreach
      └─────┬──────┘
            │
            ▼
      ┌────────────┐
      │ OUTREACH   │ ← Message sent / call initiated
      │ SENT       │
      └─────┬──────┘
            │
     ┌──────┼──────┬──────────┬──────────┐
     ▼      ▼      ▼          ▼          ▼
  ┌────┐ ┌────┐ ┌─────┐  ┌────────┐ ┌────────┐
  │REPLY│ │OPEN │ │CLICK│  │NO_REPLY│ │FAILED  │
  └─┬──┘ └──┬─┘ └──┬──┘  └───┬────┘ └───┬────┘
    │       │      │         │           │
    │       │      │         ▼           ▼
    │       │      │    ┌────────┐  ┌────────┐
    │       │      │    │RETRY   │  │ENDED   │
    │       │      │    └───┬────┘  └────────┘
    │       │      │        │
    │       │      │        ▼
    │       │      │    ┌────────┐
    │       │      │    │EXHAUSTED│
    │       │      │    └───┬────┘
    │       │      │        │
    └───────┼──────┼────────┘
            ▼      ▼
      ┌──────────────┐
      │ ENGAGED      │ ← Patient responded
      └──────┬───────┘
             │
    ┌────────┼────────┬─────────────┐
    ▼        ▼        ▼             ▼
┌───────┐ ┌──────┐ ┌───────┐  ┌──────────┐
│BOOKED │ │ASK_Q │ │DECLINE│  │SCHEDULE  │
│        │ │       │ │        │  │LATER     │
└───┬────┘ └───┬──┘ └───┬───┘  └────┬─────┘
    │          │        │            │
    │          │        │            ▼
    │          │        │    ┌──────────────┐
    │          │        │    │WAITING       │
    │          │        │    └──────┬───────┘
    │          │        │           │
    │          │        │    ┌──────┴──────┐
    │          │        │    ▼             ▼
    │          │        │  ┌───────┐   ┌────────┐
    │          │        │  │TIMEOUT│   │FOLLOWUP│
    │          │        │  └───┬───┘   └───┬────┘
    │          │        │      │           │
    │          │        │      ▼           ▼
    │          │        │  ┌──────────┐ ┌────────┐
    │          │        │  │COMPLETED │ │ENDED   │
    │          │        │  └──────────┘ └────────┘
    │          │        │
    └──────────┼────────┘
               ▼
        ┌──────────────┐
        │COMPLETED     │ ← Booking confirmed
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ ARCHIVED     │ ← Final state
        └──────────────┘

Terminal/Handoff States:
    ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────┐
    │ HANDOFF  │  │SAFETY_ESC  │  │ OPTED_OUT│  │ ENDED    │
    │ TO HUMAN │  │ALATION     │  │          │  │          │
    └──────────┘  └────────────┘  └──────────┘  └──────────┘
```

## G.2 Conversation State Machine

```
                    ┌───────────┐
                    │  NEW      │
                    └─────┬─────┘
                          │
              ┌───────────▼───────────┐
              │  ACTIVE / GREETING    │
              └─────┬─────────────────┘
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
┌──────────┐ ┌──────────┐ ┌──────────────┐
│ UNDERSTAND│ │ ACTION   │ │ CLARIFY      │
│ INTENT    │ │ PHASE    │ │              │
└────┬─────┘ └────┬─────┘ └──────┬───────┘
     │            │               │
     │            ▼               │
     │      ┌──────────┐          │
     │      │ TOOL     │          │
     │      │ CALLING  │          │
     │      └────┬─────┘          │
     │           │                │
     │           ▼                │
     │      ┌──────────┐          │
     │      │ RESPOND  │          │
     │      └────┬─────┘          │
     │           │                │
     └───────────┼────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌──────────┐ ┌────────────┐
│BOOKED  │  │ HANDOFF  │ │ ENDED      │
│        │  │ TO HUMAN │ │            │
└────────┘  └────┬─────┘ └────────────┘
                 │
                 ▼
           ┌───────────┐
           │ RESOLVED  │
           └───────────┘
```

## G.3 Patient Lifecycle State Machine

```
    ┌──────────┐   lead.created    ┌──────────┐
    │ UNKNOWN  │ ────────────────► │  LEAD    │
    └──────────┘                   └────┬─────┘
                                        │
                          contacted ───┼─── engaged
                                        │
                                        ▼
                                  ┌──────────┐
                                  │ ENGAGED  │
                                  └────┬─────┘
                                        │
                               qualified ──┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │ BOOKING  │
                                  │  PENDING │
                                  └────┬─────┘
                                        │
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
                   ┌────────┐     ┌──────────┐   ┌──────────┐
                   │ BOOKED │     │ABANDONED │   │DECLINED  │
                   └───┬────┘     └──────────┘   └──────────┘
                       │
                       ▼
                 ┌──────────┐
                 │CONFIRMED │
                 └────┬─────┘
                      │
                      ▼
                 ┌──────────┐
                 │ COMPLETED│
                 └────┬─────┘
                      │
            ┌─────────┼──────────┐
            ▼         ▼          ▼
       ┌────────┐ ┌───────┐ ┌──────────┐
       │RECALL  │ │TREAT- │ │INACTIVE  │
       │ DUE    │ │ MENT  │ │          │
       └───┬────┘ └───┬───┘ └────┬─────┘
           │         │           │
           │         ▼           │
           │   ┌──────────┐     │
           │   │ TREATMENT│     │
           │   │ PLAN     │     │
           │   └────┬─────┘     │
           │        │           │
           │        ▼           │
           │   ┌──────────┐    │
           │   │ TREATMENT│    │
           │   │ UNSCHED  │◄───┘
           │   └────┬─────┘
           │        │
           │        ▼
           │   ┌──────────┐
           │   │SCHEDULED │
           │   └──────────┘
           │
           ▼
     ┌──────────┐     ┌──────────┐
     │ CANCELLED│     │ NO_SHOW  │
     └────┬─────┘     └────┬─────┘
          │                │
          │    ┌───────────┼───────────┐
          │    ▼           ▼           ▼
          │ ┌────────┐ ┌────────┐ ┌────────┐
          │ │RESCHED │ │REACHED │ │UNREACH │
          │ └───┬────┘ └───┬────┘ └───┬────┘
          │     │          │          │
          └─────┼──────────┼──────────┘
                │          │
                ▼          ▼
          ┌──────────────────┐
          │  RECAPTURE LOOP  │
          └────────┬─────────┘
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
      ┌────────┐ ┌──────┐ ┌──────────┐
      │REBOOKED│ │ENDED │ │OPTED_OUT │
      └────────┘ └──────┘ └──────────┘
```

## G.4 Valid State Transitions (Formal)

```
LEAD_CREATED
  → ELIGIBLE (passed policy checks)
  → SUPPRESSED (failed policy checks)
  → INELIGIBLE (wrong tenant, invalid contact, etc.)

ELIGIBLE
  → QUEUED (scheduled for outreach)
  → SUPPRESSED (opted out after creation)
  → INELIGIBLE (contact became invalid)

QUEUED
  → OUTREACH_SENT (message dispatched)
  → SUPPRESSED (opted out before send)
  → CANCELLED (campaign stopped)
  → ENDED (opportunity expired)

OUTREACH_SENT
  → REPLIED (patient responded)
  → OPENED (email opened)
  → CLICKED (link clicked)
  → DELIVERED (no interaction)
  → FAILED (delivery failure)
  → NO_REPLY (timeout)
  → OPTED_OUT (patient opted out)
  → SUPPRESSED (added to suppression)
  → ENDED (final attempt reached)

REPLIED / ENGAGED
  → BOOKED (appointment created)
  → BOOKING_PENDING (slot offered, awaiting confirmation)
  → DECLINED (explicitly declined)
  → SCHEDULE_LATER (wants future appointment)
  → QUESTION (needs more information)
  → HANDOFF (human needed)
  → SAFETY_ESCALATION (safety concern)
  → ENDED (conversation ended)

BOOKING_PENDING
  → BOOKED (confirmed)
  → ABANDONED (hold expired)
  → CANCELLED (patient cancelled)
  → HANDOFF (booking issue)
  → ENDED (no longer interested)

BOOKED
  → CONFIRMED (appointment confirmed)
  → MODIFIED (appointment changed)
  → CANCELLED (appointment cancelled)
  → COMPLETED (visit happened)
  → NO_SHOW (patient didn't arrive)
  → ENDED (appointment removed)

CANCELLED / NO_SHOW / ABANDONED / DECLINED
  → RECAPTURE_ELIGIBLE (re-engage after cooling period)
  → ENDED (not recapturable)
  → OPTED_OUT (patient opted out)

Any State
  → HANDOFF (safety, complaint, complex issue)
  → SAFETY_ESCALATION (emergency signal)
  → SUPPRESSED (opted out)
  → OPTED_OUT (opted out)
  → ENDED (final state)
```

---

**Continue to next section: System Architecture, Data Architecture, Database Schema...**
