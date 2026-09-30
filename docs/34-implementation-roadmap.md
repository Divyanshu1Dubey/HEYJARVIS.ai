# Implementation Roadmap — Exact Build Sequence

## IR.1 Pre-Development (Weeks 1-4)

**Goal:** Complete architecture, set up infrastructure, and begin development environment.

### Week 1-2: Architecture Finalization
```
Day 1-2:
→ Finalize database schema
→ Review with team
→ Get sign-off

Day 3-4:
→ Design API specification
→ Design state machine
→ Create ADRs

Day 5-10:
→ Design AI architecture
→ Design integration architecture
→ Document security requirements
→ Document compliance requirements
```

### Week 3-4: Infrastructure Setup
```
Day 1-3:
→ Set up cloud accounts (AWS/GCP)
→ Set up VPC and networking
→ Set up Kubernetes cluster (staging)
→ Set up PostgreSQL (staging)
→ Set up Redis (staging)

Day 4-7:
→ Set up CI/CD (GitHub Actions)
→ Set up monitoring (Datadog)
→ Set up logging (CloudWatch/Loki)
→ Set up secrets management (Vault)

Day 8-10:
→ Set up development environment
→ Create Docker Compose for local dev
→ Document development setup
→ Team onboarding
```

---

## IR.2 Phase 1: Rules-First MVP (Weeks 5-12)

### Week 5-6: Core Backend
```
Day 1-3:
→ Set up FastAPI project structure
→ Implement authentication (JWT)
→ Implement tenant isolation (RLS)
→ Create user/clinic management

Day 4-7:
→ Create database models
→ Create database migrations
→ Implement patient CRUD
→ Implement consent management

Day 8-10:
→ Implement communication preferences
→ Create suppression lists
→ Implement opt-out handling
→ Write tests
```

### Week 7-8: Event System + Queue
```
Day 1-3:
→ Set up Redis Streams
→ Create event definitions
→ Implement event producers
→ Implement event consumers

Day 4-7:
→ Create job scheduling system
→ Implement retry logic
→ Implement dead-letter queue
→ Create webhook handlers

Day 8-10:
→ Test event flow end-to-end
→ Test idempotency
→ Test retry behavior
```

### Week 9-10: Campaign Engine
```
Day 1-3:
→ Design campaign configuration schema
→ Implement campaign CRUD
→ Implement campaign execution engine
→ Implement frequency caps

Day 4-7:
→ Implement message template system
→ Create initial templates (5-10)
→ Implement stop conditions
→ Implement state transitions

Day 8-10:
→ Test campaign execution
→ Test stop conditions
→ Test frequency caps
→ Create campaign builder API
```

### Week 11-12: Staff Dashboard + Testing
```
Day 1-3:
→ Create staff dashboard (basic)
→ Create opportunities queue
→ Create handoff queue
→ Create basic analytics

Day 4-7:
→ Integration testing
→ E2E testing
→ Safety testing
→ Staff training

Day 8-10:
→ Deploy to staging
→ Pilot with 1 clinic
→ Gather feedback
→ Fix bugs
```

---

## IR.3 Phase 2: AI Personalization (Weeks 13-20)

### Week 13-14: AI Infrastructure
```
Day 1-3:
→ Set up LLM client
→ Create prompt management system
→ Create output validation layer
→ Implement safety classifier

Day 4-7:
→ Create tool framework
→ Implement tool allowlists
→ Create tool execution layer
→ Implement tenant-scoped retrieval

Day 8-10:
→ Create RAG system
→ Index clinic data
→ Test retrieval quality
→ Implement context management
```

### Week 15-16: Conversation AI
```
Day 1-3:
→ Write conversation agent prompt
→ Implement intent classifier
→ Implement conversation memory
→ Test basic conversations

Day 4-7:
→ Implement tool calling
→ Test availability lookup
→ Test booking flow
→ Test insurance lookup

Day 8-10:
→ Implement human handoff
→ Test safety escalation
→ Test edge cases
→ Run safety evaluation
```

### Week 17-18: Message Generation
```
Day 1-3:
→ Write message generator prompt
→ Implement template system
→ Test message generation
→ Test personalization

Day 4-7:
→ Implement output validation
→ Test for hallucinations
→ Test for policy compliance
→ Test for opt-out inclusion

Day 8-10:
→ Run AI evaluation suite
→ Fix hallucinations
→ Optimize prompts
→ Staff review of generated messages
```

### Week 19-20: Integration + Rollout
```
Day 1-3:
→ Deploy AI features to staging
→ Shadow testing (AI runs but doesn't affect patients)
→ Review AI decisions

Day 4-7:
→ Canary deployment (10%)
→ Monitor closely
→ Expand to 50%
→ Full rollout

Day 8-10:
→ Staff training on AI features
→ Monitor AI performance
→ Gather feedback
→ Fix issues
```

---

## IR.4 Phase 3: ML Prediction (Weeks 21-28)

### Week 21-22: Data + Features
```
Day 1-3:
→ Set up feature store
→ Define feature schemas
→ Implement feature extraction
→ Create training data pipeline

Day 4-7:
→ Collect historical data
→ Clean and validate data
→ Create train/val/test splits
→ Prevent data leakage

Day 8-10:
→ Train baseline model (logistic regression)
→ Evaluate baseline
→ Set baseline metrics
```

### Week 23-24: Model Development
```
Day 1-3:
→ Train gradient boosting model
→ Tune hyperparameters
→ Compare to baseline

Day 4-7:
→ Calibrate probabilities
→ Evaluate on test set
→ Analyze feature importance
→ Run adversarial evaluation

Day 8-10:
→ Create model registry
→ Version model
→ Document model
```

### Week 25-26: Model Integration
```
Day 1-3:
→ Integrate model into scoring pipeline
→ Implement shadow scoring
→ Test predictions against rules

Day 4-7:
→ A/B test (10% ML-driven)
→ Compare to rules baseline
→ Monitor metrics

Day 8-10:
→ Expand A/B test
→ Analyze results
→ Decide on rollout
```

### Week 27-28: Monitoring + Rollout
```
Day 1-3:
→ Implement model monitoring
→ Set up drift detection
→ Create alerting

Day 4-7:
→ Full rollout (if A/B positive)
→ Monitor closely
→ Collect feedback

Day 8-10:
→ Document results
→ Plan next iteration
```

---

## IR.5 Phase 4-7: (Weeks 29-52)

Following the same pattern:
1. Design (1 week)
2. Develop (2 weeks)
3. Test (1 week)
4. Deploy (1 week)

---

## IR.6 Critical Path

```
Week 1-4:  Architecture + Infrastructure
     ↓
Week 5-8:  Database + Events + Campaign Engine
     ↓
Week 9-12: Dashboard + Phase 1 Launch
     ↓
Week 13-16: AI Infrastructure + Conversation AI
     ↓
Week 17-20: Message Generation + Phase 2 Launch
     ↓
Week 21-24: Data + Model Development
     ↓
Week 25-28: Model Integration + Phase 3 Launch
     ↓
Week 29-52: Phases 4-7
```

## IR.7 Key Milestones

| Week | Milestone | Criteria |
|------|-----------|----------|
| Week 4 | Architecture Complete | All docs signed off |
| Week 8 | Backend Ready | API functional, DB working |
| Week 12 | Phase 1 Live | 3 clinics using rules-first |
| Week 16 | AI Ready | AI evaluation passes |
| Week 20 | Phase 2 Live | AI-powered conversations |
| Week 24 | Model Ready | ML model trained and evaluated |
| Week 28 | Phase 3 Live | ML predictions in production |
| Week 36 | Multi-Channel | Email + Voice working |
| Week 44 | Real Integrations | PMS connected |
| Week 52 | Full System | All features live |

## IR.8 Resource Requirements

### Phase 1-2 (Weeks 5-20)
- 3 Backend Engineers
- 1 Frontend Engineer
- 1 AI/ML Engineer (starting Week 13)
- 1 Product Manager
- 0.5 Clinical Advisor
- 1 QA Engineer (starting Week 10)

### Phase 3-4 (Weeks 21-36)
- 3 Backend Engineers
- 1 Frontend Engineer
- 1 AI/ML Engineer
- 1 Product Manager
- 0.5 Clinical Advisor
- 1 QA Engineer
- 1 Integration Specialist (starting Week 35)

### Phase 5-7 (Weeks 37-52)
- 3 Backend Engineers
- 1 Frontend Engineer
- 1 AI/ML Engineer
- 1 Product Manager
- 0.5 Clinical Advisor
- 1 QA Engineer
- 1 Integration Specialist
- 1 Data Analyst (starting Week 43)
