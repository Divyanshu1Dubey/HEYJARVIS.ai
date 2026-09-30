# ML Training Plan
## Dataset Design, Feature Engineering, and Training Strategy

**Document:** 06 of 20  
**Purpose:** Defines how to construct training data, prevent leakage, and train production-ready models for all prediction tasks.

---

## 1. Training Philosophy

### 1.1 Core Principles

1. **Temporal splitting only.** Never split randomly. Patient interactions are time-ordered. Training on future data to predict the past is data leakage.
2. **Patient-level splits.** All interactions from one patient must be in the same split. Otherwise, the model sees the same patient in training and test, inflating metrics.
3. **Clinic-level awareness.** Models trained on pooled data must account for clinic-level variation. New clinics get calibrated models, not raw predictions.
4. **No post-outreach features in pre-outreach predictions.** Features for a prediction must only include data available at the time of the prediction.
5. **Outcome measurement.** Every prediction must eventually be matched to an outcome (responded/didn't, booked/didn't). This is the ground truth.

### 1.2 Data Requirements Summary

| Model | Minimum Records | Minimum Clinics | Minimum Positive Outcomes |
|-------|----------------|-----------------|---------------------------|
| Response probability | 10,000 | 5 | 2,000 |
| Booking probability | 10,000 | 5 | 1,000 |
| Risk score | 5,000 | 5 | 500 |
| Optimal contact time | 5,000 | 5 | N/A (time-series) |
| Cancellation reason (LLM) | 1,000 labeled | 1 | N/A (supervised) |
| Intent classification (LLM) | 2,000 labeled | 1 | N/A (supervised) |

### 1.3 Cold Start Strategy

**Before sufficient data exists (Doc 19 covers this in detail):**
- Use rules-based scoring only (Tier 1 from Doc 4).
- Use keyword-based intent classification only (Tier 1 from Doc 5).
- Collect data from day one for future model training.
- Use pooled data from similar clinics for pretrained priors.

---

## 2. Feature Engineering

### 2.1 Feature Categories

Features are grouped into four categories:

| Category | Description | Examples |
|----------|-------------|---------|
| **Patient demographics** | Static or slow-changing patient attributes | Age, gender, zip code, patient tenure |
| **Recapture context** | Features specific to this recapture opportunity | Recapture type, days since event, cancellation reason |
| **Historical behavior** | Patient's past interactions with the practice | Response rate, booking rate, no-show rate, visit frequency |
| **Temporal/environmental** | Time and context at moment of outreach | Hour, day of week, season, clinic busyness |

### 2.2 Feature Definitions

#### Patient Demographics

```python
PATIENT_DEMOGRAPHIC_FEATURES = {
    "patient_age": "integer — age at time of event",
    "patient_tenure_days": "integer — days since first visit",
    "patient_tenure_years": "float — years since first visit",
    "is_new_patient": "boolean — first visit < 90 days ago",
    "is_long_term_patient": "boolean — patient for > 3 years",
    "zip_code": "string — patient zip code",
    "distance_to_clinic_miles": "float — approximate distance",
    "insurance_type": "categorical — delta_dental, cigna, metlife, aetna, other, none",
    "has_insurance": "boolean",
    "total_lifetime_visits": "integer",
    "total_lifetime_value": "decimal",
    "avg_visit_value": "decimal",
    "last_visit_type": "categorical — hygiene, exam, procedure, emergency",
    "days_since_last_visit": "integer",
}
```

**Privacy note:** Zip code is used for distance estimation. Never store or use full address in features.

#### Recapture Context

```python
RECAPTURE_CONTEXT_FEATURES = {
    "recapture_type": "categorical — from taxonomy (41 values)",
    "recapture_type_category": "categorical — lead, booking, cancellation, no_show, treatment, recall",
    "days_since_trigger_event": "integer — age of the recapture opportunity",
    "cancellation_reason": "categorical — if applicable",
    "treatment_type": "categorical — if applicable",
    "treatment_cost": "decimal — if applicable",
    "treatment_urgency": "categorical — routine, moderate, urgent, emergency",
    "lead_source": "categorical — web_form, phone, web_chat, referral, landing_page",
    "service_interest": "categorical — if known",
    "appointment_type": "categorical — if applicable",
    "provider_id": "uuid — if applicable",
    "slot_time_of_day": "categorical — morning, afternoon, evening — for hold expiration",
    "is_after_hours_lead": "boolean",
    "is_weekend_lead": "boolean",
}
```

#### Historical Behavior

```python
HISTORICAL_BEHAVIOR_FEATURES = {
    # Response history
    "total_outreach_received": "integer — all-time count",
    "outreach_last_30d": "integer — count in last 30 days",
    "outreach_last_90d": "integer — count in last 90 days",
    "response_rate_all_time": "float — 0.0 to 1.0",
    "response_rate_last_90d": "float",
    "avg_response_time_hours": "float — average hours to respond",
    "days_since_last_response": "integer",
    "never_responded": "boolean",

    # Booking history
    "total_booked": "integer — all-time appointments booked",
    "booking_rate": "float — booked / offered",
    "booking_rate_after_response": "float",
    "cancellation_rate": "float — cancelled / booked",
    "no_show_rate": "float — no_shows / confirmed",
    "total_no_shows": "integer",
    "total_cancellations": "integer",
    "reschedule_rate": "float",

    # Treatment history
    "treatment_plans_accepted": "integer",
    "treatment_plans_scheduled": "integer",
    "treatment_plan_schedule_rate": "float",
    "has_pending_treatment": "boolean",

    # Recall history
    "recall_response_rate": "float",
    "recall_appointments_attended": "integer",
    "recall_appointments_missed": "integer",

    # Channel preferences
    "preferred_channel": "categorical",
    "sms_response_rate": "float",
    "email_response_rate": "float",
    "voice_response_rate": "float",
    "has_sms_consent": "boolean",
    "has_email_consent": "boolean",
    "has_voice_consent": "boolean",

    # Sentiment/complaint
    "has_complaint_history": "boolean",
    "has_negative_review": "boolean",
    "opted_out_before": "boolean",
    "opted_out_count": "integer",
}
```

#### Temporal/Environmental

```python
TEMPORAL_FEATURES = {
    "hour_of_day": "integer — 0-23 (in patient timezone)",
    "day_of_week": "integer — 0-6 (Monday=0)",
    "is_weekend": "boolean",
    "month": "integer — 1-12",
    "is_holiday": "boolean — US federal holidays",
    "is_january": "boolean — new year effect",
    "clinic_busyness": "float — % of slots booked that day",
    "days_until_next_holiday": "integer",
}
```

### 2.3 Feature Snapshot Rules

**Critical: Features must represent the state of the world at the TIME OF PREDICTION, not at the time of outcome measurement.**

```python
def build_features(patient_id, prediction_time, recapture_type) -> FeatureVector:
    """
    Build feature vector for a prediction.

    All features are computed AS OF prediction_time.
    No future information is included.
    """
    patient = get_patient_as_of(patient_id, prediction_time)
    history = get_history_as_of(patient_id, prediction_time)
    context = get_recapture_context(patient_id, prediction_time)

    return FeatureVector(
        # Patient features (as of prediction_time)
        patient_age=patient.age_at(prediction_time),
        patient_tenure_days=patient.tenure_at(prediction_time),

        # Historical features (up to prediction_time, NOT including)
        response_rate=history.response_rate_up_to(prediction_time),
        outreach_last_30d=history.count(prediction_time - 30d, prediction_time),
        # Note: count UP TO prediction_time, not including future outreach

        # Context features
        recapture_type=context.recapture_type,
        days_since_trigger=(prediction_time - context.trigger_time).days,
    )
```

**Anti-leakage rules:**
1. Never include features from after `prediction_time`.
2. Never include the outcome being predicted (e.g., don't include `patient_replied` when predicting `response_probability`).
3. Never include features derived from the test set when training.
4. Patient-level splits ensure no patient appears in both training and test.

---

## 3. Dataset Construction

### 3.1 Example: Response Probability Dataset

**Objective:** Predict whether a patient will respond to a recapture outreach message.

**Positive example:** Patient received outreach AND replied within 48 hours.  
**Negative example:** Patient received outreach AND did not reply within 48 hours.  
**Excluded:** Patient received outreach but opted out (censored — not a true negative).

```python
def build_response_dataset(start_date, end_date) -> pd.DataFrame:
    """
    Build dataset for response probability prediction.

    Each row = one outreach attempt.
    Label = 1 if patient replied within 48h, 0 if no reply within 48h.
    """
    # Get all outreach attempts in the time range
    attempts = db.query(CampaignAttempt).filter(
        CampaignAttempt.sent_at >= start_date,
        CampaignAttempt.sent_at <= end_date,
        CampaignAttempt.status == "sent",
    ).all()

    rows = []
    for attempt in attempts:
        prediction_time = attempt.sent_at

        # Determine label
        reply = db.query(Message).filter(
            Message.patient_id == attempt.patient_id,
            Message.direction == "inbound",
            Message.created_at > prediction_time,
            Message.created_at <= prediction_time + timedelta(hours=48),
        ).first()

        # Check for opt-out during window (censored)
        opt_out = db.query(OptOut).filter(
            OptOut.patient_id == attempt.patient_id,
            OptOut.created_at > prediction_time,
            OptOut.created_at <= prediction_time + timedelta(hours=48),
        ).first()

        if opt_out:
            continue  # Censored — skip

        label = 1 if reply else 0

        # Build features (AS OF prediction_time)
        features = build_features(attempt.patient_id, prediction_time, attempt.recapture_type)

        rows.append({
            "attempt_id": attempt.id,
            "patient_id": attempt.patient_id,
            "tenant_id": attempt.tenant_id,
            "prediction_time": prediction_time,
            "label": label,
            **features.to_dict(),
        })

    return pd.DataFrame(rows)
```

### 3.2 Example: Booking Probability Dataset

**Objective:** Predict whether a patient will book an appointment after responding.

**Positive example:** Patient responded to outreach AND booked an appointment within 14 days.  
**Negative example:** Patient responded to outreach AND did not book within 14 days.  
**Note:** This dataset is a SUBSET of the response dataset — only patients who responded.

```python
def build_booking_dataset(start_date, end_date) -> pd.DataFrame:
    """
    Build dataset for booking probability prediction.

    Each row = one response to outreach.
    Label = 1 if patient booked within 14 days, 0 if no booking within 14 days.
    """
    # Get all patient replies in the time range
    replies = db.query(Message).filter(
        Message.direction == "inbound",
        Message.created_at >= start_date,
        Message.created_at <= end_date,
    ).all()

    rows = []
    for reply in replies:
        response_time = reply.created_at

        # Find the outreach that prompted this reply
        outreach = db.query(CampaignAttempt).filter(
            CampaignAttempt.patient_id == reply.patient_id,
            CampaignAttempt.sent_at <= response_time,
            CampaignAttempt.sent_at >= response_time - timedelta(hours=72),  # Within 72h window
        ).order_by(CampaignAttempt.sent_at.desc()).first()

        if not outreach:
            continue  # Can't link to outreach

        # Determine label
        booking = db.query(Appointment).filter(
            Appointment.patient_id == reply.patient_id,
            Appointment.created_at > response_time,
            Appointment.created_at <= response_time + timedelta(days=14),
        ).first()

        label = 1 if booking else 0

        # Build features (AS OF response_time)
        features = build_features(reply.patient_id, response_time, outreach.recapture_type)

        rows.append({
            "reply_id": reply.id,
            "patient_id": reply.patient_id,
            "tenant_id": reply.tenant_id,
            "response_time": response_time,
            "label": label,
            **features.to_dict(),
        })

    return pd.DataFrame(rows)
```

### 3.3 Example: Risk Score Dataset

**Objective:** Predict likelihood of negative outcome from outreach.

**Negative outcomes (any of these = positive label):**
- Patient files complaint
- Patient leaves negative review
- Patient opts out after outreach
- Staff must handoff conversation
- Patient books then immediately cancels (within 24h)

```python
def build_risk_dataset(start_date, end_date) -> pd.DataFrame:
    """
    Build dataset for risk scoring.

    Each row = one outreach attempt.
    Label = 1 if any negative outcome occurs within 7 days.
    """
    attempts = get_outreach_attempts(start_date, end_date)

    rows = []
    for attempt in attempts:
        prediction_time = attempt.sent_at

        # Check for negative outcomes in 7-day window
        complaint = db.query(Complaint).filter(
            Complaint.patient_id == attempt.patient_id,
            Complaint.created_at > prediction_time,
            Complaint.created_at <= prediction_time + timedelta(days=7),
        ).first()

        opt_out = db.query(OptOut).filter(
            OptOut.patient_id == attempt.patient_id,
            OptOut.created_at > prediction_time,
            OptOut.created_at <= prediction_time + timedelta(days=7),
        ).first()

        handoff = db.query(HumanHandoff).filter(
            HumanHandoff.patient_id == attempt.patient_id,
            HumanHandoff.created_at > prediction_time,
            HumanHandoff.created_at <= prediction_time + timedelta(days=7),
        ).first()

        quick_cancel = db.query(Appointment).filter(
            Appointment.patient_id == attempt.patient_id,
            Appointment.created_at > prediction_time,
            Appointment.created_at <= prediction_time + timedelta(days=7),
            Appointment.status == "cancelled",
        ).first()

        label = 1 if any([complaint, opt_out, handoff, quick_cancel]) else 0

        features = build_features(attempt.patient_id, prediction_time, attempt.recapture_type)
        rows.append({"label": label, **features.to_dict()})

    return pd.DataFrame(rows)
```

### 3.4 Label Quality

**Label definition must be precise and consistent.**

| Dataset | Positive Label | Negative Label | Excluded |
|---------|---------------|----------------|----------|
| Response | Replied within 48h | No reply within 48h | Opted out within 48h |
| Booking | Booked within 14d | No booking within 14d | Opted out within 14d |
| Risk | Negative outcome within 7d | No negative outcome within 7d | Patient deactivated |

**Hard negatives:** Examples that look like positives but are not.
- Patient replied but didn't book (for booking model: negative)
- Patient said "stop" but is actually asking about stopping a specific service (for intent: tricky boundary)
- Patient asked about availability but for a different service (for recapture: still a response)

**Missing data:**
- Missing features → impute with sentinel value (-999) or domain-appropriate default (median for numeric, "unknown" for categorical).
- Missing labels → exclude from that model's dataset.

**Class imbalance:**
- Response rate is typically 15-25%. Use class weights or SMOTE for training. Evaluate on precision-recall AUC, not just ROC AUC.

---

## 4. Dataset Splits

### 4.1 Temporal Split (MANDATORY)

```
Data from Jan 2024 - Sep 2024  →  Training set (80%)
Data from Oct 2024 - Nov 2024  →  Validation set (10%)
Data from Dec 2024             →  Test set (10%)
```

**Never random shuffle.** Time-ordered data must be split chronologically. A random shuffle would leak future information into training.

### 4.2 Patient-Level Split

Within the temporal split, ensure no patient appears in more than one split:

```python
def temporal_patient_split(df, train_end, val_end):
    """
    Split by time, ensuring patient-level isolation.
    """
    # First, assign each patient to a split based on their FIRST appearance
    patient_first_appearance = df.groupby("patient_id")["prediction_time"].min()

    train_patients = patient_first_appearance[patient_first_appearance <= train_end].index
    val_patients = patient_first_appearance[(patient_first_appearance > train_end) & (patient_first_appearance <= val_end)].index
    test_patients = patient_first_appearance[patient_first_appearance > val_end].index

    train = df[df["patient_id"].isin(train_patients)]
    val = df[df["patient_id"].isin(val_patients)]
    test = df[df["patient_id"].isin(test_patients)]

    return train, val, test
```

### 4.3 Clinic-Level Considerations

For pooled models (trained across multiple clinics):

```python
def clinic_stratified_split(df):
    """
    Ensure each split has representative clinic distribution.
    """
    # Group by clinic
    clinics = df["tenant_id"].unique()

    # Stratified sampling
    train_clinics, remaining = train_test_split(clinics, test_size=0.2, random_state=42)
    val_clinics, test_clinics = train_test_split(remaining, test_size=0.5, random_state=42)

    train = df[df["tenant_id"].isin(train_clinics)]
    val = df[df["tenant_id"].isin(val_clinics)]
    test = df[df["tenant_id"].isin(test_clinics)]

    return train, val, test
```

**Important:** For new clinics not in the training data, the model will produce out-of-distribution predictions. This is handled by:
1. Calibration using pooled priors.
2. Confidence scoring — low confidence predictions are flagged.
3. Fallback to rules-based scoring when confidence is too low.

---

## 5. Model Training

### 5.1 Response Probability Model

**Model:** Gradient Boosting Classifier (XGBoost or LightGBM)

**Hyperparameters:**
```python
XGB_PARAMS = {
    "n_estimators": 200,
    "max_depth": 5,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary:logistic",
    "eval_metric": "aucpr",  # Precision-Recall AUC (better for imbalanced data)
    "scale_pos_weight": compute_scale_pos_weight(y_train),  # Handle imbalance
    "early_stopping_rounds": 20,
}
```

**Training:**
```python
model = XGBClassifier(**XGB_PARAMS)
model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=False,
)
```

**Calibration:**
```python
from sklearn.calibration import CalibratedClassifierCV

calibrator = CalibratedClassifierCV(model, method="isotonic", cv="prefit")
calibrator.fit(X_val, y_val)
```

**Evaluation metrics:**
```python
metrics = {
    "roc_auc": roc_auc_score(y_test, y_pred_proba),
    "pr_auc": average_precision_score(y_test, y_pred_proba),
    "brier_score": brier_score_loss(y_test, y_pred_proba),
    "calibration_error": expected_calibration_error(y_test, y_pred_proba),
    "precision_at_10": precision_at_k(y_test, y_pred_proba, k=10),
    "precision_at_50": precision_at_k(y_test, y_pred_proba, k=50),
    "recall_at_10": recall_at_k(y_test, y_pred_proba, k=10),
}

# Targets:
# roc_auc: > 0.75
# pr_auc: > 0.40
# brier_score: < 0.15
# calibration_error: < 0.05
# precision_at_10: > 0.40 (top 10 predictions)
# precision_at_50: > 0.25 (top 50 predictions)
```

### 5.2 Booking Probability Model

Same architecture as response model, but trained on the subset of patients who responded.

**Key difference:** Positive rate is higher (~30-40% of responders book), so class weight is lower.

### 5.3 Risk Score Model

Same architecture, but with different feature set focused on:
- Prior complaint history
- Opt-out history
- No-show history
- Recent negative interactions
- Sentiment from recent conversations

### 5.4 Optimal Contact Time Model

**Approach:** Survival analysis with time-varying covariates.

Instead of binary classification, model the time-to-response as a function of hour and day.

```python
# Simplified approach: Train a model per hour-of-day
for hour in range(24):
    # For each hour, create a binary dataset:
    # Positive = patient responded when contacted at this hour
    # Negative = patient did not respond when contacted at this hour
    train_hour_model(hour, X, y)

# At prediction time, score all 24 hours and pick the best
def predict_best_hour(patient_features):
    scores = {}
    for hour in range(24):
        scores[hour] = hour_models[hour].predict_proba(patient_features)[0, 1]
    return max(scores, key=scores.get)
```

---

## 6. Feature Importance & Explainability

### 6.1 Global Feature Importance

```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Summary plot
shap.summary_plot(shap_values, X_test)

# Feature importance ranking
mean_shap = np.abs(shap_values).mean(axis=0)
importance = pd.Series(mean_shap, index=feature_names).sort_values(ascending=False)
```

**Expected top features (by importance):**
1. Recapture type (different types have very different conversion rates)
2. Days since trigger event (freshness matters)
3. Patient response rate (past behavior predicts future behavior)
4. Prior booking rate
5. Channel consent status
6. Time of day
7. Day of week
8. Season
9. Patient tenure
10. Treatment type (for treatment recapture)

### 6.2 Per-Prediction Explanation

For each scoring decision, store the top contributing features:

```python
def explain_prediction(model, features, top_k=5) -> Explanation:
    shap_values = explainer.shap_values(features)
    contributions = list(zip(feature_names, shap_values, features))
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)

    return Explanation(
        score=model.predict_proba(features)[0, 1],
        top_factors=[
            {
                "feature": name,
                "value": value,
                "contribution": shap_val,
                "direction": "increases" if shap_val > 0 else "decreases",
            }
            for name, shap_val, value in contributions[:top_k]
        ],
    )
```

**Usage:**
- Dashboard displays top factors for each opportunity.
- Staff can understand why a patient is high/low priority.
- Model debugging: identify unexpected feature contributions.
- Compliance: explain automated decisions.

---

## 7. Model Evaluation

### 7.1 Offline Evaluation

```python
class ModelEvaluator:
    def evaluate(self, model, X_test, y_test) -> EvaluationReport:
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        return EvaluationReport(
            roc_auc=roc_auc_score(y_test, y_proba),
            pr_auc=average_precision_score(y_test, y_proba),
            brier=brier_score_loss(y_test, y_proba),
            calibration=expected_calibration_error(y_test, y_proba),
            confusion_matrix=confusion_matrix(y_test, y_pred),
            classification_report=classification_report(y_test, y_pred, output_dict=True),
            # Business metrics
            precision_at_10=precision_at_k(y_test, y_proba, 10),
            precision_at_50=precision_at_k(y_test, y_proba, 50),
            lift_at_10=lift_at_k(y_test, y_proba, 10),
        )
```

### 7.2 Online Evaluation

Offline metrics are necessary but not sufficient. Models must be evaluated in production:

1. **Holdout cohort:** 5% of patients are randomly assigned to rules-only scoring. Compare rules vs ML outcomes.
2. **A/B tests:** Doc 4 describes the experiment framework.
3. **Drift monitoring:** Doc 4 describes drift detection.
4. **Outcome tracking:** Every scored opportunity must eventually have a tracked outcome.

---

## 8. Retraining Pipeline

```python
class RetrainingPipeline:
    """
    Automated retraining pipeline.
    Runs weekly for response/booking models, monthly for risk model.
    """

    def run(self, model_id):
        model = ModelRegistry.get(model_id)

        # 1. Extract latest data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)  # Use 90 days of data

        data = self.extract_training_data(model.task, start_date, end_date)

        # 2. Validate data quality
        quality_report = self.validate_data(data)
        if quality_report.issues:
            alert_oncall(f"Data quality issues: {quality_report.issues}")

        # 3. Split data
        train, val, test = temporal_patient_split(data)

        # 4. Train model
        new_model = self.train(model.task, train, val)

        # 5. Evaluate
        eval_report = self.evaluate(new_model, test)

        # 6. Compare to production
        if eval_report.improves_over(model):
            # 7. Shadow test (run alongside production for 1 week)
            self.deploy_shadow(new_model, model)

            # 8. Register new version
            ModelRegistry.create_version(
                model_id=model_id,
                model=new_model,
                metrics=eval_report.metrics,
            )
```

---

## 9. Dataset Examples for LLM Training

### 9.1 Intent Classification Training Data

```python
INTENT_TRAINING_DATA = [
    {
        "message": "I want to book a cleaning",
        "intent": "book_appointment",
        "entities": {"service": "cleaning"},
        "urgency": "low",
    },
    {
        "message": "I need to cancel my appointment tomorrow",
        "intent": "cancel",
        "entities": {"time": "tomorrow"},
        "urgency": "medium",
    },
    {
        "message": "Do you accept Delta Dental?",
        "intent": "insurance_question",
        "entities": {"insurance": "Delta Dental"},
        "urgency": "low",
    },
    {
        "message": "My tooth is killing me and my face is swelling",
        "intent": "emergency",
        "entities": {"symptom": "pain", "symptom": "swelling"},
        "urgency": "emergency",
    },
    {
        "message": "Can I speak to a real person please",
        "intent": "human_handoff",
        "entities": {},
        "urgency": "low",
    },
    # ... minimum 2000 examples covering:
    # - All intent categories
    # - Typos, abbreviations, informal language
    # - Spanish language examples (es)
    # - Multi-intent messages
    # - Edge cases (empty, very short, very long)
]
```

**Label quality:** Each example must be labeled by at least 2 annotators. Disagreements are resolved by a third annotator. Inter-annotator agreement target: Cohen's kappa > 0.85.

### 9.2 Cancellation Reason Classification

```python
CANCELLATION_TRAINING_DATA = [
    {
        "text": "I have a work meeting that came up",
        "reason": "schedule_conflict",
        "confidence": "high",
    },
    {
        "text": "It's too expensive",
        "reason": "price",
        "confidence": "high",
    },
    {
        "text": "I'm not sure my insurance covers this",
        "reason": "insurance",
        "confidence": "medium",
    },
    {
        "text": "I'm scared of the dentist",
        "reason": "fear_anxiety",
        "confidence": "high",
    },
    {
        "text": "My car broke down",
        "reason": "transportation",
        "confidence": "high",
    },
    {
        "text": "Something came up",
        "reason": "no_explanation",
        "confidence": "high",
    },
    # ... minimum 1000 examples
    # Include ambiguous cases (low confidence labels)
    # Include edge cases (empty string, single word)
]
```

**Label confidence:** Each labeled example includes a confidence score. During training, low-confidence labels are weighted less or excluded.

---

## 10. Data Leakage Prevention Checklist

Before training any model, verify:

- [ ] All features are computed AS OF the prediction time, not the outcome time.
- [ ] No patient appears in both training and test sets.
- [ ] No clinic appears in both training and test sets (for pooled models).
- [ ] The split is temporal, not random.
- [ ] The label is computed AFTER the prediction time with a defined observation window.
- [ ] No features derived from the test set were used during training.
- [ ] Categorical features are encoded using only training data statistics.
- [ ] Scaling/normalization uses only training data statistics.
- [ ] No patient identifiers (name, phone, email) are used as features.
- [ ] No message content is used as a direct feature (use derived features like length, sentiment instead).
