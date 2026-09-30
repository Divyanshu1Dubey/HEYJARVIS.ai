# Database Schema — Complete Production Schema

## DB.1 Schema Design Principles

1. All tables have `tenant_id` (except reference tables)
2. Row-level security on all tables
3. Every table has `created_at`, `updated_at`
4. UUIDs for all primary keys
5. Soft deletes where appropriate
6. Audit trail in `state_transitions`
7. JSONB for flexible attributes
8. Proper indexes for query patterns
9. Idempotency keys for external events

## DB.2 Complete Schema

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Enable Row-Level Security
ALTER DATABASE heyjarvis SET row_security = on;

-- ============================================
-- TENANT & ORGANIZATION
-- ============================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE clinics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    address JSONB DEFAULT '{}',
    phone VARCHAR(20),
    email VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    business_hours JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, slug)
);

CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address JSONB DEFAULT '{}',
    phone VARCHAR(20),
    business_hours JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- USERS & ROLES
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    clinic_id UUID REFERENCES clinics(id),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'staff',
    permissions JSONB DEFAULT '[]',
    active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, email)
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, name)
);

-- ============================================
-- PATIENTS
-- ============================================

CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED, -- for RLS
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    address JSONB DEFAULT '{}',
    emergency_contact JSONB DEFAULT '{}',
    insurance_carrier VARCHAR(255),
    insurance_id VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    state VARCHAR(50) DEFAULT 'new_lead',
    first_visit_at TIMESTAMP,
    last_visit_at TIMESTAMP,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE patient_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    tenant_id UUID GENERATED ALWAYS AS (
        (SELECT clinic_id FROM patients WHERE id = patient_id)
    ) STORED,
    type VARCHAR(20) NOT NULL, -- phone, email, sms
    value VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    verification_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    tenant_id UUID GENERATED ALWAYS AS (
        (SELECT clinic_id FROM patients WHERE id = patient_id)
    ) STORED,
    type VARCHAR(50) NOT NULL, -- sms, email, voice, marketing, hipaa
    granted BOOLEAN NOT NULL,
    method VARCHAR(50), -- web_form, phone, in_person, verbal
    ip_address INET,
    consent_date TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    consenting_user_id UUID REFERENCES users(id),
    consent_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE communication_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    tenant_id UUID GENERATED ALWAYS AS (
        (SELECT clinic_id FROM patients WHERE id = patient_id)
    ) STORED,
    preferred_channel VARCHAR(20) DEFAULT 'sms',
    preferred_language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    quiet_hours JSONB DEFAULT '{"start": "21:00", "end": "09:00"}',
    do_not_contact BOOLEAN DEFAULT false,
    dnc_reason TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CONVERSATIONS & MESSAGES
-- ============================================

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    patient_id UUID REFERENCES patients(id),
    channel VARCHAR(20) NOT NULL, -- sms, email, web, voice, whatsapp
    status VARCHAR(20) DEFAULT 'active',
    intent VARCHAR(50),
    context JSONB DEFAULT '{}',
    assigned_to UUID REFERENCES users(id),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES patients(id),
    tenant_id UUID GENERATED ALWAYS AS (
        (SELECT clinic_id FROM conversations WHERE id = conversation_id)
    ) STORED,
    sender_type VARCHAR(20) NOT NULL, -- patient, ai, staff, system
    sender_id UUID,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    ai_data JSONB DEFAULT '{}',
    sent_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conversation_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    occurred_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE state_transitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL, -- patient, conversation, opportunity, campaign
    entity_id UUID NOT NULL,
    from_state VARCHAR(50),
    to_state VARCHAR(50) NOT NULL,
    event VARCHAR(100) NOT NULL,
    actor VARCHAR(50) NOT NULL, -- ai, staff, system, patient
    actor_id UUID,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- APPOINTMENTS
-- ============================================

CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    patient_id UUID NOT NULL REFERENCES patients(id),
    provider_id UUID REFERENCES providers(id),
    service_id UUID REFERENCES services(id),
    location_id UUID REFERENCES locations(id),
    scheduled_start TIMESTAMP NOT NULL,
    scheduled_end TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    cancellation_reason VARCHAR(100),
    cancellation_notes TEXT,
    notes TEXT,
    source VARCHAR(50), -- ai, staff, patient, phone, web
    created_by UUID REFERENCES users(id),
    pms_id VARCHAR(255), -- External PMS appointment ID
    pms_sync_status VARCHAR(20) DEFAULT 'synced',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE appointment_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    previous_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by_type VARCHAR(20), -- patient, ai, staff, system
    changed_by_id UUID,
    change_data JSONB DEFAULT '{}',
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE appointment_holds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    provider_id UUID NOT NULL REFERENCES providers(id),
    slot_start TIMESTAMP NOT NULL,
    slot_end TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    conversation_id UUID REFERENCES conversations(id),
    patient_id UUID REFERENCES patients(id),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PROVIDERS & SERVICES
-- ============================================

CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    user_id UUID REFERENCES users(id),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    title VARCHAR(20), -- DDS, DMD, RDH, etc.
    specialty VARCHAR(100),
    schedule JSONB DEFAULT '{}',
    accepts_new_patients BOOLEAN DEFAULT true,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2),
    requires_consultation BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- TREATMENT PLANS
-- ============================================

CREATE TABLE treatment_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    patient_id UUID NOT NULL REFERENCES patients(id),
    provider_id UUID REFERENCES providers(id),
    appointment_id UUID REFERENCES appointments(id),
    status VARCHAR(20) DEFAULT 'proposed',
    notes TEXT,
    total_cost DECIMAL(10,2),
    proposed_at TIMESTAMP DEFAULT NOW(),
    accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE treatment_plan_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    treatment_plan_id UUID NOT NULL REFERENCES treatment_plans(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id),
    description TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    cost DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    appointment_id UUID REFERENCES appointments(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- RECAPTURE
-- ============================================

CREATE TABLE recapture_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    patient_id UUID NOT NULL REFERENCES patients(id),
    appointment_id UUID REFERENCES appointments(id),
    treatment_plan_id UUID REFERENCES treatment_plans(id),
    campaign_id UUID REFERENCES recapture_campaigns(id),
    category VARCHAR(50) NOT NULL, -- lead, booking, cancellation, no_show, treatment, recall, inactive, operational
    sub_category VARCHAR(50),
    trigger_data JSONB DEFAULT '{}',
    potential_value DECIMAL(10,2),
    priority_score INTEGER DEFAULT 0,
    state VARCHAR(20) DEFAULT 'identified',
    detected_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recapture_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_event VARCHAR(100) NOT NULL,
    eligibility_rules JSONB DEFAULT '{}',
    sequence JSONB DEFAULT '[]', -- Array of steps
    active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recapture_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id UUID NOT NULL REFERENCES recapture_opportunities(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES recapture_campaigns(id),
    attempt_number INTEGER NOT NULL,
    channel VARCHAR(20) NOT NULL,
    state VARCHAR(20) DEFAULT 'pending',
    message_data JSONB DEFAULT '{}',
    outcome_data JSONB DEFAULT '{}',
    scheduled_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    responded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE channel_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID NOT NULL REFERENCES recapture_attempts(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,
    provider_message_id VARCHAR(255),
    state VARCHAR(20) DEFAULT 'queued',
    error_code VARCHAR(50),
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- AI & ML
-- ============================================

CREATE TABLE ai_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id),
    opportunity_id UUID REFERENCES recapture_opportunities(id),
    decision_type VARCHAR(50) NOT NULL,
    input_data JSONB DEFAULT '{}',
    decision_data JSONB DEFAULT '{}',
    model_version VARCHAR(50),
    confidence FLOAT,
    outcome VARCHAR(50),
    decided_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ai_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID NOT NULL REFERENCES ai_decisions(id),
    action_type VARCHAR(50) NOT NULL,
    parameters JSONB DEFAULT '{}',
    result JSONB DEFAULT '{}',
    state VARCHAR(20) DEFAULT 'pending',
    executed_at TIMESTAMP
);

CREATE TABLE model_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID REFERENCES ai_decisions(id),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    features JSONB DEFAULT '{}',
    prediction JSONB NOT NULL,
    probability FLOAT,
    predicted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE human_handoffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    reason VARCHAR(100) NOT NULL,
    urgency VARCHAR(20) DEFAULT 'medium',
    context JSONB DEFAULT '{}',
    assigned_to UUID REFERENCES users(id),
    state VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    assigned_at TIMESTAMP,
    resolved_at TIMESTAMP
);

-- ============================================
-- MESSAGING
-- ============================================

CREATE TABLE message_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    variables JSONB DEFAULT '[]',
    content_sms TEXT,
    content_email_subject VARCHAR(255),
    content_email_body TEXT,
    content_voice TEXT,
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE suppression_list (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    patient_id UUID REFERENCES patients(id),
    phone VARCHAR(20),
    email VARCHAR(255),
    reason VARCHAR(100),
    scope VARCHAR(50), -- campaign, global, temporary
    expires_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INTEGRATIONS
-- ============================================

CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    type VARCHAR(50) NOT NULL, -- pms, insurance, sms, email, voice
    provider VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    configuration JSONB DEFAULT '{}',
    credentials_encrypted BYTEA,
    state VARCHAR(20) DEFAULT 'configured',
    last_sync_at TIMESTAMP,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE integration_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    integration_id UUID NOT NULL REFERENCES integrations(id),
    event_type VARCHAR(100) NOT NULL,
    direction VARCHAR(20), -- inbound, outbound
    request_data JSONB DEFAULT '{}',
    response_data JSONB DEFAULT '{}',
    state VARCHAR(20), -- success, failed, timeout
    error_message TEXT,
    occurred_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    event_type VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    signature VARCHAR(500),
    processed BOOLEAN DEFAULT false,
    error_message TEXT,
    idempotency_key VARCHAR(255),
    received_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

-- ============================================
-- AUDIT
-- ============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- CAMPAIGNS
-- ============================================

CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id),
    tenant_id UUID GENERATED ALWAYS AS (clinic_id) STORED,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    state VARCHAR(20) DEFAULT 'draft',
    configuration JSONB DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- JOBS
-- ============================================

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(100) NOT NULL,
    clinic_id UUID REFERENCES clinics(id),
    payload JSONB DEFAULT '{}',
    result JSONB DEFAULT '{}',
    state VARCHAR(20) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

-- Patient lookups
CREATE INDEX idx_patients_clinic ON patients(clinic_id);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_patients_state ON patients(state);
CREATE INDEX idx_patients_active ON patients(active);

-- Appointment lookups
CREATE INDEX idx_appointments_clinic ON appointments(clinic_id);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_start ON appointments(scheduled_start);
CREATE INDEX idx_appointments_patient_status ON appointments(patient_id, status);

-- Conversation lookups
CREATE INDEX idx_conversations_clinic ON conversations(clinic_id);
CREATE INDEX idx_conversations_patient ON conversations(patient_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_sent_at ON messages(sent_at);

-- Recapture lookups
CREATE INDEX idx_opportunities_clinic ON recapture_opportunities(clinic_id);
CREATE INDEX idx_opportunities_patient ON recapture_opportunities(patient_id);
CREATE INDEX idx_opportunities_state ON recapture_opportunities(state);
CREATE INDEX idx_opportunities_priority ON recapture_opportunities(priority_score DESC);
CREATE INDEX idx_attempts_opportunity ON recapture_attempts(opportunity_id);

-- Consent lookups
CREATE INDEX idx_consents_patient_type ON consents(patient_id, type);
CREATE INDEX idx_consents_expires ON consents(expires_at);

-- Audit
CREATE INDEX idx_audit_clinic ON audit_logs(clinic_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(occurred_at);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- State transitions
CREATE INDEX idx_state_transitions_entity ON state_transitions(entity_type, entity_id);
CREATE INDEX idx_state_transitions_timestamp ON state_transitions(timestamp);

-- Webhooks
CREATE INDEX idx_webhooks_idempotency ON webhook_events(idempotency_key);
CREATE INDEX idx_webhooks_processed ON webhook_events(processed, received_at);
```

## DB.3 Row-Level Security Policies

```sql
-- Enable RLS on all tenant tables
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE recapture_opportunities ENABLE ROW LEVEL SECURITY;
-- ... etc for all tenant tables

-- Policy: Users can only see data from their clinic
CREATE POLICY tenant_isolation ON patients
    FOR ALL TO app_role
    USING (clinic_id = current_setting('app.current_tenant')::UUID);

-- Policy: Users must belong to the same organization
CREATE POLICY org_isolation ON users
    FOR ALL TO app_role
    USING (organization_id = current_setting('app.current_org')::UUID);
```

## DB.4 Idempotency Strategy

```sql
-- Idempotency tracking for external events
CREATE TABLE idempotency_keys (
    key VARCHAR(255) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Usage:
-- Before processing any external event:
INSERT INTO idempotency_keys (key, entity_type, entity_id)
VALUES ('webhook_abc123', 'appointment', 'uuid-here')
ON CONFLICT (key) DO NOTHING;
```
