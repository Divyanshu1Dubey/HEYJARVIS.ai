# Diagrams — Visual Architecture Reference

This directory contains architecture diagrams in Mermaid format.
Render with any Mermaid-compatible viewer (GitHub, VS Code Mermaid plugin, Mermaid Live Editor).

---

## 1. System Overview

```mermaid
graph TB
    subgraph "External Systems"
        PATIENT[Patient / Lead]
        PMS[Practice Management System]
        INS[Insurance Provider]
        SMS[SMS Provider]
        EMAIL[Email Provider]
    end

    subgraph "HeyJarvis Platform"
        API[API Gateway]
        WEB[Web Dashboard]
        AGENT[AI Agent Layer]
        ENGINE[Recapture Engine]
        POLICY[Policy Engine]
        CAMP[Campaign Engine]
        MSG[Message Service]
        WORKER[Worker Queue]

        subgraph "Data Layer"
            DB[(PostgreSQL)]
            REDIS[(Redis)]
            S3[(S3 Storage)]
        end

        subgraph "AI Layer"
            LLM[LLM Provider]
            CLASSIFIER[Safety/Intent Classifier]
            VALIDATOR[Response Validator]
        end
    end

    PATIENT -->|"SMS/Web/Chat"| API
    API --> AGENT
    AGENT --> ENGINE
    ENGINE --> POLICY
    POLICY -->|"Approve/Reject"| CAMP
    CAMP --> MSG
    MSG --> SMS
    MSG --> EMAIL
    AGENT --> LLM
    AGENT --> CLASSIFIER
    AGENT --> VALIDATOR

    ENGINE <-->|"Check availability"| PMS
    ENGINE <-->|"Verify insurance"| INS

    WEB --> API
    API --> DB
    WORKER --> DB
    WORKER --> REDIS
    ENGINE --> S3
```

---

## 2. Patient State Machine

```mermaid
stateDiagram-v2
    [*] --> NEW_LEAD

    NEW_LEAD --> CONTACTED: Outreach sent
    NEW_LEAD --> OPTED_OUT: Patient opts out
    NEW_LEAD --> SUPPRESSED: Business rule suppresses
    NEW_LEAD --> INVALID_CONTACT: Wrong number/email

    CONTACTED --> ENGAGED: Patient responds
    CONTACTED --> NO_RESPONSE: No reply after attempts
    CONTACTED --> SAFETY_ESCALATION: Safety keywords detected

    ENGAGED --> QUALIFIED: Intent understood
    ENGAGED --> HUMAN_HANDOFF: Patient requests human
    ENGAGED --> SAFETY_ESCALATION: Safety concern

    QUALIFIED --> BOOKING_PENDING: Offer appointment
    QUALIFIED --> DECLINED: Patient says no
    QUALIFIED --> HUMAN_HANDOFF: Complex question

    BOOKING_PENDING --> BOOKED: Patient confirms
    BOOKING_PENDING --> BOOKING_ABANDONED: No response
    BOOKING_PENDING --> DECLINED: Patient declines

    BOOKED --> CONFIRMED: Confirmation sent
    BOOKED --> CANCELLED: Patient cancels
    BOOKED --> NO_SHOW: Patient doesn't show

    CONFIRMED --> COMPLETED: Visit happens
    CONFIRMED --> CANCELLED: Patient cancels
    CONFIRMED --> NO_SHOW: Patient doesn't show

    CANCELLED --> RESCHEDULE_PENDING: Reschedule initiated
    CANCELLED --> INACTIVE: No reschedule attempt
    CANCELLED --> RECAPTURE_FAILED: Outreach fails

    NO_SHOW --> RESCHEDULE_PENDING: Reschedule offered
    NO_SHOW --> INACTIVE: No action
    NO_SHOW --> RECAPTURE_FAILED: Outreach fails

    RESCHEDULE_PENDING --> BOOKED: Rescheduled
    RESCHEDULE_PENDING --> INACTIVE: No response

    DECLINED --> INACTIVE: Record for future

    NO_RESPONSE --> INACTIVE: All attempts exhausted
    NO_RESPONSE --> RECAPTURE_ATTEMPT: Retry later

    INACTIVE --> RECALL_DUE: Time passes
    INACTIVE --> RECAPTURE_ATTEMPT: Reactivation campaign

    RECALL_DUE --> CONTACTED: Outreach initiated

    SAFETY_ESCALATION --> HANDLED: Staff resolves
    HUMAN_HANDOFF --> HANDLED: Staff resolves
    HUMAN_HANDOFF --> CONTACTED: Returns to AI

    RECAPTURE_FAILED --> [*]
    COMPLETED --> [*]
    HANDLED --> [*]
    INVALID_CONTACT --> [*]
    OPTED_OUT --> [*]
    SUPPRESSED --> [*]
```

---

## 3. Event Flow Architecture

```mermaid
sequenceDiagram
    participant P as Patient
    participant API as API Gateway
    participant AGENT as AI Agent
    participant POLICY as Policy Engine
    participant CAMP as Campaign Engine
    participant MSG as Message Service
    participant SMS as SMS Provider
    participant PMS as Practice System
    participant DB as Database

    P->>API: Patient message
    API->>AGENT: Route conversation
    AGENT->>DB: Load patient context
    AGENT->>POLICY: Check eligibility

    alt Not eligible
        POLICY-->>AGENT: Suppress
        AGENT->>DB: Log suppression
    else Eligible
        AGENT->>AGENT: Classify intent
        AGENT->>AGENT: Classify safety

        alt Safety concern
            AGENT->>DB: Create handoff
            AGENT->>MSG: Send safety message
            AGENT->>P: Emergency guidance
        else Normal
            AGENT->>PMS: Check availability
            PMS-->>AGENT: Available slots
            AGENT->>P: Offer appointment

            alt Patient confirms
                P->>AGENT: Yes, book it
                AGENT->>PMS: Book appointment
                PMS-->>AGENT: Booking confirmed
                AGENT->>MSG: Send confirmation
                MSG->>SMS: Deliver SMS
                AGENT->>DB: Update state → BOOKED
            else Patient declines
                AGENT->>DB: Update state → DECLINED
            end
        end
    end

    AGENT->>DB: Log all events
    AGENT->>DB: Create audit record
```

---

## 4. Database ERD

```mermaid
erDiagram
    ORGANIZATION ||--o{ CLINIC : has
    CLINIC ||--o{ LOCATION : has
    CLINIC ||--o{ PROVIDER : employs
    CLINIC ||--o{ SERVICE : offers
    CLINIC ||--o{ PATIENT : serves
    CLINIC ||--o{ USER : has

    PATIENT ||--o{ PATIENT_CONTACT : has
    PATIENT ||--o{ CONSENT : gives
    PATIENT ||--o{ COMMUNICATION_PREFERENCE : has
    PATIENT ||--o{ CONVERSATION : participates
    PATIENT ||--o{ APPOINTMENT : has
    PATIENT ||--o{ TREATMENT_PLAN : receives
    PATIENT ||--o{ RECAPTURE_OPPORTUNITY : generates

    CONVERSATION ||--o{ MESSAGE : contains
    CONVERSATION ||--o{ CONVERSATION_EVENT : tracks
    CONVERSATION ||--o{ HUMAN_HANDOFF : may_create

    APPOINTMENT ||--o{ APPOINTMENT_HISTORY : has
    APPOINTMENT ||--o{ APPOINTMENT_HOLD : may_have

    TREATMENT_PLAN ||--o{ TREATMENT_PLAN_ITEM : contains

    RECAPTURE_OPPORTUNITY ||--o{ RECAPTURE_ATTEMPT : has
    RECAPTURE_ATTEMPT ||--o{ CHANNEL_DELIVERY : has

    CAMPAIGN ||--o{ RECAPTURE_OPPORTUNITY : generates

    USER ||--o{ ROLE : has
    ROLE ||--o{ PERMISSION : grants

    AI_DECISION ||--o{ AI_ACTION : results_in
    AI_DECISION ||--o{ MODEL_PREDICTION : uses
```

---

## 5. AI Decision Flow

```mermaid
flowchart TD
    START[Patient Message Received] --> LOAD[Load Patient Context]
    LOAD --> CHECK_CONSENT{Consent OK?}

    CHECK_CONSENT -->|No| SUPPRESS[Suppress & Log]
    CHECK_CONSENT -->|Yes| CHECK_OPT_OUT{Opted Out?}

    CHECK_OPT_OUT -->|Yes| SUPPRESS
    CHECK_OPT_OUT -->|No| CHECK_FREQ{Frequency Cap?}

    CHECK_FREQ -->|Exceeded| SUPPRESS
    CHECK_FREQ -->|OK| SAFETY[Safety Classification]

    SAFETY --> SAFE{Is it safe?}
    SAFE -->|No| ESCALATE[Emergency Escalation → Staff]
    SAFE -->|Yes| INTENT[Intent Classification]

    INTENT --> INTENT_TYPE{What intent?}

    INTENT_TYPE -->|BOOKING| CHECK_AVAIL[Check Availability]
    INTENT_TYPE -->|INSURANCE| CHECK_INS[Check Insurance Status]
    INTENT_TYPE -->|CANCEL| HANDLE_CANCEL[Handle Cancellation]
    INTENT_TYPE -->|QUESTION| ANSWER[Answer from RAG]
    INTENT_TYPE -->|HUMAN| HANDOFF[Create Handoff]
    INTENT_TYPE -->|UNKNOWN| CLARIFY[Ask for Clarification]

    CHECK_AVAIL --> OFFER[Offer Appointment]
    CHECK_INS --> EXPLAIN[Explain Coverage]
    HANDLE_CANCEL --> RESCHED[Offer Reschedule]
    ANSWER --> RESPOND[Send Response]
    CLARIFY --> RESPOND

    OFFER --> VALIDATE[Validate Response]
    EXPLAIN --> VALIDATE
    RESCHED --> VALIDATE
    RESPOND --> VALIDATE

    VALIDATE --> VALID{Valid?}
    VALID -->|No| FIX[Fix or Escalate]
    VALID -->|Yes| SEND[Send to Patient]

    HANDOFF --> NOTIFY[Notify Staff]
    ESCALATE --> NOTIFY
    FIX --> NOTIFY

    SEND --> LOG[Log & Track]
    NOTIFY --> LOG

    SUPPRESS --> LOG
    LOG --> END[End]
```

---

## 6. Deployment Architecture

```mermaid
graph TB
    subgraph "AWS Cloud"
        subgraph "VPC"
            CF[CloudFront CDN]

            subgraph "Public Subnet"
                ALB[Application Load Balancer]
            end

            subgraph "Private Subnet"
                subgraph "ECS Cluster"
                    API1[API Server 1]
                    API2[API Server 2]
                    W1[Worker 1]
                    W2[Worker 2]
                    W3[Worker 3]
                end

                subgraph "Data"
                    RDS_PRIMARY[(RDS Primary)]
                    RDS_REPLICA[(RDS Replica)]
                    REDIS[(ElastiCache Redis)]
                end
            end
        end

        subgraph "Storage"
            S3_LOGS[S3 - Logs]
            S3_FILES[S3 - Files]
        end

        subgraph "Monitoring"
            CW[CloudWatch]
            JAEGER[Jaeger Tracing]
        end
    end

    CF --> ALB
    ALB --> API1
    ALB --> API2
    API1 --> RDS_PRIMARY
    API2 --> RDS_PRIMARY
    RDS_PRIMARY --> RDS_REPLICA
    API1 --> REDIS
    W1 --> RDS_PRIMARY
    W2 --> REDIS
    W3 --> REDIS
    API1 --> CW
    API1 --> JAEGER
```

---

## 7. Message Campaign Flow

```mermaid
flowchart LR
    TRIGGER[Event Trigger] --> ELIGIBLE{Eligible?}

    ELIGIBLE -->|No| STOP1[Stop]
    ELIGIBLE -->|Yes| QUEUE[Add to Campaign Queue]

    QUEUE --> WAIT1[Wait - Delay 1]
    WAIT1 --> SEND1[Send Message 1]
    SEND1 --> CHECK1{Check Response}

    CHECK1 -->|Positive| BOOK[Attempt Booking]
    CHECK1 -->|Negative| RECORD1[Record Decline]
    CHECK1 -->|No Response| WAIT2[Wait - Delay 2]

    WAIT2 --> SEND2[Send Message 2]
    SEND2 --> CHECK2{Check Response}

    CHECK2 -->|Positive| BOOK
    CHECK2 -->|Negative| RECORD2[Record Decline]
    CHECK2 -->|No Response| WAIT3[Wait - Delay 3]

    WAIT3 --> SEND3[Final Message]
    SEND3 --> CHECK3{Check Response}

    CHECK3 -->|Positive| BOOK
    CHECK3 -->|Negative| RECORD3[Record Decline]
    CHECK3 -->|No Response| END[End Campaign]

    BOOK --> SUCCESS[Booked ✓]
    BOOK --> FAIL[Booking Failed]

    RECORD1 --> END
    RECORD2 --> END
    RECORD3 --> END
    SUCCESS --> END
    FAIL --> END
    STOP1 --> END
```

---

## 8. Data Flow for Booking

```mermaid
sequenceDiagram
    participant AI as AI Agent
    participant TOOLS as Tool Gateway
    participant VALIDATOR as Validator
    participant HOLD as Hold System
    participant PMS as Practice System
    participant DB as Database
    participant PATIENT as Patient

    AI->>PATIENT: "I can see you today at 3:20 PM. Want me to book?"
    PATIENT->>AI: "Yes!"

    AI->>TOOLS: hold_appointment_slot(clinic, datetime, duration)
    TOOLS->>HOLD: Create hold
    HOLD->>DB: INSERT hold (expires 5 min)
    HOLD-->>TOOLS: Hold created
    TOOLS-->>AI: Hold ID: abc123

    AI->>PMS: book_appointment(hold_id, patient_id)
    PMS->>PMS: Verify slot available
    PMS->>PMS: Create appointment
    PMS-->>AI: Appointment ID: 456789

    AI->>VALIDATOR: Verify booking succeeded
    VALIDATOR->>DB: Check appointment exists
    DB-->>VALIDATOR: Confirmed
    VALIDATOR-->>AI: VALID

    AI->>PATIENT: "You're booked for today at 3:20 PM with Dr. Smith"
    AI->>DB: Log booking event

    Note over AI,PATIENT: Booking ONLY confirmed after PMS confirms
```

---

## 9. Multi-Tenant Data Isolation

```mermaid
graph TB
    subgraph "Application Layer"
        APP[API / Worker]
        MW[Tenant Middleware]
    end

    subgraph "Database Layer"
        RLS[Row-Level Security]
        QUERY1[Query with tenant_id]
        QUERY2[Query without tenant_id]
        BLOCK[🔴 BLOCKED]
    end

    APP --> MW
    MW -->|"SET tenant_id = 'clinic_123'"| RLS

    RLS -->|"WHERE tenant_id = 'clinic_123'"| QUERY1
    RLS -->|"Missing tenant_id"| BLOCK
    RLS -->|"WHERE tenant_id = 'clinic_456' (wrong)"| BLOCK

    style BLOCK fill:#ff6b6b
    style QUERY1 fill:#51cf66
```

---

## 10. Observability Data Flow

```mermaid
graph TB
    subgraph "Application"
        APP[API / Worker]
        LOGS[App Logs]
        METRICS[Metrics]
        TRACES[Distributed Traces]
    end

    subgraph "Collection"
        OTEL[OpenTelemetry Collector]
        CW_AGENT[CloudWatch Agent]
    end

    subgraph "Storage"
        ES[OpenSearch - Logs]
        CW_METRICS[CloudWatch Metrics]
        JAEGER[Jaeger - Traces]
        S3[S3 - Archives]
    end

    subgraph "Visualization"
        GRAFANA[Grafana]
        CW_DASH[CloudWatch Dashboards]
        ALERTS[Alert Manager]
    end

    APP --> LOGS
    APP --> METRICS
    APP --> TRACES

    LOGS --> OTEL
    METRICS --> OTEL
    TRACES --> OTEL

    OTEL --> ES
    OTEL --> CW_METRICS
    OTEL --> JAEGER

    ES --> GRAFANA
    CW_METRICS --> CW_DASH
    JAEGER --> GRAFANA

    GRAFANA --> ALERTS
    CW_DASH --> ALERTS

    ALERTS --> PAGERDUTY[PagerDuty]
```

---

## 11. Patient Journey Map

```mermaid
journey
    title Patient Recapture Journey
    section Lead
        Patient submits form: 5: Patient
        AI sends welcome: 4: AI
        Patient asks question: 5: Patient
        AI answers: 4: AI
    section Engagement
        AI offers appointment: 4: AI
        Patient interested: 5: Patient
        AI checks availability: 3: AI
        AI offers slot: 4: AI
    section Booking
        Patient confirms: 5: Patient
        AI books: 4: AI
        AI sends confirmation: 5: AI
    section Visit
        Patient arrives: 5: Patient
        Treatment completed: 5: Clinic
    section Failure Paths
        Patient ignores: 2: Patient
        AI retries: 3: AI
        Patient declines: 2: Patient
        AI records decline: 3: AI
        Safety escalation: 1: AI, Staff: 5
```

---

## 12. AI Accuracy Targets

```mermaid
graph LR
    subgraph "Accuracy Targets"
        A1[Intent Classification<br/>Target: >95%]
        A2[Safety Classification<br/>Target: >99%]
        A3[Hallucination Rate<br/>Target: <2%]
        A4[Handoff Accuracy<br/>Target: >90%]
        A5[Response Relevance<br/>Target: >90%]
        A6[Booking Accuracy<br/>Target: 100%]
        A7[Tool Selection<br/>Target: >95%]
    end

    subgraph "Measurement"
        E1[Golden Test Suite]
        E2[Human Review]
        E3[Production Monitoring]
    end

    E1 --> A1
    E1 --> A2
    E1 --> A3
    E2 --> A4
    E2 --> A5
    E3 --> A6
    E3 --> A7
```
