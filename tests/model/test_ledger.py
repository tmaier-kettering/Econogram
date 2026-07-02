import pytest
from scripts.model.ledger import CashFlowLedger
from scripts.model.errors import LedgerError


def test_new_ledger_is_empty():
    ledger = CashFlowLedger()
    assert ledger.is_empty() is True
    assert ledger.as_dataframe().empty


def test_reserve_series_id_returns_increasing_unique_ids():
    ledger = CashFlowLedger()
    first = ledger.reserve_series_id()
    second = ledger.reserve_series_id()
    assert second > first


def test_add_single_creates_one_row():
    ledger = CashFlowLedger()
    series_id = ledger.add_single(period=2, amount=-500.0, color="red", series_name="Fee")
    df = ledger.as_dataframe()
    assert len(df) == 1
    row = df.iloc[0]
    assert row["Period"] == 2
    assert row["Cash Flow"] == -500.0
    assert row["Color"] == "red"
    assert row["Series_Name"] == "Fee"
    assert row["Series_ID"] == series_id
    assert ledger.is_empty() is False


def test_add_single_assigns_unique_increasing_row_ids():
    ledger = CashFlowLedger()
    ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    ledger.add_single(period=1, amount=200.0, color="blue", series_name="B")
    df = ledger.as_dataframe()
    row_ids = df["Row_ID"].tolist()
    assert row_ids[0] != row_ids[1]
    assert row_ids[1] > row_ids[0]


def test_add_single_with_empty_series_name_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.add_single(period=0, amount=100.0, color="red", series_name="")


def test_add_single_with_zero_amount_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.add_single(period=0, amount=0.0, color="red", series_name="A")


def test_as_dataframe_returns_a_copy_not_a_live_reference():
    ledger = CashFlowLedger()
    ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    snapshot = ledger.as_dataframe()
    snapshot.iloc[0, snapshot.columns.get_loc("Cash Flow")] = 999.0
    assert ledger.as_dataframe().iloc[0]["Cash Flow"] == 100.0


def test_dataframe_columns_have_correct_dtypes():
    ledger = CashFlowLedger()
    ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    ledger.add_single(period=1, amount=-200.0, color="blue", series_name="B")
    df = ledger.as_dataframe()
    assert df["Row_ID"].dtype == "int64"
    assert df["Period"].dtype == "int64"
    assert df["Cash Flow"].dtype == "float64"
    assert df["Series_ID"].dtype == "int64"
