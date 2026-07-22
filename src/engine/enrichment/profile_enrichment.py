"""Selective profile enrichment logic (sanitized showcase excerpt).

Only shortlisted profiles are enriched, to respect the budget and to avoid
unnecessary paid calls. Enrichment examines founder and executive roles,
company links, and identity evidence. Follower count and verification status
do not determine advancement. This excerpt performs no network calls.
"""
from __future__ import annotations

EXAMINED = ("founder_and_executive_roles", "company_links", "identity_evidence")
IGNORED_FOR_ADVANCEMENT = ("follower_count", "verified")


def select_for_enrichment(candidates: list[dict], max_profiles: int) -> list[dict]:
    """Pick the shortlisted candidates to enrich, capped by budget.

    Selection prefers verified Level A leads, then leads flagged for enrichment.
    Follower count is never used to rank advancement.
    """
    def rank(c: dict) -> tuple:
        disp = c.get("lead_disposition")
        primary = 0 if disp == "keep_verified" else (1 if disp == "keep_for_enrichment" else 2)
        score = c.get("research_score") or 0
        return (primary, -score)

    ordered = sorted(candidates, key=rank)
    return ordered[: max(0, max_profiles)]


def enrichment_signal_is_advancing(profile: dict) -> bool:
    """A profile advances on role and company evidence, not on popularity."""
    role = (profile.get("role") or "").lower()
    has_company_link = bool(profile.get("company_links"))
    is_leader = any(k in role for k in ("founder", "ceo", "cto", "co-founder", "chief"))
    return is_leader and has_company_link
