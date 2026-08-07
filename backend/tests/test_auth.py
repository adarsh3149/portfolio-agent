from app.core.security import (
    create_access_token,
    decode_access_token,
)


def test_jwt_creation_and_decoding():
    token = create_access_token("1")

    payload = decode_access_token(token)

    assert payload["sub"] == "1"