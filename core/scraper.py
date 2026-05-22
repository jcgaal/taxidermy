import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .fetcher import fetch_url
from .parser import extract_metadata, extract_text
from .slugify import url_to_filepath, url_to_slug
from .storage import ensure_dir, file_is_valid, save_index, save_page, validate_output


class UniversalScraper:
    def __init__(
        self,
        output_dir: str = './scraped_content',
        delay: float = 1.5,
        delay_range: tuple = (1.0, 3.0),
        timeout: int = 30,
        max_retries: int = 3,
        min_content_length: int = 500,
        force_rescrape: bool = False,
        extra_headers: Optional[dict] = None,
        verbose: bool = True,
    ):
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.delay_range = delay_range
        self.timeout = timeout
        self.max_retries = max_retries
        self.min_content_length = min_content_length
        self.force_rescrape = force_rescrape
        self.extra_headers = extra_headers or {}
        self.verbose = verbose
        self.results: list[dict] = []

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg, flush=True)

    def _sleep(self) -> None:
        time.sleep(random.uniform(*self.delay_range))

    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def scrape_url(self, url: str) -> dict:
        domain_dir, filename = url_to_filepath(url)
        slug = url_to_slug(url)
        filepath = self.output_dir / domain_dir / filename
        rel = f"{domain_dir}/{filename}"

        if not self.force_rescrape and file_is_valid(filepath, self.min_content_length):
            self._log(f"  ✓ Skipped (exists): {rel}")
            return {'url': url, 'slug': slug, 'filename': rel, 'status': 'skipped'}

        try:
            response = fetch_url(
                url,
                timeout=self.timeout,
                max_retries=self.max_retries,
                extra_headers=self.extra_headers,
            )
            meta = extract_metadata(response.text)
            content = extract_text(response.text)

            if len(content) < 50:
                raise ValueError(f"Extracted content too short ({len(content)} chars)")

            save_page(filepath, url, content, title=meta['title'], description=meta['description'])

            self._log(f"  ✓ Saved: {rel} ({len(content):,} chars)")
            return {
                'url': url,
                'slug': slug,
                'filename': rel,
                'status': 'success',
                'content_length': len(content),
                'title': meta['title'],
                'scraped_at': self._now(),
            }

        except Exception as exc:
            self._log(f"  ✗ Failed: {exc}")
            return {
                'url': url,
                'slug': slug,
                'status': 'failed',
                'error': str(exc),
                'attempted_at': self._now(),
            }

    def scrape_urls(self, urls: list) -> dict:
        ensure_dir(self.output_dir)
        total = len(urls)
        self.results = []
        seen: set[str] = set()

        for i, raw_url in enumerate(urls, 1):
            url = raw_url.strip()
            if not url:
                continue

            if url in seen:
                self._log(f"\n[{i}/{total}] Duplicate — skipping: {url}")
                continue
            seen.add(url)

            self._log(f"\n[{i}/{total}] Scraping: {url}")
            result = self.scrape_url(url)
            self.results.append(result)

            ok = sum(1 for r in self.results if r['status'] in ('success', 'skipped'))
            fail = sum(1 for r in self.results if r['status'] == 'failed')
            pct = int((i / total) * 100)
            self._log(f"  Progress: {pct}% | OK: {ok} | Failed: {fail}")

            if i < total:
                self._sleep()

        index_path = save_index(self.output_dir, self.results)
        return self._summary(index_path)

    def _summary(self, index_path: Path = None) -> dict:
        ok = sum(1 for r in self.results if r['status'] in ('success', 'skipped'))
        fail = sum(1 for r in self.results if r['status'] == 'failed')
        return {
            'total': len(self.results),
            'successful': ok,
            'failed': fail,
            'output_dir': str(self.output_dir),
            'index_path': str(index_path) if index_path else None,
        }

    def validate(self) -> list[str]:
        return validate_output(self.output_dir)
