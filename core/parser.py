import re
from bs4 import BeautifulSoup, Tag

_REMOVE_TAGS = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript', 'iframe']
_REMOVE_CLASS_KEYWORDS = ['menu', 'sidebar', 'cookie', 'modal', 'popup', 'banner', 'advertisement']

_CONTENT_SELECTORS = [
    'main', 'article',
    '[role="main"]',
    '.content', '.main-content', '.post-content', '.entry-content',
    '#content', '#main',
]


def _remove_noise(soup: BeautifulSoup, remove_tags: list, remove_class_keywords: list) -> None:
    for tag in remove_tags:
        for el in soup.find_all(tag):
            el.decompose()

    for el in soup.find_all(class_=True):
        classes = ' '.join(el.get('class', [])).lower()
        if any(kw in classes for kw in remove_class_keywords):
            el.decompose()


def _find_content_root(soup: BeautifulSoup) -> Tag:
    for selector in _CONTENT_SELECTORS:
        el = soup.select_one(selector)
        if el:
            return el
    return soup.body or soup


def _to_markdown(root: Tag) -> list[str]:
    lines = []
    _BLOCK_TAGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote'}

    for el in root.find_all(_BLOCK_TAGS):
        # Skip nested list elements — handled when parent ul/ol is processed
        if el.name in ('ul', 'ol') and el.find_parent({'ul', 'ol'}):
            continue
        if el.name == 'p' and el.find_parent({'li', 'blockquote'}):
            continue

        text = el.get_text(separator=' ', strip=True)
        if not text:
            continue

        if el.name == 'h1':
            lines.append(f"\n# {text}\n")
        elif el.name == 'h2':
            lines.append(f"\n## {text}\n")
        elif el.name == 'h3':
            lines.append(f"\n### {text}\n")
        elif el.name in ('h4', 'h5', 'h6'):
            lines.append(f"\n#### {text}\n")
        elif el.name == 'p':
            lines.append(f"{text}\n")
        elif el.name in ('ul', 'ol'):
            for li in el.find_all('li', recursive=False):
                li_text = li.get_text(separator=' ', strip=True)
                if li_text:
                    lines.append(f"- {li_text}")
            lines.append('')
        elif el.name == 'blockquote':
            lines.append(f"> {text}\n")

    return lines


def extract_text(
    html: str,
    remove_tags: list = None,
    remove_class_keywords: list = None,
) -> str:
    """Parse HTML and return clean Markdown text."""
    soup = BeautifulSoup(html, 'html.parser')
    _remove_noise(soup, remove_tags or _REMOVE_TAGS, remove_class_keywords or _REMOVE_CLASS_KEYWORDS)

    root = _find_content_root(soup)
    lines = _to_markdown(root)

    if not lines:
        # Fallback: plain text from whatever content remains
        text = root.get_text(separator='\n', strip=True)
        return re.sub(r'\n{3,}', '\n\n', text).strip()

    result = '\n'.join(lines)
    return re.sub(r'\n{3,}', '\n\n', result).strip()


def extract_metadata(html: str) -> dict:
    """Extract page title and meta description."""
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.title.get_text(strip=True) if soup.title else ''

    description = ''
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta:
        description = meta.get('content', '')

    return {'title': title, 'description': description}
