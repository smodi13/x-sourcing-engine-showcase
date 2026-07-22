"""Project-name normalization and company consolidation (sanitized excerpt).

Several posts can describe the same project. The engine normalizes project
names and consolidates records into companies or projects. A post is not a
project, and a project is not an incorporated startup. These stay distinct.
"""
from __future__ import annotations

import re
from collections import defaultdict

_SUFFIXES = (
    " inc", " inc.", " llc", " ltd", " labs", " ai", " io", " app", " hq",
    " technologies", " technology", " systems", " software",
)


def normalize_name(name: str) -> str:
    """Lowercase, strip punctuation and common suffixes, collapse whitespace."""
    if not name:
        return ""
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    for suf in _SUFFIXES:
        if s.endswith(suf):
            s = s[: -len(suf)].strip()
    return s


def consolidation_key(record: dict) -> str:
    """Prefer the normalized project name, else fall back to the artifact org."""
    name = normalize_name(record.get("normalized_company_or_project_name") or "")
    if name:
        return name
    for url in record.get("artifact_urls", []) or []:
        m = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if m:
            return m.group(1).split(".")[0].lower()
    return record.get("post_id", "unknown")


def consolidate(records: list[dict]) -> list[dict]:
    """Group records into consolidated companies or projects."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        groups[consolidation_key(rec)].append(rec)

    consolidated: list[dict] = []
    for key, members in sorted(groups.items()):
        artifacts: list[str] = []
        queries: set[str] = set()
        authors: set[str] = set()
        for m in members:
            artifacts.extend(m.get("artifact_urls", []) or [])
            queries.update(m.get("source_queries", []) or [])
            if m.get("author_id") is not None:
                authors.add(m["author_id"])
        consolidated.append({
            "consolidation_key": key,
            "post_count": len(members),
            "unique_artifacts": sorted(set(artifacts)),
            "source_queries": sorted(queries),
            "author_count": len(authors),
        })
    return consolidated
