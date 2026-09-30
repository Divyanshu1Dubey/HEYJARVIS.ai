# Exact First Implementation Steps

## Pre-Flight Checklist

Before writing any code:

```
WEEK 0: PREPARATION (No Coding)

Day 1-2: Legal & Compliance Foundation
  [ ] Engage healthcare attorney for HIPAA review
  [ ] Draft BAA templates (you + each vendor)
  [ ] Review TCPA requirements with legal counsel
  [ ] Document state-specific requirements
  [ ] Draft privacy policy
  [ ] Draft terms of service
  [ ] Create patient consent form template
  [ ] Create data processing agreement

Day 3-4: Vendor Contracts
  [ ] Sign BAA with LLM provider (Anthropic)
  [ ] Sign BAA with cloud provider (AWS/GCP)
  [ ] Sign BAA with SMS provider (Twilio)
  [ ] Sign BAA with email provider (Postmark)
  [ ] Set up HIPAA-eligible accounts
  [ ] Configure audit logging for all vendors

Day 5: Development Environment
  [ ] Set up development environment
  [ ] Configure Git repository
  [ ] Set up CI/CD pipeline
  [ ] Configure secrets management (Vault/SSM)
  [ ] Set up staging environment (HIPAA-eligible)
```

## PHASE 1: Foundation (Weeks 1-4)

### Week 1: Project Setup

```
Day 1: Repository Structure
  → Create monorepo with /apps, /packages, /services, /ml, /docs, /tests
  → Set up linting (ruff, black, mypy)
  → Set up testing framework (pytest)
  → Configure pre-commit hooks
  → Set up Docker configuration
  → Create README with setup instructions

Day 2: Database Schema (Core Tables)
  → Create organizations table
  → Create clinics table
  → Create users table
  → Create patients table
  → Create consents table
  → Create audit_logs table
  → Set up RLS policies
  → Create migration scripts
  → Test RLS enforcement

Day 3: API Foundation
  → Set up FastAPI project
  → Configure CORS
  → Implement JWT authentication
  → Implement RBAC
  → Create health check endpoint
  → Create API documentation
  → Implement error handling
  → Add request ID middleware

Day 4: Event Infrastructure
  → Set up Redis
  → Create event schema
  → Implement event producer
  → Implement event consumer
  → Create dead-letter queue
  → Test event flow
  → Add event replay capability

Day 5: Safety Foundation
  → Create emergency keyword list
  → Implement pattern matcher
  → Create safety event types
  → Implement audit logging
  → Test safety triggers
```

### Week 2: Core Business Logic

```
Day 1-2: Patient Management
  → Create patient CRUD endpoints
  → Implement patient validation
  → Implement patient search
  → Create patient timeline endpoint
  → Add patient merge capability (for duplicates)
  → Test patient operations

Day 3: Consent Management
  → Create consent CRUD
  → Implement consent verification
  → Create consent revocation
  → Implement consent history tracking
  → Add consent to policy engine
  → Test consent flows

Day 4: Communication Preferences
  → Create preferences CRUD
  → Implement quiet hours logic
  → Implement channel preferences
  → Create timezone handling
  → Test preference enforcement

Day 5: Integration Adapters (Base)
  → Create SchedulingProvider interface
  → Create PatientProvider interface
  → Create CommunicationProvider interface
  → Create mock implementations
  → Write tests for adapters
```

### Week 3: Policy Engine

```
Day 1-2: Policy Engine Core
  → Create PolicyEngine class
  → Implement consent check
  → Implement opt-out check
  → Implement frequency cap check
  → Implement quiet hours check
  → Implement suppression check
  → Create policy context object
  → Write comprehensive tests

Day 3: Policy Rules Configuration
  → Create per-tenant policy config
  → Implement rule evaluation
  → Create rule composition
  → Add rule priority
  → Implement rule caching
  → Test rule combinations

Day 4: Safety Policy
  → Integrate emergency keyword matcher
  → Implement safety escalation rules
  → Create safety event handler
  → Implement safety audit trail
  → Test safety triggers

Day 5: Policy Integration Tests
  → Test cross-tenant isolation
  → Test policy override rejection
  → Test edge cases
  → Load test policy engine
  → Performance benchmarks
```

### Week 4: Recapture Engine (Rules-First)

```
Day 1-2: Opportunity Detection
  → Create event handlers for:
    - appointment.cancelled
    - appointment.no_show
    - lead.abandoned
    - treatment_plan.unscheduled
    - recall.due
  → Implement opportunity creation
  → Implement opportunity deduplication
  → Test event handling

Day 3: Eligibility Evaluation
  → Integrate policy engine
  → Implement opportunity filtering
  → Create opportunity scoring (rules-based)
  → Implement opportunity queue
  → Test eligibility logic

Day 4: Message Templates
  → Create template data model
  → Create template CRUD API
  → Implement template rendering
  → Create templates for each recapture type
  → Test template rendering

Day 5: Campaign Engine (Simple)
  → Create campaign data model
  → Implement campaign execution
  → Implement attempt tracking
  → Create campaign scheduling
  → Test campaign execution
```

### Phase 1 Milestone
```
Delivery:
  ✓ Working API with authentication
  ✓ Database with RLS
  ✓ Event infrastructure
  ✓ Policy engine (consent, opt-out, safety)
  ✓ Opportunity detection (rules-based)
  ✓ Message sending (SMS)
  ✓ Staff dashboard (basic)
  ✓ Audit logging
  ✓ Tests (>80% coverage)

Exit Criteria:
  ✓ All Phase 1 tests pass
  ✓ Can create patient and send message
  ✓ RLS prevents cross-tenant access
  ✓ Safety triggers work
  ✓ Consent enforced
  ✓ No security vulnerabilities
```

---

## PHASE 2: AI Integration (Weeks 5-12)

### Week 5-6: LLM Integration

```
Day 1-2: LLM Service Setup
  → Create LLM client wrapper
  → Implement rate limiting
  → Implement retry logic
  → Create request/response logging
  → Implement token counting
  → Add cost tracking

Day 3-4: Intent Classification
  → Define intent taxonomy
  → Create intent classification prompt
  → Implement intent classifier
  → Add safety classification
  → Create evaluation dataset
  → Test classification accuracy

Day 5: Safety Classifier
  → Create safety classification prompt
  → Implement safety classifier
  → Test emergency detection
  → Test medical advice detection
  → Optimize false positive/negative rate
```

### Week 7-8: Message Generation

```
Day 1-2: Message Generator
  → Create message generation prompt
  → Implement structured output (JSON)
  → Add context assembly
  → Implement patient info injection
  → Create template fallback
  → Test message generation

Day 3: Output Validation
  → Create validation rules
  → Implement hallucination checks
  → Implement claim verification
  → Create validation pipeline
  → Test validation failures

Day 4: Conversation Agent
  → Create conversation context
  → Implement conversation state
  → Add tool calling
  → Implement handoff detection
  → Test conversation flows

Day 5: Safety Integration
  → Integrate safety checks in conversation
  → Test emergency scenarios
  → Test escalation triggers
  → Test opt-out handling
```

### Week 9-10: Tool Calling

```
Day 1-2: Tool Implementation
  → Implement get_patient_info tool
  → Implement get_clinic_info tool
  → Implement check_availability tool
  → Implement hold_slot tool
  → Implement book_appointment tool
  → Implement create_staff_task tool
  → Add tool allowlist
  → Add tool validation

Day 3-4: Tool Gateway
  → Create tool routing
  → Implement tool logging
  → Add tenant scoping
  → Implement error handling
  → Add retry logic
  → Test tool calls

Day 5: Tool Testing
  → Test all tool scenarios
  → Test error cases
  → Test concurrent calls
  → Test timeout handling
```

### Week 11-12: Human Handoff

```
Day 1-2: Handoff System
  → Create handoff data model
  → Implement handoff creation
  → Create handoff queue
  → Implement staff notifications
  → Create handoff resolution
  → Test handoff flow

Day 3: Staff Dashboard
  → Create conversation inbox
  → Create handoff queue view
  → Implement patient timeline
  → Create message composer
  → Add quick actions
  → Test dashboard functionality

Day 4-5: Integration Testing
  → End-to-end conversation tests
  → End-to-end recapture tests
  → Integration tests with mock PMS
  → Load testing
  → Security testing
```

### Phase 2 Milestone
```
Delivery:
  ✓ AI intent classification
  ✓ AI safety classification
  ✓ AI message generation
  ✓ AI conversation handling
  ✓ Tool calling with external systems
  ✓ Human handoff system
  ✓ Staff dashboard
  ✓ Evaluation suite (100+ test cases)

Exit Criteria:
  ✓ Safety test suite passes
  ✓ No hallucination in tested scenarios
  ✓ Handoff works correctly
  ✓ Staff can resolve handoffs
  ✓ Evaluation suite automated
  ✓ All Phase 1 tests still pass
```

---

## PHASE 3: ML & Optimization (Weeks 13-20)

### Week 13-16: ML Pipeline

```
Day 1-2: Feature Engineering
  → Define feature schema
  → Implement feature extraction
  → Create feature store
  → Implement feature versioning
  → Test feature pipeline

Day 3-5: Model Training
  → Prepare training dataset
  → Train conversion probability model
  → Train priority scoring model
  → Train optimal timing model
  → Evaluate models
  → Create model registry

Week 14-15: Model Evaluation
  → Create evaluation dataset
  → Implement offline evaluation
  → Create calibration pipeline
  → Test model fairness
  → Document model performance
  → Create model cards

Week 16: Model Deployment
  → Deploy models to production
  → Implement A/B testing
  → Create shadow mode
  → Monitor model performance
  → Create rollback procedure
```

### Week 17-20: A/B Testing & Analytics

```
Day 1-2: Experimentation Framework
  → Create experiment data model
  → Implement random assignment
  → Create holdout groups
  → Implement metric tracking
  → Test experiment flow

Day 3-4: Analytics Dashboard
  → Create KPI calculations
  → Implement revenue attribution
  → Create cohort analysis
  → Create campaign analytics
  → Create staff dashboard analytics

Day 5: Optimization Loop
  → Implement model retraining pipeline
  → Create label collection interface
  → Implement feedback loop
  → Create model monitoring
  → Test retraining pipeline
```

---

## Week-by-Week Checklist

```
PHASE 1 (Foundation) - 4 weeks:
  □ Repository setup
  □ Database schema + RLS
  □ API foundation (auth, RBAC)
  □ Event infrastructure
  □ Policy engine
  □ Safety foundation
  □ Patient management
  □ Consent management
  □ Opportunity detection
  □ Message templates
  □ Campaign engine (simple)
  □ SMS integration
  □ Basic staff dashboard
  □ Audit logging

PHASE 2 (AI Integration) - 8 weeks:
  □ LLM integration
  □ Intent classification
  □ Safety classification
  □ Message generation
  □ Output validation
  □ Conversation agent
  □ Tool calling
  □ Human handoff
  □ Staff dashboard
  □ Evaluation suite

PHASE 3 (ML & Optimization) - 8 weeks:
  □ Feature engineering
  □ Model training pipeline
  □ Model evaluation
  □ Model deployment
  □ A/B testing
  □ Analytics dashboard
  □ Optimization loop
```

---

## Go-Live Checklist

```
BEFORE FIRST PATIENT CONTACT:

Technical:
  ✓ All tests pass (>90% coverage)
  ✓ Security scan passes (no critical/high)
  ✓ Performance test passes (p95 < 200ms)
  ✓ Load test passes (10K concurrent)
  ✓ Backup/restore tested
  ✓ Monitoring configured
  ✓ Alerts configured
  ✓ Runbooks documented

Safety:
  ✓ Safety test suite passes (100%)
  ✓ Emergency detection tested (real scenarios)
  ✓ Human handoff tested
  ✓ Opt-out tested (all channels)
  ✓ Consent verification tested
  ✓ Frequency caps tested
  ✓ Output validation tested

Compliance:
  ✓ BAA signed with all vendors
  ✓ HIPAA policies documented
  ✓ Audit log retention configured
  ✓ Data retention configured
  ✓ Deletion process tested
  ✓ Consent flow tested
  ✓ Privacy policy published

Clinical:
  ✓ Clinical advisor reviewed
  ✓ Emergency protocol documented
  ✓ Staff trained on dashboard
  ✓ Staff trained on handoff
  ✓ Escalation SLA defined
  ✓ Incident response plan documented

Operational:
  ✓ Pilot clinic selected
  ✓ Pilot data imported
  ✓ Consent data imported
  ✓ Staff accounts created
  ✓ Onboarding completed
  ✓ Support contact established
  ✓ Rollback plan documented
```
