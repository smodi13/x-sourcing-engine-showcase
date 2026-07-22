"""Verify the metric terminology, provenance, and public-subset accounting."""
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "public" / "demo-data"
APP_DIR = Path(__file__).resolve().parent.parent / "app"


def load(name):
    return json.loads((DATA_DIR / name).read_text())


def test_provenance_uses_unambiguous_field_names():
    p = load("metrics-provenance.json")
    c = p["counts"]
    assert c["artifact_bearing_posts"] == 851
    assert c["strict_level_a_posts"] == 737
    assert c["engine_consolidated_projects"] == 159
    assert c["analyst_adjudicated_projects"] == 153
    assert c["public_broad_run_records"] == 122
    assert c["featured_analysis_pages"] == 1
    assert c["total_detail_pages"] == 123
    # The ambiguous level_a_posts field must not be used for 851.
    assert "level_a_posts" not in c
    blob = json.dumps(p)
    assert '"level_a_posts"' not in blob


def test_851_is_never_labeled_strict_level_a():
    p = load("metrics-provenance.json")
    # 851 is artifact-bearing, explicitly broader than strict Level A.
    assert p["artifact_vs_level_a"]["artifact_bearing_posts"] == 851
    assert p["artifact_vs_level_a"]["strict_level_a_posts"] == 737
    assert p["artifact_vs_level_a"]["difference"] == 114
    # 851 is never positively labeled Level A. Negations ("851 is not Level A")
    # are allowed; direct labels ("851 Level A", "851 verified Level A") are not.
    for f in DATA_DIR.glob("*.json"):
        text = f.read_text()
        assert not re.search(r"851[- ](?:verified[- ])?Level A", text), f"851 labeled Level A in {f.name}"
        assert not re.search(r"Level A[^.]{0,20}\b851\b", text), f"851 labeled Level A in {f.name}"


def test_737_is_the_strict_level_a_count():
    p = load("metrics-provenance.json")
    assert p["counts"]["strict_level_a_posts"] == 737
    assert p["count_definitions"]["strict_level_a_posts"]["value"] == 737
    assert "strict" in p["count_definitions"]["strict_level_a_posts"]["definition"].lower()


def test_159_engine_consolidated_and_153_analyst_adjudicated():
    p = load("metrics-provenance.json")
    ev = p["engine_vs_analyst_projects"]
    assert ev["engine_consolidated_projects"] == 159
    assert ev["analyst_adjudicated_projects"] == 153
    assert ev["difference"] == 6
    assert "analyst" in ev["explanation"].lower()
    assert "record-level audit file" in ev["limitation"]
    assert p["count_definitions"]["engine_consolidated_projects"]["stage"] == "engine_consolidation"
    assert p["count_definitions"]["analyst_adjudicated_projects"]["stage"] == "analyst_adjudication"


def test_122_labeled_sanitized_broad_run_records():
    p = load("metrics-provenance.json")
    cand = load("candidates.json")
    assert p["counts"]["public_broad_run_records"] == cand["count"] == len(cand["candidates"]) == 122
    label = p["count_definitions"]["public_broad_run_records"]["definition"].lower()
    assert "sanitized broad-run project records" in label


def test_123_is_detail_pages_not_candidates():
    p = load("metrics-provenance.json")
    cand = load("candidates.json")
    pages = len(cand["candidates"]) + len(cand["featured"])
    assert p["counts"]["total_detail_pages"] == pages == 123
    defn = p["count_definitions"]["total_detail_pages"]["definition"]
    assert "not 123 equivalent candidates" in defn


def test_aos_not_included_in_122_and_is_separate_featured():
    p = load("metrics-provenance.json")
    cand = load("candidates.json")
    assert p["public_showcase"]["aos_included_in_public_records"] is False
    slugs = {c["slug"] for c in cand["candidates"]}
    assert "aos-unicity-labs" not in slugs
    assert any(f["slug"] == "aos-unicity-labs" for f in cand["featured"])
    assert "separate featured" in p["public_showcase"]["aos_note"].lower()


def test_public_exclusion_reconciles():
    p = load("metrics-provenance.json")
    d = p["public_showcase"]["derivation"]
    assert d["actionable_posts"] - d["excluded_unnamed_posts"] - d["duplicate_project_posts_collapsed"] == d["public_broad_run_records"] == 122
    assert p["public_showcase"]["exclusion_count"] == d["excluded_unnamed_posts"] + d["duplicate_project_posts_collapsed"]


def test_aos_button_label_updated():
    home = (APP_DIR / "page.tsx").read_text()
    assert "View the AOS investment case" in home
    assert "View the AOS thesis" not in home


def test_multi_query_labeled_non_deduplicated():
    qp = load("query-performance.json")
    assert "68" in qp["totals_note"]
    assert qp["totals"]["posts_processed"] > 1166
    assert load("metrics-provenance.json")["multi_query_posts"] == 68


def test_forbidden_wording_absent():
    blob = " ".join((DATA_DIR / f.name).read_text() for f in DATA_DIR.glob("*.json"))
    assert not re.search(r"851\s+Level A", blob)
    assert not re.search(r"851\s+verified\s+(artifact\s+)?compan", blob)
    assert not re.search(r"1,?279\s+unique\s+Posts", blob)
    assert not re.search(r"851\s+companies", blob)
    assert not re.search(r"153\s+incorporated", blob)
    assert not re.search(r"123\s+sanitized\s+candidates", blob)
    assert not re.search(r"123\s+broad-run\s+companies", blob)


def test_funnel_order_and_values():
    p = load("metrics-provenance.json")
    keys = [f["key"] for f in p["funnel"]]
    assert keys.index("artifact_bearing_posts") < keys.index("strict_level_a_posts")
    assert keys.index("engine_consolidated_projects") < keys.index("analyst_adjudicated_projects")
    by_key = {f["key"]: f["value"] for f in p["funnel"]}
    assert by_key["artifact_bearing_posts"] == 851
    assert by_key["strict_level_a_posts"] == 737
    assert by_key["engine_consolidated_projects"] == 159
    assert by_key["analyst_adjudicated_projects"] == 153
    assert by_key["public_broad_run_records"] == 122
