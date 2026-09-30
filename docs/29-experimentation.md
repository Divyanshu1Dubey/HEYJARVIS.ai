# Experimentation — A/B Testing and Continuous Optimization

## EX.1 Experimentation Philosophy

1. **Patient safety first.** Never experiment with safety-critical behavior.
2. **Consent-respecting.** Only test with patients who have consented.
3. **Sample size matters.** Don't declare winners without statistical significance.
4. **Multiple metrics.** Look at conversion, opt-out, complaints together.
5. **Stop harmful variants.** Kill any variant that underperforms on safety or patient experience.

## EX.2 What Can Be Tested

| Variable | Example Tests | Safety Concern |
|----------|--------------|----------------|
| Message wording | "We missed you" vs "Let's reschedule" | Low |
| Timing | 2h vs 24h delay | Low |
| Channel | SMS vs Email | Low |
| CTA | "Reply YES" vs "Call us" vs "Book now" | Low |
| Personalization | Name only vs Name + last visit | Low |
| Number of attempts | 2 vs 3 attempts | Low |
| Message length | Short vs Long | Low |
| Offer framing | "We have availability" vs "Limited slots" | Medium (manipulation risk) |
| Urgency level | Gentle vs Direct | Medium |
| Safety handling | Different escalation triggers | High — **requires clinical review** |

## EX.3 What Cannot Be Tested

| Constraint | Reason |
|-----------|--------|
| Opt-out bypass | TCPA violation |
| Consent requirements | HIPAA violation |
| Frequency caps | Patient trust |
| Safety triggers | Medical safety |
| Cross-tenant data access | Privacy violation |
| Booking without confirmation | Double booking risk |
| Insurance claims | Legal liability |
| Medical advice | Malpractice risk |

## EX.4 Experiment Design

```python
class Experiment:
    """A/B test configuration."""

    id: str
    name: str
    hypothesis: str
    variant_a: Variant  # Control (current)
    variant_b: Variant  # Treatment (new)
    traffic_allocation: float  # 0.0-1.0 for variant B
    min_sample_size: int
    max_duration_days: int
    primary_metric: str
    secondary_metrics: List[str]
    guardrail_metrics: List[str]
    status: str  # draft, running, completed, killed

class Variant:
    name: str
    description: str
    config: dict  # The actual change
    traffic_percentage: float  # % of traffic
```

## EX.5 Statistical Requirements

```python
class ExperimentStats:
    """Statistical analysis for experiments."""

    MIN_SAMPLE_SIZE = 1000  # Per variant
    CONFIDENCE_LEVEL = 0.95
    MIN_EFFECT_SIZE = 0.05  # 5% relative improvement

    def calculate_sample_size(self, baseline_rate: float, mde: float):
        """Calculate required sample size."""
        from scipy.stats import norm

        alpha = 0.05  # Type I error
        power = 0.80  # 1 - Type II error

        z_alpha = norm.ppf(1 - alpha / 2)
        z_beta = norm.ppf(power)

        p1 = baseline_rate
        p2 = baseline_rate * (1 + mde)

        n = (
            (z_alpha * (2 * p1 * (1 - p1)) ** 0.5 +
             z_beta * (p1 * (1 - p1) + p2 * (1 - p2)) ** 0.5) ** 2
            / (p1 - p2) ** 2
        )

        return int(n)

    def analyze_results(self, experiment: Experiment) -> AnalysisResult:
        """Analyze experiment results."""

        control = experiment.variant_a.data
        treatment = experiment.variant_b.data

        # Calculate metrics
        control_rate = control.conversions / control.sample_size
        treatment_rate = treatment.conversions / treatment.sample_size

        # Statistical test
        from scipy.stats import chi2_contingency
        contingency = [
            [control.conversions, control.sample_size - control.conversions],
            [treatment.conversions, treatment.sample_size - treatment.conversions]
        ]
        chi2, p_value, dof, expected = chi2_contingency(contingency)

        # Effect size
        relative_lift = (treatment_rate - control_rate) / control_rate

        # Decision
        if p_value < 0.05 and relative_lift > self.MIN_EFFECT_SIZE:
            if treatment_rate > control_rate:
                recommendation = "implement_b"
            else:
                recommendation = "keep_control"
        else:
            recommendation = "inconclusive"

        return AnalysisResult(
            control_rate=control_rate,
            treatment_rate=treatment_rate,
            relative_lift=relative_lift,
            p_value=p_value,
            recommendation=recommendation,
            confidence=1 - p_value
        )
```

## EX.6 Guardrail Metrics

```python
GUARDRAIL_METRICS = {
    "opt_out_rate": {
        "threshold": 0.005,  # 0.5% max
        "action": "kill_experiment"
    },
    "complaint_rate": {
        "threshold": 0.01,  # 1% max
        "action": "kill_experiment"
    },
    "handoff_rate": {
        "threshold": 0.25,  # 25% max
        "action": "pause_and_review"
    },
    "safety_events": {
        "threshold": 1,  # Any safety event
        "action": "kill_experiment"
    },
    "response_time_p95": {
        "threshold": 5000,  # 5 seconds
        "action": "pause_and_review"
    }
}
```

## EX.7 Experiment Lifecycle

```
1. DESIGN
   - Define hypothesis
   - Define variants
   - Calculate sample size
   - Define success criteria
   - Review for safety concerns
   ↓
2. APPROVAL
   - Engineering review
   - Product review
   - Safety review (if applicable)
   ↓
3. RUNNING
   - Deploy with traffic split
   - Monitor guardrail metrics daily
   - No peeking at primary metric before sample size
   ↓
4. ANALYSIS
   - Check sample size reached
   - Calculate statistical significance
   - Review all metrics (primary + secondary + guardrail)
   ↓
5. DECISION
   - Implement winner (if significant)
   - Keep control (if not significant)
   - Kill both (if both underperform)
   ↓
6. DOCUMENT
   - Record results
   - Document learnings
   - Share with team
```

## EX.8 Common Experiment Mistakes

| Mistake | Problem | Solution |
|---------|---------|---------|
| Peeking at results | Multiple testing problem | Pre-define sample size, don't look until reached |
| Too many variants | Dilutes statistical power | Max 3 variants per experiment |
| Small sample size | False positives | Calculate sample size before starting |
| Ignoring guardrails | Patient harm | Monitor guardrails daily, kill immediately |
| Not controlling for time | Time-of-day bias | Run experiments for full weekly cycle |
| Not controlling for cohort | Patient mix bias | Randomize at patient level |
| Multiple primary metrics | p-hacking | One primary metric, others are secondary |
