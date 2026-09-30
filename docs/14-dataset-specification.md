# Dataset Specification — Production Dataset Design

## DS.1 Overview

This document defines the complete dataset schema for training, evaluation, and production features of the HeyJarvis Patient Recapture system.

## DS.2 Data Sources

```
DATA FLOW:
  External Systems → Ingestion → Feature Store → Model Training
                      ↓
                   Feature Store → Model Inference
```

### Source Systems
1. **Lead forms** — Website form submissions
2. **Chat system** — Website chat conversations
3. **SMS** — Twilio message logs
4. **Email** — Postmark email logs
5. **PMS** — Practice management system (Open Dental, etc.)
6. **Phone system** — Call logs (V2)
7. **Staff actions** — Manual notes, handoffs, overrides
8. **Campaign system** — Outreach attempts and outcomes

## DS.3 Dataset Schemas

### A. Patient Events Dataset

```python
@dataclass
class PatientEvent:
    """Base event record."""
    event_id: str
    event_type: str  # lead_created, appointment_cancelled, etc.
    patient_id: str
    clinic_id: str
    timestamp: datetime
    event_data: dict  # Type-specific payload
    source_system: str  # website, pms, chat, sms
```

```sql
-- events table (append-only, immutable)
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    patient_id UUID NOT NULL,
    clinic_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_data JSONB NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    idempotency_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for feature extraction
CREATE INDEX idx_events_patient_time ON events(patient_id, timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_clinic_time ON events(clinic_id, timestamp);
```

### B. Communication History Dataset

```python
@dataclass
class CommunicationRecord:
    """Single communication event."""
    communication_id: str
    patient_id: str
    clinic_id: str
    channel: str  # sms, email, voice, web
    direction: str  # inbound, outbound
    timestamp: datetime
    content: str  # Message content (for AI training)
    content_redacted: str  # PHI-removed version
    intent: Optional[str]  # AI-classified intent
    sentiment: Optional[str]  # AI-classified sentiment
    safety_flags: List[str]  # Any safety concerns
    outcome: Optional[str]  # response, no_response, opted_out
    response_timestamp: Optional[datetime]
    response_content: Optional[str]
    ai_generated: bool  # Was the outbound message AI-generated?
    campaign_id: Optional[str]
    opportunity_id: Optional[str]
```

```sql
CREATE TABLE communication_history (
    communication_id UUID PRIMARY KEY,
    patient_id UUID NOT NULL,
    clinic_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,  -- inbound, outbound
    timestamp TIMESTAMP NOT NULL,
    content TEXT,  -- PHI: restricted access
    content_hash VARCHAR(64),  -- For dedup without PHI
    intent VARCHAR(50),
    sentiment VARCHAR(20),
    safety_flags JSONB DEFAULT '[]',
    outcome VARCHAR(20),
    response_timestamp TIMESTAMP,
    response_content TEXT,
    ai_generated BOOLEAN DEFAULT false,
    campaign_id UUID,
    opportunity_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### C. Appointment History Dataset

```python
@dataclass
class AppointmentRecord:
    """Appointment record for ML features."""
    appointment_id: str
    patient_id: str
    clinic_id: str
    provider_id: str
    service_id: str
    service_category: str  # cleaning, root_canal, etc.
    scheduled_start: datetime
    scheduled_end: datetime
    status: str  # scheduled, confirmed, completed, cancelled, no_show
    cancellation_reason: Optional[str]
    cancellation_notes: Optional[str]
    source: str  # ai, staff, patient, phone, web
    confirmation_sent: bool
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime
```

### D. Recapture Outcome Dataset

```python
@dataclass
class RecaptureOutcome:
    """Recapture attempt outcome for ML training."""
    opportunity_id: str
    patient_id: str
    clinic_id: str
    category: str  # cancellation, no_show, lead, recall, etc.
    sub_category: str
    attempt_number: int
    channel: str
    message_template: str
    personalization_vars: dict
    sent_at: datetime
    delivered_at: Optional[datetime]
    patient_responded: bool
    response_timestamp: Optional[datetime]
    response_content: Optional[str]
    response_intent: Optional[str]
    booked: bool
    booked_at: Optional[datetime]
    appointment_value: Optional[float]
    opted_out: bool
    handoff_created: bool
    days_since_trigger: int
    patient_features: dict  # Aggregated patient features
    clinic_features: dict  # Clinic-level features
```

### E. Patient Feature Vector

```python
@dataclass
class PatientFeatures:
    """Aggregated patient features for ML models."""

    # Demographics
    age: int
    days_since_first_visit: int

    # Visit history
    total_visits: int
    visits_last_12_months: int
    visits_last_6_months: int
    days_since_last_visit: int
    avg_visit_interval_days: float

    # Financial
    total_lifetime_value: float
    avg_appointment_value: float
    outstanding_balance: float
    has_insurance: bool
    insurance_type: str

    # Engagement
    total_communications: int
    communications_last_30_days: int
    response_rate: float
    opt_out_count: int
    no_show_count: int
    cancellation_count: int

    # Recapture history
    prior_recapture_attempts: int
    prior_recapture_successes: int
    prior_recapture_response_rate: float

    # Appointment patterns
    preferred_day_of_week: int
    preferred_time_of_day: str  # morning, afternoon, evening
    avg_advance_booking_days: float
    cancellation_rate: float
    no_show_rate: float
```

### F. Feature Store

```python
class FeatureStore:
    """Store and serve features for ML models."""

    async def get_patient_features(
        self,
        patient_id: str,
        as_of: datetime
    ) -> PatientFeatures:
        """Get patient features as of a specific timestamp.

        CRITICAL: No data leakage — features must only use
        information available BEFORE the as_of timestamp.
        """
        patient = await self.db.get_patient_at(patient_id, as_of)
        appointments = await self.db.get_appointments_before(patient_id, as_of)
        communications = await self.db.get_communications_before(patient_id, as_of)
        recapture_attempts = await self.db.get_recapture_before(patient_id, as_of)

        return PatientFeatures(
            # Demographics (snapshot at time)
            age=calculate_age(patient.dob, as_of),
            days_since_first_visit=(as_of - patient.created_at).days,

            # Visit history (only visits before as_of)
            total_visits=len(appointments),
            visits_last_12_months=count_recent(appointments, as_of, days=365),
            days_since_last_visit=days_since_last(appointments, as_of),

            # Financial (only from past appointments)
            total_lifetime_value=sum(a.value for a in appointments if a.completed),
            avg_appointment_value=mean([a.value for a in appointments if a.completed]),

            # Engagement (only communications before as_of)
            total_communications=len(communications),
            response_rate=response_rate(communications),

            # Recapture history (only attempts before as_of)
            prior_recapture_attempts=len(recapture_attempts),
            prior_recapture_successes=count_successful(recapture_attempts),

            # IMPORTANT: No data from after as_of
        )
```

## DS.4 Training Dataset Construction

### Construction Rules

```python
class TrainingDatasetBuilder:
    """Build training datasets with strict no-leakage rules."""

    def build_conversion_dataset(self) -> pd.DataFrame:
        """Build dataset: will this outreach convert?"""
        rows = []

        # Get all outreach attempts
        for attempt in self.get_all_outreach_attempts():
            # CRITICAL: Get features as of the moment BEFORE the outreach
            features = self.feature_store.get_features(
                patient_id=attempt.patient_id,
                as_of=attempt.sent_at - timedelta(seconds=1)
            )

            # Label: Did this specific outreach result in booking?
            label = self.get_outcome(
                patient_id=attempt.patient_id,
                after=attempt.sent_at,
                within=timedelta(days=7)
            )

            rows.append({
                # Features (all before outreach)
                **features.to_dict(),

                # Outreach details
                "outreach_channel": attempt.channel,
                "outreach_hour": attempt.sent_at.hour,
                "outreach_day_of_week": attempt.sent_at.weekday(),
                "attempt_number": attempt.attempt_number,

                # Label (outcome AFTER outreach)
                "booked": label.booked,
                "responded": label.responded,
                "opted_out": label.opted_out,
            })

        return pd.DataFrame(rows)

    def get_outcome(self, patient_id, after, within):
        """Get outcome after an outreach.

        This is the LABEL — it uses data AFTER the feature timestamp.
        This is OK because labels are separate from features.
        """
        appointments = self.db.get_appointments(
            patient_id=patient_id,
            created_after=after,
            created_before=after + within
        )
        responses = self.db.get_responses(
            patient_id=patient_id,
            after=after,
            before=after + within
        )
        opt_outs = self.db.get_opt_outs(
            patient_id=patient_id,
            after=after
        )

        return Outcome(
            booked=len(appointments) > 0,
            responded=len(responses) > 0,
            opted_out=len(opt_outs) > 0
        )
```

### Train/Validation/Test Split

```python
def split_dataset(dataset: pd.DataFrame):
    """Split dataset with proper temporal and patient-level separation."""

    # 1. Sort by timestamp
    dataset = dataset.sort_values("timestamp")

    # 2. Get unique patients
    patients = dataset["patient_id"].unique()

    # 3. Split patients (not rows!) into train/val/test
    # This prevents data leakage from same patient in train and test
    train_patients, temp_patients = train_test_split(patients, test_size=0.3)
    val_patients, test_patients = train_test_split(temp_patients, test_size=0.5)

    # 4. Filter rows by patient split
    train = dataset[dataset["patient_id"].isin(train_patients)]
    val = dataset[dataset["patient_id"].isin(val_patients)]
    test = dataset[dataset["patient_id"].isin(test_patients)]

    # 5. Verify temporal separation
    assert train["timestamp"].max() < val["timestamp"].min()
    assert val["timestamp"].max() < test["timestamp"].min()

    return train, val, test
```

## DS.5 Dataset Quality

### Label Quality Checks

```python
class DatasetQualityChecker:
    """Verify dataset quality before training."""

    def check_label_consistency(self, dataset):
        """Check for inconsistent labels."""
        # Same patient+scenario should have consistent labels
        inconsistencies = []
        for patient_id, group in dataset.groupby("patient_id"):
            if group["label"].nunique() > 1:
                inconsistencies.append(patient_id)
        return inconsistencies

    def check_class_balance(self, dataset):
        """Report class distribution."""
        return dataset["label"].value_counts(normalize=True)

    def check_feature_distribution(self, train, test):
        """Check for train/test distribution shift."""
        from scipy.stats import ks_2samp
        shifts = {}
        for col in feature_columns:
            stat, p_value = ks_2samp(train[col], test[col])
            if p_value < 0.01:
                shifts[col] = {"statistic": stat, "p_value": p_value}
        return shifts

    def check_missing_data(self, dataset):
        """Report missing data patterns."""
        return dataset.isnull().sum() / len(dataset)
```

## DS.6 Feature Versioning

```python
class FeatureVersion:
    """Versioned feature definitions."""

    version: str
    features: List[str]
    transformations: dict
    created_at: datetime
    deprecated_at: Optional[datetime]

    def transform(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Apply feature transformations."""
        df = raw_data.copy()
        for feature in self.features:
            df[feature] = self.transformations[feature](df)
        return df
```

Every model is trained and served with specific feature versions. Changing features requires retraining.

## DS.7 Synthetic Data for Testing

```python
class SyntheticDataGenerator:
    """Generate realistic synthetic data for testing and cold start."""

    def generate_patients(self, n: int) -> List[dict]:
        """Generate synthetic patient records."""
        patients = []
        for _ in range(n):
            patients.append({
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "phone": fake.phone_number(),
                "email": fake.email(),
                "date_of_birth": fake.date_of_birth(),
                "insurance_carrier": random.choice(INSURANCE_CARRIERS),
                "state": random.choice(PATIENT_STATES)
            })
        return patients

    def generate_conversations(self, n: int) -> List[dict]:
        """Generate synthetic conversations."""
        conversations = []
        intents = ["BOOK_APPOINTMENT", "CANCEL", "INSURANCE_QUESTION", ...]
        for _ in range(n):
            intent = random.choice(intents)
            conversations.append({
                "messages": generate_conversation_for_intent(intent),
                "intent": intent,
                "outcome": random.choice(["booked", "declined", "no_response"])
            })
        return conversations
```
