# Use Cases — Functional Use Case Catalog

## UC.01: Abandoned Lead — Website Form

**Primary Actor:** Potential Patient
**Preconditions:**
- Patient submitted a lead form on the practice website
- No appointment was booked
- 1-24 hours have passed

**Main Flow:**
1. Lead form submission triggers `lead.created` event
2. System creates `RECAPTURE_OPPORTUNITY` (category: `lead`, sub: `web_form_abandoned`)
3. Eligibility engine evaluates opportunity
4. If eligible: Campaign engine queues first outreach
5. System sends personalized SMS:
   "Hi [First Name]! You recently reached out to [Clinic] about [Service]. I'm here to help with any questions or to get you scheduled. Reply YES for availability or call [Phone]."
6. Patient receives message
7. If patient replies: Conversation enters AI agent
8. AI classifies intent, offers booking
9. If patient books: Opportunity marked `COMPLETED`, revenue attributed
10. If patient declines/opts out: Opportunity marked appropriately

**Alternative Flows:**
- Patient doesn't respond → wait, send second message (24h later)
- Patient opts out → add to suppression list, end campaign
- AI detects safety concern → create handoff
- Patient asks question AI can't answer → handoff to staff

**Success Criteria:** Patient books appointment within 7 days

---

## UC.02: Abandoned Booking Flow

**Primary Actor:** Potential Patient
**Preconditions:**
- Patient started booking on the website or via chat
- Selected a service and time slot
- Did not complete confirmation
- 30 minutes - 4 hours have passed

**Main Flow:**
1. Booking system triggers `booking.abandoned` event
2. System creates opportunity (category: `booking`, sub: `flow_abandoned`)
3. System checks if slot is still available
4. If slot available: Send message:
   "Hi [First Name]! I noticed you started booking a [Service] appointment with us. The [Time] slot you selected is still available. Would you like me to complete the booking?"
5. If patient confirms: System books through PMS
6. Send confirmation

**Alternative Flows:**
- Slot no longer available → offer alternative slots
- Patient wants different time → check new availability
- Patient has questions → AI handles or handoff

---

## UC.03: Cancellation Recovery

**Primary Actor:** Patient (cancelled appointment)
**Preconditions:**
- Patient had a scheduled appointment
- Patient cancelled (with or without reason)
- Appointment has not been rescheduled

**Main Flow:**
1. PMS triggers `appointment.cancelled` event
2. System creates opportunity (category: `cancellation`)
3. Determine cancellation reason from PMS data or AI follow-up
4. Select appropriate message based on reason:
   - Schedule conflict → offer alternative times
   - Price concern → discuss financial options
   - Insurance → offer to verify coverage
   - Anxiety → offer pre-visit consultation
   - No reason → general reschedule offer
5. If reason unknown: Send gentle reschedule offer

**Alternative Flows:**
- Patient cancels via text → handle in conversation
- Patient requests specific time → check availability
- Patient says they'll call back → don't push, note for follow-up

---

## UC.04: No-Show Recovery

**Primary Actor:** Patient (no-showed)
**Preconditions:**
- Patient had a scheduled appointment
- Patient did not show and did not cancel
- 2-24 hours after appointment time

**Main Flow:**
1. PMS triggers `appointment.no_show` event
2. System creates opportunity (category: `no_show`)
3. Check if this is first or repeat no-show
4. First no-show: Send gentle message:
   "Hi [First Name], we missed you today for your [Service] appointment. We hope everything is okay. Would you like to reschedule?"
5. Repeat no-show: More careful approach
   - Staff task to call (not SMS)
   - Check if there are accessibility/transportation issues

**Alternative Flows:**
- Patient replies with explanation → handle appropriately
- Patient reschedules → mark success
- Patient unreachable → try alternative channel
- Staff notes special circumstance → suppress further outreach

---

## UC.05: Treatment Plan Not Scheduled

**Primary Actor:** Patient (accepted treatment but didn't schedule)
**Preconditions:**
- Dentist created treatment plan
- Patient accepted the treatment plan
- No appointment was scheduled for treatment
- 1-7 days after plan acceptance

**Main Flow:**
1. PMS triggers `treatment_plan.unscheduled` event
2. System creates opportunity (category: `treatment`, sub: `unscheduled`)
3. AI sends personalized message:
   "Hi [First Name], great news that you're moving forward with [Treatment]! We'd love to get you scheduled. [Provider] has availability on [Dates]. Would you like to book?"
4. If patient wants to schedule: Check availability, book

**Alternative Flows:**
- Patient has questions about treatment → AI answers or hands off
- Patient wants to discuss cost → AI explains financial options or hands off
- Patient isn't ready → schedule a follow-up reminder

---

## UC.06: Overdue Recall

**Primary Actor:** Patient (overdue for routine visit)
**Preconditions:**
- Patient's last hygiene visit was >6 months ago (configurable)
- Patient is not already scheduled
- Patient hasn't opted out

**Main Flow:**
1. System runs daily recall sweep
2. Identifies overdue patients
3. Creates opportunity (category: `recall`, sub: `hygiene_overdue`)
4. Sends message:
   "Hi [First Name], it's been about [X] months since your last cleaning at [Clinic]. We'd love to see you! Reply YES to check availability."
5. If patient responds: Schedule appointment
6. If no response: Send second message with different timing

**Alternative Flows:**
- Patient recently visited elsewhere → note, suppress
- Patient has special needs → ensure appropriate provider available
- Patient requests specific hygienist → honor preference

---

## UC.07: Inactive Patient Reactivation

**Primary Actor:** Former Active Patient
**Preconditions:**
- Patient was active at the practice (had appointments)
- No visit in >12 months
- No recent contact
- Not opted out

**Main Flow:**
1. System identifies inactive patients nightly
2. Creates opportunity (category: `inactive`)
3. Sends warm re-engagement message:
   "Hi [First Name], it's been a while since we've seen you at [Clinic]! We miss you. Is there anything we can help with? Reply or call us at [Phone]."
4. Wait for response
5. If interested: Offer checkup appointment
6. If not interested: Respect decision, note

**Alternative Flows:**
- Patient moved → update record, suppress
- Patient unhappy → escalate to staff
- Patient wants to return → prioritize scheduling

---

## UC.08: After-Hours Lead

**Primary Actor:** Potential Patient
**Preconditions:**
- Patient submitted lead form or started chat outside business hours
- Practice is closed

**Main Flow:**
1. Lead triggers `lead.created` event
2. System detects after-hours
3. Creates opportunity (category: `operational`, sub: `after_hours`)
4. Sends immediate automated response:
   "Thanks for reaching out to [Clinic]! We're closed right now but we'll get back to you as soon as we open at [Business Hours]. For urgent needs, call [Emergency Number]."
5. First thing next business morning: Staff or AI follows up

**Alternative Flows:**
- Patient message indicates emergency → safety escalation immediately
- Patient asks to book → AI books for next available (if allowed)
- Chat is live → AI handles in real-time

---

## UC.09: Missed Call

**Primary Actor:** Patient (called, no answer)
**Preconditions:**
- Patient called the practice
- Call went to voicemail or wasn't answered
- Voicemail system didn't capture number/need (or was not set up)

**Main Flow:**
1. Call system triggers `call.missed` event
2. System creates opportunity (category: `operational`, sub: `missed_call`)
3. System sends SMS:
   "Hi, this is [Clinic]. We missed your call. How can we help? Call us back at [Phone] or reply to this message."
4. If patient replies: Handle in conversation
5. If no response: Follow up with second message

**Alternative Flows:**
- Caller ID available → personalize message
- Voicemail captured request → address specific need
- Repeated missed calls → staff task to investigate

---

## UC.10: Insurance Verification Follow-Up

**Primary Actor:** Patient (needs insurance verification)
**Preconditions:**
- Patient asked about insurance coverage
- System couldn't verify real-time
- Patient hasn't followed up

**Main Flow:**
1. System triggers `insurance.verification_pending` event
2. Creates opportunity (category: `lead`, sub: `insurance_question`)
3. When verification completes: AI notifies patient
4. If verification fails: AI explains and offers alternatives

**Alternative Flows:**
- Insurance rejected → discuss payment options
- Partial coverage → explain patient responsibility
- Patient never completed insurance form → staff follows up

---

## UC.11: Patient Asks to Cancel

**Primary Actor:** Patient
**Preconditions:**
- Patient has a future appointment
- Patient contacts clinic to cancel

**Main Flow:**
1. Patient message triggers conversation
2. AI classifies intent: CANCEL
3. AI confirms: "I can help you cancel your [Service] appointment on [Date/Time]. Can I ask the reason so we can help better in the future?"
4. Patient provides reason (optional)
5. AI cancels through PMS
6. AI offers: "Would you like to reschedule for another time?"
7. If yes → offer available slots
8. If no → confirm cancellation, note reason

**Alternative Flows:**
- AI uncertain about intent → handoff to staff
- Complex cancellation (multiple appointments) → handoff
- Patient angry → immediate handoff

---

## UC.12: Patient Requests Human

**Primary Actor:** Patient
**Preconditions:**
- Patient is in AI conversation
- Patient says "human", "staff", "real person", etc.

**Main Flow:**
1. AI detects handoff intent
2. AI: "Of course! Let me connect you with our team. One moment please."
3. Creates `HUMAN_HANDOFF` record with full conversation context
4. Notifies available staff via dashboard/push notification
5. AI sends: "I've let our team know. Someone will be with you shortly. In the meantime, is there anything else I can help with while you wait?"
6. Staff takes over conversation
7. When resolved: Staff marks handoff resolved

**Alternative Flows:**
- No staff available → "Our team is currently busy. We'll respond within [Time]. For emergencies, call [Number]"
- Patient has urgent need → safety escalation + immediate notification
