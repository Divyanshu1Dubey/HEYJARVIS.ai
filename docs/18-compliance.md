# Compliance Architecture — Healthcare Communication Compliance

## CP.1 Regulatory Framework

### HIPAA (Health Insurance Portability and Accountability Act)

**Applies to:** All protected health information (PHI)

**Key requirements for HeyJarvis:**

| Requirement | Implementation |
|------------|----------------|
| **Privacy Rule** | Patient consent for communications, minimum necessary |
| **Security Rule** | Encryption, access controls, audit logs |
| **Breach Notification** | 60-day notification for PHI breaches |
| **Business Associate Agreement** | Required for all vendors handling PHI |
| **Patient Rights** | Access, amendment, accounting of disclosures |
| **Minimum Necessary** | Only use/share minimum PHI needed |

### TCPA (Telephone Consumer Protection Act)

**Applies to:** SMS and voice communications

**Key requirements for HeyJarvis:**

| Requirement | Implementation |
|------------|----------------|
| **Express Written Consent** | Required for SMS (not implied) |
| **Opt-out Mechanism** | STOP keyword, reply STOP |
| **Do-Not-Call Registry** | Check against DNC list |
| **Auto-dialer restrictions** | Use manual dialing or consent |
| **Timing restrictions** | No calls before 8 AM or after 9 PM |
| **Identification** | Identify sender in message |
| **Opt-out compliance** | Honor opt-outs within 30 days |

**Critical: Healthcare exemption note:**
The TCPA has a healthcare exemption that allows certain communications without consent, but:
1. This exemption is LIMITED and does NOT apply to marketing
2. Appointment reminders MAY qualify if using healthcare provider's number
3. Consult legal counsel before relying on exemptions
4. The safest approach: explicit consent for all communications

### CAN-SPAM (Controlling the Assault of Non-Solicited Pornography and Marketing Act)

**Applies to:** Commercial email

**Key requirements:**

| Requirement | Implementation |
|------------|----------------|
| **No deceptive headers** | Accurate From/Reply-To |
| **No deceptive subject lines** | Subject matches content |
| **Physical address** | Include clinic address |
| **Opt-out mechanism** | Working unsubscribe link |
| **Opt-out honor within 10 days** | Process opt-outs quickly |
| **No charge for opt-out** | Free unsubscribe |

### State Privacy Laws

**Major state laws to consider:**

| State | Law | Key Requirement |
|-------|-----|-----------------|
| California | CCPA/CPRA | Right to know, delete, opt-out of sale |
| California | CMIA | Confidentiality of medical information |
| New York | SHIELD Act | Data security requirements |
| Texas | HB 300 | Healthcare data breach notification |
| Massachusetts | 201 CMR 17.00 | Data security standards |
| Washington | HB 1155 | Health data sharing restrictions |

## CP.2 Consent Management

### Consent Types

```python
class ConsentType(str, Enum):
    SMS_TREATMENT = "sms_treatment"      # SMS for treatment/healthcare
    SMS_APPOINTMENT = "sms_appointment"  # SMS for appointment reminders
    SMS_MARKETING = "sms_marketing"      # SMS for marketing (requires express)
    EMAIL_TREATMENT = "email_treatment"
    EMAIL_MARKETING = "email_marketing"
    VOICE_TREATMENT = "voice_treatment"
    VOICE_MARKETING = "voice_marketing"
    HIPAA_ACK = "hipaa_ack"              # HIPAA privacy notice acknowledgment
    PRIVACY_POLICY = "privacy_policy"    # Privacy policy agreement
```

### Consent Record

```python
class Consent:
    id: UUID
    patient_id: UUID
    consent_type: str
    granted: bool
    method: str  # web_form, phone, in_person, verbal
    ip_address: Optional[str]
    consent_text: str  # Exact text patient agreed to
    consent_date: datetime
    expires_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    consenting_user_id: Optional[UUID]  # Staff who obtained consent
```

### Consent Verification

```python
class ConsentService:
    """Verify and enforce consent."""

    async def can_send_sms(self, patient_id: str, purpose: str) -> bool:
        """Check if we can send SMS to this patient for this purpose."""

        consent = await self.get_consent(patient_id, f"sms_{purpose}")

        if not consent:
            return False

        if not consent.granted:
            return False

        if consent.expires_at and consent.expires_at < datetime.now():
            return False

        if consent.withdrawn_at:
            return False

        return True

    async def record_consent(
        self,
        patient_id: str,
        consent_type: str,
        granted: bool,
        method: str,
        ip_address: str = None,
        consenting_user_id: UUID = None
    ):
        """Record patient consent."""

        # Get current consent text from configuration
        consent_text = await self.config.get_consent_text(consent_type)

        consent = Consent(
            patient_id=patient_id,
            consent_type=consent_type,
            granted=granted,
            method=method,
            ip_address=ip_address,
            consent_text=consent_text,
            consenting_user_id=consenting_user_id
        )

        await self.db.save(consent)

        # Emit event
        await self.events.emit(
            "patient.consent.updated",
            patient_id=patient_id,
            consent_type=consent_type,
            granted=granted
        )
```

## CP.3 Opt-out Handling

```python
class OptOutService:
    """Handle patient opt-outs."""

    STOP_KEYWORDS = {
        "stop", "stopall", "end", "cancel", "unsubscribe",
        "quit", "leave", "remove", "no more"
    }

    async def process_opt_out(self, patient_id: str, channel: str, source: str):
        """Process patient opt-out."""

        # 1. Mark patient as opted out for this channel
        await self.db.execute("""
            INSERT INTO consents (patient_id, consent_type, granted, method, withdrawn_at)
            VALUES (:pid, :type, false, 'patient_request', NOW())
            ON CONFLICT (patient_id, consent_type)
            WHERE granted = true
            DO UPDATE SET granted = false, withdrawn_at = NOW()
        """, {"pid": patient_id, "type": f"{channel}_treatment"})

        # 2. Add to suppression list
        await self.suppression_list.add(
            patient_id=patient_id,
            channel=channel,
            reason="patient_opted_out",
            scope="channel"
        )

        # 3. Stop any active campaigns
        await self.campaigns.stop_for_patient(patient_id)

        # 4. Log for compliance
        await self.audit.log(
            action="patient_opted_out",
            patient_id=patient_id,
            channel=channel,
            source=source
        )

        # 5. Send confirmation
        await self.messages.send(
            patient_id=patient_id,
            channel=channel,
            content="You've been removed from our messages. Reply START to re-subscribe."
        )

        # 6. Emit event
        await self.events.emit("patient.opted_out", patient_id=patient_id, channel=channel)
```

## CP.4 Communication Rules by Channel

### SMS

```
REQUIRED:
✓ Explicit consent before first message
✓ Clear opt-out mechanism (STOP keyword)
✓ Sender identification
✓ Message content relevant to healthcare relationship
✓ Opt-out confirmation message

PROHIBITED:
✗ Messages without consent
✗ No opt-out option
✗ False or misleading sender ID
✗ Content unrelated to healthcare (without separate consent)
✗ Messages before 8 AM or after 9 PM (patient timezone)
```

### Email

```
REQUIRED:
✓ Valid From address (clinic email)
✓ Accurate subject line
✓ Physical mailing address
✓ Working unsubscribe link
✓ Opt-out honored within 10 business days
✓ If marketing: prior consent or existing relationship

PROHIBITED:
✗ Deceptive headers/subjects
✗ No unsubscribe mechanism
✗ Harvested email addresses
✗ Misleading content
```

### Voice (V2)

```
REQUIRED:
✓ Consent for automated calls
✓ Disclosure of automated nature (if using pre-recorded)
✓ Opt-out mechanism
✓ Identification of calling entity
✓ Time-of-day restrictions (8 AM - 9 PM)

PROHIBITED:
✗ Robocalls without consent
✗ No opt-out option
✗ Misleading caller ID
```

### Website Chat

```
REQUIRED:
✓ Privacy notice on chat widget
✓ Disclosure that AI is being used
✓ Option to request human
✓ Data handling disclosure

PROHIBITED:
✗ Hidden AI disclosure
✗ No way to reach human
✗ Collecting data without disclosure
```

## CP.5 Audit Requirements

```sql
CREATE TABLE compliance_audit_log (
    id UUID PRIMARY KEY,
    clinic_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    patient_id UUID,
    user_id UUID,
    ip_address INET,
    user_agent TEXT,
    consent_verified BOOLEAN,
    channel VARCHAR(20),
    message_content TEXT,  -- Redacted in production
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- Required audit reports:
-- 1. All messages sent (daily)
-- 2. All opt-outs (daily)
-- 3. All consent changes (daily)
-- 4. All handoffs (daily)
-- 5. All safety events (daily)
-- 6. All data access (real-time)
-- 7. All data exports (real-time)
-- 8. All data deletions (real-time)
```

## CP.6 Data Retention

| Data Type | Retention Period | Legal Basis | Disposal |
|-----------|-----------------|-------------|----------|
| Patient records | 7 years after last visit | State dental board | Secure deletion |
| Appointments | 7 years | HIPAA | Secure deletion |
| Communications (SMS/Email) | 7 years | HIPAA | Secure deletion |
| Consent records | 7 years after consent | HIPAA | Secure deletion |
| Audit logs | 6 years | HIPAA | Secure deletion |
| AI logs | 3 years | Best practice | Secure deletion |

## CP.7 Patient Rights

### Right to Access
```python
class PatientAccessService:
    async def export_patient_data(self, patient_id: str):
        """HIPAA right of access - provide all patient data."""

        data = {
            "profile": await self.patients.get(patient_id),
            "appointments": await self.appointments.get_for_patient(patient_id),
            "communications": await self.communications.get_for_patient(patient_id),
            "consents": await self.consents.get_for_patient(patient_id),
            "treatment_plans": await self.treatment_plans.get_for_patient(patient_id),
        }

        # Generate export within 30 days (HIPAA requirement)
        export = await self.generate_export(data, format="json")

        await self.audit.log(
            action="patient_data_export",
            patient_id=patient_id,
            requested_by="patient_request"
        )

        return export
```

### Right to Deletion
```python
class PatientDeletionService:
    async def delete_patient_data(self, patient_id: str, reason: str):
        """HIPAA right to amendment / deletion request."""

        # Check legal hold
        if await self.has_legal_hold(patient_id):
            raise CannotDeleteError("Data under legal hold")

        # Check retention requirements
        if await self.retention_required(patient_id):
            await self.anonymize_patient_data(patient_id)
        else:
            await self.delete_patient_data(patient_id)

        await self.audit.log(
            action="patient_data_deletion",
            patient_id=patient_id,
            reason=reason
        )
```

## CP.8 Business Associate Agreement

All vendors handling PHI must sign a BAA:

| Vendor | PHI Access | BAA Required |
|--------|-----------|-------------|
| LLM Provider | Yes (prompts may contain PHI) | YES |
| SMS Provider | Yes (phone numbers) | YES |
| Email Provider | Yes (email addresses) | YES |
| Cloud Provider | Yes (data at rest) | YES |
| Analytics Provider | No (aggregated only) | Not required |
| Monitoring Provider | Yes (logs) | YES |
| Integration Partners | Yes (appointment data) | YES |

## CP.9 Breach Response

```python
class BreachResponse:
    async def handle_breach(self, incident: SecurityIncident):
        """HIPAA breach response procedure."""

        # 1. Contain the breach
        await self.contain(incident)

        # 2. Assess scope
        phi_affected = await self.assess_phi_exposure(incident)
        individual_count = len(phi_affected)

        # 3. Determine if reportable
        if self.is_reportable(phi_affected):
            # 4. Notify HHS within 60 days
            await self.notify_hhs(incident, phi_affected)

            # 5. Notify affected individuals
            await self.notify_individuals(phi_affected, incident)

            # 6. Notify media if > 500 individuals
            if individual_count >= 500:
                await self.notify_media(incident)

        # 7. Document everything
        await self.document_breach(incident)

        # 8. Remediate
        await self.remediate(incident)
```

## CP.10 Compliance Checklist

```
PRIVACY:
□ Consent obtained before first communication
□ Consent text matches what patient agreed to
□ Consent records are complete and accurate
□ Opt-out mechanism is functional
□ Opt-outs are honored immediately
□ Patient data access requests handled within 30 days
□ Minimum necessary principle applied

SECURITY:
□ PHI encrypted at rest (AES-256)
□ PHI encrypted in transit (TLS 1.3)
□ Access controls implemented (RBAC)
□ Audit logs for all PHI access
□ BAAs signed with all vendors

COMMUNICATION:
□ SMS consent verified before sending
□ STOP keyword functional
□ Do-Not-Call list checked
□ Time-of-day restrictions enforced
□ Sender identification included
□ Email unsubscribe functional

BREACH:
□ Breach response plan documented
□ HHS notification process defined
□ Individual notification process defined
□ 60-day timeline understood
□ Breach log maintained
```
