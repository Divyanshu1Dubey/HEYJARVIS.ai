# Production Readiness Checklist

## Release Gate Checklist

**This checklist must be 100% complete before any patient-facing deployment.**

---

## SAFETY

- [ ] Emergency pattern detection implemented
- [ ] Emergency detection rate > 99% on test set
- [ ] Medical advice request detection implemented
- [ ] Medical advice leakage = 0
- [ ] Safety escalation workflow tested
- [ ] Handoff to human works correctly
- [ ] After-hours safety protocol defined and tested
- [ ] All safety test cases pass (100%)
- [ ] Safety audit log is functional
- [ ] Emergency response SLA defined (≤30 seconds)
- [ ] Safety monitoring alerts configured
- [ ] Clinical advisor reviewed safety design

## COMPLIANCE

- [ ] Consent management system functional
- [ ] Consent verification before EVERY message send
- [ ] Opt-out handling implemented and tested
- [ ] STOP keyword functional
- [ ] Opt-out confirmation message sent
- [ ] Frequency caps enforced
- [ ] Quiet hours enforced (timezone-aware)
- [ ] Audit log captures all PHI access
- [ ] Audit log captures all message sends
- [ ] Audit log captures all consent changes
- [ ] BAAs signed with: LLM provider, SMS provider, email provider, cloud provider
- [ ] Encryption at rest verified (AES-256)
- [ ] Encryption in transit verified (TLS 1.3)
- [ ] Row-level security (tenant isolation) verified
- [ ] Data retention policies implemented
- [ ] Data deletion process implemented
- [ ] Patient data export implemented (HIPAA access right)
- [ ] Do-Not-Call list check implemented
- [ ] Email unsubscribe link functional
- [ ] CAN-SPAM requirements met
- [ ] TCPA requirements met

## TENANT ISOLATION

- [ ] RLS policies created on all tables
- [ ] Tenant from JWT (never from client)
- [ ] Cross-tenant query test passes (100%)
- [ ] Cross-tenant access blocked in all endpoints
- [ ] Cross-tenant data in LLM context prevented
- [ ] Tenant isolation in audit logs
- [ ] Tenant isolation in metrics/analytics
- [ ] Separate encryption keys per tenant verified
- [ ] Rate limits per tenant implemented
- [ ] Tenant configuration isolation verified

## BOOKING / APPOINTMENT INTEGRITY

- [ ] No double booking (tested with concurrency)
- [ ] Slot hold mechanism implemented
- [ ] Booking transaction atomic (rollback on failure)
- [ ] Booking confirmation requires external verification
- [ ] AI cannot book without patient confirmation
- [ ] Appointment slot availability from PMS only (not LLM)
- [ ] Race condition tests pass
- [ ] Integration failure handling tested
- [ ] PMS outage fallback behavior defined
- [ ] Booking audit trail complete

## AI / LLM

- [ ] Output validation layer implemented
- [ ] Hallucination test suite passes (rate < 1%)
- [ ] Tool-only for availability/insurance (no training data)
- [ ] Tenant-scoped RAG implemented
- [ ] Prompt injection detection implemented
- [ ] Adversarial input handling tested
- [ ] No PHI leakage in LLM context verified
- [ ] Fallback behavior when LLM unavailable defined
- [ ] Output validation catches fabricated appointments
- [ ] Output validation catches fabricated insurance
- [ ] Output validation catches medical claims
- [ ] Required disclaimer injection works
- [ ] LLM provider BAA signed
- [ ] Backup LLM provider configured

## DATA INTEGRITY

- [ ] No orphaned records
- [ ] No missing foreign keys
- [ ] No duplicate opportunities (per patient+category)
- [ ] Outcome tracking implemented for all outreaches
- [ ] Feature timestamps prevent data leakage
- [ ] Patient-level train/test split enforced
- [ ] Temporal split enforced (no future data in training)
- [ ] Backup/restore tested
- [ ] Data retention policies implemented
- [ ] Deletion process implemented

## SYSTEM RELIABILITY

- [ ] Health checks implemented
- [ ] Graceful degradation defined for each component
- [ ] LLM fallback behavior defined
- [ ] SMS provider fallback behavior defined
- [ ] PMS unavailable fallback behavior defined
- [ ] Webhook deduplication implemented
- [ ] Idempotency keys implemented
- [ ] Dead letter queue implemented
- [ ] Retry logic with exponential backoff
- [ ] Circuit breakers for external services
- [ ] Database connection pooling configured
- [ ] Queue consumer scaling configured
- [ ] Auto-scaling configured

## MONITORING AND ALERTING

- [ ] API latency monitoring (p50, p95, p99)
- [ ] Error rate monitoring
- [ ] Queue depth monitoring
- [ ] Database health monitoring
- [ ] SMS delivery rate monitoring
- [ ] AI response time monitoring
- [ ] Safety event monitoring
- [ ] Opt-out rate monitoring
- [ ] Handoff queue monitoring
- [ ] Integration health monitoring
- [ ] Critical alerts configured (PagerDuty/SMS)
- [ ] Warning alerts configured (Slack)
- [ ] Dashboard for operations
- [ ] Dashboard for AI quality
- [ ] Dashboard for compliance
- [ ] Correlation IDs on all logs

## SECURITY

- [ ] JWT authentication implemented
- [ ] MFA available for staff accounts
- [ ] RBAC implemented
- [ ] Rate limiting implemented
- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] XSS prevention implemented
- [ ] Prompt injection detection implemented
- [ ] Secrets in Vault (not in code or env vars)
- [ ] TLS 1.3 for all connections
- [ ] Security headers configured
- [ ] CORS configured
- [ ] Vulnerability scanning automated (daily)
- [ ] Secret scanning automated (every commit)
- [ ] Penetration test completed (at least once)
- [ ] Red team exercise completed

## TESTING

- [ ] Unit tests > 90% coverage
- [ ] Integration tests pass
- [ ] Contract tests pass for all integrations
- [ ] E2E tests pass
- [ ] AI evaluation tests pass
- [ ] Prompt regression tests pass
- [ ] Safety test suite passes (100%)
- [ ] Hallucination tests pass
- [ ] Adversarial input tests pass
- [ ] Concurrency tests pass
- [ ] Load tests pass (target: 10K concurrent conversations)
- [ ] Webhook tests pass
- [ ] Consent logic tests pass
- [ ] Frequency cap tests pass
- [ ] State machine transition tests pass
- [ ] Red team test results reviewed
- [ ] Performance benchmarks met

## OPERATIONAL READINESS

- [ ] Runbooks documented for all critical scenarios
- [ ] Incident response procedure documented
- [ ] Disaster recovery plan documented
- [ ] Backup/restore tested
- [ ] Rollback procedure tested
- [ ] On-call rotation defined
- [ ] Escalation chain defined
- [ ] Status page configured
- [ ] Team trained on system
- [ ] Pilot clinic trained on dashboard
- [ ] Support contacts documented
- [ ] Vendor contacts documented

## CLINIC READINESS

- [ ] Clinic onboarded successfully
- [ ] Clinic staff trained
- [ ] Consent collection process defined
- [ ] Clinic's quiet hours configured
- [ ] Clinic's communication preferences configured
- [ ] Clinic's message templates approved
- [ ] Clinic's escalation rules configured
- [ ] Clinic's suppression list imported
- [ ] Integration with PMS tested
- [ ] Integration with insurance (if applicable) tested
- [ ] Go-live checklist reviewed with clinic

## FINAL GATE

```
All checkboxes above must be checked before production deployment.

Sign-off required from:
□ Engineering Lead
□ Security Lead
□ Compliance Lead
□ Product Manager
□ Clinical Advisor (if applicable)
□ Legal (if applicable)
```
