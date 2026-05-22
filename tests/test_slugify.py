import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.slugify import url_to_domain_dir, url_to_filepath, url_to_path_filename, url_to_slug


def test_homepage():
    assert url_to_domain_dir("https://flyguys.com/") == "flyguys_com"
    assert url_to_path_filename("https://flyguys.com/") == "homepage.md"
    assert url_to_slug("https://flyguys.com/") == "flyguys_com__homepage"


def test_path_with_hyphens():
    url = "https://flyguys.com/services/roof-inspections/"
    assert url_to_path_filename(url) == "services__roof_inspections.md"
    assert url_to_slug(url) == "flyguys_com__services__roof_inspections"


def test_deep_path():
    url = "https://api.example.com/docs/v2/auth"
    assert url_to_domain_dir(url) == "api_example_com"
    assert url_to_path_filename(url) == "docs__v2__auth.md"


def test_filepath_tuple():
    url = "https://flyguys.com/project/lemoine"
    domain, filename = url_to_filepath(url)
    assert domain == "flyguys_com"
    assert filename == "project__lemoine.md"


def test_port_stripped():
    url = "http://localhost:8000/about"
    assert url_to_domain_dir(url) == "localhost"


def test_special_chars_in_path():
    url = "https://example.com/path?query=1#section"
    # query/fragment should not leak into the slug
    filename = url_to_path_filename(url)
    assert '.md' in filename
    assert '?' not in filename
    assert '#' not in filename
