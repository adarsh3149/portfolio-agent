from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import TransactionType
from app.models.portfolio_snapshot import PortfolioSnapshot
from app.models.transaction import Transaction


def create_authenticated_user(
    client: TestClient,
    email: str,
):
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "name": "Portfolio XIRR User",
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def create_asset(
    client: TestClient,
    headers: dict,
):
    response = client.post(
        "/assets",
        headers=headers,
        json={
            "symbol": "XIRR",
            "name": "XIRR Test Asset",
            "asset_type": "STOCK",
            "exchange": "NSE",
            "currency": "INR",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def get_user_id(
    client: TestClient,
    headers: dict,
):
    response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert response.status_code == 200

    return response.json()["id"]


def create_transaction(
    db_session: Session,
    user_id: int,
    asset_id: int,
    transaction_date: date,
    amount: Decimal,
    charges: Decimal = Decimal("0.00"),
    transaction_type: TransactionType = TransactionType.BUY,
):
    transaction = Transaction(
        user_id=user_id,
        asset_id=asset_id,
        transaction_type=transaction_type,
        quantity=Decimal("1"),
        price=amount,
        amount=amount,
        charges=charges,
        transaction_date=transaction_date,
    )

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    return transaction


def create_snapshot(
    db_session: Session,
    user_id: int,
    snapshot_date: date,
    market_value: Decimal,
):
    snapshot = PortfolioSnapshot(
        user_id=user_id,
        snapshot_date=snapshot_date,
        total_invested=Decimal("100000.00"),
        total_market_value=market_value,
        total_realized_profit_loss=Decimal("0.00"),
        total_unrealized_profit_loss=Decimal("0.00"),
        total_profit_loss=Decimal("0.00"),
    )

    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)

    return snapshot


def test_get_portfolio_xirr(
    client: TestClient,
    db_session: Session,
):
    headers = create_authenticated_user(
        client,
        "xirr_api@example.com",
    )

    user_id = get_user_id(
        client,
        headers,
    )

    asset_id = create_asset(
        client,
        headers,
    )

    create_transaction(
        db_session,
        user_id,
        asset_id,
        date(2025, 8, 10),
        Decimal("100000.00"),
        Decimal("20.00"),
    )

    create_snapshot(
        db_session,
        user_id,
        date(2026, 8, 10),
        Decimal("110000.00"),
    )

    response = client.get(
        "/portfolio/xirr",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert float(data["xirr"]) == pytest.approx(
        0.099780044,
        abs=0.0001,
    )


def test_portfolio_xirr_requires_authentication(
    client: TestClient,
):
    response = client.get(
        "/portfolio/xirr",
    )

    assert response.status_code == 401


def test_portfolio_xirr_is_user_isolated(
    client: TestClient,
    db_session: Session,
):
    user_1_headers = create_authenticated_user(
        client,
        "xirr_user1@example.com",
    )

    user_2_headers = create_authenticated_user(
        client,
        "xirr_user2@example.com",
    )

    user_1_id = get_user_id(
        client,
        user_1_headers,
    )

    user_2_id = get_user_id(
        client,
        user_2_headers,
    )

    asset_id = create_asset(
        client,
        user_1_headers,
    )

    create_transaction(
        db_session,
        user_1_id,
        asset_id,
        date(2025, 8, 10),
        Decimal("100000.00"),
    )

    create_snapshot(
        db_session,
        user_1_id,
        date(2026, 8, 10),
        Decimal("110000.00"),
    )

    create_transaction(
        db_session,
        user_2_id,
        asset_id,
        date(2025, 8, 10),
        Decimal("200000.00"),
    )

    create_snapshot(
        db_session,
        user_2_id,
        date(2026, 8, 10),
        Decimal("220000.00"),
    )

    user_1_response = client.get(
        "/portfolio/xirr",
        headers=user_1_headers,
    )

    assert user_1_response.status_code == 200

    user_2_response = client.get(
        "/portfolio/xirr",
        headers=user_2_headers,
    )

    assert user_2_response.status_code == 200

    assert float(
        user_1_response.json()["xirr"]
    ) == pytest.approx(
        0.10,
        abs=0.0001,
    )

    assert float(
        user_2_response.json()["xirr"]
    ) == pytest.approx(
        0.10,
        abs=0.0001,
    )


def test_portfolio_xirr_with_date_range(
    client: TestClient,
    db_session: Session,
):
    headers = create_authenticated_user(
        client,
        "xirr_date_range@example.com",
    )

    user_id = get_user_id(
        client,
        headers,
    )

    asset_id = create_asset(
        client,
        headers,
    )

    create_transaction(
        db_session,
        user_id,
        asset_id,
        date(2025, 1, 1),
        Decimal("100000.00"),
    )

    create_transaction(
        db_session,
        user_id,
        asset_id,
        date(2026, 1, 1),
        Decimal("10000.00"),
    )

    create_snapshot(
        db_session,
        user_id,
        date(2026, 1, 1),
        Decimal("125000.00"),
    )

    response = client.get(
        "/portfolio/xirr",
        params={
            "start_date": "2025-01-01",
            "end_date": "2026-01-01",
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert "xirr" in response.json()


def test_portfolio_xirr_requires_transactions(
    client: TestClient,
):
    headers = create_authenticated_user(
        client,
        "xirr_no_transactions@example.com",
    )

    response = client.get(
        "/portfolio/xirr",
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "At least one transaction is required."
    )


def test_portfolio_xirr_requires_snapshot(
    client: TestClient,
    db_session: Session,
):
    headers = create_authenticated_user(
        client,
        "xirr_no_snapshot@example.com",
    )

    user_id = get_user_id(
        client,
        headers,
    )

    asset_id = create_asset(
        client,
        headers,
    )

    create_transaction(
        db_session,
        user_id,
        asset_id,
        date(2025, 8, 10),
        Decimal("100000.00"),
    )

    response = client.get(
        "/portfolio/xirr",
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "A portfolio snapshot is required."
    )


def test_portfolio_xirr_rejects_invalid_date_range(
    client: TestClient,
):
    headers = create_authenticated_user(
        client,
        "xirr_invalid_range@example.com",
    )

    response = client.get(
        "/portfolio/xirr",
        params={
            "start_date": "2026-08-10",
            "end_date": "2026-08-01",
        },
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "start_date cannot be greater than end_date"
    )