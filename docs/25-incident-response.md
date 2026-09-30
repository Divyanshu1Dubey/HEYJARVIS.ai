# Incident Response — Operational Runbooks and Procedures

## IR.1 Incident Classification

| Level | Description | Examples | Response Time | Escalation |
|-------|-------------|---------|--------------|------------|
| **SEV-1** | System down / data breach / safety event | DB outage, PHI breach, safety failure | 15 min | CTO, Legal |
| **SEV-2** | Major feature broken | SMS not delivering, AI not responding | 1 hour | Engineering Lead |
| **SEV-3** | Minor degradation | Slow API, one integration down | 4 hours | On-call |
| **SEV-4** | Cosmetic / informational | Wrong dashboard number, log issue | 24 hours | Backlog |

## IR.2 Common Incident Runbooks

### RB-01: Database Outage

**Detection:** Database health check failing, API errors spiking

**Impact:** Complete system outage

**Steps:**
1. Confirm outage (check DB directly)
2. Check connection pool status
3. Check for long-running queries
4. Check disk space
5. Check replication status

**Mitigation:**
```
1. If primary down → failover to replica
   - Verify replica is current
   - Promote replica to primary
   - Update connection strings

2. If connection pool exhausted:
   - Kill long-running queries
   - Restart workers
   - Increase pool size temporarily

3. If disk full:
   - Archive old data
   - Expand storage
   - Enable log rotation
```

**Recovery:**
1. Verify system is operational
2. Check for data consistency
3. Notify stakeholders
4. Write post-mortem

### RB-02: SMS Provider Outage

**Detection:** SMS delivery rate drops, Twilio status page shows issues

**Impact:** Outbound messages not delivered

**Steps:**
1. Check Twilio status page
2. Check error logs for SMS failures
3. Check rate limit status

**Mitigation:**
```
1. Switch to backup SMS provider (if available)
   - Update routing configuration
   - Queue will retry with new provider

2. If no backup:
   - Hold messages in queue
   - Notify clinic of delay
   - Send messages when provider recovers
```

**Recovery:**
1. Monitor Twilio status page for recovery
2. Switch back to primary provider
3. Drain message queue
4. Verify all messages sent

### RB-03: LLM Provider Outage

**Detection:** AI requests failing, LLM API errors

**Impact:** AI conversations not working

**Steps:**
1. Check LLM provider status
2. Check API key validity
3. Check rate limits

**Mitigation:**
```
1. Switch to fallback LLM provider
   - Update configuration
   - Queue will retry with new provider

2. If no fallback:
   - AI conversations return to deterministic rules
   - Simple responses using templates
   - Escalate complex cases to human
   - Notify patients of delay
```

**Recovery:**
1. Monitor LLM provider status
2. Switch back to primary provider
3. Verify AI responses are working
4. Review any conversations that fell back

### RB-04: Safety Event (Emergency Patient)

**Detection:** Safety classifier triggers emergency escalation

**Impact:** Patient may need urgent care

**Steps:**
1. Immediate notification to on-call staff
2. Verify handoff was created
3. Verify staff acknowledged

**Mitigation:**
```
1. Emergency contact protocol:
   - Call patient if possible
   - Send message with emergency number
   - Create urgent staff task

2. If no response from staff:
   - Escalate to manager
   - Escalate to practice owner
   - Document all actions
```

**Recovery:**
1. Log resolution
2. Follow up with patient
3. Review safety classification accuracy

### RB-05: Cross-Tenant Data Leak

**Detection:** Audit log shows tenant A accessing tenant B data

**Impact:** HIPAA violation, trust loss

**Steps:**
1. Immediately isolate affected systems
2. Determine scope of exposure
3. Preserve evidence

**Mitigation:**
```
1. Block affected user/session
2. Disable affected API keys
3. Review all recent access for affected tenant
4. Notify affected clinics immediately
```

**Recovery:**
1. Fix the underlying bug
2. Audit all affected data access
3. Determine if breach notification required (HIPAA 60-day rule)
4. Document incident
5. Notify DPO and legal team

### RB-06: Booking Race Condition (Double Booking)

**Detection:** Two patients confirmed for same slot

**Impact:** Patient dissatisfaction, revenue impact

**Steps:**
1. Verify double booking in PMS
2. Determine which booking should stand (first confirmed)
3. Contact affected patient

**Mitigation:**
```
1. Confirm booking with PMS (source of truth)
2. If conflict:
   a. Honor first confirmed booking
   b. Offer alternative to second patient
   c. Offer priority rebooking
   d. Consider compensation
```

**Recovery:**
1. Fix booking transaction logic
2. Add additional hold mechanism
3. Review all recent bookings for conflicts

## IR.3 Emergency Procedures

### Data Breach Response

```
HOUR 0: Discovery
├── Contain the breach
├── Preserve evidence
├── Notify security team
└── Begin assessment

HOUR 1-4: Assessment
├── Determine what PHI was accessed
├── Determine number of affected individuals
├── Assess likelihood of compromise
└── Document findings

HOUR 4-24: Decision
├── Determine if reportable (HHS threshold)
├── Notify DPO
├── Notify legal counsel
└── Prepare notifications

DAY 2-60: Notification (if required)
├── Notify affected individuals
├── Notify HHS (if >500 individuals)
├── Notify media (if >500 individuals in some states)
└── Document all notifications

ONGOING: Remediation
├── Fix vulnerability
├── Enhance monitoring
├── Staff training
└── Process improvements
```

## IR.4 Communication Templates

### Incident Notification to Clinics

```
Subject: Service Incident Notification — [Severity]

Dear [Clinic Contact],

We are experiencing a [severity] incident affecting [component].

Current Status: [Investigating / Identified / Monitoring]
Impact: [Description of impact]
Expected Resolution: [Time estimate]
Workaround: [If available]

We will provide updates every [interval] until resolved.

Regards,
HeyJarvis Operations Team
```

### Patient Communication for Service Issues

```
[When appropriate and within consent]

"Hi [Name], we're experiencing a temporary technical issue with our messaging system. If you don't receive a response to your message, please call us directly at [phone] or visit our website. Thank you for your patience."
```

## IR.5 Post-Incident Review

```python
class PostMortem:
    """Post-incident review process."""

    async def create(self, incident: Incident):
        postmortem = {
            "incident_id": incident.id,
            "severity": incident.severity,
            "duration_minutes": (incident.resolved_at - incident.started_at).total_seconds() / 60,
            "affected_users": incident.affected_user_count,
            "root_cause": self.determine_root_cause(incident),
            "timeline": self.build_timeline(incident),
            "impact": self.assess_impact(incident),
            "remediation_steps": [
                "Immediate fix: ...",
                "Short-term: ...",
                "Long-term: ..."
            ],
            "lessons_learned": [],
            "action_items": []
        }

        # Required review
        await self.review_with_team(postmortem)

        # Publish to team
        await self.publish(postmortem)

        # Track action items
        for item in postmortem["action_items"]:
            await self.track_action(item)
```
