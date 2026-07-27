#!/usr/bin/env python3
"""Taxidermy — CLI entry point. Point it at a company, mount its public voice as clean markdown."""

import json
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from core.scraper import Taxidermist


# ── Input parsing ──────────────────────────────────────────────────────────────

def parse_urls(text: str) -> list[str]:
    """Accept newline-separated, comma-separated, or JSON array of URLs."""
    text = text.strip()
    if text.startswith('['):
        try:
            return [u.strip() for u in json.loads(text) if str(u).strip()]
        except json.JSONDecodeError:
            pass
    if ',' in text and '\n' not in text:
        return [u.strip() for u in text.split(',') if u.strip()]
    return [u.strip() for u in text.splitlines() if u.strip()]


def load_urls(path: str) -> list[str]:
    return parse_urls(Path(path).read_text(encoding='utf-8'))


def fetch_sitemap_urls(sitemap_url: str) -> list[str]:
    """Recursively extract all <loc> URLs from a sitemap or sitemap index."""
    print(f"Fetching sitemap: {sitemap_url}")
    resp = requests.get(sitemap_url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'lxml-xml')

    # Sitemap index → recurse into each child sitemap
    child_sitemaps = soup.find_all('sitemap')
    if child_sitemaps:
        urls: list[str] = []
        for sm in child_sitemaps:
            loc = sm.find('loc')
            if loc:
                urls.extend(fetch_sitemap_urls(loc.get_text(strip=True)))
        return urls

    return [loc.get_text(strip=True) for loc in soup.find_all('loc')]


# ── CLI ────────────────────────────────────────────────────────────────────────

def build_parser():
    import argparse

    p = argparse.ArgumentParser(
        prog='taxidermy.py',
        description='Taxidermy — point it at a company, mount its public voice as clean markdown.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python taxidermy.py urls.txt
  python taxidermy.py urls.txt --output ./mounts/company --delay 2.0
  python taxidermy.py --url https://example.com/page
  python taxidermy.py --sitemap https://example.com/sitemap.xml
  python taxidermy.py urls.txt --force --validate
        """,
    )

    src = p.add_mutually_exclusive_group()
    src.add_argument('url_file', nargs='?', metavar='URL_FILE',
                     help='File with URLs (newline / comma / JSON array)')
    src.add_argument('--url', '-u', metavar='URL',
                     help='Scrape a single URL')
    src.add_argument('--sitemap', '-s', metavar='SITEMAP_URL',
                     help='Discover URLs from a sitemap.xml')

    p.add_argument('--output', '-o', default='./scraped_content', metavar='DIR',
                   help='Output directory (default: ./scraped_content)')
    p.add_argument('--delay', '-d', type=float, default=1.5,
                   help='Base delay between requests in seconds (default: 1.5)')
    p.add_argument('--delay-min', type=float, default=1.0,
                   help='Min randomised delay (default: 1.0)')
    p.add_argument('--delay-max', type=float, default=3.0,
                   help='Max randomised delay (default: 3.0)')
    p.add_argument('--timeout', '-t', type=int, default=30,
                   help='Request timeout in seconds (default: 30)')
    p.add_argument('--retries', type=int, default=3,
                   help='Max retry attempts per URL (default: 3)')
    p.add_argument('--min-length', type=int, default=500,
                   help='Min chars to consider a file already valid (default: 500)')
    p.add_argument('--force', '-f', action='store_true',
                   help='Force re-scrape even if output file exists')
    p.add_argument('--js', action='store_true',
                   help='Use headless Chromium (Playwright) for JS-rendered sites')
    p.add_argument('--validate', action='store_true',
                   help='Run content validation after scraping')
    p.add_argument('--quiet', '-q', action='store_true',
                   help='Suppress per-URL progress output')

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # ── Gather URLs ────────────────────────────────────────────────────────────
    urls: list[str] = []

    if args.url:
        urls = [args.url]
    elif args.sitemap:
        try:
            urls = fetch_sitemap_urls(args.sitemap)
        except Exception as exc:
            print(f"Error fetching sitemap: {exc}", file=sys.stderr)
            return 1
        print(f"Found {len(urls)} URLs in sitemap.")
    elif args.url_file:
        try:
            urls = load_urls(args.url_file)
        except FileNotFoundError:
            print(f"File not found: {args.url_file}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1

    if not urls:
        print("No URLs found. Exiting.", file=sys.stderr)
        return 1

    print(f"Starting scrape of {len(urls)} URL(s) → {args.output}", flush=True)

    # ── Run scraper ────────────────────────────────────────────────────────────
    if args.js:
        print("Mode: JavaScript rendering (Playwright/Chromium)", flush=True)

    scraper = Taxidermist(
        output_dir=args.output,
        delay=args.delay,
        delay_range=(args.delay_min, args.delay_max),
        timeout=args.timeout,
        max_retries=args.retries,
        min_content_length=args.min_length,
        force_rescrape=args.force,
        use_js=args.js,
        verbose=not args.quiet,
    )

    summary = scraper.scrape_urls(urls)

    # ── Print summary ──────────────────────────────────────────────────────────
    sep = '=' * 72
    print(f"\n{sep}")
    print("SCRAPING COMPLETE")
    print(sep)
    print(f"Total URLs : {summary['total']}")
    print(f"Successful : {summary['successful']}")
    print(f"Failed     : {summary['failed']}")
    print(f"Output dir : {summary['output_dir']}")
    print(f"Index file : {summary['index_path']}")

    # ── Optional validation ────────────────────────────────────────────────────
    if args.validate:
        issues = scraper.validate()
        print(f"\nValidation ({len(issues)} issue(s) found):")
        if issues:
            for issue in issues:
                print(f"  ⚠  {issue}")
        else:
            print("  ✓  All files passed.")

    print(sep)
    return 0 if summary['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
