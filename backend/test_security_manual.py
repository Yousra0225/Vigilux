from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from jose import jwt

def test_security():
    password = "secret_password"
    hashed = get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed}")
    
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
    print("Password verification works.")
    
    token = create_access_token(subject="user_123")
    print(f"Token: {token}")
    
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"Decoded: {decoded}")
    assert decoded["sub"] == "user_123"
    print("Token generation and decoding works.")

if __name__ == "__main__":
    test_security()
