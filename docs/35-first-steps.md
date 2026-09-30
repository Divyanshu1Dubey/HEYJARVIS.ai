# First Implementation Steps — Exact Build Order

## Before You Write Any Code

### Step 1: Get Legal Review (Week 1)
- [ ] Have legal counsel review HIPAA compliance plan
- [ ] Have legal counsel review TCPA compliance plan
- [ ] Draft Business Associate Agreement template
- [ ] Review consent language with legal
- [ ] Review privacy policy with legal

### Step 2: Set Up Infrastructure (Week 1-2)
```bash
# Cloud accounts
→ Create AWS/GCP account
→ Set up IAM users and roles
→ Set up VPC
→ Set up Kubernetes cluster (staging)
→ Set up PostgreSQL (staging)
→ Set up Redis (staging)
→ Set up S3 buckets
→ Set up domain and SSL certificates
```

### Step 3: Set Up Development Environment (Week 2)
```bash
# Local development
→ Create monorepo structure
→ Set up Docker Compose for local dev
→ Set up Python environment (API, worker)
→ Set up Node.js environment (frontend)
→ Set up database migrations (Alembic)
→ Set up linting and formatting
→ Create .env.example
→ Document development setup
```

### Step 4: Set Up CI/CD (Week 2)
```bash
# GitHub Actions
→ Create CI workflow (lint, test)
→ Create security scan workflow
→ Create deploy to staging workflow
→ Set up secrets in GitHub
→ Configure branch protection
```

## Phase 1: Rules-First MVP (Weeks 5-12)

### Week 5: Database Foundation

**Priority 1: Create all database tables**
```bash
# Files to create:
→ packages/database/src/models/patient.py
→ packages/database/src/models/clinic.py
→ packages/database/src/models/consent.py
→ packages/database/src/models/communication_preference.py
→ packages/database/src/models/appointment.py
→ packages/database/src/models/conversation.py
→ packages/database/src/models/message.py
→ packages/database/src/models/recapture_opportunity.py
→ packages/database/src/models/recapture_attempt.py
→ packages/database/src/models/campaign.py
→ packages/database/src/models/human_handoff.py
→ packages/database/src/models/audit_log.py

# Migration:
→ alembic revision --autogenerate -m "initial_schema"
→ alembic upgrade head
```

**Priority 2: Create database indexes and constraints**
```sql
-- Critical indexes for performance
CREATE INDEX idx_patients_clinic ON patients(clinic_id);
CREATE INDEX idx_opportunities_patient ON recapture_opportunities(patient_id);
CREATE INDEX idx_opportunities_clinic ON recapture_opportunities(clinic_id);
CREATE INDEX idx_opportunities_state ON recapture_opportunities(state);
CREATE INDEX idx_consents_patient ON consents(patient_id);
CREATE INDEX idx_audit_log_tenant ON audit_logs(tenant_id, created_at);
```

### Week 6: Core API + Authentication

**Priority 1: Authentication**
```python
# JWT authentication
→ Implement token creation/validation
→ Implement refresh tokens
→ Create auth middleware
→ Implement MFA (optional for V1)
```

**Priority 2: Clinic/Staff Management**
```python
# CRUD endpoints
POST /api/v1/clinics
GET  /api/v1/clinics/:id
POST /api/v1/clinics/:id/staff
GET  /api/v1/clinics/:id/staff
```

**Priority 3: Patient Management**
```python
POST /api/v1/patients
GET  /api/v1/patients/:id
PUT  /api/v1/patients/:id
GET  /api/v1/patients (with tenant filter)
```

### Week 7: Consent + Suppression + Policy Engine

**Priority 1: Consent Management**
```python
# Consent endpoints
POST /api/v1/patients/:id/consents
GET  /api/v1/patients/:id/consents
PUT  /api/v1/patients/:id/consents/:id
DELETE /api/v1/patients/:id/consents/:id

# Policy engine
→ Can we send SMS to this patient? (checks consent)
→ Can we send email to this patient?
→ Has frequency cap been reached?
→ Is patient opted out?
→ Is it quiet hours?
```

**Priority 2: Suppression Lists**
```python
→ SuppressionList class
→ Add to suppression list
→ Check suppression before any outreach
→ Handle STOP keyword
```

### Week 8: Event System + Queue

**Priority 1: Event Definitions**
```python
# Define all events
lead.created
appointment.cancelled
appointment.completed
appointment.no_show
patient.opted_out
conversation.started
message.sent
message.delivered
message.failed
human_handoff.created
```

**Priority 2: Queue Infrastructure**
```python
→ Redis Streams setup
→ Event producer
→ Event consumer
→ Retry logic (exponential backoff)
→ Dead letter queue
→ Idempotency handling
```

### Week 9: Campaign Engine

**Priority 1: Campaign Configuration**
```python
# Campaign CRUD
POST /api/v1/campaigns
GET  /api/v1/campaigns
GET  /api/v1/campaigns/:id
PUT  /api/v1/campaigns/:id
DELETE /api/v1/campaigns/:id

# Campaign execution
→ Evaluate eligibility (policy engine)
→ Execute sequence (send messages)
→ Handle stop conditions
→ Track outcomes
```

**Priority 2: Message Templates**
```python
# Template system
→ Template CRUD
→ Variable substitution
→ Channel-specific templates
→ Version tracking
```

**Priority 3: Initial Templates**
```
Create 10-15 templates:
- cancellation_recovery_1
- cancellation_recovery_2
- no_show_recovery_1
- lead_follow_up_1
- recall_overdue_1
- treatment_plan_follow_up_1
```

### Week 10: Communication Layer

**Priority 1: SMS (Twilio)**
```python
→ Twilio integration
→ Send SMS function
→ Handle delivery webhooks
→ Handle STOP keyword
→ Track delivery status
```

**Priority 2: Email (Postmark)**
```python
→ Postmark integration
→ Send email function
→ Handle delivery webhooks
→ Handle unsubscribe
→ Track delivery status
```

### Week 11: Staff Dashboard (Basic)

```python
# Screens:
→ Recapture Overview (metrics, charts)
→ Opportunities Queue (list, filters)
→ Human Handoff Queue (prioritized list)
→ Patient Search
→ Campaign List
→ Basic Analytics
```

### Week 12: Testing + Pilot

```
→ All unit tests pass (>90% coverage)
→ Integration tests pass
→ E2E tests pass
→ Safety tests pass (consent, opt-out, suppression)
→ Performance tests pass
→ Deploy to staging
→ Onboard pilot clinic
→ Run with real patients (limited)
→ Gather feedback
→ Fix bugs
```

## Phase 2: AI Personalization (Weeks 13-20)

### Week 13-14: AI Infrastructure
```
→ Set up LLM client (Anthropic)
→ Create prompt management system
→ Create output validation layer
→ Implement safety classifier
→ Create tool framework
→ Implement tenant-scoped RAG
```

### Week 15-16: Conversation AI
```
→ Write conversation agent prompt
→ Implement intent classifier
→ Implement safety classification
→ Create tool definitions (check_availability, etc.)
→ Implement tool calling
→ Implement human handoff
```

### Week 17-18: Message Generation
```
→ Write message generator prompt
→ Implement personalization
→ Implement output validation
→ Test against hallucination test set
→ Run safety evaluation
```

### Week 19-20: Integration + Rollout
```
→ Shadow testing
→ Canary deployment
→ Full rollout
→ Staff training
```

## The Very First Day of Coding

```python
# 1. Create the project
mkdir -p heyjarvis/{apps,packages,infra,docs,tests}
cd heyjarvis
git init

# 2. Set up Python project
python -m venv venv
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
pip install pytest pytest-asyncio

# 3. Create first API endpoint
# apps/api/src/main.py

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="HeyJarvis API")

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/patients")
async def create_patient(data: dict):
    # TODO: Implement
    return {"id": "temp-uuid"}

# 4. Run it
uvicorn apps.api.src.main:app --reload --port 8000

# 5. Verify it works
curl http://localhost:8000/health
# → {"status": "ok", "timestamp": "..."}
```

## Acceptance Criteria for Each Phase

### Phase 1 Complete When:
- [ ] API is running with all endpoints
- [ ] Database has all tables with proper constraints
- [ ] Consent management works (create, verify, revoke)
- [ ] Opt-out handling works (STOP keyword)
- [ ] Campaign engine runs basic campaigns
- [ ] SMS and email sending works
- [ ] Staff dashboard shows recapture overview
- [ ] All safety tests pass (100%)
- [ ] All unit tests pass (>90% coverage)
- [ ] Pilot clinic using system successfully

### Phase 2 Complete When:
- [ ] AI conversation works for common scenarios
- [ ] Safety classifier catches 100% of test emergencies
- [ ] Hallucination rate < 1%
- [ ] Output validation catches fabricated claims
- [ ] Human handoff works seamlessly
- [ ] Staff can take over conversations
- [ ] AI evaluation suite passes all thresholds
- [ ] Pilot clinic approves AI features

## What NOT to Build in V1

❌ Voice AI (add in Phase 4)
❌ Multi-language (add when needed)
❌ Advanced ML predictions (Phase 3)
❌ Real-time PMS sync (Phase 5)
❌ Custom reporting builder (use built-in reports)
❌ White-label / custom branding
❌ Advanced A/B testing (basic version in Phase 2)
❌ Mobile app (web-first)
❌ Patient-facing mobile app
❌ Advanced analytics (basic in Phase 1)

## What to Build First (Priority Order)

**Week 1:** Nothing code — architecture, design, legal
**Week 2:** Infrastructure + development environment
**Week 3-4:** Database + core API + authentication
**Week 5-6:** Consent + suppression + policy engine
**Week 7-8:** Event system + queue + job scheduling
**Week 9-10:** Campaign engine + message templates
**Week 11-12:** Communication layer (SMS, email) + dashboard
**Week 13+:** AI features (only after Phase 1 is stable)
