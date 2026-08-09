from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enums import TransactionType
from app.models.market_price import MarketPrice
from app.models.transaction import Transaction


def create_authenticated_user(
    client: TestClient,
    email: str,
):
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "name": "Performance API User",
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
            "symbol": "INFY",
            "name": "Infosys",
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


def test_get_portfolio_performance(
    client: TestClient,
    db_session: Session,
):
    headers = create_authenticated_user(
        client,
        "performance_api@example.com",
    )

    asset_id = create_asset(
        client,
        headers,
    )

    user_id = get_user_id(
        client,
        headers,
    )

    transaction = Transaction(
        user_id=user_id,
        asset_id=asset_id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
        transaction_date="2026-08-09",
    )

    db_session.add(transaction)
    db_session.commit()

    market_price = MarketPrice(
        asset_id=asset_id,
        price=Decimal("60"),
        source="test",
        price_time="2026-08-09T10:30:00+00:00",
    )

    db_session.add(market_price)
    db_session.commit()

    response = client.get(
        "/portfolio/performance",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_invested"] == "5020.00"
    assert data["total_market_value"] == "6000.000000000000"
    assert data["total_realized_profit_loss"] == "0"
    assert data["total_unrealized_profit_loss"] == "980.000000000000"
    assert data["total_profit_loss"] == "980.000000000000"


def test_portfolio_performance_requires_authentication(
    client: TestClient,
):
    response = client.get(
        "/portfolio/performance",
    )

    assert response.status_code == 401


def test_portfolio_performance_is_user_isolated(
    client: TestClient,
    db_session: Session,
):
    user_1_headers = create_authenticated_user(
        client,
        "performance_user1@example.com",
    )

    user_2_headers = create_authenticated_user(
        client,
        "performance_user2@example.com",
    )

    asset_id = create_asset(
        client,
        user_1_headers,
    )

    user_1_id = get_user_id(
        client,
        user_1_headers,
    )

    transaction = Transaction(
        user_id=user_1_id,
        asset_id=asset_id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
        transaction_date="2026-08-09",
    )

    db_session.add(transaction)

    market_price = MarketPrice(
        asset_id=asset_id,
        price=Decimal("60"),
        source="test",
        price_time="2026-08-09T10:30:00+00:00",
    )

    db_session.add(market_price)
    db_session.commit()

    user_1_response = client.get(
        "/portfolio/performance",
        headers=user_1_headers,
    )

    assert user_1_response.status_code == 200

    user_1_data = user_1_response.json()

    assert user_1_data["total_invested"] == "5020.00"
    assert user_1_data["total_market_value"] == "6000.000000000000"

    user_2_response = client.get(
        "/portfolio/performance",
        headers=user_2_headers,
    )

    assert user_2_response.status_code == 200

    user_2_data = user_2_response.json()

    assert user_2_data["total_invested"] == "0"
    assert user_2_data["total_market_value"] == "0"
    assert user_2_data["total_realized_profit_loss"] == "0"
    assert user_2_data["total_unrealized_profit_loss"] == "0"
    assert user_2_data["total_profit_loss"] == "0"
