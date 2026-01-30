"""
X (Twitter) API Setup Verification Script

This script verifies that:
1. Python version is compatible (3.7+)
2. tweepy library is installed
3. X API credentials are valid
4. API connectivity works
5. Basic search functionality works

Run this before using the twitter-keyword-search skill.
"""

import sys
import io
import os
import platform

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

# Load credentials from environment
BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")

def check_python_version():
    """Check if Python version is 3.7 or higher."""
    print("1️⃣ Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 7:
        print("   ✅ Python version is compatible")
        return True
    else:
        print(f"   ❌ Python 3.7+ required (you have {version.major}.{version.minor})")
        return False


def check_tweepy():
    """Check if tweepy is installed."""
    print("\n2️⃣ Checking tweepy library...")
    try:
        import tweepy
        print(f"   ✅ tweepy {tweepy.__version__} is installed")
        return True
    except ImportError:
        print("   ❌ tweepy is not installed")
        print("   Install it with: pip install tweepy")
        return False


def check_credentials():
    """Check if API credentials are configured."""
    print("\n3️⃣ Checking X API credentials...")

    if not BEARER_TOKEN or BEARER_TOKEN == "your_bearer_token_here":
        print("   ❌ Bearer Token not found in environment variables")
        print("   Add to your .env file: TWITTER_BEARER_TOKEN=your_bearer_token")
        return False

    print(f"   ✅ Bearer Token configured: {BEARER_TOKEN[:20]}...")
    return True


def test_api_connection():
    """Test actual API connection."""
    print("\n4️⃣ Testing X API connection...")

    try:
        import tweepy

        client = tweepy.Client(bearer_token=BEARER_TOKEN)

        # Test with a simple user lookup (Elon Musk's account)
        print("   Testing API authentication...")
        user = client.get_user(username="elonmusk")

        if user.data:
            print(f"   ✅ API connection successful!")
            print(f"   Test lookup: @{user.data.username} ({user.data.name})")
            return True
        else:
            print("   ❌ API returned no data")
            return False

    except tweepy.Unauthorized:
        print("   ❌ Authentication failed - Invalid credentials")
        print("   Check your Bearer Token is correct")
        return False
    except tweepy.Forbidden:
        print("   ❌ API access forbidden")
        print("   Check your API tier permissions")
        return False
    except tweepy.TooManyRequests:
        print("   ❌ Rate limit exceeded")
        print("   Wait 15 minutes and try again")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_search_functionality():
    """Test basic search functionality."""
    print("\n5️⃣ Testing search functionality...")

    try:
        import tweepy
        from datetime import datetime, timedelta, timezone

        client = tweepy.Client(bearer_token=BEARER_TOKEN)

        # Test search with a simple query
        print("   Testing recent search (query: 'AI' lang:en)...")
        start_time = datetime.now(timezone.utc) - timedelta(days=1)

        tweets = client.search_recent_tweets(
            query="AI lang:en",
            start_time=start_time,
            max_results=10,
            tweet_fields=['created_at', 'public_metrics']
        )

        if tweets.data:
            print(f"   ✅ Search successful! Found {len(tweets.data)} tweets")
            print(f"   Sample tweet: \"{tweets.data[0].text[:100]}...\"")
            return True
        else:
            print("   ⚠️  Search returned no results (this is okay)")
            print("   Your API connection is working!")
            return True

    except tweepy.Unauthorized:
        print("   ❌ Authentication failed during search")
        return False
    except tweepy.Forbidden as e:
        print("   ❌ Search forbidden - Check API tier access")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Search error: {e}")
        return False


def check_rate_limits():
    """Check current rate limit status."""
    print("\n6️⃣ Checking rate limit status...")

    try:
        import tweepy

        client = tweepy.Client(bearer_token=BEARER_TOKEN)

        # Get rate limit status
        limits = client.get_rate_limit_status()

        if limits:
            print("   ✅ Rate limit check successful")
            print("   (Detailed rate limits available via API)")
            return True
        else:
            print("   ⚠️  Could not retrieve rate limits (this is okay)")
            return True

    except Exception as e:
        print(f"   ⚠️  Could not check rate limits: {e}")
        print("   (This is okay, your API is still working)")
        return True


def main():
    """Run all verification checks."""
    print("=" * 80)
    print("🔍 X (TWITTER) API SETUP VERIFICATION")
    print("=" * 80)
    print()

    results = []

    results.append(("Python Version", check_python_version()))
    results.append(("tweepy Library", check_tweepy()))
    results.append(("API Credentials", check_credentials()))
    results.append(("API Connection", test_api_connection()))
    results.append(("Search Functionality", test_search_functionality()))
    results.append(("Rate Limits", check_rate_limits()))

    # Summary
    print("\n" + "=" * 80)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 80)

    all_passed = True
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name:<30} {status}")
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n🎉 SUCCESS! Your X API setup is ready to use!")
        print("\nYou can now use the twitter-keyword-search skill.")
        print("\nNext steps:")
        print("  1. Edit twitter_collection_template.py")
        print("  2. Set your search query and parameters")
        print("  3. Run: python twitter_collection_template.py")
    else:
        print("\n⚠️  SETUP INCOMPLETE")
        print("\nPlease fix the failed checks above before using the skill.")
        print("\nCommon fixes:")
        print("  • Python version: Upgrade to Python 3.7+")
        print("  • tweepy: Run 'pip install tweepy'")
        print("  • Credentials: Add TWITTER_BEARER_TOKEN to your .env file")
        print("  • API access: Verify your X Developer account and API tier")

    print()


if __name__ == "__main__":
    main()
