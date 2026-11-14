"""Tests that every link in the processed data is logged in docs/sources.md.

Rule: every number in the app must trace to a row in the source log, and a
source only counts once someone has opened it (status "Opened").
"""

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "data" / "processed"
TESTS_JSON = PROCESSED_DIR / "tests.json"
SOURCES_MD = ROOT / "docs" / "sources.md"

URL_RE = re.compile(r"https?://[^\s|<>()]+")


def find_urls(text: str) -> list[str]:
    return [u.rstrip(".,;:") for u in URL_RE.findall(text)]


def collect_source_urls(node: Any, found: set[str]) -> None:
    """Walk nested dicts and lists and collect every string `source_url`."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "source_url" and isinstance(value, str):
                found.add(value)
            collect_source_urls(value, found)
    elif isinstance(node, list):
        for item in node:
            collect_source_urls(item, found)


def parse_url_statuses(markdown: str) -> dict[str, set[str]]:
    """Map each URL in a markdown table row to the statuses of those rows."""
    statuses: dict[str, set[str]] = {}
    status_col: int | None = None
    for line in markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            status_col = None
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        if "Status" in cells:
            status_col = cells.index("Status")
            continue
        if status_col is None or status_col >= len(cells):
            continue
        for url in find_urls(line):
            statuses.setdefault(url, set()).add(cells[status_col])
    return statuses


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return json.loads(TESTS_JSON.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def processed_urls() -> set[str]:
    found: set[str] = set()
    for path in sorted(PROCESSED_DIR.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        # embeddings.json is a long list of vectors; skip parsing files with no links.
        if '"source_url"' not in text:
            continue
        collect_source_urls(json.loads(text), found)
    return found


@pytest.fixture(scope="module")
def sources_text() -> str:
    return SOURCES_MD.read_text(encoding="utf-8")


# --- tests.json records ------------------------------------------------------


def test_no_placeholder_investigation(records: list[dict]) -> None:
    bad = [
        r.get("id")
        for r in records
        if str(r.get("investigation", "")).strip().lower().startswith("tbd")
    ]
    assert not bad, f"records with a TBD investigation: {bad[:10]}"


def is_nasa_url(url: object) -> bool:
    if not isinstance(url, str) or not url.startswith("https://"):
        return False
    host = (urlparse(url).hostname or "").lower()
    return host == "nasa.gov" or host.endswith(".nasa.gov")


def test_every_record_has_nasa_source(records: list[dict]) -> None:
    bad = [r.get("id") for r in records if not is_nasa_url(r.get("source_url"))]
    assert not bad, f"records without an https NASA source_url: {bad[:10]}"


# --- source log --------------------------------------------------------------


def test_every_source_url_is_logged(processed_urls: set[str], sources_text: str) -> None:
    logged = set(find_urls(sources_text))
    missing = sorted(processed_urls - logged)
    assert not missing, f"source_url values missing from docs/sources.md: {missing}"


def test_every_source_url_is_opened(processed_urls: set[str], sources_text: str) -> None:
    statuses = parse_url_statuses(sources_text)
    not_opened = sorted(
        url for url in processed_urls if "Opened" not in statuses.get(url, set())
    )
    assert not not_opened, f"source_url values without an Opened row: {not_opened}"


def test_status_parser_reads_rows() -> None:
    md = (
        "| Source | URL | Status |\n"
        "|---|---|---|\n"
        "| A | https://a.nasa.gov/x | Unchecked |\n"
        "| A again | https://a.nasa.gov/x | Opened |\n"
        "| B | https://b.nasa.gov/y | Search result |\n"
    )
    statuses = parse_url_statuses(md)
    assert statuses["https://a.nasa.gov/x"] == {"Unchecked", "Opened"}
    assert statuses["https://b.nasa.gov/y"] == {"Search result"}


def test_nasa_host_check() -> None:
    assert is_nasa_url("https://psi.nasa.gov/physci/repo/")
    assert is_nasa_url("https://nasa.gov/")
    assert not is_nasa_url("http://psi.nasa.gov/")
    assert not is_nasa_url("https://nasa.gov.example.com/")
    assert not is_nasa_url("https://notnasa.gov/")
    assert not is_nasa_url(None)
