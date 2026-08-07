from app.core.security import create_access_token, decode_access_token

token = create_access_token("1")

print("Token:")
print(token)

print()

payload = decode_access_token(token)

print("Decoded Payload:")
print(payload)