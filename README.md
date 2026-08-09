# 📊 Portfolio Agent

A backend-first portfolio management platform designed to track investments, transactions, holdings, and portfolio analytics.

The project is being built incrementally with a focus on clean architecture, financial precision, automated testing, and future extensibility toward live market data and AI-powered portfolio insights.

---

## 🚀 Current Status

### Sprint 2 — Portfolio Management

**Status: ✅ Complete**

```text
Authentication              ✅
Asset Management            ✅
Transaction Management      ✅
Holdings Engine             ✅
Portfolio Summary           ✅
API Integration Tests       ✅
User Portfolio Isolation    ✅

Test Suite: 19/19 PASSED
```

---

# 🏗️ Architecture

The application follows a layered architecture:

```text
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │       API Layer     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Service Layer     │
                    │ Business Logic      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Repository Layer    │
                    │ Database Access     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    PostgreSQL       │
                    └─────────────────────┘
```

### Project Structure

```text
portfolio-agent/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── asset.py
│   │   │   ├── portfolio.py
│   │   │   └── transaction.py
│   │   │
│   │   ├── core/
│   │   │   ├── security.py
│   │   │   └── database_types.py
│   │   │
│   │   ├── database/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   │
│   │   ├── dependencies/
│   │   │   ├── auth.py
│   │   │   ├── database.py
│   │   │   └── services.py
│   │   │
│   │   ├── enums/
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── asset.py
│   │   │   └── transaction.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── asset_repository.py
│   │   │   └── transaction_repository.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── asset.py
│   │   │   ├── holding.py
│   │   │   ├── portfolio.py
│   │   │   └── transaction.py
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── asset_service.py
│   │   │   ├── holding_accumulator.py
│   │   │   ├── holding_service.py
│   │   │   ├── portfolio_service.py
│   │   │   └── transaction_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_asset_api.py
│   │   ├── test_auth.py
│   │   ├── test_holding_service.py
│   │   ├── test_portfolio_isolation.py
│   │   ├── test_portfolio_service.py
│   │   ├── test_security.py
│   │   └── test_transaction_api.py
│   │
│   ├── .env
│   └── ...
│
├── docker-compose.yml
└── README.md
```

---

# 🛠️ Tech Stack

| Technology     | Purpose                     |
| -------------- | --------------------------- |
| Python         | Backend language            |
| FastAPI        | REST API framework          |
| PostgreSQL     | Primary database            |
| SQLAlchemy     | ORM                         |
| Alembic        | Database migrations         |
| Pydantic       | Request/response validation |
| JWT            | Authentication              |
| Pytest         | Automated testing           |
| Docker Compose | Local development           |

---

# 🔐 Authentication

The API uses JWT-based authentication.

### Register

```http
POST /auth/register
```

Example:

```json
{
  "name": "Adarsh",
  "email": "adarsh@example.com",
  "password": "your-password"
}
```

### Login

```http
POST /auth/login
```

The login endpoint uses OAuth2 password form authentication.

Example form data:

```text
username=adarsh@example.com
password=your-password
```

Response:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

Protected endpoints require:

```http
Authorization: Bearer <JWT_TOKEN>
```

---

# 📈 Asset Management

Assets represent investment instruments such as stocks, mutual funds, ETFs, gold, and other supported asset types.

### Create Asset

```http
POST /assets
```

Example:

```json
{
  "symbol": "INFY",
  "name": "Infosys",
  "asset_type": "STOCK",
  "exchange": "NSE",
  "currency": "INR",
  "isin": "INE009A01021"
}
```

### Get All Assets

```http
GET /assets
```

### Get Asset

```http
GET /assets/{asset_id}
```

### Asset Validation

The API prevents duplicate assets and returns:

```text
409 Conflict
```

when an existing asset conflicts with the requested symbol.

---

# 💰 Transactions

Transactions represent actual investment activity.

Currently supported transaction types include:

```text
BUY
SELL
```

### Create Transaction

```http
POST /transactions
```

Example:

```json
{
  "asset_id": 2,
  "transaction_type": "BUY",
  "quantity": "100",
  "price": "50",
  "charges": "20.00",
  "transaction_date": "2026-08-09",
  "notes": "First investment"
}
```

The transaction amount is calculated from:

```text
quantity × price
```

For example:

```text
100 × ₹50
= ₹5,000
```

With ₹20 charges:

```text
Invested Amount
= ₹5,000 + ₹20
= ₹5,020
```

Financial values use `Decimal` rather than floating-point arithmetic.

---

# 📊 Holdings Engine

The Holdings Engine derives the current holdings from the user's transaction history.

For BUY transactions:

```text
Units
    +
Invested Amount
    +
Charges
```

For SELL transactions:

```text
Units
    -

Average Cost × Sold Units
    ↓
Invested Amount
```

The engine also prevents selling more units than currently owned.

Example:

```text
Owned: 100 units
Sell: 120 units

→ ValueError
→ Cannot sell more units than owned.
```

---

# 📋 Portfolio APIs

## Get Holdings

```http
GET /portfolio/holdings
```

Example response:

```json
[
  {
    "asset_id": 2,
    "symbol": "INFY",
    "asset_name": "Infosys",
    "units": "100.00000000",
    "average_cost": "50.20",
    "invested_amount": "5020.00"
  }
]
```

---

## Portfolio Summary

```http
GET /portfolio/summary
```

Example:

```json
{
  "total_holdings": 1,
  "total_transactions": 2,
  "total_invested": "8030.00"
}
```

The summary is calculated specifically for the authenticated user.

For a new user with no transactions:

```json
{
  "total_holdings": 0,
  "total_transactions": 0,
  "total_invested": "0.00"
}
```

---

# 🔒 User Data Isolation

Portfolio information is isolated by user.

For example:

```text
User A
 └── BUY 100 INFY
       │
       └── Portfolio A
             └── 100 INFY


User B
 └── No transactions
       │
       └── Portfolio B
             └── Empty
```

User B cannot see User A's holdings or transactions.

This behavior is covered by an automated integration test.

---

# 🧪 Testing

The project uses Pytest for automated testing.

Run the complete test suite:

```bash
docker compose exec backend pytest
```

Current result:

```text
19 passed
```

### Test Coverage Includes

```text
Authentication
    ✅ JWT creation and decoding

Asset APIs
    ✅ Create asset
    ✅ Get assets
    ✅ Get asset by ID
    ✅ Missing asset handling
    ✅ Duplicate asset handling

Transaction APIs
    ✅ Create transaction
    ✅ Unauthenticated transaction rejection
    ✅ Unknown asset handling

Holdings
    ✅ BUY processing
    ✅ SELL processing
    ✅ Overselling protection
    ✅ Holdings API

Portfolio
    ✅ Portfolio summary
    ✅ Empty portfolio
    ✅ Multi-user isolation
```

---

# 🗄️ Database Migrations

Alembic is used for database schema management.

Check the current migration:

```bash
docker compose exec backend alembic current
```

View migration history:

```bash
docker compose exec backend alembic history
```

Create a migration:

```bash
docker compose exec backend alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
docker compose exec backend alembic upgrade head
```

Rollback one migration:

```bash
docker compose exec backend alembic downgrade -1
```

---

# 🐳 Running Locally

Start the application:

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

View backend logs:

```bash
docker compose logs backend
```

Open the FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

Open ReDoc:

```text
http://localhost:8000/redoc
```

Health check:

```http
GET /health
```

Expected:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

# 🧩 Development Workflow

Typical development workflow:

```text
1. Modify model/schema/service
          ↓
2. Create Alembic migration
          ↓
3. Apply migration
          ↓
4. Implement/update API
          ↓
5. Add tests
          ↓
6. Run pytest
          ↓
7. Verify Swagger
          ↓
8. Commit changes
```

Run all tests before committing:

```bash
docker compose exec backend pytest
```

---

# 🗺️ Roadmap

## Sprint 1 — Foundation

```text
✅ Project setup
✅ Docker environment
✅ PostgreSQL
✅ Authentication
✅ JWT
✅ SQLAlchemy
✅ Alembic
```

## Sprint 2 — Portfolio Management

```text
✅ Asset management
✅ Transaction management
✅ Holdings engine
✅ BUY/SELL processing
✅ Portfolio holdings API
✅ Portfolio summary API
✅ Integration testing
✅ User isolation
```

## Sprint 3 — Market Data & Analytics

Planned:

```text
⬜ Live market prices
⬜ Current portfolio value
⬜ Unrealized P/L
⬜ Realized P/L
⬜ Asset allocation
⬜ Historical portfolio value
⬜ SIP analytics
⬜ XIRR
```

## Future — AI Portfolio Intelligence

Planned:

```text
⬜ Portfolio insights
⬜ Investment summaries
⬜ Risk analysis
⬜ Anomaly detection
⬜ Personalized portfolio explanations
⬜ AI-powered portfolio assistant
```

---

# 🎯 Project Vision

Portfolio Agent is being built as more than a simple transaction tracker.

The long-term goal is to evolve from:

```text
Transaction Tracker
        ↓
Portfolio Manager
        ↓
Portfolio Analytics Platform
        ↓
AI-Powered Investment Assistant
```

The architecture is intentionally being built incrementally so that future market-data, analytics, and AI capabilities can be added without rewriting the core portfolio management system.

---

# 📌 Current Milestone

```text
Portfolio Agent
────────────────────────────────

Sprint 2 Complete

19 / 19 Tests Passed

Authentication       ✅
Assets               ✅
Transactions         ✅
Holdings             ✅
Portfolio Summary    ✅
API Integration      ✅
User Isolation       ✅

Next:
Market Data & Portfolio Analytics
```

---

## License

This project is currently being developed as a personal portfolio-management project.
