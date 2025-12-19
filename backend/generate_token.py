from jose import jwt
import datetime
from datetime import timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "v0nFwgGQbleNgcJSSDjTpXOVCPH75x5bIvFY-yc-sfQ")
ALGORITHM = "HS256"

# You can modify these values as needed
CUSTOMER_ID = "binah-sigma-demo"
TIER = "startup"  # Options: "demo", "startup", "professional", "enterprise"
EMAIL = "demo@example.com"
DAYS_VALID = 365

payload = {
    "sub": CUSTOMER_ID,
    "tier": TIER,
    "email": EMAIL,
    "iat": datetime.datetime.now(timezone.utc),
    "exp": datetime.datetime.now(timezone.utc) + datetime.timedelta(days=DAYS_VALID)
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

print("="*60)
print("API KEY GENERATED")
print("="*60)
print(f"Customer: {CUSTOMER_ID}")
print(f"Tier: {TIER}")
print(f"Email: {EMAIL}")
print(f"Valid for: {DAYS_VALID} days")
print("="*60)
print(f"\nAPI Key:\n{token}")
print("\n" + "="*60)
