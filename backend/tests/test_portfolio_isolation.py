from decimal import Decimal


def create_user(client, email, name):
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "name": name,
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


def create_asset(client):

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


def test_users_have_isolated_portfolios(client):

    user_a_headers = create_user(
        client,
        "user_a@example.com",
        "User A",
    )

    user_b_headers = create_user(
        client,
        "user_b@example.com",
        "User B",
    )

    asset_id = create_asset(client)

    # User A makes an investment
    transaction_response = client.post(
        "/transactions",
        headers=user_a_headers,
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

    # User A should see the investment
    user_a_holdings = client.get(
        "/portfolio/holdings",
        headers=user_a_headers,
    )

    assert user_a_holdings.status_code == 200

    holdings_a = user_a_holdings.json()

    assert len(holdings_a) == 1
    assert holdings_a[0]["asset_id"] == asset_id
    assert Decimal(
        holdings_a[0]["units"]
    ) == Decimal("100")

    # User B should see NO holdings
    user_b_holdings = client.get(
        "/portfolio/holdings",
        headers=user_b_headers,
    )

    assert user_b_holdings.status_code == 200

    holdings_b = user_b_holdings.json()

    assert holdings_b == []

    # User A summary
    user_a_summary = client.get(
        "/portfolio/summary",
        headers=user_a_headers,
    )

    assert user_a_summary.status_code == 200

    summary_a = user_a_summary.json()

    assert summary_a["total_holdings"] == 1
    assert summary_a["total_transactions"] == 1
    assert Decimal(
        summary_a["total_invested"]
    ) == Decimal("5020")

    # User B summary
    user_b_summary = client.get(
        "/portfolio/summary",
        headers=user_b_headers,
    )

    assert user_b_summary.status_code == 200

    summary_b = user_b_summary.json()

    assert summary_b["total_holdings"] == 0
    assert summary_b["total_transactions"] == 0
    assert Decimal(
        summary_b["total_invested"]
    ) == Decimal("0")