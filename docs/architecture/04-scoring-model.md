# Recovery Scoring Model
## Recapture Priority, Conversion Probability & Risk

**Document:** 04 of 20  
**Purpose:** Defines how the system scores each recapture opportunity, ranks patients, and estimates outcomes.

---

## 1. Scoring Objectives

When the system identifies a recapture opportunity, it must answer:

1. **How likely is this patient to respond?** (response_probability)
2. **How likely is this patient to book if they respond?** (conversion_probability)
3. **What is the overall recapture priority?** (recapture_priority_score)
4. **What is the risk of negative outcome?** (risk_score)
5. **What is the likelihood human staff will need to intervene?** (handoff_probability)
6. **Which channel is best?** (recommended_channel)
7. **When should we contact?** (recommended_time)
8. **What messaging strategy?** (recommended_strategy)

---

## 2. Scoring Architecture

The scoring system has two tiers:

**Tier 1: Rules-Based (Deterministic) — Always runs, always available.**

Used for:
- Initial scoring when no model data exists
- Baseline scoring alongside ML models
- Safety and compliance constraints
- Cold start (new clinics)

**Tier 2: ML-Assisted (Probabilistic) — Runs when model is available and calibrated.**

Used for:
- Refining priority scores
- Personalizing channel and timing
- Predicting response and conversion
- Risk scoring

**Both tiers run. The rules-based score is the floor. ML can only increase priority, never decrease below the rules floor.**

---

## 3. Rules-Based Scoring (Tier 1)

### 3.1 Base Score by Recapture Type

Different recapture opportunities have different baseline conversion rates. The rules engine assigns base scores based on the recapture taxonomy.

```python
BASE_SCORES = {
    # High-value, high-intent
    "treatment_plan_accepted_unscheduled": 85,
    "crown_implant_root_canal_unscheduled": 90,
    "orthodontic_unscheduled": 88,
    "slot_selected_not_confirmed": 82,
    "treatment_estimate_sent_no_response": 80,

    # Medium-high value
    "cancellation_scheduling_conflict": 75,
    "cancellation_price": 70,
    "no_show_first": 72,
    "no_show_repeat": 65,
    "booking_flow_abandoned": 68,
    "web_chat_abandoned": 65,

    # Medium
    "lead_form_no_response": 55,
    "website_lead_no_response": 50,
    "missed_call": 55,
    "after_hours_lead": 52,
    "patient_asked_about_service": 58,
    "patient_requested_price": 60,
    "patient_requested_availability": 62,
    "patient_insurance_question": 55,

    # Lower
    "recall_hygiene_overdue": 40,
    "recall_exam_overdue": 45,
    "inactive_12_months": 35,
    "inactive_18_months": 25,
    "long_term_inactive": 15,
    "overdue_continuing_care": 42,
}
```

### 3.2 Score Modifiers

The base score is adjusted by a series of modifiers. Each modifier is additive.

#### Urgency Modifier

```python
URGENCY_MODIFIERS = {
    # Cancellation reasons
    "cancellation_reason_pain": +15,
    "cancellation_reason_emergency": +20,
    "cancellation_reason_schedule_conflict": +5,
    "cancellation_reason_price": -5,
    "cancellation_reason_insurance": +5,
    "cancellation_reason_fear": +5,
    "cancellation_reason_transportation": -5,
    "cancellation_reason_no_explanation": 0,

    # Treatment urgency
    "treatment_type_emergency": +20,
    "treatment_type_root_canal": +15,
    "treatment_type_extraction": +12,
    "treatment_type_crown": +10,
    "treatment_type_implant": +10,
    "treatment_type_orthodontic": +5,
    "treatment_type_cosmetic": +3,
    "treatment_type_cleaning": 0,
}
```

#### Patient History Modifier

```python
HISTORY_MODIFIERS = {
    "previous_response_rate_high": +10,    # Responded to 70%+ of outreach
    "previous_response_rate_medium": +5,   # Responded to 30-70%
    "previous_response_rate_low": -10,     # Responded to <30%
    "previous_booking_rate_high": +10,     # Booked after 60%+ of responses
    "previous_booking_rate_medium": +5,    # Booked after 30-60%
    "previous_booking_rate_low": -5,       # Booked after <30%
    "no_show_history": -10,                # Has no-showed before
    "repeat_cancellations": -15,           # 3+ cancellations
    "first_time_patient": +5,              # New to practice (more lenient)
    "long_term_patient": +8,               # Been coming for years
    "high_lifetime_value": +10,            # Top 20% of patient value
}
```

#### Timing Modifier

```python
TIMING_MODIFIERS = {
    "lead_age_0_1_days": +15,       # Very fresh lead
    "lead_age_1_3_days": +10,       # Still warm
    "lead_age_3_7_days": +5,        # Getting cold
    "lead_age_7_14_days": 0,        # Cold
    "lead_age_14_30_days": -10,     # Very cold
    "lead_age_30_plus_days": -20,   # Stale

    "cancellation_within_24h": +15, # Cancelled very recently
    "cancellation_1_3_days": +10,
    "cancellation_3_7_days": +5,
    "cancellation_7_plus_days": 0,

    "no_show_within_24h": +10,
    "no_show_1_3_days": +5,
    "no_show_3_plus_days": 0,

    "treatment_plan_0_7_days": +10, # Recently accepted
    "treatment_plan_7_14_days": +5,
    "treatment_plan_14_30_days": 0,
    "treatment_plan_30_plus_days": -10,

    "recall_0_7_days_overdue": +5,
    "recall_7_30_days_overdue": 0,
    "recall_30_90_days_overdue": -5,
    "recall_90_plus_days": -15,
}
```

#### Channel Preference Modifier

```python
CHANNEL_MODIFIERS = {
    "preferred_channel_match": +15,
    "preferred_channel_available": +5,
    "preferred_channel_no_consent": -20,  # Penalize if preferred channel unavailable
    "sms_consented": +5,
    "email_consented": +3,
    "voice_consented": +5,
}
```

#### Seasonality Modifier

```python
SEASONALITY_MODIFIERS = {
    "january_new_year": +5,          # People think about health in January
    "back_to_school_august": +3,
    "holiday_season_december": -5,   # People are busy
    "summer_june_july": -3,          # Vacations
}
```

### 3.3 Final Rules-Based Score Calculation

```python
def calculate_rules_score(recapture_opportunity) -> float:
    """Calculate the deterministic rules-based score (0-100)."""

    # Start with base score for recapture type
    score = BASE_SCORES.get(recapture_opportunity.recapture_type, 50)

    # Apply urgency modifiers
    if recapture_opportunity.cancellation_reason:
        score += URGENCY_MODIFIERS.get(f"cancellation_reason_{recapture_opportunity.cancellation_reason}", 0)

    if recapture_opportunity.treatment_type:
        score += URGENCY_MODIFIERS.get(f"treatment_type_{recapture_opportunity.treatment_type}", 0)

    # Apply timing modifiers
    age_days = recapture_opportunity.age_days
    if recapture_opportunity.recapture_type.startswith("cancellation"):
        score += TIMING_MODIFIERS.get(f"cancellation_{_timing_bucket(age_days)}", 0)
    elif recapture_opportunity.recapture_type.startswith("lead"):
        score += TIMING_MODIFIERS.get(f"lead_age_{_timing_bucket(age_days)}", 0)
    elif recapture_opportunity.recapture_type.startswith("no_show"):
        score += TIMING_MODIFIERS.get(f"no_show_{_timing_bucket(age_days)}", 0)
    elif recapture_opportunity.recapture_type.startswith("treatment"):
        score += TIMING_MODIFIERS.get(f"treatment_plan_{_timing_bucket(age_days)}", 0)
    elif recapture_opportunity.recapture_type.startswith("recall"):
        score += TIMING_MODIFIERS.get(f"recall_{_timing_bucket(age_days)}", 0)

    # Apply patient history modifiers
    score += HISTORY_MODIFIERS.get(_get_response_rate_bucket(recapture_opportunity.patient_id), 0)
    score += HISTORY_MODIFIERS.get(_get_booking_rate_bucket(recapture_opportunity.patient_id), 0)

    # Apply channel preference modifier
    score += CHANNEL_MODIFIERS.get(_get_channel_preference_score(recapture_opportunity), 0)

    # Apply seasonality
    score += SEASONALITY_MODIFIERS.get(_get_seasonality_bucket(), 0)

    # Clamp to 0-100
    return max(0, min(100, score))
```

**Rules score is ALWAYS computed. It is the baseline priority.**

---

## 4. ML-Assisted Scoring (Tier 2)

### 4.1 When ML Is Justified

ML models are introduced when ALL of the following are true:
1. The clinic has at least 500 completed patient interaction records.
2. The clinic has been active for at least 3 months.
3. There is sufficient outcome data (at least 50 completed recapture outcomes).
4. The rules-based model shows suboptimal calibration (predicted vs actual conversion differs by >15%).

Before these thresholds, rules-only scoring is used.

### 4.2 ML Models

#### Model A: Response Probability

**Predicts:** Will the patient respond to outreach?

**Inputs:**
- Recapture type (categorical)
- Patient age group
- Days since trigger event
- Prior response rate (patient-level)
- Prior response rate (clinic-level, for similar recapture types)
- Channel
- Time of day
- Day of week
- Message length (from template)
- Personalization level
- Prior number of attempts
- Season

**Output:** `response_probability` (0.0 to 1.0)

**Model:** Gradient boosting classifier (XGBoost/LightGBM)

**Why GBM over logistic regression:**
- Non-linear interactions between features (e.g., age × recapture type)
- Handles categorical features well with proper encoding
- Robust to missing data
- Produces well-calibrated probabilities with isotonic regression

**Training data size:** 50K+ examples across multiple clinics (pooled, de-identified)

#### Model B: Conversion Probability

**Predicts:** If the patient responds, will they book?

**Inputs:**
- Recapture type
- Treatment type (if applicable)
- Prior booking rate (patient-level)
- Prior booking rate (clinic-level)
- Insurance status
- Distance to clinic (if available)
- Patient lifetime value
- Channel
- Message strategy
- Slot availability at time of outreach

**Output:** `booking_probability` (0.0 to 1.0)

**Model:** Gradient boosting classifier

#### Model C: Overall Recapture Priority Score

**Predicts:** Combined score for ranking patients in a campaign queue.

**Formula:**
```
recapture_priority = rules_score * 0.4
                   + response_probability * 30
                   + booking_probability * 30
```

**Rationale:** The rules score (40% weight) ensures safety, compliance, and clinical judgment are always represented. The ML components (60%) add data-driven optimization.

**Ranking:** Patients are ranked by `recapture_priority` within each campaign. The campaign runner processes highest-priority patients first.

#### Model D: Risk Score

**Predicts:** Likelihood of negative outcome from outreach.

**Negative outcomes:**
- Patient complaint
- Negative review
- Opt-out
- Staff escalation (handoff)
- No-show if rebooked

**Inputs:**
- Prior complaint history
- Prior opt-out rate
- No-show history
- Recent negative sentiment (from conversation)
- Number of recent contacts
- Time since last negative interaction

**Output:** `risk_score` (0.0 to 1.0)

**Model:** Gradient boosting classifier

**Usage:**
- If `risk_score > 0.7`: Add human review step before sending
- If `risk_score > 0.9`: Suppress automated outreach, staff-only

#### Model E: Optimal Contact Time

**Predicts:** Best time to contact this patient.

**Output:** `recommended_hour` (0-23), `recommended_day_of_week` (0-6)

**Model:** Survival analysis / time-to-response model

**Approach:** For each patient, estimate the probability density of response across hours/days. Select the time with highest expected response probability, subject to quiet hours and business hours constraints.

---

## 5. Confidence Calibration

ML model outputs must be calibrated so that a score of 0.8 means ~80% actual probability.

**Calibration method:**
1. Train model on training set.
2. Fit isotonic regression on validation set predictions.
3. Apply calibration to production predictions.
4. Re-calibrate quarterly or when distribution shift detected.

**Confidence tiers:**
```python
CONFIDENCE_TIERS = {
    "high": (0.8, 1.0),    # Model has seen many similar patients
    "medium": (0.5, 0.8),  # Moderate similarity to training data
    "low": (0.0, 0.5),     # Novel patient — rely more on rules
}
```

**Low-confidence handling:**
- When ML confidence is low, the rules score has higher weight.
- When ML confidence is very low (< 0.3), ML score is ignored entirely.
- Low-confidence predictions are flagged for human review.

---

## 6. Score Integration

### Final Score Calculation

```python
def calculate_final_score(opportunity, ml_scores=None) -> RecaptureScore:
    """
    Combine rules-based and ML scores into final priority score.

    If ml_scores is None (no model available), rules score is used alone.
    """

    # Always compute rules score
    rules_score = calculate_rules_score(opportunity)

    if ml_scores is None:
        # No ML available — use rules only
        return RecaptureScore(
            recapture_priority_score=rules_score,
            confidence_tier="rules_only",
            confidence=1.0,  # Rules are deterministic
            response_probability=None,
            booking_probability=None,
            risk_score=None,
            recommended_channel=_default_channel(opportunity),
            recommended_time=_default_time(opportunity),
            recommended_strategy=_default_strategy(opportunity),
            handoff_probability=None,
        )

    # ML available — blend scores
    response_prob = ml_scores.response_probability
    booking_prob = ml_scores.booking_probability
    risk = ml_scores.risk_score

    # Confidence-weighted blending
    ml_confidence = ml_scores.confidence

    if ml_confidence < 0.3:
        # Too uncertain — use rules
        final_score = rules_score
        confidence_tier = "low"
    elif ml_confidence < 0.5:
        # Blend with high rules weight
        final_score = rules_score * 0.7 + (response_prob * 30 + booking_prob * 30) * 0.3
        confidence_tier = "medium"
    else:
        # Full blend
        final_score = rules_score * 0.4 + (response_prob * 30 + booking_prob * 30) * 0.6
        confidence_tier = "high"

    # Risk adjustment — reduce score if high risk
    if risk and risk > 0.7:
        final_score *= 0.5  # Halve the priority
        recommended_strategy = "conservative"
    elif risk and risk > 0.5:
        final_score *= 0.75
        recommended_strategy = "standard_with_review"

    # Clamp
    final_score = max(0, min(100, final_score))

    # Determine recommended channel
    recommended_channel = ml_scores.recommended_channel or _default_channel(opportunity)

    # Determine recommended time
    recommended_time = ml_scores.recommended_time or _default_time(opportunity)

    # Determine handoff probability
    handoff_prob = ml_scores.handoff_probability or _estimate_handoff_prob(opportunity)

    return RecaptureScore(
        recapture_priority_score=final_score,
        confidence_tier=confidence_tier,
        confidence=ml_confidence,
        response_probability=response_prob,
        booking_probability=booking_prob,
        risk_score=risk,
        recommended_channel=recommended_channel,
        recommended_time=recommended_time,
        recommended_strategy=recommended_strategy or "standard",
        handoff_probability=handoff_prob,
    )
```

---

## 7. Score Thresholds

```python
SCORE_THRESHOLDS = {
    "high_priority": 70,    # Process immediately
    "medium_priority": 40,  # Process in normal queue
    "low_priority": 20,     # Process in background / weekly batch
    "suppress": 0,          # Do not process
}
```

**Thresholds are overridable per tenant.**

---

## 8. Score Monitoring & Drift Detection

The scoring system must be monitored for drift:

1. **Calibration monitoring:** Weekly, compare predicted probabilities to actual outcomes. If calibration error > 0.1, flag for retraining.
2. **Score distribution monitoring:** Track the distribution of scores across campaigns. Sudden shifts may indicate data quality issues.
3. **Outcome tracking:** For every outreach attempt, track whether the patient responded and whether they booked. This is the ground truth for model evaluation.
4. **Model performance dashboard:**
   - AUC-ROC (target: > 0.75)
   - Brier score (target: < 0.15)
   - Calibration error (target: < 0.05)
   - Precision@K (top-K predictions — how many of the top-K actually converted?)

---

## 9. Attribution

When a recapture outreach leads to a booked appointment, the system must attribute revenue:

```python
Attribution:
  recapture_campaign_id: uuid
  recapture_opportunity_id: uuid
  appointment_id: uuid
  attributed_revenue: decimal
  attribution_model: "last_touch"  # The last outreach before booking gets credit
  attribution_confidence: "high | medium | low"
  days_from_outreach_to_booking: integer
```

**Attribution window:** 30 days from last outreach to booking. If patient books within 30 days of a recapture outreach, attribute to that campaign.

**Multi-touch attribution (future):** When a patient receives multiple outreach types, distribute credit based on a weighted model (first touch, last touch, or linear).

---

## 10. A/B Testing Infrastructure

The scoring system must support experimentation:

```python
Experiment:
  id: uuid
  tenant_id: uuid
  name: string
  description: string
  status: "draft" | "running" | "completed" | "cancelled"
  variant_a: {
      "description": "Control — current scoring",
      "scoring_config": {...}
  }
  variant_b: {
      "description": "Treatment — new scoring weights",
      "scoring_config": {...}
  }
  traffic_split: float  # 0.5 = 50/50
  start_date: datetime
  end_date: datetime
  metrics: {
      "primary": "booking_rate",
      "secondary": ["response_rate", "opt_out_rate", "revenue_per_contact"]
  }
  result: {
      "winner": "a" | "b" | "inconclusive",
      "confidence": float,
      "p_value": float
  }
```

**Experiment design:**
1. Randomly assign patients to variant A or B (stratified by recapture type).
2. Run for minimum 2 weeks or until statistical significance.
3. Compare primary metric (booking rate) and secondary metrics.
4. If variant B wins with p < 0.05 and no degradation in safety metrics, promote to default.
