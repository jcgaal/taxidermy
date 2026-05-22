import time
import requests
from typing import Optional


_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Status codes that are permanent failures — don't retry
_NO_RETRY_CODES = {403, 404, 410}


def fetch_url(
    url: str,
    timeout: int = 30,
    max_retries: int = 3,
    extra_headers: Optional[dict] = None,
) -> requests.Response:
    """Fetch a URL with retry and exponential backoff.

    Raises requests.exceptions.RequestException on final failure.
    """
    headers = {**_DEFAULT_HEADERS, **(extra_headers or {})}

    last_exc: Exception = RuntimeError("fetch_url called with max_retries=0")
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as exc:
            last_exc = exc
            if exc.response is not None and exc.response.status_code in _NO_RETRY_CODES:
                raise
        except requests.exceptions.RequestException as exc:
            last_exc = exc

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s …

    raise last_exc
