"""Query validator, count preflight, enrichment selection, and reporting tests."""
import pytest

from engine.search.query_validator import (
    MAX_QUERY_CHARS, QueryValidationError, validate_query,
)
from engine.search.count_preflight import aggregate_count, volume_label
from engine.enrichment.profile_enrichment import (
    enrichment_signal_is_advancing, select_for_enrichment,
)
from engine.reporting.report import run_metrics


def test_validator_rejects_unsupported_operator():
    with pytest.raises(QueryValidationError):
        validate_query('agent runtime min_faves:10')


def test_validator_rejects_over_length():
    with pytest.raises(QueryValidationError):
        validate_query("x " * (MAX_QUERY_CHARS))


def test_validator_requires_standalone_term_with_has_links():
    with pytest.raises(QueryValidationError):
        validate_query("has:links lang:en -is:retweet")
    # a standalone term makes it valid
    validate_query('"agent runtime" has:links lang:en')


def test_validator_accepts_real_query():
    validate_query('(agent runtime OR "MCP server") ("just launched" OR "open sourced")')


def test_volume_label_bands():
    assert volume_label(0) == "empty"
    assert volume_label(10) == "very_low"
    assert volume_label(60) == "manageable"
    assert volume_label(300) == "broad"
    assert volume_label(1200) == "very_broad"


def test_aggregate_count():
    assert aggregate_count({"q01": 63, "q02": 101, "q03": 151}) == 315


def test_enrichment_selection_caps_and_prioritizes():
    cands = [
        {"lead_disposition": "manual_review", "research_score": 90},
        {"lead_disposition": "keep_verified", "research_score": 50},
        {"lead_disposition": "keep_for_enrichment", "research_score": 80},
    ]
    picked = select_for_enrichment(cands, 2)
    assert len(picked) == 2
    # keep_verified ranks ahead of manual_review despite lower score
    assert picked[0]["lead_disposition"] == "keep_verified"


def test_enrichment_advances_on_role_not_popularity():
    assert enrichment_signal_is_advancing({"role": "Co-founder and CEO", "company_links": ["https://acme.com"]}) is True
    assert enrichment_signal_is_advancing({"role": "influencer", "company_links": [], "follower_count": 999999}) is False


def test_run_metrics_rates_are_derived():
    records = [
        {"announcement_attribution": "direct_builder_claim", "evidence_levels": ["A"], "lead_disposition": "keep_verified", "author_id": "a"},
        {"announcement_attribution": "commentary", "evidence_levels": ["D"], "lead_disposition": "manual_review", "author_id": "b"},
    ]
    m = run_metrics(records)
    assert m["posts_processed"] == 2
    assert m["direct_builder_claims"] == 1
    assert m["actionable_leads"] == 1
    assert m["actionable_lead_rate"] == 0.5
