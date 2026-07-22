"""Approval control via request fingerprinting (sanitized showcase excerpt).

A paid request is gated on an approval computed from the FULL canonical request,
not just the literal query text. Adding an expansion, changing a field, or
bumping the config version changes the fingerprint and therefore invalidates a
prior approval. Approvals expire after a fixed window, and an execution lock
prevents duplicate paid execution.

This is a faithful, self-contained excerpt. It contains no secrets, no bearer
token handling, and performs no network calls.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

APPROVAL_TTL_MINUTES = 15


@dataclass(frozen=True)
class CanonicalRequest:
    """Every parameter that affects returned resources, cost, or interpretation.

    Anything added here becomes part of the fingerprint. Keep it exhaustive.
    """

    query_id: str
    query: str
    tweet_fields: str
    expansions: str
    user_fields: str
    start_time_policy: str
    end_time_policy: str
    max_results_per_page: int
    query_config_version: str
    extra: dict[str, Any] = field(default_factory=dict)

    def canonical_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["extra"] = {k: d["extra"][k] for k in sorted(d["extra"])}
        return d

    def fingerprint(self) -> str:
        blob = json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        return f"sha256:{digest}"


@dataclass(frozen=True)
class Approval:
    fingerprint: str
    approved_at: datetime
    ttl_minutes: int = APPROVAL_TTL_MINUTES

    def expires_at(self) -> datetime:
        return self.approved_at + timedelta(minutes=self.ttl_minutes)

    def is_valid_for(self, request: CanonicalRequest, now: datetime | None = None) -> bool:
        """An approval is valid only for the exact request and only before expiry."""
        now = now or datetime.now(timezone.utc)
        if self.fingerprint != request.fingerprint():
            return False
        if now >= self.expires_at():
            return False
        return True


class ApprovalError(RuntimeError):
    """Raised when a paid request is not covered by a valid approval."""


def require_approval(request: CanonicalRequest, approval: Approval | None, now: datetime | None = None) -> None:
    """Fail closed if the request is not covered by a valid, unexpired approval."""
    if approval is None:
        raise ApprovalError("no approval present, refusing paid request")
    if not approval.is_valid_for(request, now=now):
        raise ApprovalError("approval does not match this request or has expired")


class ExecutionLockError(RuntimeError):
    """Raised when a run would duplicate an already-executed paid request."""


class ExecutionLock:
    """In-memory execution lock that prevents duplicate paid execution.

    The real engine persists locks on disk so a re-run cannot repeat a paid
    call. This excerpt keeps the same fail-closed semantics in memory.
    """

    def __init__(self) -> None:
        self._locked: set[str] = set()

    def acquire(self, fingerprint: str) -> None:
        if fingerprint in self._locked:
            raise ExecutionLockError(f"fingerprint already executed: {fingerprint}")
        self._locked.add(fingerprint)

    def is_locked(self, fingerprint: str) -> bool:
        return fingerprint in self._locked
