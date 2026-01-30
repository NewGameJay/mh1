#!/usr/bin/env python3
"""
LinkedIn Keyword Search - Setup Verification Script

This script verifies that:
1. Python environment is correctly set up
2. Required libraries are installed
3. API credentials are valid
4. API connectivity works
5. A simple test query succeeds

Run this before using the main collection script.
"""

import sys
import json
import io
import os

# Load environment variables from .env file (if python-dotenv is installed)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use existing environment variables

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================================
# CONFIGURATION (loaded from .env file)
# ============================================================================

CRUSTDATA_API_KEY = os.environ.get("CRUSTDATA_API_KEY", "")
CRUSTDATA_API_URL = "https://api.crustdata.com"

# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

def check_python_version():
    """Check Python version is 3.7+"""
    print("\n" + "=" * 80)
    print("1️⃣  CHECKING PYTHON VERSION")
    print("=" * 80)

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 7:
        print("✅ Python version is compatible (3.7+)")
        return True
    else:
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False


def check_requests_library():
    """Check if requests library is installed"""
    print("\n" + "=" * 80)
    print("2️⃣  CHECKING REQUESTS LIBRARY")
    print("=" * 80)

    try:
        import requests
        print(f"✅ requests library installed (version {requests.__version__})")
        return True, requests
    except ImportError:
        print("❌ requests library not found")
        print("\nInstalling requests library...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
            print(f"✅ requests library installed successfully (version {requests.__version__})")
            return True, requests
        except Exception as e:
            print(f"❌ Failed to install requests: {str(e)}")
            print("\nPlease install manually:")
            print("  pip install requests")
            return False, None


def check_api_credentials():
    """Verify API key format"""
    print("\n" + "=" * 80)
    print("3️⃣  CHECKING API CREDENTIALS")
    print("=" * 80)

    if not CRUSTDATA_API_KEY or CRUSTDATA_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ API key not configured")
        print("\nPlease set CRUSTDATA_API_KEY in the script")
        return False

    print(f"API Key: {CRUSTDATA_API_KEY[:20]}..." + "*" * (len(CRUSTDATA_API_KEY) - 20))
    print(f"API URL: {CRUSTDATA_API_URL}")
    print("✅ API credentials configured")
    return True


def test_api_connectivity(requests):
    """Test API connectivity with a minimal query"""
    print("\n" + "=" * 80)
    print("4️⃣  TESTING API CONNECTIVITY")
    print("=" * 80)

    endpoint = f"{CRUSTDATA_API_URL}/screener/linkedin_posts/keyword_search/"

    headers = {
        "Authorization": f"Token {CRUSTDATA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Minimal test payload (should cost 1 credit if successful)
    payload = {
        "keyword": "test",
        "limit": 1,
        "date_posted": "past-week"
    }

    print(f"Endpoint: {endpoint}")
    print(f"Test payload: {json.dumps(payload, indent=2)}")
    print("\nSending test request...")

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)

        # Check rate limit headers
        rate_limit = response.headers.get("X-RateLimit-Limit")
        rate_remaining = response.headers.get("X-RateLimit-Remaining")

        print(f"\n📊 Response Status: {response.status_code}")

        if rate_limit and rate_remaining:
            print(f"📊 Rate Limit: {rate_remaining}/{rate_limit} remaining")

        if response.status_code == 200:
            data = response.json()

            # Handle both response formats
            if isinstance(data, dict):
                posts = data.get("posts", [])
                total_count = data.get("total_count", len(posts))
            elif isinstance(data, list):
                posts = data
                total_count = len(posts)
            else:
                posts = []
                total_count = 0

            print(f"\n✅ API REQUEST SUCCESSFUL!")
            print(f"   Posts returned: {len(posts)}")
            print(f"   Total available: {total_count}")
            print(f"   Estimated credit cost: {len(posts)} credit(s)")

            if posts:
                first_post = posts[0]
                print(f"\n📄 First post preview:")
                print(f"   Actor: {first_post.get('actor_name', 'N/A')}")
                print(f"   Type: {first_post.get('actor_type', 'N/A')}")
                print(f"   URL: {first_post.get('share_url', 'N/A')}")
                text = first_post.get('text', '')
                if text:
                    print(f"   Text: {text[:100]}...")

            return True

        elif response.status_code == 404:
            print(f"⚠️  404 Not Found - No posts matched the test query")
            print(f"   This is OK - API is working, just no results for test keyword")
            try:
                error_data = response.json()
                if "total_fetched_posts" in error_data:
                    print(f"   Posts scanned: {error_data['total_fetched_posts']}")
            except:
                pass
            return True  # API is working, just no results

        elif response.status_code == 401:
            print(f"❌ 401 Unauthorized - Invalid API key")
            print(f"   Please check your CRUSTDATA_API_KEY")
            return False

        elif response.status_code == 429:
            print(f"⚠️  429 Too Many Requests - Rate limit exceeded")
            print(f"   Wait a moment and try again")
            return False

        elif response.status_code == 400:
            print(f"❌ 400 Bad Request")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:500]}")
            return False

        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - API may be slow or unavailable")
        return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - Cannot reach API")
        print(f"   Check your internet connection")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def print_summary(results):
    """Print final summary"""
    print("\n" + "=" * 80)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 80)

    checks = [
        ("Python Version", results.get("python", False)),
        ("Requests Library", results.get("requests", False)),
        ("API Credentials", results.get("credentials", False)),
        ("API Connectivity", results.get("connectivity", False)),
    ]

    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")

    all_passed = all(result for result in results.values())

    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! You're ready to use the skill.")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Customize linkedin_collection_template.py with your search parameters")
        print("2. Run: python linkedin_keyword_search.py")
        print("3. Check the generated CSV and stats files")
        print("\nFor examples, see: linkedin_examples.md")
        print("For quick reference, see: quick_reference.md")
    else:
        print("⚠️  SOME CHECKS FAILED - Please fix the issues above")
        print("=" * 80)
        print("\nCommon fixes:")
        print("- Install Python 3.7+: https://www.python.org/downloads/")
        print("- Install requests: pip install requests")
        print("- Check API key in script configuration")
        print("- Verify internet connection")

    return all_passed


def main():
    """Run all verification checks"""
    print("🔍 LINKEDIN KEYWORD SEARCH - SETUP VERIFICATION")
    print("This script will verify your environment is ready to use the skill")

    results = {}

    # Check 1: Python version
    results["python"] = check_python_version()

    if not results["python"]:
        print("\n❌ Cannot proceed without Python 3.7+")
        return False

    # Check 2: Requests library
    results["requests"], requests_module = check_requests_library()

    if not results["requests"]:
        print("\n❌ Cannot proceed without requests library")
        return False

    # Check 3: API credentials
    results["credentials"] = check_api_credentials()

    if not results["credentials"]:
        print("\n❌ Cannot proceed without valid credentials")
        return False

    # Check 4: API connectivity
    results["connectivity"] = test_api_connectivity(requests_module)

    # Print summary
    all_passed = print_summary(results)

    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
