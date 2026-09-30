# Model Training Plan — Complete ML Training Strategy

## MT.1 Training Philosophy

1. **Start rules-first.** Do not train models until you have sufficient data and a clear evaluation framework.
2. **Measure before you model.** Know your baseline (rules-based) performance before adding ML.
3. **Cold start safely.** Use pretrained models and pooled data for new clinics.
4. **Every model has a kill switch.** Rollback must be instant and automatic.
5. **Offline evaluation first.** Models must pass offline tests before any live traffic.
6. **Shadow → Canary → Production.** Gradual rollout with monitoring at each stage.

## MT.2 Model Inventory

| Model | Purpose | Type | When to Train | Data Needed |
|-------|---------|------|--------------|-------------|
| Intent Classifier | Classify patient message intent | Fine-tuned classifier / LLM | After 1000+ labeled conversations | Labeled conversations |
| Recapture Reason | Classify why patient didn't convert | Fine-tuned classifier | After 500+ labeled opportunities | Labeled opportunities |
| Conversion Predictor | Predict likelihood of booking | Gradient boosting / Calibrated classifier | After 2000+ outreach outcomes | Historical outreach + outcomes |
| Response Predictor | Predict if patient will respond | Logistic regression | After 1000+ outreach attempts | Outreach + response data |
| Optimal Time | Best time to contact patient | Survival model | After 500+ contact attempts | Contact timestamps + responses |
| Priority Scorer | Score recapture opportunity priority | Gradient boosting | After 1000+ opportunities | Opportunity features + outcomes |
| Message Ranker | Rank message variants by effectiveness | Learning-to-rank | After A/B tests with 500+ per variant | A/B test results |
| Next-Best-Action | Predict best next action | Multi-class classifier | After 2000+ actions + outcomes | Action history + outcomes |

## MT.3 Intent Classification Model

### Purpose
Determine what the patient wants from their message.

### Classes
```python
INTENT_CLASSES = [
    "BOOK_APPOINTMENT",           # Wants to schedule
    "RESCHEDULE_APPOINTMENT",     # Wants to change time
    "CANCEL_APPOINTMENT",         # Wants to cancel
    "EMERGENCY_REQUEST",           # Urgent dental need
    "INSURANCE_QUESTION",          # Asking about insurance
    "PRICING_QUESTION",            # Asking about cost
    "SERVICE_QUESTION",            # Asking about a service
    "LOCATION_QUESTION",           # Asking about location/hours
    "HUMAN_HANDOFF",               # Asking for staff
    "GENERAL_QUESTION",            # Other question
    "DECLINE",                     # Not interested
    "CONFIRM",                     # Confirming something
    "UNKNOWN"                      # Cannot determine
]
```

### Input
```python
{
    "message": "I broke my front tooth and need to be seen today",
    "conversation_history": [
        {"role": "ai", "content": "..."},
        {"role": "patient", "content": "..."}
    ],
    "patient_context": {
        "first_name": "John",
        "state": "engaged",
        "has_upcoming_appointment": False
    },
    "clinic_context": {
        "name": "Sunrise Dental",
        "services": ["cleaning", "root_canal", ...]
    }
}
```

### Output
```python
{
    "intent": "BOOK_APPOINTMENT",
    "confidence": 0.92,
    "urgency": "high",
    "entities": {
        "problem": "broken_tooth",
        "deadline": "saturday",
        "insurance": "delta_dental"
    },
    "alternative_intents": [
        {"intent": "EMERGENCY_REQUEST", "confidence": 0.6}
    ]
}
```

### Training Data Requirements
- **Minimum:** 1,000 labeled examples
- **Preferred:** 5,000+ labeled examples
- **Per-class minimum:** 50 examples (for rare intents)
- **Hard negatives:** Include messages that look similar but are different intents

### Labeling Guidelines
```
Labeling criteria:
1. Label the PRIMARY intent (what the patient most wants)
2. If multiple intents, label the most important one
3. Use urgency based on keywords + context
4. Mark EMERGENCY_REQUEST only for genuine urgency indicators

Emergency indicators (trigger EMERGENCY_REQUEST):
- "broken tooth", "severe pain", "bleeding", "swelling"
- "emergency", "urgent", "asap", "today"
- But NOT: "I need a cleaning urgently" (that's BOOK_APPOINTMENT)
```

### Evaluation Metrics
| Metric | Minimum | Target |
|--------|---------|--------|
| Overall accuracy | 85% | 92% |
| Per-class F1 (min) | 70% | 80% |
| EMERGENCY_REQUEST recall | 99% | 99.5% |
| HUMAN_HANDOFF recall | 90% | 95% |
| BOOK_APPOINTMENT precision | 85% | 90% |

### Data Leakage Prevention
```
NEVER use:
- Future messages to classify current message
- Outcome data (did they book?) to predict intent
- Staff labels from after the conversation ended

ALWAYS use:
- Only messages up to and including the current one
- Conversation state at time of message
- No outcome data in training
```

## MT.4 Conversion Prediction Model

### Purpose
Predict whether a recapture outreach will result in a booked appointment.

### Input Features
```python
{
    # Patient features
    "patient_age": 34,
    "patient_is_new": False,
    "patient_visit_count": 5,
    "patient_last_visit_days_ago": 90,
    "patient_total_spend": 2500,

    # Opportunity features
    "opportunity_category": "cancellation",
    "opportunity_sub_category": "schedule_conflict",
    "opportunity_age_hours": 24,
    "potential_value": 250,

    # Outreach features
    "outreach_channel": "sms",
    "outreach_attempt_number": 1,
    "time_since_last_contact_days": 30,
    "is_business_hours": True,
    "is_weekday": True,

    # Historical features
    "patient_prior_response_rate": 0.3,
    "patient_prior_booking_rate": 0.15,
    "clinic_avg_conversion_rate": 0.18,

    # Context features
    "has_consent_sms": True,
    "preferred_channel_matches": True,
    "treatment_type": "cleaning"
}
```

### Output
```python
{
    "conversion_probability": 0.25,
    "confidence": 0.8,
    "recommended_channel": "sms",
    "recommended_time": "2025-10-01T14:00:00Z",
    "recommended_message_strategy": "availability_focus",
    "risk_score": 0.1
}
```

### Model Selection

**Recommended:** Gradient Boosting (XGBoost / LightGBM)

**Why:**
- Handles mixed feature types well
- Provides feature importance (explainability)
- Works well with tabular data
- Calibrated probabilities
- Fast inference

**Alternatives:**
- Logistic Regression: Simpler, more interpretable, but less accurate
- Neural network: More complex, needs more data, less interpretable
- Survival model: Better for time-to-event, but more complex

### Training Data
```python
# Each training example is one outreach attempt
training_example = {
    "features": { ... },  # Features at time of outreach
    "label": 1,  # 1 if booked, 0 if not
    "patient_id": "uuid",
    "clinic_id": "uuid",
    "timestamp": "2025-10-01T14:00:00Z"
}
```

### Critical: No Data Leakage
```
WRONG (leakage):
  features = {
      "patient_responded": True,  # ← This happens AFTER outreach
      "outcome": "booked"          # ← This is the label!
  }

CORRECT:
  features = {
      "patient_prior_response_rate": 0.3,  # ← Historical, before this outreach
      "patient_prior_booking_rate": 0.15    # ← Historical, before this outreach
  }
  label = 1  # ← Whether THIS outreach resulted in booking
```

### Evaluation
- **Primary metric:** PR-AUC (Precision-Recall AUC) — better for imbalanced data
- **Secondary:** ROC-AUC, calibration (Brier score)
- **Business metric:** Lift at top 20% (are we better than random?)
- **Minimum viable:** PR-AUC > 0.3 (vs random 0.15 for 15% conversion rate)

## MT.5 Optimal Contact Time Model

### Approach: Survival Analysis

Use survival analysis to model time-to-response:

```python
from lifelines import CoxPHFitter

# Features: patient demographics, prior response patterns, time of day, day of week
# Outcome: time until response (or censored if no response)

model = CoxPHFitter()
model.fit(df, duration_col='hours_to_response', event_col='responded')

# Predict optimal contact time
def get_optimal_time(patient_id):
    survival_curve = model.predict_survival_function(patient_features)
    # Find time with highest response probability
    optimal_time = find_peak(survival_curve)
    return optimal_time
```

## MT.6 Cold Start Strategy

### Phase 0: No Data
- Use deterministic rules only
- Use industry benchmarks for defaults
- Pooled data from other clinics (anonymized)

### Phase 1: < 1000 examples
- Use transfer learning from pooled data
- Fine-tune on available data
- Conservative confidence thresholds
- Heavy human review

### Phase 2: 1000-5000 examples
- Clinic-specific models
- Moderate confidence thresholds
- Reduced human review
- A/B testing for optimization

### Phase 3: 5000+ examples
- Full ML deployment
- Optimized thresholds
- Automated optimization
- Full A/B testing infrastructure

## MT.7 Champion/Challenger Pattern

```python
class ModelRegistry:
    """Manage model versions."""

    async def deploy_challenger(self, model_id: str):
        """Deploy new model as challenger."""
        model = await self.get_model(model_id)

        # Shadow test: run on live traffic, don't affect decisions
        await self.shadow_test(model, traffic_percentage=0.1)

        # Compare metrics
        if model.metrics > self.champion.metrics:
            # Promote to canary
            await self.canary_deploy(model, traffic_percentage=0.05)

            # If canary passes, full rollout
            if await self.canary_passes():
                await self.full_deploy(model)
                self.champion = model
```

## MT.8 Model Monitoring

```python
class ModelMonitor:
    """Monitor production model performance."""

    DRIFT_THRESHOLDS = {
        "prediction_drift": 0.1,  # 10% change in predictions
        "feature_drift": 0.15,    # 15% change in feature distribution
        "performance_drop": 0.05  # 5% drop in metrics
    }

    async def check_drift(self, model_id: str):
        # Compare recent predictions to training distribution
        recent_predictions = await self.get_recent_predictions(model_id)
        training_distribution = await self.get_training_distribution(model_id)

        drift_score = calculate_drift(recent_predictions, training_distribution)

        if drift_score > self.DRIFT_THRESHOLDS["prediction_drift"]:
            await self.alert_ops(f"Model drift detected: {model_id}")
            # Consider retraining or rollback
```
