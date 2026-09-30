# State Machine — Complete Patient & Conversation State Model

## SM.1 Design Principles

1. Every entity has a well-defined set of states
2. Every state has defined valid transitions
3. Transitions are triggered by events
4. State transitions are logged and auditable
5. Invalid transitions are rejected with clear errors
6. State machines are deterministic

## SM.2 Patient State Machine

### States

```python
class PatientState(str, Enum):
    # New patient who hasn't had any contact
    NEW_LEAD = "new_lead"

    # Patient has been contacted
    CONTACTED = "contacted"

    # Patient responded positively
    ENGAGED = "engaged"

    # Patient qualified (intent understood, ready to book)
    QUALIFIED = "qualified"

    # Booking in progress
    BOOKING_PENDING = "booking_pending"

    # Appointment booked
    BOOKED = "booked"

    # Appointment confirmed
    CONFIRMED = "confirmed"

    # Appointment completed
    COMPLETED = "completed"

    # Patient declined/no action on lead
    LEAD_ABANDONED = "lead_abandoned"

    # Contacted, no response after all attempts
    NO_RESPONSE = "no_response"

    # Appointment cancelled
    CANCELLED = "cancelled"

    # Patient no-showed
    NO_SHOW = "no_show"

    # Reschedule in progress
    RESCHEDULE_PENDING = "reschedule_pending"

    # Treatment plan exists but no appointment
    TREATMENT_UNSCHEDULED = "treatment_unscheduled"

    # Recall is due
    RECALL_DUE = "recall_due"

    # Patient inactive (no visits)
    INACTIVE = "inactive"

    # Patient opted out
    OPTED_OUT = "opted_out"

    # Do not contact (staff set)
    DO_NOT_CONTACT = "do_not_contact"

    # Human handling conversation
    HUMAN_HANDOFF = "human_handoff"

    # Safety escalation
    SAFETY_ESCALATION = "safety_escalation"

    # Invalid/undeliverable contact
    INVALID_CONTACT = "invalid_contact"

    # Message delivery failed
    FAILED_DELIVERY = "failed_delivery"

    # Integration/system failure
    FAILED_INTEGRATION = "failed_integration"

    # Recapture failed (all attempts exhausted)
    RECAPTURE_FAILED = "recapture_failed"
```

### Valid Transitions

```python
VALID_TRANSITIONS = {
    PatientState.NEW_LEAD: [
        PatientState.CONTACTED,        # Outreach sent
        PatientState.OPTED_OUT,        # Patient opts out immediately
        PatientState.SUPPRESSED,       # Business rule suppresses
        PatientState.INVALID_CONTACT,  # Wrong contact info
    ],

    PatientState.CONTACTED: [
        PatientState.ENGAGED,          # Patient responds
        PatientState.NO_RESPONSE,      # All attempts exhausted
        PatientState.OPTED_OUT,        # Patient opts out
        PatientState.SAFETY_ESCALATION, # Safety concern
        PatientState.HUMAN_HANDOFF,    # Needs human
        PatientState.INVALID_CONTACT,  # Bounce/invalid
    ],

    PatientState.ENGAGED: [
        PatientState.QUALIFIED,        # Intent understood
        PatientState.HUMAN_HANDOFF,    # Needs human
        PatientState.SAFETY_ESCALATION, # Safety concern
        PatientState.DECLINED,         # Patient says no
        PatientState.NO_RESPONSE,      # Went silent
    ],

    PatientState.QUALIFIED: [
        PatientState.BOOKING_PENDING,  # Appointment offered
        PatientState.HUMAN_HANDOFF,    # Complex question
        PatientState.DECLINED,         # Patient declines
        PatientState.NO_RESPONSE,      # Went silent
    ],

    PatientState.BOOKING_PENDING: [
        PatientState.BOOKED,           # Patient confirms
        PatientState.LEAD_ABANDONED,   # Doesn't respond
        PatientState.DECLINED,         # Patient says no
        PatientState.HUMAN_HANDOFF,    # Complex booking issue
    ],

    PatientState.BOOKED: [
        PatientState.CONFIRMED,        # Confirmation sent
        PatientState.CANCELLED,        # Cancelled
        PatientState.NO_SHOW,          # No-showed
    ],

    PatientState.CONFIRMED: [
        PatientState.COMPLETED,        # Visit completed
        PatientState.CANCELLED,        # Cancelled before visit
        PatientState.NO_SHOW,          # Didn't show
    ],

    PatientState.COMPLETED: [
        PatientState.RECALL_DUE,       # Time for recall
        PatientState.INACTIVE,         # No return after long time
        PatientState.TREATMENT_UNSCHEDULED, # More treatment needed
    ],

    PatientState.CANCELLED: [
        PatientState.RESCHEDULE_PENDING, # Trying to reschedule
        PatientState.INACTIVE,           # No reschedule attempt
        PatientState.RECAPTURE_FAILED,   # Outreach failed
        PatientState.COMPLETED,          # Rescheduled and completed
    ],

    PatientState.NO_SHOW: [
        PatientState.RESCHEDULE_PENDING, # Trying to reschedule
        PatientState.INACTIVE,           # No action
        PatientState.RECAPTURE_FAILED,   # Outreach failed
        PatientState.COMPLETED,          # Rescheduled and completed
    ],

    PatientState.RESCHEDULE_PENDING: [
        PatientState.BOOKED,           # Rescheduled
        PatientState.INACTIVE,         # No response to reschedule
    ],

    PatientState.LEAD_ABANDONED: [
        PatientState.CONTACTED,        # Re-engagement campaign
        PatientState.INACTIVE,         # No re-engagement
        PatientState.OPTED_OUT,        # Opts out
    ],

    PatientState.NO_RESPONSE: [
        PatientState.CONTACTED,        # Retry campaign
        PatientState.INACTIVE,         # Give up
        PatientState.OPTED_OUT,        # Opts out during retry
    ],

    PatientState.TREATMENT_UNSCHEDULED: [
        PatientState.BOOKED,           # Scheduled treatment
        PatientState.QUALIFIED,        # Needs more info
        PatientState.DECLINED,         # Declined treatment
        PatientState.INACTIVE,         # No action
    ],

    PatientState.RECALL_DUE: [
        PatientState.CONTACTED,        # Recall outreach
        PatientState.INACTIVE,         # No response
        PatientState.OPTED_OUT,        # Opts out
        PatientState.COMPLETED,        # Came in for recall
    ],

    PatientState.INACTIVE: [
        PatientState.CONTACTED,        # Reactivation campaign
        PatientState.OPTED_OUT,        # Opts out
        PatientState.DO_NOT_CONTACT,   # Staff mark
        PatientState.INVALID_CONTACT,  # Contact info invalid
    ],

    PatientState.HUMAN_HANDOFF: [
        PatientState.ENGAGED,          # Handoff resolved, back to AI
        PatientState.CONTACTED,        # Staff contacted, continuing
        PatientState.COMPLETED,        # Issue resolved
        PatientState.OPTED_OUT,        # During handoff
    ],

    PatientState.SAFETY_ESCALATION: [
        PatientState.HUMAN_HANDOFF,    # Transferred to human
        PatientState.COMPLETED,        # Safety issue resolved
    ],

    # Terminal states (no outgoing transitions)
    PatientState.OPTED_OUT: [],
    PatientState.DO_NOT_CONTACT: [],
    PatientState.INVALID_CONTACT: [],
    PatientState.FAILED_DELIVERY: [],
    PatientState.FAILED_INTEGRATION: [],
    PatientState.RECAPTURE_FAILED: [],
}
```

### State Transition Handler

```python
class PatientStateMachine:
    async def transition(self, patient_id, from_state, to_state, event, actor):
        if to_state not in VALID_TRANSITIONS.get(from_state, []):
            raise InvalidStateTransition(
                f"Cannot transition from {from_state} to {to_state}"
            )

        async with transaction():
            # Update state
            await self.db.execute(
                "UPDATE patients SET state = :to_state WHERE id = :id",
                {"to_state": to_state, "id": patient_id}
            )

            # Log transition
            await self.db.execute(
                """INSERT INTO state_transitions
                   (patient_id, from_state, to_state, event, actor, timestamp)
                   VALUES (:pid, :from, :to, :event, :actor, NOW())""",
                {
                    "pid": patient_id,
                    "from": from_state,
                    "to": to_state,
                    "event": event,
                    "actor": actor
                }
            )

            # Trigger side effects
            await self.trigger_side_effects(to_state, patient_id, event)

        return to_state
```

## SM.3 Conversation State Machine

### States

```python
class ConversationState(str, Enum):
    INITIAL = "initial"                    # Created, no messages
    GREETING = "greeting"                  # AI sent greeting
    WAITING_FOR_PATIENT = "waiting"        # Waiting for patient response
    PROCESSING = "processing"              # AI processing response
    TOOL_CALL = "tool_call"                # AI calling a tool
    AWAITING_TOOL_RESULT = "awaiting_tool" # Waiting for tool response
    BOOKING = "booking"                    # In booking flow
    HANDOFF_PENDING = "handoff_pending"    # Handoff initiated
    HANDED_OFF = "handed_off"              # Staff now owns conversation
    ENDED = "ended"                        # Conversation complete
    ABANDONED = "abandoned"                # Patient abandoned
    TIMED_OUT = "timed_out"                # Session expired
```

### Transitions

```
INITIAL → GREETING: conversation.started
GREETING → WAITING_FOR_PATIENT: greeting_sent
WAITING_FOR_PATIENT → PROCESSING: message.received
PROCESSING → TOOL_CALL: tool_required
PROCESSING → WAITING_FOR_PATIENT: response_sent
PROCESSING → HANDOFF_PENDING: handoff_triggered
PROCESSING → ENDED: conversation_ended
TOOL_CALL → AWAITING_TOOL_RESULT: tool_invoked
AWAITING_TOOL_RESULT → PROCESSING: tool_result_received
AWAITING_TOOL_RESULT → HANDOFF_PENDING: tool_failed
BOOKING → WAITING_FOR_PATIENT: booking_offered
BOOKING → PROCESSING: booking_confirmed
BOOKING → HANDOFF_PENDING: booking_failed
HANDOFF_PENDING → HANDED_OFF: handoff_accepted
HANDED_OFF → ENDED: handoff_resolved
WAITING_FOR_PATIENT → TIMED_OUT: timeout_reached
TIMED_OUT → ENDED: cleanup
Any → ABANDONED: patient_disconnected
```

## SM.4 Opportunity State Machine

### States

```python
class OpportunityState(str, Enum):
    IDENTIFIED = "identified"            # Just detected
    PENDING_ELIGIBILITY = "pending"      # Waiting for eligibility check
    ELIGIBLE = "eligible"                # Passed eligibility
    SUPPRESSED = "suppressed"            # Blocked by rules
    QUEUED = "queued"                    # In campaign queue
    ACTIVE = "active"                    # Outreach in progress
    COMPLETED = "completed"              # Successfully recaptured
    DECLINED = "declined"                # Patient declined
    OPTED_OUT = "opted_out"              # Patient opted out during campaign
    FAILED = "failed"                    # All attempts exhausted
    EXPIRED = "expired"                  # Opportunity expired
    HANDOFF = "handoff"                  # Requires human intervention
```

## SM.5 Campaign Execution State Machine

### States

```python
class CampaignState(str, Enum):
    DRAFT = "draft"                  # Created, not active
    ACTIVE = "active"                # Running
    PAUSED = "paused"                # Temporarily paused
    COMPLETED = "completed"          # All opportunities processed
    CANCELLED = "cancelled"          # Cancelled by user
    ERROR = "error"                  # System error
```

### Attempt States

```python
class AttemptState(str, Enum):
    PENDING = "pending"              # Queued, not started
    RUNNING = "running"              # Currently executing
    SENT = "sent"                    # Message sent
    DELIVERED = "delivered"          # Delivered to patient
    FAILED = "failed"                # Delivery failed
    RESPONDED = "responded"          # Patient responded
    COMPLETED = "completed"          # Attempt cycle done
    STOPPED = "stopped"              # Stopped by condition
```

## SM.6 Integration State Machine

```python
class IntegrationState(str, Enum):
    CONFIGURED = "configured"        # Credentials set up
    CONNECTING = "connecting"        # Testing connection
    ACTIVE = "active"                # Connected and syncing
    DEGRADED = "degraded"            # Partial functionality
    ERROR = "error"                  # Connection error
    DISABLED = "disabled"            # Manually disabled
}
```

## SM.7 State Persistence

All state transitions are stored in `state_transitions` table:

```sql
CREATE TABLE state_transitions (
    id UUID PRIMARY KEY,
    entity_type VARCHAR(50),        -- 'patient', 'conversation', 'opportunity', 'campaign'
    entity_id UUID,
    from_state VARCHAR(50),
    to_state VARCHAR(50),
    event VARCHAR(100),
    actor VARCHAR(50),              -- 'ai', 'staff', 'system', 'patient'
    actor_id UUID,
    metadata JSONB,
    timestamp TIMESTAMP NOT NULL
);
```

This provides:
- Complete audit trail of every state change
- Ability to reconstruct patient journey
- Debugging capability
- Compliance evidence
