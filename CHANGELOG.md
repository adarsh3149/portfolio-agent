# Changelog

All notable changes to **Portfolio Agent** are documented in this file.

The project follows a version-based release approach as development progresses.

---

## [0.3.0] — 2026-08-09

### 🚀 Sprint 2 — Portfolio Management

Completed the core portfolio management layer, including assets, transactions, holdings, portfolio summaries, and API integration testing.

### Added

#### 🔐 Authentication

* JWT-based authentication.
* User registration.
* User login using OAuth2 password form.
* Protected portfolio and transaction endpoints.
* Current-user authentication dependency.

#### 📈 Asset Management

* Added `Asset` model.
* Added support for asset types:

  * Stock
  * Mutual Fund
  * ETF
  * Gold
  * Fixed Deposit
* Added exchange support.
* Added currency support.
* Added ISIN support.
* Added asset repository.
* Added asset service.
* Added Asset APIs:

  * `POST /assets`
  * `GET /assets`
  * `GET /assets/{asset_id}`
* Added duplicate asset protection.
* Added asset lookup and validation.

#### 💰 Transaction Management

* Added `Transaction` model.
* Added BUY and SELL transaction types.
* Added transaction repository.
* Added transaction service.
* Added transaction creation API:

  * `POST /transactions`
* Added transaction amount calculation.
* Added transaction charges support.
* Added transaction date and notes.
* Added `Decimal`-based financial values for improved precision.
* Added validation for unknown assets.

#### 📊 Holdings Engine

* Added `HoldingAccumulator`.
* Added `HoldingService`.
* Added BUY transaction processing.
* Added SELL transaction processing.
* Added average-cost calculation.
* Added invested-amount calculation.
* Added protection against selling more units than owned.
* Added holdings schema.
* Added holdings API:

  * `GET /portfolio/holdings`

#### 📋 Portfolio Summary

* Added `PortfolioSummary` schema.
* Added `PortfolioService`.
* Added transaction counting.
* Added total holdings calculation.
* Added total invested amount calculation.
* Added portfolio summary API:

  * `GET /portfolio/summary`
* Added support for empty portfolios.

#### 🧪 Testing

Added comprehensive unit and API integration tests.

Current test suite:

```text
19 / 19 PASSED
```

Coverage includes:

* Authentication
* JWT creation and decoding
* Asset creation
* Asset retrieval
* Duplicate asset handling
* Missing asset handling
* Transaction creation
* Unauthenticated transaction rejection
* Unknown asset handling
* BUY processing
* SELL processing
* Overselling protection
* Holdings API
* Portfolio Summary API
* Empty portfolio handling
* Test database isolation
* Multi-user portfolio isolation

#### 🗄️ Database

* Added PostgreSQL-backed persistence.
* Added SQLAlchemy models for users, assets, and transactions.
* Added Alembic migrations for:

  * Users
  * Assets
  * Transactions
* Added dedicated test database configuration.
* Added automated database setup for integration tests.

#### 🐳 Development

* Continued Docker Compose-based development environment.
* Added API integration testing through FastAPI `TestClient`.
* Added test database dependency overrides.
* Added test database isolation between test cases.
* Updated project documentation.

---

## [0.2.0] — Previous Release

### Added

* Initial authentication foundation.
* User model.
* Password hashing.
* JWT security utilities.
* FastAPI application foundation.
* PostgreSQL integration.
* SQLAlchemy setup.
* Alembic migration setup.
* Docker-based development environment.

---

## [Unreleased]

### Planned

#### 📈 Market Data & Analytics

* Live market prices.
* Current portfolio valuation.
* Unrealized profit/loss.
* Realized profit/loss.
* Asset allocation.
* Historical portfolio performance.
* SIP analytics.
* XIRR calculations.

#### 🤖 AI Portfolio Intelligence

* AI-generated portfolio insights.
* Investment summaries.
* Risk analysis.
* Portfolio anomaly detection.
* Personalized portfolio explanations.
* AI-powered portfolio assistant.

---

## Versioning

Portfolio Agent uses semantic versioning:

```text
MAJOR.MINOR.PATCH
```

Example:

```text
v0.3.0
```

where:

* `MAJOR` represents breaking changes.
* `MINOR` represents new functionality.
* `PATCH` represents fixes and small improvements.
