"""
Authentication and Authorization for Binah-Σ

Supports:
- API key authentication
- JWT tokens
- Tier-based access control
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_PLEASE")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 365


class Tier:
    """Subscription tiers"""
    STARTUP = "startup"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    DEMO = "demo"


class TierLimits:
    """Usage limits per tier"""
    LIMITS = {
        Tier.DEMO: {
            "requests_per_month": 3,
            "requests_per_day": 3,
            "requests_per_minute": 1
        },
        Tier.STARTUP: {
            "requests_per_month": 100,
            "requests_per_day": 10,
            "requests_per_minute": 5
        },
        Tier.PROFESSIONAL: {
            "requests_per_month": 1000,
            "requests_per_day": 100,
            "requests_per_minute": 20
        },
        Tier.ENTERPRISE: {
            "requests_per_month": float('inf'),
            "requests_per_day": float('inf'),
            "requests_per_minute": 100
        }
    }

    @classmethod
    def get_limit(cls, tier: str, limit_type: str) -> float:
        """Get limit for a tier and limit type"""
        return cls.LIMITS.get(tier, cls.LIMITS[Tier.DEMO]).get(limit_type, 0)


def create_api_key(customer_id: str, tier: str = Tier.STARTUP, email: str = None) -> str:
    """
    Generate a new API key (JWT token).

    Args:
        customer_id: Unique customer identifier
        tier: Subscription tier
        email: Customer email (optional)

    Returns:
        str: JWT token to use as API key
    """
    payload = {
        "sub": customer_id,
        "tier": tier,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_api_key(token: str) -> dict:
    """
    Decode and validate API key.

    Args:
        token: JWT token

    Returns:
        dict: Decoded payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired API key: {str(e)}"
        )


class APIKeyAuth:
    """API key authentication dependency"""

    @staticmethod
    async def verify_api_key(
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        """
        Verify API key from Authorization header.

        Args:
            credentials: HTTP authorization credentials

        Returns:
            dict: Decoded token payload with customer info

        Raises:
            HTTPException: If authentication fails
        """
        token = credentials.credentials

        # Decode and validate
        payload = decode_api_key(token)

        # Check expiration (already done in decode_api_key, but double-check)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="API key expired")

        return payload

    @staticmethod
    async def verify_tier(
        min_tier: str,
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        """
        Verify API key has minimum tier level.

        Args:
            min_tier: Minimum required tier
            credentials: HTTP authorization credentials

        Returns:
            dict: Token payload

        Raises:
            HTTPException: If tier insufficient
        """
        payload = await APIKeyAuth.verify_api_key(credentials)

        tier_hierarchy = [Tier.DEMO, Tier.STARTUP, Tier.PROFESSIONAL, Tier.ENTERPRISE]
        user_tier = payload.get("tier", Tier.DEMO)

        if tier_hierarchy.index(user_tier) < tier_hierarchy.index(min_tier):
            raise HTTPException(
                status_code=403,
                detail=f"This feature requires {min_tier} tier or higher"
            )

        return payload


# Simple in-memory storage for demo (replace with database in production)
DEMO_API_KEYS = {}


def initialize_demo_keys():
    """Initialize some demo API keys for testing"""
    demo_key = create_api_key("demo_user", Tier.DEMO, "demo@example.com")
    startup_key = create_api_key("startup_user", Tier.STARTUP, "startup@example.com")

    DEMO_API_KEYS["demo"] = demo_key
    DEMO_API_KEYS["startup"] = startup_key

    print("\n" + "="*60)
    print("DEMO API KEYS GENERATED")
    print("="*60)
    print(f"Demo Tier:    {demo_key}")
    print(f"Startup Tier: {startup_key}")
    print("="*60 + "\n")


# Initialize on import
if os.getenv("INIT_DEMO_KEYS", "true").lower() == "true":
    initialize_demo_keys()
