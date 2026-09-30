# HeyJarvis Patient Recapture System

## Complete Product Architecture & Implementation Documentation

**Version:** 1.0
**Date:** 2025
**Status:** Production-Ready Specification

---

## What This Is

This repository contains the complete product architecture, system design, and implementation specification for the **HeyJarvis AI Patient Recapture System** — a production-grade, HIPAA-compliant, AI-augmented patient communication and revenue recovery platform for U.S. dental practices.

---

## Documentation Package

### Core Architecture Documents (34 files)

| File | Description |
|------|-------------|
| [00-executive-summary.md](00-executive-summary.md) | Executive overview of the product vision |
| [01-product-requirements.md](01-product-requirements.md) | Complete product requirements specification |
| [02-user-personas.md](02-user-personas.md) | All user personas (patient, staff, admin, etc.) |
| [03-use-cases.md](03-use-cases.md) | Comprehensive use case catalog |
| [04-recapture-taxonomy.md](04-recapture-taxonomy.md) | Complete taxonomy of recapture opportunities |
| [05-event-model.md](05-event-model.md) | Event-driven architecture specification |
| [06-state-machine.md](06-state-machine.md) | Patient lifecycle state machine |
| [07-system-architecture.md](07-system-architecture.md) | System architecture overview |
| [08-data-architecture.md](08-data-architecture.md) | Data architecture and flows |
| [09-database-schema.md](09-database-schema.md) | Complete PostgreSQL schema |
| [10-api-specification.md](10-api-specification.md) | REST API specification |
| [11-integration-architecture.md](11-integration-architecture.md) | Integration adapter architecture |
| [12-ai-architecture.md](12-ai-architecture.md) | AI/ML architecture |
| [13-model-training-plan.md](13-model-training-plan.md) | ML model training strategy |
| [14-dataset-specification.md](14-dataset-specification.md) | Dataset design and schema |
| [15-llm-prompt-specification.md](15-llm-prompt-specification.md) | All production prompts |
| [16-safety-policy.md](16-safety-policy.md) | Medical safety boundaries and policies |
| [17-human-handoff.md](17-human-handoff.md) | Human-in-the-loop system design |
| [18-compliance.md](18-compliance.md) | HIPAA, TCPA, and regulatory compliance |
| [19-security.md](19-security.md) | Security architecture |
| [20-threat-model.md](20-threat-model.md) | Security threat model |
| [21-red-team-plan.md](21-red-team-plan.md) | AI red teaming plan |
| [22-evaluation-framework.md](22-evaluation-framework.md) | Model and product evaluation |
| [23-testing-strategy.md](23-testing-strategy.md) | Comprehensive testing strategy |
| [24-observability.md](24-observability.md) | Monitoring and observability |
| [25-incident-response.md](25-incident-response.md) | Incident response procedures |
| [26-disaster-recovery.md](26-disaster-recovery.md) | DR and business continuity |
| [27-cost-model.md](27-cost-model.md) | Detailed cost breakdown |
| [28-analytics.md](28-analytics.md) | Analytics and KPI design |
| [29-experimentation.md](29-experimentation.md) | A/B testing framework |
| [30-ui-ux-specification.md](30-ui-ux-specification.md) | Complete UI/UX specification |
| [31-implementation-roadmap.md](31-implementation-roadmap.md) | MVP to production roadmap |
| [31-runbooks.md](31-runbooks.md) | Operational runbooks |
| [32-deployment.md](32-deployment.md) | Deployment architecture |
| [33-rollout-plan.md](33-rollout-plan.md) | Production rollout plan |
| [34-implementation-roadmap.md](34-implementation-roadmap.md) | Detailed implementation plan |
| [35-first-steps.md](35-first-steps.md) | Exact first implementation steps |

### Architecture Decision Records (ADRs)

| File | Description |
|------|-------------|
| [adr-index.md](adr-index.md) | Index of all architecture decisions |
| [adr/index.md](adr/index.md) | Individual ADR documents |

### Business & Presentation Materials

| File | Description |
|------|-------------|
| [architecture-summary.md](architecture-summary.md) | One-page architecture overview |
| [business-model.md](business-model.md) | Revenue model and pricing |
| [production-readiness-checklist.md](production-readiness-checklist.md) | Go/no-go production checklist |
| [presentations/INDEX.md](presentations/INDEX.md) | Master index of all presentations |
| [presentations/executive-deck.md](presentations/executive-deck.md) | 15-slide board/investor deck |
| [presentations/sales-pitch-deck.md](presentations/sales-pitch-deck.md) | 15-slide client pitch deck |
| [presentations/technical-deep-dive.md](presentations/technical-deep-dive.md) | 15-slide engineering presentation |
| [presentations/architecture-diagrams.md](presentations/architecture-diagrams.md) | All system diagrams (Mermaid) |
| [presentations/clinical-advisor-brief.md](presentations/clinical-advisor-brief.md) | Safety and compliance brief |
| [presentations/roi-calculator.md](presentations/roi-calculator.md) | Revenue impact analysis |
| [presentations/first-implementation-steps.md](presentations/first-implementation-steps.md) | Week-by-week implementation |

---

## Quick Start by Role

### For the CEO / Founder
1. Read: [architecture-summary.md](architecture-summary.md)
2. Read: [business-model.md](business-model.md)
3. Review: [presentations/executive-deck.md](presentations/executive-deck.md)
4. Review: [presentations/roi-calculator.md](presentations/roi-calculator.md)

### For the CTO / Lead Engineer
1. Read: [07-system-architecture.md](07-system-architecture.md)
2. Read: [09-database-schema.md](09-database-schema.md)
3. Read: [10-api-specification.md](10-api-specification.md)
4. Review: [presentations/technical-deep-dive.md](presentations/technical-deep-dive.md)
5. Review: [presentations/architecture-diagrams.md](presentations/architecture-diagrams.md)
6. Start: [35-first-steps.md](35-first-steps.md)

### For the Product Manager
1. Read: [01-product-requirements.md](01-product-requirements.md)
2. Read: [02-user-personas.md](02-user-personas.md)
3. Read: [03-use-cases.md](03-use-cases.md)
4. Read: [04-recapture-taxonomy.md](04-recapture-taxonomy.md)
5. Read: [31-implementation-roadmap.md](31-implementation-roadmap.md)

### For the Engineering Team
1. Read: [07-system-architecture.md](07-system-architecture.md)
2. Read: [08-data-architecture.md](08-data-architecture.md)
3. Read: [09-database-schema.md](09-database-schema.md)
4. Read: [12-ai-architecture.md](12-ai-architecture.md)
5. Read: [15-llm-prompt-specification.md](15-llm-prompt-specification.md)
6. Read: [23-testing-strategy.md](23-testing-strategy.md)
7. Start: [35-first-steps.md](35-first-steps.md)

### For the AI/ML Engineer
1. Read: [12-ai-architecture.md](12-ai-architecture.md)
2. Read: [13-model-training-plan.md](13-model-training-plan.md)
3. Read: [14-dataset-specification.md](14-dataset-specification.md)
4. Read: [15-llm-prompt-specification.md](15-llm-prompt-specification.md)
5. Read: [22-evaluation-framework.md](22-evaluation-framework.md)
6. Read: [21-red-team-plan.md](21-red-team-plan.md)

### For the Security Engineer
1. Read: [19-security.md](19-security.md)
2. Read: [20-threat-model.md](20-threat-model.md)
3. Read: [18-compliance.md](18-compliance.md)
4. Read: [16-safety-policy.md](16-safety-policy.md)
5. Read: [21-red-team-plan.md](21-red-team-plan.md)
6. Review: [production-readiness-checklist.md](production-readiness-checklist.md)

### For the Clinical Advisor / Legal
1. Read: [16-safety-policy.md](16-safety-policy.md)
2. Read: [18-compliance.md](18-compliance.md)
3. Review: [presentations/clinical-advisor-brief.md](presentations/clinical-advisor-brief.md)
4. Review: [20-threat-model.md](20-threat-model.md)

### For the QA / Testing Team
1. Read: [22-evaluation-framework.md](22-evaluation-framework.md)
2. Read: [23-testing-strategy.md](23-testing-strategy.md)
3. Review: [production-readiness-checklist.md](production-readiness-checklist.md)

### For Sales / Business Development
1. Read: [architecture-summary.md](architecture-summary.md)
2. Read: [business-model.md](business-model.md)
3. Review: [presentations/sales-pitch-deck.md](presentations/sales-pitch-deck.md)
4. Review: [presentations/roi-calculator.md](presentations/roi-calculator.md)
5. Review: [presentations/executive-deck.md](presentations/executive-deck.md)

### For the Client (Dental Practice Owner)
1. Review: [presentations/sales-pitch-deck.md](presentations/sales-pitch-deck.md)
2. Review: [presentations/roi-calculator.md](presentations/roi-calculator.md)
3. Review: [presentations/clinical-advisor-brief.md](presentations/clinical-advisor-brief.md)
4. Review: [presentations/architecture-diagrams.md](presentations/architecture-diagrams.md) (simplified sections)

---

## Key Design Principles

1. **Rules before AI** — Deterministic policy layer always comes first
2. **AI never is the source of truth** — External systems are authoritative
3. **Safety beats conversion** — Patient safety always takes priority
4. **Explainability** — Every AI decision is auditable
5. **Patient trust** — Non-pushy, transparent, respectful communication
6. **Incremental lift** — Measure true incremental impact, not vanity metrics

---

## System Summary

```
WHAT: AI-powered patient recapture system for dental practices
WHY: Recover 15-25% of lost revenue from patient drop-off ($240K/year typical)
HOW: Rules-first → AI personalization → ML optimization
WHERE: Multi-tenant SaaS, HIPAA + TCPA compliant
WHEN: 5 weeks to first pilot, production-ready in 12 weeks
COST: $89K/month for 50 clinics ($1,792/clinic/month)
ROI: 25-85x per clinic
```

---

## File Count Summary

- **Core Architecture Docs:** 36 files
- **ADR Documents:** 2 files (index + individual)
- **Presentation Materials:** 9 files
- **Diagrams:** 10+ Mermaid diagrams
- **Total Documentation:** 48+ files
- **Total Pages:** 2,000+ pages
- **Total Scenarios:** 100+
- **Total ADRs:** 12

---

## License

Proprietary — HeyJarvis.ai

---

*This documentation represents a complete, production-grade product architecture for the HeyJarvis Patient Recapture System. All components have been designed with safety, compliance, reliability, and scalability as primary requirements.*
