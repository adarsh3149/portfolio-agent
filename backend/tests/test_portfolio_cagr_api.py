from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.portfolio_snapshot import PortfolioSnapshot


def create_authenticated_user(
    client: TestClient,
    email: str,
):
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "name": "Portfolio CAGR User",
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


def test_get_portfolio_cagr(
    client: TestClient,
    db_session: Session,
):
    headers = create_authenticated_user(
        client,
        "cagr_api@example.com",
    )

    user_id = get_user_id(
        client,
        headers,
    )

    create_snapshot(
        db_session,
        user_id,
        date(2024, 8, 10),
        Decimal("100000.00"),
    )

    create_snapshot(
        db_session,
        user_id,
        date(2026, 8, 10),
        Decimal("121000.00"),
    )

    response = client.get(
        "/portfolio/cagr",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["cagr"] == "0.100000000000000000000000000"


def test_portfolio_cagr_requires_authentication(
    client: TestClient,
):
    response = client.get(
        "/portfolio/cagr",
    )

    assert response.status_code == 401


def test_portfolio_cagr_is_user_isolated(
    client: TestClient,
    db_session: Session,
):
    user_1_headers = create_authenticated_user(
        client,
        "cagr_user1@example.com",
    )

    user_2_headers = create_authenticated_user(
        client,
        "cagr_user2@example.com",
    )

    user_1_id = get_user_id(
        client,
        user_1_headers,
    )

    user_2_id = get_user_id(
        client,
        user_2_headers,
    )

    create_snapshot(
        db_session,
        user_1_id,
        date(2024, 8, 10),
        Decimal("100000.00"),
    )

    create_snapshot(
        db_session,
        user_1_id,
        date(2026, 8, 10),
        Decimal("121000.00"),
    )

    create_snapshot(
        db_session,
        user_2_id,
        date(2024, 8, 10),
        Decimal("500000.00"),
    )

    create_snapshot(
        db_session,
        user_2_id,
        date(2026, 8, 10),
        Decimal("605000.00"),
    )

    user_1_response = client.get(
        "/portfolio/cagr",
        headers=user_1_headers,
    )

    assert user_1_response.status_code == 200
    assert (
        user_1_response.json()["cagr"]
        == "0.100000000000000000000000000"
    )

    user_2_response = client.get(
        "/portfolio/cagr",
        headers=user_2_headers,
    )

    assert user_2_response.status_code == 200
    assert (
        user_2_response.json()["cagr"]
        == "0.100000000000000000000000000"
    )


def test_portfolio_cagr_with_date_range(
    client: TestClient,
    db_session: Session,
):
    headers = create_authenticated_user(
        client,
        "cagr_date_range@example.com",
    )

    user_id = get_user_id(
        client,
        headers,
    )

    create_snapshot(
        db_session,
        user_id,
        date(2024, 8, 10),
        Decimal("100000.00"),
    )

    create_snapshot(
        db_session,
        user_id,
        date(2025, 8, 10),
        Decimal("110000.00"),
    )

    create_snapshot(
        db_session,
        user_id,
        date(2026, 8, 10),
        Decimal("121000.00"),
    )

    response = client.get(
        "/portfolio/cagr",
        params={
            "start_date": "2024-08-10",
            "end_date": "2026-08-10",
        },
        headers=headers,
    )

    assert response.status_code == 200

    assert (
        response.json()["cagr"]
        == "0.100000000000000000000000000"
    )


def test_portfolio_cagr_requires_two_snapshots(
    client: TestClient,
    db_session: Session,
):
    headers = create_authenticated_user(
        client,
        "cagr_insufficient@example.com",
    )

    user_id = get_user_id(
        client,
        headers,
    )

    create_snapshot(
        db_session,
        user_id,
        date(2026, 8, 10),
        Decimal("100000.00"),
    )

    response = client.get(
        "/portfolio/cagr",
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "At least two portfolio snapshots are required."
    )


def test_portfolio_cagr_with_no_snapshots(
    client: TestClient,
):
    headers = create_authenticated_user(
        client,
        "cagr_empty@example.com",
    )

    response = client.get(
        "/portfolio/cagr",
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "At least two portfolio snapshots are required."
    )


def test_portfolio_cagr_rejects_invalid_date_range(
    client: TestClient,
):
    headers = create_authenticated_user(
        client,
        "cagr_invalid_range@example.com",
    )

    response = client.get(
        "/portfolio/cagr",
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