"""
JWT token utilities for authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular imports - config will be passed in
    pass


def create_access_token(
    data: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None,
    default_expire_minutes: int = 1440
) -> str:
    """
    Create JWT access token
    
    Args:
        data: Token payload data
        secret_key: Secret key for signing
        algorithm: JWT algorithm (default: HS256)
        expires_delta: Custom expiration time
        default_expire_minutes: Default expiration in minutes (24 hours)
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=default_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        secret_key,
        algorithm=algorithm
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expire_days: int = 7
) -> str:
    """
    Create JWT refresh token
    
    Args:
        data: Token payload data
        secret_key: Secret key for signing
        algorithm: JWT algorithm (default: HS256)
        expire_days: Expiration in days (default: 7)
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=expire_days)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        secret_key,
        algorithm=algorithm
    )
    
    return encoded_jwt


def decode_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256"
) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
        secret_key: Secret key for verification
        algorithm: JWT algorithm (default: HS256)
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm]
        )
        return payload
    except JWTError:
        return None


def verify_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256"
) -> Dict[str, Any]:
    """
    Verify and decode JWT token, raising exception on failure
    
    Args:
        token: JWT token string
        secret_key: Secret key for verification
        algorithm: JWT algorithm (default: HS256)
    
    Returns:
        Decoded token payload
    
    Raises:
        JWTError: If token is invalid or expired
    """
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm]
    )
    return payload

