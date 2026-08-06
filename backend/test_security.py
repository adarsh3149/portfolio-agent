from app.core.security import hash_password, verify_password

password = "MyPassword123"

hashed = hash_password(password)

print("Hash:", hashed)

print(
    "Verification:",
    verify_password(password, hashed)
)