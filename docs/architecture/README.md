# HeyJarvis Patient Recapture System
## Product Architecture & Implementation Blueprint

**Version:** 1.0  
**Date:** 2025-01-15  
**Status:** Draft — Implementation Reference  
**Author:** HeyJarvis Engineering  

---

## Document Index

This blueprint is organized into domain-specific documents. Read them in order for full context.

| # | Document | Purpose |
|---|----------|---------|
| 1 | [01-recapture-state-machine.md](./01-recapture-state-machine.md) | Patient journey state machine — all states, transitions, lifecycle |
| 2 | [02-event-architecture.md](./02-event-architecture.md) | Complete event catalog, payloads, producers, consumers, deduplication |
| 3 | [03-decision-engine.md](./03-decision-engine.md) | Deterministic policy layer — should-we-contact decision pipeline |
| 4 | [04-scoring-model.md](./04-scoring-model.md) | Recapture priority scoring, conversion probability, risk scoring |
| 5 | [05-model-strategy.md](./05-model-strategy.md) | LLM / classical ML / rules / RAG — where each belongs |
| 6 | [06-ml-training-plan.md](./06-ml-training-plan.md) | Dataset design, feature engineering, training strategy, leakage prevention |
| 7 | [07-message-generation.md](./07-message-generation.md) | Message generation engine with verified data, templates, safety constraints |
| 8 | [08-channel-selection.md](./08-channel-selection.md) | Channel selection, frequency caps, next-best-action |
| 9 | [09-conversational-ai.md](./09-conversational-ai.md) | AI agent architecture, tools, tool calling, policy enforcement |
| 10 | [10-human-in-the-loop.md](./10-human-in-the-loop.md) | Escalation triggers, staff workflow, handoff, SLA |
| 11 | [11-safety.md](./11-safety.md) | Medical safety boundary, emergency escalation, adversarial examples |
| 12 | [12-compliance-security.md](./12-compliance-security.md) | HIPAA, TCPA, security controls, data governance |
| 13 | [13-multitenancy.md](./13-multitenancy.md) | Multi-tenant architecture, isolation, RBAC |
| 14 | [14-database-schema.md](./14-database-schema.md) | Complete production relational schema |
| 15 | [15-queue-architecture.md](./15-queue-architecture.md) | Async queue design, Celery, retries, DLQ, idempotency |
| 16 | [16-integrations.md](./16-integrations.md) | Dental PMS adapters, scheduling, insurance, communication |
| 17 | [17-communication-channels.md](./17-communication-channels.md) | SMS, email, voice, chat — capabilities, costs, compliance |
| 18 | [18-testing-strategy.md](./18-testing-strategy.md) | Unit, integration, safety, compliance, load testing |
| 19 | [19-cold-start.md](./19-cold-start.md) | New clinic onboarding with no historical data |
| 20 | [20-operations.md](./20-operations.md) | Monitoring, alerting, incident response, runbooks |

---

## Executive Summary

### What This System Does

The HeyJarvis Patient Recapture System identifies patients who started but never completed a dental care journey, determines whether outreach is appropriate and safe, selects the right communication channel, generates personalized messages using verified data only, executes campaigns with full compliance, and measures the revenue impact.

### What This System Does NOT Do

- **Does NOT diagnose** dental conditions
- **Does NOT prescribe** treatment or medication
- **Does NOT independently assess** clinical severity beyond a triage/escalation policy
- **Does NOT fabricate** appointments, insurance coverage, prices, discounts, or availability
- **Does NOT override** opt-out, suppression, consent, quiet-hour, or safety rules
- **Does NOT message** patients who have requested no contact

### System Properties

| Property | Requirement |
|----------|-------------|
| Compliance | HIPAA, TCPA, CAN-SPAM, state privacy laws |
| Latency (AI response) | < 2 seconds |
| Latency (outreach dispatch) | < 30 seconds |
| Uptime | 99.9% |
| Audit retention | 7 years (HIPAA) |
| Message accuracy | No fabricated clinical/financial data |
| Opt-out compliance | Immediate, across all channels |
| Multi-tenant isolation | Row-level security, tenant-scoped all the way down |

### Architecture Principles

1. **Policy before AI.** Every AI action passes through a deterministic policy layer first. Rules are never overridden by LLM output.
2. **Events are the source of truth.** The system is event-driven. All state changes emit events. No component mutates state silently.
3. **Verified data only.** Messages use data from the database, not LLM generation, for any clinical, financial, scheduling, or insurance information.
4. **Tenant isolation by design.** Every query, every event, every LLM call is scoped to a tenant. Cross-tenant leakage is architecturally impossible.
5. **Fail safe.** When in doubt, suppress outreach and escalate to human. False negatives (missed opportunities) cost revenue. False positives (wrong messages, safety incidents) cost trust and compliance.
6. **Observable and auditable.** Every decision, every message, every handoff is logged with full context for compliance review.

### Technology Stack (Current)

| Layer | Technology | Notes |
|-------|-----------|-------|
| API | FastAPI | Already in use |
| Database | PostgreSQL + SQLAlchemy 2.0 | Already in use |
| Queue | Celery + Redis | Already in use |
| LLM | Anthropic Claude | Haiku for speed, Sonnet for complex reasoning |
| Auth | JWT (python-jose) | Already in use |
| SMS | Twilio | Mock in dev, real in production |
| Email | Postmark | Mock in dev, real in production |
| Frontend | Next.js + shadcn/ui | Dashboard, staff workflow |
| Infra | Docker Compose (dev), K8s (prod) | TBD |

### Current Codebase Status

The HeyJarvis repository at `C:\Users\DIVYANSHU\Desktop\HeyJarvis.ai\` already contains:

- **Shared models** — All entity models (Patient, Appointment, Campaign, Consent, etc.) in `packages/shared/src/models.py`
- **Policy engine** — Complete deterministic policy layer in `packages/policy/src/policy_engine.py` with opt-out, consent, frequency caps, quiet hours, duplicate suppression, safety checks
- **Safety classifier** — Emergency and medical advice detection in `packages/policy/src/safety.py`
- **AI engine** — LLM client, intent classifier (Tier 1 keyword + Tier 2 LLM), message generator with templates in `packages/ai/src/ai_engine.py`
- **Event bus** — Event publishing, idempotency, event definitions in `packages/shared/src/events.py`
- **Database** — SQLAlchemy setup with RLS support in `packages/shared/src/database.py`
- **Integrations** — Abstract provider interfaces + Mock implementations for scheduling and insurance in `packages/shared/src/integrations.py`
- **Communication** — Mock + Twilio communication providers in `packages/shared/src/communication.py`
- **Constants** — All system constants in `packages/shared/src/constants.py`
- **Recapture taxonomy** — Complete taxonomy with 41 categories in `docs/04-recapture-taxonomy.md`
- **Recapture API routes** — REST endpoints for opportunities, campaigns in `apps/api/routes/recapture.py`
- **Worker tasks** — Celery tasks for scoring in `apps/worker/tasks/recapture.py`
- **Demo data** — Rich demo dataset for development in `packages/shared/src/demo_data.py`
- **Tests** — Policy, AI, API, communication tests in `tests/`
- **pyproject.toml** — Full dependency specification

### What This Blueprint Adds

The current codebase has the building blocks. This blueprint specifies:

1. **The complete state machine** — all patient states and valid transitions (Doc 1)
2. **The full event catalog** — every event with exact payload schemas (Doc 2)
3. **The decision pipeline** — exact ordering of policy checks, what each checks, what happens on failure (Doc 3)
4. **Scoring methodology** — initial rules-based approach, ML transition criteria, confidence calibration (Doc 4)
5. **Model placement** — exactly which problems get LLM, which get classical ML, which get rules (Doc 5)
6. **Training data strategy** — how to construct datasets without leakage, how to cold-start (Doc 6)
7. **Message generation design** — template structure, data sourcing, verification, forbidden content (Doc 7)
8. **Channel selection logic** — consent-aware, preference-aware, context-aware channel routing (Doc 8)
9. **Conversational AI architecture** — system prompt design, tool definitions, tool calling, policy enforcement (Doc 9)
10. **Human escalation** — triggers, SLA, staff workflow, audit trail (Doc 10)
11. **Safety design** — medical boundary, adversarial examples, emergency workflow (Doc 11)
12. **Compliance implementation** — HIPAA technical safeguards, TCPA messaging rules, audit requirements (Doc 12)
13. **Multi-tenancy** — tenant isolation, RBAC, per-tenant configuration (Doc 13)
14. **Database schema** — complete table definitions with columns, indexes, constraints (Doc 14)
15. **Queue architecture** — Celery design, retry strategies, DLQ, scheduled jobs (Doc 15)
16. **Integration adapters** — production adapter architecture for real PMS systems (Doc 16)
17. **Channel specifications** — SMS, email, voice, chat — exact requirements and costs (Doc 17)
18. **Testing strategy** — unit, integration, safety adversarial, load testing (Doc 18)
19. **Cold start plan** — new clinic onboarding without historical data (Doc 19)
20. **Operations** — monitoring, alerting, incident response (Doc 20)
