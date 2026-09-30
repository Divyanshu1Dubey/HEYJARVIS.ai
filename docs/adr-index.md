# Architecture Decision Records

## ADR-001: LLM Provider Selection

**Status:** Accepted
**Date:** 2025-10-01
**Decision Makers:** Principal Engineer, CTO

### Context
We need an LLM for intent classification, conversation, and message generation. Must be HIPAA-compatible, reliable, and cost-effective at scale.

### Options
| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **Anthropic Claude** (RECOMMENDED) | Best safety, long context, good at tool use | Slightly higher cost | ~$3-15/1M tokens |
| OpenAI GPT-4 | Good quality, widely used | Safety less explicit, shorter context | ~$2.5-10/1M tokens |
| Google Gemini | Good multimodal, competitive pricing | Less tool-use experience | ~$1-5/1M tokens |
| Self-hosted Llama | Full control, no data sharing | Requires GPU infra, quality gap | High infra cost |

### Decision
Use **Anthropic Claude** as primary, with OpenAI as fallback.

### Rationale
- Claude has best-in-class safety alignment (explicit Constitutional AI)
- Tool calling is well-supported
- Long context window (200K) allows complex patient context
- BAA available from Anthropic for HIPAA
- Fallback to GPT-4 if Claude unavailable

### Consequences
- Vendor lock-in mitigated by abstraction layer
- Cost is higher but justified by safety
- Need tiered routing for cost control

---

## ADR-002: Database Strategy

**Status:** Accepted
**Date:** 2025-10-01

### Context
We need a database that supports complex queries, audit trails, and scales to millions of records.

### Options
| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **PostgreSQL** (RECOMMENDED) | Mature, rich query support, JSON support, great tooling | Vertical scaling limits | $50-500/month |
| CockroachDB | Distributed, horizontal scale | More complex, smaller ecosystem | $200-1000/month |
| MongoDB | Flexible schema | Weaker consistency, harder joins | $50-500/month |

### Decision
Use **PostgreSQL 16** with read replicas.

### Rationale
- ACID compliance essential for booking
- JSONB for flexible patient/conversation data
- Excellent tooling and ORM support
- Row-level security for multi-tenancy
- Read replicas for analytics queries
- Proven at scale for similar SaaS applications

### Consequences
- Single-primary architecture (no distributed transactions)
- Read replicas for analytics (eventual consistency acceptable)
- Connection pooling required (PgBouncer)

---

## ADR-003: Queue Architecture

**Status:** Accepted
**Date:** 2025-10-01

### Context
We need async processing for campaigns, messages, AI inference, and integrations.

### Options
| Option | Pros | Cons | Complexity |
|--------|------|------|------------|
| **Redis + Celery** (RECOMMENDED) | Simple, proven, good Python support | Redis single-node limit | Low |
| Temporal | Stronger guarantees, built-in retries | Steeper learning curve | Medium-High |
| Kafka | High throughput, streaming | Overkill for our scale | High |
| SQS | Managed, reliable | Vendor lock-in, higher latency | Low |

### Decision
Use **Redis + Celery** for development/small scale, with migration path to Temporal at scale.

### Rationale
- Perfect fit for our workload types (jobs, delays, campaigns)
- Familiar to Python developers
- Built-in retry, scheduling, monitoring
- Easy to migrate later if needed

### Consequences
- Redis as single point of failure (mitigate with Redis Cluster)
- Workers need to be horizontally scalable
- Dead-letter queues needed for failed jobs

---

## ADR-004: Multi-Tenant Isolation

**Status:** Accepted
**Date:** 2025-10-01

### Context
We need strong tenant isolation to prevent data leakage between dental practices.

### Options
| Option | Pros | Cons | Isolation |
|--------|------|------|-----------|
| **Row-level security (RLS)** (RECOMMENDED) | Strong isolation, single database | Complex queries | Strong |
| Separate databases | Complete isolation | Expensive, complex ops | Complete |
| Separate schemas | Moderate isolation | Still shared infra | Moderate |

### Decision
Use **Row-Level Security** in PostgreSQL, enforced at every query layer.

### Rationale
- Strongest isolation achievable in shared database
- Cannot be bypassed by application code
- Single backup/restore for all tenants
- Efficient resource utilization
- Industry standard for multi-tenant SaaS

### Consequences
- All queries must include tenant_id
- Index design must account for tenant_id
- Requires careful query review
- Application must never bypass RLS

---

## ADR-005: Communication Architecture

**Status:** Accepted
**Date:** 2025-10-01

### Context
We need to send/receive messages across SMS, email, and eventually voice.

### Options
| Option | Pros | Cons |
|--------|------|------|
| **Adapter pattern per channel** (RECOMMENDED) | Clean separation, easy to add channels | More interfaces |
| Unified message API | Simpler | Harder to extend |
| Third-party aggregator | Simple | Less control, higher cost |

### Decision
Use **adapter pattern** with:
- Primary SMS: Twilio
- Primary Email: Postmark
- Future voice: Twilio Voice or similar

### Rationale
- Clean separation allows adding channels without changing core logic
- Direct provider integration gives best control and pricing
- Fallback providers easy to add
- Each channel has different consent requirements

### Consequences
- Need to maintain provider integrations
- Need provider failover logic
- Each channel has its own rate limits and constraints

---

## ADR-006: AI Safety Architecture

**Status:** Accepted
**Date:** 2025-10-01

### Context
AI must never fabricate, diagnose, or bypass safety rules.

### Options
| Option | Pros | Cons |
|--------|------|------|
| **Rules + validation layer** (RECOMMENDED) | Deterministic safety, auditable | More code |
| LLM-only safety | Simpler | Unreliable |
| Hybrid (rules + LLM) | Best of both | Most complex |

### Decision
Use **deterministic rules FIRST, then LLM, then strict validation**.

### Rationale
- Rules are 100% reliable for known conditions
- LLM is good for nuanced conversation
- Validation catches any LLM mistakes
- Combined approach is safest

### Consequences
- More code to maintain
- Validation adds latency (~50-100ms)
- Requires careful prompt engineering
- LLM cannot override rules

---

## ADR-007: Feature Store Strategy

**Status:** Accepted
**Date:** 2025-10-01

### Context
ML models need consistent, versioned features for training and inference.

### Options
| Option | Pros | Cons |
|--------|------|------|
| **Application DB with snapshots** (RECOMMENDED) | Simple, no extra infra | Manual feature management |
| Feast/Tecton | Full feature store | Complex, overkill for V1 |
| Data warehouse | Good for batch | Slow for real-time |

### Decision
Use **application database with feature snapshots**.

### Rationale
- V1 doesn't need real-time feature serving at scale
- Simpler to operate
- Features can be computed in batch jobs
- Snapshot approach prevents data leakage

### Consequences
- Need careful snapshot management
- Feature computation in batch
- May need to migrate to Feast later for real-time

---

## ADR-008: Observability Stack

**Status:** Accepted
**Date:** 2025-10-01

### Context
We need logs, metrics, traces, and alerting.

### Options
| Component | Recommendation | Alternative |
|-----------|---------------|-------------|
| Logs | **CloudWatch + OpenSearch** | ELK, Loki |
| Metrics | **CloudWatch + Prometheus** | Datadog, Grafana |
| Traces | **OpenTelemetry + Jaeger** | Datadog APM |
| Alerting | **PagerDuty + CloudWatch Alarms** | OpsGenie |
| Dashboards | **Grafana** | CloudWatch Dashboards |

### Decision
Use **Open-source observability stack on AWS**.

### Rationale
- Cost-effective
- Open standards (no vendor lock-in)
- Full control over data
- Good enough for our scale

### Consequences
- Requires self-hosting and maintenance
- More setup work
- Need SRE expertise
