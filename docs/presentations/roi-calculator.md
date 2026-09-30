# ROI Calculator — Patient Recapture Revenue Impact

## RC.1 ROI Calculation Framework

```
ROI = (Recovered Revenue - System Cost) / System Cost

Recovered Revenue = Σ(Opportunity Value × Recapture Rate)

Recapture Rate = Bookings / Total Opportunities
```

## RC.2 Practice Parameters

```
PRACTICE SIZE
├── Small: 1 dentist, 1 location, ~1,000 patients
├── Medium: 2-3 dentists, 1-2 locations, ~5,000 patients
├── Large: 5+ dentists, 3+ locations, ~15,000 patients
└── Group: 10+ dentists, 5+ locations, ~50,000 patients

PATIENT VOLUME
├── New patients/month: 20-100
├── Active patients: 500-50,000
├── Cancellations/month: 20-200
├── No-shows/month: 5-50
├── Unscheduled treatment plans: 30-300
└── Overdue recalls: 100-1,000

AVERAGE APPOINTMENT VALUE
├── Cleaning/Exam: $150-250
├── Filling: $200-400
├── Root Canal: $1,000-2,000
├── Crown: $1,200-2,500
├── Implant: $3,000-5,000
└── Orthodontics: $4,000-7,000
```

## RC.3 ROI by Practice Size

### Small Practice (1 dentist, 1,000 patients)

```
Monthly Parameters:
  Active patients: 1,000
  Cancellations/month: 20
  No-shows/month: 5
  Unscheduled treatment/month: 15
  Overdue recalls/month: 30
  Total opportunities/month: 70

Expected Recapture (15-25%):
  Conservative (15%): 10.5 bookings/month
  Expected (20%): 14 bookings/month
  Optimistic (25%): 17.5 bookings/month

Average Appointment Value: $300

Revenue Recovered:
  Conservative: 10.5 × $300 = $3,150/month
  Expected: 14 × $300 = $4,200/month
  Optimistic: 17.5 × $300 = $5,250/month

System Cost:
  Plan: Starter ($299/month)
  SMS: 70 msgs × $0.0075 = $0.53
  Total: ~$300/month

ROI:
  Conservative: ($3,150 - $300) / $300 = 9.5x
  Expected: ($4,200 - $300) / $300 = 13x
  Optimistic: ($5,250 - $300) / $300 = 16.5x

Annual Revenue Recovered: $37,800 - $63,000
```

### Medium Practice (3 dentists, 5,000 patients)

```
Monthly Parameters:
  Active patients: 5,000
  Cancellations/month: 100
  No-shows/month: 25
  Unscheduled treatment/month: 75
  Overdue recalls/month: 150
  Total opportunities/month: 350

Expected Recapture (15-25%):
  Conservative (15%): 52.5 bookings/month
  Expected (20%): 70 bookings/month
  Optimistic (25%): 87.5 bookings/month

Average Appointment Value: $400 (mix of services)

Revenue Recovered:
  Conservative: 52.5 × $400 = $21,000/month
  Expected: 70 × $400 = $28,000/month
  Optimistic: 87.5 × $400 = $35,000/month

System Cost:
  Plan: Growth ($799/month)
  SMS: 350 msgs × $0.0075 = $2.63
  AI: 100 conversations × $0.05 = $5
  Total: ~$807/month

ROI:
  Conservative: ($21,000 - $807) / $807 = 25x
  Expected: ($28,000 - $807) / $807 = 33.7x
  Optimistic: ($35,000 - $807) / $807 = 42.3x

Annual Revenue Recovered: $252,000 - $420,000
```

### Large Practice (10 dentists, 25,000 patients)

```
Monthly Parameters:
  Active patients: 25,000
  Cancellations/month: 500
  No-shows/month: 125
  Unscheduled treatment/month: 375
  Overdue recalls/month: 750
  Total opportunities/month: 1,750

Expected Recapture (15-25%):
  Conservative (15%): 262.5 bookings/month
  Expected (20%): 350 bookings/month
  Optimistic (25%): 437.5 bookings/month

Average Appointment Value: $500 (mix including higher-value)

Revenue Recovered:
  Conservative: 262.5 × $500 = $131,250/month
  Expected: 350 × $500 = $175,000/month
  Optimistic: 437.5 × $500 = $218,750/month

System Cost:
  Plan: Professional ($1,999/month)
  SMS: 1,750 msgs × $0.0075 = $13.13
  AI: 500 conversations × $0.05 = $25
  Total: ~$2,037/month

ROI:
  Conservative: ($131,250 - $2,037) / $2,037 = 64x
  Expected: ($175,000 - $2,037) / $2,037 = 85x
  Optimistic: ($218,750 - $2,037) / $2,037 = 106x

Annual Revenue Recovered: $1,575,000 - $2,625,000
```

## RC.4 ROI by Recapture Category

```
CANCELATION RECAPTURE
  Volume: 20-500/month (depends on practice size)
  Success rate: 20-30% (patient already interested)
  Value: $200-500/appointment
  Monthly recovered: $800 - $75,000

NO-SHOW RECAPTURE
  Volume: 5-125/month
  Success rate: 15-25%
  Value: $150-400/appointment
  Monthly recovered: $110 - $12,500

TREATMENT PLAN RECAPTURE
  Volume: 15-375/month
  Success rate: 10-20% (higher value)
  Value: $500-5,000/appointment
  Monthly recovered: $750 - $375,000

LEAD RECAPTURE
  Volume: 10-200/month
  Success rate: 10-20%
  Value: $150-400/appointment
  Monthly recovered: $150 - $16,000

RECALL REACTIVATION
  Volume: 30-750/month
  Success rate: 10-15%
  Value: $150-300/appointment
  Monthly recovered: $450 - $33,750

OVERALL:
  Conservative: 15% recapture rate
  Expected: 20% recapture rate
  Optimistic: 25% recapture rate
```

## RC.5 Time Savings ROI

```
STAFF TIME SAVINGS

Current State (Manual Follow-Up):
  Cancellations: 30 calls/week × 5 min = 2.5 hrs
  No-shows: 10 calls/week × 5 min = 0.8 hrs
  Treatment follow-up: 15 calls/week × 5 min = 1.25 hrs
  Recall calls: 50 calls/week × 3 min = 2.5 hrs
  Total: 7.05 hrs/week per front desk staff

With HeyJarvis:
  AI handles routine outreach: 5 hrs/week
  Staff handles only complex cases: 2 hrs/week
  Time saved: 5.05 hrs/week

Staff Cost:
  Front desk hourly rate: $20/hr
  Weekly savings: 5.05 × $20 = $101
  Monthly savings: $404
  Annual savings: $4,848

Additional Value:
  Staff freed for high-value tasks:
  • Better patient experience
  • More new patient intake
  • More complex case handling
  • Reduced staff burnout
```

## RC.6 Competitive ROI

```
vs. IN-HOUSE SOLUTION

Building In-House:
  • 2-3 engineers × 12 months × $150K = $450K-$675K
  • Infrastructure: $5K/month × 12 = $60K
  • Compliance/legal: $50K
  • Ongoing maintenance: $200K/year
  Total Year 1: $760K - $985K

Buying HeyJarvis:
  • Monthly: $799-1,999
  • Annual: $9,588 - $23,988
  • Implementation: Included

Savings: $736K - $961K in Year 1

vs. COMPETITOR (e.g., Weave, Solutionreach)

Competitor:
  • Similar pricing: $300-800/month
  • No AI conversation (manual after initial contact)
  • No tool-verified responses
  • No safety architecture
  • Generic templates

HeyJarvis:
  • AI-powered conversation
  • Tool-verified responses (no hallucination)
  • Healthcare safety architecture
  • Personalized messages
  • ML optimization

Value Differential:
  Higher conversion rate (20-30% vs 10-15%)
  Better patient experience
  Less staff time
  Compliance advantage
```

## RC.7 Sensitivity Analysis

```
SENSITIVITY: What If Numbers Change?

Scenario A: Lower Recapture Rate (10%)
  Expected monthly: 7 bookings × $400 = $2,800
  Cost: $807
  ROI: 3.5x (still positive)

Scenario B: Lower Average Value ($200)
  Expected monthly: 14 bookings × $200 = $2,800
  Cost: $807
  ROI: 3.5x (still positive)

Scenario C: Higher Costs (double)
  Cost: $1,614
  ROI: 16.8x (still excellent)

Scenario D: Best Case (30% recapture, $500 avg)
  Expected monthly: 21 bookings × $500 = $10,500
  Cost: $807
  ROI: 12x

BREAK-EVEN ANALYSIS:
  Minimum recapture rate: 3-5%
  Minimum bookings/month: 3-5
  Minimum revenue/month: $1,200-2,500

Even at very low adoption, system pays for itself.
```

## RC.8 3-Year Financial Model

```
YEAR 1
  Months 1-3: Pilot (5 clinics)
    Revenue: $5,000 ARR
    Cost: $150K (engineering + infra)
    Net: -$145K

  Months 4-6: Expansion (15 clinics)
    Revenue: $60,000 ARR
    Cost: $200K
    Net: -$140K

  Months 7-9: Growth (30 clinics)
    Revenue: $180,000 ARR
    Cost: $300K
    Net: -$120K

  Months 10-12: Scale (50 clinics)
    Revenue: $360,000 ARR
    Cost: $400K
    Net: -$40K

  Year 1 Total: $605K revenue, $1,050K cost, -$445K

YEAR 2
  Q1: 80 clinics, $800K ARR
  Q2: 120 clinics, $1.4M ARR
  Q3: 170 clinics, $2.1M ARR
  Q4: 250 clinics, $3.0M ARR

  Revenue: $3.0M
  Cost: $2.0M (engineering + sales + infra)
  Net: $1.0M

YEAR 3
  400 clinics, $5.0M ARR
  Cost: $3.5M
  Net: $1.5M

3-Year Cumulative: $8.6M revenue, $6.6M cost, $2.0M profit
```

## RC.9 Key Financial Metrics

```
UNIT ECONOMICS (Per Clinic - Growth Tier)

  Monthly Revenue:
    Subscription: $799
    Usage: $150
    Revenue share: $300
    Total: $1,249

  Monthly Cost:
    Infrastructure: $50
    AI/LLM: $40
    SMS/Email: $10
    Total: $100

  Gross Margin: 92%

  CAC (Customer Acquisition Cost): $1,200
  LTV (3-year): $44,964
  LTV/CAC: 37x
  Payback: 1 month

  Key Metrics:
    MRR: $1,249
    ARR: $14,988
    Gross Profit: $1,149/month
```

## RC.10 ROI Presentation Summary

```
FOR THE DENTAL PRACTICE OWNER

Your Situation:
  • 100 active patients dropping off/month
  • Average appointment: $300
  • Hidden revenue loss: $30,000/month

What HeyJarvis Does:
  • Recaptures 20% (industry benchmark)
  • = 20 recovered appointments/month
  • = $6,000/month recovered

Your Investment:
  • Growth plan: $799/month
  • Usage: $150/month
  • Total: $949/month

Your Return:
  • Recovered: $6,000/month
  • Cost: $949/month
  • Net benefit: $5,051/month
  • ROI: 6.3x

Plus:
  ✓ Staff time saved: 5 hrs/week
  ✓ Better patient experience
  ✓ 24/7 availability
  ✓ Full analytics dashboard
  ✓ HIPAA + TCPA compliant

Annual Impact:
  Recovered: $72,000
  Cost: $11,388
  Net: $60,612

This is a no-brainer.
```
