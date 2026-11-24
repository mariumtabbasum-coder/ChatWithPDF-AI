from functools import lru_cache
import time

from google import genai
from google.genai import types

from config import API_KEY


@lru_cache(maxsize=1)
def get_gemini_client():
    """Reuse one Gemini client so its HTTP transport stays open across requests."""
    if not API_KEY:
        raise RuntimeError('GEMINI_API_KEY is missing. Add it to your .env file.')
    return genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(
            timeout=20000,
            # The SDK defaults to five retries, which kept the UI waiting for too long.
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def call_gemini(operation):
    """Retry short Gemini service overloads before returning an error to the UI."""
    for attempt in range(2):
        try:
            return operation()
        except Exception as error:
            if not is_temporary_overload(error) or attempt == 1:
                raise
            time.sleep(1 + attempt)


def is_temporary_overload(error):
    status = getattr(error, 'code', None) or getattr(error, 'status_code', None)
    error_name = type(error).__name__.lower()
    return (
        str(status) in {'503', '504'}
        or '503 UNAVAILABLE' in str(error).upper()
        or 'timeout' in error_name
    )


def user_facing_error(error):
    if is_temporary_overload(error):
        return 'Gemini is temporarily busy or not responding. Please try again shortly.'
    return str(error)
