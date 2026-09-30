# Architecture Decision Records — Index

## ADR-001: Monorepo Repository Structure

**Status:** Accepted

**Context:** Need to decide between monorepo and polyrepo for the HeyJarvis platform.

**Decision:** Use monorepo with pnpm workspaces and Turborepo.

**Rationale:**
- Tight coupling between AI, policy, and API layers
- Shared libraries reduce duplication
- Easier cross-cutting changes
- Simpler CI/CD
- Better dependency management

**Consequences:**
- Positive: Simplified development, easier refactoring
- Negative: Larger repo, longer CI times (mitigated by Turborepo caching)

---

## ADR-002: PostgreSQL as Primary Database

**Status:** Accepted

**Context:** Need to choose a database for production data.

**Decision:** Use PostgreSQL with Row-Level Security (RLS).

**Rationale:**
- ACID compliance critical for appointments and financial data
- JSONB for flexible schema (integrations, events)
- RLS for tenant isolation
- Mature ecosystem, strong community
- Excellent performance for relational data

**Alternatives considered:**
- MySQL: Less robust JSON support, weaker RLS
- MongoDB: No ACID guarantees, no RLS
- CockroachDB: Good but less mature ecosystem

---

## ADR-003: Rules Before AI

**Status:** Accepted

**Context:** How much AI should be used in V1?

**Decision:** Deterministic rules for all decisions in Phase 1. AI only in Phase 2+.

**Rationale:**
- Rules are auditable and explainable
- Rules are safer (no hallucination risk)
- Rules are cheaper
- Rules work without training data
- Build trust before adding complexity

**Consequences:**
- Phase 1 is simpler to build and validate
- Phase 2 requires careful evaluation before deployment
- Business rules are defined in code, not LLM prompts

---

## ADR-004: LLM Provider — Anthropic Claude

**Status:** Accepted

**Context:** Need to choose an LLM provider for AI features.

**Decision:** Use Anthropic Claude API as primary LLM provider.

**Rationale:**
- Strong safety alignment
- Good instruction following
- Reliable API
- Strong performance on classification tasks
- Good rate limits
- BAA available

**Alternatives considered:**
- OpenAI GPT-4: Similar quality, slightly higher cost
- Open-source models: Inferior safety/alignment, self-hosting complexity

**Consequences:**
- Vendor dependency on Anthropic
- Need backup LLM provider for failover
- Costs scale with usage

---

## ADR-005: Redis Streams for Queue (V1)

**Status:** Accepted

**Context:** Need a message queue for async processing.

**Decision:** Use Redis Streams for V1, migrate to Kafka at scale.

**Rationale:**
- Simple to set up and operate
- Low operational overhead
- Sufficient for V1 scale (< 10K messages/sec)
- Can migrate to Kafka later when needed

**Alternatives considered:**
- Kafka: Overkill for V1, higher operational complexity
- SQS: External dependency, less control
- RabbitMQ: Higher operational overhead

**Consequences:**
- Migration path to Kafka defined
- May need to reimplement consumers at scale
- Redis as single point of failure (mitigated with cluster)

---

## ADR-006: Patient State Machine

**Status:** Accepted

**Context:** How to model patient journey through the system?

**Decision:** Implement a strict state machine for patient states.

**Rationale:**
- Deterministic and auditable
- Prevents invalid state transitions
- Makes system behavior predictable
- Easier to debug and test

**Consequences:**
- All state changes are logged
- Invalid transitions are rejected
- System behavior is consistent

---

## ADR-007: Tool Calling with Confirmation Gates

**Status:** Accepted

**Context:** How to allow AI to interact with external systems safely?

**Decision:** AI can call tools, but certain tools require confirmation.

**Rationale:**
- Prevents AI from making unauthorized changes
- Patient must confirm before booking
- Human must confirm before certain actions
- Audit trail for all tool calls

**Consequences:**
- Safer AI interactions
- Better patient experience (no surprise bookings)
- Clear audit trail

---

## ADR-008: Consent-First Communication

**Status:** Accepted

**Context:** What communication rules to enforce?

**Decision:** Require explicit consent before any patient communication. Never rely on implied consent.

**Rationale:**
- TCPA compliance
- HIPAA compliance
- Patient trust
- Avoids regulatory penalties
- Best practice regardless of legal minimums

**Consequences:**
- Higher onboarding friction (consent collection)
- Lower opt-out rates (patients expect to be asked)
- Requires consent management system
- Legal review required for consent language

---

## ADR-009: PHI Minimization in AI Context

**Status:** Accepted

**Context:** What patient data should be sent to LLM providers?

**Decision:** Minimize PHI in LLM prompts. Only include first name, never full name, phone, email, or DOB.

**Rationale:**
- LLM providers are third parties
- BAA required but PHI exposure should still be minimized
- Reduces blast radius if LLM is compromised
- Patient trust

**Consequences:**
- Some AI capabilities limited (can't show full patient record)
- Need structured data for most operations
- LLM works best with minimal context

---

## ADR-010: Shadow → Canary → Production Deployment

**Status:** Accepted

**Context:** How to deploy AI/ML models safely?

**Decision:** All AI/ML changes go through Shadow → Canary → Full Production deployment.

**Rationale:**
- Prevents bad models from affecting patients
- Allows comparison to baseline
- Early detection of regressions
- Industry best practice

**Consequences:**
- Slower deployment for AI changes
- Requires monitoring infrastructure
- Requires shadow infrastructure

---

## ADR-011: Holdout Groups for Attribution

**Status:** Accepted

**Context:** How to measure recapture effectiveness?

**Decision:** Use randomized holdout groups for causal attribution.

**Rationale:**
- Only reliable way to measure incrementality
- Required for ROI calculation
- Industry standard for causal inference

**Consequences:**
- Some patients don't receive outreach (ethical trade-off)
- Requires statistical expertise
- Sample size requirements

---

## ADR-012: Separate Evaluation Environment

**Status:** Accepted

**Context:** Where to test AI changes before production?

**Decision:** Separate evaluation environment with synthetic data, completely isolated from production.

**Rationale:**
- No risk to production data
- Reproducible test conditions
- Can test edge cases safely
- Required for safety validation

**Consequences:**
- Need to maintain separate environment
- Need to sync configuration changes
- Additional infrastructure cost
