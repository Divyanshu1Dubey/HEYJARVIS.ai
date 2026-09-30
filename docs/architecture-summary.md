# Architecture Summary — Executive Overview

> This document is the single-page summary for presenting HeyJarvis Patient Recapture to stakeholders.

---

## What Is It?

**HeyJarvis Patient Recapture** is an AI-augmented system that identifies dental patients who didn't complete their appointments, treatments, or inquiries, and intelligently re-engages them through personalized, multi-channel outreach — while maintaining HIPAA compliance, patient safety, and full auditability.

## What Does It Solve?

Dental practices lose **20-30% of scheduled revenue** to:
- Patients who inquire but don't book
- Appointment cancellations that aren't rescheduled
- No-shows that aren't followed up
- Treatment plans that are accepted but never scheduled
- Overdue recalls that go unaddressed
- After-hours leads that are never followed up

Current solutions: **manual phone calls and basic SMS blasts** — which are slow, inconsistent, and miss patients.

## How Does It Work?

```
PATIENT EVENT (lead abandoned, appointment cancelled, etc.)
         │
         ▼
   RECAPTURE ENGINE
   - Identify the patient
   - Verify eligibility (consent, opt-out, frequency caps)
   - Score priority (ML + rules)
   - Select channel (SMS, email, voice)
   - Generate personalized message (AI)
   - Send message
         │
         ▼
   PATIENT RESPONDS
   - AI handles (intent classification, booking, etc.)
   - OR human takes over
         │
         ▼
   OUTCOME
   - Booked → Revenue recovered
   - Declined → Stop outreach
   - Opted out → Suppress
   - No response → Escalate or end
```

## Key Principles

| Principle | What It Means |
|-----------|--------------|
| **Rules Before AI** | Deterministic decisions first. AI only for personalization and conversation. |
| **AI Never the Source of Truth** | PMS and database are authoritative. AI never fabricates appointments, insurance, or availability. |
| **Patient Safety First** | AI never diagnoses, never prescribes, never minimizes emergency symptoms. |
| **Compliance Built-In** | HIPAA, TCPA, consent, opt-out — enforced by code, not policy docs. |
| **Explain Everything** | Every AI decision has a reason. Every action is auditable. |
| **Measure Incrementality** | Holdout groups measure what the AI ADDED, not vanity metrics. |

## Architecture in 60 Seconds

```
Patient → [Chat/SMS/Email/Web] → API → [Policy Engine] → [AI Engine] → [Tools] → [PMS/Insurance/SMS]
                              ↓
                         [Event Queue] → [Workers] → [Analytics]
                              ↓
                         [Audit Log] (everything logged)
```

**5 Core Systems:**
1. **Policy Engine** — Rules for eligibility, consent, safety, frequency
2. **AI Engine** — LLM for conversation, classification, generation
3. **Tool Layer** — Verified actions (booking, checking availability, etc.)
4. **Campaign Engine** — Configurable outreach sequences
5. **Analytics** — Revenue attribution, conversion tracking, optimization

## What Makes This Different?

| Traditional Approach | HeyJarvis Recapture |
|---------------------|---------------------|
| Manual follow-up calls | Automated, personalized outreach |
| Generic SMS blasts | Context-aware, individual messages |
| Misses after-hours leads | 24/7 AI availability |
| No tracking of why patients don't book | Structured reason capture |
| Staff decides who to contact | ML-prioritized opportunity scoring |
| No measurement of incrementality | Holdout-based causal attribution |
| No safety controls | Multi-layer safety + compliance enforcement |
| Hallucination risk | Tool-verified, validated responses |

## AI Usage — Where and Why

| AI Component | Technology | Purpose | Safety |
|-------------|-----------|---------|--------|
| Intent Classification | Small LLM | Understand patient message | Deterministic safety check first |
| Message Generation | Strong LLM | Personalized, context-aware messages | Output validation + tool verification |
| Safety Classifier | LLM + Rules | Detect emergencies, medical questions | Rules handle critical cases |
| Conversion Prediction | Gradient Boosting | Score which patients to contact | Rules always override |
| Priority Scoring | Gradient Boosting | Rank opportunities | Transparent feature importance |

**AI NEVER:**
- Diagnoses
- Prescribes
- Books without patient confirmation
- Fabricates appointments or insurance
- Bypasses consent or suppression
- Controls booking or scheduling directly

## Compliance Architecture

| Requirement | Implementation |
|------------|---------------|
| **HIPAA** | BAA with all vendors, encryption, audit logs, access controls |
| **TCPA** | Express consent before SMS, STOP keyword, time restrictions |
| **CAN-SPAM** | Unsubscribe link, valid headers, physical address |
| **State Privacy** | CCPA/CPRA compliance, data deletion rights |
| **Security** | TLS, AES-256, RLS, RBAC, MFA, secret management |

## Safety Architecture

```
Patient Message
       │
       ▼
 ┌─────────────┐
 │ Emergency   │ ← Pattern matching (deterministic)
 │ Pattern     │ → SAFETY_ESCALATION if matched
 │ Detection   │
 └──────┬──────┘
        │ No emergency
        ▼
 ┌─────────────┐
 │ Policy      │ ← Consent, opt-out, frequency (rules)
 │ Engine      │ → SUPPRESS if policy fails
 └──────┬──────┘
        │ Pass
        ▼
 ┌─────────────┐
 │ Intent      │ ← AI classification
 │ Classification│
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ Tool Calls  │ ← Verified data only
 │ + AI        │
 │ Generation  │
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ Output      │ ← Validation (deterministic)
 │ Validation  │ → REJECT if hallucination detected
 └──────┬──────┘
        │
        ▼
   Send to Patient
```

## Multi-Tenant Architecture

```
Organization (Dental Group)
  ├── Clinic 1
  │   ├── Location A
  │   │   ├── Provider 1
  │   │   └── Provider 2
  │   ├── Staff
  │   ├── Patients (isolated)
  │   └── Settings (isolated)
  │
  ├── Clinic 2
  │   └── ...
  │
  └── HQ Staff (cross-clinic view)
```

**Isolation mechanisms:**
- Row-Level Security (RLS) on all tables
- Tenant from JWT (never from client)
- Separate encryption keys per clinic
- Separate API rate limits per clinic
- Separate AI configuration per clinic

## Analytics — What We Measure

**Revenue Metrics:**
- Revenue recovered (actual dollar amount)
- Revenue per opportunity
- Recapture ROI (target: > 5x)

**Conversion Metrics:**
- Recapture rate (target: > 15%)
- Response rate (target: > 20%)
- Booking conversion (target: > 40%)

**Patient Experience Metrics:**
- Opt-out rate (target: < 0.3%)
- Complaint rate (target: < 0.5%)
- Safety event rate (target: < 0.5 per 1000 conversations)

**AI Quality Metrics:**
- Hallucination rate (target: < 1%)
- Safety detection rate (target: > 99%)
- Intent accuracy (target: > 90%)

## Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| API | FastAPI | Fast, async, Python ecosystem |
| Frontend | Next.js | React, SSR, modern |
| Worker | Python asyncio | Same language, async |
| Database | PostgreSQL | ACID, JSONB, RLS |
| Cache/Queue | Redis Streams | Simple, fast, sufficient for V1 |
| LLM | Anthropic Claude | Safety, quality, reliability |
| SMS | Twilio | Industry standard |
| Email | Postmark | Reliable, good deliverability |
| Infrastructure | Docker + K8s | Standard, scalable |
| Monitoring | Datadog | Full observability |

## Phased Delivery

| Phase | Timeline | What It Does | Risk Level |
|-------|----------|-------------|-----------|
| **Phase 1** | Weeks 5-12 | Rules-based recapture, no AI | Low |
| **Phase 2** | Weeks 13-20 | AI personalization + conversation | Medium |
| **Phase 3** | Weeks 21-28 | ML predictions + optimization | Medium |
| **Phase 4** | Weeks 29-36 | Multi-channel (email, voice) | Low |
| **Phase 5** | Weeks 37-44 | Real PMS integrations | Medium |
| **Phase 6** | Weeks 45-52 | Optimization + A/B testing | Low |

**Phase 1 can go live with 1-2 clinics.** Each phase builds on the previous.

## Cost Estimate

| Scale | Monthly Cost | Per Clinic |
|-------|-------------|------------|
| 10 clinics | ~$15,000 | ~$1,500 |
| 50 clinics | ~$90,000 | ~$1,800 |
| 200 clinics | ~$175,000 | ~$875 |
| 500 clinics | ~$415,000 | ~$830 |

**Revenue opportunity per clinic:** $5,000-$20,000/month in recovered appointments.

## What Could Go Wrong (Top Risks)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM hallucinates insurance | Medium | High | Tool verification, output validation |
| Double booking | Medium | High | Database locking, hold mechanism |
| Cross-tenant data leak | Low | Critical | RLS, automated tests |
| Patient opt-out ignored | Low | High | Automated opt-out enforcement |
| Emergency not escalated | Low | Critical | Pattern matching + LLM safety |
| SMS provider outage | Medium | Medium | Backup provider, queue retry |
| AI cost overrun | Medium | Medium | Tiered AI, caching, monitoring |
| Poor pilot results | Medium | High | Shadow testing, canary rollout |

## Production Readiness Checklist

Before any patient-facing deployment:
- ✅ No duplicate booking
- ✅ No cross-tenant leakage
- ✅ Opt-out reliably enforced
- ✅ Safety escalation works
- ✅ Audit logs complete
- ✅ All tests pass
- ✅ Staff trained
- ✅ Backup tested
- ✅ Rollback tested
- ✅ Monitoring and alerting active

## The Bottom Line

**HeyJarvis Patient Recapture is not a chatbot.** It is a production-grade, compliance-aware, multi-tenant system that uses AI carefully — as a layer on top of deterministic, auditable rules — to recover lost revenue for dental practices while protecting patient safety and privacy.

The system is designed to be:
- **Safe** — Safety checks before every AI action
- **Reliable** — No false bookings, no fabrication
- **Auditable** — Every decision logged and explainable
- **Measurable** — Incrementality measured via holdout groups
- **Compliant** — HIPAA, TCPA, and state laws built in
- **Cost-aware** — Tiered AI, caching, optimization
- **Ship-ready** — Phased delivery with clear gates
