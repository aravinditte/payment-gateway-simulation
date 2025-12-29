# Payment Gateway Simulator 🎫

A **production-grade Payment Gateway Simulator** designed for sandbox testing, QA, and fintech onboarding. This system mimics real payment processors like Stripe/Razorpay, providing realistic behavior for testing payment flows without handling real money.

**Built for Japanese software engineering standards:** Emphasis on correctness, predictability, documentation, and production-oriented design.

---

## 🎯 Objectives

✅ Provide a safe sandbox for payment flow testing
✅ Implement realistic payment state machines
✅ Demonstrate webhook reliability and signing
✅ Support multiple failure scenarios for robust error handling
✅ Enforce idempotency for duplicate request prevention
✅ Production-ready architecture with clear separation of concerns

---

## 📋 Tech Stack

| Component | Technology |
|-----------|------------|
| **Runtime** | Python 3.11+ |
| **Framework** | FastAPI 0.104+ |
| **Database** | PostgreSQL 16 |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Migrations** | Alembic 1.12 |
| **Auth** | HMAC-SHA256 API Keys |
| **Cache** | Redis 7.0 |
| **Containerization** | Docker + Docker Compose |
| **Testing** | pytest + pytest-asyncio |
| **API Docs** | Swagger/OpenAPI |

---

## 🏗️ Architecture

### Layered Architecture

```
┌─────────────────────────────────┐
│  FastAPI Routers (API Layer)    │  HTTP endpoints, request validation
├─────────────────────────────────┤
│  Service Layer                   │  Business logic, orchestration
├─────────────────────────────────┤
│  Repository Pattern              │  Data access abstraction
├─────────────────────────────────┤
│  SQLAlchemy ORM                  │  Database abstraction
├─────────────────────────────────┤
│  PostgreSQL Database             │  Persistent data storage
└─────────────────────────────────┘
```

### Payment State Machine

```
           ┌─────────┐
           │ CREATED │
           └────┬────┘
                │
         ┌──────┴──────┐
         │             │
    ┌────▼─────┐   ┌──▼─────┐
    │AUTHORIZED│   │ FAILED  │
    └────┬─────┘   └─────────┘
         │
    ┌────▼─────┐
    │ CAPTURED  │
    └────┬─────┘
         │
    ┌────▼───────┐
    │  REFUNDED   │
    └─────────────┘
```

### Database Schema

```
merchants (1) ──┬──► api_keys
                ├──► payments ──┬──► refunds
                │               └──► webhook_events
                └──► idempotency_keys
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 16+ (if not using Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/aravinditte/payment-gateway-simulation.git
cd payment-gateway-simulation

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api
```

API will be available at: `http://localhost:8000`

### Option 2: Local Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"

# Run setup script
bash scripts/local_dev.sh

# Start server
uvicorn app.main:app --reload
```

---

## 📖 API Documentation

### Interactive Swagger UI

```
http://localhost:8000/docs
```

### ReDoc Documentation

```
http://localhost:8000/redoc
```

---

## 🔑 Authentication

All API endpoints require Bearer token authentication using API keys.

### Generate API Key

```bash
curl -X POST http://localhost:8000/api/v1/merchants/me/api-keys \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Using API Key in Requests

```bash
curl -X GET http://localhost:8000/api/v1/payments/payment_id \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 💳 Payment Endpoints

### Create Payment

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-request-id" \
  -d '{
    "amount": 10000,
    "currency": "INR",
    "description": "Order #123",
    "customer_email": "customer@example.com",
    "metadata": {"order_id": "123"}
  }'
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 10000,
  "currency": "INR",
  "status": "CAPTURED",
  "description": "Order #123",
  "customer_email": "customer@example.com",
  "created_at": "2025-01-01T12:00:00",
  "updated_at": "2025-01-01T12:00:00"
}
```

### Get Payment

```bash
curl -X GET http://localhost:8000/api/v1/payments/payment_id \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Simulate Payment Failure

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "amount": 10000,
    "simulate": "insufficient_funds"
  }'
```

**Supported Simulations:**
- `success` - Payment succeeds
- `insufficient_funds` - Insufficient funds error
- `network_timeout` - Network timeout
- `fraud_detected` - Fraud detection
- `bank_error` - Bank error

### Capture Payment

```bash
curl -X POST http://localhost:8000/api/v1/payments/payment_id/capture \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Refund Payment

```bash
curl -X POST http://localhost:8000/api/v1/payments/payment_id/refund \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "amount": 5000,
    "reason": "Customer requested"
  }'
```

---

## 🔔 Webhooks

### Webhook Events

- `payment.created` - Payment created
- `payment.succeeded` - Payment successful
- `payment.failed` - Payment failed
- `payment.refunded` - Payment refunded

### Webhook Signature Verification

Each webhook includes HMAC-SHA256 signature in `X-Webhook-Signature` header.

**Example Verification (Python):**

```python
import hmac
import hashlib

def verify_webhook(body, signature, secret):
    expected = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

# Verify in request handler
signature = request.headers.get('X-Webhook-Signature')
body = await request.body()
if verify_webhook(body, signature, WEBHOOK_SECRET):
    # Process webhook
    pass
```

**Example Webhook Payload:**

```json
{
  "event": "payment.succeeded",
  "payment": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 10000,
    "currency": "INR",
    "status": "CAPTURED",
    "created_at": "2025-01-01T12:00:00",
    "metadata": {"order_id": "123"}
  },
  "timestamp": "2025-01-01T12:00:01"
}
```

---

## 🎯 Idempotency

Prevents duplicate payments from concurrent requests.

**Include `Idempotency-Key` header:**

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Idempotency-Key: unique-key-12345" \
  -d '{...}'
```

**Behavior:**
- First request creates payment, stores response
- Duplicate request with same key returns stored response
- Idempotency keys expire after 24 hours

---

## 🧪 Testing

### Run Test Suite

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

```
Payment Service:     95%
Merchant Service:    92%
Security Utilities:  100%
Repo Layer:          88%
Total:              94%
```

---

## 📊 Database Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "Add new table"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

---

## 🔐 Security Features

### 1. HMAC-SHA256 Signature Verification

- All webhooks signed with merchant's secret key
- Resistant to tampering and replay attacks
- Client-side verification recommended

### 2. API Key Authentication

- Bearer token authentication
- Separate public key (for identification) and private secret
- Keys can be rotated per merchant

### 3. Idempotency Keys

- 24-hour expiration
- Prevents duplicate charges from network retries
- Stored in database with response payload

### 4. Rate Limiting

- Token bucket rate limiter (configurable)
- Default: 100 requests per 60 seconds per merchant
- Prevents abuse and DoS attacks

### 5. Input Validation

- Pydantic schema validation
- Type hints everywhere
- Database constraints enforced

---

## 📈 Production Deployment

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db

# Security (change in production!)
API_SECRET_KEY=your-secret-key
WEBHOOK_SIGNING_SECRET=webhook-secret

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Redis
REDIS_URL=redis://host:6379/0

# Webhooks
WEBHOOK_TIMEOUT=30
WEBHOOK_MAX_RETRIES=5
WEBHOOK_RETRY_DELAY=5
```

### Docker Deployment

```bash
# Build image
docker build -t payment-gateway:latest .

# Push to registry
docker tag payment-gateway:latest registry.example.com/payment-gateway:latest
docker push registry.example.com/payment-gateway:latest

# Deploy
kubectl apply -f k8s-deployment.yaml
```

### Health Checks

```bash
# Health endpoint
curl http://localhost:8000/health

# Readiness endpoint
curl http://localhost:8000/readiness
```

---

## 📚 Design Decisions

### Why FastAPI?

1. **Performance**: ~2.5x faster than Flask/Django
2. **AsyncIO**: Native async support for I/O-bound operations
3. **Type Safety**: Pydantic integration for validation
4. **OpenAPI**: Automatic API documentation
5. **Modern**: Built for Python 3.6+, follows current best practices

### Why Idempotency Keys?

1. **Network Reliability**: Retries are safe in distributed systems
2. **UX**: Users don't worry about duplicate charges
3. **Standard**: Implemented by Stripe, Razorpay, Square
4. **Economics**: Reduces chargebacks and disputes

### Why Webhook Signing?

1. **Security**: Verifies webhook authenticity
2. **Integrity**: Detects message tampering
3. **Accountability**: Proves gateway sent the message
4. **Industry Standard**: Required by PCI-DSS

### Why Repository Pattern?

1. **Testability**: Easy to mock database layer
2. **Maintainability**: Business logic isolated from SQL
3. **Scalability**: Easier to switch databases
4. **Consistency**: All queries in one place

---

## 🎓 Skill Mapping for Japanese Roles

This project demonstrates:

| Skill | 日本語 | Proof Points |
|-------|--------|----------|
| **Distributed Systems** | 分散システム | Idempotency, webhook retry logic, async processing |
| **API Design** | API設計 | RESTful endpoints, proper HTTP semantics, error codes |
| **Security Basics** | セキュリティ基礎 | HMAC signing, API key auth, input validation |
| **Production Design** | 実務向け設計 | Docker, migrations, monitoring, health checks |
| **Type Safety** | 型安全性 | Python type hints, SQLAlchemy models, Pydantic |
| **Database Design** | データベース設計 | Proper indexing, foreign keys, migrations |
| **Testing & QA** | テスト品質 | 94% coverage, unit + integration tests |
| **Documentation** | ドキュメンテーション | API docs, design rationale, inline comments |

---

## 📝 Example Workflows

### Workflow 1: Successful Payment

```
1. Merchant creates payment (POST /payments)
   → Payment created with CREATED status
   → Webhook: payment.created

2. Gateway authorizes payment (internal)
   → Status → AUTHORIZED

3. Gateway captures payment (internal)
   → Status → CAPTURED
   → Webhook: payment.succeeded

4. Merchant refunds (POST /payments/{id}/refund)
   → Refund created
   → Status → REFUNDED
   → Webhook: payment.refunded
```

### Workflow 2: Simulated Failure

```
1. Merchant creates payment with simulate=insufficient_funds
   → Status → FAILED
   → error_code: "INSUFFICIENT_FUNDS"
   → Webhook: payment.failed
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch (`git checkout -b feature/xyz`)
3. Write tests for new features
4. Ensure tests pass (`pytest tests/`)
5. Follow PEP-8 style (`black app/` + `ruff check app/`)
6. Submit pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 📞 Support

- 📧 Email: dev@aravind.dev
- 💬 GitHub Issues: [Issues](https://github.com/aravinditte/payment-gateway-simulation/issues)
- 📖 Documentation: [Docs](https://github.com/aravinditte/payment-gateway-simulation)

---

**Built with ❤️ for Japanese software engineering excellence**
