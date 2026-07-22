"""Reporting (sanitized showcase excerpt).

Builds run metrics from processed records. Rates are derived, not hardcoded.
This excerpt is deterministic and offline.
"""
from __future__ import annotations


def run_metrics(records: list[dict]) -> dict:
    """Compute headline run metrics from processed records."""
    total = len(records)
    direct = sum(1 for r in records if r.get("announcement_attribution") == "direct_builder_claim")
    level_a = sum(1 for r in records if "A" in (r.get("evidence_levels") or []))
    actionable = sum(1 for r in records if r.get("lead_disposition") in {"keep_verified", "keep_for_enrichment"})
    authors = len({r.get("author_id") for r in records if r.get("author_id") is not None})

    def rate(n: int) -> float:
        return round(n / total, 4) if total else 0.0

    return {
        "posts_processed": total,
        "unique_authors": authors,
        "direct_builder_claims": direct,
        "level_a_artifacts": level_a,
        "actionable_leads": actionable,
        "direct_builder_rate": rate(direct),
        "actionable_lead_rate": rate(actionable),
    }
