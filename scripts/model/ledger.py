"""The cash-flow data model: a ledger of cash flow rows, independent of
any Tkinter or matplotlib code.

Every row has a permanent Row_ID, assigned once at insert time and never
reused or renumbered — this replaces using the pandas DataFrame's
positional index as an implicit identity key, which broke whenever a
reset_index() happened between when a row was selected and when it was
acted on.
"""
import pandas as pd

from scripts.model.errors import LedgerError

COLUMNS = ["Row_ID", "Period", "Cash Flow", "Color", "Series_ID", "Series_Name"]


class CashFlowLedger:
    """Owns the cash flow rows. No UI, no rendering, no color assignment
    (colors are passed in by the caller, which owns a ColorAssigner)."""

    def __init__(self):
        self._df = pd.DataFrame({
            "Row_ID": pd.Series(dtype="int64"),
            "Period": pd.Series(dtype="int64"),
            "Cash Flow": pd.Series(dtype="float64"),
            "Color": pd.Series(dtype="object"),
            "Series_ID": pd.Series(dtype="int64"),
            "Series_Name": pd.Series(dtype="object"),
        })
        self._next_row_id = 1
        self._next_series_id = 1

    def as_dataframe(self) -> pd.DataFrame:
        """A copy of the current rows. Callers must not mutate the ledger
        through this — it's a snapshot, not a live reference."""
        return self._df.copy()

    def is_empty(self) -> bool:
        return self._df.empty

    def reserve_series_id(self) -> int:
        """Allocate a new series id without adding any rows under it yet.
        Used by callers that need to know the id before building rows
        (e.g. Present Value's "create a new series" mode)."""
        series_id = self._next_series_id
        self._next_series_id += 1
        return series_id

    def add_single(self, period: int, amount: float, color, series_name: str) -> int:
        """Add one cash flow as its own new series. Returns the new series_id."""
        series_name = series_name.strip()
        if not series_name:
            raise LedgerError("Series name cannot be empty.")
        if amount == 0:
            raise LedgerError("Cash flow amount must be non-zero.")

        series_id = self.reserve_series_id()
        self._append_rows([(period, amount)], color=color, series_id=series_id, series_name=series_name)
        return series_id

    def add_uniform(self, start_period: int, amount: float, length: int, color, series_name: str) -> int:
        """Add `length` equal cash flows starting at start_period. Returns the new series_id."""
        series_name = series_name.strip()
        if not series_name:
            raise LedgerError("Series name cannot be empty.")
        if length < 1:
            raise LedgerError("Length of series must be at least 1.")

        series_id = self.reserve_series_id()
        entries = [(start_period + i, amount) for i in range(length)]
        self._append_rows(entries, color=color, series_id=series_id, series_name=series_name)
        return series_id

    def add_gradient(self, start_period: int, gradient_amount: float, length: int, color, series_name: str) -> int:
        """Add a gradient series: cash_flow(i) = gradient_amount * i, for
        i in 0..length-1, so the first value is always 0. Returns the new series_id."""
        series_name = series_name.strip()
        if not series_name:
            raise LedgerError("Series name cannot be empty.")
        if length < 1:
            raise LedgerError("Length of series must be at least 1.")

        series_id = self.reserve_series_id()
        entries = [(start_period + i, gradient_amount * i) for i in range(length)]
        self._append_rows(entries, color=color, series_id=series_id, series_name=series_name)
        return series_id

    def add_geometric(self, start_period: int, initial_value: float, length: int,
                      growth_rate_pct: float, color, series_name: str) -> int:
        """Add a geometric series: cash_flow(i) = initial_value * (1 +
        growth_rate_pct/100) ** i, for i in 0..length-1. Returns the new series_id."""
        series_name = series_name.strip()
        if not series_name:
            raise LedgerError("Series name cannot be empty.")
        if length < 1:
            raise LedgerError("Length of series must be at least 1.")
        if initial_value == 0:
            raise LedgerError("Initial value must be non-zero.")

        series_id = self.reserve_series_id()
        growth_rate = growth_rate_pct / 100.0
        entries = [
            (start_period + i, initial_value * ((1 + growth_rate) ** i))
            for i in range(length)
        ]
        self._append_rows(entries, color=color, series_id=series_id, series_name=series_name)
        return series_id

    def delete_rows(self, row_ids: list) -> int:
        """Delete rows by Row_ID. Unknown ids in the list are ignored as
        long as at least one given id still exists. Returns the number of
        rows actually deleted."""
        if not row_ids:
            raise LedgerError("No rows selected to delete.")

        existing_ids = set(self._df["Row_ID"])
        valid_ids = [r for r in row_ids if r in existing_ids]
        if not valid_ids:
            raise LedgerError("The selected rows no longer exist.")

        self._df = self._df[~self._df["Row_ID"].isin(valid_ids)].reset_index(drop=True)
        return len(valid_ids)

    def invert_series(self, series_ids: list) -> int:
        """Negate Cash Flow for every row in each given series. Unknown
        series ids are ignored as long as at least one still exists.
        Returns the number of series actually inverted."""
        if not series_ids:
            raise LedgerError("No series selected to invert.")

        existing_ids = set(self._df["Series_ID"])
        valid_ids = [s for s in series_ids if s in existing_ids]
        if not valid_ids:
            raise LedgerError("The selected series no longer exist.")

        mask = self._df["Series_ID"].isin(valid_ids)
        self._df.loc[mask, "Cash Flow"] = -self._df.loc[mask, "Cash Flow"]
        return len(valid_ids)

    def split_series(self, series_id: int, split_period: int, name_1: str, name_2: str, color_2) -> tuple:
        """Split a series into two at split_period: rows with Period <=
        split_period go to a new series named name_1 (keeping the original
        color), rows with Period > split_period go to a new series named
        name_2 with color_2. Returns (new_series_id_1, new_series_id_2)."""
        series_rows = self._df[self._df["Series_ID"] == series_id]
        if series_rows.empty:
            raise LedgerError("The series to split no longer exists.")
        if len(series_rows) <= 1:
            raise LedgerError("Cannot split a series with only one cash flow.")

        first_mask = (self._df["Series_ID"] == series_id) & (self._df["Period"] <= split_period)
        second_mask = (self._df["Series_ID"] == series_id) & (self._df["Period"] > split_period)
        if not first_mask.any() or not second_mask.any():
            raise LedgerError("Split point must leave cash flows on both sides.")

        original_color = series_rows.iloc[0]["Color"]
        series_id_1 = self.reserve_series_id()
        series_id_2 = self.reserve_series_id()

        self._df.loc[first_mask, "Series_ID"] = series_id_1
        self._df.loc[first_mask, "Series_Name"] = name_1
        self._df.loc[first_mask, "Color"] = pd.Series([original_color] * first_mask.sum(), index=self._df[first_mask].index)

        self._df.loc[second_mask, "Series_ID"] = series_id_2
        self._df.loc[second_mask, "Series_Name"] = name_2
        self._df.loc[second_mask, "Color"] = pd.Series([color_2] * second_mask.sum(), index=self._df[second_mask].index)

        return series_id_1, series_id_2

    def _append_rows(self, entries, *, color, series_id: int, series_name: str) -> list:
        """Append (period, cash_flow) pairs as new rows under one series.
        Returns the list of new Row_IDs, in order. The single mutation
        path every add_* method goes through, so there's one consistent
        way rows get added instead of each dialog hand-rolling its own
        pd.concat."""
        new_row_ids = []
        rows = []
        for period, cash_flow in entries:
            row_id = self._next_row_id
            self._next_row_id += 1
            new_row_ids.append(row_id)
            rows.append({
                "Row_ID": row_id,
                "Period": int(period),
                "Cash Flow": float(cash_flow),
                "Color": color,
                "Series_ID": series_id,
                "Series_Name": series_name,
            })
        new_df = pd.DataFrame(rows, columns=COLUMNS).astype({
            "Row_ID": "int64",
            "Period": "int64",
            "Cash Flow": "float64",
            "Series_ID": "int64",
        })
        self._df = pd.concat([self._df, new_df], ignore_index=True)
        return new_row_ids
