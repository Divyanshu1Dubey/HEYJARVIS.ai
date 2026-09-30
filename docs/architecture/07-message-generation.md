# Message Generation Engine
## Templates, Personalization, Verification, and Safety

**Document:** 07 of 20  
**Purpose:** Defines how outreach messages are generated, ensuring they contain only verified data, respect patient preferences, and never fabricate clinical or financial information.

---

## 1. Core Principle

**The LLM personalizes. The database provides facts. The LLM never invents.**

Every outreach message is constructed from:
1. A verified template (from the template library).
2. Verified patient data (from the database).
3. Verified clinic data (from the database/RAG).
4. Optional LLM personalization (within strict guardrails).

The LLM is NOT a source of truth for any clinical, financial, scheduling, or insurance information.

---

## 2. Message Generation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    RECAPTURE OPPORTUNITY                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: SELECT TEMPLATE                                        │
│  - Based on recapture type                                      │
│  - Based on channel                                             │
│  - Based on patient state                                       │
│  - Based on cancellation reason (if known)                      │
│  - Based on tenant configuration                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: FETCH VERIFIED DATA                                    │
│  - Patient name, last visit date                                │
│  - Clinic name, phone, address                                  │
│  - Appointment slots (from scheduling API)                      │
│  - Insurance status (from insurance API)                        │
│  - Treatment plan details (from database)                       │
│  - Staff/doctor name (from database)                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: FILL TEMPLATE                                          │
│  - Replace template variables with verified data                 │
│  - Do NOT fill variables for which data is unavailable           │
│  - Missing data → use fallback or omit the field                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: LLM PERSONALIZATION (optional)                         │
│  - Adjust tone and wording                                      │
│  - Add contextual references                                    │
│  - STRICTLY within the bounds of verified data                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: SAFETY VALIDATION                                      │
│  - Check for hallucinated content                               │
│  - Check for prohibited claims                                  │
│  - Check for inappropriate tone                                 │
│  - Check for PHI leakage                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: COMPLIANCE CHECK                                       │
│  - Required disclaimers present                                 │
│  - Opt-out instructions included (marketing messages)           │
│  - Channel-appropriate formatting                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: OUTPUT                                                  │
│  - Final message text                                           │
│  - Template ID used                                             │
│  - Variables filled                                             │
│  - Personalization applied                                      │
│  - Safety flags                                                 │
│  - Requires human review?                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Template Library

### 3.1 Template Structure

```python
class MessageTemplate:
    id: uuid
    tenant_id: uuid
    name: string
    recapture_type: string       # From taxonomy
    channel: ChannelType          # SMS, email, voice
    strategy: string              # gentle, standard, urgent, conservative
    language: string              # "en", "es"
    subject: string | null        # For email only
    body: string                  # Template with {{variables}}
    variables: list[string]       # List of variable names used
    fallback_body: string | null  # If primary can't be filled
    requires_review: boolean      # Staff must approve before sending
    max_length: int | null        # Channel-specific limit
    created_at: datetime
    updated_at: datetime
    active: boolean
```

### 3.2 Template Variables

Variables are replaced with verified data. If data is unavailable, the variable is omitted or replaced with a safe default.

**Allowed variables (must map to database fields):**

| Variable | Source | Example | Fallback |
|----------|--------|---------|----------|
| `{{patient_first_name}}` | Patient record | "John" | "there" |
| `{{patient_last_name}}` | Patient record | "Smith" | (omit) |
| `{{clinic_name}}` | Clinic config | "Maple Dental" | (omit — error) |
| `{{clinic_phone}}` | Clinic config | "(555) 123-4567" | (omit — error) |
| `{{last_visit_date}}` | Appointment history | "March 15, 2024" | (omit) |
| `{{last_service}}` | Appointment history | "cleaning" | (omit) |
| `{{cancellation_reason}}` | Cancellation data | "schedule conflict" | (omit) |
| `{{provider_name}}` | Provider record | "Dr. Chen" | (omit) |
| `{{appointment_type}}` | Service catalog | "root canal" | (omit) |
| `{{treatment_description}}` | Treatment plan | "crown on tooth #14" | (omit) |
| `{{insurance_plan}}` | Insurance record | "Delta Dental" | (omit) |
| `{{days_overdue}}` | Calculated field | "14 days" | (omit) |
| `{{opt_out_instructions}}` | Static | "Reply STOP to unsubscribe" | (omit — not for transactional) |

**Prohibited variables (LLM cannot generate):**
- `{{appointment_time}}` — must come from verified scheduling API
- `{{appointment_date}}` — must come from verified scheduling API
- `{{insurance_coverage}}` — must come from verified insurance API
- `{{price}}` — must come from verified pricing data
- `{{discount}}` — must come from verified offer data
- `{{doctor_availability}}` — must come from verified scheduling API
- `{{treatment_outcome}}` — not available at outreach time
- `{{specific_clinical_advice}}` — prohibited

### 3.3 Template Examples

#### Template: Lead Abandoned — SMS

```text
Hi {{patient_first_name}}, this is {{clinic_name}}. We noticed you started looking into [service] but didn't get a chance to book. We'd love to help! Reply YES to see available times, or call us at {{clinic_phone}}. Reply STOP to unsubscribe.
```

#### Template: Cancellation (Schedule Conflict) — SMS

```text
Hi {{patient_first_name}}, sorry you had to cancel your [appointment_type] at {{clinic_name}}. We have new times available that might work better for your schedule. Reply YES and we'll send you options, or call {{clinic_phone}}. Reply STOP to unsubscribe.
```

#### Template: No-Show Recovery — SMS

```text
Hi {{patient_first_name}}, we missed you at {{clinic_name}} today. We hope everything is okay! Would you like to reschedule your [appointment_type]? Reply YES and we'll find a new time. Reply STOP to unsubscribe.
```

#### Template: Treatment Plan Not Scheduled — SMS

```text
Hi {{patient_first_name}}, following up on your treatment plan at {{clinic_name}}. If you have questions about [treatment_description] or would like to schedule, we're here to help. Call us at {{clinic_phone}}. Reply STOP to unsubscribe.
```

#### Template: Recall Overdue — SMS

```text
Hi {{patient_first_name}}, it's been a while since your last visit at {{clinic_name}}. Time for your regular checkup? Reply YES to see available times, or call {{clinic_phone}}. Reply STOP to unsubscribe.
```

#### Template: Inactive Patient — Email

```text
Subject: We'd love to see you again at {{clinic_name}}

Hi {{patient_first_name}},

It's been a while since your last visit to {{clinic_name}}, and we wanted to reach out. We've made some updates to our office and would love to show you around.

If you'd like to schedule a visit, you can:
- Reply to this email
- Call us at {{clinic_phone}}
- Book online at {{clinic_website}}

If we don't hear from you, we understand — but the door is always open.

Warm regards,
The team at {{clinic_name}}

---
You're receiving this because you've visited our practice before.
To update your preferences or unsubscribe, click here: {{preference_link}}
```

### 3.4 Template Management

- Templates are managed per-tenant.
- Tenants can customize templates but cannot remove required elements (clinic identification, opt-out instructions, safety language).
- Templates have a review workflow: new templates require approval before activation.
- Template performance is tracked: response rate, booking rate, opt-out rate per template.

---

## 4. LLM Personalization

### 4.1 When Personalization Is Applied

LLM personalization is applied to:
- Message tone and warmth
- Reference to patient's specific situation
- CTA wording
- Greeting style

LLM personalization is NOT applied to:
- Appointment times or dates
- Insurance information
- Prices or costs
- Clinical information
- Clinic hours or availability
- Treatment recommendations

### 4.2 Personalization Prompt

```
You are personalizing a dental practice outreach message.

PATIENT:
- Name: {patient_first_name}
- Last visit: {last_visit_date} ({last_service})
- Service interest: {service_interest}
- This outreach is about: {recapture_description}

CLINIC:
- Name: {clinic_name}
- Phone: {clinic_phone}

BASE MESSAGE (fill in the blanks):
{template_with_verified_data}

RULES:
1. Keep the same structure and length as the base message.
2. Adjust tone to be warm and personal, matching the patient's situation.
3. Do NOT add any information not provided above.
4. Do NOT mention appointment times, prices, insurance, or clinical details.
5. For SMS: keep under 160 characters if possible.
6. For email: keep under 500 characters in the body.
7. Always include clinic name and phone number.
8. Include opt-out instructions: "Reply STOP to unsubscribe" (SMS) or preference link (email).

Return ONLY the final message text. No explanations.
```

### 4.3 Personalization Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| None | Template as-is, variables filled | Default for all messages |
| Light | Minor tone adjustments, greeting personalization | Low-risk recapture types |
| Full | Contextual references, CTA customization | High-intent patients, treatment recapture |

---

## 5. Safety Validation

### 5.1 Prohibited Content

The safety validator checks for and BLOCKS messages containing:

1. **Fabricated appointments:**
   - "Your appointment is scheduled for Tuesday at 2pm" (without verified booking)
   - Any specific time/date not from the scheduling system

2. **Fabricated insurance information:**
   - "Your insurance covers 100%" (without verification)
   - Any coverage percentage not from the insurance API

3. **Fabricated prices or discounts:**
   - "Only $99" (without verified pricing)
   - "20% off" (without verified offer)

4. **Medical claims or guarantees:**
   - "This treatment will fix your problem"
   - "You need this procedure"
   - Any diagnostic or prescriptive language

5. **Clinical assessment:**
   - "Based on your symptoms..."
   - "This sounds serious..."
   - Any assessment of the patient's condition

6. **Inappropriate urgency:**
   - "URGENT: You must come in today"
   - "Emergency" unless genuinely triggered

7. **PHI in wrong context:**
   - Sending patient's full name, DOB, or address in a message where not needed
   - Including other patients' information

### 5.2 Validation Rules

```python
class SafetyValidator:
    PROHIBITED_PATTERNS = [
        # Fabricated appointments
        r"your appointment is (scheduled|confirmed|set)",
        r"we (have|reserved|saved) (a|the) (slot|time|spot)",
        r"see you on\s+\w+day",  # "see you on Tuesday"

        # Fabricated insurance
        r"your insurance (covers|pays|will pay)",
        r"(100%|fully|copay.free)",
        r"\d+% (covered|off|discount)",

        # Medical claims
        r"this (will|should|can|could) (fix|help|resolve|treat| cure)",
        r"you (need|require|must have)",
        r"based on (your|the) (symptoms|condition|description)",
        r"this (sounds|appears|seems) (serious|urgent|emergency)",

        # Clinical assessment
        r"(diagnose|diagnosis|prescribe|prescription)",
        r"your (tooth|gum|mouth) (needs|requires|has)",
    ]

    def validate(self, message: str, verified_data: dict) -> ValidationResult:
        issues = []

        for pattern in PROHIBITED_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                issues.append(f"Prohibited content: pattern '{pattern}' matched")

        # Check for unverified claims
        if "appointment" in message.lower() and not verified_data.get("has_verified_appointment"):
            issues.append("Message mentions appointment without verified booking")

        if "insurance" in message.lower() and not verified_data.get("has_verified_insurance"):
            issues.append("Message mentions insurance without verification")

        if any(char.isdigit() for char in message) and "price" in message.lower():
            if not verified_data.get("has_verified_price"):
                issues.append("Message contains numbers that look like pricing without verification")

        if issues:
            return ValidationResult(
                valid=False,
                issues=issues,
                requires_review=True,
            )

        return ValidationResult(valid=True, issues=[])
```

---

## 6. Compliance Checks

### 6.1 Required Elements by Channel

| Channel | Required Elements |
|---------|-------------------|
| SMS | Clinic identification, opt-out instruction ("Reply STOP to unsubscribe") |
| SMS (transactional) | Clinic identification, opt-out instruction |
| Email | Physical address, unsubscribe link, "why you're receiving this" |
| Voice (automated) | Clinic identification, opt-out instruction, disclosure that it's automated |
| Voice (live agent) | Clinic identification, caller ID matching |

### 6.2 Disallowed Content by Channel

| Channel | Disallowed |
|---------|-----------|
| SMS | Links (shortened URLs only with tenant approval), images |
| Email | Deceptive subject lines, false header information |
| Voice | Pre-recorded message without consent disclosure |

---

## 7. Message Length & Formatting

### 7.1 Channel Limits

| Channel | Max Length | Recommendation |
|---------|-----------|----------------|
| SMS | 1600 chars (concatenated) | Target ≤160 chars for single segment |
| Email body | No hard limit | Target ≤500 chars body + full details in link |
| Email subject | 50 chars | Target ≤50 chars |
| Voice script | No hard limit | Target ≤30 seconds speech (~75 words) |

### 7.2 Concatenation Strategy

For SMS over 160 characters:
- Option A: Truncate and add "[...]" — keep it one message.
- Option B: Split into 2-3 segments — natural breaks at sentences.
- Option C: Convert to email with link — if SMS can't convey the message effectively.

---

## 8. Multi-Language Support

### 8.1 Supported Languages

| Language | Code | Support Level |
|----------|------|---------------|
| English | en | Full (templates, LLM, intent classification) |
| Spanish | es | Full (templates, LLM, intent classification) |

### 8.2 Translation Strategy

- Templates are maintained in both English and Spanish.
- LLM personalization uses the same language as the template.
- Patient's preferred language is determined from:
  1. Explicit preference in communication preferences.
  2. Conversation language detection (first message).
  3. Clinic configuration (if no patient preference).

**Translation quality:**
- Templates are professionally translated, not LLM-translated.
- LLM personalization uses the target language with instructions to maintain professional medical tone.
- Spanish translations include culturally appropriate tone for dental communication.

---

## 9. Message Audit & Review

### 9.1 Auto-Approval Criteria

Messages are auto-approved (sent without staff review) if:
1. Safety validation passes.
2. Compliance checks pass.
3. Risk score < 0.3.
4. Template is marked as "auto-approve."
5. No LLM personalization was applied (template-only messages).

### 9.2 Human Review Queue

Messages require staff review if ANY of:
1. Safety validation flags issues.
2. Risk score ≥ 0.3.
3. LLM personalization was applied to a new template (first 10 uses).
4. Template is marked as "requires review."
5. Patient has complaint history.
6. Message contains financial information.

**Review SLA:** Staff must review flagged messages within 4 business hours. If not reviewed, the message is NOT sent (suppressed).

---

## 10. Performance Tracking

Every sent message is tracked:

```python
MessagePerformance:
  template_id: uuid
  channel: ChannelType
  recapture_type: string
  strategy: string
  total_sent: integer
  total_delivered: integer
  total_replied: integer
  total_booked: integer
  total_opted_out: integer
  total_complained: integer
  response_rate: float
  booking_rate: float
  opt_out_rate: float
  complaint_rate: float
  revenue_attributed: decimal
  last_updated: datetime
```

**Template retirement:** Templates with opt-out rate > 2% or complaint rate > 0.5% are automatically flagged for review and may be retired.
