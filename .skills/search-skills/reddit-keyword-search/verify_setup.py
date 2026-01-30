"""
Reddit Keyword Search Skill - Setup Verification

This script verifies that your environment is ready to use the skill.
"""

import sys
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

print("=" * 80)
print("🔍 REDDIT KEYWORD SEARCH SKILL - SETUP VERIFICATION")
print("=" * 80)
print()

# Track overall status
all_checks_passed = True

# Check 1: Python version
print("[1/4] Checking Python version...")
python_version = sys.version_info
if python_version.major >= 3 and python_version.minor >= 7:
    print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (OK)")
else:
    print(f"  ❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (Need 3.7+)")
    all_checks_passed = False
print()

# Check 2: PRAW library
print("[2/4] Checking praw library...")
try:
    import praw
    praw_version = praw.__version__
    print(f"  ✅ praw {praw_version} installed")
except ImportError:
    print("  ❌ praw not installed")
    print("     Fix: Run 'pip install praw'")
    all_checks_passed = False
print()

# Check 3: Reddit API credentials (loaded from .env file)
print("[3/4] Checking Reddit API credentials...")
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "RedditKeywordSearch/1.0")

if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
    print(f"  ✅ Client ID: {REDDIT_CLIENT_ID[:10]}...")
    print(f"  ✅ Client Secret: {REDDIT_CLIENT_SECRET[:10]}...")
    print(f"  ✅ User Agent: {REDDIT_USER_AGENT}")
else:
    print("  ❌ Credentials not found in environment variables")
    print("     Fix: Add to your .env file:")
    print("       REDDIT_CLIENT_ID=your_client_id")
    print("       REDDIT_CLIENT_SECRET=your_client_secret")
    print("       REDDIT_USER_AGENT=YourApp/1.0 (optional)")
    all_checks_passed = False
print()

# Check 4: Reddit API connectivity
print("[4/4] Testing Reddit API connectivity...")
try:
    import praw
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    # Try to fetch a subreddit to verify connection
    test_sub = reddit.subreddit("python")
    test_title = test_sub.display_name

    print(f"  ✅ Successfully connected to Reddit API")
    print(f"  ✅ Test query successful (r/{test_title})")
except ImportError:
    print("  ⚠️  Skipped (praw not installed)")
except Exception as e:
    print(f"  ❌ Connection failed: {str(e)}")
    print("     This might be a temporary issue. Try again in a moment.")
    all_checks_passed = False
print()

# Summary
print("=" * 80)
if all_checks_passed:
    print("✨ SETUP VERIFICATION COMPLETE - ALL CHECKS PASSED!")
    print("=" * 80)
    print()
    print("🎉 Your environment is ready to use the Reddit Keyword Search skill!")
    print()
    print("Next steps:")
    print("  1. Try a simple search in Claude Code:")
    print("     'Search Reddit for mentions of Python in r/programming'")
    print()
    print("  2. Check out the examples:")
    print("     Read reddit_examples.md for usage patterns")
    print()
    print("  3. Review the documentation:")
    print("     See SKILL.md for complete instructions")
else:
    print("⚠️  SETUP VERIFICATION INCOMPLETE - SOME CHECKS FAILED")
    print("=" * 80)
    print()
    print("Please fix the issues above and run this script again.")
    print()
    print("Common fixes:")
    print("  • Install praw: pip install praw")
    print("  • Update Python: Download Python 3.7+ from python.org")
    print("  • Set credentials in .env file: REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")

print()
print("=" * 80)
