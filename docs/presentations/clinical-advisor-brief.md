# Clinical Advisor Brief — Healthcare Safety & Compliance

## CA.1 Clinical Safety Principles

```
CLINICAL SAFETY BOUNDARIES

The HeyJarvis AI Patient Recapture system is NOT a clinical tool.
It is a communication and scheduling assistant.

What the AI CAN do:
  ✓ Schedule appointments
  ✓ Reschedule appointments
  ✓ Cancel appointments (with confirmation)
  ✓ Answer questions about:
    - Clinic hours
    - Services offered
    - Insurance accepted (general)
    - Location and directions
    - Appointment availability
  ✓ Collect basic patient information
  ✓ Follow up on missed appointments
  ✓ Send reminders and confirmations

What the AI CANNOT do:
  ✗ Diagnose dental conditions
  ✗ Prescribe medication
  ✗ Recommend specific treatments
  ✗ Assess clinical severity
  ✗ Provide medical advice
  ✗ Interpret symptoms
  ✗ Guarantee treatment outcomes
  ✗ Advise on pain management
  ✗ Comment on medical history
  ✗ Make clinical judgments
```

## CA.2 Emergency Detection Protocol

```
EMERGENCY KEYWORD DETECTION

Pattern Categories:

1. TRAUMA
   Keywords: broken, knocked out, fell, hit, avulsed, displaced
   Phrases: "tooth fell out", "tooth is loose", "broke my tooth"
   Action: SAFETY ESCALATION

2. BLEEDING
   Keywords: bleeding, blood, hemorrhage, won't stop bleeding
   Phrases: "bleeding won't stop", "gushing blood"
   Action: SAFETY ESCALATION

3. SWELLING
   Keywords: swelling, swollen, abscess, pus, infection
   Phrases: "my face is swollen", "gums are very swollen"
   Action: SAFETY ESCALATION

4. PAIN
   Keywords: severe pain, extreme pain, unbearable, throbbing
   Phrases: "pain is unbearable", "can't stop crying from pain"
   Action: URGENT - offer urgent appointment

5. BREATHING
   Keywords: can't breathe, difficulty breathing, choking
   Action: SAFETY ESCALATION + 911 guidance

6. FEVER / SYSTEMIC
   Keywords: fever, temperature, chills, spreading
   Phrases: "fever won't go down", "swelling is spreading"
   Action: SAFETY ESCALATION

Response Protocol:

Level 1: Emergency (Immediate)
  → "This sounds like it may need immediate attention.
     Please call 911 or go to the nearest emergency room.
     We can also call you back at [clinic phone]."

Level 2: Urgent (Same Day)
  → "It sounds like you need to be seen soon.
     We have an opening today at [time].
     Would you like me to book it?"

Level 3: Routine (Schedule)
  → "I understand. Let's get you scheduled.
     When would work best for you?"

Response MUST include:
  ✓ Clear statement that AI is not a dentist
  ✓ Clear next step (call, book, or escalate)
  ✓ Never minimize symptoms
  ✓ Never delay escalation
  ✓ Never provide treatment advice
```

## CA.3 Consent Management

```
CONSENT REQUIREMENTS

Before ANY patient communication:

1. SMS CONSENT
   Required: Express written consent
   Methods:
     - Signed form at office
     - Online form with e-signature
     - Verbal consent (documented by staff)
   Must include:
     - What messages will be sent
     - How often
     - How to opt out (STOP keyword)
     - That message/data rates may apply
   Storage: Consent record with timestamp, method, version

2. EMAIL CONSENT
   Required: Express consent
   Methods:
     - Signed form
     - Online opt-in
     - Checkbox during registration
   Must include:
     - Unsubscribe link in every email
     - Privacy policy link
     - Clear sender identification

3. VOICE CONSENT
   Required: Express written consent
   Methods:
     - Signed form
     - Recorded verbal consent
   Must include:
     - Type of calls
     - Pre-recorded message disclosure
     - Opt-out method
   TCPA requires:
     - Prior express written consent for autodialed calls
     - Clear disclosure of autodialed nature

Consent Verification:
  → Checked BEFORE every message send
  → Checked at policy engine level
  → Never bypassed
  → Consent revocation is immediate

Consent Revocation:
  → STOP keyword → immediate
  → Patient request → immediate
  → Staff action → immediate
  → Cannot be reversed without re-consent
```

## CA.4 Patient Communication Ethics

```
COMMUNICATION ETHICS

The AI MUST:
  ✓ Be transparent (disclose AI nature)
  ✓ Be respectful
  ✓ Be concise
  ✓ Be helpful
  ✓ Provide clear opt-out
  ✓ Honor communication preferences
  ✓ Use patient's preferred name
  ✓ Be culturally sensitive

The AI MUST NOT:
  ✗ Use manipulative urgency ("limited time offer!")
  ✗ Create false scarcity ("only 1 slot left!" unless true)
  ✗ Use fear-based tactics ("you'll lose your teeth!")
  ✗ Pressure patients
  ✗ Make medical claims
  ✗ Fabricate information
  ✗ Share information without consent
  ✗ Ignore patient requests
  ✗ Continue after opt-out

Tone Guidelines:

For Cancellation Recovery:
  ✓ "We missed you — would you like to reschedule?"
  ✗ "You MUST reschedule or you'll lose your spot!"

For No-Show:
  ✓ "Hope you're okay. Want to reschedule?"
  ✗ "You missed your appointment. When can you come in?"

For Treatment Follow-Up:
  ✓ "Dr. Smith recommended a crown. Want to discuss scheduling?"
  ✗ "You NEED a crown. Book now!"

For Recall:
  ✓ "It's been 6 months since your cleaning. Time for a checkup?"
  ✗ "You're overdue! Schedule immediately!"

For Emergency:
  ✓ "This sounds urgent. Can you call us at [number]?"
  ✗ "You have an emergency!"
```

## CA.5 Staff Escalation Protocol

```
WHEN TO ESCALATE TO HUMAN

Automatic Escalation (AI Detects):
  → Emergency keywords detected
  → Medical symptoms described
  → Patient requests human/dentist
  → Insurance dispute mentioned
  → Payment dispute mentioned
  → Legal threat mentioned
  → Repeated misunderstanding (3+ times)
  → Patient expresses anger/frustration
  → AI confidence below threshold
  → Integration failure during conversation
  → Patient asks about records/deletion

Staff-Initiated Escalation:
  → Staff sees handoff queue item
  → Staff reviews and assigns to self
  → Staff calls patient directly
  → Staff marks as resolved

Escalation Response SLA:
  Critical (emergency): < 30 minutes
  High (medical): < 2 hours
  Medium (routine): < 24 hours
  Low (administrative): < 48 hours

Handoff Process:
  1. AI creates handoff record
  2. Handoff queued in staff dashboard
  3. Staff notified (SMS/email/push)
  4. Staff reviews conversation context
  5. Staff takes over (phone or chat)
  6. Staff marks resolved with notes
  7. Conversation closed or resumed
```

## CA.6 Data Governance

```
PATIENT DATA GOVERNANCE

Data Collection:
  ✓ Only necessary data collected
  ✓ Patient informed of collection
  ✓ Consent obtained
  ✓ Data minimization principle

Data Access:
  ✓ Role-based access
  ✓ Least privilege
  ✓ Audit trail for all access
  ✓ No bulk data exports without approval

Data Retention:
  ✓ Defined retention periods
  ✓ Automatic deletion after period
  ✓ Patient can request deletion
  ✓ Deletion is permanent and verified

Data Sharing:
  ✓ Only with patient consent
  ✓ Only with signed BAA
  ✓ Minimum necessary principle
  ✓ Audit trail for all sharing

Patient Rights (HIPAA):
  ✓ Right to access records
  ✓ Right to request amendment
  ✓ Right to accounting of disclosures
  ✓ Right to request restrictions
  ✓ Right to confidential communications
  ✓ Right to file complaint
```

## CA.7 Performance Monitoring

```
CLINICAL-RELEVANT METRICS

These metrics should be monitored for patient safety:

Safety Metrics:
  • Emergency detection rate: Target > 99%
  • Medical advice leakage: Target = 0%
  • Safety escalation response time: Target < 30 min
  • Handoff completeness: Target 100%

Compliance Metrics:
  • Opt-out compliance: Target 100%
  • Consent verification rate: Target 100%
  • Quiet hours compliance: Target 100%
  • Frequency cap compliance: Target 100%

Patient Experience:
  • Complaint rate: Target < 0.5%
  • Opt-out rate: Target < 0.3%
  • Response rate: Target > 20%
  • Patient satisfaction: Target > 4/5

Clinical Impact:
  • Appointment recovery rate: Target > 15%
  • No-show recovery rate: Target > 20%
  • Treatment plan completion rate: Monitor trend
  • Recall compliance rate: Monitor trend

Alert Thresholds:
  Safety events > 1/day → Immediate review
  Opt-out rate > 1% → Review message strategy
  Complaint rate > 1% → Immediate review
  Response rate < 10% → Review message quality
  Emergency detection < 95% → Model retrain
```

## CA.8 Incident Response

```
CLINICAL INCIDENT RESPONSE

Category 1: Patient Safety Event
  Examples:
    - AI provided medical advice
    - AI failed to detect emergency
    - AI delayed escalation
    - AI caused patient harm

  Response:
    1. Immediately stop AI for affected patient
    2. Escalate to clinical advisor
    3. Document incident
    4. Notify practice leadership
    5. If patient harm: follow incident protocol
    6. Root cause analysis
    7. Model/prompt update
    8. Report to team

Category 2: Compliance Violation
  Examples:
    - Message sent without consent
    - Opt-out ignored
    - Quiet hours violated
    - Frequency cap exceeded

  Response:
    1. Stop affected campaign
    2. Document violation
    3. Notify compliance team
    4. Fix technical issue
    5. Review affected patients
    6. Report if required by law

Category 3: Data Breach
  Examples:
    - Cross-tenant data leak
    - Unauthorized access
    - Data exfiltration

  Response:
    1. Follow HIPAA breach protocol
    2. Notify affected patients
    3. Notify HHS (if >500 patients)
    4. Document and remediate
    5. Forensic analysis
```
