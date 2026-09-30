# Runbooks — Operational Runbooks

## RB.1 Daily Operations Runbook

### Morning Checklist (Daily at 8 AM)

```
1. HEALTH CHECK
   □ Run: kubectl get pods -n heyjarvis
   □ All pods in Running state?
   □ Check: Health dashboard (Datadog)
   □ API latency < 200ms p95?
   □ Error rate < 0.5%?

2. QUEUE HEALTH
   □ Check queue depth: < 1000?
   □ Check consumer lag: < 60s?
   □ Check failed messages: < 10?

3. INTEGRATION STATUS
   □ PMS sync: Last successful sync < 1 hour ago?
   □ SMS provider: No error spikes?
   □ Email provider: Delivery rate > 98%?

4. OVERNIGHT JOBS
   □ Daily backup completed?
   □ Analytics aggregation completed?
   □ Campaign scheduling completed?

5. ALERTS
   □ Review overnight alerts
   □ Any P1/P2 incidents?
   □ Follow up on unresolved items

6. METRICS REVIEW
   □ Yesterday's outreach volume
   □ Response rates
   □ Booking conversions
   □ Any anomalies?

7. TEAM STANDUP NOTES
   □ Review handoff queue
   □ Assign pending handoffs
   □ Review patient complaints
```

### Weekly Checklist (Every Monday)

```
1. BACKUP VERIFICATION
   □ Run restore test on latest backup
   □ Verify backup size is normal
   □ Check backup retention

2. SECURITY
   □ Review security alerts
   □ Check failed login attempts
   □ Review access logs for anomalies

3. PERFORMANCE
   □ Review slow queries
   □ Review slow API endpoints
   □ Check database connection pool

4. COST REVIEW
   □ AI costs this week
   □ SMS costs this week
   □ Infrastructure costs
   □ Compare to budget

5. COMPLIANCE
   □ Opt-outs processed
   □ Consent changes logged
   □ Audit log completeness

6. DATA QUALITY
   □ Check for orphaned records
   □ Check for missing outcomes
   □ Verify data consistency
```

## RB.2 Common Procedures

### Deploy a New Version

```bash
# 1. Build and test
make lint test test-ai

# 2. Build Docker images
docker build -f infra/docker/Dockerfile.api -t heyjarvis/api:v1.2.4 .
docker build -f infra/docker/Dockerfile.worker -t heyjarvis/worker:v1.2.4 .

# 3. Push to registry
docker push heyjarvis/api:v1.2.4
docker push heyjarvis/worker:v1.2.4

# 4. Deploy to staging
kubectl set image deployment/api api=heyjarvis/api:v1.2.4 -n heyjarvis-staging
kubectl rollout status deployment/api -n heyjarvis-staging

# 5. Run smoke tests
make test-e2e ENV=staging

# 6. Deploy to production (canary)
kubectl set image deployment/api api=heyjarvis/api:v1.2.4 -n heyjarvis-production
kubectl rollout pause deployment/api -n heyjarvis-production  # Pause for canary

# 7. Canary: 5% traffic
kubectl patch virtualservice api -n heyjarvis-production --type='json' -p='[...]'

# 8. Monitor for 1 hour
# Check: error rate, latency, booking rate

# 9. Full rollout
kubectl rollout resume deployment/api -n heyjarvis-production

# 10. Verify
kubectl rollout status deployment/api -n heyjarvis-production
```

### Handle Patient Opt-out

```bash
# Option 1: Patient says STOP via SMS
# → Automatic via webhook handler
# → Verify: Check consents table

# Option 2: Staff marks patient opted out
curl -X POST https://api.heyjarvis.ai/api/v1/patients/:id/opt-out \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channel": "sms", "reason": "patient_request"}'

# Option 3: Bulk opt-out (legal request)
python scripts/bulk_opt_out.py --file legal_optouts.csv

# Verify opt-out was processed
curl https://api.heyjarvis.ai/api/v1/patients/:id/consents \
  -H "Authorization: Bearer $STAFF_TOKEN"
```

### Handle Safety Escalation

```bash
# 1. Check handoff queue
curl https://api.heyjarvis.ai/api/v1/handoffs?status=pending&urgency=critical \
  -H "Authorization: Bearer $STAFF_TOKEN"

# 2. Get handoff details
curl https://api.heyjarvis.ai/api/v1/handoffs/:id \
  -H "Authorization: Bearer $STAFF_TOKEN"

# 3. Assign to self
curl -X POST https://api.heyjarvis.ai/api/v1/handoffs/:id/assign \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{"user_id": "my-user-id"}'

# 4. Resolve
curl -X POST https://api.heyjarvis.ai/api/v1/handoffs/:id/resolve \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{"resolution": "patient_booked_over_phone", "notes": "..."}'
```

### Emergency: Stop All Campaigns

```bash
# Pause all campaigns for a clinic
curl -X POST https://api.heyjarvis.ai/api/v1/clinics/:id/campaigns/pause-all \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Or for all clinics (global emergency)
curl -X POST https://api.heyjarvis.ai/api/v1/campaigns/pause-all \
  -H "Authorization: Bearer $OWNER_TOKEN"

# Resume when ready
curl -X POST https://api.heyjarvis.ai/api/v1/campaigns/resume-all \
  -H "Authorization: Bearer $OWNER_TOKEN"
```

### Database Maintenance

```bash
# Run migrations
alembic upgrade head

# Check database size
psql -c "SELECT pg_size_pretty(pg_database_size('heyjarvis'));"

# Vacuum analyze
psql -c "VACUUM ANALYZE;"

# Check long-running queries
psql -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"

# Kill long-running query
psql -c "SELECT pg_terminate_backend(:pid);"
```

## RB.3 Incident Response Procedures

### SMS Provider Outage

```
TIME 0: Detection
├── Twilio status page shows incident
├── Error rate spike in monitoring
└── Clinics start reporting undelivered messages

TIME 0-5min: Response
├── Confirm outage (check Twilio status)
├── Notify ops team
├── Check if backup provider available
└── Update status page

TIME 5-15min: Mitigation
├── Option A: Switch to backup SMS provider
│   └── Update routing config
│   └── Verify messages routing correctly
├── Option B: Hold messages in queue
│   └── Notify clinics of delay
│   └── Set TTL for queued messages (24h)
└── Monitor recovery

TIME 15min+: Recovery
├── Monitor Twilio status for recovery
├── When resolved: Switch back to Twilio
├── Drain message queue
├── Verify all messages sent
├── Notify clinics of resolution
└── Document incident
```

### LLM Provider Outage

```
TIME 0: Detection
├── LLM API returning errors
├── AI conversations failing
└── Error rate spike

TIME 0-5min: Response
├── Confirm LLM provider outage
├── Check if backup provider available
└── Notify ops team

TIME 5-15min: Mitigation
├── Switch to backup LLM provider
│   └── Update configuration
│   └── Verify AI working
├── If no backup: Fall back to templates
│   └── Simple responses using templates
│   └── Complex cases → human handoff
│   └── Notify clinics: "AI temporarily limited"
└── Monitor

TIME 15min+: Recovery
├── Monitor LLM provider status
├── When resolved: Switch back
├── Verify AI quality
└── Document incident
```
