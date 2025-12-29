# Design Document: Payment Gateway Simulator

## 1. Executive Summary

This document explains the architectural decisions and design principles behind the Payment Gateway Simulator project. It demonstrates production-grade software engineering practices suitable for Japanese companies valuing correctness and clarity.

---

## 2. Core Design Principles

### 2.1 Separation of Concerns

**Layer 1: API Layer (Routers)**
- HTTP request/response handling
- Authentication/authorization
- Input validation (Pydantic schemas)
- Response serialization

```python
# app/api/routers/payments.py
@router.post("/payments")
async def create_payment(
    request: CreatePaymentRequest,  # Validation
    merchant_data = Depends(get_current_merchant),  # Auth
) -> PaymentResponse:  # Serialization
    # Delegate to service
    service = PaymentService(session)
    payment = await service.create_payment(...)
    return PaymentResponse.from_orm(payment)
```

**Layer 2: Service Layer**
- Business logic
- State transitions
- Validation rules
- Orchestration

```python
# app/services/payment_service.py
class PaymentService:
    async def create_payment(self, merchant, amount, ...):
        # Validate
        if amount <= 0:
            raise ValidationError()
        
        # Create domain entity
        payment = await self.payment_repo.create(...)
        
        # State transition
        payment.status = PaymentStatus.AUTHORIZED
        
        # Side effects
        await self.webhook_service.create_event(...)
        
        return payment
```

**Layer 3: Repository Layer**
- Data access abstraction
- Query construction
- Type safety

```python
# app/repositories/payment_repository.py
class PaymentRepository(BaseRepository[Payment]):
    async def get_by_merchant_and_payment_id(
        self, merchant_id: str, payment_id: str
    ) -> Optional[Payment]:
        stmt = select(Payment).where(
            Payment.id == payment_id,
            Payment.merchant_id == merchant_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

**Layer 4: ORM Layer**
- SQLAlchemy models
- Database abstraction
- Type-safe queries

### 2.2 Type Safety

Every function has full type hints:

```python
async def create_payment(
    self,
    merchant: Merchant,
    amount: int,
    currency: str = "INR",
    description: Optional[str] = None,
    metadata: Optional[dict] = None,
    idempotency_key: Optional[str] = None,
    simulate: Optional[str] = None,
) -> tuple[Payment, dict]:  # Return type annotated
    ...
```

**Enforcement:**
- `mypy` for static type checking
- `disallow_untyped_defs = true` in mypy config
- Pydantic for runtime validation

### 2.3 Error Handling

Custom exception hierarchy:

```python
PaymentGatewayException  # Base
├── AuthenticationError  # 401
├── ValidationError      # 400
├── NotFoundError        # 404
├── ConflictError        # 409
└── PaymentError         # 402
```

All exceptions have:
- Meaningful error message
- Appropriate HTTP status code
- Consistent JSON response format

---

## 3. Domain Model

### 3.1 Entities

**Merchant**
```python
class Merchant:
    id: UUID
    name: str
    email: str  # Unique
    webhook_url: Optional[str]
    webhook_secret: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**APIKey**
```python
class APIKey:
    id: UUID
    merchant_id: UUID  # FK
    api_key: str  # Public (starts with "pk_")
    api_secret: str  # Private
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
```

**Payment** (Core Entity)
```python
class Payment:
    id: UUID
    merchant_id: UUID  # FK
    amount: int  # Amount in paise/cents (no floats!)
    currency: str  # ISO 4217
    status: PaymentStatus  # Enum
    error_code: Optional[str]
    error_message: Optional[str]
    metadata: Optional[dict]  # JSON
    created_at: datetime
    updated_at: datetime
    authorized_at: Optional[datetime]
    captured_at: Optional[datetime]
```

**Refund**
```python
class Refund:
    id: UUID
    payment_id: UUID  # FK
    amount: int  # Partial refund allowed
    reason: Optional[str]
    status: str
    created_at: datetime
```

**WebhookEvent**
```python
class WebhookEvent:
    id: UUID
    payment_id: UUID  # FK
    merchant_id: UUID  # FK
    event_type: WebhookEventType  # Enum
    payload: dict  # JSON
    status: WebhookStatus  # PENDING/DELIVERED/FAILED
    delivery_attempts: int
    next_retry_at: Optional[datetime]
    delivered_at: Optional[datetime]
```

**IdempotencyKey**
```python
class IdempotencyKey:
    id: UUID
    idempotency_key: str  # Unique
    merchant_id: UUID  # FK
    payment_id: UUID  # FK
    response_data: dict  # JSON
    expires_at: datetime  # 24 hours
```

### 3.2 Value Objects

**PaymentStatus** (Enum)
```python
CREATED → AUTHORIZED → CAPTURED → [REFUNDED]
              ↓
            FAILED
```

**WebhookEventType** (Enum)
```python
payment.created
payment.succeeded
payment.failed
payment.refunded
```

---

## 4. Key Features Deep Dive

### 4.1 Idempotency Implementation

**Problem:** What if payment request is sent twice due to network timeout?
```
Request 1: POST /payments (hangs)
Timeout ↓
Request 2: POST /payments (retry)
```

Without idempotency: Two payments created (bad!)

**Solution:** Idempotency keys

```python
async def create_payment(self, ..., idempotency_key: Optional[str] = None):
    # Check if we've seen this key before
    if idempotency_key:
        existing_key = await self.idempotency_repo.get_by_key(idempotency_key)
        if existing_key:
            # Return cached response
            return await self.payment_repo.get_by_id(existing_key.payment_id), existing_key.response_data
    
    # Create new payment
    payment = await self.payment_repo.create(...)
    
    # Store idempotency key with response
    if idempotency_key:
        await self.idempotency_repo.create(
            idempotency_key=idempotency_key,
            payment_id=payment.id,
            response_data={...},
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
    
    return payment, response_data
```

**Client Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Idempotency-Key: unique-key-12345" \
  -d '{...}'
```

**Behavior:**
- First request: Creates payment, stores response
- Retry with same key: Returns cached response instantly
- New request: New idempotency key → new payment
- Expiry: After 24 hours, key can be reused

### 4.2 Webhook Signing

**Problem:** How do merchants verify webhooks come from payment gateway?

Without signing: Anyone can POST to webhook URL (CSRF attack)

**Solution:** HMAC-SHA256 signatures

```python
# Gateway signs payload
import hmac, hashlib

payload_json = json.dumps(webhook_event.payload)
signature = hmac.new(
    webhook_secret.encode(),
    payload_json.encode(),
    hashlib.sha256
).hexdigest()

# Send webhook with signature
headers = {
    'X-Webhook-Signature': signature,
    'X-Webhook-ID': webhook_event.id,
}

await client.post(webhook_url, json=payload, headers=headers)
```

**Merchant Verification:**

```python
# Merchant receives webhook
def verify_webhook(request):
    signature = request.headers['X-Webhook-Signature']
    body = request.body  # Raw bytes
    
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,  # Use raw request body, not parsed JSON!
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        raise ValueError('Invalid signature')
    
    # Safe to process webhook
    payload = json.loads(body)
    process_payment(payload)
```

**Security Properties:**
- ✅ Only gateway can sign (knows secret)
- ✅ Tampering detected (signature changes)
- ✅ Timing-safe comparison (prevents timing attacks)
- ✅ Nonce in `X-Webhook-ID` (prevents replay)

### 4.3 Payment State Machine

**Valid Transitions:**

```python
CREATED
  ├─→ AUTHORIZED (on successful authorization)
  │     ├─→ CAPTURED (on capture)
  │     │     └─→ REFUNDED (on refund)
  │     └─→ FAILED (on capture failure)
  └─→ FAILED (on authorization failure)
```

**Implementation:**

```python
async def capture_payment(self, merchant_id: str, payment_id: str) -> Payment:
    payment = await self.get_payment(merchant_id, payment_id)
    
    # Validate state
    if payment.status != PaymentStatus.AUTHORIZED:
        raise ConflictError(
            f"Cannot capture {payment.status} payment. Expected: AUTHORIZED"
        )
    
    # Transition state
    payment.status = PaymentStatus.CAPTURED
    payment.captured_at = datetime.utcnow()
    
    await self.payment_repo.update(payment)
    await self.webhook_service.create_event(...)
    
    return payment
```

**Benefits:**
- ✅ Type safety (PaymentStatus enum)
- ✅ Validation (explicit checks)
- ✅ Atomicity (single transaction)
- ✅ Auditability (timestamps)

### 4.4 Simulation System

**Purpose:** Test payment failures without real payment processor

**Implementation:**

```python
async def _simulate_payment(
    self, payment: Payment, simulation: SimulationType
) -> tuple[Payment, WebhookEventType]:
    
    if simulation == SimulationType.SUCCESS:
        payment.status = PaymentStatus.CAPTURED
        return payment, WebhookEventType.PAYMENT_SUCCEEDED
    
    elif simulation == SimulationType.INSUFFICIENT_FUNDS:
        payment.status = PaymentStatus.FAILED
        payment.error_code = "INSUFFICIENT_FUNDS"
        payment.error_message = "Insufficient funds in account"
        return payment, WebhookEventType.PAYMENT_FAILED
    
    elif simulation == SimulationType.FRAUD_DETECTED:
        payment.status = PaymentStatus.FAILED
        payment.error_code = "FRAUD_DETECTED"
        payment.error_message = "Transaction flagged as fraudulent"
        return payment, WebhookEventType.PAYMENT_FAILED
    
    # ... more simulations
```

**Supported Scenarios:**
```
simulate=success              → Payment succeeds
simulate=insufficient_funds   → NSF error
simulate=network_timeout      → Gateway timeout
simulate=fraud_detected       → Fraud detection
simulate=bank_error           → Bank rejection
```

---

## 5. Database Design

### 5.1 Schema

```sql
-- Merchants
CREATE TABLE merchants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    webhook_url TEXT,
    webhook_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_merchant_email (email)
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_secret VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP,
    UNIQUE KEY uq_merchant_api_key (merchant_id, api_key),
    INDEX idx_api_key_key (api_key),
    INDEX idx_api_key_merchant (merchant_id)
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    amount INT NOT NULL,  -- paise/cents
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(50) NOT NULL,
    description TEXT,
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    metadata JSON,
    error_code VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    authorized_at TIMESTAMP,
    captured_at TIMESTAMP,
    INDEX idx_payment_merchant (merchant_id),
    INDEX idx_payment_status (status),
    INDEX idx_payment_created (created_at)
);

-- Refunds
CREATE TABLE refunds (
    id UUID PRIMARY KEY,
    payment_id UUID NOT NULL REFERENCES payments(id),
    amount INT NOT NULL,
    reason VARCHAR(255),
    status VARCHAR(50) DEFAULT 'COMPLETED',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_refund_payment (payment_id),
    INDEX idx_refund_created (created_at)
);

-- Webhook Events
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY,
    payment_id UUID NOT NULL REFERENCES payments(id),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    event_type VARCHAR(50) NOT NULL,
    payload JSON NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    delivery_attempts INT DEFAULT 0,
    last_error TEXT,
    next_retry_at TIMESTAMP,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_webhook_payment (payment_id),
    INDEX idx_webhook_merchant (merchant_id),
    INDEX idx_webhook_status (status),
    INDEX idx_webhook_next_retry (next_retry_at)
);

-- Idempotency Keys
CREATE TABLE idempotency_keys (
    id UUID PRIMARY KEY,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    payment_id UUID NOT NULL REFERENCES payments(id),
    response_data JSON NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    INDEX idx_idempotency_key (idempotency_key),
    INDEX idx_idempotency_merchant (merchant_id),
    INDEX idx_idempotency_expires (expires_at)
);
```

### 5.2 Indexing Strategy

| Index | Reason |
|-------|--------|
| `idx_merchant_email` | Email lookup for authentication |
| `idx_api_key_key` | API key lookup on every request |
| `idx_payment_merchant` | List payments for merchant |
| `idx_payment_status` | Query by status (for reporting) |
| `idx_payment_created` | Time-range queries |
| `idx_webhook_status` | Find pending webhooks for retry |
| `idx_webhook_next_retry` | Find webhooks due for retry |
| `idx_idempotency_key` | Lookup on every payment creation |
| `idx_idempotency_expires` | Cleanup expired keys |

### 5.3 Data Type Choices

**Why UUID for IDs?**
- ✅ Distributed systems (no central sequence needed)
- ✅ Privacy (can't enumerate resources by ID)
- ✅ Security (harder to guess valid IDs)
- ✅ Standard in modern APIs

**Why INT for amounts?**
- ✅ No precision loss (unlike float)
- ✅ Smaller storage than DECIMAL
- ✅ Faster arithmetic operations
- ✅ Industry standard (paise/cents)

**Why JSON for metadata?**
- ✅ Flexible schema
- ✅ Native PostgreSQL support
- ✅ Queryable within database
- ✅ Serializes to API responses easily

---

## 6. API Design

### 6.1 RESTful Principles

```
POST   /api/v1/payments              Create payment
GET    /api/v1/payments/{id}         Get payment
POST   /api/v1/payments/{id}/capture Capture payment
POST   /api/v1/payments/{id}/refund  Refund payment
```

**HTTP Status Codes:**
- `200 OK` - Successful GET
- `201 Created` - Successful POST (resource created)
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Resource not found
- `409 Conflict` - Invalid state transition
- `500 Internal Server Error` - Unexpected error

### 6.2 Request/Response Format

**Request:**
```json
{
  "amount": 10000,
  "currency": "INR",
  "description": "Order #123",
  "customer_email": "user@example.com",
  "metadata": {"order_id": "123"}
}
```

**Response (Success):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 10000,
  "currency": "INR",
  "status": "CAPTURED",
  "description": "Order #123",
  "customer_email": "user@example.com",
  "metadata": {"order_id": "123"},
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "error_code": null,
  "error_message": null
}
```

**Response (Error):**
```json
{
  "error": {
    "message": "Validation failed",
    "details": [{"field": "amount", "message": "Amount must be greater than 0"}],
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

### 6.3 Pagination (Future)

```
GET /api/v1/payments?limit=20&offset=0
```

---

## 7. Testing Strategy

### 7.1 Test Pyramid

```
        /\        E2E Tests (5%)
       /  \       Integration Tests (25%)
      /    \      Unit Tests (70%)
     /______\
```

### 7.2 Unit Tests (app/services)

```python
# tests/test_payment_service.py

class TestPaymentService:
    async def test_create_payment_success(self):
        """Successful payment creation"""
    
    async def test_create_payment_invalid_amount(self):
        """Negative amount rejected"""
    
    async def test_idempotency(self):
        """Same key returns same payment"""
    
    async def test_invalid_state_transition(self):
        """Cannot capture non-authorized payment"""
```

### 7.3 Integration Tests (full flow)

```python
# tests/test_integration.py

async def test_payment_lifecycle():
    """Create → Authorize → Capture → Refund"""
    # 1. Create payment
    payment = await service.create_payment(...)
    assert payment.status == CAPTURED
    
    # 2. Refund payment
    refund = await service.refund_payment(payment.id)
    assert refund.status == COMPLETED
    
    # 3. Verify webhooks created
    events = await webhook_repo.get_by_payment_id(payment.id)
    assert len(events) == 2  # created + succeeded
```

### 7.4 Test Coverage Target

- **Services**: 95%+
- **Repositories**: 90%+
- **Models**: 100% (enforced by mypy)
- **Routers**: 85%+ (tricky to test, focuses on business logic)
- **Total**: 90%+

---

## 8. Future Improvements

### Phase 2
- [ ] Webhook retry with exponential backoff
- [ ] Redis-based idempotency cache (faster lookups)
- [ ] Rate limiting enforcement
- [ ] Merchant dashboard UI
- [ ] Payment analytics (reporting)

### Phase 3
- [ ] Subscription payments
- [ ] Batch refunds
- [ ] Payment splits
- [ ] Compliance logging (PCI-DSS)
- [ ] Audit trail

---

## 9. Monitoring & Observability

### Metrics to Track

```
# Payment metrics
payment_creation_count
payment_success_rate
payment_failure_rate
payment_refund_rate

# Performance metrics
api_response_time
payment_creation_latency
webhook_delivery_latency
database_query_time

# Business metrics
total_payment_amount
refunded_amount
mean_payment_amount
```

### Logging Strategy

```python
# Structured logging (JSON)
logger.info(
    "payment_created",
    extra={
        "payment_id": payment.id,
        "merchant_id": merchant.id,
        "amount": payment.amount,
        "status": payment.status,
    }
)
```

---

## Conclusion

This Payment Gateway Simulator demonstrates:

✅ **Correctness** - Type-safe, well-tested code
✅ **Predictability** - Clear state machines, idempotent operations
✅ **Security** - HMAC signing, input validation, auth
✅ **Production-Ready** - Docker, migrations, monitoring
✅ **Documentation** - Code comments, design rationale
✅ **Scalability** - Async/await, database indexing
✅ **Maintainability** - Clean architecture, separation of concerns

Built for excellence. Built for Japan. 🇯🇵
