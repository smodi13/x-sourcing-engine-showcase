#!/usr/bin/env python3
"""Build sanitized static demo JSON for the public X sourcing engine showcase.

This script reads the authoritative saved outputs from a COMPLETED private
sourcing run and produces the public, sanitized JSON consumed by the Next.js
replay demo. It performs no network calls and never touches the X API.

Design rules:
  * No secrets, tokens, authorization values, or credentials are ever read
    into the output.
  * No raw X post text, personal names, usernames, author ids, profile
    descriptions, or locations are copied into the output. Only engine-derived
    classifications plus public permalinks and public artifact URLs are kept.
  * No private local absolute paths are written into the output.
  * Summary-level metrics are the finalized canonical historical figures
    (see CANONICAL below). They are fixed project records and are not
    recomputed from intermediate files.
  * Output JSON is stable and sorted, and every em dash is removed.

Usage:
  SOURCE_DIR=/path/to/private/engine python scripts/build_sanitized_demo_data.py

SOURCE_DIR must point at the private engine project root (the directory that
contains data/output and config). It is never committed and never printed.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

TRANSFORM_VERSION = "1.0.0"

# --------------------------------------------------------------------------
# Finalized canonical historical metrics. These are fixed project records.
# --------------------------------------------------------------------------
CANONICAL = {
    "pilot": {
        "query_families": 6,
        "sourcing_lanes": 3,
        "returned_post_resources": 177,
        "unique_posts": 176,
        "unique_authors": 146,
        "direct_builder_claims": 30,
        "level_a_artifact_posts": 20,
        "retained_leads": 29,
        "keep_verified": 7,
        "keep_for_enrichment": 22,
        "profiles_enriched": 11,
        "estimated_activity_usd": "1.085",
    },
    "broad": {
        "query_families": 20,
        "count_preflight_requests": 20,
        "aggregate_seven_day_count": 1486,
        "retrieval_http_requests": 25,
        "returned_post_resources": 1279,
        "net_new_posts": 1166,
        "cross_run_duplicates_removed": 26,
        "within_run_duplicates_removed": 70,
        "posts_matched_multiple_queries": 68,
        "unique_authors": 967,
        "direct_builder_claims": 190,
        "level_a_artifact_posts": 851,
        "actionable_posts": 187,
        "consolidated_companies_or_projects": 153,
        "profiles_enriched": 14,
        "profiles_returned": 14,
        "passing_tests_original_engine": 450,
        "estimated_activity_usd": "7.720",
        "estimated_unused_allowance_usd": "17.280",
        "total_allowance_usd": "25.000",
    },
}

METRIC_NOTES = {
    "returned_post_resources": "Returned Post resources, not unique Posts.",
    "net_new_posts": "Net-new Posts after within-run and cross-run deduplication.",
    "level_a_artifact_posts": "Final adjudicated count of Posts carrying an external product artifact (851). This is a Post count, not a company count. An intermediate processing stage recorded 737 Posts meeting the strict verifiable Level A bar. See the metrics reconciliation.",
    "consolidated_companies_or_projects": "Final adjudicated count of consolidated companies or projects (153). Not a count of incorporated startups. An intermediate consolidation stage recorded 159. See the metrics reconciliation.",
    "profiles_enriched": "Shortlisted profiles enriched. Not a count of funded companies.",
    "estimated_activity_usd": "Estimated API activity. Not reconciled against the external Developer Console.",
}

OFFICIAL_ENDPOINTS = [
    {"method": "GET", "url": "https://api.x.com/2/tweets/search/recent", "purpose": "Recent search over the seven-day window."},
    {"method": "GET", "url": "https://api.x.com/2/tweets/counts/recent", "purpose": "Count preflight to size volume before any retrieval."},
    {"method": "GET", "url": "https://api.x.com/2/users", "purpose": "Selective profile enrichment for shortlisted authors."},
]

REPLAY_NOTICE = (
    "Replay mode: this demo uses saved outputs from the completed sourcing run "
    "and does not initiate new X API requests."
)

# --------------------------------------------------------------------------
# Sanitization helpers
# --------------------------------------------------------------------------
EM_DASH = "\u2014"  # em dash, referenced only to detect and strip it
EN_DASH = "\u2013"  # en dash

# Fields that must never appear in public output.
FORBIDDEN_KEYS = {
    "author_id", "author_name", "username", "name", "description", "location",
    "created_at", "pinned_tweet_id", "protected", "post_text", "raw_text",
    "public_metrics", "verified", "url_entities", "author_ids",
}

# Match credential SHAPES (a token value or a header assignment), not domain
# vocabulary. The phrase "bearer tokens" as a technology term must not match;
# a real "Bearer AAAA..." value must.
SECRET_PATTERN = re.compile(
    r"(bearer\s+[A-Za-z0-9._%+/-]{16,}"          # Bearer <token>
    r"|authorization\s*[:=]"                       # Authorization: / =
    r"|api[_-]?key\s*[:=]"                          # api_key: / =
    r"|client[_-]?secret\s*[:=]"                    # client_secret: / =
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"         # PEM private key
    r"|AAAA[A-Za-z0-9%]{24,}"                       # X bearer token body
    r"|sk-[A-Za-z0-9]{20,})",                       # OpenAI-style key
    re.IGNORECASE,
)


def strip_em_dashes(value):
    if isinstance(value, str):
        out = value.replace(" " + EM_DASH + " ", ", ").replace(EM_DASH, ", ")
        out = out.replace(EN_DASH, "-")
        return out
    if isinstance(value, list):
        return [strip_em_dashes(v) for v in value]
    if isinstance(value, dict):
        return {k: strip_em_dashes(v) for k, v in value.items()}
    return value


def assert_no_secret(obj, where):
    blob = json.dumps(obj)
    if SECRET_PATTERN.search(blob):
        raise SystemExit(f"SECRET-LIKE VALUE detected in generated output at {where}. Aborting.")
    if "/Users/" in blob or "/home/" in blob:
        raise SystemExit(f"Local absolute path detected in generated output at {where}. Aborting.")


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "candidate"


def company_status_for(disposition: str) -> str:
    return {
        "keep_verified": "Verified public artifact",
        "keep_for_enrichment": "Shortlisted for enrichment",
        "manual_review": "Manual review queue",
    }.get(disposition, "Archived")


def load_json(path: Path):
    with path.open() as fh:
        return json.load(fh)


def write_json(out_dir: Path, name: str, payload):
    payload = strip_em_dashes(payload)
    assert_no_secret(payload, name)
    path = out_dir / name
    with path.open("w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, ensure_ascii=True)
        fh.write("\n")
    return path


def provenance(source_name: str) -> dict:
    """Provenance that records the source file name and transform version only,
    never a private absolute path."""
    return {
        "source_file": source_name,
        "transform_version": TRANSFORM_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "Generated from saved completed-run outputs by build_sanitized_demo_data.py.",
    }


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------
def build_run_summary(out_dir: Path):
    payload = {
        "replay_notice": REPLAY_NOTICE,
        "official_api_used": True,
        "scraping_used": False,
        "llm_in_classification_or_disposition": False,
        "final_selection": "human",
        "billing_reconciled": False,
        "recent_search_window_days": 7,
        "searched_entire_market": False,
        "official_endpoints": OFFICIAL_ENDPOINTS,
        "pilot": CANONICAL["pilot"],
        "broad": CANONICAL["broad"],
        "metric_notes": METRIC_NOTES,
        "headline_metrics": [
            {"key": "net_new_posts", "label": "Net-new Posts", "value": 1166, "note": METRIC_NOTES["net_new_posts"]},
            {"key": "unique_authors", "label": "Unique authors", "value": 967, "note": "Distinct post authors across the broad run."},
            {"key": "direct_builder_claims", "label": "Direct-builder claims", "value": 190, "note": "Posts attributed to the actual builder, not commentary or third-party reporting."},
            {"key": "level_a_artifact_posts", "label": "Level A artifact Posts", "value": 851, "note": "Final adjudicated Posts carrying an external product artifact. A Post count, not a company count. Intermediate stage recorded 737 strictly verifiable."},
            {"key": "actionable_posts", "label": "Actionable Posts", "value": 187, "note": "Posts passing attribution and artifact checks."},
            {"key": "consolidated_companies_or_projects", "label": "Consolidated companies or projects", "value": 153, "note": "Final adjudicated consolidated companies or projects, not incorporated startups. Intermediate stage recorded 159."},
            {"key": "profiles_enriched", "label": "Enriched profiles", "value": 14, "note": METRIC_NOTES["profiles_enriched"]},
            {"key": "estimated_activity_usd", "label": "Estimated activity (USD)", "value": "7.720", "note": METRIC_NOTES["estimated_activity_usd"]},
            {"key": "estimated_remaining_usd", "label": "Estimated remaining (USD)", "value": "17.280", "note": "Unused portion of the USD 25.000 estimated allowance."},
            {"key": "passing_tests", "label": "Original engine tests", "value": 450, "note": "Passing tests in the original private engine repository."},
        ],
        "provenance": provenance("global_metrics.json, processing_summary.json, cost ledgers"),
    }
    return write_json(out_dir, "run-summary.json", payload)


def build_candidates(out_dir: Path, src: Path):
    actionable = load_json(src / "data/output/broad_market_4000/processed/actionable_candidates.json")
    # Keep only engine-derived, public-safe fields. Drop identity + raw text.
    by_slug = {}
    for rec in actionable:
        name = (rec.get("normalized_company_or_project_name") or "").strip()
        if not name:
            continue
        slug = slugify(name)
        clean = {
            "slug": slug,
            "name": name,
            "sector_bucket": rec.get("sector_bucket"),
            "source_queries": sorted(set(rec.get("source_queries") or [])),
            "post_url": rec.get("post_url"),  # public permalink only
            "artifact_urls": rec.get("artifact_urls") or [],
            "artifact_types": rec.get("artifact_types") or [],
            "artifact_owner_scope": rec.get("artifact_owner_scope"),
            "evidence_levels": rec.get("evidence_levels") or [],
            "announcement_attribution": rec.get("announcement_attribution"),
            "actor_project_relation": rec.get("actor_project_relation"),
            "broad_market_relevance": rec.get("broad_market_relevance"),
            "headline_mandate_fit": rec.get("headline_mandate_fit"),
            "general_venture_attractiveness": rec.get("general_venture_attractiveness"),
            "research_score": rec.get("research_score"),
            "reason_codes": rec.get("reason_codes") or [],
            "unresolved_questions": rec.get("unresolved_questions") or [],
            "lead_disposition": rec.get("lead_disposition"),
            "company_status": company_status_for(rec.get("lead_disposition")),
            "candidate_rank": rec.get("candidate_rank"),
            "is_featured": False,
        }
        # Deduplicate by project: keep the best-ranked record, merge queries.
        prior = by_slug.get(slug)
        if prior is None:
            by_slug[slug] = clean
        else:
            prior["source_queries"] = sorted(set(prior["source_queries"]) | set(clean["source_queries"]))
            if (clean.get("candidate_rank") or 1e9) < (prior.get("candidate_rank") or 1e9):
                merged_queries = prior["source_queries"]
                by_slug[slug] = clean
                by_slug[slug]["source_queries"] = merged_queries

    candidates = sorted(by_slug.values(), key=lambda c: (c.get("candidate_rank") or 1e9, c["name"].lower()))

    # Featured human-selected candidate: public facts only, thesis is a placeholder.
    featured = [{
        "slug": "aos-unicity-labs",
        "name": "AOS / Unicity Labs",
        "sector_bucket": "ai_infrastructure",
        "is_featured": True,
        "company_status": "Human-selected for focused diligence",
        "summary": (
            "Zug-based team behind the Unicity protocol, a bearer-token peer-to-peer "
            "settlement layer. AOS is the working thesis for a secure agent execution, "
            "identity, policy, and proof layer beneath autonomous agents. Selected from "
            "the comparison set by human judgment, not by an automated score."
        ),
        "public_facts": [
            {"claim": "USD 3.0 million seed announced February 2026", "evidence_class": "company_reported"},
            {"claim": "Unicity protocol (bearer-token settlement) is the live public product", "evidence_class": "official_protocol_source"},
            {"claim": "Public GitHub organization with multiple repositories", "evidence_class": "official_protocol_source"},
            {"claim": "AOS as a distinct enterprise product is a working thesis, not a confirmed brand", "evidence_class": "analyst_hypothesis"},
        ],
        "artifact_urls": ["https://unicity.network", "https://github.com/unicitynetwork"],
        "artifact_types": ["product_website", "github_organization"],
        "evidence_levels": ["A", "C"],
        "disposition_note": (
            "The engine organized the evidence and structured the comparison. The scorecard was a "
            "decision aid, not the decision. ScaleDown scored higher on the standardized framework. "
            "AOS was advanced by human investment judgment for focused diligence, not funded."
        ),
        "thesis_availability": "placeholder",
        "thesis_note": (
            "The full investment thesis, underwriting model, and diligence playbook are maintained "
            "privately and are not published in this showcase."
        ),
        "unresolved_questions": [
            "What is AOS today, and how does it relate to the Unicity protocol, the SDK, and bearer tokens?",
            "Is there paid enterprise demand, and who is the economic buyer?",
            "Which entity captures equity value if the protocol succeeds?",
            "Is the announced seed still open, and when is the next financing?",
        ],
    }]

    payload = {
        "count": len(candidates),
        "featured_count": len(featured),
        "candidates": candidates,
        "featured": featured,
        "data_dictionary": {
            "name": "Normalized company or project name derived by the engine.",
            "sector_bucket": "Sector assigned from the matching query family.",
            "source_queries": "Query families whose results included this project.",
            "post_url": "Direct permalink to the original public X Post.",
            "artifact_urls": "Public product, documentation, or repository links extracted from the Post.",
            "artifact_types": "Type of each external artifact (repository, documentation, product website, live demo).",
            "evidence_levels": "Evidence levels present on the Post (A strongest, D weakest).",
            "announcement_attribution": "Who made the claim (direct builder, third party, commentary).",
            "actor_project_relation": "Relationship between the author and the project (self, employee, unrelated).",
            "headline_mandate_fit": "Fit with the AI Infrastructure and Software mandate.",
            "research_score": "Deterministic 0 to 100 organizing score. Not an investment score.",
            "reason_codes": "Deterministic codes explaining the disposition.",
            "lead_disposition": "Engine routing decision for the lead.",
            "company_status": "Human-readable status derived from the disposition.",
        },
        "notes": [
            "Raw Post text, author names, usernames, author ids, and profile fields are intentionally excluded.",
            "Only engine-derived classifications plus public permalinks and public artifact URLs are shown.",
        ],
        "provenance": provenance("actionable_candidates.json"),
    }
    write_json(out_dir, "candidates.json", payload)
    return len(candidates), len(featured)


def build_queries_and_performance(out_dir: Path, src: Path):
    pilot_cfg = yaml.safe_load((src / "config/queries.yaml").read_text())
    broad_cfg = yaml.safe_load((src / "config/broad_market_queries.yaml").read_text())
    counts = {c["query_id"]: c for c in load_json(src / "data/output/broad_market_4000/count_preflight/count_metrics.json")}
    qmetrics = load_json(src / "data/output/broad_market_4000/processed/query_metrics.json")["metrics"]
    summary = load_json(src / "data/output/broad_market_4000/processed/processing_summary.json")
    recs = summary.get("query_recommendations", {})

    pilot_queries = []
    for q in pilot_cfg["queries"]:
        pilot_queries.append({
            "id": q["id"],
            "lane": q.get("lane"),
            "topics": q.get("topics"),
            "query": q["query"],
            "objective": q.get("objective"),
            "expected_strong_signals": q.get("expected_strong_signals"),
            "expected_false_positives": q.get("expected_false_positives"),
        })

    broad_queries = []
    perf_rows = []
    for q in broad_cfg["queries"]:
        qid = q["id"]
        qm = qmetrics.get(qid, {})
        row = {
            "id": qid,
            "sector_bucket": q.get("sector_bucket"),
            "discovery_lane": q.get("discovery_lane"),
            "broad_group": q.get("broad_group"),
            "query": q["query"],
            "objective": q.get("objective"),
            "expected_strong_signal": q.get("expected_strong_signal"),
            "expected_false_positives": q.get("expected_false_positives"),
            "count_preflight_estimate": counts.get(qid, {}).get("total_recent_count"),
            "posts_processed": qm.get("posts_processed"),
            "actionable_leads": qm.get("actionable_leads"),
            "recommendation": recs.get(qid),
        }
        broad_queries.append(row)
        perf_rows.append({k: row[k] for k in (
            "id", "sector_bucket", "discovery_lane", "broad_group",
            "count_preflight_estimate", "posts_processed", "actionable_leads", "recommendation")})

    write_json(out_dir, "queries-pilot.json", {
        "count": len(pilot_queries),
        "architecture": "Three role-topic groups by three discovery lanes, six curated queries.",
        "lanes": ["product_artifact", "founder_transition", "early_traction"],
        "queries": pilot_queries,
        "provenance": provenance("config/queries.yaml"),
    })
    write_json(out_dir, "queries-broad.json", {
        "count": len(broad_queries),
        "broad_groups": broad_cfg.get("broad_groups", []),
        "queries": broad_queries,
        "provenance": provenance("config/broad_market_queries.yaml"),
    })
    write_json(out_dir, "query-performance.json", {
        "count": len(perf_rows),
        "columns": ["id", "sector_bucket", "discovery_lane", "broad_group",
                    "count_preflight_estimate", "posts_processed", "actionable_leads", "recommendation"],
        "recommendation_legend": {
            "expand": "Strong yield, widen coverage.",
            "retain": "Useful yield, keep as is.",
            "revise": "Mixed yield, refine operators.",
            "disable": "Low yield, retire in version two.",
        },
        "rows": perf_rows,
        "totals": {
            "count_preflight_estimate": sum((r["count_preflight_estimate"] or 0) for r in perf_rows),
            "posts_processed": sum((r["posts_processed"] or 0) for r in perf_rows),
            "actionable_leads": sum((r["actionable_leads"] or 0) for r in perf_rows),
        },
        "totals_note": (
            "Per-query posts and actionable counts are attributed to each query and sum higher than "
            "the deduplicated run totals of 1,166 net-new Posts and 187 actionable Posts, because 68 "
            "Posts matched more than one query and are counted under each."
        ),
        "provenance": provenance("query_metrics.json, count_metrics.json"),
    })
    return len(pilot_queries), len(broad_queries)


def build_cost_ledger(out_dir: Path):
    lines = [
        {"phase": "Pilot phase", "detail": "Six-query pilot retrieval plus 11 pilot profile enrichments (cumulative).", "unit_price_usd": None, "units": None, "estimated_usd": "1.085"},
        {"phase": "Broad count preflight", "detail": "20 count requests at USD 0.005 each.", "unit_price_usd": "0.005", "units": 20, "estimated_usd": "0.100"},
        {"phase": "Broad retrieval", "detail": "1,279 returned Post resources at USD 0.005 each.", "unit_price_usd": "0.005", "units": 1279, "estimated_usd": "6.395"},
        {"phase": "Broad profile enrichment", "detail": "14 profiles at USD 0.010 each.", "unit_price_usd": "0.010", "units": 14, "estimated_usd": "0.140"},
    ]
    payload = {
        "currency": "USD",
        "allowance_usd": "25.000",
        "estimated_activity_usd": "7.720",
        "estimated_remaining_usd": "17.280",
        "billing_status": "estimated_only",
        "reconciliation_status": "unavailable_external_project_access",
        "reconciliation_note": "API activity is estimated. The external Developer Console belonged to a separate project and was not accessible, so costs were not console reconciled.",
        "lines": lines,
        "official_endpoints": OFFICIAL_ENDPOINTS,
        "governance": {
            "approval_required": True,
            "approval_expiration_minutes": 15,
            "fingerprint_algorithm": "SHA-256 over the canonical request",
            "run_locked": True,
            "raw_before_derived": True,
            "fail_closed": True,
            "decimal_arithmetic": True,
        },
        "provenance": provenance("broad_run_cost_ledger.json, count_cost_ledger.json, enrichment_cost_ledger.json, pilot_cost_ledger.json"),
    }
    return write_json(out_dir, "cost-ledger.json", payload)


def build_evidence_framework(out_dir: Path):
    payload = {
        "levels": [
            {"level": "A", "label": "Direct external product artifact", "definition": "A verifiable external artifact such as a GitHub repository, documentation, a product website, or a live demo."},
            {"level": "B", "label": "Builder launch statement", "definition": "A founder or builder launch or shipping statement without a qualifying external artifact."},
            {"level": "C", "label": "Indirect supporting evidence", "definition": "Indirect signals such as related links, mentions, or context that support but do not prove the claim."},
            {"level": "D", "label": "Weak or unresolved evidence", "definition": "Weak, unresolved, or non-actionable evidence."},
        ],
        "artifact_types": ["github_repository", "documentation", "product_website", "live_demo", "api_endpoint", "app_store_listing"],
        "builder_relations": [
            {"key": "direct_builder", "definition": "The author is the builder or founder of the project."},
            {"key": "employee", "definition": "The author works at the company but is not attributed as the builder."},
            {"key": "third_party_reporter", "definition": "The author reports on someone else's launch."},
            {"key": "reviewer", "definition": "The author reviews or comments on the product."},
            {"key": "investor", "definition": "The author is an investor promoting a portfolio company."},
            {"key": "industry_commentator", "definition": "The author comments on the category, not a specific new company."},
            {"key": "established_company_announcement", "definition": "An announcement from an established company, out of scope for early discovery."},
            {"key": "unrelated_author", "definition": "The author is unrelated to any in-scope company."},
        ],
        "attribution_classes": ["direct_builder_claim", "third_party_announcement", "commentary", "unclear_attribution"],
        "dispositions": [
            {"key": "keep_verified", "definition": "Direct builder with a verified Level A artifact."},
            {"key": "keep_for_enrichment", "definition": "Promising lead that warrants selective profile enrichment."},
            {"key": "manual_review", "definition": "Ambiguous lead routed to a human for review."},
            {"key": "archive_third_party", "definition": "Third-party announcement, archived."},
            {"key": "archive_commentary", "definition": "Commentary, archived."},
            {"key": "archive_out_of_scope", "definition": "Out of mandate scope, archived."},
        ],
        "ownership_note": "An artifact alone does not prove ownership. The engine checks the relationship between the author and the artifact organization before treating an artifact as the author's own.",
        "provenance": provenance("evidence.py, classify.py, ownership.py"),
    }
    return write_json(out_dir, "evidence-framework.json", payload)


def build_methodology(out_dir: Path):
    payload = {
        "thesis": (
            "Early company signals surface on X before they appear in structured databases. "
            "A deterministic engine can convert a sourcing thesis into official X API queries, "
            "separate builders from commentary, verify public product artifacts, and produce an "
            "auditable diligence queue within a fixed budget."
        ),
        "pilot_lanes": [
            {"lane": "product_artifact", "description": "Product launches and open-source artifacts."},
            {"lane": "founder_transition", "description": "Founder-transition signals such as leaving a job or building in stealth."},
            {"lane": "early_traction", "description": "Early customer or design-partner signals."},
        ],
        "pipeline": [
            "Sourcing thesis",
            "Query configuration",
            "Count preflight",
            "Recent search",
            "URL resolution",
            "Evidence classification",
            "Builder attribution",
            "Deduplication",
            "Project consolidation",
            "Selective profile enrichment",
            "Diligence queue",
            "Human investment decision",
        ],
        "deterministic_rules": [
            "Scoring and classification are deterministic Python. No LLM assigns a score or a disposition.",
            "A validator rejects unsupported operators before any API call.",
            "Time decay applies only to time-sensitive signals, never to enduring facts.",
            "Engagement and follower counts are non-scoring and cannot advance a lead.",
        ],
        "enrichment": {
            "why_selective": "Only shortlisted profiles were enriched to respect the budget and to avoid unnecessary paid calls.",
            "what_it_examined": ["founder and executive roles", "company links", "identity evidence"],
            "what_it_ignored": ["follower count", "verification status"],
        },
        "human_decision": (
            "The engine organized evidence and structured comparison. It did not select the "
            "investment candidate. The final decision was human judgment."
        ),
        "provenance": provenance("queries.yaml, broad_market_queries.yaml, pipeline.py"),
    }
    return write_json(out_dir, "methodology.json", payload)


def build_test_summary(out_dir: Path):
    # Public showcase test categories. Counts are filled from the showcase suite,
    # not copied from the original engine. See tests/ in this repository.
    payload = {
        "original_engine_tests": 450,
        "showcase_tests": 85,
        "showcase_note": "The public showcase ships its own focused test suite of 85 tests. This count is reported separately from the original engine's 450 tests.",
        "categories": [
            {"category": "evidence_classification", "description": "Evidence level and attribution mapping."},
            {"category": "builder_attribution", "description": "Direct-builder versus third-party detection."},
            {"category": "url_exclusion", "description": "X-domain exclusion and artifact URL handling."},
            {"category": "deduplication", "description": "Within-run and cross-run duplicate removal."},
            {"category": "consolidation", "description": "Project-name normalization and company consolidation."},
            {"category": "cost_calculations", "description": "Decimal cost math and budget checks."},
            {"category": "fingerprint_determinism", "description": "Stable SHA-256 request fingerprints."},
            {"category": "approval_expiration", "description": "Fifteen-minute approval expiry."},
            {"category": "execution_lock", "description": "Run lock prevents duplicate paid execution."},
            {"category": "sanitized_json_validation", "description": "Generated demo JSON has required fields and no secrets or em dashes."},
            {"category": "metric_reconciliation", "description": "Canonical, intermediate, and public metric layers reconcile and are labeled correctly."},
        ],
        "provenance": provenance("tests/ in the showcase repository"),
    }
    return write_json(out_dir, "test-summary.json", payload)


def build_limitations(out_dir: Path):
    payload = {
        "limitations": [
            "The recent-search window is seven days, so older signals are not captured.",
            "Results carry platform and query bias toward people who post on X.",
            "A public artifact does not guarantee a company was formed.",
            "Public artifacts can be side projects rather than companies.",
            "GitHub activity does not prove customer demand.",
            "Profile self-description can be circular and is treated as a claim, not proof.",
            "API activity is estimated rather than Developer Console reconciled.",
            "No LLM performs classification or disposition.",
            "Public evidence can become stale.",
            "The engine did not search the entire startup market.",
        ],
        "version_two": [
            "Longer time horizon and historical-search support.",
            "Stronger entity resolution and an organization and domain graph.",
            "Improved product-formation detection and better handling of side projects.",
            "Stronger company identity enrichment and source freshness tracking.",
            "Configurable scoring and an analyst review workflow.",
            "Additional social and public-data sources.",
            "Deterministic replay testing and stronger public-display compliance.",
        ],
        "provenance": provenance("README.md, platform_risk.py, analysis notes"),
    }
    return write_json(out_dir, "limitations.json", payload)


def build_metrics_provenance(out_dir: Path, src: Path):
    """Exact, audited reconciliation of the three metric layers.

    The public exclusion figures are computed from the saved actionable-Posts
    output so the reconciliation is verifiable, not asserted.
    """
    actionable = load_json(src / "data/output/broad_market_4000/processed/actionable_candidates.json")
    total_actionable = len(actionable)
    named = [r for r in actionable if (r.get("normalized_company_or_project_name") or "").strip()]
    unnamed = total_actionable - len(named)
    slugs = {}
    for r in named:
        slugs.setdefault(slugify(r["normalized_company_or_project_name"]), []).append(r)
    unique_public = len(slugs)
    dup_collapsed = len(named) - unique_public
    aos_in_public = any(("aos" in s or "unicity" in s) for s in slugs)

    payload = {
        "canonical": {
            "level_a_posts": 851,
            "consolidated_projects": 153,
            "actionable_posts": 187,
            "net_new_posts": 1166,
            "source_label": "Final adjudicated metrics from the completed investment package summary.",
            "stage": "final_adjudicated",
            "definition": (
                "851 counts broad-run Posts that carry at least one external product artifact link. "
                "153 counts the final adjudicated consolidated companies or projects."
            ),
        },
        "intermediate": {
            "level_a_posts": 737,
            "consolidated_projects": 159,
            "source_label": "Intermediate processing-stage outputs (global metrics and consolidated-company audit).",
            "stage": "intermediate_processing",
            "definition": (
                "737 counts broad-run Posts whose external artifact met the strict verifiable Level A "
                "bar after link resolution. 159 counts the actionable consolidated projects at the "
                "engine's intermediate consolidation stage (124 keep_verified plus 35 keep_for_enrichment)."
            ),
            "level_a_difference": 851 - 737,
            "level_a_difference_explanation": (
                "The 114 difference is Posts that carry an external artifact link but whose artifact did "
                "not meet the strict verifiable Level A bar at the intermediate stage. 851 is the broader "
                "artifact-bearing Post count, 737 is the strict verifiable subset. Neither is an error; "
                "they measure different bars at different stages."
            ),
            "consolidated_difference": 159 - 153,
            "consolidated_difference_explanation": (
                "The engine's intermediate stage records 159 actionable consolidated projects. The final "
                "package reports 153 after a final manual adjudication that merged near-duplicate projects "
                "and reclassified a small number of borderline non-company projects. The 6-project "
                "reduction is a final-adjudication step and is not itemized as a separate saved engine "
                "audit file, so the six records are not enumerated here to avoid guessing."
            ),
        },
        "public_showcase": {
            "sanitized_records": unique_public,
            "featured_pages": 1,
            "unique_sourced_projects_represented": unique_public,
            "candidate_detail_pages": unique_public + 1,
            "aos_included_in_sanitized_records": aos_in_public,
            "source_label": "Sanitized public subset derived from the 187 broad-run actionable Posts.",
            "derivation": {
                "actionable_posts": total_actionable,
                "excluded_unnamed_posts": unnamed,
                "named_posts": len(named),
                "duplicate_project_posts_collapsed": dup_collapsed,
                "unique_public_records": unique_public,
                "formula": f"{total_actionable} actionable Posts - {unnamed} without a project name - {dup_collapsed} same-project duplicates = {unique_public} unique public records",
            },
            "exclusion_count": unnamed + dup_collapsed,
            "exclusion_reasons": [
                {"reason": "no_normalized_project_name", "count": unnamed,
                 "detail": "Actionable Posts with no engine-normalized project name cannot be shown as a meaningful, safe public project row."},
                {"reason": "same_project_duplicate_post", "count": dup_collapsed,
                 "detail": "Multiple actionable Posts describing the same project are collapsed to one public record by normalized-name slug."},
            ],
            "consolidation_key_note": (
                "The public subset consolidates the 187 actionable Posts by normalized project-name slug. "
                "This is a simpler key than the engine's final adjudicated consolidation (repo, domain, or "
                "project plus author), so 122 is not a strict subtraction from 153."
            ),
            "aos_note": (
                "AOS / Unicity Labs is not among the 122 broad-run records. It was surfaced by the same "
                "engine in the earlier pilot and targeted-enrichment comparison, and is presented "
                "separately as the featured investment-thesis page. Total candidate detail pages: "
                f"{unique_public} broad-run records plus 1 featured page equals {unique_public + 1}."
            ),
        },
        "multi_query_posts": 68,
        "multi_query_note": (
            "Per-query Post and actionable counts are attributed to each query and sum higher than the "
            "deduplicated run totals of 1,166 net-new Posts and 187 actionable Posts, because 68 Posts "
            "matched more than one query family. Query-level sums are never presented as deduplicated "
            "global totals."
        ),
        "definitions": {
            "post_resource": "A returned Post resource from recent search. 1,279 returned resources, not unique Posts.",
            "net_new_post": "A unique Post remaining after within-run and cross-run deduplication (1,166).",
            "artifact_post": "A Post carrying at least one external product artifact link (851).",
            "verifiable_level_a_post": "A Post whose artifact met the strict verifiable Level A bar (737).",
            "actionable_post": "A Post passing attribution and artifact checks (187).",
            "consolidated_project": "A consolidated company or project, not an incorporated startup (153 final, 159 intermediate).",
        },
        "policy": [
            "The public summary uses the final adjudicated metrics: 851 Level A artifact Posts and 153 consolidated companies or projects.",
            "Intermediate artifacts (737 and 159) are earlier pipeline stages and are shown here for provenance, not as errors.",
            "The 1,279 figure is returned Post resources, not a unique-Post count. The 851 figure is a Post count, not a company count. The 153 figure is consolidated projects, not incorporated startups. No specific count of unique engine-sourced companies is claimed beyond the verified public records.",
        ],
        "provenance": provenance("global_metrics.json, artifact_evidence_audit.json, consolidated_companies.json, processing_summary.json, actionable_candidates.json"),
    }
    write_json(out_dir, "metrics-provenance.json", payload)
    return unique_public, unnamed, dup_collapsed, aos_in_public


def main():
    src_env = os.environ.get("SOURCE_DIR")
    if not src_env:
        print("ERROR: set SOURCE_DIR to the private engine project root.", file=sys.stderr)
        print("Example: SOURCE_DIR=/path/to/engine python scripts/build_sanitized_demo_data.py", file=sys.stderr)
        return 2
    src = Path(src_env).expanduser().resolve()
    if not (src / "data/output/broad_market_4000").exists():
        print(f"ERROR: SOURCE_DIR does not look like the engine root (missing data/output/broad_market_4000).", file=sys.stderr)
        return 2

    out_dir = Path(__file__).resolve().parent.parent / "public" / "demo-data"
    out_dir.mkdir(parents=True, exist_ok=True)

    build_run_summary(out_dir)
    n_cand, n_feat = build_candidates(out_dir, src)
    n_pilot, n_broad = build_queries_and_performance(out_dir, src)
    build_cost_ledger(out_dir)
    build_evidence_framework(out_dir)
    build_methodology(out_dir)
    build_test_summary(out_dir)
    build_limitations(out_dir)
    n_public, n_unnamed, n_dup, aos_in = build_metrics_provenance(out_dir, src)

    # Final guard: scan every generated file for secrets, private paths, em dashes.
    problems = []
    for f in sorted(out_dir.glob("*.json")):
        text = f.read_text()
        if EM_DASH in text:
            problems.append(f"{f.name}: em dash present")
        if "/Users/" in text or "/home/" in text:
            problems.append(f"{f.name}: local path present")
        if SECRET_PATTERN.search(text):
            problems.append(f"{f.name}: secret-like value present")
    if problems:
        for p in problems:
            print("GUARD FAILURE:", p, file=sys.stderr)
        return 1

    print("Sanitized demo data written to public/demo-data/")
    print(f"  candidates: {n_cand} (plus {n_feat} featured)")
    print(f"  pilot queries: {n_pilot}")
    print(f"  broad queries: {n_broad}")
    print("  files:", ", ".join(sorted(f.name for f in out_dir.glob("*.json"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
