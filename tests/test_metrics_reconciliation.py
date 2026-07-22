"""Verify the metric reconciliation and public-subset accounting."""
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "public" / "demo-data"


def load(name):
    return json.loads((DATA_DIR / name).read_text())


def test_provenance_file_exists():
    assert (DATA_DIR / "metrics-provenance.json").exists()


def test_canonical_metrics_preserved():
    p = load("metrics-provenance.json")
    assert p["canonical"]["level_a_posts"] == 851
    assert p["canonical"]["consolidated_projects"] == 153
    # run-summary headline still shows the canonical figures
    run = load("run-summary.json")
    assert run["broad"]["level_a_artifact_posts"] == 851
    assert run["broad"]["consolidated_companies_or_projects"] == 153


def test_intermediate_metrics_documented():
    p = load("metrics-provenance.json")
    assert p["intermediate"]["level_a_posts"] == 737
    assert p["intermediate"]["consolidated_projects"] == 159
    assert p["intermediate"]["level_a_difference"] == 851 - 737 == 114
    assert p["intermediate"]["consolidated_difference"] == 159 - 153 == 6


def test_public_record_count_matches_generated_json():
    p = load("metrics-provenance.json")
    cand = load("candidates.json")
    assert p["public_showcase"]["sanitized_records"] == cand["count"] == len(cand["candidates"])


def test_candidate_page_count_equals_records_plus_featured():
    p = load("metrics-provenance.json")
    cand = load("candidates.json")
    ps = p["public_showcase"]
    pages = len(cand["candidates"]) + len(cand["featured"])
    assert ps["candidate_detail_pages"] == pages == ps["sanitized_records"] + 1
    assert ps["featured_pages"] == len(cand["featured"]) == 1


def test_aos_documented_as_separate_not_in_records():
    p = load("metrics-provenance.json")
    cand = load("candidates.json")
    assert p["public_showcase"]["aos_included_in_sanitized_records"] is False
    slugs = {c["slug"] for c in cand["candidates"]}
    assert "aos-unicity-labs" not in slugs
    assert any(f["slug"] == "aos-unicity-labs" for f in cand["featured"])


def test_public_exclusion_reconciles():
    p = load("metrics-provenance.json")
    d = p["public_showcase"]["derivation"]
    # 187 actionable - 37 unnamed - 28 duplicate = 122 unique
    assert d["actionable_posts"] - d["excluded_unnamed_posts"] - d["duplicate_project_posts_collapsed"] == d["unique_public_records"]
    assert d["unique_public_records"] == p["public_showcase"]["sanitized_records"]
    assert p["public_showcase"]["exclusion_count"] == d["excluded_unnamed_posts"] + d["duplicate_project_posts_collapsed"]


def test_multi_query_labeled_non_deduplicated():
    qp = load("query-performance.json")
    assert "68" in qp["totals_note"]
    assert qp["totals"]["posts_processed"] > 1166  # per-query sums exceed dedup total
    p = load("metrics-provenance.json")
    assert p["multi_query_posts"] == 68


def test_site_data_does_not_make_forbidden_claims():
    # Scan all demo JSON text for forbidden overstatements.
    blob = " ".join((DATA_DIR / f.name).read_text() for f in DATA_DIR.glob("*.json"))
    assert not re.search(r"1,?279\s+unique\s+Posts", blob)
    assert not re.search(r"851\s+companies", blob)
    assert not re.search(r"153\s+incorporated", blob)
    assert not re.search(r"123\s+unique\s+(engine[- ]sourced\s+)?companies", blob)
