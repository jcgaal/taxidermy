import re
from urllib.parse import urlparse


def url_to_domain_dir(url: str) -> str:
    """Extract domain as a filesystem-safe directory name."""
    parsed = urlparse(url)
    netloc = parsed.netloc.split(':')[0]  # strip port
    return re.sub(r'[^\w]', '_', netloc)


def url_to_path_filename(url: str) -> str:
    """Convert URL path to a filesystem-safe markdown filename."""
    parsed = urlparse(url)
    path = parsed.path.strip('/')

    if not path:
        return 'homepage.md'

    parts = []
    for seg in path.split('/'):
        seg = re.sub(r'[^\w]', '_', seg)
        seg = re.sub(r'_+', '_', seg).strip('_')
        if seg:
            parts.append(seg)

    return ('__'.join(parts) or 'homepage') + '.md'


def url_to_slug(url: str) -> str:
    """Full slug: domain__path (no .md extension). Used in _index.json."""
    domain = url_to_domain_dir(url)
    filename = url_to_path_filename(url)[:-3]  # strip .md
    return f"{domain}__{filename}"


def url_to_filepath(url: str) -> tuple[str, str]:
    """Return (domain_dir, filename) for organizing output by domain."""
    return url_to_domain_dir(url), url_to_path_filename(url)
