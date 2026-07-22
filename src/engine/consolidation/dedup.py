"""Deduplication (sanitized showcase excerpt).

The broad run removes within-run duplicate records and cross-run duplicates
against the pilot. A single post can match more than one query, so multi-query
matches are recorded rather than counted twice at the run level.
"""
from __future__ import annotations

from collections import defaultdict


def dedupe_within_run(records: list[dict]) -> tuple[list[dict], int, int]:
    """Collapse records that share a post_id.

    Returns the deduplicated records (each annotated with the set of matching
    queries), the number of duplicate records removed, and the number of posts
    that matched more than one query.
    """
    by_post: dict[str, dict] = {}
    queries_for: dict[str, set[str]] = defaultdict(set)
    duplicates_removed = 0

    for rec in records:
        pid = rec["post_id"]
        for q in rec.get("source_queries", []):
            queries_for[pid].add(q)
        if pid in by_post:
            duplicates_removed += 1
            continue
        by_post[pid] = dict(rec)

    multi_query = 0
    out: list[dict] = []
    for pid, rec in by_post.items():
        qset = sorted(queries_for[pid])
        rec["source_queries"] = qset
        if len(qset) > 1:
            multi_query += 1
        out.append(rec)
    return out, duplicates_removed, multi_query


def remove_cross_run_duplicates(records: list[dict], prior_post_ids: set[str]) -> tuple[list[dict], int]:
    """Drop records already seen in a prior run. Returns kept records and removed count."""
    kept = [r for r in records if r["post_id"] not in prior_post_ids]
    return kept, len(records) - len(kept)


def dedupe_authors(records: list[dict]) -> int:
    """Count of unique authors across records."""
    return len({r.get("author_id") for r in records if r.get("author_id") is not None})
