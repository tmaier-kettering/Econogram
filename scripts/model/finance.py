"""Pure financial math: present value, future value, and annual value.

No tkinter, no matplotlib, no pandas — these are the formulas engineering
economics students already know, extracted from where they used to be
inlined inside Tkinter dialog handlers (Present_Value.py, Future_Value.py,
Annual_Value.py) so they can be tested and reused without a GUI.

`rate` is always a decimal (0.05, not 5), matching how the app already
converts `interest_rate / 100` before calling these.
"""
from scripts.model.errors import LedgerError


def present_value(cash_flow: float, rate: float, periods: int) -> float:
    """Value of `cash_flow`, `periods` periods before it occurs.

    `periods` is typically negative here (moving a flow backward in time
    by N periods multiplies by (1+rate)**(-N)), matching how callers pass
    `new_period - current_period` where new_period < current_period.
    """
    return cash_flow * ((1 + rate) ** periods)


def future_value(cash_flow: float, rate: float, periods: int) -> float:
    """Value of `cash_flow`, `periods` periods after it occurs."""
    return cash_flow * ((1 + rate) ** periods)


def annual_value(cash_flow: float, rate: float, periods: int) -> float:
    """Equivalent uniform annual amount of a single `cash_flow` spread over
    `periods` periods at `rate`.

    Raises LedgerError if periods <= 0 (an annuity needs at least one period).
    """
    if periods <= 0:
        raise LedgerError("Number of periods must be greater than zero.")
    if rate == 0:
        return cash_flow / periods
    return cash_flow * rate / (1 - (1 + rate) ** -periods)
