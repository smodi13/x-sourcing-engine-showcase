"""Builder attribution (sanitized showcase excerpt).

Before a lead is trusted, the engine decides who is speaking. A direct builder
claim ("we launched", "I built") is treated differently from a third-party
announcement or generic commentary. Attribution is deterministic. No language
model is involved.
"""
from __future__ import annotations

import re

DIRECT_BUILDER = "direct_builder_claim"
THIRD_PARTY = "third_party_announcement"
COMMENTARY = "commentary"
UNCLEAR = "unclear_attribution"

_FIRST_PERSON_BUILD = re.compile(
    r"\b(we|i)\s+(just\s+)?(launched|built|shipped|open[\s-]?sourced|released|"
    r"are\s+building|started|created)\b",
    re.IGNORECASE,
)
_FIRST_PERSON_OWNERSHIP = re.compile(r"\b(our|my)\s+(product|tool|app|startup|company|repo|project)\b", re.IGNORECASE)
_THIRD_PARTY = re.compile(
    r"\b(check\s+out|congrats\s+to|love\s+what|great\s+work\s+by|shoutout\s+to|"
    r"just\s+tried|has\s+launched|have\s+launched|launches|announced\s+that)\b",
    re.IGNORECASE,
)
_COMMENTARY = re.compile(
    r"\b(the\s+future\s+of|hot\s+take|in\s+my\s+opinion|thread\b|here\s+are\s+\d+|"
    r"top\s+\d+|why\s+i\s+think)\b",
    re.IGNORECASE,
)


def classify_attribution(text: str) -> str:
    """Deterministic attribution class for a post."""
    t = text or ""
    if _FIRST_PERSON_BUILD.search(t) or _FIRST_PERSON_OWNERSHIP.search(t):
        # A first-person build statement that also praises someone else is still
        # a direct claim about the author's own work.
        return DIRECT_BUILDER
    if _THIRD_PARTY.search(t):
        return THIRD_PARTY
    if _COMMENTARY.search(t):
        return COMMENTARY
    return UNCLEAR


def is_actionable(attribution: str, evidence_level: str) -> bool:
    """A lead is actionable when a direct builder is paired with a Level A artifact."""
    return attribution == DIRECT_BUILDER and evidence_level == "A"
