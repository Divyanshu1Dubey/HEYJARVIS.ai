# Integration Architecture — External System Adapters

## IA.1 Integration Principles

1. **Abstraction:** Core system never depends on a specific provider's API
2. **Adapter pattern:** Each provider gets a clean adapter interface
3. **Resilience:** External failures never crash the core system
4. **Idempotency:** All external operations are idempotent
5. **Observability:** Every integration call is logged and measured
6. **Fallback:** Graceful degradation when integrations fail
7. **Sync strategy:** Event-driven where possible, polling as fallback

## IA.2 Provider Abstraction

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

class SchedulingProvider(ABC):
    """Abstract interface for scheduling systems."""

    @abstractmethod
    async def get_availability(
        self,
        clinic_id: str,
        service_id: str,
        date_from: datetime,
        date_to: datetime,
        provider_id: Optional[str] = None
    ) -> List[TimeSlot]:
        """Get available appointment slots."""
        pass

    @abstractmethod
    async def book_appointment(
        self,
        clinic_id: str,
        patient_id: str,
        service_id: str,
        provider_id: str,
        slot_start: datetime,
        slot_end: datetime,
        notes: str = ""
    ) -> AppointmentResult:
        """Book an appointment. MUST return the real appointment ID."""
        pass

    @abstractmethod
    async def cancel_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
        reason: str = ""
    ) -> bool:
        """Cancel an appointment."""
        pass

    @abstractmethod
    async def reschedule_appointment(
        self,
        clinic_id: str,
        appointment_id: str,
        new_start: datetime,
        new_end: datetime
    ) -> AppointmentResult:
        """Reschedule an appointment."""
        pass

    @abstractmethod
    async def get_appointment(
        self,
        clinic_id: str,
        appointment_id: str
    ) -> Optional[Appointment]:
        """Get appointment details."""
        pass

    @abstractmethod
    async def hold_slot(
        self,
        clinic_id: str,
        provider_id: str,
        slot_start: datetime,
        slot_end: datetime
    ) -> HoldResult:
        """Create temporary hold on a slot."""
        pass


class InsuranceProvider(ABC):
    """Abstract interface for insurance verification."""

    @abstractmethod
    async def verify_eligibility(
        self,
        clinic_id: str,
        patient_id: str,
        insurance_carrier: str,
        insurance_id: str,
        service_code: str
    ) -> EligibilityResult:
        """Verify patient insurance eligibility."""
        pass

    @abstractmethod
    async def get_benefits(
        self,
        clinic_id: str,
        patient_id: str,
        insurance_carrier: str,
        insurance_id: str
    ) -> BenefitsResult:
        """Get patient's benefit details."""
        pass


class CommunicationProvider(ABC):
    """Abstract interface for communication channels."""

    @abstractmethod
    async def send_sms(
        self,
        to: str,
        content: str,
        clinic_id: str
    ) -> MessageResult:
        """Send SMS message."""
        pass

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        clinic_id: str
    ) -> MessageResult:
        """Send email."""
        pass

    @abstractmethod
    async def get_delivery_status(
        self,
        provider_message_id: str
    ) -> DeliveryStatus:
        """Check delivery status of a message."""
        pass
```

## IA.3 PMS Adapters

### Supported Systems (Priority Order)

1. **Open Dental** — Most widely used cloud-based dental PMS
2. **Eaglesoft** — Popular Windows-based PMS
3. **Dentrix** — Henry Schein product, large market share
4. **DentalWin** — Smaller but used
5. **Custom/Bridge** — For practices with custom solutions

### Open Dental Adapter

```python
class OpenDentalAdapter(SchedulingProvider):
    """Open Dental API integration."""

    BASE_URL = "https://api.opendental.com/api/v1"
    AUTH_URL = "https://api.opendental.com/authorizations"

    def __init__(self, developer_key: str, practice_id: str):
        self.developer_key = developer_key
        self.practice_id = practice_id
        self._access_token = None
        self._token_expires_at = None

    async def _get_token(self) -> str:
        """Get or refresh OAuth token."""
        if self._access_token and datetime.now() < self._token_expires_at:
            return self._access_token

        async with self.http.post(self.AUTH_URL, json={
            "DeveloperKey": self.developer_key,
            "PracticeId": self.practice_id
        }) as resp:
            data = await resp.json()
            self._access_token = data["AccessToken"]
            self._token_expires_at = datetime.now() + timedelta(
                seconds=data["ExpiresIn"] - 300  # 5 min buffer
            )
            return self._access_token

    async def get_availability(self, clinic_id, service_id, date_from, date_to, provider_id=None):
        """Get available slots from Open Dental."""
        token = await self._get_token()

        async with self.http.get(
            f"{self.BASE_URL}/appointments/availability",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "clinic_id": clinic_id,
                "service_id": service_id,
                "start_date": date_from.isoformat(),
                "end_date": date_to.isoformat(),
                "provider_id": provider_id
            }
        ) as resp:
            data = await resp.json()
            return [TimeSlot(**slot) for slot in data["slots"]]

    async def book_appointment(self, clinic_id, patient_id, service_id, provider_id, slot_start, slot_end, notes=""):
        """Book appointment in Open Dental."""
        token = await self._get_token()

        request = {
            "PatientId": patient_id,
            "ClinicId": clinic_id,
            "ProviderId": provider_id,
            "ServiceId": service_id,
            "StartTime": slot_start.isoformat(),
            "EndTime": slot_end.isoformat(),
            "Notes": notes,
            "Source": "HeyJarvis"
        }

        async with self.http.post(
            f"{self.BASE_URL}/appointments",
            headers={"Authorization": f"Bearer {token}"},
            json=request
        ) as resp:
            data = await resp.json()
            return AppointmentResult(
                success=True,
                appointment_id=data["AppointmentId"],
                external_id=str(data["AppointmentId"])
            )
```

### Adapter Configuration

```python
ADAPTERS = {
    "scheduling": {
        "opendental": OpenDentalAdapter,
        "eaglesoft": EaglesoftAdapter,
        "dentrix": DentrixAdapter,
        "dentalwin": DentalWinAdapter,
    },
    "insurance": {
        "change_healthcare": ChangeHealthcareAdapter,
        "claimconnect": ClaimConnectAdapter,
        "verifai": VerifaiAdapter,
    },
    "communication": {
        "twilio": TwilioAdapter,
        "postmark": PostmarkAdapter,
    }
}

def get_adapter(provider_type: str, provider_name: str, config: dict):
    """Get configured adapter instance."""
    adapter_class = ADAPTERS[provider_type][provider_name]
    return adapter_class(**config)
```

## IA.4 Integration Health Monitoring

```python
class IntegrationHealthMonitor:
    """Monitor all integration health."""

    async def check_all(self) -> dict:
        results = {}
        for integration in await self.get_active_integrations():
            try:
                start = time.time()
                await integration.health_check()
                latency = time.time() - start

                results[integration.id] = {
                    "status": "healthy",
                    "latency_ms": round(latency * 1000, 2),
                    "last_checked": datetime.now()
                }
            except Exception as e:
                results[integration.id] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_checked": datetime.now()
                }
                # Alert ops team
                await self.alert_ops(integration, e)
        return results
```

## IA.5 Webhook Handling

```python
class WebhookHandler:
    """Handle inbound webhooks from external systems."""

    async def handle(self, request, provider: str):
        # 1. Verify signature
        if not self.verify_signature(request, provider):
            raise InvalidSignatureError()

        # 2. Extract idempotency key
        idempotency_key = request.headers.get("X-Idempotency-Key")
        if not idempotency_key:
            raise MissingIdempotencyKey()

        # 3. Check if already processed
        if await self.is_processed(idempotency_key):
            return {"status": "already_processed"}

        # 4. Parse event
        event = WebhookEvent(
            source=provider,
            event_type=request.json["event_type"],
            payload=request.json,
            received_at=datetime.now()
        )

        # 5. Queue for processing (don't block webhook response)
        await self.queue_event(event)

        # 6. Mark as received (not yet processed)
        await self.mark_received(idempotency_key, event)

        # 7. Return immediately
        return {"status": "accepted"}

    async def process_queue(self):
        """Process queued webhook events."""
        while True:
            event = await self.get_next_event()
            if not event:
                await asyncio.sleep(1)
                continue

            try:
                await self.process_event(event)
                await self.mark_processed(event.idempotency_key)
            except Exception as e:
                await self.mark_failed(event.idempotency_key, str(e))
                # Retry with backoff
                await self.retry_later(event, delay=self.get_retry_delay(event))
```

## IA.6 Retry Strategy

```python
class IntegrationRetryPolicy:
    """Retry policy for integration calls."""

    MAX_RETRIES = 3
    BASE_DELAY = 1  # seconds
    MAX_DELAY = 30  # seconds

    RETRYABLE_ERRORS = {
        "timeout",           # Network timeout
        "rate_limit",        # 429 Too Many Requests
        "server_error",      # 500, 502, 503
        "service_unavailable"
    }

    NON_RETRYABLE_ERRORS = {
        "unauthorized",     # 401 — don't retry
        "forbidden",        # 403 — don't retry
        "not_found",        # 404 — don't retry
        "validation_error", # 422 — don't retry
    }

    async def execute(self, operation, *args, **kwargs):
        """Execute operation with retry logic."""
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                return await operation(*args, **kwargs)
            except NonRetryableError as e:
                raise  # Don't retry
            except RetryableError as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    delay = min(
                        self.BASE_DELAY * (2 ** attempt),  # Exponential backoff
                        self.MAX_DELAY
                    )
                    jitter = random.uniform(0, delay * 0.1)  # 10% jitter
                    await asyncio.sleep(delay + jitter)

        raise MaxRetriesExceeded(f"Failed after {self.MAX_RETRIES} retries: {last_error}")
```

## IA.7 Sync Strategy

```
PMS System Changes
       │
       ├─→ Webhook (preferred)
       │     └─→ Immediate, reliable
       │     └─→ Requires PMS to support webhooks
       │
       ├─→ Polling (fallback)
       │     └─→ Every 5 minutes
       │     └─→ "Last modified" filter
       │     └─→ Only fetches changes since last sync
       │
       └─→ Manual sync (emergency)
             └─→ Staff-triggered
             └─→ Full re-sync
```

```python
class PMSSyncService:
    """Sync data from PMS systems."""

    async def sync(self, integration: Integration):
        adapter = get_adapter("scheduling", integration.provider, integration.config)

        # Get last sync timestamp
        last_sync = integration.last_sync_at or datetime(2000, 1, 1)

        # Fetch changes since last sync
        changes = await adapter.get_changes_since(last_sync)

        for change in changes:
            await self.apply_change(integration.clinic_id, change)

        integration.last_sync_at = datetime.now()
        await integration.save()
```

## IA.8 Conflict Resolution

When PMS data conflicts with HeyJarvis data:

```
RULE: PMS is always the source of truth for appointments and patients.

Conflict types:
1. Appointment time changed in PMS
   → Update HeyJarvis, notify patient if needed

2. Patient info changed in PMS
   → Update HeyJarvis, don't overwrite HeyJarvis-specific fields

3. Appointment cancelled in PMS (outside HeyJarvis)
   → Detect via sync, create recapture opportunity if appropriate

4. Appointment booked in PMS (outside HeyJarvis)
   → Detect via sync, mark as booked, cancel any outreach
```
