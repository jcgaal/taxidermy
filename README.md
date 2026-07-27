# 🦌 Taxidermy

![Employee dusting a massive taxidermy bighorn sheep display at a Cabela's retail store, 1998](too-much-is-not-enough.webp)

> **"Too Much Is Not Enough"** — an employee dusts a wall-sized bighorn sheep mount at a Cabela's superstore, 1998. Photograph by **Joel Sartore**. The mount outlives the animal; that is the whole idea.

Point it at a company. Get back everything they have ever said about themselves, cleaned, structured, and ready to hand to a model.

Taxidermy is the art of preserving the outward form of an animal after removing everything that made it alive. This does that to corporate communications. The company survives the process. Only the voice comes home with you.

```bash
taxidermy --sitemap https://company.com/sitemap.xml --output ./mounts/company
```

Twenty minutes later you have their entire public voice as clean markdown, organised by domain, with a metadata header on every file and an index of the whole job.

---

## Why you would want this

Every company has spent years and a real budget deciding exactly how to sound. That decision lives scattered across a few hundred pages: the about page, the careers copy, the pricing objections, the blog nobody reads, the docs, the changelog, the founder's manifesto from 2019. Nobody has ever assembled it in one place, including them.

Taxidermy assembles it in one place.

What you do with the mount is up to you. Some uses that work:

**Voice cloning for agents.** Drop the mount into a Claude Project or an agent's knowledge base and the model can write in that company's register with actual evidence instead of vibes.

**Competitive research.** Mount three competitors and read what they refuse to say. Absence is the most legible thing in a corpus.

**Client onboarding.** Mount the client before the kickoff call and arrive knowing their language better than the person who wrote it.

**Positioning audits.** A company's site is a record of every strategic decision they were too polite to announce. Mount it and the drift shows up as text.

**RAG corpora.** Clean markdown with source URLs and metadata headers, which is what retrieval actually wants.

---

## Quickstart

Requires Python 3.10 or later. Tested on 3.12.

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

One page:

```bash
python -u taxidermy.py --url https://example.com/about
```

Whole site, discovered automatically:

```bash
python -u taxidermy.py --sitemap https://example.com/sitemap.xml
```

A list you assembled yourself, one URL per line in `urls.txt`:

```bash
python -u taxidermy.py urls.txt
```

The `-u` forces unbuffered output so progress shows up live instead of arriving in one lump at the end.

---

## Mounting a company properly

The sitemap is the lazy path and it works. The better path takes five extra minutes and produces a mount worth reading.

**1. Pull the sitemap and look at it first.**

```bash
curl -s https://company.com/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' > all_urls.txt
wc -l all_urls.txt
```

**2. Cut the noise.** Most sites carry a long tail of pages with no voice in them. Author archives, tag pages, paginated listings, legal boilerplate, and anything under `/wp-content/`.

```bash
grep -vE '/(tag|category|author|page)/|\.(pdf|jpg|png)$' all_urls.txt > urls.txt
```

**3. Keep the pages where a company actually talks.** The about page, careers, pricing, customer stories, the blog, the docs, the changelog, and any manifesto or values page. Careers pages are the underrated one, since companies say things to prospective employees they would never say to a prospect.

**4. Mount it politely.**

```bash
python -u taxidermy.py urls.txt --delay-min 2.0 --delay-max 4.0 --output ./mounts/company --validate
```

**5. Feed it.** Drop `./mounts/company/` into a Claude Project's knowledge, an agent's context directory, or whatever retrieval setup you run.

If the job dies partway, run the same command again. Completed files are skipped and it picks up where it stopped. Use `--force` when you want the whole thing re-taken.

---

## Skittish sites

Some sites render nothing until JavaScript runs. When a mount comes back thin or empty, take it again with a headless Chromium behind it:

```bash
python -u taxidermy.py urls.txt --js
```

This needs Playwright's Chromium installed once:

```bash
pip install playwright && playwright install chromium
```

Slower than the plain path, so reach for it only when the plain path comes home empty.

---

## CLI reference

```
python taxidermy.py [URL_FILE] [options]

Input (pick one):
  URL_FILE              File with URLs (newline, comma, or JSON array)
  --url URL             A single page
  --sitemap URL         Discover everything from sitemap.xml, follows indexes

Options:
  --output DIR          Where the mount goes (default: ./scraped_content)
  --delay SECS          Base delay between requests (default: 1.5)
  --delay-min SECS      Min randomised delay (default: 1.0)
  --delay-max SECS      Max randomised delay (default: 3.0)
  --timeout SECS        Request timeout (default: 30)
  --retries N           Max retries per URL (default: 3)
  --min-length N        Chars needed to count a file as already done (default: 500)
  --force               Re-take everything, ignore existing files
  --js                  Render with headless Chromium for JS-only sites
  --validate            Check content quality when the job finishes
  --quiet               Stop narrating every URL
```

Input format is auto-detected. Newline-separated, comma-separated, and JSON arrays all work.

---

## What you get back

```
mounts/company/
├── company_com/
│   ├── homepage.md
│   ├── about.md
│   ├── careers.md
│   └── blog__why-we-built-this.md
└── _index.json
```

Every file carries a header so the model knows what it is reading and where it came from:

```markdown
# Why We Built This

**Source URL:** https://company.com/blog/why-we-built-this
**Scraped:** 2026-07-22 14:30:00 UTC
**Description:** The origin story, retold for the fourth time

---

## The problem nobody was solving

...
```

`_index.json` holds the status, filename, and content length for every URL in the job, which is what you check when something looks thin.

---

## Programmatic use

```python
from core import scrape_urls

result = scrape_urls(
    urls=["https://example.com/", "https://example.com/about"],
    output_dir="./mounts/example",
    delay=1.5,
    force_rescrape=False,
)
# {"total": 2, "successful": 2, "failed": 0, "output_dir": "...", "index_path": "..."}
```

Need the knobs the wrapper hides? Drive the `Taxidermist` class directly:

```python
from core.scraper import Taxidermist

mount = Taxidermist(output_dir="./mounts/example", use_js=True)
mount.scrape_urls(["https://example.com/"])
```

---

## MCP server

Register it and Claude can mount things without you touching a terminal.

```json
{
  "mcpServers": {
    "taxidermy": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/tools/mcp_server.py"]
    }
  }
}
```

Exposes `scrape_urls` and `validate_scraped_content`.

---

## Tests

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

---

## Structure

```
├── taxidermy.py            CLI entry point
├── requirements.txt        Everything, including brotli and mcp
├── config/
│   └── default_config.json Default settings
├── core/
│   ├── fetcher.py          HTTP and retry logic
│   ├── js_fetcher.py       Headless Chromium fetch (--js)
│   ├── parser.py           HTML to markdown
│   ├── slugify.py          URL to filename
│   ├── storage.py          File I/O, index, resume, validation
│   └── scraper.py          The Taxidermist — orchestrator
└── tools/
    └── mcp_server.py       MCP server (FastMCP)
```

---

## House rules

Respect `robots.txt`. Keep the delays generous on anything you do not own. This takes public pages that a browser would render for anyone, and it is still your job to know the terms of the site you are pointing it at.

Do not mount a site you would be embarrassed to be caught mounting.
