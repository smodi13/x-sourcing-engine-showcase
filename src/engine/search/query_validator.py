"""Query validator (sanitized showcase excerpt).

The validator runs before any API call. It rejects unsupported operators,
enforces the allowed operator set, requires a standalone term alongside
conjunction-required operators, and enforces the recent-search character limit.
This is deterministic and offline.
"""
from __future__ import annotations

import re

MAX_QUERY_CHARS = 512

# Operators that X recent search does not support for this access tier.
FORBIDDEN_OPERATORS = ("min_faves:", "min_replies:", "min_retweets:")

# Conjunction-required operators must be paired with a standalone search term.
CONJUNCTION_REQUIRED = ("has:links", "has:media", "has:images", "has:videos")


class QueryValidationError(ValueError):
    """Raised when a query violates a recent-search constraint."""


def _has_standalone_term(query: str) -> bool:
    """True if the query contains a non-operator term or an exact phrase."""
    if '"' in query:
        return True
    tokens = re.split(r"\s+", query.strip())
    for tok in tokens:
        bare = tok.strip("()")
        if not bare or bare in {"OR", "AND"}:
            continue
        if ":" in bare or bare.startswith("-"):
            continue
        return True
    return False


def validate_query(query: str) -> None:
    """Validate a single query string, failing closed on any violation."""
    if not query or not query.strip():
        raise QueryValidationError("empty query")
    if len(query) > MAX_QUERY_CHARS:
        raise QueryValidationError(f"query exceeds {MAX_QUERY_CHARS} characters ({len(query)})")
    lowered = query.lower()
    for op in FORBIDDEN_OPERATORS:
        if op in lowered:
            raise QueryValidationError(f"unsupported operator: {op}")
    for op in CONJUNCTION_REQUIRED:
        if op in lowered and not _has_standalone_term(query):
            raise QueryValidationError(f"{op} requires a standalone search term")


def validate_all(queries: list[str]) -> None:
    for q in queries:
        validate_query(q)
