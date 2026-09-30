# Cost Model — Detailed Cost Analysis and Optimization

## CM.1 Cost Architecture

### Monthly Cost Breakdown (Production SaaS — 50 Clinics, 5000 Patients)

```
INFRASTRUCTURE COSTS (Monthly)
├── Compute (API + Workers)
│   ├── API servers (3x medium): $450
│   ├── Worker servers (5x medium): $750
│   ├── Scheduled jobs (1x small): $75
│   └── Total: $1,275
│
├── Database
│   ├── Primary PostgreSQL (large): $500
│   ├── Read replicas (2x): $600
│   ├── Redis cache: $200
│   └── Total: $1,300
│
├── Storage
│   ├── S3 (data + backups): $50
│   ├── Backup storage: $30
│   └── Total: $80
│
├── Queue / Message Bus
│   └── SQS / Redis Streams: $100
│
├── Networking / CDN
│   ├── Load balancer: $50
│   ├── CDN (frontend): $25
│   └── Total: $75
│
└── INFRASTRUCTURE TOTAL: $2,830/month

AI / LLM COSTS (Monthly)
├── LLM API calls
│   ├── Intent classification (small LLM, Tier 2)
│   │   └── 50,000 calls × $0.01 = $500
│   ├── Response generation (strong LLM, Tier 3)
│   │   └── 20,000 calls × $0.05 = $1,000
│   ├── Safety classification (small LLM)
│   │   └── 50,000 calls × $0.005 = $250
│   └── Other LLM calls: $250
│   └── LLM TOTAL: $2,000
│
├── Embeddings (for RAG)
│   └── 100K embeddings × $0.0001 = $10
│
└── AI TOTAL: $2,010/month

COMMUNICATION COSTS (Monthly)
├── SMS
│   ├── 100,000 messages × $0.0075 = $750
│   ├── Short code (optional): $500
│   └── SMS TOTAL: $1,250
│
├── Email
│   ├── 50,000 emails × $0.001 = $50
│   └── Email TOTAL: $50
│
├── Voice (V2, optional)
│   └── (estimated for future)
│
└── COMMUNICATION TOTAL: $1,300/month

EXTERNAL INTEGRATIONS (Monthly)
├── PMS API calls (Open Dental, etc.): $200
├── Insurance verification API: $300
├── Monitoring (Datadog): $300
├── Error tracking (Sentry): $50
├── Logging (CloudWatch / Loki): $100
└── OTHER SERVICES: $950/month

PERSONNEL COSTS (Monthly)
├── Engineering (2 FTEs): $30,000
├── AI/ML Engineer (1 FTE): $20,000
├── Product Manager (0.5 FTE): $10,000
├── QA Engineer (0.5 FTE): $7,500
├── DevOps/SRE (0.5 FTE): $10,000
├── Clinical Advisor (0.25 FTE): $5,000
└── PERSONNEL TOTAL: $82,500/month

TOTAL MONTHLY COST (at 50 clinics):
Infrastructure: $2,830
AI/LLM: $2,010
Communications: $1,300
Services: $950
Personnel: $82,500
──────────────────────
TOTAL: $89,590/month

COST PER CLINIC: $1,792/month
```

### Per-Patient Cost Analysis

```
Per 1000 patients per clinic:
- AI processing: ~$50/month (messages, classifications)
- Communications: ~$200/month (SMS, email)
- Infrastructure allocation: ~$100/month
- Per-patient cost: ~$0.35/month
- Annual per-patient cost: ~$4.20
```

## CM.2 Cost Optimization Strategies

### Strategy 1: Tiered AI

```python
# Before: Every message uses strong LLM
response = await strong_llm.generate(prompt)  # $0.05/call

# After: Route to appropriate tier
if is_simple_query(message):
    response = await template_lookup(message)  # $0
elif is_classification_task(message):
    response = await small_llm.classify(message)  # $0.01/call
else:
    response = await strong_llm.generate(prompt)  # $0.05/call

# SAVINGS: ~70% on AI costs
```

### Strategy 2: Caching

```python
# Cache common responses
CACHE_TTL = {
    "clinic_info": 86400,  # 24 hours
    "service_info": 86400,  # 24 hours
    "insurance_list": 604800,  # 7 days
    "common_responses": 3600  # 1 hour
}

async def get_clinic_info_cached(clinic_id: str):
    cache_key = f"clinic:{clinic_id}:info"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    info = await db.get_clinic(clinic_id)
    await redis.set(cache_key, json.dumps(info), ex=CACHE_TTL["clinic_info"])
    return info
```

### Strategy 3: Batch Processing

```python
# Before: Individual API calls
for patient in patients:
    await send_sms(patient)  # 1000 calls

# After: Batch API calls
await send_sms_batch(patients)  # 1 call for batch
```

### Strategy 4: Right-Sizing Infrastructure

```yaml
# Scale based on load
api:
  min_replicas: 2
  max_replicas: 10
  target_cpu: 70%

workers:
  min_replicas: 3
  max_replicas: 20
  scaling_metric: queue_depth
  scale_up_threshold: 1000
  scale_down_threshold: 100
```

### Strategy 5: Smart Scheduling

```python
# Send messages during business hours
# Don't wake up workers unnecessarily
# Batch similar operations

SEND_SCHEDULE = {
    "sms": {
        "batch_size": 100,
        "batch_interval": 5,  # seconds
        "business_hours_only": True
    },
    "email": {
        "batch_size": 1000,
        "batch_interval": 60,
        "business_hours_only": False
    }
}
```

## CM.3 Cost Monitoring

```python
class CostMonitor:
    """Track and alert on costs."""

    ALERT_THRESHOLDS = {
        "daily_ai_cost": 100,  # Alert if > $100/day
        "daily_sms_cost": 100,  # Alert if > $100/day
        "monthly_total_budget": 100000  # Alert if approaching
    }

    async def check_costs(self):
        daily_ai = await self.get_daily_ai_cost()
        daily_sms = await self.get_daily_sms_cost()

        if daily_ai > self.ALERT_THRESHOLDS["daily_ai_cost"]:
            await self.alert(f"AI cost spike: ${daily_ai}")

        if daily_sms > self.ALERT_THRESHOLDS["daily_sms_cost"]:
            await self.alert(f"SMS cost spike: ${daily_sms}")
```

## CM.4 Cost vs. Quality Trade-offs

| Optimization | Cost Impact | Quality Impact | Recommended |
|-------------|-------------|----------------|-------------|
| Strong LLM → Small LLM | -80% | May reduce quality for complex cases | Tiered approach |
| Skip caching | +20% | No impact (just slower) | Always cache |
| Reduce retries | -5% | May miss some messages | 3 retries max |
| Smaller DB instance | -30% | Slower queries, timeouts | Scale based on load |
| Skip backup testing | -$0 | Risk of unrecoverable backups | NEVER SKIP |
| Reduce monitoring | -$50/mo | May miss issues | Minimum required |

## CM.5 Cost Projections

### At Scale (200 Clinics, 50,000 Patients)

```
INFRASTRUCTURE: $8,000/month
AI/LLM: $7,000/month
COMMUNICATIONS: $5,000/month
SERVICES: $2,500/month
PERSONNEL: $150,000/month (scaled team)
─────────────────────────────────────────
TOTAL: $172,500/month
COST PER CLINIC: $863/month
```

### At Scale (500 Clinics, 200,000 Patients)

```
INFRASTRUCTURE: $20,000/month
AI/LLM: $20,000/month
COMMUNICATIONS: $20,000/month
SERVICES: $6,000/month
PERSONNEL: $350,000/month (scaled team)
─────────────────────────────────────────
TOTAL: $416,000/month
COST PER CLINIC: $832/month
```

Economies of scale reduce per-clinic cost as volume increases.
