# Data Architecture — Data Strategy, Storage, and Flow

## DA.1 Data Classification

Every data element is classified:

| Classification | Description | Examples | Handling |
|---------------|-------------|---------|----------|
| **PHI** | Protected Health Information | Name, DOB, phone, email, address, SSN, insurance ID, medical history, appointment details | Encrypted at rest/transit, access-controlled, audit-logged, minimum necessary |
| **PII** | Personal Information (non-health) | Name, email, phone (when not linked to health) | Encrypted, access-controlled |
| **BUSINESS** | Operational data | Clinic names, provider names, service names, pricing | Standard security |
| **PUBLIC** | Non-sensitive | Marketing copy, UI text | No special handling |
| **SECRET** | Credentials and keys | API keys, passwords, tokens | Vault-only, never logged |

## DA.2 Data Ownership

```
ORGANIZATION (tenant)
  └── CLINIC (sub-tenant)
       └── All patient data belongs to the clinic
       └── Clinic controls who can access their data
       └── Clinic can request data export/deletion
```

Data is never shared between clinics without explicit authorization.

## DA.3 Data Flow Architecture

```
                    ┌───────────────────┐
                    │   Data Sources    │
                    │                   │
                    │  • Patient forms  │
                    │  • PMS sync       │
                    │  • Chat/SMS       │
                    │  • Phone system   │
                    │  • Insurance API  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  Ingestion Layer  │
                    │                   │
                    │  • Validation     │
                    │  • Normalization  │
                    │  • Enrichment     │
                    │  • PHI tagging    │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  Hot      │   │  Warm    │   │  Cold    │
        │  Store    │   │  Store   │   │  Store   │
        │           │   │          │   │          │
        │ PostgreSQL│   │ S3       │   │ Glacier  │
        │ (active)  │   │ (30-90d) │   │ (archive)│
        └─────┬─────┘   └────┬─────┘   └────┬─────┘
              │              │              │
              │    ┌─────────▼─────────┐    │
              │    │   Data Warehouse   │    │
              │    │   (analytics)      │    │
              │    │                     │    │
              │    │  • Aggregations    │    │
              │    │  • Reports         │    │
              │    │  • ML features     │    │
              │    │  • No PHI           │    │
              │    └─────────────────────┘    │
              │                               │
              └───────────────────────────────┘
```

## DA.4 Data Retention Policy

| Data Type | Retention Period | Legal Basis | Disposal Method |
|-----------|-----------------|-------------|-----------------|
| Patient records | 7 years after last visit | State dental board requirements | Secure deletion |
| Appointment records | 7 years | HIPAA/State | Secure deletion |
| Communication records | 7 years | HIPAA | Secure deletion |
| Consent records | 7 years after consent expires | HIPAA | Secure deletion |
| Audit logs | 6 years | HIPAA | Secure deletion |
| AI decision logs | 3 years | Best practice | Secure deletion |
| Analytics data (aggregated) | Indefinite | Business | N/A (no PHI) |
| Webhook logs | 90 days | Operational | Auto-delete |

## DA.5 PHI Handling Rules

### PHI in LLM Prompts
```
RULE: Minimize PHI in LLM context.

ALLOWED:
- Patient first name (for personalization)
- Last 4 digits of phone
- General appointment context (not specific health details)
- Clinic name and services

PROHIBITED:
- Full medical history
- Full phone number
- Full address
- Insurance ID numbers
- Social security numbers
- Specific diagnoses
- Treatment notes

If more context needed: Use structured tool calls instead of prompt context.
```

### PHI in Logs
```
RULE: Never log PHI.

Instead of:
  logger.info(f"Patient {patient.name} ({patient.phone}) booked appointment")

Use:
  logger.info(f"Patient {patient.id} booked appointment {appointment.id}")

PHI can be looked up from the ID in the audit system
by authorized personnel only.
```

### PHI in Analytics
```
RULE: Analytics uses aggregated, de-identified data.

NO PHI in:
- Metric definitions
- Dashboard labels
- Report exports
- ML features
- Model training data

All analytics data must pass through de-identification:
- Remove direct identifiers
- Generalize dates
- Aggregate counts
- Minimum cell size = 5 (prevent re-identification)
```

## DA.6 Data Minimization

```
DATA COLLECTION PRINCIPLE:
Collect only what is necessary for the specific purpose.

Example: Patient phone number
  ✓ Needed for: SMS communication, appointment reminders
  ✗ NOT needed for: Analytics, ML features, reporting
  → Phone is stored in patient record, NOT in analytics tables

Example: Appointment details
  ✓ Needed for: Scheduling, reminders, recapture
  ✗ NOT needed for: ML features → use aggregated categories instead
  → Service category (cleaning, root canal) — yes
  → Specific diagnosis — no
```

## DA.7 Data Quality

```python
class DataQualityRules:
    """Enforce data quality at ingestion."""

    RULES = {
        "phone": {
            "required": True,
            "format": "E.164",
            "validation": "^\+[1-9]\d{1,14}$"
        },
        "email": {
            "required": False,
            "format": "RFC 5322",
            "validation": "..."
        },
        "first_name": {
            "required": True,
            "max_length": 100,
            "pattern": "^[a-zA-Z\s\-'.]+$"
        },
        "date_of_birth": {
            "required": True,
            "validation": "age >= 0 AND age <= 120"
        },
        "appointment_time": {
            "required": True,
            "validation": "must be in the future at time of creation"
        }
    }

    async def validate(self, data: dict, entity_type: str):
        rules = self.RULES.get(entity_type, {})
        errors = []
        for field, rule in rules.items():
            value = data.get(field)
            if rule.get("required") and not value:
                errors.append(f"{field} is required")
            if value and "format" in rule:
                if not validate_format(value, rule["format"]):
                    errors.append(f"{field} has invalid format")
        if errors:
            raise ValidationError(errors)
        return True
```

## DA.8 Data Export

Patients and clinics can request data export:

```python
class DataExportService:
    async def export_patient_data(self, patient_id: str):
        """Export all data for a patient (GDPR/HIPAA right of access)."""

        data = {
            "patient_profile": await self.get_patient(patient_id),
            "appointments": await self.get_appointments(patient_id),
            "conversations": await self.get_conversations(patient_id),
            "messages": await self.get_messages(patient_id),
            "consents": await self.get_consents(patient_id),
            "treatment_plans": await self.get_treatment_plans(patient_id),
            "communication_history": await self.get_communications(patient_id),
        }

        # Remove internal fields
        data = self.sanitize_for_export(data)

        # Generate export file
        export_file = await self.generate_export(data, format="json")

        # Log export for compliance
        await self.log_export(patient_id, requested_by="patient_request")

        return export_file
```

## DA.9 Data Deletion

```python
class DataDeletionService:
    async def delete_patient_data(self, patient_id: str, reason: str):
        """Delete patient data (GDPR/HIPAA right to erasure)."""

        # Check if data is needed for:
        # 1. Legal claims (retain if litigation pending)
        # 2. Regulatory requirements (retain per retention policy)
        # 3. Operational needs (anonymize instead)

        legal_hold = await self.check_legal_hold(patient_id)
        if legal_hold:
            raise CannotDeleteError("Data under legal hold")

        retention_required = await self.check_retention_requirement(patient_id)
        if retention_required:
            await self.anonymize_patient_data(patient_id)
            return

        # Safe to delete
        async with transaction():
            await self.delete_patient_record(patient_id)
            await self.delete_conversations(patient_id)
            await self.delete_messages(patient_id)
            await self.delete_communications(patient_id)
            # Keep anonymized audit trail
            await self.anonymize_audit_trail(patient_id)

        await self.log_deletion(patient_id, reason)
```

## DA.10 Data Lineage

Every data element has lineage tracking:
```
Source → Transformation → Destination

Example: Patient phone number
  Source: Lead form submission
  ↓ (validation, normalization)
  Stored: patients.phone
  ↓ (used in)
  - Message sending (SMS provider)
  - Patient lookup (internal)
  - Communication preference check

NOT used in:
  - Analytics
  - ML features
  - Reports
```

Lineage is tracked in a metadata table:
```sql
CREATE TABLE data_lineage (
    id UUID PRIMARY KEY,
    source_entity VARCHAR(100),
    source_field VARCHAR(100),
    destination_entity VARCHAR(100),
    destination_field VARCHAR(100),
    transformation VARCHAR(500),
    purpose VARCHAR(200),
    retention_period VARCHAR(50),
    created_at TIMESTAMP
);
```
