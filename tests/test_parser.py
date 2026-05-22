import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parser import extract_metadata, extract_text

_SAMPLE_HTML = """
<html>
<head>
  <title>Test Page</title>
  <meta name="description" content="A test page">
</head>
<body>
  <nav><a href="/">Home</a></nav>
  <header><h1>Site Title</h1></header>
  <main>
    <h1>Main Heading</h1>
    <p>First paragraph with some text.</p>
    <h2>Section Two</h2>
    <ul>
      <li>Item one</li>
      <li>Item two</li>
    </ul>
    <p>Final paragraph.</p>
  </main>
  <footer>Copyright 2026</footer>
  <script>alert('noise')</script>
</body>
</html>
"""


def test_headings_converted():
    text = extract_text(_SAMPLE_HTML)
    assert "# Main Heading" in text
    assert "## Section Two" in text


def test_nav_footer_removed():
    text = extract_text(_SAMPLE_HTML)
    assert "Home" not in text
    assert "Copyright" not in text


def test_script_removed():
    text = extract_text(_SAMPLE_HTML)
    assert "alert" not in text


def test_list_items_converted():
    text = extract_text(_SAMPLE_HTML)
    assert "- Item one" in text
    assert "- Item two" in text


def test_paragraphs_present():
    text = extract_text(_SAMPLE_HTML)
    assert "First paragraph" in text
    assert "Final paragraph" in text


def test_metadata():
    meta = extract_metadata(_SAMPLE_HTML)
    assert meta["title"] == "Test Page"
    assert meta["description"] == "A test page"


def test_fallback_plain_text():
    """Pages with no block elements should fall back to plain text."""
    html = "<html><body><div>Just some plain text here.</div></body></html>"
    text = extract_text(html)
    assert "Just some plain text" in text
