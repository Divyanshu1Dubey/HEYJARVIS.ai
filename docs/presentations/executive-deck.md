# Executive Presentation — Board/Investor Deck

## Slide 1: Title

```
HEYJARVIS PATIENT RECAPTURE
AI-Powered Revenue Recovery for Dental Practices

[HeyJarvis logo]

Confidential — For Internal Review
```

## Slide 2: The Problem

```
THE PROBLEM
Dental Practices Lose 20-30% of Revenue to Patient Drop-off

Current State:
• Manual phone calls (slow, inconsistent)
• Generic SMS blasts (low response, often ignored)
• Staff overwhelmed with follow-up tasks
• No visibility into WHY patients don't book
• No systematic approach to recovery

The Cost to a Typical Practice:
• 100 missed opportunities/month
• $200 average appointment value
• = $20,000/month in lost revenue
• = $240,000/year

Current Solutions Are Broken:
• "Send more messages" → Spam
• "Hire more staff" → Expensive
• "Better scheduling software" → Doesn't help with drop-off
```

## Slide 3: The Solution

```
THE SOLUTION
AI-Powered Patient Recapture

What It Does:
1. IDENTIFY — Automatically finds patients who didn't complete their journey
2. UNDERSTAND — AI determines WHY they didn't convert
3. PRIORITIZE — ML scores which patients to contact first
4. PERSONALIZE — AI crafts context-aware messages
5. CONVERT — Patient books/reschedules through AI or staff
6. MEASURE — Holdout-based attribution of recovered revenue

The System in 60 Seconds:

Patient drops off
       ↓
Recapture Engine detects opportunity
       ↓
Policy Engine checks: consent? opted out? frequency caps?
       ↓
ML Model scores priority
       ↓
AI generates personalized message
       ↓
Message sent via optimal channel (SMS, email, voice)
       ↓
Patient responds → AI handles OR human takes over
       ↓
Appointment booked → Revenue recovered
```

## Slide 4: How It Works (Architecture)

```
PATIENT
  │
  ▼
┌─────────────────────────────────────────────┐
│  CHANNELS                                   │
│  SMS │ Email │ Web Chat │ Voice │ WhatsApp   │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  API GATEWAY                                │
│  Auth │ Rate Limit │ Tenant Isolation        │
└──────────────────┬──────────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│  Policy Engine  │  │  AI Engine      │
│  (Rules First)  │  │  (LLM + ML)     │
│                 │  │                 │
│  Consent check  │  │  Intent classify│
│  Opt-out check  │  │  Message gen    │
│  Frequency cap  │  │  Safety check   │
│  Quiet hours    │  │  Tool calling   │
│  Suppression    │  │  Conversation   │
└────────┬────────┘  └────────┬────────┘
         │                    │
         ▼                    ▼
┌─────────────────────────────────────────────┐
│  TOOL LAYER                                 │
│  Booking │ Availability │ Insurance │ Tools  │
└──────────────────┬──────────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│  EXTERNAL APIs  │  │  ANALYTICS      │
│  PMS │ Insurance │  │  Revenue        │
│  SMS │ Email     │  │  Attribution    │
└─────────────────┘  └─────────────────┘
```

## Slide 5: Key Differentiators

```
WHAT MAKES HEYJARVIS DIFFERENT

vs. Traditional Approaches:
  Manual follow-up → AI 24/7 availability
  Generic messages → Personalized, context-aware
  No tracking → Full attribution
  Staff overload → AI containment

vs. Other Tech:
  Chatbot → Full recapture system with conversation + tools
  Generic → Healthcare-specific (HIPAA, TCPA, safety)
  Messaging → Multi-channel orchestration
  Claims → Tool-verified, no hallucination
  Blast campaigns → ML-prioritized, frequency-capped

vs. Build In-House:
  $500K+ investment → $299/month
  12+ months → 8 weeks to pilot
  Hiring AI team → AI included
  Compliance burden → Built-in
  Integration work → Pre-built connectors
```

## Slide 6: AI Architecture

```
AI USAGE: WHERE AND WHY

Layer 1: Deterministic Rules (Always)
├── Consent checks
├── Opt-out enforcement
├── Frequency caps
├── Quiet hours
├── Safety patterns (emergency keywords)
└── Business rules

Layer 2: AI Classification (When Needed)
├── Intent classification (what does patient want?)
├── Safety classification (is this an emergency?)
├── Reason extraction (why did patient drop off?)
└── Cost: $0.01/call (small LLM)

Layer 3: AI Generation (When Needed)
├── Message personalization
├── Conversation responses
├── Handoff summaries
└── Cost: $0.05/call (strong LLM)

Layer 4: ML Prediction (When Available)
├── Conversion probability
├── Priority scoring
├── Optimal timing
├── Channel selection
└── Cost: $0.001/prediction (gradient boosting)

TOTAL AI COST PER PATIENT: ~$0.15
```

## Slide 7: Safety & Compliance

```
SAFETY & COMPLIANCE ARCHITECTURE

HIPAA Compliance:
✓ BAA with all vendors (LLM, SMS, email, cloud)
✓ Encryption at rest (AES-256)
✓ Encryption in transit (TLS 1.3)
✓ Row-level security (tenant isolation)
✓ Complete audit trail
✓ PHI minimization in AI context
✓ Data retention and deletion

TCPA Compliance:
✓ Express consent before SMS
✓ STOP keyword handling
✓ Time restrictions
✓ Opt-out within 10 business days

AI Safety:
✓ Emergency pattern detection (99%+ accuracy)
✓ Medical advice prevention (0% leakage)
✓ No diagnosis capability
✓ No prescription capability
✓ Human handoff for sensitive cases
✓ Output validation (no hallucination)

Safety Layers:
1. Pattern matching (deterministic)
2. Policy engine (deterministic)
3. Safety classifier (AI)
4. Output validation (deterministic)
5. Human review (human)
```

## Slide 8: Technology Stack

```
TECHNOLOGY STACK

Backend:
  API:        FastAPI (Python)
  Worker:     Python asyncio
  Database:   PostgreSQL (RLS, ACID)
  Cache:      Redis
  Queue:      Redis Streams

AI/ML:
  LLM:        Anthropic Claude
  ML:         Gradient Boosting (XGBoost)
  Embeddings: Sentence Transformers

Integrations:
  SMS:        Twilio
  Email:      Postmark
  PMS:        Open Dental, Eaglesoft, Dentrix
  Insurance:  [Provider API]

Infrastructure:
  Container:  Docker
  Orchestrate: Kubernetes
  IaC:        Terraform
  CI/CD:      GitHub Actions

Observability:
  Monitoring: Datadog
  Logging:    CloudWatch / Loki
  Tracing:    OpenTelemetry
```

## Slide 9: Revenue Model

```
REVENUE MODEL

SaaS Subscription (70% of revenue):
  Starter:    $299/month (up to 1,000 patients)
  Growth:     $799/month (up to 5,000 patients)
  Professional: $1,999/month (up to 25,000 patients)
  Enterprise: Custom pricing

Usage-Based (20% of revenue):
  SMS:        $0.0075/message
  AI conv:    $0.05/conversation
  Revenue share: 5% of recovered revenue

Professional Services (10%):
  Implementation: $5,000-$15,000
  Custom integration: $10,000+
  Training: $2,000/session

Example Clinic (Growth Tier):
  Subscription:  $799/month
  Usage:           $150/month
  Revenue share:   $300/month
  ─────────────────────────
  Total:         $1,249/month

Clinic ROI:
  Recovered revenue:  $6,000/month
  Cost:               $1,249/month
  ROI:                4.8x
```

## Slide 10: Go-to-Market

```
GO-TO-MARKET STRATEGY

Target: Independent dental practices (1-3 dentists)

Phase 1: Direct Sales (Months 1-6)
  • Target: 10 pilot clinics
  • Method: Direct outreach, industry connections
  • Goal: Case studies

Phase 2: Channel Partnerships (Months 6-18)
  • PMS vendor partnerships
  • Dental supplier partnerships
  • Marketing agency partnerships
  • Goal: 100 clinics

Phase 3: Digital Marketing (Months 12-24)
  • SEO, content, paid ads
  • Review sites
  • Goal: 300 clinics

Phase 4: Inside Sales (Months 18-36)
  • Self-service signup
  • Freemium tier
  • Referral program
  • Goal: 500+ clinics

Market Size:
  TAM: $40-60B/year
  SAM: $10-15B/year
  SOM (Year 3): $9M ARR
```

## Slide 11: Financial Projections

```
FINANCIAL PROJECTIONS

Year 1:
  Q1:  5 clinics,   $30K ARR
  Q2: 15 clinics,  $120K ARR
  Q3: 30 clinics,  $300K ARR
  Q4: 50 clinics,  $600K ARR
  Total Year 1: $600K ARR

Year 2:
  Q1: 80 clinics, $1.0M ARR
  Q2: 120 clinics, $1.6M ARR
  Q3: 170 clinics, $2.4M ARR
  Q4: 200 clinics, $3.2M ARR
  Total Year 2: $3.2M ARR

Unit Economics:
  ARR per clinic:    $11,388/year
  COGS per clinic:   $1,200/year
  Gross margin:      89%
  LTV/CAC:           28.5x
  Payback period:    1.2 months

Funding Required: ~$2-3M to reach profitability
```

## Slide 12: Competitive Landscape

```
COMPETITIVE LANDSCAPE

                    High AI Capability
                         │
                         │   HeyJarvis
                         │   ★★★★★
              Custom AI  │
                    ★★★   │
                         │
  ───────────────────────┼────────────────────────
                         │
                    ★★    │   ★★★★
              Weave      │   Solutionreach
                         │   RevenueWell
                         │
              ★          │   ★★★
         Basic SMS        │   Podium
                         │
                    Low AI Capability
                         │
                         └────────────────────────
                    Low Healthcare Focus          High

Key Differentiators vs. Competitors:
✓ AI conversation (not just messaging)
✓ Healthcare compliance (HIPAA, TCPA)
✓ Safety-first architecture
✓ Tool-verified responses (no hallucination)
✓ Holdout-based attribution
✓ ML-powered prioritization
```

## Slide 13: Roadmap

```
PRODUCT ROADMAP

Phase 1 (Weeks 5-12): Rules-First MVP
  ✓ Patient database
  ✓ Consent management
  ✓ Rule-based recapture
  ✓ SMS/Email
  ✓ Staff dashboard
  → 1-2 pilot clinics

Phase 2 (Weeks 13-20): AI Personalization
  ✓ AI message generation
  ✓ Intent classification
  ✓ Conversation agent
  ✓ Safety classifier
  ✓ Human handoff
  → 10-20 clinics

Phase 3 (Weeks 21-28): ML Predictions
  ✓ Conversion prediction
  ✓ Priority scoring
  ✓ Optimal timing
  ✓ A/B testing
  → 50+ clinics

Phase 4 (Weeks 29-36): Multi-Channel
  ✓ Email channel
  ✓ Voice channel
  ✓ Multi-channel orchestration
  → 100+ clinics

Phase 5+ (Weeks 37+): Scale
  ✓ Real PMS integrations
  ✓ Advanced analytics
  ✓ White-label options
  → 500+ clinics
```

## Slide 14: Ask

```
THE ASK

We are raising [AMOUNT] to:

1. COMPLETE PHASE 1 (Rules-First MVP)
   • 8 weeks to first pilot clinic
   • Proven architecture and safety
   • Initial revenue validation

2. COMPLETE PHASE 2 (AI Personalization)
   • 8 weeks to AI-powered conversations
   • Full evaluation suite
   • Safety validation

3. ACQUIRE FIRST 50 CLIENTS
   • Direct sales
   • Channel partnerships
   • Case study development

4. BUILD TEAM
   • 3 additional engineers
   • 1 sales/business development
   • 1 customer success

Use of Funds:
  Engineering:    60%
  Sales/Marketing: 25%
  Operations:      15%

Milestones (12 months):
  Month 3:  First live clinic
  Month 6:  15 clinics, $120K ARR
  Month 9:  30 clinics, $300K ARR
  Month 12: 50 clinics, $600K ARR

Contact: [Contact Info]
```

## Slide 15: Team

```
THE TEAM

[Founder/CEO]:
• [Background]
• [Relevant experience]

[CTO]:
• [Background]
• [Technical leadership]

[Lead Engineer]:
• [Background]
• [Architecture experience]

[Clinical Advisor]:
• [Dental practice experience]
• [Patient communication expertise]

Advisors:
• [Name]: [Expertise]
• [Name]: [Expertise]

Why Us:
• Deep healthcare compliance knowledge
• Proven AI/ML engineering
• Dental industry connections
• Built production healthcare systems before
```
