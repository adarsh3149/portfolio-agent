from decimal import Decimal

from fastapi.testclient import TestClient

from app.models.market_price import MarketPrice


def create_authenticated_user(client: TestClient):

    email = "market_data_test@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "name": "Market Data Test User",
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
        "Authorization": f"Bearer {token}"
    }


def create_asset(client: TestClient):

    response = client.post(
        "/assets",
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


def test_fetch_asset_price(client: TestClient):

    headers = create_authenticated_user(client)

    asset_id = create_asset(client)

    response = client.post(
        f"/market-data/assets/{asset_id}/price",
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["asset_id"] == asset_id
    assert data["price"] == "1450.2500"
    assert data["source"] == "provider"


def test_fetch_price_for_unknown_asset(client: TestClient):

    headers = create_authenticated_user(client)

    response = client.post(
        "/market-data/assets/999999/price",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Asset with ID '999999' not found."
    )


def test_fetch_price_without_authentication(
    client: TestClient,
):

    asset_id = create_asset(client)

    response = client.post(
        f"/market-data/assets/{asset_id}/price",
    )

    assert response.status_code in (401, 403)
