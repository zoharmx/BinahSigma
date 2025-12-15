"""
Simple test script to validate Binah-Σ API functionality.
Run this after starting the server to verify everything works.

Usage:
    python test_api.py
"""

import requests
import json


API_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint"""
    print("\n🔍 Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")

    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"   Response: {response.json()}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False


def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")
    response = requests.get(f"{API_URL}/")

    if response.status_code == 200:
        print("✅ Root endpoint passed")
        data = response.json()
        print(f"   Service: {data.get('service')}")
        print(f"   Status: {data.get('status')}")
        return True
    else:
        print(f"❌ Root endpoint failed: {response.status_code}")
        return False


def test_analysis():
    """Test main analysis endpoint"""
    print("\n🔍 Testing analysis endpoint...")

    payload = {
        "context": "Tech startup considering pivot to AI products",
        "decision_question": "Should we pivot our entire product line to AI-first features?",
        "stakeholders": ["founders", "employees", "customers", "investors"],
        "constraints": ["limited runway", "team expertise", "market competition"],
        "time_horizon": "12 months"
    }

    print("   Sending request...")
    print(f"   Decision: {payload['decision_question']}")

    try:
        response = requests.post(
            f"{API_URL}/binah-sigma/analyze",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            print("✅ Analysis completed successfully")
            data = response.json()

            print("\n📊 Results:")
            print(f"   Binah-Σ Index: {data.get('binah_sigma_index'):.2f}")
            print(f"   Confidence: {data.get('binah_sigma_confidence'):.2f}")
            print(f"   Coherence: {data.get('decision_coherence')}")
            print(f"   Ethical Alignment: {data.get('ethical_alignment')}")
            print(f"   Systemic Risk: {data.get('systemic_risk')}")

            if data.get('key_tensions'):
                print(f"\n   Key Tensions ({len(data['key_tensions'])}):")
                for tension in data['key_tensions'][:3]:
                    print(f"   - {tension}")

            if data.get('binah_recommendation'):
                print(f"\n   Recommendation:")
                print(f"   {data['binah_recommendation'][:200]}...")

            print(f"\n   Full response saved to: analysis_result.json")
            with open("analysis_result.json", "w") as f:
                json.dump(data, f, indent=2)

            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timeout - analysis took too long")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_invalid_request():
    """Test that invalid requests are properly rejected"""
    print("\n🔍 Testing validation (should fail gracefully)...")

    invalid_payload = {
        "context": "Test",
        "decision_question": "Test?",
        # Missing required fields
    }

    response = requests.post(
        f"{API_URL}/binah-sigma/analyze",
        json=invalid_payload
    )

    if response.status_code == 422:  # Validation error
        print("✅ Validation working correctly (rejected invalid request)")
        return True
    else:
        print(f"⚠️  Unexpected response for invalid request: {response.status_code}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Binah-Σ API Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Validation", test_invalid_request()))
    results.append(("Full Analysis", test_analysis()))

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Binah-Σ is ready for production.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("   Make sure the server is running:")
        print("   cd backend && uvicorn main:app --reload")
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
