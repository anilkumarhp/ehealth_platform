from datetime import timedelta
from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt
from app.core.config import settings

def test_hash_password():
    """
    Tests that the hashing function returns a non-empty string
    that is different from the original password.
    """
    password = "a-plain-password"
    hashed = hash_password(password)
    
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password

def test_verify_password_correct():
    """
    Tests that the verification function correctly identifies a valid password.
    """
    password = "a-valid-password-123"
    hashed = hash_password(password)
    
    assert verify_password(plain_password=password, hashed_password=hashed) is True

def test_verify_password_incorrect():
    """
    Tests that the verification function correctly identifies an invalid password.
    """
    password = "a-valid-password-456"
    hashed = hash_password(password)
    
    wrong_password = "a-wrong-password"
    
    assert verify_password(plain_password=wrong_password, hashed_password=hashed) is False

def test_create_access_token():
    """
    Tests that an access token is created correctly and contains the right data.
    """
    subject = "test@example.com"
    claims = {"role": "TESTER", "custom_claim": "some_value"}
    
    # Test with a specific expiry time
    expires = timedelta(minutes=15)
    token = create_access_token(subject=subject, expires_delta=expires, claims=claims)
    
    assert isinstance(token, str)
    
    # Decode the token to verify its contents
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert decoded_payload["sub"] == subject
    assert decoded_payload["role"] == "TESTER"
    assert decoded_payload["custom_claim"] == "some_value"
    # The 'exp' claim should also be present and correct
    assert "exp" in decoded_payload