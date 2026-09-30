# Recapture Taxonomy — Complete Classification System

## RT.1 Taxonomy Overview

Every patient interaction failure can be classified. This taxonomy ensures:
1. Consistent classification across all clinics
2. Appropriate outreach strategies per category
3. Accurate analytics and attribution
4. Consistent rules and campaign selection

## RT.2 Master Taxonomy

```
RECAPTURE (root)
├── A. LEAD_RECAPTURE
│   ├── A1. web_form_abandoned
│   ├── A2. web_chat_abandoned
│   ├── A3. phone_lead_missed
│   ├── A4. service_inquiry_no_action
│   ├── A5. price_inquiry_no_action
│   ├── A6. availability_inquiry_no_action
│   ├── A7. insurance_inquiry_no_action
│   ├── A8. lead_form_no_booking
│   └── A9. after_hours_lead
│
├── B. BOOKING_RECAPTURE
│   ├── B1. booking_flow_abandoned
│   ├── B2. slot_offered_not_accepted
│   ├── B3. slot_selected_not_confirmed
│   ├── B4. patient_said_think_about_it
│   ├── B5. patient_said_call_back
│   ├── B6. stopped_responding
│   └── B7. booking_timeout
│
├── C. CANCELLATION_RECAPTURE
│   ├── C1. cancelled_schedule_conflict
│   ├── C2. cancelled_price_concern
│   ├── C3. cancelled_insurance_uncertainty
│   ├── C4. cancelled_fear_anxiety
│   ├── C5. cancelled_transportation
│   ├── C6. cancelled_timing
│   ├── C7. cancelled_no_explanation
│   └── C8. cancelled_no_show
│
├── D. NO_SHOW_RECAPTURE
│   ├── D1. no_show_first
│   ├── D2. no_show_repeat
│   ├── D3. no_show_unreachable
│   ├── D4. no_show_rescheduled
│   └── D5. no_show_no_action
│
├── E. TREATMENT_RECAPTURE
│   ├── E1. treatment_plan_unscheduled
│   ├── E2. treatment_accepted_not_scheduled
│   ├── E3. treatment_estimate_sent_no_response
│   ├── E4. treatment_partially_completed
│   ├── E5. multi_visit_stalled
│   ├── E6. crown_not_scheduled
│   ├── E7. implant_not_scheduled
│   ├── E8. root_canal_not_scheduled
│   ├── E9. orthodontic_not_scheduled
│   ├── E10. periodontal_not_scheduled
│   └── E11. cosmetic_not_scheduled
│
├── F. RECALL_REACTIVATION
│   ├── F1. recall_hygiene_overdue
│   ├── F2. recall_periodic_exam_overdue
│   ├── F3. patient_inactive
│   ├── F4. post_treatment_no_return
│   ├── F5. continuing_care_overdue
│   └── F6. long_term_inactive
│
├── G. POST_VISIT_OPPORTUNITY
│   ├── G1. follow_up_needed
│   ├── G2. treatment_continuation
│   ├── G3. review_request
│   └── G4. referral_opportunity
│
└── H. OPERATIONAL_MISSED
    ├── H1. missed_call
    ├── H2. after_hours_inquiry
    ├── H3. weekend_lead
    ├── H4. unresolved_contact_request
    └── H5. staff_task_incomplete
```

## RT.3 Detailed Category Definitions

### A. LEAD_RECAPTURE

**Trigger:** Patient expressed interest but never booked

**A1. web_form_abandoned**
- Definition: Patient submitted lead form on website but no booking followed
- Detection: `lead.created` event with no corresponding `appointment.booked` within 4 hours
- Typical value: $200-500
- Recommended channel: SMS (if consented)
- Recommended sequence: 3 messages over 5 days
- Stop conditions: Booked, replied no, opted out, handoff

**A2. web_chat_abandoned**
- Definition: Patient started chat conversation and disconnected without booking
- Detection: `conversation.abandoned` with no booking intent or completed booking
- Typical value: $150-400
- Recommended channel: SMS (continue chat if returns)
- Recommended sequence: Resume chat + SMS follow-up

**A3. phone_lead_missed**
- Definition: Patient called but wasn't answered (or went to unmonitored voicemail)
- Detection: `call.missed` event from telephony system
- Typical value: $300-800 (phone leads tend to be higher intent)
- Recommended channel: SMS callback
- Recommended sequence: Immediate SMS + staff task if no response

**A4. service_inquiry_no_action**
- Definition: Patient asked about a specific service but didn't proceed
- Detection: AI classifies intent as SERVICE_QUESTION, no subsequent booking within 48h
- Typical value: $200-1000 (depends on service)
- Recommended channel: SMS with service-specific information
- Recommended sequence: Info message → availability offer

**A5. price_inquiry_no_action**
- Definition: Patient asked about pricing but didn't book
- Detection: AI classifies intent as PRICING_QUESTION, no booking
- Typical value: $150-600
- Recommended channel: Email (pricing details) + SMS (nudge)
- Recommended sequence: Price transparency → financing options → booking offer

**A6. availability_inquiry_no_action**
- Definition: Patient asked about availability but didn't book
- Detection: AI classifies intent as AVAILABILITY_QUESTION
- Typical value: $200-500
- Recommended channel: SMS with specific time slots
- Recommended sequence: Specific slots → simplified booking

**A7. insurance_inquiry_no_action**
- Definition: Patient asked about insurance but didn't proceed
- Detection: AI classifies intent as INSURANCE_QUESTION
- Typical value: $300-1500 (insurance questions often precede high-value treatment)
- Recommended channel: SMS with verification update
- Recommended sequence: Verification update → coverage explanation → booking

**A8. lead_form_no_booking**
- Definition: Lead form submitted, contact attempted, no booking
- Detection: `lead.contacted` without `appointment.booked` within 7 days
- Typical value: $200-500
- Recommended channel: Multi-touch (SMS, email, call task)
- Recommended sequence: SMS → Email → Staff call task

**A9. after_hours_lead**
- Definition: Lead submitted during closed hours
- Detection: `lead.created` during non-business hours
- Typical value: $200-500
- Recommended channel: SMS (immediate acknowledgement) + Email
- Recommended sequence: Acknowledge (immediate) → Follow up next business morning

### B. BOOKING_RECAPTURE

**B1. booking_flow_abandoned**
- Definition: Patient started online booking and didn't complete
- Detection: `booking.started` without `booking.completed` within 1 hour
- Typical value: $150-400
- Recommended channel: SMS
- Recommended sequence: Resume flow reminder → Alternative offer

**B2. slot_offered_not_accepted**
- Definition: AI or staff offered specific time, patient didn't accept or respond
- Detection: `appointment.offered` without `appointment.booked` or response within 2 hours
- Typical value: $200-500
- Recommended channel: SMS
- Recommended sequence: Different time offer → General availability

**B3. slot_selected_not_confirmed**
- Definition: Patient selected a slot but confirmation step incomplete
- Detection: Booking system shows slot selected but not confirmed
- Typical value: $200-500
- Recommended channel: SMS with direct booking link
- Recommended sequence: Reminder + direct link → Alternative slots

**B4. patient_said_think_about_it**
- Definition: Patient explicitly said they need to think
- Detection: AI intent classification or staff note
- Typical value: $200-800 (often high-value treatment)
- Recommended channel: Email (detailed info) + delayed SMS
- Recommended sequence: Wait 3-5 days → Informational message → Check back

**B5. patient_said_call_back**
- Definition: Patient said they would call back
- Detection: AI intent classification or staff note
- Typical value: $200-500
- Recommended channel: SMS (reminder that we're here when they're ready)
- Recommended sequence: Wait 1-2 days → Gentle SMS reminder

**B6. stopped_responding**
- Definition: Patient was engaged in conversation but went silent
- Detection: No response within 24h of last AI message
- Typical value: Variable
- Recommended channel: Different channel or different message
- Recommended sequence: 1 follow-up with different approach → End

**B7. booking_timeout**
- Definition: Patient's held slot expired without confirmation
- Detection: `appointment_hold.expired` without booking
- Typical value: $200-500
- Recommended channel: SMS
- Recommended sequence: Apologize for hold expiring → Offer new availability

### C. CANCELLATION_RECAPTURE

**C1-C7:** Various cancellation reasons
- Each has tailored messaging
- Cancellation reason is key to recovery strategy
- Price → offer financing/insurance check
- Fear/anxiety → offer consultation/explanation
- Transportation → discuss telehealth or mobile services
- Timing → offer different times
- No explanation → general offer

**C8. cancelled_no_show** (also in D)
- Borderline between cancellation and no-show
- Patient cancelled at or after appointment time

### D. NO_SHOW_RECAPTURE

**D1. no_show_first**
- Definition: First no-show, no pattern
- Tone: Gentle, concerned
- Assumption: Something came up
- Message: "We missed you! Hope you're okay. Let's reschedule."

**D2. no_show_repeat**
- Definition: 2+ no-shows
- Tone: More careful
- Action: Consider phone call instead of SMS
- Consider: Is there an underlying issue?

**D3. no_show_unreachable**
- Definition: Contact attempts all failed
- Action: Mark record, try alternative contact method
- Stop: After all methods exhausted

**D4. no_show_rescheduled**
- Definition: Patient did reschedule after no-show
- State: COMPLETED (successful recapture)
- No further action needed

**D5. no_show_no_action**
- Definition: No-showed and didn't reschedule after all attempts
- State: RECAPTURE_FAILED
- Note for future recall

### E. TREATMENT_RECAPTURE

**E1. treatment_plan_unscheduled**
- Definition: Treatment plan exists, no appointment for treatment
- Typical value: $500-5000 (high value)
- Recommended approach: Multi-step, patient education, address concerns
- May require: Insurance verification, financial discussion

**E2-E11:** Specific treatment types
- Each may need specialized messaging
- Some require consent for specific procedures
- Treatment-specific FAQs may be relevant

### F. RECALL_REACTIVATION

**F1. recall_hygiene_overdue**
- Definition: 6+ months since last hygiene visit
- Frequency: Every 6 months (configurable)
- Message: Routine, warm reminder
- Not urgent

**F2. recall_periodic_exam_overdue**
- Definition: 12+ months since last exam
- Similar to hygiene recall

**F3. patient_inactive**
- Definition: 12+ months since any visit
- Higher effort to reactivate
- May need incentives

**F4-F6:** Various inactivity levels
- Longer inactive = more careful approach needed
- May need to update contact info

### G. POST_VISIT_OPPORTUNITY

**G1. follow_up_needed**
- Post-operative follow-up
- System or provider flags need for follow-up

**G2. treatment_continuation**
- Multi-visit treatment next step
- Ensure next appointment is scheduled

**G3. review_request**
- Post-visit review request
- Only if patient had positive experience
- Timing: 24-48h after visit

**G4. referral_opportunity**
- Satisfied patient, potential for referrals
- Timing: After positive outcome

### H. OPERATIONAL_MISSED

**H1. missed_call**
- Phone call not answered
- SMS callback

**H2. after_hours_inquiry**
- Contact during closed hours
- Immediate acknowledgement + next-day follow-up

**H3. weekend_lead**
- Weekend inquiry
- Monday follow-up

**H4. unresolved_contact_request**
- Patient requested contact but no follow-up occurred
- Staff task creation

**H5. staff_task_incomplete**
- Assigned task not completed
- Reassignment or escalation

## RT.4 Opportunity Lifecycle

```
DETECTED
  → Eligibility Check
  → PENDING (waiting for eligibility)
  → ELIGIBLE (can be contacted)
  → ACTIVE (outreach in progress)
  → SUCCESS (booked/recovered)
  → DECLINED (patient said no)
  → OPTED_OUT (patient opted out)
  → FAILED (all attempts exhausted)
  → SUPPRESSED (blocked by rules)
  → HANDOFF (requires human)
```

## RT.5 Opportunity Scoring

Each opportunity receives a score based on:
- Category weight (treatment recapture > lead recapture > recall)
- Urgency signal (emergency > routine)
- Patient history (repeat patient > new lead)
- Recency (more recent > older)
- Engagement history (previously engaged > never engaged)
- Treatment value
- Conversion probability (from ML model when available)

Score ranges: 0-100
- 80-100: High priority (immediate outreach)
- 50-79: Medium priority (standard queue)
- 0-49: Low priority (batch processing)
