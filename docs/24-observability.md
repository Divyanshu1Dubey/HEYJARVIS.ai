# Observability — Monitoring, Logging, and Alerting

## OB.1 Observability Philosophy

1. **Every important action is logged.** Nothing happens without a record.
2. **Correlation IDs everywhere.** Trace any operation end-to-end.
3. **PHI-safe logging.** No PHI in logs unless explicitly required.
4. **Actionable alerts.** Every alert has a clear action.
5. **Dashboard for every persona.** Different views for ops, engineering, product, compliance.

## OB.2 Correlation IDs

```python
class CorrelationContext:
    """Propagate correlation ID through the system."""

    async def __call__(self, request, call_next):
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Set in request state
        request.state.correlation_id = correlation_id

        # Set in logging context
        log_context = {
            "correlation_id": correlation_id,
            "tenant_id": request.state.tenant_id,
            "user_id": request.state.user_id,
            "endpoint": request.url.path
        }

        # Process request with context
        with self.logger.bind(**log_context):
            response = await call_next(request)

        # Return correlation ID in response
        response.headers["X-Correlation-ID"] = correlation_id
        return response
```

Every log entry includes:
```json
{
  "timestamp": "2025-10-01T14:30:00.123Z",
  "correlation_id": "abc-123",
  "tenant_id": "clinic-uuid",
  "conversation_id": "conv-uuid",
  "patient_id": "patient-uuid",
  "event": "message.sent",
  "channel": "sms",
  "status": "delivered",
  "duration_ms": 150,
  "error": null
}
```

## OB.3 Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Usage throughout the codebase
logger.info("message.sent",
    correlation_id=corr_id,
    tenant_id=tenant_id,
    patient_id=patient_id,
    message_id=message_id,
    channel="sms",
    provider="twilio",
    status="sent"
)

logger.error("tool.execution_failed",
    correlation_id=corr_id,
    tool_name="check_availability",
    error=str(error),
    duration_ms=duration
)

logger.warning("safety.escalation",
    correlation_id=corr_id,
    trigger="emergency_keyword",
    patient_message="My tooth is killing me",
    action="handoff_created"
)
```

## OB.4 Metrics

### System Metrics

```python
SYSTEM_METRICS = {
    # API
    "api_requests_total": Counter("Total API requests"),
    "api_request_duration_seconds": Histogram("API request duration"),
    "api_errors_total": Counter("API errors by type"),

    # Database
    "db_connections_active": Gauge("Active DB connections"),
    "db_query_duration_seconds": Histogram("DB query duration"),
    "db_errors_total": Counter("DB errors"),

    # Queue
    "queue_messages_total": Counter("Total queue messages"),
    "queue_messages_processed": Counter("Processed messages"),
    "queue_messages_failed": Counter("Failed messages"),
    "queue_depth": Gauge("Current queue depth"),
    "queue_consumer_lag_seconds": Gauge("Consumer lag"),

    # Workers
    "worker_tasks_total": Counter("Total tasks processed"),
    "worker_task_duration_seconds": Histogram("Task duration"),
    "worker_errors_total": Counter("Worker errors"),

    # External integrations
    "integration_requests_total": Counter("Integration requests"),
    "integration_errors_total": Counter("Integration errors"),
    "integration_latency_seconds": Histogram("Integration latency")
}
```

### Business Metrics

```python
BUSINESS_METRICS = {
    # Conversations
    "conversations_started_total": Counter("Conversations started"),
    "conversations_ended_total": Counter("Conversations ended"),
    "conversation_duration_seconds": Histogram("Conversation duration"),

    # Recapture
    "opportunities_detected_total": Counter("Opportunities detected"),
    "outreach_sent_total": Counter("Outreach messages sent"),
    "outreach_delivered_total": Counter("Outreach delivered"),
    "outreach_failed_total": Counter("Outreach failed"),
    "responses_received_total": Counter("Patient responses received"),
    "bookings_recovered_total": Counter("Bookings recovered"),
    "revenue_recovered_dollars": Counter("Revenue recovered"),

    # AI
    "ai_requests_total": Counter("AI requests"),
    "ai_request_duration_seconds": Histogram("AI request duration"),
    "ai_tool_calls_total": Counter("AI tool calls"),
    "ai_handoffs_total": Counter("AI handoffs to human"),
    "ai_safety_escalations_total": Counter("Safety escalations"),

    # Messages
    "messages_sent_total": Counter("Messages sent by channel"),
    "messages_delivered_total": Counter("Messages delivered"),
    "messages_failed_total": Counter("Messages failed"),
    "messages_opted_out_total": Counter("Opt-outs received"),
    "opt_out_rate": Gauge("Opt-out rate (rolling 24h)")
}
```

## OB.5 Alerts

### Critical Alerts (PagerDuty / SMS)

```python
CRITICAL_ALERTS = [
    {
        "name": "database_down",
        "condition": "db_connections_active == 0",
        "duration": "1m",
        "action": "Page on-call engineer"
    },
    {
        "name": "sms_provider_down",
        "condition": "sms_delivery_rate < 0.5",
        "duration": "5m",
        "action": "Page on-call + notify ops"
    },
    {
        "name": "safety_escalation_spike",
        "condition": "safety_escalations_per_minute > 10",
        "duration": "5m",
        "action": "Page security team"
    },
    {
        "name": "booking_failure_spike",
        "condition": "booking_failure_rate > 0.1",
        "duration": "5m",
        "action": "Page on-call + notify engineering"
    },
    {
        "name": "cross_tenant_leak_detected",
        "condition": "tenant_isolation_violation > 0",
        "duration": "0m",
        "action": "Page security team immediately"
    }
]
```

### Warning Alerts (Slack)

```python
WARNING_ALERTS = [
    {
        "name": "queue_depth_high",
        "condition": "queue_depth > 10000",
        "duration": "10m",
        "action": "Slack #ops-alerts"
    },
    {
        "name": "ai_latency_high",
        "condition": "ai_request_duration_p95 > 5000ms",
        "duration": "5m",
        "action": "Slack #ai-alerts"
    },
    {
        "name": "error_rate_high",
        "condition": "api_error_rate > 0.05",
        "duration": "5m",
        "action": "Slack #ops-alerts"
    },
    {
        "name": "opt_out_spike",
        "condition": "opt_out_rate_1h > 0.01",
        "duration": "1h",
        "action": "Slack #product-alerts"
    }
]
```

## OB.6 Dashboards

### Operations Dashboard
- API latency (p50, p95, p99)
- Error rate by endpoint
- Queue depth and processing rate
- Database connections and query performance
- External integration health

### AI Dashboard
- AI request volume
- Response latency
- Intent classification distribution
- Handoff rate
- Safety escalation rate
- Tool call success rate
- Hallucination rate (from evaluations)

### Business Dashboard
- Opportunities detected (daily, weekly, monthly)
- Outreach sent by channel
- Response rate
- Booking recovery rate
- Revenue recovered
- Campaign performance
- Conversion funnel

### Compliance Dashboard
- Messages sent per day
- Opt-outs per day
- Consent changes
- Safety events
- Audit log completeness
- Data access patterns

## OB.7 Log Retention

| Log Type | Retention | Storage |
|----------|-----------|---------|
| Application logs | 90 days | Hot storage |
| API logs | 90 days | Hot storage |
| Audit logs | 6 years | Cold storage |
| Security logs | 6 years | Cold storage |
| AI logs | 1 year | Cold storage |
| Error logs | 1 year | Cold storage |

## OB.8 Distributed Tracing

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@trace
async def process_conversation(conversation_id: str):
    with tracer.start_as_current_span("process_conversation") as span:
        span.set_attribute("conversation_id", conversation_id)

        # Intent classification span
        with tracer.start_as_current_span("intent_classification"):
            intent = await classify_intent(conversation)

        # Tool calls span
        if intent.requires_availability_check:
            with tracer.start_as_current_span("check_availability"):
                slots = await check_availability(service_id)

        # Response generation span
        with tracer.start_as_current_span("generate_response"):
            response = await generate_response(intent, slots)

        return response
```

## OB.9 Health Checks

```python
class HealthCheck:
    async def check(self):
        checks = {
            "database": await self.check_database(),
            "redis": await self.check_redis(),
            "queue": await self.check_queue(),
            "llm": await self.check_llm(),
            "sms_provider": await self.check_sms(),
            "pms": await self.check_pms()
        }

        all_healthy = all(c["status"] == "healthy" for c in checks.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
```

## OB.10 Incident Response

```python
class IncidentResponse:
    INCIDENT_LEVELS = {
        "P1": {
            "description": "System down / data breach",
            "response_time": "15 minutes",
            "notification": ["CTO", "Legal", "Compliance"]
        },
        "P2": {
            "description": "Major feature broken",
            "response_time": "1 hour",
            "notification": ["Engineering Lead", "Product"]
        },
        "P3": {
            "description": "Minor issue / degradation",
            "response_time": "4 hours",
            "notification": ["On-call"]
        }
    }
```
