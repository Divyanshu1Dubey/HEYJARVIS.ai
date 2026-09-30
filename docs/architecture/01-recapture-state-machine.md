# Patient Recapture State Machine
## Complete State & Transition Specification

**Document:** 01 of 20  
**Purpose:** Defines every possible patient state, the events that trigger transitions, and the rules governing valid state changes.

---

## 1. Design Philosophy

The state machine is the single source of truth for patient lifecycle. Every component — the recapture engine, the AI, the campaign runner, the dashboard — reads and writes state through this machine.

**Rules:**
- No component may transition a patient to a state that is not a valid transition from the current state.
- All transitions emit an event.
- All transitions are auditable.
- Some transitions require human confirmation.
- Some transitions are irreversible.

---

## 2. State Categories

States are grouped into six categories:

| Category | States | Description |
|----------|--------|-------------|
| **Acquisition** | `NEW_LEAD`, `CONTACTED`, `ENGAGED`, `QUALIFIED`, `DISQUALIFIED` | Patient is being acquired |
| **Booking** | `BOOKING_PENDING`, `BOOKED`, `CONFIRMED`, `COMPLETED` | Patient has an appointment |
| **Failure** | `LEAD_ABANDONED`, `NO_RESPONSE`, `CANCELLED`, `NO_SHOW`, `RESCHEDULE_PENDING`, `TREATMENT_UNSCHEDULED` | Something went wrong |
| **Recall** | `RECALL_DUE`, `INACTIVE`, `LONG_TERM_INACTIVE` | Patient needs re-engagement |
| **Terminal** | `OPTED_OUT`, `DO_NOT_CONTACT`, `DEACTIVATED` | Patient cannot be contacted |
| **Process** | `HUMAN_HANDOFF`, `SAFETY_ESCALATION`, `CAMPAIGN_ACTIVE`, `RECAPTURE_FAILED`, `RECAPTURE_SUCCESS` | System processing states |

---

## 3. Complete State Definitions

### 3.1 Acquisition States

#### `NEW_LEAD`
- **Definition:** Patient has expressed interest but has not been contacted.
- **Entry events:** `lead.created`, `patient.registered`, `web_chat.started`
- **Recapture eligible:** Yes
- **Allowed outbound channels:** SMS (if consented), Email (if consented)
- **AI action:** None — wait for contact
- **Staff action:** None — automated outreach begins

#### `CONTACTED`
- **Definition:** Patient has been contacted at least once.
- **Entry:** `message.sent` with successful delivery
- **Recapture eligible:** Yes
- **Allowed outbound channels:** Any consented channel
- **AI action:** Can engage in conversation

#### `ENGAGED`
- **Definition:** Patient has responded or shown engagement signals.
- **Entry:** `message.replied`, `conversation.started`
- **Recapture eligible:** Yes — high intent
- **AI action:** Full conversation handling
- **Staff action:** Monitor for handoff triggers

#### `QUALIFIED`
- **Definition:** Patient has confirmed intent to book or proceed with treatment.
- **Entry:** AI classification + positive response signal
- **Recapture eligible:** Yes — high priority
- **AI action:** Facilitate booking
- **Staff action:** Monitor, ready to assist

#### `DISQUALIFIED`
- **Definition:** Patient is not a viable candidate for the current service or is out of service area.
- **Entry:** Staff decision or AI classification (e.g., "not interested permanently")
- **Recapture eligible:** No — suppress from campaigns
- **Can transition to:** `DO_NOT_CONTACT` if patient requests

### 3.2 Booking States

#### `BOOKING_PENDING`
- **Definition:** Patient is in the process of booking.
- **Entry:** `appointment.offered` and patient is considering
- **Recapture eligible:** Yes — at risk of abandonment
- **AI action:** Assist with booking, provide information
- **Timeout:** Transitions to `LEAD_ABANDONED` after 24h without confirmation

#### `BOOKED`
- **Definition:** Appointment has been scheduled.
- **Entry:** `appointment.booked`
- **Recapture eligible:** No — not a recapture target
- **Next states:** `CONFIRMED` (time passes) or `CANCELLED` (cancellation event)

#### `CONFIRMED`
- **Definition:** Appointment is confirmed.
- **Entry:** `appointment.confirmed`
- **Recapture eligible:** No
- **Next states:** `COMPLETED` (visit happens) or `CANCELLED` (cancellation event) or `NO_SHOW` (patient doesn't arrive)

#### `COMPLETED`
- **Definition:** Appointment was completed successfully.
- **Entry:** `appointment.completed`
- **Recapture eligible:** Not for this appointment — but triggers recall scheduling
- **Next states:** `RECALL_DUE` (when next recall is due) or `INACTIVE` (patient stops coming)

### 3.3 Failure States

#### `LEAD_ABANDONED`
- **Definition:** Patient started a journey but abandoned it without converting.
- **Entry:** `conversation.abandoned`, `booking_flow.abandoned`, lead timeout
- **Recapture eligible:** Yes — primary recapture target
- **Allowed channels:** Different from the abandoned channel (if possible)
- **AI action:** Generate recovery message
- **Timeout:** Not applicable — waits for recapture attempt

#### `NO_RESPONSE`
- **Definition:** Patient was contacted but never responded.
- **Entry:** After 48h with no reply to outreach
- **Recapture eligible:** Yes — may need different channel or message
- **AI action:** Do not continue same channel — escalate or switch
- **Timeout:** After 3 attempts across channels, transitions to `RECAPTURE_FAILED`

#### `CANCELLED`
- **Definition:** Patient cancelled an appointment.
- **Entry:** `appointment.cancelled`
- **Recapture eligible:** Yes — cancellation recapture
- **Cancellation reason is REQUIRED:** If reason is unknown, use general message
- **AI action:** Generate reason-specific recovery message
- **Next states:** `RESCHEDULE_PENDING` (patient responds positively) or `RECAPTURE_FAILED` (no response)

#### `RESCHEDULE_PENDING`
- **Definition:** Patient agreed to reschedule but hasn't picked a time yet.
- **Entry:** Positive response to cancellation recapture
- **Recapture eligible:** Yes — at risk of further abandonment
- **AI action:** Help select new time
- **Timeout:** 48h without selecting time → back to `CANCELLED` for retry

#### `NO_SHOW`
- **Definition:** Patient missed a confirmed appointment without cancelling.
- **Entry:** `appointment.no_show`
- **Recapture eligible:** Yes — no-show recovery
- **Subtype tracking:** First no-show vs. repeat no-show (different messaging)
- **Next states:** `CANCELLED` (if patient reschedules) or stays `NO_SHOW` (if not)

#### `TREATMENT_UNSCHEDULED`
- **Definition:** Patient has accepted or been presented with a treatment plan but no treatment appointment is scheduled.
- **Entry:** `treatment_plan.accepted` without scheduling within 14 days
- **Recapture eligible:** Yes — high-value target
- **AI action:** Address barriers (cost, fear, timing)
- **Next states:** `BOOKED` (treatment scheduled) or `CANCELLED` (patient declines)

### 3.4 Recall States

#### `RECALL_DUE`
- **Definition:** Patient is overdue for a routine recall appointment.
- **Entry:** Scheduled recall trigger (e.g., 6 months since last hygiene)
- **Recapture eligible:** Yes — recall campaign
- **AI action:** Gentle reminder, not urgent
- **Next states:** `BOOKED` (schedules recall) or `INACTIVE` (ignores)

#### `INACTIVE`
- **Definition:** Patient has not visited in 12+ months but has history.
- **Entry:** `patient.inactive` trigger
- **Recapture eligible:** Yes — reactivation campaign
- **AI action:** Welcome-back message, update contact info if needed
- **Next states:** `ENGAGED` (responds) or `LONG_TERM_INACTIVE` (no response after extended campaign)

#### `LONG_TERM_INACTIVE`
- **Definition:** Patient has not visited in 24+ months or has explicitly gone inactive.
- **Entry:** Timeout from `INACTIVE` or patient request
- **Recapture eligible:** Limited — may need fresh consent
- **AI action:** Minimal — verify contact info and interest before heavy outreach
- **Next states:** `INACTIVE` (re-engaged) or `OPTED_OUT` / `DO_NOT_CONTACT`

### 3.5 Terminal States

#### `OPTED_OUT`
- **Definition:** Patient explicitly requested to stop communications.
- **Entry:** `patient.opted_out` (STOP keyword, patient request)
- **Recapture eligible:** NO — hard stop
- **AI action:** None — do not engage
- **Reversible:** No — requires explicit opt-in from patient (new consent record)

#### `DO_NOT_CONTACT`
- **Definition:** Patient is on the do-not-contact list (staff decision or patient request).
- **Entry:** Staff action or patient request
- **Recapture eligible:** NO
- **Reversible:** Only by staff with appropriate permissions

#### `DEACTIVATED`
- **Definition:** Patient record is deactivated (deceased, moved away, etc.)
- **Entry:** Staff action
- **Recapture eligible:** NO
- **Reversible:** No

### 3.6 Process States

#### `HUMAN_HANDOFF`
- **Definition:** Conversation has been escalated to human staff.
- **Entry:** Any AI-detected escalation trigger
- **Recapture eligible:** Depends on outcome of human interaction
- **AI action:** None — stop generating
- **Staff action:** Take over conversation
- **Timeout:** 24h → if no staff action, send reminder to staff queue

#### `SAFETY_ESCALATION`
- **Definition:** A safety concern was detected requiring immediate human attention.
- **Entry:** Emergency keywords, medical advice requests
- **Recapture eligible:** After safety is addressed
- **AI action:** STOP — do not continue automated outreach
- **Staff action:** Immediate — call patient, assess urgency
- **Timeout:** 30 minutes for acknowledgment, 2 hours for resolution

#### `CAMPAIGN_ACTIVE`
- **Definition:** Patient is currently in an active outreach campaign.
- **Entry:** Campaign enrollment
- **Recapture eligible:** No — already being processed
- **AI action:** Track responses, adjust messaging
- **Next states:** Any terminal state based on outcome

#### `RECAPTURE_FAILED`
- **Definition:** All recapture attempts have been exhausted without success.
- **Entry:** Maximum attempts reached, or patient declined
- **Recapture eligible:** No — suppress for cooldown period (90 days)
- **Re-evaluation:** After 90 days, re-evaluate if patient circumstances may have changed
- **AI action:** None

#### `RECAPTURE_SUCCESS`
- **Definition:** Recapture attempt succeeded — patient booked or re-engaged.
- **Entry:** `appointment.booked` following recapture outreach
- **Recapture eligible:** No — transition to normal booking flow
- **Attribution:** Track revenue attribution to the recapture campaign

---

## 4. Complete Transition Matrix

The table below defines every valid state transition. Invalid transitions are rejected by the state machine.

| From | To | Trigger | Requires Human | Notes |
|------|----|---------|---------------|-------|
| `NEW_LEAD` | `CONTACTED` | `message.sent` + delivered | No | Automated outreach |
| `NEW_LEAD` | `ENGAGED` | `message.replied` | No | Patient responded |
| `NEW_LEAD` | `DISQUALIFIED` | Staff/AI decision | No | Not a viable lead |
| `NEW_LEAD` | `OPTED_OUT` | `patient.opted_out` | No | Hard stop |
| `NEW_LEAD` | `HUMAN_HANDOFF` | Complex inquiry | No | AI can't handle |
| `CONTACTED` | `ENGAGED` | `message.replied` | No | Patient engaged |
| `CONTACTED` | `NO_RESPONSE` | 48h timeout | No | No reply |
| `CONTACTED` | `LEAD_ABANDONED` | `conversation.abandoned` | No | Patient stopped responding |
| `CONTACTED` | `HUMAN_HANDOFF` | Escalation trigger | No | Complexity/confusion |
| `CONTACTED` | `OPTED_OUT` | `patient.opted_out` | No | |
| `ENGAGED` | `QUALIFIED` | Intent classified + positive signal | No | High intent detected |
| `ENGAGED` | `BOOKING_PENDING` | Appointment offered | No | Offer made |
| `ENGAGED` | `LEAD_ABANDONED` | `conversation.abandoned` | No | Ghosted |
| `ENGAGED` | `HUMAN_HANDOFF` | Request/complexity | No | |
| `ENGAGED` | `OPTED_OUT` | `patient.opted_out` | No | |
| `QUALIFIED` | `BOOKING_PENDING` | Slot offered | No | |
| `QUALIFIED` | `BOOKED` | `appointment.booked` | No | |
| `QUALIFIED` | `LEAD_ABANDONED` | Stopped responding | No | |
| `QUALIFIED` | `HUMAN_HANDOFF` | Complex treatment plan | No | |
| `BOOKING_PENDING` | `BOOKED` | Booking confirmed | No | |
| `BOOKING_PENDING` | `LEAD_ABANDONED` | 24h timeout | No | Booking abandoned |
| `BOOKING_PENDING` | `CANCELLED` | `appointment.cancelled` | No | Cancelled before booking |
| `BOOKING_PENDING` | `HUMAN_HANDOFF` | Conflict/unclear | No | |
| `BOOKED` | `CONFIRMED` | Time passes (24h before apt) | No | Auto-advance |
| `BOOKED` | `CANCELLED` | `appointment.cancelled` | No | Patient cancelled |
| `BOOKED` | `NO_SHOW` | `appointment.no_show` | No | Patient didn't show |
| `CONFIRMED` | `COMPLETED` | `appointment.completed` | No | Visit happened |
| `CONFIRMED` | `CANCELLED` | `appointment.cancelled` | No | Late cancellation |
| `CONFIRMED` | `NO_SHOW` | `appointment.no_show` | No | No-show |
| `LEAD_ABANDONED` | `CONTACTED` | Recapture campaign | No | Re-engagement |
| `LEAD_ABANDONED` | `ENGAGED` | Recapture + response | No | Re-engaged |
| `LEAD_ABANDONED` | `RECAPTURE_FAILED` | Max attempts | No | Give up |
| `LEAD_ABANDONED` | `OPTED_OUT` | `patient.opted_out` | No | |
| `NO_RESPONSE` | `CONTACTED` | Different channel attempt | No | Channel switch |
| `NO_RESPONSE` | `ENGAGED` | Response received | No | Late response |
| `NO_RESPONSE` | `RECAPTURE_FAILED` | Max attempts | No | |
| `CANCELLED` | `RESCHEDULE_PENDING` | Positive recapture response | No | Will reschedule |
| `CANCELLED` | `CONTACTED` | Recapture campaign | No | Try again |
| `CANCELLED` | `RECAPTURE_FAILED` | Max attempts | No | |
| `CANCELLED` | `OPTED_OUT` | `patient.opted_out` | No | |
| `CANCELLED` | `SAFETY_ESCALATION` | Emergency signal | YES | Immediate |
| `RESCHEDULE_PENDING` | `BOOKED` | New appointment booked | No | Success |
| `RESCHEDULE_PENDING` | `CANCELLED` | Timeout / patient cancels | No | Back to cancelled |
| `RESCHEDULE_PENDING` | `HUMAN_HANDOFF` | Staff needed | No | |
| `NO_SHOW` | `CANCELLED` | Patient reschedules | No | Recover as reschedule |
| `NO_SHOW` | `CONTACTED` | No-show recapture | No | Outreach |
| `NO_SHOW` | `ENGAGED` | Response | No | Recovered |
| `NO_SHOW` | `SAFETY_ESCALATION` | Emergency signal | YES | Immediate |
| `TREATMENT_UNSCHEDULED` | `BOOKED` | Treatment scheduled | No | Success |
| `TREATMENT_UNSCHEDULED` | `CONTACTED` | Treatment recapture | No | Outreach |
| `TREATMENT_UNSCHEDULED` | `CANCELLED` | Patient declines treatment | No | Treatment declined |
| `TREATMENT_UNSCHEDULED` | `HUMAN_HANDOFF` | Complex financial discussion | No | |
| `RECALL_DUE` | `BOOKED` | Recall appointment booked | No | Success |
| `RECALL_DUE` | `INACTIVE` | No response after campaign | No | Deepened inactivity |
| `RECALL_DUE` | `OPTED_OUT` | `patient.opted_out` | No | |
| `INACTIVE` | `ENGAGED` | Reactivation response | No | Welcome back |
| `INACTIVE` | `CONTACTED` | Reactivation campaign | No | Outreach |
| `INACTIVE` | `LONG_TERM_INACTIVE` | No response | No | Deepened |
| `INACTIVE` | `DO_NOT_CONTACT` | Staff decision | YES | Hard stop |
| `LONG_TERM_INACTIVE` | `INACTIVE` | Fresh contact/interest | No | Step back up |
| `LONG_TERM_INACTIVE` | `DO_NOT_CONTACT` | Staff decision | YES | Hard stop |
| Any | `HUMAN_HANDOFF` | Escalation trigger | No | AI hands off |
| Any | `SAFETY_ESCALATION` | Safety trigger | YES | Emergency |
| Any | `OPTED_OUT` | STOP keyword, patient request | No | Hard stop |
| Any | `DO_NOT_CONTACT` | Staff decision | YES | Hard stop |
| `HUMAN_HANDOFF` | Previous state | Staff resolves | No | Resume |
| `HUMAN_HANDOFF` | `OPTED_OUT` | Patient opts out during handoff | No | |
| `HUMAN_HANDOFF` | `BOOKED` | Staff books | YES | Human completed |
| `SAFETY_ESCALATION` | `HUMAN_HANDOFF` | Safety resolved, needs staff | No | |
| `SAFETY_ESCALATION` | `OPTED_OUT` | Patient opts out | No | |
| `RECAPTURE_FAILED` | `CONTACTED` | Re-evaluation (90-day cooldown) | No | Retry after cooldown |

### Invalid Transitions (Rejected)

| From | To | Reason |
|------|----|--------|
| `COMPLETED` → `BOOKING_PENDING` | Patient already had their appointment |
| `OPTED_OUT` → Any non-terminal | Hard stop — requires new consent |
| `DEACTIVATED` → Any | Record is closed |
| `NO_SHOW` → `CONFIRMED` | Must rebook, not confirm |
| `RECAPTURE_SUCCESS` → `LEAD_ABANDONED` | Already succeeded |
| `DO_NOT_CONTACT` → Any outreach state | Staff override only |

---

## 5. State Machine Implementation

### Core Rules

1. **Single writer:** Only the state machine service may modify patient state.
2. **Event emission:** Every state transition emits a typed event with the full transition context.
3. **Audit trail:** Every transition is logged with: timestamp, from_state, to_state, trigger_event, triggered_by (system/staff/AI), correlation_id.
4. **Concurrency:** State transitions use optimistic locking (version column) to prevent race conditions.
5. **Validation:** Before any transition, the engine validates that it is in the allowed transition matrix.

### Pseudocode

```python
class PatientStateMachine:
    ALLOWED_TRANSITIONS = {
        PatientState.NEW_LEAD: {
            PatientState.CONTACTED: [Trigger.OUTREACH_SENT],
            PatientState.ENGAGED: [Trigger.PATIENT_REPLIED],
            PatientState.DISQUALIFIED: [Trigger.STAFF_DECISION, Trigger.AI_DECISION],
            PatientState.OPTED_OUT: [Trigger.PATIENT_OPTED_OUT],
            PatientState.HUMAN_HANDOFF: [Trigger.ESCALATION],
        },
        # ... (full matrix from Section 4)
    }

    def transition(self, patient, to_state, trigger, context, triggered_by):
        if to_state not in self.ALLOWED_TRANSITIONS.get(patient.state, {}):
            raise InvalidTransition(
                f"Cannot transition from {patient.state} to {to_state}"
            )

        # Optimistic lock
        if context.get("expected_version") != patient.version:
            raise ConcurrentModification("Patient state was modified concurrently")

        # Emit event BEFORE state change (event sourcing pattern)
        event = Event(
            type=f"patient.transitioned",
            from_state=patient.state,
            to_state=to_state,
            trigger=trigger,
            context=context,
            triggered_by=triggered_by,
        )
        event_bus.publish(event)

        # Update state
        patient.state = to_state
        patient.version += 1
        patient.last_transition_at = datetime.utcnow()

        # Log audit entry
        audit_log.create(
            patient_id=patient.id,
            action="state_transition",
            from_state=from_state,
            to_state=to_state,
            trigger=trigger,
        )
```

---

## 6. State-Dependent Behavior

Each state determines what the system may and may not do:

| State | Can AI Message? | Can AI Call Tool? | Can AI Book? | Can AI Take Payment? |
|-------|----------------|-------------------|--------------|---------------------|
| `NEW_LEAD` | Yes (first contact) | Read-only | No | No |
| `CONTACTED` | Yes | Read-only | No | No |
| `ENGAGED` | Yes | Read-only | No | No |
| `QUALIFIED` | Yes | Read + availability | No (hold only) | No |
| `BOOKING_PENDING` | Yes | Read + hold | Hold only | No |
| `BOOKED` | Confirmations only | Read | No (cancel only with confirm) | No |
| `CONFIRMED` | Confirmations only | Read | No | No |
| `COMPLETED` | Post-visit only | Read | No | No |
| `LEAD_ABANDONED` | Yes (recapture) | Read | No | No |
| `NO_RESPONSE` | Yes (retry) | Read | No | No |
| `CANCELLED` | Yes (reschedule) | Read + availability | No | No |
| `RESCHEDULE_PENDING` | Yes (facilitate) | Read + availability | Yes (with confirmation) | No |
| `NO_SHOW` | Yes (recovery) | Read | No | No |
| `TREATMENT_UNSCHEDULED` | Yes (encourage) | Read + availability | No | No |
| `RECALL_DUE` | Yes (reminder) | Read + availability | Yes (with confirmation) | No |
| `INACTIVE` | Yes (reactivation) | Read | No | No |
| `LONG_TERM_INACTIVE` | Yes (limited) | Read | No | No |
| `OPTED_OUT` | NO | NO | NO | NO |
| `DO_NOT_CONTACT` | NO | NO | NO | NO |
| `DEACTIVATED` | NO | NO | NO | NO |
| `HUMAN_HANDOFF` | NO (staff owns) | Read-only | Staff only | Staff only |
| `SAFETY_ESCALATION` | NO | Read-only | Staff only | Staff only |
| `CAMPAIGN_ACTIVE` | Yes (within campaign) | Read | No | No |
| `RECAPTURE_FAILED` | No (cooldown) | Read | No | No |
| `RECAPTURE_SUCCESS` | No (normal flow) | Read | Normal booking | Normal |

---

## 7. Recapture Eligibility by State

Not every patient in a "failure" state should be recaptured. The decision engine (Doc 3) makes the final call, but the state machine defines the baseline eligibility:

| State | Recapture Eligible | Default Priority | Max Attempts |
|-------|-------------------|-----------------|--------------|
| `LEAD_ABANDONED` | Yes | Medium | 3 |
| `NO_RESPONSE` | Yes | Medium | 2 |
| `CANCELLED` | Yes | High | 3 |
| `NO_SHOW` | Yes | High | 2 |
| `TREATMENT_UNSCHEDULED` | Yes | High | 4 |
| `RESCHEDULE_PENDING` | Yes | High | 3 |
| `RECALL_DUE` | Yes | Medium | 2 |
| `INACTIVE` | Yes | Low | 2 |
| `LONG_TERM_INACTIVE` | Limited | Low | 1 |
| `OPTED_OUT` | NO | N/A | 0 |
| `DO_NOT_CONTACT` | NO | N/A | 0 |
| `DEACTIVATED` | NO | N/A | 0 |
| `RECAPTURE_FAILED` | After cooldown | Low | 1 |
| `HUMAN_HANDOFF` | Pending outcome | N/A | 0 |
| `SAFETY_ESCALATION` | After resolution | N/A | 0 |
| `BOOKED` / `CONFIRMED` / `COMPLETED` | NO | N/A | 0 |
| `NEW_LEAD` / `CONTACTED` / `ENGAGED` / `QUALIFIED` | Already in acquisition flow | N/A | 0 |
