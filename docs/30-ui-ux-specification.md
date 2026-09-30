# UI/UX Specification — Complete Interface Design

## UX.1 Design Principles

1. **Staff-first.** Staff uses this system 8+ hours/day. Optimize for them.
2. **Patient-first.** Patients see this briefly. Make it clear and fast.
3. **Clarity over cleverness.** No confusing interactions.
4. **Consistency.** Same patterns everywhere.
5. **Accessibility.** WCAG 2.1 AA compliant.
6. **Responsive.** Works on desktop, tablet, mobile.

## UX.2 Patient-Facing Interfaces

### Website Chat Widget

```
┌─────────────────────────────────────────────┐
│  HeyJarvis AI                    [X Close]  │
├─────────────────────────────────────────────┤
│                                             │
│  👋 Hi! I'm the Sunrise Dental AI.         │
│  How can I help you today?                  │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ 👤 I broke my front tooth            │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  I'm sorry to hear that! Let me help you    │
│  get seen right away.                        │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ We have Dr. Smith available today at │    │
│  │ 3:20 PM. Would you like me to book   │    │
│  │ that for you?                        │    │
│  │                                      │    │
│  │     [Yes, book it]  [Other times]    │    │
│  └─────────────────────────────────────┘    │
│                                             │
├─────────────────────────────────────────────┤
│  💬 Type a message...          [Send]       │
└─────────────────────────────────────────────┘

Disclosure: "You're chatting with an AI assistant."
```

### SMS Conversation

```
Patient phone screen:

[8:30 AM] Sunrise Dental: Hi Maria! We missed you for
your cleaning last week. Dr. Smith has openings Thursday
at 10 AM. Want me to book it? Reply YES or call
(555) 123-4567. Reply STOP to unsubscribe.

[8:35 AM] Maria: YES

[8:35 AM] Sunrise Dental: Great! I've booked you for
Thursday, Oct 5 at 10 AM with Dr. Smith for a cleaning.
You'll get a confirmation shortly. See you then!
Reply HELP for help or STOP to unsubscribe.

[8:36 AM] System: Confirmation sent (email/SMS)
```

## UX.3 Staff Dashboard

### Screen 1: Recapture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│ HeyJarvis                    Sunrise Dental    ▼  Jennifer S.    │
├──────────────────────────────────────────────────────────────────┤
│  Dashboard  │  Recapture  │  Conversations  │  Campaigns  │ ... │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TODAY'S RECAPTURE                                        [Date]  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ 42       │ │ 28       │ │ 8        │ │ $4,250   │          │
│  │Opportunities│Sent Today│ │Responses│ │Recovered │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                  │
│  THIS WEEK              vs LAST WEEK              Trend          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [Bar chart: opportunities, sent, responded, booked]     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  RECENT ACTIVITY                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 🔴 Sarah J. — Emergency handoff (2 min ago)              │  │
│  │ 🟠 Mike C. — Booked cleaning (15 min ago)                │  │
│  │ 🟢 Emily D. — Responded to recall (30 min ago)           │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Screen 2: Opportunities Queue

```
┌──────────────────────────────────────────────────────────────────┐
│  Recapture  │  Opportunities  │  Active  │  Paused  │  Archived  │
├──────────────────────────────────────────────────────────────────┤
│  Filter: [Category ▼] [Priority ▼] [Date ▼]    [Export]        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🔴 HIGH │ Sarah Johnson │ Cancellation │ $350 │ 2h ago   │   │
│  │ Due: Root canal. Cancelled yesterday. High value.          │   │
│  │ [View] [Message] [Dismiss]                                  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ 🟡 MED │ Mike Chen │ No-show │ $150 │ 1d ago              │   │
│  │ Missed cleaning. First no-show.                            │   │
│  │ [View] [Message] [Dismiss]                                  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ 🟢 LOW │ Emily Davis │ Recall │ $120 │ 3d ago              │   │
│  │ Overdue for hygiene recall.                                 │   │
│  │ [View] [Message] [Dismiss]                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Showing 1-20 of 42 opportunities                    [1] 2 3 ▸ │
└──────────────────────────────────────────────────────────────────┘
```

### Screen 3: Conversation Inbox

```
┌──────────────────────────────────────────────────────────────────┐
│  Conversations  │  Active (12) │  Handoffs (3) │  Ended (156)    │
├──────────────────────┬───────────────────────────────────────────┤
│                      │                                           │
│  SEARCH              │  Sarah Johnson                            │
│  [🔍 Search...    ]  │  +1 (555) 234-5678                       │
│                      │  SMS • Active • Started 2h ago            │
│  FILTERS             │                                           │
│  □ Needs reply       │  ┌───────────────────────────────────┐    │
│  □ Handoffs          │  │ AI: Hi Sarah! I can see Dr. Smith  │    │
│  □ Safety            │  │ has availability today at 3:20 PM.  │    │
│  □ Urgent            │  │ Would you like me to book that?     │    │
│                      │  ├───────────────────────────────────┤    │
│  CONVERSATIONS       │  │ 👤 Yes please!                     │    │
│                      │  ├───────────────────────────────────┤    │
│  🔴 S. Johnson 2m   │  │ AI: I've booked you for today at   │    │
│  🟠 M. Chen 15m     │  │ 3:20 PM. You'll get a confirmation. │    │
│  🟢 E. Davis 30m    │  └───────────────────────────────────┘    │
│  ...                 │                                           │
│                      │  ┌───────────────────────────────────┐    │
│  Quick stats:        │  │ Type a message...          [Send] │    │
│  12 active           │  └───────────────────────────────────┘    │
│  3 handoffs          │                                           │
│  8 need reply        │                                           │
└──────────────────────┴───────────────────────────────────────────┘
```

### Screen 4: Human Handoff Queue

```
┌──────────────────────────────────────────────────────────────────┐
│  Handoffs  │  Pending (3) │  In Progress (1) │  Resolved (24)   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SORT BY: [Urgency ▼] [Time ▼]                                  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🚨 CRITICAL │ Sarah Johnson                               │   │
│  │ Emergency: "My face is swelling"                           │   │
│  │ 2 min ago | Unassigned                                    │   │
│  │ [Take] [View Conversation]                                 │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ 😤 HIGH │ Mike Chen                                        │   │
│  │ Complaint: "This is ridiculous, I've been waiting..."      │   │
│  │ 15 min ago | Assigned: Jennifer S.                        │   │
│  │ [View] [Call Patient]                                      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ ❓ MEDIUM │ Emily Davis                                     │   │
│  │ Insurance question about Invisalign                        │   │
│  │ 30 min ago | Unassigned                                    │   │
│  │ [Take] [View]                                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Screen 5: Campaign Builder

```
┌──────────────────────────────────────────────────────────────────┐
│  Campaigns  │  [+ New Campaign]                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ACTIVE CAMPAIGNS                    Status  │  Metrics    │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  Abandoned Consultation Recovery                        │   │
│  │  Trigger: Booking abandoned > 2h ago                     │   │
│  │  Sequence: SMS (2h) → SMS (48h) → Staff task (72h)      │   │
│  │                                                          │   │
│  │  ● Active                                                │   │
│  │  Sent: 156 │ Response: 32 │ Booked: 18 │ Rev: $4,500   │   │
│  │                                                          │   │
│  │  [Edit] [Pause] [Analytics]                               │   │
│  │                                                          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  Cancellation Recovery                                   │   │
│  │  Trigger: Appointment cancelled                           │   │
│  │  Sequence: SMS (1h) → SMS (24h) → Staff task (48h)      │   │
│  │                                                          │   │
│  │  ● Active                                                │   │
│  │  Sent: 89 │ Response: 15 │ Booked: 7 │ Rev: $1,750     │   │
│  │                                                          │   │
│  │  [Edit] [Pause] [Analytics]                               │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Screen 6: Analytics Dashboard

```
┌──────────────────────────────────────────────────────────────────┐
│  Analytics  │  Overview  │  Campaigns  │  Channels  │  Revenue   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OCTOBER 2025                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ 150       │ │ 28%      │ │ 18       │ │ $4,250   │          │
│  │Opportunities│Response │ │Booked    │ │Recovered │          │
│  │ this month│rate      │ │          │ │          │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                  │
│  FUNNEL                                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  150 Opportunities → 140 Sent → 39 Responses → 18 Booked  │   │
│  │  [==========100%====>] [==93%==>] [==28%=>] [==46%=>]    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  BY CATEGORY                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Cancellation│ No-show  │  Recall  │  Lead     │          │
│  │   50     │ │   30     │ │   40     │ │   30     │          │
│  │ 12 booked│ │  4 booked│ │  1 booked│ │  1 booked│          │
│  │ 24% rate │ │ 13% rate │ │ 2.5% rate│ │ 3.3% rate│          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                  │
│  BY CHANNEL                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SMS:  100 sent → 30 responses (30%) → 15 booked         │   │
│  │  Email:  35 sent → 8 responses (23%) → 3 booked          │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## UX.4 Design System

### Colors
```
Primary: #2563EB (Blue)
Success: #16A34A (Green)
Warning: #F59E0B (Amber)
Danger: #DC2626 (Red)
Info: #0891B2 (Cyan)
Background: #FFFFFF
Surface: #F8FAFC
Text Primary: #1E293B
Text Secondary: #64748B
Border: #E2E8F0
```

### Typography
```
Font: Inter
Sizes:
- H1: 30px / Bold
- H2: 24px / Bold
- H3: 20px / Semibold
- Body: 16px / Regular
- Small: 14px / Regular
- Caption: 12px / Regular
```

### Spacing
```
Unit: 4px
Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64
```
