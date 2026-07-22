"""Evidence levels and time-decay weighting (sanitized showcase excerpt).

Every material claim is tagged with an evidence level. Time decay applies only
to time-sensitive signals such as launch, customer, usage, design-partner,
hiring, and shipping. Enduring facts such as founder background, product
category, and technical architecture are never decayed.

This excerpt is self-contained and performs no network calls.
"""
from __future__ import annotations

from dataclasses import dataclass

# Evidence levels, strongest to weakest.
LEVEL_A = "A"  # direct external product artifact (repo, docs, product site, live demo)
LEVEL_B = "B"  # builder launch statement without a qualifying external artifact
LEVEL_C = "C"  # indirect supporting evidence
LEVEL_D = "D"  # weak, unresolved, or non-actionable evidence

LEVEL_ORDER = {LEVEL_A: 0, LEVEL_B: 1, LEVEL_C: 2, LEVEL_D: 3}

ARTIFACT_TYPES = {
    "github_repository", "documentation", "product_website",
    "live_demo", "api_endpoint", "app_store_listing",
}

DECAYABLE_SIGNALS = {"launch", "customer", "usage", "design_partner", "hiring", "shipping"}
ENDURING_SIGNALS = {"founder_background", "product_category", "technical_architecture", "product_artifact"}


def best_level(levels: list[str]) -> str:
    """Return the strongest (lowest-order) evidence level present."""
    present = [l for l in levels if l in LEVEL_ORDER]
    if not present:
        return LEVEL_D
    return min(present, key=lambda l: LEVEL_ORDER[l])


def level_for_post(has_external_artifact: bool, is_builder_claim: bool, has_indirect_support: bool) -> str:
    """Deterministic evidence level for a post.

    Level A requires a verifiable external artifact. A builder launch statement
    without an external artifact is Level B. Indirect support is Level C.
    Everything else is Level D.
    """
    if has_external_artifact:
        return LEVEL_A
    if is_builder_claim:
        return LEVEL_B
    if has_indirect_support:
        return LEVEL_C
    return LEVEL_D


@dataclass
class Signal:
    signal_type: str
    age_days: float


def decay_weight_for_age(age_days: float) -> float:
    """Recency weight bands: 0-7 full, 8-30 high, 31-90 medium, 91-180 context, >180 background."""
    if age_days < 0:
        age_days = 0.0
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.9
    if age_days <= 90:
        return 0.7
    if age_days <= 180:
        return 0.3
    return 0.1


def apply_time_decay(signal: Signal) -> float:
    """Enduring facts keep weight 1.0. Time-sensitive signals decay with age."""
    if signal.signal_type in ENDURING_SIGNALS:
        return 1.0
    if signal.signal_type in DECAYABLE_SIGNALS:
        return decay_weight_for_age(signal.age_days)
    # Unknown signals are treated as context only, never full weight.
    return 0.3
