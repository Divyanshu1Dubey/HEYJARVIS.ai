# System Architecture — Complete Technical Architecture

## SA.1 Architecture Overview

```
                        ┌─────────────────────────────────────────────┐
                        │              External Systems                │
                        │  PMS (Open Dental/Eaglesoft/Dentrix)         │
                        │  Insurance Verification APIs                 │
                        │  SMS Provider (Twilio)                       │
                        │  Email Provider (Postmark)                   │
                        │  LLM Provider (Anthropic/OpenAI)             │
                        └──────────────────┬──────────────────────────┘
                                           │
                        ┌──────────────────▼──────────────────────────┐
                        │           API Gateway / Load Balancer        │
                        └──────────────────┬──────────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
    ┌─────────▼──────────┐    ┌───────────▼──────────┐    ┌─────────▼──────────┐
    │   Web Dashboard    │    │     REST API          │    │   WebSocket API    │
    │   (Next.js)        │    │   (FastAPI)           │    │   (Real-time)      │
    └─────────┬──────────┘    └───────────┬──────────┘    └────────────────────┘
              │                            │
              │          ┌─────────────────▼─────────────────┐
              │          │         Service Layer              │
              │          │                                     │
              │          │  ┌──────────┐  ┌──────────────┐   │
              │          │  │ Auth /   │  │  Policy /    │   │
              │          │  │ Tenant   │  │  Eligibility │   │
              │          │  │ Middleware│  │  Engine      │   │
              │          │  └────┬─────┘  └──────┬───────┘   │
              │          │       │               │            │
              │          │  ┌────▼─────┐  ┌─────▼────────┐  │
              │          │  │Conversation│ │  Campaign    │  │
              │          │  │  Service  │ │  Engine      │  │
              │          │  └────┬─────┘  └─────┬────────┘  │
              │          │       │               │            │
              │          │  ┌────▼─────┐  ┌─────▼────────┐  │
              │          │  │  AI /    │  │  Message     │  │
              │          │  │  Agent   │  │  Service     │  │
              │          │  │  Layer   │  │              │  │
              │          │  └────┬─────┘  └─────┬────────┘  │
              │          │       │               │            │
              │          │  ┌────▼─────┐  ┌─────▼────────┐  │
              │          │  │Integration│ │  Analytics   │  │
              │          │  │  Layer   │  │  Service     │  │
              │          │  └──────────┘  └──────────────┘  │
              │          └─────────────────┬─────────────────┘
              │                            │
              │    ┌───────────────────────▼───────────────────────┐
              │    │              Message Queue (Redis/Celery)       │
              │    │                                               │
              │    │  ┌─────────────┐  ┌───────────────────────┐  │
              │    │  │  Campaign   │  │  AI Inference Worker   │  │
              │    │  │  Workers    │  │                       │  │
              │    │  └─────────────┘  └───────────────────────┘  │
              │    │                                               │
              │    │  ┌─────────────┐  ┌───────────────────────┐  │
              │    │  │   Message   │  │  Integration Workers  │  │
              │    │  │  Workers    │  │                       │  │
              │    │  └─────────────┘  └───────────────────────┘  │
              │    └───────────────────────┬───────────────────────┘
              │                            │
              │          ┌─────────────────▼─────────────────┐
              │          │         Data Layer                 │
              │          │                                     │
              │          │  ┌─────────────┐  ┌─────────────┐ │
              │          │  │ PostgreSQL  │  │   Redis     │ │
              │          │  │  (Primary)  │  │  (Cache)    │ │
              │          │  └──────┬──────┘  └─────────────┘ │
              │          │         │                          │
              │          │  ┌──────▼──────┐  ┌─────────────┐ │
              │          │  │  RDS        │  │  S3/Obj     │ │
              │          │  │  Replica    │  │  Storage    │ │
              │          │  └─────────────┘  └─────────────┘ │
              │          └───────────────────────────────────┘
              │
    ┌─────────▼──────────────────────────────────────────────────┐
    │                    Observability Layer                      │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐ │
    │  │  Logs    │ │ Metrics  │ │ Traces   │ │   Alerting    │ │
    │  │(OpenSearch│ │(Prometheus│ │(Jaeger)  │ │  (PagerDuty)  │ │
    │  └──────────┘ └──────────┘ └──────────┘ └───────────────┘ │
    └────────────────────────────────────────────────────────────┘
```

## SA.2 Service Boundaries

### API Service
- HTTP REST API
- WebSocket for real-time conversation
- Request authentication and tenant resolution
- Input validation
- Rate limiting
- Response serialization

### AI Agent Layer
- Conversation orchestration
- LLM interaction
- Tool calling
- Context management
- Response generation
- NOT: database writes (delegated to services)

### Policy Engine
- Eligibility determination
- Consent verification
- Frequency cap enforcement
- Quiet hours enforcement
- Suppression rules
- Business rules
- NOT: message content generation

### Campaign Engine
- Opportunity eligibility triggering
- Sequence execution
- Wait time management
- Stop condition evaluation
- Retry logic

### Message Service
- Template rendering
- Channel routing
- Provider interaction
- Delivery tracking
- Opt-out processing

### Integration Layer
- PMS adapter
- Insurance adapter
- SMS adapter
- Email adapter
- Webhook processing
- Retry and error handling

### Analytics Service
- Metric computation
- Report generation
- Cohort analysis
- Attribution

### Worker Service
- Background job processing
- Campaign execution
- Batch processing
- Scheduled tasks
- AI inference

## SA.3 Data Flow: Patient Outreach

```
1. EVENT TRIGGERED
   └─→ e.g., appointment.cancelled

2. OPPORTUNITY CREATED
   └─→ RecaptureOpportunity record created
   └─→ recapture.opportunity_created event emitted

3. ELIGIBILITY CHECK
   └─→ PolicyEngine.evaluate(opportunity)
   ├─→ Check consent
   ├─→ Check opt-out
   ├─→ Check frequency caps
   ├─→ Check quiet hours
   ├─→ Check suppression
   └─→ Result: ELIGIBLE or SUPPRESSED

4. IF ELIGIBLE → CAMPAIGN MATCH
   └─→ Find matching campaign for event type
   └─→ Queue first step

5. CAMPAIGN EXECUTION
   └─→ Wait for scheduled time
   └─→ Render message template with patient data
   └─→ Route to appropriate channel
   └─→ Send message

6. MESSAGE SENT
   └─→ Track delivery status
   └─→ Wait for response (timeout based on campaign config)

7a. PATIENT RESPONDS → AI CONVERSATION
    └─→ Intent classification
    └─→ Safety classification
    ├─→ Safety concern → HANDOFF
    ├─→ Booking intent → Check availability → Book
    ├─→ Question → Answer or handoff
    └─→ Decline → Record, end campaign

7b. NO RESPONSE → NEXT STEP
    └─→ Wait for next delay
    └─→ Send next message
    └─→ Repeat until exhausted

8. CAMPAIGN COMPLETE
    └─→ Record outcome
    └─→ Update opportunity state
    └─→ Emit analytics event
```

## SA.4 AI Agent Architecture

```
                    ┌─────────────────────────────┐
                    │     Patient Message          │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  Conversation Context Loader │
                    │  - Patient history          │
                    │  - Clinic context           │
                    │  - Conversation memory      │
                    │  - RAG retrieval            │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Safety Classification    │
                    │    (DETERMINISTIC FIRST)    │
                    │                             │
                    │  Check for:                 │
                    │  - Emergency symptoms       │
                    │  - Medical questions        │
                    │  - Abuse/threats            │
                    │  - Illegal requests         │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     Intent Classification   │
                    │     (LLM-assisted)          │
                    │                             │
                    │  BOOK_APPOINTMENT           │
                    │  RESCHEDULE                 │
                    │  CANCEL                     │
                    │  INSURANCE_QUESTION         │
                    │  PRICING_QUESTION           │
                    │  SERVICE_QUESTION           │
                    │  HUMAN_HANDOFF              │
                    │  UNKNOWN                    │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Policy Check             │
                    │    (DETERMINISTIC)          │
                    │                             │
                    │  - Is this action allowed?  │
                    │  - Is patient eligible?     │
                    │  - Are we within hours?     │
                    │  - Frequency cap OK?        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Tool Selection & Call    │
                    │                             │
                    │  check_availability()       │
                    │  book_appointment()         │
                    │  check_insurance()          │
                    │  get_clinic_info()          │
                    │  handoff_to_human()         │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Response Generation      │
                    │    (LLM with constraints)   │
                    │                             │
                    │  - Only use verified data   │
                    │  - Never fabricate          │
                    │  - Include opt-out          │
                    │  - Appropriate tone         │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Response Validation      │
                    │    (DETERMINISTIC)          │
                    │                             │
                    │  - No unsupported claims    │
                    │  - No medical advice        │
                    │  - No fake appointments     │
                    │  - No fake insurance info   │
                    │  - Policy compliance        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     Send Response           │
                    │     & Log Everything        │
                    └─────────────────────────────┘
```

## SA.5 Key Design Decisions

### Why API + Workers, not monolith?
- Different scaling profiles (API: request-driven, Workers: batch/scheduled)
- Failure isolation (worker crash doesn't affect API)
- Independent deployment
- Different resource needs (workers need more CPU for AI, API needs more memory for connections)

### Why event-driven?
- Decouples components
- Natural audit trail
- Enables async processing
- Supports replay and debugging
- Natural fit for healthcare (every action logged)

### Why rules before AI?
- Deterministic compliance
- Auditable decisions
- Faster for common cases
- Reduces LLM dependency and cost
- Safety-critical rules must never depend on AI

### Why tool calling instead of function calling?
- Same concept, "tools" is clearer mental model
- Each tool has explicit schema, validation, and authorization
- Tools are the only way AI affects the real world
- Tools are logged and auditable

### Why PostgreSQL vs NoSQL?
- ACID for booking (can't double-book)
- Complex queries for analytics
- JSONB for flexible data
- Strong consistency for critical operations
- Row-level security for multi-tenancy
