"""
JavaScript-rendered page fetcher using Playwright (headless Chromium).
Used for SPAs and JS-heavy sites that return empty shells to plain requests.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def fetch_url_js(url: str, timeout: int = 30000, wait_until: str = "networkidle") -> str:
    """
    Fetch a URL using a headless Chromium browser and return the fully-rendered HTML.

    Args:
        url:        The page URL to fetch.
        timeout:    Navigation timeout in milliseconds (default 30s).
        wait_until: 'networkidle' waits for no network activity — best for SPAs.

    Returns:
        Full rendered HTML as a string.

    Raises:
        Exception on navigation failure or timeout.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=timeout, wait_until=wait_until)
            html = page.content()
        except PlaywrightTimeout:
            # Fallback: grab whatever rendered so far
            html = page.content()
        finally:
            browser.close()
    return html
