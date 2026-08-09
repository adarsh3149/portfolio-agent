def test_create_asset(client):

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

    data = response.json()

    assert data["symbol"] == "TCS"
    assert data["name"] == "Tata Consultancy Services"
    assert data["asset_type"] == "STOCK"
    assert data["exchange"] == "NSE"
    assert data["currency"] == "INR"

def test_get_assets(client):

    client.post(
        "/assets",
        json={
            "symbol": "RELIANCE",
            "name": "Reliance Industries",
            "asset_type": "STOCK",
            "exchange": "NSE",
            "currency": "INR",
            "isin": "INE002A01018",
        },
    )

    response = client.get("/assets")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1

    symbols = [
        asset["symbol"]
        for asset in data
    ]

    assert "RELIANCE" in symbols

def test_get_asset_by_id(client):

    create_response = client.post(
        "/assets",
        json={
            "symbol": "HDFCBANK",
            "name": "HDFC Bank",
            "asset_type": "STOCK",
            "exchange": "NSE",
            "currency": "INR",
            "isin": "INE040A01034",
        },
    )

    assert create_response.status_code == 201

    asset_id = create_response.json()["id"]

    response = client.get(
        f"/assets/{asset_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == asset_id
    assert data["symbol"] == "HDFCBANK"

def test_get_missing_asset(client):

    response = client.get("/assets/999999")

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Asset with ID '999999' not found."
    )

def test_duplicate_asset(client):

    payload = {
        "symbol": "INFY",
        "name": "Infosys",
        "asset_type": "STOCK",
        "exchange": "NSE",
        "currency": "INR",
    }

    first_response = client.post(
        "/assets",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/assets",
        json=payload,
    )

    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "Asset with symbol 'INFY' already exists."
    )