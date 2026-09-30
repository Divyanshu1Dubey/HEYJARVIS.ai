# Rollout Plan — Phased Production Rollout Strategy

## RP.1 Rollout Philosophy

1. **Patient safety is non-negotiable.** Every phase must pass safety evaluation.
2. **Gradual exposure.** Start with zero patients, end with all patients.
3. **Human oversight at every stage.** Staff review required before each expansion.
4. **Easy rollback.** Every phase must be reversible.
5. **Measure everything.** Data-driven decisions at each gate.

## RP.2 Phase Definitions

### Phase 0: Architecture + Research (Weeks 1-4)

**Goal:** Complete architecture, design, and initial research.

**Deliverables:**
- Complete architecture documentation (this document set)
- Database schema designed and reviewed
- API specification complete
- Security architecture reviewed
- Compliance requirements documented
- LLM provider selected and tested
- Initial safety test cases written
- Technical spike for scheduling integration

**Go/No-Go Criteria:**
- Architecture approved by Principal Engineer
- Security review passed
- Compliance review passed
- Budget approved
- Timeline approved

**Team:** 2 Engineers, 1 PM, 1 Clinical Advisor

---

### Phase 1: Rules-First Recapture MVP (Weeks 5-12)

**Goal:** Deploy rule-based recapture with no AI.

**Features:**
- Patient database (basic CRUD)
- Appointment sync from PMS
- Basic consent management
- Rule-based eligibility engine
- SMS communication (via Twilio)
- Campaign engine (deterministic rules)
- Staff dashboard (basic)
- Basic analytics

**What the AI does NOT do in Phase 1:**
- No LLM for message generation (templates only)
- No intent classification (rules-based)
- No conversation AI
- No prediction models

**Example rule:**
```
IF appointment.cancelled AND NOT patient.opted_out AND consent.sms = true:
  → Add to recapture queue
  → After 1 hour: Send SMS template "cancellation_recovery_1"
  → If no response in 24h: Send SMS template "cancellation_recovery_2"
  → If still no response in 48h: Create staff task
  → STOP: If patient replies, opts out, or books
```

**Testing:**
- Unit tests: >90% coverage
- Integration tests: All PMS adapters
- E2E tests: Full recapture flow
- Safety tests: Consent, opt-out, suppression

**Go/No-Go Criteria:**
- All tests pass
- Safety tests pass (100%)
- Consent/opt-out verified
- Staff trained
- Pilot clinic onboarded
- 2 weeks stable in staging

**Rollout:**
1. Week 8: Staging deployment with synthetic data
2. Week 9: Pilot with 1 clinic (synthetic patients)
3. Week 10: Pilot with 1 clinic (real patients, limited)
4. Week 12: Expand to 3 clinics

**Team:** 3 Engineers, 1 PM, 0.5 Clinical Advisor

---

### Phase 2: AI Personalization (Weeks 13-20)

**Goal:** Add AI for message personalization and conversation.

**Features:**
- LLM-powered message generation (templated + personalized)
- Intent classification (AI)
- Conversation agent (basic)
- Safety classifier
- Human handoff system
- Response validation layer
- A/B testing framework

**AI Components:**
- Intent classifier (fine-tuned)
- Message generator (LLM with tools)
- Safety classifier (LLM + rules)
- Response validator (deterministic)

**Safety Requirements:**
- 100% emergency detection on test set
- 0% medical advice leakage
- All responses validated before sending
- Human handoff for safety events

**Testing:**
- AI evaluation suite (>100 test cases)
- Safety test suite (>50 test cases)
- Prompt regression tests
- Hallucination tests
- Red team exercises

**Go/No-Go Criteria:**
- AI evaluation passes all thresholds
- Safety evaluation passes
- Hallucination rate < 1%
- Staff trained on AI capabilities
- Pilot clinic (1) approves

**Rollout:**
1. Week 16: Shadow testing (AI runs but doesn't affect patients)
2. Week 17: Canary (10% of traffic to AI)
3. Week 18: Expand to 50% traffic
4. Week 20: Full rollout to pilot clinics

**Team:** 4 Engineers (1 AI/ML), 1 PM, 0.5 Clinical Advisor

---

### Phase 3: ML Prediction (Weeks 21-28)

**Goal:** Add ML-based predictions for prioritization and optimization.

**Features:**
- Conversion probability model
- Optimal contact time prediction
- Priority scoring model
- Next-best-action model
- Message ranking model
- Model monitoring

**ML Components:**
- Gradient boosting model for conversion prediction
- Survival model for optimal timing
- Multi-class classifier for next-best-action

**Data Requirements:**
- Minimum 2,000 outreach outcomes
- Minimum 1,000 conversations labeled

**Go/No-Go Criteria:**
- Offline evaluation: PR-AUC > 0.3
- Calibration: Brier score < 0.15
- No data leakage confirmed
- Champion model outperforms rules baseline by >10%

**Rollout:**
1. Week 24: Shadow testing (predictions logged but not used)
2. Week 25: A/B test (10% AI-driven priority)
3. Week 26: Expand A/B to 50%
4. Week 28: Full rollout if A/B positive

**Team:** 4 Engineers (1 AI/ML), 1 PM, 0.5 Clinical Advisor

---

### Phase 4: Multi-Channel (Weeks 29-36)

**Goal:** Add email and voice channels.

**Features:**
- Email channel
- Voice channel (V2)
- Multi-channel orchestration
- Channel preference engine
- Unified conversation inbox

**Channels:**
- SMS: V1 (already implemented)
- Email: New
- Voice: New (optional, add later if needed)
- Web chat: V1 (already implemented)

**Go/No-Go Criteria:**
- Email delivery rate > 98%
- Email template compliance verified
- Voice quality acceptable (if implemented)
- No cross-channel confusion

**Rollout:**
1. Week 32: Email to pilot clinics
2. Week 34: Email to all Phase 1-3 clinics
3. Week 36: Voice (optional)

**Team:** 3 Engineers, 1 PM

---

### Phase 5: Real Integrations (Weeks 37-44)

**Goal:** Connect to real PMS systems.

**Features:**
- Open Dental integration
- Eaglesoft integration
- Dentrix integration
- Real-time appointment sync
- Real-time insurance verification
- Webhook handling

**Integrations:**
- Scheduling: All 3 major PMS
- Insurance: At least 1 provider
- Voice: Twilio

**Go/No-Go Criteria:**
- All PMS adapters tested with real systems
- Webhook handling reliable
- Idempotency verified
- Conflict resolution tested
- Fallback behavior defined

**Rollout:**
1. Week 39: Integration testing with partner clinic
2. Week 41: Expand to pilot clinics
3. Week 44: All clinics

**Team:** 3 Engineers, 1 PM, 0.5 Integration Specialist

---

### Phase 6: Optimization (Weeks 45-52)

**Goal:** Optimize based on real-world data.

**Features:**
- A/B testing infrastructure
- Message optimization
- Timing optimization
- Channel optimization
- Cost optimization

**Activities:**
- Run A/B tests on message wording
- Optimize send timing
- Optimize channel selection
- Reduce AI costs through caching
- Optimize database queries

**Go/No-Go Criteria:**
- A/B testing framework operational
- At least 3 experiments completed
- Positive lift demonstrated
- Costs within budget

**Team:** 3 Engineers (1 AI/ML), 1 PM, 1 Data Analyst

---

### Phase 7: Scale (Week 52+)

**Goal:** Scale to 100+ clinics.

**Features:**
- Multi-region deployment
- Advanced analytics
- Custom reporting
- White-label options
- Advanced AI features

**Team:** Scaling team based on growth

## RP.3 Rollout Gates Summary

| Gate | Required | Phase 1 | Phase 2 | Phase 3+ |
|------|----------|---------|---------|----------|
| Safety tests pass | ✓ | ✓ | ✓ | ✓ |
| Consent verified | ✓ | ✓ | ✓ | ✓ |
| Opt-out verified | ✓ | ✓ | ✓ | ✓ |
| Staff trained | ✓ | ✓ | ✓ | ✓ |
| Pilot clinic approval | ✓ | ✓ | ✓ | ✓ |
| AI evaluation passes | — | — | ✓ | ✓ |
| A/B test positive | — | — | — | ✓ |
| Compliance review | ✓ | ✓ | ✓ | ✓ |

## RP.4 Rollback Procedures

Each phase has a defined rollback:

**Phase 1 Rollback:** Disable campaigns, keep data
**Phase 2 Rollback:** Disable AI features, fall back to templates
**Phase 3 Rollback:** Disable ML features, use rules
**Phase 4 Rollback:** Disable new channels, use existing
**Phase 5 Rollback:** Disable integrations, manual data entry
**Phase 6 Rollback:** Revert experiments, keep stable config
