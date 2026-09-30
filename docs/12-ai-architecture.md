# AI Architecture — Complete AI/ML System Design

## AI.1 Architecture Overview

```
                    ┌─────────────────────────────┐
                    │    Patient Message Input    │
                    └──────────────┬──────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │          Pre-Processing Layer            │
              │  • Language detection                     │
              │  • PII masking (if needed for logs)       │
              │  • Input validation                       │
              │  • Duplicate detection                    │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │        Safety Classification             │
              │        (DETERMINISTIC)                    │
              │  • Emergency pattern matching             │
              │  • Medical advice detection               │
              │  • Threat/inappropriate content           │
              │  → SAFETY_ESCALATION if triggered         │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │        Policy Engine Check               │
              │        (DETERMINISTIC)                    │
              │  • Can we contact this patient?           │
              │  • Is consent valid?                      │
              │  • Within quiet hours?                    │
              │  • Frequency cap OK?                      │
              │  → SUPPRESS if any rule fails             │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │         Intent Classification            │
              │         (LLM + classifier)                │
              │  • What does the patient want?            │
              │  • What is their urgency level?           │
              │  • What is their emotional state?         │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │         Tool Selection & Execution       │
              │                                          │
              │  check_availability()                    │
              │  check_insurance()                       │
              │  get_clinic_info()                       │
              │  get_service_info()                      │
              │  book_appointment()                      │
              │  handoff_to_human()                      │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │      Response Generation (LLM)           │
              │  • Use ONLY verified data from tools      │
              │  • Never fabricate                        │
              │  • Appropriate tone                       │
              │  • Include opt-out                        │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │      Response Validation                  │
              │      (DETERMINISTIC)                      │
              │  • No unsupported claims                  │
              │  • No medical advice                      │
              │  • No fake appointments                   │
              │  • Policy compliance check                │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │         Output Delivery                   │
              │  • Send to patient                        │
              │  • Log everything                         │
              │  • Update conversation state              │
              └──────────────────────────────────────────┘
```

## AI.2 Technology Stack by Use Case

### A. LLM (Large Language Model)

**Used for:**
| Use Case | Model Tier | Why LLM |
|----------|-----------|---------|
| Intent extraction | Small (Tier 2) | Needs context understanding |
| Conversation understanding | Small (Tier 2) | Multi-turn context |
| Reason classification | Small (Tier 2) | Nuanced text understanding |
| Message personalization | Small (Tier 2) | Template filling with context |
| Summarization | Small (Tier 2) | Conversation summaries |
| Response generation | Strong (Tier 3) | Quality patient-facing text |
| Human-handoff explanations | Small (Tier 2) | Clear context summary |

**NOT used for:**
- Booking decisions (use tools + deterministic validation)
- Insurance verification (use insurance API)
- Safety classification (use deterministic rules)
- Compliance decisions (use rules engine)
- Eligibility (use rules engine)

### B. Classical ML

**Used for:**
| Use Case | Model Type | Why ML |
|----------|-----------|--------|
| Conversion probability | Gradient boosting / Calibrated classifier | Historical patterns |
| Response probability | Logistic regression | Simple, interpretable |
| Optimal contact timing | Survival model / Time-to-event | Time-based patterns |
| Churn prediction | Gradient boosting | Patient history patterns |
| Next-best-action | Multi-class classifier | Historical action effectiveness |
| Message ranking | Learning-to-rank | A/B test data → optimization |
| Priority scoring | Gradient boosting | Multi-feature scoring |

**NOT used for:**
- Any decision that overrides rules
- Safety-critical decisions
- Compliance decisions
- First-contact decisions in V1

### C. Rules Engine

**Used for:**
| Use Case | Implementation |
|----------|---------------|
| Eligibility | Deterministic rules |
| Consent verification | Rule-based state machine |
| Frequency caps | Counter + time-window rules |
| Quiet hours | Timezone-aware time checks |
| Suppression | List + rule matching |
| Safety escalation | Pattern matching + keywords |
| Booking validation | State machine + API confirmation |
| Insurance disclaimers | Fixed text rules |
| Channel eligibility | Consent + capability matching |
| Business rules | Configurable per clinic |

### D. RAG (Retrieval-Augmented Generation)

**Used for:**
| Use Case | Source |
|----------|--------|
| Clinic-specific policies | Clinic settings database |
| Business hours | Clinic config |
| Services offered | Services table |
| Accepted insurance | Insurance table |
| Cancellation policy | Clinic settings |
| Appointment types | Services table |
| FAQs | Clinic FAQ database |
| Provider info | Providers table |

**NOT used for:**
- Patient-specific data (use structured data)
- Real-time availability (use scheduling API)
- Insurance verification (use insurance API)

## AI.3 Model Tiering

### Tier 0: Deterministic Rules (Free, Instant)
```
Input → Rules Engine → Output

Examples:
- Is patient opted out? → Yes/No
- Is it quiet hours? → Yes/No
- Is consent valid for SMS? → Yes/No
- Has frequency cap been reached? → Yes/No
- Is this an emergency symptom? → Yes/No
```

### Tier 1: Small Classifier (~$0.001/call)
```
Input → Fine-tuned classifier → Classification

Examples:
- Intent classification
- Sentiment classification
- Language detection
- Urgency classification
- Topic classification
```

### Tier 2: Small LLM (~$0.01/call)
```
Input → Small LLM (Haiku/Flash) → Structured output

Examples:
- Conversation summarization
- Reason extraction from patient message
- Entity extraction (dates, times, names)
- Template variable extraction
- Simple response generation
```

### Tier 3: Strong LLM (~$0.05/call)
```
Input → Strong LLM (Sonnet/Opus) → Response

Examples:
- Complex multi-turn conversation
- Nuanced patient communication
- Complex scheduling conversation
- Complaint handling
- Escalation explanation
```

## AI.4 Cost Optimization Strategy

```python
class TieredAIOrchestrator:
    """Route requests to appropriate AI tier."""

    async def process(self, request):
        # Tier 0: Rules first (always)
        if self.rules_can_handle(request):
            return self.rules_engine.process(request)

        # Tier 1: Classifier for simple classifications
        if request.task == "classify_intent":
            return await self.classifier.classify(request)

        # Tier 2: Small LLM for structured extraction
        if request.task in ["extract_entities", "summarize"]:
            return await self.small_llm.process(request)

        # Tier 3: Strong LLM for complex conversation
        if request.task == "generate_response":
            # Check if cached
            cache_key = self.get_cache_key(request)
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            response = await self.strong_llm.process(request)
            await self.cache.set(cache_key, response, ttl=3600)
            return response
```

## AI.5 Context Management

```python
class ConversationContext:
    """Manage conversation context efficiently."""

    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.system_prompt = self._load_system_prompt()
        self.patient_context = self._load_patient_context()
        self.clinic_context = self._load_clinic_context()
        self.conversation_history = self._load_recent_messages(limit=10)
        self.retrieved_docs = []

    def build_llm_messages(self, user_message: str) -> list:
        """Build messages for LLM, staying within token budget."""
        messages = []

        # System prompt (always included)
        messages.append({"role": "system", "content": self.system_prompt})

        # Clinic context (structured, compact)
        messages.append({
            "role": "system",
            "content": f"Clinic: {self.clinic_context.name}. "
                       f"Hours: {self.clinic_context.hours}. "
                       f"Phone: {self.clinic_context.phone}."
        })

        # Patient context (structured, minimal PHI)
        messages.append({
            "role": "system",
            "content": f"Patient: {self.patient_context.first_name}. "
                       f"State: {self.patient_context.state}. "
                       f"Preferred: {self.patient_context.preferred_channel}."
        })

        # Retrieved docs (RAG)
        if self.retrieved_docs:
            docs_content = "\n".join([d.content for d in self.retrieved_docs])
            messages.append({
                "role": "system",
                "content": f"Clinic Information:\n{docs_content}"
            })

        # Conversation history (last N messages)
        for msg in self.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _load_patient_context(self) -> PatientContext:
        """Load patient context with PHI minimization."""
        patient = db.get_patient(self.conversation_id)
        return PatientContext(
            first_name=patient.first_name,
            # NO: last_name, full phone, full email, DOB
            state=patient.state,
            last_visit=patient.last_visit_at,
            preferred_channel=patient.preferred_channel,
            # Only include what's needed for the conversation
        )
```

## AI.6 Tool Calling Design

```python
class PatientRecaptureTools:
    """Tools available to the AI agent."""

    def __init__(self, services: ServiceContainer):
        self.scheduling = services.scheduling
        self.insurance = services.insurance
        self.messages = services.messages
        self.patients = services.patients

    @tool(requires_confirmation=True)
    async def book_appointment(
        self,
        patient_id: str,
        service_id: str,
        provider_id: str,
        slot_start: str,  # ISO datetime
        slot_end: str,
        notes: str = ""
    ) -> dict:
        """Book an appointment for the patient.

        This action requires the patient's explicit confirmation.
        The AI must NOT call this tool without patient confirmation.
        """
        # 1. Verify patient consent
        if not await self.patients.has_consent(patient_id, "appointment_booking"):
            return {"error": "No consent for booking"}

        # 2. Verify slot is still available (race condition prevention)
        available = await self.scheduling.check_availability(
            provider_id, slot_start, slot_end
        )
        if not available:
            return {"error": "Slot no longer available"}

        # 3. Book via scheduling system
        result = await self.scheduling.book_appointment(
            patient_id=patient_id,
            service_id=service_id,
            provider_id=provider_id,
            slot_start=slot_start,
            slot_end=slot_end,
            notes=notes
        )

        # 4. Log the action
        await self.audit.log_action(
            action="appointment_booked",
            patient_id=patient_id,
            result=result
        )

        return {
            "success": True,
            "appointment_id": result.appointment_id,
            "scheduled_start": slot_start,
            "provider": result.provider_name
        }

    @tool
    async def check_availability(
        self,
        service_id: str,
        date: str,
        provider_id: Optional[str] = None
    ) -> dict:
        """Check available appointment slots.

        Returns available time slots for the given service and date.
        """
        slots = await self.scheduling.get_availability(
            service_id=service_id,
            date=date,
            provider_id=provider_id
        )

        return {
            "available": len(slots) > 0,
            "slots": [
                {
                    "start": slot.start.isoformat(),
                    "end": slot.end.isoformat(),
                    "provider": slot.provider_name
                }
                for slot in slots[:5]  # Max 5 slots
            ]
        }

    @tool
    async def check_insurance(
        self,
        patient_id: str,
        service_id: str
    ) -> dict:
        """Check insurance coverage for a service.

        NEVER fabricate insurance information.
        Always return actual verification result.
        """
        patient = await self.patients.get(patient_id)
        if not patient.insurance_carrier:
            return {"status": "no_insurance_on_file"}

        result = await self.insurance.verify(
            carrier=patient.insurance_carrier,
            insurance_id=patient.insurance_id,
            service_id=service_id
        )

        return {
            "status": result.status,  # active, inactive, unknown
            "coverage_verified": result.covered,
            "estimated_patient_responsibility": result.patient_portion,
            "note": "Coverage verification is pending final determination"
        }

    @tool(requires_confirmation=True)
    async def handoff_to_human(
        self,
        reason: str,
        urgency: str = "medium",
        context: dict = {}
    ) -> dict:
        """Transfer conversation to human staff.

        Use when:
        - Patient explicitly requests human
        - Medical/emergency situation detected
        - AI cannot resolve the issue
        - Patient is frustrated/complaining
        """
        handoff = await self.handoffs.create(
            conversation_id=self.conversation_id,
            patient_id=self.patient_id,
            reason=reason,
            urgency=urgency,
            context=context
        )

        # Notify available staff
        await self.notifications.notify_staff(
            clinic_id=self.clinic_id,
            message=f"Patient needs assistance: {reason}",
            urgency=urgency
        )

        return {
            "success": True,
            "handoff_id": handoff.id,
            "message": "I've connected you with our team. Someone will be with you shortly."
        }
```

## AI.7 Model Training Infrastructure

```python
class ModelTrainingPipeline:
    """End-to-end model training pipeline."""

    async def train_intent_classifier(self, dataset: Dataset):
        # 1. Split data (patient-level, time-based)
        train, val, test = dataset.patient_level_split(
            train_ratio=0.7,
            val_ratio=0.15,
            test_ratio=0.15
        )

        # 2. Train model
        model = IntentClassifier()
        model.train(train)

        # 3. Evaluate
        metrics = model.evaluate(test)
        # Check: precision, recall, F1, per-class metrics

        # 4. Validate against safety requirements
        safety_metrics = self.evaluate_safety(model, test)
        # Check: no safety-critical intents misclassified

        # 5. Compare to current production model
        if metrics.f1 > self.production_model.f1 + self.MIN_IMPROVEMENT:
            # 6. Shadow test
            shadow_result = await self.shadow_test(model)

            # 7. Canary deployment
            if shadow_result.error_rate < self.MAX_ERROR_RATE:
                await self.canary_deploy(model)

                # 8. Full rollout if canary succeeds
                if await self.canary_passes():
                    await self.full_deploy(model)
```
