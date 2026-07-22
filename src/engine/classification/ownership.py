"""Actor to project ownership check (sanitized showcase excerpt).

An artifact alone does not prove ownership. The engine checks the relationship
between the author and the artifact's organization before treating an artifact
as the author's own. This excerpt is deterministic and offline.
"""
from __future__ import annotations

from urllib.parse import urlparse

SELF_ORGANIZATION = "self_organization"
EMPLOYEE = "employee"
UNRELATED = "unrelated"
UNREGISTERED = "unregistered"


def org_from_url(url: str) -> str | None:
    """Best-effort organization slug from a repository or product URL."""
    p = urlparse(url)
    host = (p.netloc or "").lower().removeprefix("www.")
    if host in {"github.com", "gitlab.com"}:
        parts = [x for x in p.path.split("/") if x]
        return parts[0].lower() if parts else None
    # Otherwise use the second-level domain as the organization hint.
    labels = host.split(".")
    if len(labels) >= 2:
        return labels[-2]
    return host or None


def actor_project_relation(
    author_handle: str | None,
    artifact_urls: list[str],
    known_registry: dict[str, str] | None = None,
) -> str:
    """Classify the actor to project relation.

    ``known_registry`` maps a normalized organization to an established company
    name. A match to an established, non-startup org routes the artifact away
    from the "self organization" path.
    """
    registry = known_registry or {}
    handle = (author_handle or "").lower().lstrip("@")
    for url in artifact_urls:
        org = org_from_url(url)
        if not org:
            continue
        if org in registry:
            # The artifact belongs to a registered established org.
            return EMPLOYEE if handle and handle in registry.get(org, "").lower() else UNRELATED
        if handle and (org == handle or handle in org or org in handle):
            return SELF_ORGANIZATION
    # No registry match and no handle match: unregistered, treat with caution.
    return UNREGISTERED
