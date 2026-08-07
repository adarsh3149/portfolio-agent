# 📈 Portfolio Agent

A modern portfolio management platform built with **FastAPI**, **PostgreSQL**, and **Docker**.

Portfolio Agent is designed to help investors manage and analyze their investments across multiple asset classes including mutual funds, stocks, ETFs, gold, fixed deposits, and other financial instruments.

The project is being developed incrementally while following production-grade backend engineering practices and clean architecture principles.

> **Current Version:** v0.2.0
> **Status:** 🚧 Active Development

---

# 🎯 Vision

The goal of Portfolio Agent is to build a scalable and production-ready investment platform that enables users to:

* Track investments across multiple asset classes
* Record every investment transaction
* Monitor portfolio performance
* Calculate realized and unrealized profit/loss
* Analyze portfolio allocation
* Generate investment reports
* Receive AI-powered investment insights

This project is also intended to demonstrate backend engineering best practices, making it suitable as a portfolio project for software engineering interviews.

---

# ✨ Features

## ✅ Sprint 1 - Infrastructure & Authentication

### Infrastructure

* FastAPI
* PostgreSQL
* Docker & Docker Compose
* SQLAlchemy 2.0
* Alembic Database Migrations

### Authentication & Authorization

* User Registration
* User Login
* JWT Authentication
* OAuth2 Authentication
* Password Hashing using Argon2
* Protected API Endpoints

### Backend Architecture

* Layered Architecture
* Repository Pattern
* Service Layer
* Dependency Injection
* Environment-based Configuration
* Pydantic Validation

### Testing

* Unit Tests for Security Module
* JWT Testing
* Password Hashing Tests

---

# 🏗️ System Architecture

```text
                Client
                   │
                   ▼
             FastAPI Router
                   │
                   ▼
            Service Layer
                   │
                   ▼
          Repository Layer
                   │
                   ▼
            SQLAlchemy ORM
                   │
                   ▼
             PostgreSQL
```

---

# 📁 Project Structure

```text
portfolio-agent/

├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── dependencies/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
│
├── docs/
├── frontend/
└── docker-compose.yml
```

---

# 🛠️ Tech Stack

| Layer            | Technology     |
| ---------------- | -------------- |
| Backend          | FastAPI        |
| Database         | PostgreSQL     |
| ORM              | SQLAlchemy 2.0 |
| Authentication   | JWT + OAuth2   |
| Password Hashing | Argon2         |
| Migrations       | Alembic        |
| Containerization | Docker         |
| Testing          | Pytest         |
| Validation       | Pydantic v2    |

---

# 🚀 Getting Started

## Clone the Repository

```bash
git clone https://github.com/<your-username>/portfolio-agent.git

cd portfolio-agent
```

## Start the Application

```bash
docker compose up --build
```

The application will be available at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

# 🔐 Authentication

The application uses JWT-based authentication.

Authentication flow:

1. Register a new user
2. Login with email and password
3. Receive a JWT access token
4. Use the token to access protected endpoints

---

# 🧪 Running Tests

Run the unit tests using:

```bash
docker compose exec backend pytest
```

---

# 🗺️ Project Roadmap

## ✅ Sprint 1

* Project Setup
* Docker
* PostgreSQL
* SQLAlchemy
* Alembic
* User Registration
* User Login
* JWT Authentication
* OAuth2 Authorization
* Security Testing

---

## 🚧 Sprint 2

* Asset Management
* Transaction Management
* Holdings Calculation
* Portfolio Summary

---

## 📅 Sprint 3

* Dashboard APIs
* Portfolio Analytics
* Asset Allocation
* Profit & Loss Reports

---

## 🔮 Sprint 4

* Live Market Data Integration
* XIRR Calculations
* Goal Planning
* Portfolio Rebalancing
* AI Portfolio Advisor

---

# 🌿 Git Workflow

This project follows a feature-branch development workflow.

* `main` → Stable production-ready code
* `feature/*` → Feature development
* Semantic Versioning (`v0.x.x`)
* Conventional Commit Messages

---

# 🏛️ Engineering Principles

The project is being developed following modern software engineering practices:

* Clean Architecture
* SOLID Principles
* Repository Pattern
* Service Layer
* Dependency Injection
* Incremental Development
* Security First Approach

---

# 📄 License

This project is currently under active development.

A license will be added before the first public release.
