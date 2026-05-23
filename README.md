# Universal Website Scraper

URL list in → clean markdown files out. Zero config, agent-ready.

## Running it

### Single URL

```bash
cd "universal-website-scraper"
source venv/bin/activate
python -u scraper.py --url https://example.com
```

### Large batch (50–100+ URLs)

**Step 1 — Create a `urls.txt` file.** One URL per line:

```
https://example.com/
https://example.com/about
https://example.com/blog/post-one
https://example.com/blog/post-two
```

**Step 2 — Run against the file:**

```bash
cd "universal-website-scraper"
source venv/bin/activate
python -u scraper.py urls.txt
```

The `-u` flag forces unbuffered output so progress appears live in your terminal. The scraper works through every URL and saves clean markdown files organised by domain under `./scraped_content/`.

**Recommended flags for large jobs:**

```bash
# Slower delay to be polite to the server (good for 100+ URLs)
python -u scraper.py urls.txt --delay-min 2.0 --delay-max 4.0

# Custom output folder
python -u scraper.py urls.txt --output ./competitor_research/

# Validate content quality at the end
python -u scraper.py urls.txt --validate

# Combine all three
python -u scraper.py urls.txt --delay-min 2.0 --delay-max 4.0 --output ./competitor_research/ --validate
```

**If the job is interrupted** (network drop, Ctrl+C, etc.), just re-run the same command. Files that are already complete are skipped automatically — it picks up where it left off. Use `--force` to re-scrape everything from scratch.

### From a sitemap

```bash
python scraper.py --sitemap https://example.com/sitemap.xml
```

Recursively follows sitemap indexes and discovers every URL automatically.

## Installation

Requires Python 3.10+ (tested on 3.12 via Homebrew).

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` includes `brotlicffi` for brotli-compressed sites and `mcp` for agent integration — no separate MCP requirements file needed.

## CLI reference

```
python scraper.py [URL_FILE] [options]

Input (pick one):
  URL_FILE              File with URLs (newline, comma, or JSON array)
  --url URL             Scrape a single URL
  --sitemap URL         Discover URLs from sitemap.xml

Options:
  --output DIR          Output directory (default: ./scraped_content)
  --delay SECS          Base delay between requests (default: 1.5)
  --delay-min SECS      Min randomised delay (default: 1.0)
  --delay-max SECS      Max randomised delay (default: 3.0)
  --timeout SECS        Request timeout (default: 30)
  --retries N           Max retries per URL (default: 3)
  --min-length N        Min chars to consider file already valid (default: 500)
  --force               Re-scrape even if output file exists
  --validate            Run content validation after scraping
  --quiet               Suppress per-URL progress output
```

## Input formats

All three are auto-detected:

```
# Newline-separated
https://example.com/
https://example.com/about

# Comma-separated
https://example.com/, https://example.com/about

# JSON array
["https://example.com/", "https://example.com/about"]
```

## Output structure

```
scraped_content/
├── example_com/
│   ├── homepage.md
│   ├── about.md
│   └── blog__my_post.md
├── other_site_com/
│   └── homepage.md
└── _index.json
```

Each file has a metadata header followed by clean markdown content:

```markdown
# Page Title

**Source URL:** https://example.com/about
**Scraped:** 2026-05-22 14:30:00 UTC
**Description:** About us page

---

## Our Mission

...
```

`_index.json` records every URL's status, filename, and content length.

## Resume support

Re-running on the same URL list skips files that already exist and have ≥500 chars. Use `--force` to re-scrape everything.

## Programmatic API

```python
from core import scrape_urls

result = scrape_urls(
    urls=["https://example.com/", "https://example.com/about"],
    output_dir="./scraped_content",
    delay=1.5,
    force_rescrape=False,
)
# {"total": 2, "successful": 2, "failed": 0, "output_dir": "...", "index_path": "..."}
```

## MCP server (Python 3.10+ required)

Register in `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "universal-scraper": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/tools/mcp_server.py"]
    }
  }
}
```

Claude can then call `scrape_urls` and `validate_scraped_content` directly.

## Running tests

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## Project structure

```
├── scraper.py              CLI entry point
├── requirements.txt        All dependencies (Python 3.10+, includes brotli + mcp)
├── config/
│   └── default_config.json Default settings reference
├── core/
│   ├── fetcher.py          HTTP requests + retry logic
│   ├── parser.py           HTML → Markdown extraction
│   ├── slugify.py          URL → filename conversion
│   ├── storage.py          File I/O, index, resume, validation
│   └── scraper.py          Orchestrator class
└── tools/
    └── mcp_server.py       MCP server (FastMCP)
```
