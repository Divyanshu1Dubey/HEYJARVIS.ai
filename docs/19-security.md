# Security Architecture — Application and Infrastructure Security

## SC.1 Security Principles

1. **Defense in depth.** Multiple layers of security controls.
2. **Least privilege.** Users and services have minimum necessary access.
3. **Assume breach.** Design for compromise detection and response.
4. **Zero trust.** Verify every request, every time.
5. **Encrypt everything.** PHI at rest and in transit.
6. **Audit everything.** Every action is logged and reviewable.

## SC.2 Authentication

### JWT-Based Authentication

```python
class AuthService:
    """JWT-based authentication with tenant isolation."""

    async def create_token(self, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(user.clinic_id),
            "org_id": str(user.organization_id),
            "roles": user.roles,
            "permissions": user.permissions,
            "iat": datetime.now(),
            "exp": datetime.now() + timedelta(hours=24)
        }
        return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    async def validate_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
```

### Multi-Factor Authentication

```python
class MFAService:
    """MFA for staff accounts."""

    async def enable_mfa(self, user_id: str, method: str):
        if method == "totp":
            secret = pyotp.random_base32()
            await self.save_totp_secret(user_id, secret)
            return self.generate_qr_code(user_id, secret)
        elif method == "sms":
            code = generate_code()
            await self.save_sms_code(user_id, code)
            await self.send_sms_code(user_id, code)

    async def verify_mfa(self, user_id: str, code: str) -> bool:
        stored = await self.get_mfa_code(user_id)
        if not stored or stored.expired:
            return False
        return stored.code == code
```

## SC.3 Authorization

### Role-Based Access Control

```python
class RBACService:
    """Role-based access control."""

    ROLES = {
        "owner": {
            "permissions": ["*"]  # All permissions
        },
        "admin": {
            "permissions": [
                "patients:read", "patients:write",
                "appointments:read", "appointments:write",
                "campaigns:read", "campaigns:write",
                "analytics:read",
                "settings:read", "settings:write",
                "staff:read", "staff:write"
            ]
        },
        "manager": {
            "permissions": [
                "patients:read",
                "appointments:read", "appointments:write",
                "campaigns:read", "campaigns:write",
                "analytics:read"
            ]
        },
        "front_desk": {
            "permissions": [
                "patients:read", "patients:write",
                "appointments:read", "appointments:write",
                "conversations:read", "conversations:write"
            ]
        },
        "staff": {
            "permissions": [
                "patients:read",
                "appointments:read",
                "conversations:read", "conversations:write"
            ]
        },
        "readonly": {
            "permissions": [
                "patients:read",
                "appointments:read",
                "analytics:read"
            ]
        }
    }

    async def check_permission(self, user: User, resource: str, action: str) -> bool:
        if "*" in user.permissions:
            return True
        return f"{resource}:{action}" in user.permissions
```

### Tenant Isolation

```sql
-- Row-level security for tenant isolation
CREATE POLICY tenant_isolation ON patients
    FOR ALL TO app_role
    USING (
        clinic_id = current_setting('app.current_tenant')::UUID
        AND
        organization_id = current_setting('app.current_org')::UUID
    );

-- Application sets tenant on each request
async def set_tenant_context(request):
    token = request.headers.get("Authorization")
    payload = await auth.validate_token(token)
    await db.execute(
        "SET app.current_tenant = :tenant",
        {"tenant": payload.tenant_id}
    )
    await db.execute(
        "SET app.current_org = :org",
        {"org": payload.org_id}
    )
```

## SC.4 Data Protection

### Encryption at Rest

```python
class EncryptionService:
    """Handle data encryption."""

    # All PHI fields are encrypted
    ENCRYPTED_FIELDS = {
        "patients": ["phone", "email", "address", "date_of_birth"],
        "messages": ["content"],
        "appointments": ["notes"]
    }

    async def encrypt_field(self, value: str, field: str, table: str) -> str:
        if field not in self.ENCRYPTED_FIELDS.get(table, []):
            return value
        return self.fernet.encrypt(value.encode()).decode()

    async def decrypt_field(self, value: str, field: str, table: str) -> str:
        if field not in self.ENCRYPTED_FIELDS.get(table, []):
            return value
        return self.fernet.decrypt(value.encode()).decode()
```

### Encryption in Transit

```
All communication requires TLS 1.3:

API → Client: HTTPS (TLS 1.3)
API → Database: TLS
API → Cache: TLS (optional, internal network)
Workers → Queue: TLS (optional, internal network)
External APIs: TLS 1.2 minimum
Webhooks: TLS 1.2 minimum

Certificate management:
- Automated renewal (Let's Encrypt / ACM)
- Certificate pinning for mobile apps
- HSTS headers
```

## SC.5 Secrets Management

```python
class SecretsService:
    """Centralized secrets management."""

    # NEVER store secrets in:
    # - Environment variables (use vault)
    # - Configuration files
    # - Database
    # - Logs

    async def get_secret(self, key: str) -> str:
        return await self.vault.read(f"secret/{key}")

    async def rotate_secret(self, key: str):
        """Rotate a secret."""
        new_value = generate_secure_random()
        await self.vault.write(f"secret/{key}", new_value)
        await self.update_references(key)
```

**Secrets stored in Vault:**
- Database credentials
- LLM API keys
- SMS provider API keys
- Email provider API keys
- JWT signing keys
- Encryption keys
- Integration credentials

## SC.6 Input Validation

```python
from pydantic import BaseModel, validator, EmailStr, constr
import re

class PatientCreate(BaseModel):
    first_name: constr(min_length=1, max_length=100, pattern="^[a-zA-Z\s\-'.]+$")
    last_name: constr(min_length=1, max_length=100, pattern="^[a-zA-Z\s\-'.]+$")
    phone: constr(pattern=r'^\+[1-9]\d{1,14}$')  # E.164 format
    email: Optional[EmailStr]
    date_of_birth: date

    @validator('date_of_birth')
    def validate_age(cls, v):
        age = (date.today() - v).days / 365.25
        if age < 0 or age > 120:
            raise ValueError("Invalid age")
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError("Invalid phone format")
        return v
```

## SC.7 SQL Injection Prevention

```python
# ALWAYS use parameterized queries
# NEVER concatenate user input into SQL

# CORRECT:
await db.execute(
    "SELECT * FROM patients WHERE phone = :phone AND clinic_id = :clinic",
    {"phone": phone, "clinic": clinic_id}
)

# WRONG:
await db.execute(
    f"SELECT * FROM patients WHERE phone = '{phone}'"  # SQL injection!
)

# Use ORM for complex queries
patient = await Patient.filter(phone=phone, clinic_id=clinic_id).first()
```

## SC.8 Rate Limiting

```python
class RateLimiter:
    """Rate limiting per user and per endpoint."""

    LIMITS = {
        "api:default": {"requests": 1000, "window": 60},
        "api:ai": {"requests": 100, "window": 60},
        "api:websocket": {"messages": 50, "window": 60},
        "login:attempts": {"requests": 5, "window": 300}
    }

    async def check(self, key: str, limit_name: str) -> bool:
        limit = self.LIMITS.get(limit_name, self.LIMITS["api:default"])
        current = await self.redis.incr(key)

        if current == 1:
            await self.redis.expire(key, limit["window"])

        return current <= limit["requests"]
```

## SC.9 Prompt Injection Defense

```python
class PromptInjectionDefense:
    """Defend against prompt injection attacks."""

    INJECTION_PATTERNS = [
        r"ignore (previous|all) instructions",
        r"disregard (previous|all) (instructions|rules)",
        r"you are now",
        r"new instructions:",
        r"system:",
        r"admin mode",
        r"developer mode",
        r"pretend you are",
        r"act as if",
        r"your new role is",
        r"forget everything",
        r"override",
        r"bypass"
    ]

    async def check_injection(self, user_input: str) -> bool:
        """Check if user input contains prompt injection attempt."""
        lower_input = user_input.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, lower_input):
                await self.log_injection_attempt(user_input)
                return True
        return False

    async def sanitize_input(self, user_input: str) -> str:
        """Remove potential injection patterns."""
        sanitized = user_input
        for pattern in self.INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[filtered]", sanitized, flags=re.IGNORECASE)
        return sanitized
```

## SC.10 Cross-Tenant Leakage Prevention

```python
class TenantIsolationMiddleware:
    """Ensure no cross-tenant data leakage."""

    async def __call__(self, request, call_next):
        # Extract tenant from token (NEVER from client)
        token = request.headers.get("Authorization")
        payload = await auth.validate_token(token)

        # Set tenant context
        request.state.tenant_id = payload.tenant_id
        request.state.user_id = payload.user_id

        # Verify all queries use tenant context
        response = await call_next(request)

        return response

# All data access must include tenant_id
class TenantQuery:
    async def get_patient(self, patient_id: str, tenant_id: str):
        # CORRECT: tenant is part of the query
        return await db.query(
            "SELECT * FROM patients WHERE id = :id AND clinic_id = :tenant",
            {"id": patient_id, "tenant": tenant_id}
        )

    # WRONG: no tenant filter — can return other clinic's patients!
    async def get_patient_unsafe(self, patient_id: str):
        return await db.query(
            "SELECT * FROM patients WHERE id = :id",
            {"id": patient_id}
        )
```

## SC.11 Logging and Monitoring

```python
class SecurityLogger:
    """Security event logging."""

    SECURITY_EVENTS = [
        "login_success", "login_failure", "login_brute_force",
        "permission_denied", "data_access", "data_export",
        "data_deletion", "consent_change", "opt_out",
        "prompt_injection_attempt", "safety_escalation",
        "handoff_created", "admin_action", "config_change"
    ]

    async def log(self, event_type: str, **kwargs):
        """Log security event."""
        log_entry = {
            "event_type": event_type,
            "timestamp": datetime.now(),
            "user_id": kwargs.get("user_id"),
            "tenant_id": kwargs.get("tenant_id"),
            "ip_address": kwargs.get("ip_address"),
            "user_agent": kwargs.get("user_agent"),
            "details": kwargs.get("details", {})
        }

        # Store in audit log
        await self.db.execute(
            "INSERT INTO security_audit_log (event_type, event_data, user_id, tenant_id) "
            "VALUES (:type, :data, :user, :tenant)",
            log_entry
        )

        # Alert on critical events
        if event_type in ["login_brute_force", "prompt_injection_attempt"]:
            await self.alert_security_team(log_entry)
```

## SC.12 Vulnerability Management

```python
class VulnerabilityScanner:
    """Regular security scanning."""

    async def run_scan(self):
        results = {
            "dependency_check": await self.scan_dependencies(),
            "sast_scan": await self.scan_code(),
            "dast_scan": await self.scan_running_app(),
            "secret_scan": await self.scan_for_secrets(),
            "configuration_audit": await self.audit_config()
        }

        critical = [r for r in results if r.severity == "critical"]
        if critical:
            await self.alert_security_team(critical)

        return results
```

## SC.13 Incident Response

```python
class SecurityIncident:
    """Handle security incidents."""

    async def respond(self, incident_type: str, severity: str):
        if severity == "critical":
            # Immediate response
            await self.isolate_affected_systems()
            await self.preserve_evidence()
            await self.notify_security_team()
            await self.notify_dpo()  # Data Protection Officer
            await self.assess_phi_exposure()

            if self.phi_exposed:
                await self.initiate_breach_response()
```

## SC.14 Security Testing

| Test Type | Frequency | Tool |
|-----------|-----------|------|
| Dependency vulnerability scan | Daily | Snyk / Dependabot |
| Static application security testing | Every PR | Semgrep / Bandit |
| Dynamic application security testing | Weekly | OWASP ZAP |
| Secret scanning | Every commit | GitGuardian / TruffleHog |
| Penetration testing | Quarterly | External firm |
| Compliance audit | Annual | External auditor |
| Red team exercise | Quarterly | Internal/external team |
| Access control review | Monthly | Manual review |
