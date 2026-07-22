"""Count preflight sizing (sanitized showcase excerpt).

Before any post retrieval, a counts-only preflight sizes the seven-day volume
per query. Volume labels describe size only. They never make a human decision,
and they are read from configuration rather than hardcoded here.
"""
from __future__ import annotations

# Thresholds describe volume only. In the engine they live in pricing config.
VOLUME_BANDS = [
    (0, "empty"),
    (1, "very_low"),
    (25, "manageable"),
    (200, "broad"),
    (1000, "very_broad"),
]


def volume_label(count: int) -> str:
    """Return the volume label for a seven-day recent count."""
    label = "empty"
    for threshold, name in VOLUME_BANDS:
        if count >= threshold:
            label = name
    return label


def aggregate_count(per_query_counts: dict[str, int]) -> int:
    """Sum of seven-day counts across queries (the preflight aggregate)."""
    return sum(int(v) for v in per_query_counts.values())
