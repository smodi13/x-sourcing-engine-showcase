"""Exact decimal currency arithmetic (sanitized showcase excerpt).

Monetary values are never Python floats. They are stored as quoted decimal
strings, parsed and validated with decimal.Decimal, and serialized as
fixed-point strings. Ledger math uses Decimal only. This module is a faithful,
self-contained excerpt of the engine's budget arithmetic. It contains no
secrets and performs no network calls.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

_PLACEHOLDERS = {
    "placeholder", "tbd", "unset", "n/a", "na", "none", "null", "pending",
    "pending_manual_reconciliation",
}

DEFAULT_PLACES = 3


class MoneyError(ValueError):
    """Raised when a monetary value is missing, non-finite, or otherwise invalid."""


def parse_money(raw: Any, *, field: str = "value", allow_zero: bool = False) -> Decimal:
    """Parse a monetary value into an exact Decimal, failing closed on bad input.

    Rejects missing or null, empty, boolean, float source, NaN or Infinity,
    negative, zero (unless allow_zero), placeholder markers, and non-decimal
    strings.
    """
    if isinstance(raw, bool):
        raise MoneyError(f"{field}: boolean is not a valid monetary value")
    if raw is None:
        raise MoneyError(f"{field}: missing or null monetary value")
    if isinstance(raw, float):
        raise MoneyError(f"{field}: float source not allowed, quote as a decimal string")
    s = str(raw).strip()
    if not s:
        raise MoneyError(f"{field}: empty monetary value")
    if s.lower() in _PLACEHOLDERS:
        raise MoneyError(f"{field}: placeholder value '{s}' is not a valid amount")
    try:
        d = Decimal(s)
    except InvalidOperation as exc:
        raise MoneyError(f"{field}: '{s}' is not a valid decimal") from exc
    if not d.is_finite():
        raise MoneyError(f"{field}: non-finite value not allowed")
    if d < 0:
        raise MoneyError(f"{field}: negative value not allowed")
    if d == 0 and not allow_zero:
        raise MoneyError(f"{field}: zero value not allowed")
    return d


def money_str(value: Decimal, places: int = DEFAULT_PLACES) -> str:
    """Serialize a Decimal as a fixed-point string, e.g. Decimal('0.05') -> '0.050'."""
    if isinstance(value, float):
        raise MoneyError("refusing to serialize a float as money")
    quant = Decimal(1).scaleb(-places)
    return str(value.quantize(quant))


def estimate_cost(units: int, unit_price: Any, *, field: str = "unit_price") -> Decimal:
    """Estimated cost for a number of billable units at an exact unit price."""
    if not isinstance(units, int) or isinstance(units, bool) or units < 0:
        raise MoneyError(f"{field}: units must be a non-negative integer")
    price = parse_money(unit_price, field=field, allow_zero=True)
    return (Decimal(units) * price)


class BudgetExceeded(RuntimeError):
    """Raised when an estimated cost would exceed the remaining allowance."""


def check_budget(estimated: Decimal, allowance: Any, spent: Any = "0") -> Decimal:
    """Fail closed if estimated + spent would exceed the allowance. Returns remaining."""
    allow = parse_money(allowance, field="allowance", allow_zero=True)
    already = parse_money(spent, field="spent", allow_zero=True)
    projected = already + estimated
    if projected > allow:
        raise BudgetExceeded(
            f"projected {money_str(projected)} exceeds allowance {money_str(allow)}"
        )
    return allow - projected
