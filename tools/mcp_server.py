#!/usr/bin/env python3
"""MCP server — exposes scrape_urls and validate_scraped_content as tools.

Run with:
    python tools/mcp_server.py

Register in Claude Code (~/.claude/settings.json):
    {
      "mcpServers": {
        "taxidermy": {
          "command": "/absolute/path/to/venv/bin/python",
          "args": ["/absolute/path/to/tools/mcp_server.py"]
        }
      }
    }
"""

import sys
from pathlib import Path

# Make 'core' importable when running from the tools/ subdirectory
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

from core import scrape_urls as _scrape_urls
from core.storage import validate_output

mcp = FastMCP("taxidermy")


@mcp.tool()
def scrape_urls(
    urls: list[str],
    output_dir: str = "./scraped_content",
    delay: float = 1.5,
    force_rescrape: bool = False,
) -> dict:
    """Extract clean markdown text from a list of URLs.

    Saves one .md file per URL, organised by domain, in output_dir.
    Returns a summary: {total, successful, failed, output_dir, index_path}.
    """
    return _scrape_urls(
        urls=urls,
        output_dir=output_dir,
        delay=delay,
        force_rescrape=force_rescrape,
        verbose=False,
    )


@mcp.tool()
def validate_scraped_content(output_dir: str = "./scraped_content") -> dict:
    """Validate scraped content quality in an output directory.

    Returns {valid: bool, issue_count: int, issues: list[str]}.
    """
    issues = validate_output(Path(output_dir))
    return {"valid": len(issues) == 0, "issue_count": len(issues), "issues": issues}


if __name__ == "__main__":
    mcp.run()
