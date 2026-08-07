# Changelog

All notable changes to this project will be documented in this file.

The project follows a simplified version of the **Keep a Changelog** format and uses **Semantic Versioning (SemVer)**.

---

# [v0.2.0] - Authentication & Authorization Release

**Release Date:** August 2026

## Added

### Infrastructure

* Dockerized backend application
* Docker Compose environment
* PostgreSQL database integration
* SQLAlchemy 2.0 ORM configuration
* Alembic database migrations
* Environment-based configuration using Pydantic Settings

### Backend Architecture

* Clean layered architecture
* Repository Pattern
* Service Layer
* Dependency Injection
* Modular project structure

### Authentication

* User Registration API
* User Login API
* JWT Access Token generation
* JWT Token validation
* OAuth2 Password flow
* Protected API endpoints

### Security

* Password hashing using Argon2
* Duplicate email validation
* Secure JWT authentication
* Protected user endpoint (`GET /auth/me`)

### Testing

* Unit tests for password hashing
* Unit tests for JWT generation and validation

---

## Changed

* Adopted SQLAlchemy 2.0 query style (`select()`)
* Improved project structure for better maintainability
* Refactored authentication into service and repository layers

---

## Fixed

* PostgreSQL database initialization issues
* Password hashing compatibility issues
* JWT decoding and validation improvements
* Docker configuration issues
* Python package import issues during testing

---

## Security

* Passwords are never stored in plain text.
* JWT tokens contain only the minimum required user information.
* Authentication endpoints prevent user enumeration by returning generic login error messages.
* Protected endpoints require valid JWT authentication.

---

# [Unreleased]

## Planned

### Sprint 2

* Asset Management
* Transaction Management
* Portfolio Holdings
* Portfolio Summary APIs

### Sprint 3

* Portfolio Analytics
* Profit & Loss Calculations
* Asset Allocation
* Dashboard APIs

### Sprint 4

* Live Market Data Integration
* XIRR Calculations
* AI Portfolio Advisor
* Goal Planning
