"""Validate the sanitized static demo JSON that backs the replay website."""
import json
import re
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "public" / "demo-data"

REQUIRED_FILES = [
    "run-summary.json", "candidates.json", "query-performance.json",
    "cost-ledger.json", "evidence-framework.json", "methodology.json",
    "queries-pilot.json", "queries-broad.json", "test-summary.json",
    "limitations.json",
]

FORBIDDEN_IDENTITY_KEYS = {
    "author_id", "author_name", "post_text", "public_metrics", "description",
    "location", "pinned_tweet_id",
}

SECRET_RE = re.compile(
    r"(bearer\s+[A-Za-z0-9._%+/-]{16,}|authorization\s*[:=]|api[_-]?key\s*[:=]"
    r"|AAAA[A-Za-z0-9%]{24,}|sk-[A-Za-z0-9]{20,})",
    re.IGNORECASE,
)


def load(name):
    return json.loads((DATA_DIR / name).read_text())


@pytest.mark.parametrize("name", REQUIRED_FILES)
def test_file_exists_and_parses(name):
    assert (DATA_DIR / name).exists(), f"missing {name}"
    load(name)


@pytest.mark.parametrize("name", REQUIRED_FILES)
def test_no_em_dashes(name):
    text = (DATA_DIR / name).read_text()
    assert "\u2014" not in text, f"em dash present in {name}"


@pytest.mark.parametrize("name", REQUIRED_FILES)
def test_no_secrets_or_private_paths(name):
    text = (DATA_DIR / name).read_text()
    assert not SECRET_RE.search(text), f"secret-like value in {name}"
    assert "/Users/" not in text and "/home/" not in text, f"local path in {name}"


def test_candidates_have_no_identity_fields():
    file = load("candidates.json")
    for c in file["candidates"]:
        assert FORBIDDEN_IDENTITY_KEYS.isdisjoint(c.keys())
        assert c["slug"] and c["name"]


def test_candidate_slugs_are_unique():
    file = load("candidates.json")
    slugs = [c["slug"] for c in file["candidates"]] + [c["slug"] for c in file["featured"]]
    assert len(slugs) == len(set(slugs))


def test_run_summary_canonical_metrics():
    run = load("run-summary.json")
    broad = run["broad"]
    assert broad["net_new_posts"] == 1166
    assert broad["unique_authors"] == 967
    assert broad["level_a_artifact_posts"] == 851
    assert broad["actionable_posts"] == 187
    assert broad["consolidated_companies_or_projects"] == 153
    assert broad["estimated_activity_usd"] == "7.720"
    assert broad["estimated_unused_allowance_usd"] == "17.280"
    assert run["searched_entire_market"] is False
    assert run["llm_in_classification_or_disposition"] is False
    assert run["final_selection"] == "human"


def test_cost_ledger_reconciles():
    from decimal import Decimal
    ledger = load("cost-ledger.json")
    total = sum(Decimal(l["estimated_usd"]) for l in ledger["lines"])
    assert total == Decimal(ledger["estimated_activity_usd"]) == Decimal("7.720")
    assert Decimal(ledger["allowance_usd"]) - total == Decimal(ledger["estimated_remaining_usd"])


def test_queries_counts():
    assert load("queries-pilot.json")["count"] == 6
    assert load("queries-broad.json")["count"] == 20
