"""Cross-file checks on the processed data.

The record, investigation and tag files are built by separate scripts, so these
tests make sure they still agree with each other and with the backend model.
"""

import json
import sys
from pathlib import Path

import build_investigations
import build_report
import build_tests
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.models import TestRecord as RecordModel

PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "psi"

SAFFIRE_IDS = {"saffire-iv-1", "saffire-v-2", "saffire-vi-2", "saffire-vi-3", "saffire-vi-4"}


def load(name: str) -> list[dict]:
    return json.loads((PROCESSED / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return load("tests.json")


@pytest.fixture(scope="module")
def investigations() -> list[dict]:
    return load("investigations.json")


@pytest.fixture(scope="module")
def tags() -> list[dict]:
    return load("investigation_tags.json")


def raw_metadata_present() -> bool:
    manifest = json.loads((RAW / "manifest.json").read_text(encoding="utf-8"))["investigations"]
    return all((RAW / accession / "_investigation.json").exists() for accession in manifest)


def raw_tables_present() -> bool:
    return all((RAW / source.accession / source.table).exists() for source in build_tests.SOURCES)


# --- tests.json ------------------------------------------------------------


def test_test_ids_are_unique(records):
    ids = [record["id"] for record in records]
    assert len(ids) == len(set(ids))


def test_every_record_has_the_investigation_id_key(records):
    missing = [record["id"] for record in records if "investigation_id" not in record]
    assert not missing, missing[:10]


def test_investigation_ids_exist(records, investigations):
    known = {item["id"] for item in investigations}
    unknown = {r["investigation_id"] for r in records if r["investigation_id"] is not None} - known
    assert not unknown, unknown


def test_every_record_loads_through_the_backend_model(records):
    for record in records:
        RecordModel.model_validate(record)


def test_the_five_saffire_records_are_present(records):
    saffire = {r["id"] for r in records if r["id"].startswith("saffire-")}
    assert saffire == SAFFIRE_IDS


def test_no_two_records_differ_only_by_id(records):
    seen = {}
    copies = []
    for record in records:
        key = json.dumps({k: v for k, v in record.items() if k != "id"}, sort_keys=True)
        if key in seen:
            copies.append((seen[key], record["id"]))
        seen.setdefault(key, record["id"])
    assert not copies, copies[:10]


def test_saffire_records_have_no_psi_link(records):
    for record in records:
        if record["id"].startswith("saffire-"):
            assert record["investigation_id"] is None, record["id"]


# --- investigations and tags -----------------------------------------------


def test_investigations_have_the_keys_the_backend_reads(investigations):
    for item in investigations:
        assert item["id"].startswith("PSI-")
        assert item["name"], item["id"]
        assert "hardware_family" in item, item["id"]
        assert item["landing_url"].startswith("https://psi.nasa.gov/"), item["id"]
        assert "earth_benefits" in item, item["id"]


def test_earth_benefits_are_a_list_of_text_or_null(investigations):
    for item in investigations:
        benefits = item["earth_benefits"]
        if benefits is None:
            continue
        assert isinstance(benefits, list) and benefits, item["id"]
        assert all(isinstance(b, str) and b.strip() == b and b for b in benefits), item["id"]


def test_manifest_investigations_match_investigations_json(investigations):
    manifest = json.loads((RAW / "manifest.json").read_text(encoding="utf-8"))
    assert sorted(manifest["investigations"]) == sorted(item["id"] for item in investigations)


def test_manifest_skipped_are_not_listed_as_investigations():
    manifest = json.loads((RAW / "manifest.json").read_text(encoding="utf-8"))
    skipped = {item["accession"] for item in manifest.get("skipped", [])}
    assert skipped == {"PSI-108", "PSI-181"}
    assert not skipped & set(manifest["investigations"])
    for item in manifest["skipped"]:
        assert item["researchArea"] != build_investigations.KEEP_RESEARCH_AREA, item
        assert item["title"] and item["reason"], item


# --- earth_benefits from NASA's researchImpacts ----------------------------


def test_numbered_list_is_split_with_numbers_removed():
    text = "1. First point.\n2. Second point, with a comma.\n3. Third."
    assert build_investigations.earth_benefits(text) == [
        "First point.",
        "Second point, with a comma.",
        "Third.",
    ]


def test_bracketed_numbers_are_split_too():
    text = "(1) Will improve A.\n(2) Will refine B"
    assert build_investigations.earth_benefits(text) == ["Will improve A.", "Will refine B"]


def test_paragraph_with_a_list_inside_stays_whole():
    text = "Intro sentence:\n\n  1) One.\n  2) Two."
    assert build_investigations.earth_benefits(text) == [text]


def test_plain_text_is_one_trimmed_item():
    assert build_investigations.earth_benefits("  Helps engines.\n") == ["Helps engines."]


def test_numbers_out_of_order_stay_whole():
    text = "1. One.\n3. Three."
    assert build_investigations.earth_benefits(text) == [text]


@pytest.mark.parametrize("empty", [None, "", "   \n "])
def test_empty_impacts_give_null(empty):
    assert build_investigations.earth_benefits(empty) is None


@pytest.mark.skipif(not raw_metadata_present(), reason="raw PSI metadata is not fetched in this checkout")
def test_earth_benefits_keep_nasa_wording(investigations):
    """Joined back together, the items must be NASA's text minus the numbering."""
    for item in investigations:
        meta = json.loads((RAW / item["id"] / "_investigation.json").read_text(encoding="utf-8"))
        impacts = (meta.get("researchImpacts") or "").strip()
        benefits = item["earth_benefits"]
        if not impacts:
            assert benefits is None, item["id"]
            continue
        for benefit in benefits:
            assert benefit in impacts, item["id"]


def test_tag_ids_match_investigation_ids(investigations, tags):
    assert [t["id"] for t in tags] == [i["id"] for i in investigations]


def test_tag_categories_are_allowed(tags):
    allowed = {"prevent", "detect", "put out", "related"}
    for tag in tags:
        assert tag["category"] in allowed, tag
        assert "habitats" not in tag, tag


def test_dropped_investigations_are_not_combustion(investigations):
    ids = {item["id"] for item in investigations}
    assert "PSI-181" not in ids  # solder study
    assert "PSI-108" not in ids  # fluid physics


# --- generated files are up to date ----------------------------------------


@pytest.mark.skipif(not raw_tables_present(), reason="raw PSI tables are not fetched in this checkout")
def test_build_tests_check_passes():
    assert build_tests.main(["--check"]) == 0


@pytest.mark.skipif(not raw_metadata_present(), reason="raw PSI metadata is not fetched in this checkout")
def test_build_investigations_check_passes():
    assert build_investigations.main(["--check"]) == 0


@pytest.mark.skipif(
    not (raw_metadata_present() and raw_tables_present()),
    reason="raw PSI files are not fetched in this checkout",
)
def test_build_report_check_passes():
    assert build_report.main(["--check"]) == 0
