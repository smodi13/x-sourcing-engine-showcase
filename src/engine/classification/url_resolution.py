"""URL extraction, canonicalization, and artifact typing (sanitized excerpt).

An artifact link that points back to X is not an external product artifact.
The engine extracts URLs from a post, canonicalizes them, excludes X-owned
domains, and records the artifact type. It performs no network calls in this
excerpt (redirect expansion is represented by a pluggable resolver).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse

URL_RE = re.compile(r"https?://[^\s)\"'>]+", re.IGNORECASE)

# X-owned or platform-internal hosts that do not count as external artifacts.
X_DOMAINS = {"x.com", "twitter.com", "t.co", "mobile.twitter.com", "pic.twitter.com", "pic.x.com"}

ARTIFACT_HINTS = [
    ("github_repository", ("github.com", "gitlab.com", "bitbucket.org")),
    ("documentation", ("docs.", "readthedocs.io", "/docs", "notion.site", "gitbook.io")),
    ("app_store_listing", ("apps.apple.com", "play.google.com")),
    ("live_demo", ("demo.", "/demo", "huggingface.co/spaces", "vercel.app", "streamlit.app")),
    ("api_endpoint", ("/api", "api.")),
]


def extract_urls(text: str) -> list[str]:
    """Extract raw URLs from post text, order-preserving and de-duplicated."""
    seen: list[str] = []
    for m in URL_RE.findall(text or ""):
        cleaned = m.rstrip(".,;")
        if cleaned not in seen:
            seen.append(cleaned)
    return seen


def canonicalize(url: str) -> str:
    """Lowercase host, drop fragments and tracking query, strip trailing slash."""
    p = urlparse(url)
    host = (p.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    path = p.path.rstrip("/")
    return urlunparse((p.scheme.lower(), host, path, "", "", ""))


def is_x_domain(url: str) -> bool:
    host = (urlparse(url).netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host in X_DOMAINS


def artifact_type(url: str) -> str:
    """Classify the artifact type from the canonical URL. Defaults to product_website."""
    u = url.lower()
    for kind, hints in ARTIFACT_HINTS:
        if any(h in u for h in hints):
            return kind
    return "product_website"


def resolve_artifacts(text: str, resolver=canonicalize) -> list[dict]:
    """Return external artifacts only, with type. X-domain links are excluded.

    ``resolver`` stands in for redirect expansion plus canonicalization. It is
    injected so the excerpt stays offline and deterministic.
    """
    artifacts: list[dict] = []
    seen: set[str] = set()
    for raw in extract_urls(text):
        if is_x_domain(raw):
            continue  # a link back to X is not an external artifact
        canon = resolver(raw)
        if is_x_domain(canon) or canon in seen:
            continue
        seen.add(canon)
        artifacts.append({"url": canon, "type": artifact_type(canon)})
    return artifacts
