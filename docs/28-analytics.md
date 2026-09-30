# Analytics — Complete Analytics and Measurement System

## AN.1 Analytics Philosophy

1. **Incremental lift, not vanity metrics.** Measure what the AI ADDED, not what would have happened anyway.
2. **Causal attribution.** Use holdout groups and experiments.
3. **Patient-centric metrics.** Don't optimize at the expense of patient experience.
4. **Actionable insights.** Every metric should lead to a decision.

## AN.2 Core Metrics

### Revenue Metrics

| Metric | Definition | Calculation | Target |
|--------|-----------|-------------|--------|
| **Revenue Recovered** | Revenue from appointments booked due to recapture | Sum of appointment values for recapture-booked appointments | Track trend |
| **Revenue per Opportunity** | Average value per recapture opportunity | Total recovered / total opportunities | > $150 |
| **Recapture ROI** | Return on recapture investment | (Recovered revenue - system cost) / system cost | > 5x |
| **Treatment Value at Risk** | Total value of unscheduled treatment plans | Sum of treatment plan values | Track |
| **LTV Recovery Rate** | % of at-risk LTV recovered | Recovered LTV / Total at-risk LTV | > 20% |

### Conversion Metrics

| Metric | Definition | Calculation | Target |
|--------|-----------|-------------|--------|
| **Recapture Rate** | % of opportunities converted | Bookings / Opportunities | > 15% |
| **Response Rate** | % of patients who respond to outreach | Responses / Outreach sent | > 20% |
| **Booking Conversion** | % of responses that book | Bookings / Responses | > 40% |
| **Time to Book** | Time from outreach to booking | Avg time from outreach to booked | < 48 hours |
| **Channel Conversion Rate** | Conversion by channel | Bookings per channel / Outreach per channel | Track & optimize |

### Operational Metrics

| Metric | Definition | Calculation | Target |
|--------|-----------|-------------|--------|
| **AI Containment Rate** | % of conversations handled without human | AI-handled / Total conversations | > 85% |
| **Human Handoff Rate** | % requiring human intervention | Handoffs / Total conversations | < 15% |
| **Handoff Resolution Time** | Time from handoff to resolution | Avg time to resolve handoffs | < 30 min |
| **Staff Time Saved** | Time saved by AI automation | Estimated from handoff reduction | Track |
| **Campaign Completion Rate** | % of campaigns reaching end state | Completed / Started | > 90% |

### Patient Experience Metrics

| Metric | Definition | Calculation | Target |
|--------|-----------|-------------|--------|
| **Opt-out Rate** | % of patients opting out | Opt-outs / Total contacted | < 0.3% |
| **Complaint Rate** | % of patients complaining | Complaints / Total contacted | < 0.5% |
| **Negative Response Rate** | % of negative responses | Negative responses / Responses | < 10% |
| **Patient Satisfaction** | Patient satisfaction score | Survey / manual review | > 4/5 |

### AI Quality Metrics

| Metric | Definition | Calculation | Target |
|--------|-----------|-------------|--------|
| **Hallucination Rate** | % of responses with fabricated content | Hallucinations / Total responses | < 1% |
| **Intent Accuracy** | % of correct intent classifications | Correct / Total classified | > 90% |
| **Tool Use Accuracy** | % of correct tool selections | Correct / Total tool calls | > 95% |
| **Safety Event Rate** | Safety escalations per 1000 conversations | Safety events / Conversations * 1000 | < 5 |
| **False Positive Rate** | Inappropriate outreaches | False positives / Total outreach | < 1% |

## AN.3 Attribution Methodology

### The Counterfactual Problem

> How do we know the AI caused the booking?

**Solution: Holdout groups**

```python
class AttributionEngine:
    """Attribute bookings to recapture efforts."""

    def attribute_booking(self, patient_id: str, booking_time: datetime):
        """Determine if booking was caused by recapture."""

        # Get recent outreach to this patient
        recent_outreach = self.get_outreach(patient_id, hours=72)

        if not recent_outreach:
            return Attribution(
                caused_by_recapture=False,
                reason="no_recent_outreach"
            )

        # Get control group prediction
        # (Would this patient have booked without outreach?)
        control_probability = self.get_control_probability(patient_id)

        # Did they book within the attribution window?
        attribution_window = timedelta(hours=72)
        booked_within_window = (
            booking_time <= recent_outreach.sent_at + attribution_window
        )

        if booked_within_window:
            # Use uplift model to estimate incrementality
            uplift = self.estimate_uplift(
                patient_id=patient_id,
                outreach=recent_outreach,
                control_prob=control_probability
            )

            return Attribution(
                caused_by_recapture=True,
                confidence=uplift.confidence,
                estimated_lift=uplift.value,
                campaign_id=recent_outreach.campaign_id
            )

        return Attribution(caused_by_recapture=False, reason="outside_window")
```

### Holdout Group Design

```python
class HoldoutGroup:
    """Randomized holdout for causal attribution."""

    def assign_patient(self, patient_id: str, campaign_id: str) -> str:
        """Assign patient to treatment or holdout group."""

        # Hash-based assignment (consistent)
        hash_input = f"{patient_id}:{campaign_id}"
        hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)

        # 10% holdout rate
        if hash_value % 10 == 0:
            return "holdout"  # Don't send outreach
        else:
            return "treatment"  # Send outreach

    def measure_lift(self, campaign_id: str):
        """Measure incremental lift from campaign."""

        treatment = self.get_patients(campaign_id, group="treatment")
        holdout = self.get_patients(campaign_id, group="holdout")

        treatment_rate = treatment.booked.count() / treatment.count()
        holdout_rate = holdout.booked.count() / holdout.count()

        absolute_lift = treatment_rate - holdout_rate
        relative_lift = absolute_lift / holdout_rate if holdout_rate > 0 else 0

        return {
            "treatment_rate": treatment_rate,
            "holdout_rate": holdout_rate,
            "absolute_lift": absolute_lift,
            "relative_lift": relative_lift,
            "confidence": self.calculate_confidence(treatment, holdout)
        }
```

## AN.4 Cohort Analysis

```python
class CohortAnalyzer:
    """Analyze patient cohorts over time."""

    def retention_curve(self, cohort_month: str):
        """Generate retention curve for a cohort."""

        patients = self.get_patients_in_cohort(cohort_month)
        months_since = range(0, 24)  # 24 months

        retention = []
        for month in months_since:
            active = self.count_active_patients(
                patients,
                months_since_cohort=month
            )
            retention.append(active / len(patients))

        return {
            "cohort": cohort_month,
            "cohort_size": len(patients),
            "retention_curve": retention
        }
```

## AN.5 Dashboards

### Executive Dashboard
- Revenue recovered (monthly, with target)
- ROI
- Active clinics
- Total patients managed
- Key trends

### Operations Dashboard
- Opportunities by category
- Outreach volume by channel
- Response rate trend
- Handoff volume and resolution time
- AI containment rate

### Campaign Dashboard
- Campaign performance table
- Funnel visualization (opportunity → outreach → response → booking)
- Channel comparison
- A/B test results

### Clinic Dashboard
- Per-clinic metrics
- Staff performance
- Patient satisfaction
- Opt-out trends

## AN.6 Report Definitions

### Daily Report (Automated)
```
Date: {date}

Outreach Summary:
- Sent: {sent_count}
- Delivered: {delivered_count} ({delivery_rate}%)
- Failed: {failed_count}
- Responses: {response_count} ({response_rate}%)

Revenue:
- Recovered: ${recovered}
- Opportunities: {opportunity_count}

AI Performance:
- Conversations: {conv_count}
- Handoffs: {handoff_count} ({handoff_rate}%)
- Safety events: {safety_count}

Top Issues:
- SMS delivery failures: {count}
- Integration errors: {count}
- High opt-out campaigns: {list}
```

### Weekly Report (Automated)
```
Week: {week}

Recapture Performance:
- Opportunities detected: {count}
- Outreach sent: {count}
- Responses received: {count}
- Bookings recovered: {count}
- Revenue recovered: ${amount}

By Category:
{category_breakdown}

By Channel:
{channel_breakdown}

AI Metrics:
- Intent accuracy: {accuracy}%
- Safety events: {count}
- Hallucination rate: {rate}%

Recommendations:
- Top performing campaigns
- Underperforming campaigns
- Suggested optimizations
```

## AN.7 Data Quality

```python
class DataQualityMonitor:
    """Monitor data quality for analytics."""

    CHECKS = {
        "appointments_without_patients": {
            "query": "SELECT COUNT(*) FROM appointments a WHERE NOT EXISTS (SELECT 1 FROM patients p WHERE p.id = a.patient_id)",
            "threshold": 0,
            "severity": "critical"
        },
        "communications_without_patients": {
            "query": "SELECT COUNT(*) FROM messages m WHERE NOT EXISTS (SELECT 1 FROM patients p WHERE p.id = m.patient_id)",
            "threshold": 0,
            "severity": "critical"
        },
        "bookings_without_outreach": {
            "query": "SELECT COUNT(*) FROM appointments a WHERE a.source = 'ai' AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.patient_id = a.patient_id)",
            "threshold": 0,  # May have legitimate bookings
            "severity": "warning"
        },
        "outcomes_missing": {
            "query": "SELECT COUNT(*) FROM recapture_attempts WHERE outcome IS NULL AND sent_at < NOW() - INTERVAL '7 days'",
            "threshold": 100,
            "severity": "warning"
        }
    }

    async def check_data_quality(self):
        issues = []
        for check_name, check in self.CHECKS.items():
            count = await self.db.scalar(check["query"])
            if count > check["threshold"]:
                issues.append({
                    "check": check_name,
                    "count": count,
                    "severity": check["severity"]
                })
        return issues
```
