from decimal import Decimal

from fastapi.testclient import TestClient

from app.models.asset import Asset
from app.models.market_price import MarketPrice
from app.models.transaction import Transaction
from app.enums import TransactionType


def create_authenticated_user(
    client: TestClient,
    email: str,
):
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "name": "Valuation API User",
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

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
    headers,
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
            "isin": "INE009A01021",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_get_portfolio_valuation(
    client: TestClient,
    db_session,
):
    headers = create_authenticated_user(
        client,
        "valuation_api@example.com",
    )

    asset_id = create_asset(
        client,
        headers,
    )

    me_response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert me_response.status_code == 200

    user_id = me_response.json()["id"]

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
        "/portfolio/valuation",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    valuation = data[0]

    assert valuation["asset_id"] == asset_id
    assert valuation["symbol"] == "INFY"
    assert valuation["units"] == "100.00000000"
    assert valuation["invested_amount"] == "5020.00"
    assert valuation["current_price"] == "60.0000"
    assert valuation["market_value"] == "6000.000000000000"
    assert valuation["unrealized_profit_loss"] == "980.000000000000"


def test_portfolio_valuation_requires_authentication(
    client: TestClient,
):

    response = client.get(
        "/portfolio/valuation",
    )

    assert response.status_code in (401, 403)


def test_portfolio_valuation_is_user_isolated(
    client: TestClient,
    db_session,
):
    user1_headers = create_authenticated_user(
        client,
        "valuation_user1@example.com",
    )

    user2_headers = create_authenticated_user(
        client,
        "valuation_user2@example.com",
    )

    asset_id = create_asset(
        client,
        user1_headers,
    )

    user1_response = client.get(
        "/auth/me",
        headers=user1_headers,
    )

    user1_id = user1_response.json()["id"]

    transaction = Transaction(
        user_id=user1_id,
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

    db_session.add(
        MarketPrice(
            asset_id=asset_id,
            price=Decimal("60"),
            source="test",
            price_time="2026-08-09T10:30:00+00:00",
        )
    )

    db_session.commit()

    response = client.get(
        "/portfolio/valuation",
        headers=user2_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data == []
