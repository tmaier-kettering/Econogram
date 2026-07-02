import pytest
from scripts.model.finance import present_value, future_value, annual_value
from scripts.model.errors import LedgerError


def test_present_value_matches_textbook_example():
    # $1000 three periods in the future at 5% -> ~$863.84 today
    result = present_value(1000, 0.05, -3)
    assert result == pytest.approx(863.8376, abs=0.001)


def test_present_value_zero_periods_is_unchanged():
    assert present_value(500, 0.08, 0) == pytest.approx(500.0)


def test_future_value_matches_textbook_example():
    # $1000 today, moved 3 periods forward at 5% -> ~$1157.63
    result = future_value(1000, 0.05, 3)
    assert result == pytest.approx(1157.625, abs=0.001)


def test_future_value_zero_periods_is_unchanged():
    assert future_value(500, 0.08, 0) == pytest.approx(500.0)


def test_annual_value_matches_textbook_example():
    # $1000 present value, 5 periods, 10% -> A = 1000 * A/P(10%,5) ~= $263.80
    result = annual_value(1000, 0.10, 5)
    assert result == pytest.approx(263.7975, abs=0.001)


def test_annual_value_zero_interest_rate_divides_evenly():
    # No interest: annual value is just the amount spread evenly.
    assert annual_value(1000, 0.0, 4) == pytest.approx(250.0)


def test_annual_value_raises_for_zero_periods():
    with pytest.raises(LedgerError):
        annual_value(1000, 0.05, 0)
