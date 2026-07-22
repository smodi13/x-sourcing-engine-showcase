"""Classification tests: evidence levels, decay, attribution, URL handling, ownership."""
from engine.classification.evidence import (
    Signal, apply_time_decay, best_level, decay_weight_for_age, level_for_post,
)
from engine.classification.builder_attribution import (
    COMMENTARY, DIRECT_BUILDER, THIRD_PARTY, classify_attribution, is_actionable,
)
from engine.classification.url_resolution import (
    artifact_type, extract_urls, is_x_domain, resolve_artifacts,
)
from engine.classification.ownership import SELF_ORGANIZATION, UNRELATED, actor_project_relation


# --- evidence --------------------------------------------------------------
def test_level_for_post():
    assert level_for_post(True, True, True) == "A"
    assert level_for_post(False, True, True) == "B"
    assert level_for_post(False, False, True) == "C"
    assert level_for_post(False, False, False) == "D"


def test_best_level_prefers_strongest():
    assert best_level(["D", "B", "A"]) == "A"
    assert best_level(["C", "D"]) == "C"
    assert best_level([]) == "D"


def test_time_decay_bands():
    assert decay_weight_for_age(3) == 1.0
    assert decay_weight_for_age(20) == 0.9
    assert decay_weight_for_age(60) == 0.7
    assert decay_weight_for_age(120) == 0.3
    assert decay_weight_for_age(400) == 0.1


def test_enduring_signal_never_decays():
    assert apply_time_decay(Signal("founder_background", 500)) == 1.0
    assert apply_time_decay(Signal("launch", 500)) == 0.1


# --- attribution -----------------------------------------------------------
def test_direct_builder_detected():
    assert classify_attribution("We just launched our agent runtime, link below") == DIRECT_BUILDER
    assert classify_attribution("I built a new MCP server this weekend") == DIRECT_BUILDER


def test_third_party_and_commentary():
    assert classify_attribution("Check out this cool tool by another team") == THIRD_PARTY
    assert classify_attribution("The future of AI agents is bright, here are 5 reasons") == COMMENTARY


def test_is_actionable_requires_direct_plus_level_a():
    assert is_actionable(DIRECT_BUILDER, "A") is True
    assert is_actionable(DIRECT_BUILDER, "B") is False
    assert is_actionable(THIRD_PARTY, "A") is False


# --- url handling ----------------------------------------------------------
def test_extract_urls_dedup_and_trim():
    text = "see https://omninode.ai/signup. and https://omninode.ai/signup again"
    assert extract_urls(text) == ["https://omninode.ai/signup"]


def test_x_domain_excluded():
    assert is_x_domain("https://t.co/abc123") is True
    assert is_x_domain("https://x.com/i/web/status/1") is True
    assert is_x_domain("https://github.com/acme/repo") is False


def test_artifact_typing():
    assert artifact_type("https://github.com/acme/repo") == "github_repository"
    assert artifact_type("https://docs.acme.com/start") == "documentation"
    assert artifact_type("https://acme.com") == "product_website"


def test_resolve_artifacts_excludes_x_links():
    text = "launch https://t.co/x https://github.com/acme/repo https://acme.com"
    arts = resolve_artifacts(text)
    urls = [a["url"] for a in arts]
    assert "https://github.com/acme/repo" in urls
    assert all("t.co" not in u and "x.com" not in u for u in urls)


# --- ownership -------------------------------------------------------------
def test_self_organization_match():
    rel = actor_project_relation("acmehq", ["https://github.com/acmehq/runtime"])
    assert rel == SELF_ORGANIZATION


def test_registered_org_is_not_self():
    registry = {"microsoft": "Microsoft"}
    rel = actor_project_relation("randomdev", ["https://github.com/microsoft/vscode"], registry)
    assert rel == UNRELATED
