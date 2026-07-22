"""Cost control tests: Decimal money math, fingerprints, approval expiry, locks."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from engine.cost_controls.money import (
    BudgetExceeded, MoneyError, check_budget, estimate_cost, money_str, parse_money,
)
from engine.cost_controls.approval import (
    Approval, ApprovalError, CanonicalRequest, ExecutionLock, ExecutionLockError,
    require_approval,
)


def make_request(query="agent runtime launch", version="2"):
    return CanonicalRequest(
        query_id="q01",
        query=query,
        tweet_fields="id,text,created_at,author_id,public_metrics,entities",
        expansions="author_id",
        user_fields="id,name,username,description",
        start_time_policy="recent_search_default_7d",
        end_time_policy="now",
        max_results_per_page=100,
        query_config_version=version,
        extra={"paginate": True},
    )


# --- money -----------------------------------------------------------------
def test_parse_money_rejects_float():
    with pytest.raises(MoneyError):
        parse_money(0.005)


def test_parse_money_rejects_negative_and_placeholder():
    with pytest.raises(MoneyError):
        parse_money("-1.00")
    with pytest.raises(MoneyError):
        parse_money("pending_manual_reconciliation")


def test_money_str_fixed_point():
    assert money_str(Decimal("0.05")) == "0.050"


def test_estimate_cost_is_exact():
    assert estimate_cost(1279, "0.005") == Decimal("6.395")
    assert estimate_cost(20, "0.005") == Decimal("0.100")
    assert estimate_cost(14, "0.010") == Decimal("0.140")


def test_check_budget_passes_and_fails():
    remaining = check_budget(Decimal("7.720"), "25.000")
    assert remaining == Decimal("17.280")
    with pytest.raises(BudgetExceeded):
        check_budget(Decimal("30.000"), "25.000")


# --- fingerprint determinism ----------------------------------------------
def test_fingerprint_is_deterministic():
    assert make_request().fingerprint() == make_request().fingerprint()


def test_fingerprint_changes_when_any_field_changes():
    base = make_request().fingerprint()
    assert make_request(query="different query").fingerprint() != base
    assert make_request(version="3").fingerprint() != base


def test_fingerprint_has_sha256_prefix():
    fp = make_request().fingerprint()
    assert fp.startswith("sha256:")
    assert len(fp) == len("sha256:") + 64


# --- approval expiry -------------------------------------------------------
def test_approval_valid_within_window():
    req = make_request()
    now = datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc)
    appr = Approval(fingerprint=req.fingerprint(), approved_at=now)
    require_approval(req, appr, now=now + timedelta(minutes=14))


def test_approval_expires_after_fifteen_minutes():
    req = make_request()
    now = datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc)
    appr = Approval(fingerprint=req.fingerprint(), approved_at=now)
    with pytest.raises(ApprovalError):
        require_approval(req, appr, now=now + timedelta(minutes=16))


def test_approval_rejects_different_request():
    now = datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc)
    appr = Approval(fingerprint=make_request().fingerprint(), approved_at=now)
    with pytest.raises(ApprovalError):
        require_approval(make_request(query="other"), appr, now=now)


def test_missing_approval_fails_closed():
    with pytest.raises(ApprovalError):
        require_approval(make_request(), None)


# --- execution lock --------------------------------------------------------
def test_execution_lock_prevents_duplicate():
    lock = ExecutionLock()
    fp = make_request().fingerprint()
    lock.acquire(fp)
    assert lock.is_locked(fp)
    with pytest.raises(ExecutionLockError):
        lock.acquire(fp)
