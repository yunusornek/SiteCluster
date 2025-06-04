import os
import sys
import pytest

# Add project root to sys.path so tests can import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import ensure_https, strip_protocol, remove_duplicate_urls, calculate_jaccard_similarity


def test_ensure_https_basic():
    assert ensure_https("example.com") == "https://example.com"
    assert ensure_https("http://example.com") == "http://example.com"
    assert ensure_https("https://example.com/") == "https://example.com"
    assert ensure_https("https://example.com/foo/") == "https://example.com/foo"


def test_ensure_https_with_query_and_spaces():
    assert ensure_https("  https://example.com/foo?bar=1 ") == "https://example.com/foo"


def test_strip_protocol_basic():
    assert strip_protocol("https://example.com/path") == "example.com"
    assert strip_protocol("http://example.com/") == "example.com"
    assert strip_protocol("example.com") == "example.com"
    assert strip_protocol("HTTPS://EXAMPLE.COM") == "example.com"


def test_remove_duplicate_urls_basic():
    urls = ["http://example.com", "https://example.com"]
    assert remove_duplicate_urls(urls) == ["https://example.com"]


def test_remove_duplicate_urls_paths_and_query():
    urls = [
        "https://example.com/foo",
        "https://example.com/bar",
        "https://example.com/bar?baz=1",
        "http://example.org",
        "example.org/",
    ]
    result = remove_duplicate_urls(urls)
    # example.com domain should keep last https path 'bar'
    assert "https://example.com/bar" in result and len([u for u in result if "example.com" in u]) == 1
    # example.org should deduplicate and prefer https
    assert "https://example.org" in result and len(result) == 2


def test_calculate_jaccard_similarity():
    assert calculate_jaccard_similarity(["a", "b"], ["a", "b"]) == 1.0
    assert calculate_jaccard_similarity([], []) == 0.0
    assert calculate_jaccard_similarity(["a"], []) == 0.0
    assert calculate_jaccard_similarity(["a", "a", "b"], ["b", "c", "c"]) == pytest.approx(1/3)
