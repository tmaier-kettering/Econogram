"""Tracks which cash flow rows are currently selected, by Row_ID.

Deliberately independent of CashFlowLedger: it only ever deals in Row_ID
ints, never DataFrame positional indices, which is what makes selection
survive ledger mutations that renumber rows (deletes, splits, combines)
instead of silently pointing at the wrong row afterward.
"""


class SelectionState:
    def __init__(self):
        self._selected = set()

    @property
    def selected(self) -> frozenset:
        return frozenset(self._selected)

    def is_selected(self, row_id) -> bool:
        return row_id in self._selected

    def select(self, row_ids) -> None:
        self._selected.update(row_ids)

    def deselect(self, row_ids) -> None:
        self._selected.difference_update(row_ids)

    def clear(self) -> None:
        self._selected.clear()

    def select_all(self, all_row_ids) -> None:
        self._selected = set(all_row_ids)

    def toggle_series(self, row_ids, additive: bool = False) -> None:
        """If every id in row_ids is already selected, deselect them all
        (unless additive=True, which only ever adds — used for right-click,
        which should select without deselecting an already-selected series)."""
        row_ids = list(row_ids)
        fully_selected = all(r in self._selected for r in row_ids)
        if fully_selected:
            if not additive:
                self._selected.difference_update(row_ids)
        else:
            self._selected.update(row_ids)

    def sync(self, valid_row_ids) -> None:
        """Drop any selected id that isn't in valid_row_ids. Call this
        after any ledger mutation that might have removed selected rows."""
        self._selected.intersection_update(valid_row_ids)
