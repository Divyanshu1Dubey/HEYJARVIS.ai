# Human-in-the-Loop Design — Staff Handoff System

## HH.1 Design Principles

1. **Seamless handoff.** Patient should never feel the transition.
2. **Full context preserved.** Staff receives complete conversation history.
3. **Clear ownership.** Every handoff has an assigned owner.
4. **SLA tracking.** Handoffs have response time requirements.
5. **Resume capability.** AI can resume when handoff is resolved.
6. **Audit trail.** Every handoff is logged for compliance.

## HH.2 When to Hand Off

### Automatic Triggers

| Trigger | Urgency | Action |
|---------|---------|--------|
| Patient says "human", "staff", "real person" | medium | Immediate handoff |
| Emergency symptom detected | critical | Immediate handoff + alert |
| Medical question asked | high | Immediate handoff |
| Patient is angry/frustrated | high | Immediate handoff |
| Legal threat mentioned | high | Immediate handoff |
| Insurance dispute | medium | Handoff with context |
| AI confidence below threshold | medium | Handoff with context |
| Integration failure during conversation | medium | Handoff with explanation |
| Request outside AI scope | medium | Handoff |
| Patient asks for diagnosis | high | Handoff |
| Patient asks for treatment recommendation | high | Handoff |
| Patient asks to delete data | high | Handoff (privacy request) |
| Patient asks for records | medium | Handoff |
| AI cannot understand after 2 attempts | low | Handoff |

### Staff-Initiated

- Staff can take over any conversation at any time
- Staff can mark conversation as "requires AI follow-up"

## HH.3 Handoff States

```python
class HandoffState(str, Enum):
    PENDING = "pending"         # Created, not yet assigned
    ASSIGNED = "assigned"       # Assigned to staff member
    IN_PROGRESS = "in_progress" # Staff actively working
    RESOLVED = "resolved"       # Issue resolved
    TIMED_OUT = "timed_out"     # SLA expired
    ESCALATED = "escalated"     # Escalated to manager
}
```

## HH.4 Handoff Data Model

```python
class HumanHandoff:
    id: UUID
    conversation_id: UUID
    patient_id: UUID
    clinic_id: UUID
    reason: str
    urgency: str  # low, medium, high, critical
    context: dict  # Full conversation context
    ai_summary: str  # AI-generated summary for staff
    assigned_to: Optional[UUID]  # Staff member
    assigned_at: Optional[datetime]
    state: str
    sla_deadline: datetime
    resolved_at: Optional[datetime]
    resolution: Optional[str]
    created_at: datetime
```

## HH.5 Handoff Flow

```
PATIENT MESSAGE
       │
       ▼
  AI PROCESSING
       │
       ▼
  HANDOFF DETECTED
       │
       ▼
┌──────────────────┐
│ Create Handoff   │
│ - Full context   │
│ - AI summary     │
│ - Conversation   │
│   history        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Notify Staff     │
│ - Dashboard alert│
│ - Push notification│
│ - SMS (critical) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ AI Message to    │
│ Patient          │
│ "I've let our    │
│  team know..."   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Staff Takes Over │
│ - Sees full      │
│   context        │
│ - Can respond    │
│ - Can resolve    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Resolution       │
│ - Staff marks    │
│   resolved       │
│ - AI can resume  │
│   if appropriate │
└──────────────────┘
```

## HH.6 Staff Dashboard: Handoff Queue

```
┌──────────────────────────────────────────────────────┐
│              HANDOFF QUEUE                           │
├──────────────────────────────────────────────────────┤
│  🔴 CRITICAL (2)                                    │
│  ┌────────────────────────────────────────────────┐ │
│  │ 🚨 EMERGENCY: Sarah Johnson                     │ │
│  │ "My face is swelling and I can't breathe"       │ │
│  │ 2 min ago | Assigned: None                      │ │
│  │ [Take] [View]                                   │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  🟠 HIGH (3)                                        │
│  ┌────────────────────────────────────────────────┐ │
│  │ 😤 FRUSTRATED: Mike Chen                         │ │
│  │ "I've been waiting 45 minutes!"                 │ │
│  │ 5 min ago | Assigned: Jennifer S.               │ │
│  │ [View]                                          │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  🟡 MEDIUM (7)                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ ❓ QUESTION: Emily Davis                         │ │
│  │ "What does my insurance cover for Invisalign?"  │ │
│  │ 15 min ago | Assigned: None                     │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## HH.7 Handoff AI Summary

When creating a handoff, AI generates a summary for staff:

```python
class HandoffSummaryGenerator:
    async def generate(self, conversation: Conversation) -> str:
        return f"""
PATIENT: {conversation.patient.first_name} {conversation.patient.last_name}
PHONE: {conversation.patient.phone}
REASON: {handoff.reason}

CONVERSATION SUMMARY:
{self.summarize_conversation(conversation.messages)}

KEY DETAILS:
- Intent: {conversation.intent}
- Urgency: {conversation.urgency}
- Appointment status: {conversation.appointment_status}
- Prior appointments: {conversation.prior_visits}

RECOMMENDED ACTION:
{self.recommend_action(conversation)}

AI ATTEMPTED:
{self.list_ai_actions(conversation)}

NEEDS HUMAN BECAUSE:
{handoff.reason}
""".strip()
```

## HH.8 SLA Configuration

```python
HANDOFF_SLA = {
    "critical": timedelta(minutes=2),
    "high": timedelta(minutes=10),
    "medium": timedelta(minutes=30),
    "low": timedelta(minutes=60)
}

class HandoffSLAMonitor:
    async def check_sla(self):
        """Check for SLA violations."""
        overdue = await self.db.query("""
            SELECT * FROM human_handoffs
            WHERE state IN ('pending', 'assigned', 'in_progress')
            AND sla_deadline < NOW()
            AND resolved_at IS NULL
        """)

        for handoff in overdue:
            await self.escalate(handoff)
            await self.notify_manager(handoff)
```

## HH.9 Resume After Handoff

```python
class HandoffResume:
    """Handle resuming AI conversation after handoff."""

    async def resume(self, handoff_id: str):
        handoff = await self.get_handoff(handoff_id)

        if handoff.resolution == "resolved_by_staff":
            # Staff resolved the issue
            # AI can offer follow-up
            await self.send_message(
                conversation_id=handoff.conversation_id,
                content="Is there anything else I can help you with?",
                sender="ai"
            )

        elif handoff.resolution == "patient_handled_elsewhere":
            # Patient resolved on their own
            # Mark conversation as complete
            await self.end_conversation(handoff.conversation_id)

        elif handoff.resolution == "requires_follow_up":
            # Staff wants AI to follow up with specific info
            await self.send_message(
                conversation_id=handoff.conversation_id,
                content=handoff.follow_up_message,
                sender="ai"
            )
```

## HH.10 Staff Notifications

```python
class StaffNotificationService:
    """Notify staff of handoffs."""

    async def notify(self, handoff: HumanHandoff):
        """Send notifications based on urgency."""

        if handoff.urgency == "critical":
            # SMS + Push + Dashboard
            await self.sms.send(
                to=on_call_staff.phone,
                content=f"URGENT: {handoff.reason}"
            )
            await self.push.send(
                user_id=on_call_staff.id,
                title="Emergency Handoff",
                body=handoff.reason
            )

        elif handoff.urgency == "high":
            # Push + Dashboard
            await self.push.send(...)

        # Always update dashboard
        await self.dashboard.add_to_queue(handoff)
```

## HH.11 Escalation Chain

```
Level 1: Front Desk Staff
  ↓ (no response in SLA)
Level 2: Office Manager
  ↓ (no response in SLA)
Level 3: Practice Owner
  ↓ (no response in SLA)
Level 4: HeyJarvis Support (for platform issues)
```

```python
class EscalationChain:
    async def escalate(self, handoff: HumanHandoff):
        chain = await self.get_escalation_chain(handoff.clinic_id)

        for level in chain:
            if await self.notify(level.user, handoff):
                handoff.escalated_to = level.user.id
                handoff.escalated_at = datetime.now()
                await handoff.save()
                break

            # If no response from this level, move to next
            if datetime.now() > handoff.sla_deadline:
                continue
```
