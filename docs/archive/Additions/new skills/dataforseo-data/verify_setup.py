"""
DataForSEO Skill - Setup Verification

This script verifies that your environment is ready to use the DataForSEO skill.
"""

import sys
import io
import base64

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("🔍 DATAFORSEO SKILL - SETUP VERIFICATION")
print("=" * 80)
print()

# Track overall status
all_checks_passed = True

# Check 1: Python version
print("[1/3] Checking Python version...")
python_version = sys.version_info
if python_version.major >= 3 and python_version.minor >= 7:
    print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (OK)")
else:
    print(f"  ❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (Need 3.7+)")
    all_checks_passed = False
print()

# Check 2: Requests library
print("[2/3] Checking requests library...")
try:
    import requests
    print(f"  ✅ requests {requests.__version__} installed")
except ImportError:
    print("  ❌ requests not installed")
    print("     Fix: Run 'pip install requests'")
    all_checks_passed = False
print()

# Check 3: API Connectivity
print("[3/3] Testing DataForSEO API connectivity...")

# Credentials provided by user
# Base64: am9zZXBoLnF1ZXNhZGFAbWFya2V0ZXJoaXJlLmNvbToxMzk1OGIyNzNkNjZmMDEw
# Decoded: joseph.quesada@marketerhire.com:13958b273d66f010

try:
    # Using Live SERP API for a quick ping (or just checking balance/user info)
    # A simple GET to https://api.dataforseo.com/v3/serp/google/organic/live/advanced/task_post is not right for GET
    # Let's try a simple ping to their user endpoint if available, or a minimal live task
    
    # Using the credential string provided directly
    auth_header = "Basic am9zZXBoLnF1ZXNhZGFAbWFya2V0ZXJoaXJlLmNvbToxMzk1OGIyNzNkNjZmMDEw"
    
    # Endpoint to check user balance or info is usually a good test
    # DataForSEO doesn't have a simple "whoami" in V3 easily without a specific endpoint documentation handy, 
    # but we can try a lightweight Live SERP request.
    
    url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    
    # Payload for a dummy search
    payload = [{
        "language_code": "en",
        "location_code": 2840, # US
        "keyword": "test connectivity"
    }]
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    # We won't actually run a full task if we can avoid it to save money, 
    # but the Live API is the most direct test. 
    # Alternatively, we can check the `my_account` endpoint if it exists.
    # Documentation says: GET /v3/merchant/google/reviews/task_get (example).
    # Let's use a known specialized endpoint: https://api.dataforseo.com/v3/ping doesn't exist.
    # Let's just use the requests library to hit the API.
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['status_code'] == 20000:
            print("  ✅ API Connection successful")
            print(f"  ✅ Cost: {data.get('cost', 'N/A')}")
        else:
            print(f"  ❌ API Error: {data.get('status_message')}")
            all_checks_passed = False
    elif response.status_code == 401:
        print("  ❌ Authentication failed (401)")
        all_checks_passed = False
    else:
        print(f"  ❌ HTTP Error: {response.status_code}")
        all_checks_passed = False

except Exception as e:
    print(f"  ❌ Connection failed: {str(e)}")
    all_checks_passed = False
print()

# Summary
print("=" * 80)
if all_checks_passed:
    print("✨ SETUP VERIFICATION COMPLETE - ALL CHECKS PASSED!")
    print("=" * 80)
else:
    print("⚠️  SETUP VERIFICATION INCOMPLETE")
    print("=" * 80)



