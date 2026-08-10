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
            "name": "Portfolio History User",
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
    total_invested: Decimal,
    total_market_value: Decimal,
    total_realized_profit_loss: Decimal,
    total_unrealized_profit_loss: Decimal,
    total_profit_loss: Decimal,
):
    snapshot = PortfolioSnapshot(
        user_id=user_id,
        snapshot_date=snapshot_date,
        total_invested=total_invested,
        total_market_value=total_market_value,
        total_realized_profit_loss=(
            total_realized_profit_loss
        ),
        total_unrealized_profit_loss=(
            total_unrealized_profit_loss
        ),
        total_profit_loss=total_profit_loss,
    )

    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)

    return snapshot


def test_get_portfolio_history(
    client: TestClient,
    db_session: Session,
):
    headers = create_authenticated_user(
        client,
        "portfolio_history@example.com",
    )

    user_id = get_user_id(
        client,
        headers,
    )

    create_snapshot(
        db_session=db_session,
        user_id=user_id,
        snapshot_date=date(2026, 8, 8),
        total_invested=Decimal("10000.00"),
        total_market_value=Decimal("11000.00"),
        total_realized_profit_loss=Decimal("200.00"),
        total_unrealized_profit_loss=Decimal("800.00"),
        total_profit_loss=Decimal("1000.00"),
    )

    create_snapshot(
        db_session=db_session,
        user_id=user_id,
        snapshot_date=date(2026, 8, 9),
        total_invested=Decimal("10000.00"),
        total_market_value=Decimal("11500.00"),
        total_realized_profit_loss=Decimal("300.00"),
        total_unrealized_profit_loss=Decimal("1200.00"),
        total_profit_loss=Decimal("1500.00"),
    )

    response = client.get(
        "/portfolio/history",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["snapshot_date"] == "2026-08-08"
    assert data[1]["snapshot_date"] == "2026-08-09"

    assert data[0]["total_invested"] == "10000.00"
    assert data[0]["total_market_value"] == "11000.00"
    assert data[0]["total_realized_profit_loss"] == "200.00"
    assert data[0]["total_unrealized_profit_loss"] == "800.00"
    assert data[0]["total_profit_loss"] == "1000.00"

    assert data[1]["total_invested"] == "10000.00"
    assert data[1]["total_market_value"] == "11500.00"
    assert data[1]["total_realized_profit_loss"] == "300.00"
    assert data[1]["total_unrealized_profit_loss"] == "1200.00"
    assert data[1]["total_profit_loss"] == "1500.00"


def test_portfolio_history_requires_authentication(
    client: TestClient,
):
    response = client.get(
        "/portfolio/history",
    )

    assert response.status_code == 401


def test_portfolio_history_is_user_isolated(
    client: TestClient,
    db_session: Session,
):
    user_1_headers = create_authenticated_user(
        client,
        "history_user1@example.com",
    )

    user_2_headers = create_authenticated_user(
        client,
        "history_user2@example.com",
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
        db_session=db_session,
        user_id=user_1_id,
        snapshot_date=date(2026, 8, 10),
        total_invested=Decimal("10000.00"),
        total_market_value=Decimal("12000.00"),
        total_realized_profit_loss=Decimal("500.00"),
        total_unrealized_profit_loss=Decimal("1500.00"),
        total_profit_loss=Decimal("2000.00"),
    )

    create_snapshot(
        db_session=db_session,
        user_id=user_2_id,
        snapshot_date=date(2026, 8, 10),
        total_invested=Decimal("50000.00"),
        total_market_value=Decimal("55000.00"),
        total_realized_profit_loss=Decimal("2000.00"),
        total_unrealized_profit_loss=Decimal("3000.00"),
        total_profit_loss=Decimal("5000.00"),
    )

    user_1_response = client.get(
        "/portfolio/history",
        headers=user_1_headers,
    )

    assert user_1_response.status_code == 200

    user_1_data = user_1_response.json()

    assert len(user_1_data) == 1
    assert user_1_data[0]["total_invested"] == "10000.00"
    assert user_1_data[0]["total_market_value"] == "12000.00"

    user_2_response = client.get(
        "/portfolio/history",
        headers=user_2_headers,
    )

    assert user_2_response.status_code == 200

    user_2_data = user_2_response.json()

    assert len(user_2_data) == 1
    assert user_2_data[0]["total_invested"] == "50000.00"
    assert user_2_data[0]["total_market_value"] == "55000.00"


def test_empty_portfolio_history_returns_empty_list(
    client: TestClient,
):
    headers = create_authenticated_user(
        client,
        "empty_history@example.com",
    )

    response = client.get(
        "/portfolio/history",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == []
