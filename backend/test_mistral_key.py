"""
Quick test to verify Mistral API key is valid
"""
import os
from dotenv import load_dotenv
from mistralai import Mistral

# Load environment variables
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

print(f"Testing Mistral API key: {api_key[:10]}...{api_key[-5:]}")
print(f"Key length: {len(api_key)} characters")

try:
    client = Mistral(api_key=api_key)

    # Simple test request
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "user", "content": "Say 'API key is valid' if you can read this"}
        ]
    )

    print("\n[SUCCESS] API key is valid")
    print(f"Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"\n[ERROR] API key is NOT valid")
    print(f"Error: {str(e)}")
    print("\nPlease verify:")
    print("1. The API key is correct and active")
    print("2. You have credits/quota available")
    print("3. The key has the necessary permissions")
