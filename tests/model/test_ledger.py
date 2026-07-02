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


def test_add_uniform_creates_length_rows_with_constant_amount():
    ledger = CashFlowLedger()
    series_id = ledger.add_uniform(start_period=0, amount=1000.0, length=3, color="red", series_name="Rent")
    df = ledger.as_dataframe()
    assert len(df) == 3
    assert df["Period"].tolist() == [0, 1, 2]
    assert df["Cash Flow"].tolist() == [1000.0, 1000.0, 1000.0]
    assert (df["Series_ID"] == series_id).all()


def test_add_uniform_with_zero_length_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.add_uniform(start_period=0, amount=1000.0, length=0, color="red", series_name="Rent")


def test_add_uniform_with_negative_length_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.add_uniform(start_period=0, amount=1000.0, length=-1, color="red", series_name="Rent")


def test_add_gradient_first_value_is_zero_then_increases_by_gradient_amount():
    ledger = CashFlowLedger()
    series_id = ledger.add_gradient(start_period=5, gradient_amount=200.0, length=3, color="blue", series_name="Raise")
    df = ledger.as_dataframe()
    assert df["Period"].tolist() == [5, 6, 7]
    assert df["Cash Flow"].tolist() == [0.0, 200.0, 400.0]
    assert (df["Series_ID"] == series_id).all()


def test_add_gradient_with_zero_length_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.add_gradient(start_period=0, gradient_amount=200.0, length=0, color="blue", series_name="Raise")


def test_add_geometric_grows_by_percentage_each_period():
    ledger = CashFlowLedger()
    series_id = ledger.add_geometric(
        start_period=0, initial_value=1000.0, length=3, growth_rate_pct=10.0,
        color="green", series_name="Sales"
    )
    df = ledger.as_dataframe()
    assert df["Period"].tolist() == [0, 1, 2]
    cash_flows = df["Cash Flow"].tolist()
    assert cash_flows[0] == pytest.approx(1000.0)
    assert cash_flows[1] == pytest.approx(1100.0)
    assert cash_flows[2] == pytest.approx(1210.0)
    assert (df["Series_ID"] == series_id).all()


def test_add_geometric_with_zero_initial_value_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.add_geometric(
            start_period=0, initial_value=0.0, length=3, growth_rate_pct=10.0,
            color="green", series_name="Sales"
        )


def test_add_geometric_with_zero_length_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.add_geometric(
            start_period=0, initial_value=1000.0, length=0, growth_rate_pct=10.0,
            color="green", series_name="Sales"
        )


def test_delete_rows_removes_only_the_given_rows():
    ledger = CashFlowLedger()
    ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    series_id_b = ledger.add_single(period=1, amount=200.0, color="blue", series_name="B")
    row_to_delete = ledger.as_dataframe().iloc[0]["Row_ID"]

    deleted_count = ledger.delete_rows([row_to_delete])

    assert deleted_count == 1
    remaining = ledger.as_dataframe()
    assert len(remaining) == 1
    assert remaining.iloc[0]["Series_ID"] == series_id_b


def test_delete_rows_ignores_stale_ids_but_deletes_valid_ones():
    ledger = CashFlowLedger()
    ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    real_row_id = ledger.as_dataframe().iloc[0]["Row_ID"]

    deleted_count = ledger.delete_rows([real_row_id, 99999])

    assert deleted_count == 1
    assert ledger.is_empty()


def test_delete_rows_with_no_valid_ids_raises():
    ledger = CashFlowLedger()
    ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    with pytest.raises(LedgerError):
        ledger.delete_rows([99999])


def test_delete_rows_with_empty_list_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.delete_rows([])


def test_invert_series_negates_every_row_in_the_series():
    ledger = CashFlowLedger()
    series_id = ledger.add_uniform(start_period=0, amount=500.0, length=2, color="red", series_name="A")

    inverted_count = ledger.invert_series([series_id])

    assert inverted_count == 1
    assert ledger.as_dataframe()["Cash Flow"].tolist() == [-500.0, -500.0]


def test_invert_series_twice_returns_to_original_sign():
    ledger = CashFlowLedger()
    series_id = ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    ledger.invert_series([series_id])
    ledger.invert_series([series_id])
    assert ledger.as_dataframe().iloc[0]["Cash Flow"] == 100.0


def test_invert_series_with_empty_list_raises():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.invert_series([])


def test_invert_series_ignores_unknown_series_ids():
    ledger = CashFlowLedger()
    series_id = ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    inverted_count = ledger.invert_series([series_id, 99999])
    assert inverted_count == 1
