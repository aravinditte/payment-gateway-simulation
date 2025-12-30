
# Payment Gateway Simulator

A production-grade **Payment Gateway Simulator** built with **FastAPI**, **PostgreSQL**, and **Docker**, designed to demonstrate real-world backend engineering concepts used in modern payment systems such as Stripe, Adyen, or Razorpay.

This project is specifically built to showcase skills relevant for **backend / platform engineering roles**, including opportunities in **Japan-based tech companies**.

---

## ✨ Key Features

- Merchant onboarding with secure API key generation
- API-key–based authentication (hashed, never stored in plaintext)
- Idempotent payment creation (duplicate-safe requests)
- Payment lifecycle management (create, capture, refund)
- Webhook system with signature verification & retries
- Async PostgreSQL access using SQLAlchemy
- Background workers for webhook dispatch & retries
- Rate limiting & structured logging
- Dockerized local development environment
- Clean layered architecture (API, services, repositories, domain)

---

## 🏗️ Tech Stack

| Layer | Technology |
|-----|-----------|
| API | FastAPI |
| Language | Python 3.11 |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy (Async) |
| Web Server | Uvicorn |
| Auth | API Key (hashed) |
| Infra | Docker & Docker Compose |
| Testing | Pytest |
| Docs | OpenAPI / Swagger |

---

## 📁 Project Structure

```
app/
├── api/              # HTTP layer (FastAPI routers & deps)
├── core/             # Config, security, logging, rate limiting
├── db/               # Database engine, models, session
├── domain/           # Core business models & enums
├── repositories/     # Database access layer
├── services/         # Business logic (payments, refunds, webhooks)
├── schemas/          # Pydantic request/response models
├── utils/            # Helpers (idempotency, signatures, time)
├── workers/          # Background workers
└── main.py           # Application entrypoint
```

---

## 🔐 Authentication

Each merchant is issued a **secret API key**.

Clients authenticate by sending:

```
X-API-Key: sk_test_********
```

- API keys are **hashed before storage**
- Plaintext key is shown **only once**
- Stateless authentication

---

## 🔁 Idempotency

Payment creation **requires** an idempotency key.

```
Idempotency-Key: payment-001
```

- Same key + same request → same payment
- Prevents duplicate charges on retries
- Industry-standard payment safety mechanism

---

## 🚀 Getting Started (Local)

### Prerequisites

- Docker
- Docker Compose

### Run the system

```bash
docker compose up --build
```

Services:
- API → http://localhost:8000
- Docs → http://localhost:8000/docs
- Health → http://localhost:8000/health

---

## 🧪 Create a Merchant (One-Time Setup)

```bash
docker exec -it payment-api python
```

```python
import asyncio
from app.db.session import init_db, get_db_session
from app.services.merchant_service import MerchantService

async def seed():
    await init_db()
    async for db in get_db_session():
        merchant, api_key = await MerchantService.create_merchant(
            db=db,
            name="Demo Merchant",
            email="demo@merchant.com",
            webhook_url=None,
        )
        print("API KEY:", api_key)

asyncio.run(seed())
```

Save the printed API key.

---

## 💳 Create a Payment

```bash
curl -X POST http://localhost:8000/api/v1/payments   -H "Content-Type: application/json"   -H "X-API-Key: sk_test_XXXX"   -H "Idempotency-Key: payment-001"   -d '{
    "amount": 500,
    "currency": "JPY"
  }'
```

---

## 🔔 Webhooks

- Webhook events are signed using HMAC
- Automatic retries with exponential backoff
- Delivery status tracked in database

---

## 🧪 Testing

```bash
pytest
```

Includes:
- Unit tests (services & utilities)
- Integration tests (payment flows & webhooks)

---

## 🧠 Design Principles

- Clear separation of concerns
- Service & repository pattern
- Async-first architecture
- Explicit lifecycle management
- Production-like error handling

---

## 🎯 Why This Project

This simulator demonstrates:

- Real payment gateway behavior
- Production-level backend architecture
- Security-conscious design
- Debugging and lifecycle awareness

It is suitable for:
- Backend engineer interviews
- System design discussions
- Portfolio & GitHub showcase

---

## 📄 License

MIT License
