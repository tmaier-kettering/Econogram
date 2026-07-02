"""End-to-end test of the model layer working together, without any
Tkinter or matplotlib involved: build a small cash flow problem, select
some of it, invert, undo, and check present value math against the ledger
- exactly what a user does through the UI today, minus the UI."""
import pytest
from scripts.model.ledger import CashFlowLedger
from scripts.model.selection import SelectionState
from scripts.model.undo import UndoHistory
from scripts.model.colors import ColorAssigner
from scripts.model.finance import present_value


def test_worked_example_uniform_series_present_value_and_undo():
    ledger = CashFlowLedger()
    selection = SelectionState()
    undo = UndoHistory()
    colors = ColorAssigner()

    undo.checkpoint(ledger.as_dataframe())

    # Add a 3-period, $1000/period uniform series starting at period 1.
    color = colors.get_color()
    series_id = ledger.add_uniform(start_period=1, amount=1000.0, length=3, color=color, series_name="Deposits")
    undo.checkpoint(ledger.as_dataframe())

    df = ledger.as_dataframe()
    assert len(df) == 3

    # Select the whole series (as clicking any of its bars, or its legend
    # entry, would do) and invert it.
    row_ids = df["Row_ID"].tolist()
    selection.select_all(row_ids)
    inverted = ledger.invert_series([series_id])
    assert inverted == 1
    assert (ledger.as_dataframe()["Cash Flow"] < 0).all()
    undo.checkpoint(ledger.as_dataframe())

    # Compute the present value of the (now-negative) series at period 0,
    # 5% interest, the way Present_Value.py's popup_present_value would:
    # combined_value = sum(present_value(cash_flow, rate, new_period - current_period))
    rate = 0.05
    new_period = 0
    combined_value = sum(
        present_value(row["Cash Flow"], rate, new_period - row["Period"])
        for _, row in ledger.as_dataframe().iterrows()
    )
    assert combined_value == pytest.approx(-2723.248, abs=0.01)

    # Undo the invert: should get back the positive-valued series. Feed the
    # snapshot back into the ledger via restore() — the point of this test
    # is that the pieces work *together*, so it's not enough to just check
    # the raw DataFrame undo() handed back in isolation.
    restored = undo.undo()
    assert (restored["Cash Flow"] > 0).all()

    ledger.restore(restored)
    assert (ledger.as_dataframe()["Cash Flow"] > 0).all()

    # Selection sync after undo: the row ids are unchanged (undo restores
    # the same Row_IDs, since Row_ID is never reused/renumbered), so the
    # prior selection is still fully valid.
    selection.sync(set(ledger.as_dataframe()["Row_ID"]))
    assert selection.selected == frozenset(row_ids)
