import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Determine if we are running in a test environment
_is_pytest = "PYTEST_CURRENT_TEST" in os.environ
_is_unittest = len(sys.argv) > 0 and ("unittest" in sys.argv[0] or sys.argv[0].endswith("unittest"))
_is_env_testing = os.getenv("TESTING") == "1"
_is_test_script = len(sys.argv) > 0 and os.path.basename(sys.argv[0]).startswith("test_")

IS_TESTING = _is_pytest or _is_unittest or _is_env_testing or _is_test_script

if IS_TESTING:
    GOOGLE_API_KEY = os.getenv("TEST_GOOGLE_API_KEY")
else:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# We remove the immediate ValueError here so that tests that don't need the LLM can still run.
# The clients will handle the missing key when they try to initialize or generate a response.

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.6-flash") # Fallback to gemini model
APP_NAME = "PDS AI Assistant"