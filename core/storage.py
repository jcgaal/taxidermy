import json
import time
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def file_is_valid(filepath: Path, min_length: int = 500) -> bool:
    """True if the file exists and has sufficient content."""
    return filepath.exists() and filepath.stat().st_size >= min_length


def save_page(filepath: Path, url: str, content: str, title: str = '', description: str = '') -> None:
    """Write extracted content to a markdown file with a metadata header."""
    ensure_dir(filepath.parent)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title or url}\n\n")
        f.write(f"**Source URL:** {url}  \n")
        f.write(f"**Scraped:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}  \n")
        if description:
            f.write(f"**Description:** {description}  \n")
        f.write("\n---\n\n")
        f.write(content)


def save_index(output_dir: Path, results: list) -> Path:
    """Write _index.json summarising the scrape run."""
    ensure_dir(output_dir)

    successful = sum(1 for r in results if r['status'] in ('success', 'skipped'))
    failed = sum(1 for r in results if r['status'] == 'failed')

    index = {
        'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'total_urls': len(results),
        'successful': successful,
        'failed': failed,
        'urls': results,
    }

    index_path = output_dir / '_index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)

    return index_path


def validate_output(output_dir: Path) -> list[str]:
    """Return a list of issue strings for any problematic scraped files."""
    issues = []

    for filepath in sorted(output_dir.rglob('*.md')):
        try:
            content = filepath.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            issues.append(f"Encoding error: {filepath}")
            continue

        if content[:2] == '\x1f\x8b':
            issues.append(f"Binary (gzip) content: {filepath}")
        elif len(content) < 500:
            issues.append(f"Content too short ({len(content)} chars): {filepath}")
        elif 'DOCTYPE' in content[:200] or '<!DOCTYPE' in content[:200]:
            issues.append(f"Unparsed HTML leaked into output: {filepath}")

    return issues
