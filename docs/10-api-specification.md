# API Specification — Complete REST API Contract

## API.1 Design Principles

1. RESTful design with consistent naming
2. JSON request/response bodies
3. Standard HTTP status codes
4. Idempotency keys for all mutating operations
5. Tenant resolution from auth token (never from client)
6. Pagination on all list endpoints
7. Filtering, sorting, and search where appropriate
8. Consistent error format
9. Versioned API (`/api/v1/`)
10. OpenAPI specification maintained

## API.2 Authentication

All requests require a Bearer token:

```
Authorization: Bearer <JWT_TOKEN>
```

The JWT contains:
- `tenant_id`: The clinic/organization
- `user_id`: The authenticated user
- `roles`: User's roles
- `permissions`: Granted permissions

Tenant is NEVER accepted from the client. It is extracted from the token.

## API.3 Standard Response Format

### Success
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2025-10-01T14:30:00Z",
    "request_id": "uuid"
  }
}
```

### Error
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error description",
    "details": [
      {
        "field": "phone",
        "message": "Phone number is required"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-10-01T14:30:00Z",
    "request_id": "uuid"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid auth token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict (duplicate, state mismatch) |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | External service unavailable |

## API.4 Idempotency

All mutating requests support `Idempotency-Key` header:

```
Idempotency-Key: <unique-uuid-or-client-generated-id>
```

Server stores the key and response. Duplicate requests return the cached response.

## API.5 Complete Endpoint Specification

### A. Patients

#### List Patients
```
GET /api/v1/patients
```

Query Parameters:
- `page` (integer, default: 1)
- `limit` (integer, default: 20, max: 100)
- `search` (string, optional) — search by name or phone
- `state` (string, optional) — filter by patient state
- `sort` (string, default: "created_at") — sort field
- `order` (string, default: "desc") — "asc" or "desc"

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "clinic_id": "uuid",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+15551234567",
      "email": "john@example.com",
      "state": "engaged",
      "last_visit_at": "2025-08-15T10:00:00Z",
      "created_at": "2025-10-01T14:30:00Z"
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "total_pages": 8
  }
}
```

#### Get Patient
```
GET /api/v1/patients/:id
```

Response:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "clinic_id": "uuid",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1985-03-15",
    "phone": "+15551234567",
    "email": "john@example.com",
    "state": "engaged",
    "insurance_carrier": "Delta Dental",
    "first_visit_at": "2025-01-10T10:00:00Z",
    "last_visit_at": "2025-08-15T10:00:00Z",
    "created_at": "2025-10-01T14:30:00Z",
    "consents": [
      {
        "type": "sms",
        "granted": true,
        "consent_date": "2025-01-10T10:00:00Z"
      }
    ],
    "communication_preferences": {
      "preferred_channel": "sms",
      "preferred_language": "en",
      "timezone": "America/New_York",
      "quiet_hours": {"start": "21:00", "end": "09:00"}
    }
  }
}
```

#### Create Patient
```
POST /api/v1/patients
```

Request:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+15551234567",
  "email": "john@example.com",
  "date_of_birth": "1985-03-15",
  "insurance_carrier": "Delta Dental"
}
```

Response: 201 Created

#### Update Patient
```
PUT /api/v1/patients/:id
```

Request: (partial update)
```json
{
  "email": "newemail@example.com"
}
```

#### Patient Timeline
```
GET /api/v1/patients/:id/timeline
```

Response:
```json
{
  "success": true,
  "data": {
    "patient_id": "uuid",
    "events": [
      {
        "type": "lead_created",
        "timestamp": "2025-10-01T14:30:00Z",
        "data": { "source": "website_form", "service_interest": "cleaning" }
      },
      {
        "type": "conversation_started",
        "timestamp": "2025-10-01T14:31:00Z",
        "data": { "channel": "sms" }
      },
      {
        "type": "appointment_booked",
        "timestamp": "2025-10-01T14:45:00Z",
        "data": { "appointment_id": "uuid", "service": "cleaning", "time": "2025-10-05T10:00:00Z" }
      }
    ]
  }
}
```

### B. Conversations

#### List Conversations
```
GET /api/v1/conversations
```

Query Parameters:
- `page`, `limit`, `patient_id`, `channel`, `status`, `assigned_to`, `date_from`, `date_to`

#### Get Conversation
```
GET /api/v1/conversations/:id
```

Response:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "clinic_id": "uuid",
    "patient_id": "uuid",
    "channel": "sms",
    "status": "active",
    "intent": "booking",
    "assigned_to": "user_uuid",
    "started_at": "2025-10-01T14:30:00Z",
    "ended_at": null,
    "messages": [
      {
        "id": "uuid",
        "sender_type": "patient",
        "content": "I need an appointment",
        "sent_at": "2025-10-01T14:30:00Z"
      },
      {
        "id": "uuid",
        "sender_type": "ai",
        "content": "I'd be happy to help you book an appointment...",
        "sent_at": "2025-10-01T14:30:05Z",
        "ai_data": {
          "intent": "BOOK_APPOINTMENT",
          "confidence": 0.95
        }
      }
    ]
  }
}
```

#### Send Message (Patient)
```
POST /api/v1/conversations/:id/messages
```

Request:
```json
{
  "content": "Can I come in today?",
  "sender_type": "patient"
}
```

### C. Recapture Opportunities

#### List Opportunities
```
GET /api/v1/recapture/opportunities
```

Query Parameters:
- `page`, `limit`, `category`, `state`, `priority_min`, `patient_id`

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "patient_id": "uuid",
      "patient_name": "John Doe",
      "category": "cancellation",
      "sub_category": "schedule_conflict",
      "state": "eligible",
      "priority_score": 75,
      "potential_value": 250.00,
      "detected_at": "2025-10-01T10:00:00Z",
      "expires_at": "2025-10-08T10:00:00Z"
    }
  ],
  "meta": {
    "total": 42,
    "page": 1,
    "limit": 20
  }
}
```

#### Get Opportunity
```
GET /api/v1/recapture/opportunities/:id
```

#### Manually Create Opportunity
```
POST /api/v1/recapture/opportunities
```

Request:
```json
{
  "patient_id": "uuid",
  "category": "recall",
  "sub_category": "hygiene_overdue",
  "potential_value": 150.00,
  "notes": "Patient mentioned wanting to come in"
}
```

### D. Campaigns

#### List Campaigns
```
GET /api/v1/campaigns
```

#### Get Campaign
```
GET /api/v1/campaigns/:id
```

#### Create Campaign
```
POST /api/v1/campaigns
```

Request:
```json
{
  "name": "Abandoned Consultation Recovery",
  "description": "Follow up with patients who abandoned booking",
  "trigger_event": "booking.abandoned",
  "eligibility_rules": {
    "max_attempts": 3,
    "cooldown_days": 7,
    "require_consent": ["sms"],
    "min_priority_score": 30
  },
  "sequence": [
    {
      "step": 1,
      "channel": "sms",
      "template": "abandoned_booking_1",
      "delay_hours": 2,
      "stop_conditions": ["booked", "opted_out", "handoff"]
    },
    {
      "step": 2,
      "channel": "sms",
      "template": "abandoned_booking_2",
      "delay_hours": 48,
      "stop_conditions": ["booked", "opted_out", "handoff"]
    },
    {
      "step": 3,
      "channel": "staff_task",
      "template": "abandoned_booking_call",
      "delay_hours": 72
    }
  ]
}
```

#### Pause/Resume Campaign
```
POST /api/v1/campaigns/:id/pause
POST /api/v1/campaigns/:id/resume
```

### E. Human Handoffs

#### List Handoffs
```
GET /api/v1/handoffs
```

Query Parameters:
- `status` (pending, assigned, resolved)
- `urgency` (low, medium, high, critical)
- `assigned_to`

#### Assign Handoff
```
POST /api/v1/handoffs/:id/assign
```

Request:
```json
{
  "user_id": "uuid"
}
```

#### Resolve Handoff
```
POST /api/v1/handoffs/:id/resolve
```

Request:
```json
{
  "resolution": "patient_booked_over_phone",
  "notes": "Patient called back and booked"
}
```

### F. Appointments

#### Check Availability
```
GET /api/v1/availability
```

Query Parameters:
- `clinic_id` (required)
- `service_id` (required)
- `date_from` (required, date)
- `date_to` (required, date)
- `provider_id` (optional)

Response:
```json
{
  "success": true,
  "data": {
    "slots": [
      {
        "slot_id": "uuid",
        "start": "2025-10-05T10:00:00Z",
        "end": "2025-10-05T10:30:00Z",
        "provider_id": "uuid",
        "provider_name": "Dr. Smith",
        "available": true
      }
    ]
  }
}
```

#### Hold Appointment Slot
```
POST /api/v1/appointments/hold
```

Request:
```json
{
  "clinic_id": "uuid",
  "patient_id": "uuid",
  "service_id": "uuid",
  "provider_id": "uuid",
  "slot_start": "2025-10-05T10:00:00Z",
  "slot_end": "2025-10-05T10:30:00Z",
  "conversation_id": "uuid"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "hold_id": "uuid",
    "expires_at": "2025-10-01T14:38:00Z",
    "slot_start": "2025-10-05T10:00:00Z"
  }
}
```

#### Book Appointment
```
POST /api/v1/appointments/book
```

Request:
```json
{
  "hold_id": "uuid",
  "patient_id": "uuid",
  "notes": "Patient requested morning appointment"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "appointment_id": "uuid",
    "scheduled_start": "2025-10-05T10:00:00Z",
    "scheduled_end": "2025-10-05T10:30:00Z",
    "provider": "Dr. Smith",
    "service": "Dental Cleaning",
    "status": "scheduled",
    "confirmation_sent": true
  }
}
```

### G. Analytics

#### Recapture Dashboard
```
GET /api/v1/analytics/recapture
```

Query Parameters:
- `clinic_id` (optional, defaults to user's clinic)
- `date_from`, `date_to`
- `group_by` (day, week, month)

Response:
```json
{
  "success": true,
  "data": {
    "period": {
      "from": "2025-10-01",
      "to": "2025-10-31"
    },
    "summary": {
      "total_opportunities": 150,
      "outreach_sent": 140,
      "responses": 35,
      "bookings": 18,
      "revenue_recovered": 4250.00,
      "response_rate": 0.25,
      "conversion_rate": 0.1286,
      "ai_containment_rate": 0.85
    },
    "by_category": [
      {
        "category": "cancellation",
        "count": 50,
        "recovered": 12,
        "revenue": 3000.00
      },
      {
        "category": "no_show",
        "count": 30,
        "recovered": 4,
        "revenue": 800.00
      }
    ],
    "by_channel": [
      {
        "channel": "sms",
        "sent": 100,
        "delivered": 95,
        "responses": 28,
        "response_rate": 0.294
      }
    ]
  }
}
```

### H. Health

```
GET /api/v1/health
GET /api/v1/health/ready
GET /api/v1/health/live
```

Standard health check endpoints with dependency status.

## API.6 Webhook Endpoints

### Inbound Webhooks (from external systems)

```
POST /api/v1/webhooks/pms/:provider
POST /api/v1/webhooks/sms/:provider
POST /api/v1/webhooks/insurance/:provider
```

All webhooks:
1. Validate signature
2. Check idempotency key
3. Parse event
4. Queue for processing (don't process synchronously)
5. Return 200 OK immediately
6. Return 400 if signature invalid
7. Return 429 if rate limited

### Outbound Webhooks (to customer systems)

Clients can configure webhooks to receive events:
```
POST https://customer-system.com/webhooks/heyjarvis
```

Supported events:
- `appointment.booked`
- `appointment.cancelled`
- `appointment.rescheduled`
- `patient.opted_out`
- `conversation.handoff_created`

Webhook payload includes signature for verification.

## API.7 Rate Limiting

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Standard API | 1000 requests | 1 minute |
| AI endpoints | 100 requests | 1 minute |
| WebSocket messages | 50 messages | 1 minute |
| Webhook sends | 10,000 events | 1 minute |

Rate limit headers in response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1696116000
```

## API.8 Pagination

Cursor-based for real-time data, offset for analytics:

```
GET /api/v1/conversations?cursor=abc123&limit=20
GET /api/v1/analytics/metrics?offset=0&limit=20
```
