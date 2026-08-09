from decimal import Decimal

def create_authenticated_user(client):
    email = "transaction_test@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/auth/register",
        json={
            "name": "Transaction Test User",
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

def create_asset(client):

    response = client.post(
        "/assets",
        json={
            "symbol": "TCS",
            "name": "Tata Consultancy Services",
            "asset_type": "STOCK",
            "exchange": "NSE",
            "currency": "INR",
            "isin": "INE467B01029",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]

def test_create_transaction(client):

    headers = create_authenticated_user(client)

    asset_id = create_asset(client)

    response = client.post(
        "/transactions",
        headers=headers,
        json={
            "asset_id": asset_id,
            "transaction_type": "BUY",
            "quantity": "100",
            "price": "50",
            "charges": "20.00",
            "transaction_date": "2026-08-09",
            "notes": "Integration test purchase",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["asset_id"] == asset_id
    assert data["transaction_type"] == "BUY"

    assert Decimal(data["quantity"]) == Decimal("100")
    assert Decimal(data["price"]) == Decimal("50")
    assert Decimal(data["amount"]) == Decimal("5000")
    assert Decimal(data["charges"]) == Decimal("20")

    assert data["notes"] == "Integration test purchase"

def test_create_transaction_without_authentication(client):

    asset_id = create_asset(client)

    response = client.post(
        "/transactions",
        json={
            "asset_id": asset_id,
            "transaction_type": "BUY",
            "quantity": "10",
            "price": "100",
            "charges": "0.00",
            "transaction_date": "2026-08-09",
        },
    )

    assert response.status_code == 401

def test_create_transaction_with_unknown_asset(client):

    headers = create_authenticated_user(client)

    response = client.post(
        "/transactions",
        headers=headers,
        json={
            "asset_id": 999999,
            "transaction_type": "BUY",
            "quantity": "10",
            "price": "100",
            "charges": "0.00",
            "transaction_date": "2026-08-09",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Asset not found"

def test_get_holdings_after_transaction(client):

    headers = create_authenticated_user(client)

    asset_id = create_asset(client)

    transaction_response = client.post(
        "/transactions",
        headers=headers,
        json={
            "asset_id": asset_id,
            "transaction_type": "BUY",
            "quantity": "100",
            "price": "50",
            "charges": "20.00",
            "transaction_date": "2026-08-09",
        },
    )

    assert transaction_response.status_code == 201

    response = client.get(
        "/portfolio/holdings",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    holding = data[0]

    assert holding["asset_id"] == asset_id

    assert Decimal(holding["units"]) == Decimal("100")
    assert Decimal(holding["invested_amount"]) == Decimal("5020")
    assert Decimal(holding["average_cost"]) == Decimal("50.2")

def test_get_portfolio_summary(client):

    headers = create_authenticated_user(client)

    asset_id = create_asset(client)

    response = client.post(
        "/transactions",
        headers=headers,
        json={
            "asset_id": asset_id,
            "transaction_type": "BUY",
            "quantity": "100",
            "price": "50",
            "charges": "20.00",
            "transaction_date": "2026-08-09",
        },
    )

    assert response.status_code == 201

    response = client.get(
        "/portfolio/summary",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_holdings"] == 1
    assert data["total_transactions"] == 1
    assert data["total_invested"] == "5020.00"