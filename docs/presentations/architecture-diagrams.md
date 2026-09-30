# Architecture Diagrams — Visual System Architecture

## AD.1 High-Level System Architecture

```mermaid
graph TB
    subgraph "Patient Layer"
        P[Patient]
    end

    subgraph "Channel Layer"
        SMS[SMS - Twilio]
        Email[Email - Postmark]
        Web[Web Chat]
        Voice[Voice - Twilio]
        WhatsApp[WhatsApp Business]
    end

    subgraph "API Layer"
        Gateway[API Gateway / Load Balancer]
        Auth[JWT Authentication]
        Rate[Rate Limiter]
    end

    subgraph "Application Layer"
        API[FastAPI REST API]
        Worker[Background Workers]
        Scheduler[Scheduled Jobs]
    end

    subgraph "AI Layer"
        Policy[Policy Engine]
        Intent[Intent Classifier]
        Safety[Safety Classifier]
        Generator[Message Generator]
        Conversation[Conversation Agent]
        ML[ML Scoring Models]
    end

    subgraph "Integration Layer"
        ToolGateway[Tool Gateway]
        SchedAdapter[Scheduling Adapter]
        InsAdapter[Insurance Adapter]
        CommAdapter[Communication Adapter]
    end

    subgraph "External Systems"
        PMS[Practice Management System]
        Insurance[Insurance Provider]
        Calendar[Calendar System]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL)]
        Cache[(Redis)]
        Queue[Message Queue]
        S3[(S3 Storage)]
    end

    subgraph "Observability"
        Metrics[Metrics - Datadog]
        Logs[Logs - Loki]
        Traces[Traces - OpenTelemetry]
        Alerts[Alerting - PagerDuty]
    end

    %% Patient flows
    P --> SMS
    P --> Email
    P --> Web
    P --> Voice
    P --> WhatsApp

    %% Channel to API
    SMS --> Gateway
    Email --> Gateway
    Web --> Gateway
    Voice --> Gateway
    WhatsApp --> Gateway

    %% API processing
    Gateway --> Auth
    Auth --> Rate
    Rate --> API

    %% Async processing
    API --> Queue
    Queue --> Worker
    Scheduler --> Worker

    %% AI processing
    API --> Policy
    Policy --> Intent
    Intent --> Safety
    Safety --> Generator
    Generator --> Conversation
    Conversation --> ML

    %% Tool calls
    Conversation --> ToolGateway
    ToolGateway --> SchedAdapter
    ToolGateway --> InsAdapter
    ToolGateway --> CommAdapter

    %% External integrations
    SchedAdapter --> PMS
    InsAdapter --> Insurance
    CommAdapter --> SMS
    CommAdapter --> Email

    %% Data access
    API --> DB
    Worker --> DB
    Policy --> DB
    ML --> DB
    API --> Cache
    Worker --> Queue
    API --> S3

    %% Observability
    API --> Metrics
    API --> Logs
    API --> Traces
    Metrics --> Alerts
```

## AD.2 Patient Journey State Machine

```mermaid
stateDiagram-v2
    [*] --> NEW_LEAD

    NEW_LEAD --> CONTACTED: outreach_sent
    NEW_LEAD --> LEAD_INVALID: invalid_contact
    NEW_LEAD --> OPTED_OUT: patient_opts_out
    NEW_LEAD --> DO_NOT_CONTACT: staff_suppresses

    CONTACTED --> ENGAGED: patient_responds
    CONTACTED --> NO_RESPONSE: no_response_after_campaign
    CONTACTED --> OPTED_OUT: patient_opts_out

    ENGAGED --> QUALIFIED: intent_confirmed
    ENGAGED --> DISQUALIFIED: not_interested
    ENGAGED --> SAFETY_ESCALATION: emergency_detected
    ENGAGED --> HUMAN_HANDOFF: ai_uncertain
    ENGAGED --> OPTED_OUT: patient_opts_out

    QUALIFIED --> BOOKING_PENDING: availability_offered
    QUALIFIED --> TREATMENT_PENDING: treatment_discussed
    QUALIFIED --> HUMAN_HANDOFF: complex_case
    QUALIFIED --> OPTED_OUT: patient_opts_out

    BOOKING_PENDING --> BOOKED: patient_confirms
    BOOKING_PENDING --> BOOKING_ABANDONED: no_response
    BOOKING_PENDING --> CANCELLED: patient_cancels

    BOOKED --> CONFIRMED: confirmation_sent
    BOOKED --> CANCELLED: patient_cancels
    BOOKED --> NO_SHOW: patient_misses

    CONFIRMED --> COMPLETED: visit_happens
    CONFIRMED --> CANCELLED: patient_cancels
    CONFIRMED --> NO_SHOW: patient_misses

    TREATMENT_PENDING --> TREATMENT_SCHEDULED: appointment_booked
    TREATMENT_PENDING --> TREATMENT_DECLINED: patient_declines
    TREATMENT_PENDING --> TREATMENT_UNSCHEDULED: no_action

    CANCELLED --> RESCHEDULE_PENDING: reschedule_offered
    CANCELLED --> RECAPTURE_FAILED: no_response
    CANCELLED --> OPTED_OUT: patient_opts_out

    NO_SHOW --> RESCHEDULE_PENDING: reschedule_offered
    NO_SHOW --> NO_SHOW_REPEAT: second_no_show
    NO_SHOW --> RECAPTURE_FAILED: no_response

    RESCHEDULE_PENDING --> BOOKED: rescheduled
    RESCHEDULE_PENDING --> RECAPTURE_FAILED: no_response

    TREATMENT_SCHEDULED --> BOOKED: confirmed
    TREATMENT_DECLINED --> ENDED: final
    TREATMENT_UNSCHEDULED --> RECAPTURE: re_engage_later

    RECALL_DUE --> CONTACTED: recall_outreach
    RECALL_DUE --> INACTIVE: no_response

    INACTIVE --> RECAPTURE: re_engagement_campaign
    INACTIVE --> ENDED: final

    BOOKING_ABANDONED --> BOOKING_PENDING: re_engage
    NO_RESPONSE --> RECAPTURE: new_campaign
    RECAPTURE_FAILED --> ENDED: final

    SAFETY_ESCALATION --> HUMAN_HANDOFF: staff_handles
    HUMAN_HANDOFF --> ENGAGED: resolved
    HUMAN_HANDOFF --> ENDED: resolved_no_followup

    OPTED_OUT --> SUPPRESSED: permanent
    DO_NOT_CONTACT --> SUPPRESSED: permanent

    COMPLETED --> RECALL_DUE: recall_due_later
    COMPLETED --> INACTIVE: long_time_no_visit

    ENDED --> [*]
    SUPPRESSED --> [*]
```

## AD.3 Event Flow Architecture

```mermaid
graph LR
    subgraph "Event Producers"
        PMS_EVT[PMS Sync]
        WEB_EVT[Web Form]
        SMS_EVT[SMS Webhook]
        PATIENT_EVT[Patient Message]
        STAFF_EVT[Staff Action]
        SCHED_EVT[Scheduler]
        AI_EVT[AI Engine]
    end

    subgraph "Event Bus"
        Queue[Redis Streams / Kafka]
        DLQ[Dead Letter Queue]
    end

    subgraph "Event Consumers"
        Eligibility[Eligibility Consumer]
        Campaign[Campaign Consumer]
        Notification[Notification Consumer]
        Analytics[Analytics Consumer]
        Audit[Audit Consumer]
        ML[ML Feature Consumer]
    end

    subgraph "Event Store"
        EventDB[(Event Store DB)]
        AnalyticsDB[(Analytics DB)]
    end

    PMS_EVT --> Queue
    WEB_EVT --> Queue
    SMS_EVT --> Queue
    PATIENT_EVT --> Queue
    STAFF_EVT --> Queue
    SCHED_EVT --> Queue
    AI_EVT --> Queue

    Queue --> Eligibility
    Queue --> Campaign
    Queue --> Notification
    Queue --> Analytics
    Queue --> Audit
    Queue --> ML

    Queue --> DLQ

    Eligibility --> EventDB
    Campaign --> EventDB
    Audit --> EventDB
    Analytics --> AnalyticsDB
    ML --> AnalyticsDB
```

## AD.4 Data Flow — Recapture Pipeline

```mermaid
graph TB
    Start[Trigger Event<br/>cancellation, no-show, lead abandoned] --> Detect[Opportunity Detection]
    Detect --> Check{Eligibility<br/>Check}
    Check -->|Not Eligible| Suppress[Suppress - Do Not Contact]
    Check -->|Eligible| Score[ML Priority Scoring]
    Score --> Select[Channel Selection]
    Select --> Generate[AI Message Generation]
    Generate --> Validate[Output Validation]
    Validate -->|Invalid| Fix[Fix or Use Template]
    Validate -->|Valid| Send[Send Message]
    Send --> Track[Track Delivery]
    Track --> Wait{Patient<br/>Responds?}
    Wait -->|Yes| Handle[AI Conversation / Handoff]
    Wait -->|No| CheckMore{More<br/>Attempts?}
    CheckMore -->|Yes| WaitMore[Wait Cooldown]
    WaitMore --> Generate
    CheckMore -->|No| Staff[Create Staff Task]
    Handle --> Outcome[Record Outcome]
    Staff --> Outcome
    Suppress --> End[End]
    Outcome --> End
    End --> Learn[ML Learning Loop]

    style Start fill:#e1f5fe
    style Handle fill:#fff3e0
    style Safety_Check fill:#ffebee
    style End fill:#e8f5e9
```

## AD.5 AI Decision Flow

```mermaid
graph TB
    PatientMsg[Patient Message] --> Emergency{Emergency<br/>Keywords?}
    Emergency -->|Yes| SafetyEsc[SAFETY ESCALATION]
    Emergency -->|No| Consent{Consent<br/>Valid?}
    Consent -->|No| Suppress[SUPPRESS]
    Consent -->|Yes| OptOut{Opted<br/>Out?}
    OptOut -->|Yes| Suppress
    OptOut -->|No| FreqCap{Frequency<br/>Cap Reached?}
    FreqCap -->|Yes| Suppress
    FreqCap -->|No| QuietHours{Quiet<br/>Hours?}
    QuietHours -->|Yes| Schedule[Schedule for Later]
    QuietHours -->|No| Classify[AI Intent Classification]
    Classify --> Safety{AI Safety<br/>Check}
    Safety -->|Unsafe| SafetyEsc
    Safety -->|Safe| Plan[Generate Action Plan]
    Plan --> Tools{Needs<br/>Tool?}
    Tools -->|Yes| CallTool[Call Tool<br/>verify_data]
    CallTool --> Validate{Data<br/>Verified?}
    Validate -->|No| Handoff[HUMAN HANDOFF]
    Validate -->|Yes| Generate[Generate Response]
    Tools -->|No| Generate
    Generate --> ValidateOut{Output<br/>Valid?}
    ValidateOut -->|No| Handoff
    ValidateOut -->|Yes| Send[Send Response]
    Send --> Log[Log Everything]

    style SafetyEsc fill:#ffcdd2
    style Suppress fill:#fff9c4
    style Handoff fill:#ffe0b2
    style Send fill:#c8e6c9
```

## AD.6 Multi-Tenant Data Architecture

```mermaid
graph TB
    subgraph "Tenant A - Dental Group X"
        TA_Clinic[Clinic A-1]
        TA_Patients[Patients]
        TA_Staff[Staff]
        TA_Config[Configuration]
    end

    subgraph "Tenant B - Dental Group Y"
        TB_Clinic[Clinic B-1]
        TB_Clinic2[Clinic B-2]
        TB_Patients[Patients]
        TB_Staff[Staff]
        TB_Config[Configuration]
    end

    subgraph "Tenant C - Single Practice"
        TC_Clinic[Clinic C-1]
        TC_Patients[Patients]
        TC_Staff[Staff]
        TC_Config[Configuration]
    end

    subgraph "Platform Layer (HeyJarvis)"
        API[API Layer<br/>Tenant from JWT]
        RLS[Row-Level Security]
        Encryption[Per-Tenant Encryption]
        RateLimit[Per-Tenant Rate Limits]
    end

    subgraph "Shared Infrastructure"
        DB[(PostgreSQL<br/>with RLS)]
        Cache[(Redis<br/>tenant-prefixed keys)]
        Queue[Message Queue<br/>tenant in message)]
        LLM[LLM Provider<br/>BAAs per tenant]
    end

    TA_Clinic --> API
    TA_Patients --> API
    TA_Staff --> API
    TA_Config --> API

    TB_Clinic --> API
    TB_Clinic2 --> API
    TB_Patients --> API
    TB_Staff --> API
    TB_Config --> API

    TC_Clinic --> API
    TC_Patients --> API
    TC_Staff --> API
    TC_Config --> API

    API --> RLS
    RLS --> Encryption
    Encryption --> RateLimit
    RateLimit --> DB
    RateLimit --> Cache
    RateLimit --> Queue
    RateLimit --> LLM

    style TA_Clinic fill:#e3f2fd
    style TB_Clinic fill:#f3e5f5
    style TC_Clinic fill:#e8f5e9
    style API fill:#fff3e0
    style RLS fill:#ffebee
```

## AD.7 Integration Architecture

```mermaid
graph TB
    subgraph "HeyJarvis Core"
        Core[Core System]
    end

    subgraph "Integration Adapters"
        SchedBase[Scheduling Provider<br/>Base Interface]
        PatientBase[Patient Provider<br/>Base Interface]
        InsBase[Insurance Provider<br/>Base Interface]
        CommBase[Communication Provider<br/>Base Interface]
    end

    subgraph "Scheduling Adapters"
        OpenDental[Open Dental]
        Eaglesoft[Eaglesoft]
        Dentrix[Dentrix]
        CustomAPI[Custom REST API]
    end

    subgraph "Communication Adapters"
        TwilioSMS[Twilio SMS]
        TwilioVoice[Twilio Voice]
        Postmark[Postmark Email]
        WhatsAppAPI[WhatsApp Business]
    end

    subgraph "Insurance Adapters"
        NaviNet[NaviNet]
        EagleSoftIns[Eaglesoft Insurance]
        CustomIns[Custom Insurance API]
    end

    subgraph "Data Flow"
        Sync[Sync: Scheduled polling]
        Async[Async: Webhook handlers]
        Cache[Cache: Local data copy]
        Retry[Retry: Exponential backoff]
    end

    Core --> SchedBase
    Core --> PatientBase
    Core --> InsBase
    Core --> CommBase

    SchedBase --> OpenDental
    SchedBase --> Eaglesoft
    SchedBase --> Dentrix
    SchedBase --> CustomAPI

    CommBase --> TwilioSMS
    CommBase --> TwilioVoice
    CommBase --> Postmark
    CommBase --> WhatsAppAPI

    InsBase --> NaviNet
    InsBase --> EagleSoftIns
    InsBase --> CustomIns

    OpenDental --> Sync
    OpenDental --> Async
    Eaglesoft --> Sync
    Eaglesoft --> Async
    TwilioSMS --> Async
    NaviNet --> Sync

    Sync --> Cache
    Async --> Cache
    Cache --> Core

    Sync --> Retry
    Async --> Retry
    Retry --> Core
```

## AD.8 Campaign Execution Flow

```mermaid
graph TB
    Trigger[Campaign Trigger<br/>Event Detected] --> Evaluate[Evaluate Eligibility]
    Evaluate --> Check{Eligible?}
    Check -->|No| Skip[Skip - Log Reason]
    Check -->|Yes| Queue[Add to Campaign Queue]
    Queue --> Wait1[Wait for Scheduled Time]
    Wait1 --> CheckSupp{Check<br/>Suppression}
    CheckSupp -->|Suppressed| Remove[Remove from Queue]
    CheckSupp -->|Not Suppressed| Send1[Send Attempt 1]
    Send1 --> Track1[Track Delivery]
    Track1 --> WaitResponse{Patient<br/>Responds?}
    WaitResponse -->|Yes| Conversation[Handle Conversation]
    WaitResponse -->|No| WaitCooldown[Wait Cooldown Period]
    WaitCooldown --> CheckStop{Stop<br/>Condition?}
    CheckStop -->|Yes| End[End Campaign]
    CheckStop -->|No| CheckMoreAttempts{More<br/>Attempts?}
    CheckMoreAttempts -->|No| CreateTask[Create Staff Task]
    CheckMoreAttempts -->|Yes| CheckSupp2{Check<br/>Suppression}
    CheckSupp2 -->|Suppressed| End
    CheckSupp2 -->|Not Suppressed| Send2[Send Attempt N]
    Send2 --> Track2[Track Delivery]
    Track2 --> WaitResponse2{Patient<br/>Responds?}
    WaitResponse2 -->|Yes| Conversation
    WaitResponse2 -->|No| WaitCooldown2[Wait Cooldown]
    WaitCooldown2 --> CheckStop

    Conversation --> Booked{Patient<br/>Booked?}
    Booked -->|Yes| Success[SUCCESS - Record Revenue]
    Booked -->|No| Declined{Patient<br/>Declined?}
    Declined -->|Yes| End
    Declined -->|No| Continue[Continue Conversation]

    Success --> End
    CreateTask --> End
    Skip --> End
    Remove --> End

    style Success fill:#c8e6c9
    style SafetyEsc fill:#ffcdd2
    style End fill:#e8f5e9
    style Suppress fill:#fff9c4
```

## AD.9 Database Entity Relationship

```mermaid
erDiagram
    ORGANIZATION ||--o{ CLINIC : has
    CLINIC ||--o{ LOCATION : has
    CLINIC ||--o{ PROVIDER : has
    CLINIC ||--o{ STAFF : has
    CLINIC ||--o{ PATIENT : has
    CLINIC ||--o{ SERVICE : offers
    CLINIC ||--o{ CAMPAIGN : runs

    PATIENT ||--o{ APPOINTMENT : has
    PATIENT ||--o{ CONSENT : gives
    PATIENT ||--o{ COMMUNICATION_PREFERENCE : has
    PATIENT ||--o{ CONVERSATION : participates
    PATIENT ||--o{ RECAPTURE_OPPORTUNITY : generates
    PATIENT ||--o{ TREATMENT_PLAN : has

    APPOINTMENT ||--o{ APPOINTMENT_HISTORY : tracks
    APPOINTMENT }|--|| PROVIDER : with
    APPOINTMENT }|--|| SERVICE : for
    APPOINTMENT }|--|| LOCATION : at

    CONVERSATION ||--o{ MESSAGE : contains
    CONVERSATION ||--o{ CONVERSATION_EVENT : logs
    CONVERSATION ||--o{ HUMAN_HANDOFF : generates

    RECAPTURE_OPPORTUNITY ||--o{ RECAPTURE_ATTEMPT : has
    RECAPTURE_ATTEMPT ||--o{ CHANNEL_DELIVERY : uses

    CAMPAIGN ||--o{ CAMPAIGN_SEQUENCE : defines
    CAMPAIGN_SEQUENCE ||--o{ CAMPAIGN_STEP : contains

    HUMAN_HANDOFF ||--o{ HANDOFF_EVENT : tracks

    MESSAGE ||--o{ MESSAGE_EVENT : tracks

    AI_DECISION ||--o{ AI_ACTION : contains
    AI_DECISION }|--|| CONVERSATION : for

    AUDIT_LOG }|--|| ORGANIZATION : belongs_to

    ORGANIZATION {
        uuid id PK
        string name
        string industry
        jsonb settings
        timestamp created_at
        timestamp updated_at
    }

    CLINIC {
        uuid id PK
        uuid organization_id FK
        string name
        string phone
        string email
        jsonb settings
        timestamp created_at
    }

    PATIENT {
        uuid id PK
        uuid clinic_id FK
        string first_name
        string last_name
        string phone
        string email
        date dob
        jsonb demographics
        timestamp created_at
        timestamp updated_at
    }

    CONSENT {
        uuid id PK
        uuid patient_id FK
        string channel
        string status
        timestamp consented_at
        timestamp revoked_at
        string method
    }

    APPOINTMENT {
        uuid id PK
        uuid patient_id FK
        uuid clinic_id FK
        uuid provider_id FK
        uuid service_id FK
        datetime scheduled_at
        datetime completed_at
        string status
        string cancellation_reason
        timestamp created_at
    }

    CONVERSATION {
        uuid id PK
        uuid patient_id FK
        uuid clinic_id FK
        string channel
        string status
        jsonb context
        timestamp started_at
        timestamp ended_at
    }

    MESSAGE {
        uuid id PK
        uuid conversation_id FK
        uuid patient_id FK
        string direction
        string channel
        text content
        jsonb metadata
        timestamp sent_at
    }

    RECAPTURE_OPPORTUNITY {
        uuid id PK
        uuid patient_id FK
        uuid clinic_id FK
        string category
        string state
        float priority_score
        jsonb context
        timestamp detected_at
        timestamp resolved_at
    }

    CAMPAIGN {
        uuid id PK
        uuid clinic_id FK
        string name
        jsonb config
        boolean active
        timestamp created_at
    }
```

## AD.10 Deployment Architecture

```mermaid
graph TB
    subgraph "Production Region (us-east-1)"
        subgraph "VPC"
            subgraph "Public Subnets"
                ALB[Application Load Balancer]
                NAT[NAT Gateway]
            end

            subgraph "Private Subnets (Application)"
                API1[API Server 1]
                API2[API Server 2]
                API3[API Server 3]
                Worker1[Worker 1]
                Worker2[Worker 2]
                Worker3[Worker 3]
                Scheduler[Scheduler]
            end

            subgraph "Data Subnets"
                DB_Primary[(RDS Primary)]
                DB_Replica1[(RDS Replica 1)]
                DB_Replica2[(RDS Replica 2)]
                Redis[(ElastiCache Redis)]
            end

            subgraph "S3"
                AppData[Application Data]
                Backups[Database Backups]
            end
        end

        subgraph "EKS Cluster"
            K8s_Worker[Worker Pods]
            K8s_API[API Pods]
            K8s_Monitor[Monitoring]
        end
    end

    subgraph "DR Region (us-west-2)"
        DR_DB[(Standby DB)]
        DR_Redis[(Standby Redis)]
    end

    subgraph "CI/CD"
        GitHub[GitHub Actions]
        Registry[Container Registry]
    end

    Internet[Internet Users] --> ALB
    ALB --> API1
    ALB --> API2
    ALB --> API3

    API1 --> DB_Primary
    API2 --> DB_Primary
    API3 --> DB_Primary

    API1 --> Redis
    API2 --> Redis
    API3 --> Redis

    Worker1 --> DB_Primary
    Worker2 --> DB_Replica1
    Worker3 --> DB_Replica2

    DB_Primary --> DB_Replica1
    DB_Primary --> DB_Replica2

    DB_Primary --> Backups
    Backups --> DR_DB

    GitHub --> Registry
    Registry --> K8s_API
    Registry --> K8s_Worker

    style DB_Primary fill:#ffebee
    style Backups fill:#fff9c4
    style DR_DB fill:#e8f5e9
    style ALB fill:#e3f2fd
```
