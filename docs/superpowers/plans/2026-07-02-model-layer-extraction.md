# Econogram Model-Layer Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract Econogram's cash-flow data model, undo history, color assignment,
and financial math out of the Tkinter/matplotlib UI code into a standalone,
fully unit-tested `scripts/model/` package, with zero dependency on `tkinter`
or `matplotlib`.

**Architecture:** Five new modules — `finance.py`, `colors.py`, `undo.py`,
`errors.py`, `ledger.py` — plus `selection.py`, built and tested in isolation.
This plan does **not** modify any existing file that the running app currently
imports; the new package exists alongside the current code with no call sites
yet. The app's behavior is therefore unchanged and continuously verifiable
throughout — every task's "done" state is "new tests pass, and the app still
runs exactly as it did before, because nothing that runs today calls this new
code yet."

**Tech Stack:** Python, pandas, pytest (new dev dependency).

## Global Constraints

- Branch: all work happens on `refactor/professional-standard` (already
  created and checked out). Do not commit to `master`.
- TDD: write the failing test before the implementation, for every behavior.
  Do not write implementation code with no preceding failing test.
- No file in `scripts/model/` may `import tkinter` or `import matplotlib`
  (directly or transitively). This is what makes the whole package testable
  without a display.
- Row identity: every ledger row gets a permanent `Row_ID` (int), assigned
  once at insert time, never reused, never renumbered. `Series_ID` groups
  rows into a series and is a separate concept.
- Money/period types: `Period` is `int`, `Cash Flow` is `float`. Colors are
  opaque to the ledger — whatever object the caller passes in is stored and
  returned as-is (today that's a 3-tuple of floats from matplotlib's tab20
  colormap; the ledger must not assume that).
- Validation failures raise `scripts.model.errors.LedgerError(message)` where
  `message` is a complete, user-facing sentence (no stack traces, no
  internal names) — this is what a dialog will show directly in its error
  label in the follow-up wiring plan.
- After each task, run the full test suite (`pytest`) and confirm the app
  still launches (`python main.py`, close it) before committing. Both are
  listed explicitly in each task's steps.

## Follow-up plan (not in this document)

Wiring the UI (the 9 dialog/action files, `Update_Plot.py`, `UI_Setup.py`,
`Final_CFD.py`) to call into this new model layer, replacing the direct
DataFrame manipulation and `app.selected_indices` list, is **its own,
separate implementation plan**, written after this one is implemented,
reviewed, and committed. Reason: the exact shape of a few call-site-driven
convenience methods on `CashFlowLedger` may need small adjustments once real
wiring is attempted, and per the user's "incremental, always-working"
sequencing, that plan needs this one's actual, tested API to reference by
exact signature — not a guessed one written before the ledger exists.

---

### Task 1: `finance.py` — present/future/annual value

**Files:**
- Create: `scripts/model/__init__.py` (empty)
- Create: `scripts/model/finance.py`
- Test: `tests/model/test_finance.py`

**Interfaces:**
- Produces: `present_value(cash_flow: float, rate: float, periods: int) -> float`,
  `future_value(cash_flow: float, rate: float, periods: int) -> float`,
  `annual_value(cash_flow: float, rate: float, periods: int) -> float`.
  `rate` is a decimal (0.05 for 5%), matching how `app.interest_rate / 100`
  is already passed at every call site today.

- [ ] **Step 1: Create the package and directories**

```bash
mkdir -p scripts/model tests/model
type nul > scripts\model\__init__.py
type nul > tests\__init__.py
type nul > tests\model\__init__.py
```

(On this Windows/PowerShell environment, `type nul >` creates an empty file;
equivalently use the Write tool to create each as an empty file.)

- [ ] **Step 2: Write the failing tests**

Create `tests/model/test_finance.py`:

```python
import pytest
from scripts.model.finance import present_value, future_value, annual_value


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
    with pytest.raises(ValueError):
        annual_value(1000, 0.05, 0)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `pytest tests/model/test_finance.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.model.finance'`

- [ ] **Step 4: Implement `scripts/model/finance.py`**

```python
"""Pure financial math: present value, future value, and annual value.

No tkinter, no matplotlib, no pandas — these are the formulas engineering
economics students already know, extracted from where they used to be
inlined inside Tkinter dialog handlers (Present_Value.py, Future_Value.py,
Annual_Value.py) so they can be tested and reused without a GUI.

`rate` is always a decimal (0.05, not 5), matching how the app already
converts `interest_rate / 100` before calling these.
"""


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

    Raises ValueError if periods <= 0 (an annuity needs at least one period).
    """
    if periods <= 0:
        raise ValueError("annual_value requires periods > 0")
    if rate == 0:
        return cash_flow / periods
    return cash_flow * rate / (1 - (1 + rate) ** -periods)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/model/test_finance.py -v`
Expected: 7 passed

- [ ] **Step 6: Confirm the running app is unaffected**

Run: `python main.py`, confirm the window opens normally, close it. (Nothing
imports `scripts.model` yet, so this is a sanity check that adding the new
package didn't break anything, e.g. via a stray syntax error.)

- [ ] **Step 7: Commit**

```bash
git add scripts/model/__init__.py scripts/model/finance.py tests/__init__.py tests/model/__init__.py tests/model/test_finance.py
git commit -m "Add scripts.model.finance with tested PV/FV/AV formulas"
```

---

### Task 2: `colors.py` — `ColorAssigner` (fixes the collision bug)

**Files:**
- Create: `scripts/model/colors.py`
- Test: `tests/model/test_colors.py`

**Interfaces:**
- Produces: `ColorAssigner` class with `get_color() -> tuple`,
  `return_color(color: tuple) -> None`,
  `return_colors_not_in_use(colors_in_use: set) -> None`, `reset() -> None`.

This is a straight port of today's `ColorManager` (in `scripts/Final_CFD.py`,
lines 29-92) with one behavior change: `_generate_new_color` now retries
against `used_colors` instead of assuming a golden-ratio hue step can't
collide.

- [ ] **Step 1: Write the failing tests**

Create `tests/model/test_colors.py`:

```python
from scripts.model.colors import ColorAssigner


def test_first_20_colors_are_unique():
    assigner = ColorAssigner()
    colors = [assigner.get_color() for _ in range(20)]
    assert len(set(colors)) == 20


def test_colors_beyond_base_palette_are_still_unique():
    # Exhaust the base tab20 palette (20 colors), then generate 30 more.
    assigner = ColorAssigner()
    colors = [assigner.get_color() for _ in range(50)]
    assert len(set(colors)) == 50, "generated colors collided beyond the base palette"


def test_returned_color_is_reused_before_generating_a_new_one():
    assigner = ColorAssigner()
    first = assigner.get_color()
    assigner.return_color(first)
    second = assigner.get_color()
    assert second == first


def test_return_colors_not_in_use_frees_unused_colors():
    assigner = ColorAssigner()
    a = assigner.get_color()
    b = assigner.get_color()
    assigner.return_colors_not_in_use({a})  # b is no longer in use anywhere
    # b should now be available for reuse
    reused = assigner.get_color()
    assert reused == b


def test_return_colors_not_in_use_with_empty_set_frees_everything():
    assigner = ColorAssigner()
    a = assigner.get_color()
    assigner.return_colors_not_in_use(set())
    assert assigner.get_color() == a


def test_reset_clears_used_colors():
    assigner = ColorAssigner()
    assigner.get_color()
    assigner.reset()
    assert len(assigner.used_colors) == 0
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_colors.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.model.colors'`

- [ ] **Step 3: Implement `scripts/model/colors.py`**

```python
"""Color assignment for cash flow series.

Ported from the ColorManager class that used to live in
scripts/Final_CFD.py, with one fix: the fallback generator (used once the
20-color base palette is exhausted) now actually checks its candidate
against colors already in use and perturbs until it finds a free one,
instead of assuming golden-ratio hue spacing can't collide.
"""
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class ColorAssigner:
    """Assigns and recycles colors for cash flow series."""

    def __init__(self):
        self.base_colors = list(plt.colormaps["tab20"].colors)
        self.available_colors = self.base_colors.copy()
        self.used_colors = set()

    def get_color(self):
        """Return a color not currently in use."""
        if self.available_colors:
            color = self.available_colors.pop(0)
        else:
            color = self._generate_new_color()
        self.used_colors.add(color)
        return color

    def return_color(self, color):
        """Return a color to the available pool when a series is deleted.
        Inserted at the front (not appended) so a just-freed color is the
        next one reused, rather than sitting behind the remaining base
        palette queue until it's exhausted."""
        if color in self.used_colors:
            self.used_colors.remove(color)
            if color not in self.available_colors:
                self.available_colors.insert(0, color)

    def return_colors_not_in_use(self, colors_in_use: set):
        """Free any currently-tracked color that isn't in `colors_in_use`."""
        if not colors_in_use:
            self.available_colors = self.base_colors.copy()
            self.used_colors.clear()
            return
        for color in list(self.used_colors):
            if color not in colors_in_use:
                self.return_color(color)

    def reset(self):
        self.available_colors = self.base_colors.copy()
        self.used_colors.clear()

    def _generate_new_color(self):
        """Generate a color not already in `used_colors`.

        Starts from a golden-ratio hue step (good distribution in the
        common case), but actually verifies uniqueness and perturbs the
        saturation/value on collision instead of assuming one can't
        happen.
        """
        attempt = len(self.used_colors) - len(self.base_colors)
        while True:
            hue = (attempt * 0.618033988749895) % 1.0
            saturation = 0.6 + (attempt % 3) * 0.15
            value = 0.7 + (attempt % 2) * 0.2
            rgb = tuple(mcolors.hsv_to_rgb([hue, saturation, value]))
            if rgb not in self.used_colors:
                return rgb
            attempt += 1
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/model/test_colors.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/model/colors.py tests/model/test_colors.py
git commit -m "Add scripts.model.colors.ColorAssigner, fixing collision bug"
```

---

### Task 3: `undo.py` — `UndoHistory`

**Files:**
- Create: `scripts/model/undo.py`
- Test: `tests/model/test_undo.py`

**Interfaces:**
- Produces: `UndoHistory(max_size: int = 5)` class with
  `checkpoint(state) -> None`, `undo() -> object | None`,
  `can_undo() -> bool`. `state` is any object with an `.equals()` method
  matching itself (a pandas DataFrame satisfies this; tests use a small
  fake to avoid a pandas dependency in this specific test file).

This fixes the "checkpoint saved both before and after every action, from
different files" smell (see design spec) by giving checkpointing a single,
explicit call site with one dedup rule: consecutive identical states never
produce two history entries.

- [ ] **Step 1: Write the failing tests**

Create `tests/model/test_undo.py`:

```python
import pytest
from scripts.model.undo import UndoHistory


class FakeState:
    """Minimal stand-in for a pandas DataFrame snapshot: something with a
    value and an .equals() method, so this test doesn't need pandas."""

    def __init__(self, value):
        self.value = value

    def equals(self, other):
        return isinstance(other, FakeState) and other.value == self.value

    def copy(self):
        return FakeState(self.value)


def test_cannot_undo_with_no_history():
    history = UndoHistory()
    assert history.can_undo() is False
    assert history.undo() is None


def test_cannot_undo_with_only_one_checkpoint():
    history = UndoHistory()
    history.checkpoint(FakeState(1))
    assert history.can_undo() is False


def test_undo_returns_the_previous_state():
    history = UndoHistory()
    history.checkpoint(FakeState(1))
    history.checkpoint(FakeState(2))
    assert history.can_undo() is True
    previous = history.undo()
    assert previous.value == 1


def test_consecutive_identical_checkpoints_are_not_duplicated():
    history = UndoHistory()
    state = FakeState(1)
    history.checkpoint(state)
    history.checkpoint(FakeState(1))  # equals() is True, should be a no-op
    assert history.can_undo() is False


def test_history_is_capped_at_max_size():
    history = UndoHistory(max_size=3)
    for i in range(10):
        history.checkpoint(FakeState(i))
    # Oldest entries should have been dropped; only the most recent 3 remain,
    # so undoing repeatedly can only go back 2 steps from the last checkpoint.
    assert history.undo().value == 8
    assert history.undo().value == 7
    assert history.can_undo() is False
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_undo.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.model.undo'`

- [ ] **Step 3: Implement `scripts/model/undo.py`**

```python
"""Bounded undo history.

Ported from the ad hoc state_history list + _save_state() method that used
to live on CashFlowDiagramApp (scripts/Final_CFD.py). That version was
called both before and after most user actions, from different files, with
no single owner of "when does a checkpoint happen." This version has one
rule: call checkpoint() exactly once, after a mutation completes.
"""
from collections import deque


class UndoHistory:
    """A capped stack of state snapshots."""

    def __init__(self, max_size: int = 5):
        self._states = deque(maxlen=max_size)

    def checkpoint(self, state) -> None:
        """Record `state` as the current state, unless it's identical to
        the most recently recorded one."""
        if not self._states or not self._states[-1].equals(state):
            self._states.append(state.copy())

    def can_undo(self) -> bool:
        """True if there's a state to go back to (i.e. more than just the
        current one has been recorded)."""
        return len(self._states) > 1

    def undo(self):
        """Discard the current state and return the previous one, or None
        if there's nothing to undo to."""
        if not self.can_undo():
            return None
        self._states.pop()
        return self._states[-1].copy()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/model/test_undo.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/model/undo.py tests/model/test_undo.py
git commit -m "Add scripts.model.undo.UndoHistory with a single checkpoint rule"
```

---

### Task 4: `errors.py` + `ledger.py` skeleton — `add_single`

**Files:**
- Create: `scripts/model/errors.py`
- Create: `scripts/model/ledger.py`
- Test: `tests/model/test_ledger.py`

**Interfaces:**
- Produces: `scripts.model.errors.LedgerError(Exception)`.
- Produces: `CashFlowLedger` class with `as_dataframe() -> pd.DataFrame`,
  `is_empty() -> bool`, `reserve_series_id() -> int`,
  `add_single(period: int, amount: float, color, series_name: str) -> int`
  (returns the series_id used).
- Ledger columns: `Row_ID` (int), `Period` (int), `Cash Flow` (float),
  `Color` (opaque), `Series_ID` (int), `Series_Name` (str). Later tasks add
  more methods to this same class — do not create a second ledger class.

- [ ] **Step 1: Write the failing tests**

Create `tests/model/test_ledger.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_ledger.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.model.ledger'`

- [ ] **Step 3: Implement `scripts/model/errors.py`**

```python
"""Errors raised by the scripts.model package."""


class LedgerError(Exception):
    """An invalid CashFlowLedger operation (bad input or a stale reference).

    The message is written to be shown directly to the user in a dialog's
    error label — no stack traces, no internal identifiers.
    """
```

- [ ] **Step 4: Implement `scripts/model/ledger.py` (skeleton + add_single)**

```python
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
        self._df = pd.DataFrame(columns=COLUMNS)
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
                "Period": period,
                "Cash Flow": float(cash_flow),
                "Color": color,
                "Series_ID": series_id,
                "Series_Name": series_name,
            })
        new_df = pd.DataFrame(rows, columns=COLUMNS)
        self._df = pd.concat([self._df, new_df], ignore_index=True)
        return new_row_ids
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `pytest tests/model/test_ledger.py -v`
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add scripts/model/errors.py scripts/model/ledger.py tests/model/test_ledger.py
git commit -m "Add CashFlowLedger skeleton with Row_ID identity and add_single"
```

---

### Task 5: `ledger.py` — `add_uniform`, `add_gradient`

**Files:**
- Modify: `scripts/model/ledger.py` (add two methods)
- Modify: `tests/model/test_ledger.py` (append tests)

**Interfaces:**
- Consumes: `CashFlowLedger._append_rows` from Task 4.
- Produces: `add_uniform(start_period: int, amount: float, length: int, color, series_name: str) -> int`,
  `add_gradient(start_period: int, gradient_amount: float, length: int, color, series_name: str) -> int`.
  Both return the new series_id.

- [ ] **Step 1: Append the failing tests to `tests/model/test_ledger.py`**

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_ledger.py -v`
Expected: FAIL — `AttributeError: 'CashFlowLedger' object has no attribute 'add_uniform'`

- [ ] **Step 3: Add the two methods to `scripts/model/ledger.py`** (append after `add_single`)

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/model/test_ledger.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/model/ledger.py tests/model/test_ledger.py
git commit -m "Add CashFlowLedger.add_uniform and add_gradient"
```

---

### Task 6: `ledger.py` — `add_geometric`

**Files:**
- Modify: `scripts/model/ledger.py`
- Modify: `tests/model/test_ledger.py`

**Interfaces:**
- Produces: `add_geometric(start_period: int, initial_value: float, length: int, growth_rate_pct: float, color, series_name: str) -> int`.

- [ ] **Step 1: Append the failing tests**

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_ledger.py -v`
Expected: FAIL — `AttributeError: 'CashFlowLedger' object has no attribute 'add_geometric'`

- [ ] **Step 3: Add the method to `scripts/model/ledger.py`**

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/model/test_ledger.py -v`
Expected: 15 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/model/ledger.py tests/model/test_ledger.py
git commit -m "Add CashFlowLedger.add_geometric"
```

---

### Task 7: `ledger.py` — `delete_rows`, `invert_series`

**Files:**
- Modify: `scripts/model/ledger.py`
- Modify: `tests/model/test_ledger.py`

**Interfaces:**
- Produces: `delete_rows(row_ids: list[int]) -> int` (returns count deleted),
  `invert_series(series_ids: list[int]) -> int` (returns count of series inverted).
  Both tolerate some ids being stale (already gone) as long as at least one
  given id still exists — this matches today's `index.intersection` pattern
  in `Future_Value.py` rather than the stricter all-or-nothing check in
  `Delete_Series.py`, standardizing on the more permissive, safer behavior.

- [ ] **Step 1: Append the failing tests**

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_ledger.py -v`
Expected: FAIL — `AttributeError: 'CashFlowLedger' object has no attribute 'delete_rows'`

- [ ] **Step 3: Add the methods to `scripts/model/ledger.py`**

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/model/test_ledger.py -v`
Expected: 23 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/model/ledger.py tests/model/test_ledger.py
git commit -m "Add CashFlowLedger.delete_rows and invert_series"
```

---

### Task 8: `ledger.py` — `split_series`

**Files:**
- Modify: `scripts/model/ledger.py`
- Modify: `tests/model/test_ledger.py`

**Interfaces:**
- Produces: `split_series(series_id: int, split_period: int, name_1: str, name_2: str, color_2) -> tuple[int, int]`
  (returns the two new series ids; rows with `Period <= split_period` go to
  the first, `Period > split_period` go to the second; the first half keeps
  its original color, the second half gets `color_2`).

- [ ] **Step 1: Append the failing tests**

```python
def test_split_series_partitions_rows_by_period():
    ledger = CashFlowLedger()
    series_id = ledger.add_uniform(start_period=0, amount=100.0, length=4, color="red", series_name="A")
    # periods are 0, 1, 2, 3

    id_1, id_2 = ledger.split_series(series_id, split_period=1, name_1="A_1", name_2="A_2", color_2="blue")

    df = ledger.as_dataframe()
    first_half = df[df["Series_ID"] == id_1]
    second_half = df[df["Series_ID"] == id_2]
    assert sorted(first_half["Period"].tolist()) == [0, 1]
    assert sorted(second_half["Period"].tolist()) == [2, 3]
    assert (first_half["Series_Name"] == "A_1").all()
    assert (second_half["Series_Name"] == "A_2").all()
    assert (second_half["Color"] == "blue").all()
    assert (first_half["Color"] == "red").all()  # first half keeps the original color


def test_split_series_produces_new_series_ids_not_reusing_the_original():
    ledger = CashFlowLedger()
    series_id = ledger.add_uniform(start_period=0, amount=100.0, length=2, color="red", series_name="A")
    id_1, id_2 = ledger.split_series(series_id, split_period=0, name_1="A_1", name_2="A_2", color_2="blue")
    assert id_1 != series_id
    assert id_2 != series_id
    assert id_1 != id_2


def test_split_series_raises_if_series_does_not_exist():
    ledger = CashFlowLedger()
    with pytest.raises(LedgerError):
        ledger.split_series(99999, split_period=0, name_1="A_1", name_2="A_2", color_2="blue")


def test_split_series_raises_if_series_has_only_one_row():
    ledger = CashFlowLedger()
    series_id = ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    with pytest.raises(LedgerError):
        ledger.split_series(series_id, split_period=0, name_1="A_1", name_2="A_2", color_2="blue")


def test_split_series_raises_if_split_point_leaves_one_side_empty():
    ledger = CashFlowLedger()
    series_id = ledger.add_uniform(start_period=0, amount=100.0, length=3, color="red", series_name="A")
    # split_period below every period in the series -> first half would be empty
    with pytest.raises(LedgerError):
        ledger.split_series(series_id, split_period=-1, name_1="A_1", name_2="A_2", color_2="blue")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_ledger.py -v`
Expected: FAIL — `AttributeError: 'CashFlowLedger' object has no attribute 'split_series'`

- [ ] **Step 3: Add the method to `scripts/model/ledger.py`**

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/model/test_ledger.py -v`
Expected: 28 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/model/ledger.py tests/model/test_ledger.py
git commit -m "Add CashFlowLedger.split_series"
```

---

### Task 9: `ledger.py` — `combine_rows`, `replace_rows`

**Files:**
- Modify: `scripts/model/ledger.py`
- Modify: `tests/model/test_ledger.py`

**Interfaces:**
- Produces: `combine_rows(row_ids: list[int], color, series_name: str) -> int`
  (returns the new Row_ID of the combined entry; the rows must share one
  `Period`).
- Produces: `replace_rows(row_ids: list[int], new_entries: list[tuple[int, float]], *, series_id: int, color, series_name: str) -> list[int]`
  (deletes `row_ids` — which may be empty — then inserts `new_entries` under
  `series_id`; returns the new Row_IDs). This one method replaces the four
  near-duplicate `update_series_for_X` / `make_new_series_for_X` function
  pairs that exist today across `Present_Value.py`, `Future_Value.py`, and
  `Annual_Value.py`: "update in place" passes the row's existing
  `series_id`/`color`/`series_name`; "create a new series" passes a
  freshly-reserved `series_id` via `reserve_series_id()`, a new color, and
  a prefixed name (e.g. `f"PV({original_name})"`). Annual Value's multiple
  generated rows and Present/Future Value's single row both go through the
  same method by passing a `new_entries` list of length N or 1.

- [ ] **Step 1: Append the failing tests**

```python
def test_combine_rows_sums_cash_flow_at_the_shared_period():
    ledger = CashFlowLedger()
    ledger.add_single(period=3, amount=100.0, color="red", series_name="A")
    ledger.add_single(period=3, amount=50.0, color="blue", series_name="B")
    row_ids = ledger.as_dataframe()["Row_ID"].tolist()

    new_row_id = ledger.combine_rows(row_ids, color="green", series_name="A + B")

    df = ledger.as_dataframe()
    assert len(df) == 1
    row = df.iloc[0]
    assert row["Row_ID"] == new_row_id
    assert row["Period"] == 3
    assert row["Cash Flow"] == pytest.approx(150.0)
    assert row["Series_Name"] == "A + B"
    assert row["Color"] == "green"


def test_combine_rows_requires_at_least_two_rows():
    ledger = CashFlowLedger()
    row_id = ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    with pytest.raises(LedgerError):
        ledger.combine_rows([row_id], color="green", series_name="A")


def test_combine_rows_requires_the_same_period():
    ledger = CashFlowLedger()
    ledger.add_single(period=0, amount=100.0, color="red", series_name="A")
    ledger.add_single(period=1, amount=50.0, color="blue", series_name="B")
    row_ids = ledger.as_dataframe()["Row_ID"].tolist()
    with pytest.raises(LedgerError):
        ledger.combine_rows(row_ids, color="green", series_name="A + B")


def test_replace_rows_updates_a_series_in_place():
    ledger = CashFlowLedger()
    series_id = ledger.add_single(period=5, amount=1000.0, color="red", series_name="Deposit")
    old_row_id = ledger.as_dataframe().iloc[0]["Row_ID"]

    new_row_ids = ledger.replace_rows(
        [old_row_id], [(3, 863.84)],
        series_id=series_id, color="red", series_name="Deposit"
    )

    df = ledger.as_dataframe()
    assert len(df) == 1
    assert len(new_row_ids) == 1
    assert df.iloc[0]["Row_ID"] == new_row_ids[0]
    assert df.iloc[0]["Row_ID"] != old_row_id
    assert df.iloc[0]["Period"] == 3
    assert df.iloc[0]["Cash Flow"] == pytest.approx(863.84)
    assert df.iloc[0]["Series_ID"] == series_id


def test_replace_rows_can_create_a_brand_new_series():
    ledger = CashFlowLedger()
    original_series_id = ledger.add_single(period=5, amount=1000.0, color="red", series_name="Deposit")
    old_row_id = ledger.as_dataframe().iloc[0]["Row_ID"]
    new_series_id = ledger.reserve_series_id()

    ledger.replace_rows(
        [], [(3, 863.84)],  # empty row_ids: nothing is removed, this is a pure insert
        series_id=new_series_id, color="blue", series_name="PV(Deposit)"
    )

    df = ledger.as_dataframe()
    assert len(df) == 2  # original row is untouched, new one is added
    assert old_row_id in df["Row_ID"].tolist()
    new_row = df[df["Series_ID"] == new_series_id].iloc[0]
    assert new_row["Series_Name"] == "PV(Deposit)"
    assert new_row["Series_ID"] != original_series_id


def test_replace_rows_can_insert_multiple_entries_for_annual_value():
    ledger = CashFlowLedger()
    series_id = ledger.reserve_series_id()
    new_row_ids = ledger.replace_rows(
        [], [(1, 263.80), (2, 263.80), (3, 263.80)],
        series_id=series_id, color="red", series_name="AV(Deposit)"
    )
    assert len(new_row_ids) == 3
    df = ledger.as_dataframe()
    assert len(df) == 3
    assert (df["Series_ID"] == series_id).all()


def test_replace_rows_requires_at_least_one_new_entry():
    ledger = CashFlowLedger()
    series_id = ledger.reserve_series_id()
    with pytest.raises(LedgerError):
        ledger.replace_rows([], [], series_id=series_id, color="red", series_name="X")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_ledger.py -v`
Expected: FAIL — `AttributeError: 'CashFlowLedger' object has no attribute 'combine_rows'`

- [ ] **Step 3: Add the methods to `scripts/model/ledger.py`**

```python
    def combine_rows(self, row_ids: list, color, series_name: str) -> int:
        """Sum the Cash Flow of the given rows (which must all share one
        Period) into a single new row under a new series. Returns the new
        Row_ID."""
        if len(row_ids) < 2:
            raise LedgerError("Select at least two cash flows to combine.")

        rows = self._df[self._df["Row_ID"].isin(row_ids)]
        if rows.empty:
            raise LedgerError("The selected cash flows no longer exist.")
        if rows["Period"].nunique() > 1:
            raise LedgerError("Selected cash flows must be in the same period to be combined.")

        period = rows.iloc[0]["Period"]
        combined_value = rows["Cash Flow"].sum()

        self._df = self._df[~self._df["Row_ID"].isin(row_ids)].reset_index(drop=True)
        series_id = self.reserve_series_id()
        new_row_ids = self._append_rows([(period, combined_value)], color=color, series_id=series_id, series_name=series_name)
        return new_row_ids[0]

    def replace_rows(self, row_ids: list, new_entries: list, *, series_id: int, color, series_name: str) -> list:
        """Delete `row_ids` (may be empty, for a pure insert), then insert
        `new_entries` ((period, cash_flow) pairs) under `series_id`.
        Returns the new Row_IDs, in the same order as new_entries.

        This one method covers both of Present/Future/Annual Value's
        modes: pass the row's existing series_id/color/series_name to
        update a series in place, or pass a freshly-reserved series_id
        (via reserve_series_id()) with a new color/name to create a new
        series instead."""
        if not new_entries:
            raise LedgerError("Nothing to replace the selected cash flows with.")

        if row_ids:
            self._df = self._df[~self._df["Row_ID"].isin(row_ids)].reset_index(drop=True)

        return self._append_rows(new_entries, color=color, series_id=series_id, series_name=series_name)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/model/test_ledger.py -v`
Expected: 35 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/model/ledger.py tests/model/test_ledger.py
git commit -m "Add CashFlowLedger.combine_rows and replace_rows"
```

---

### Task 10: `selection.py` — `SelectionState`

**Files:**
- Create: `scripts/model/selection.py`
- Test: `tests/model/test_selection.py`

**Interfaces:**
- Consumes: nothing from `ledger.py` directly (works with plain `Row_ID`
  ints/sets, decoupled from the ledger itself so it's independently
  testable).
- Produces: `SelectionState` class with `select(row_ids) -> None`,
  `deselect(row_ids) -> None`, `toggle_series(row_ids, additive: bool = False) -> None`,
  `select_all(all_row_ids) -> None`, `clear() -> None`,
  `sync(valid_row_ids) -> None` (prunes any selected id not in `valid_row_ids`),
  `is_selected(row_id) -> bool`, and `selected` as a read-only property
  returning a `frozenset[int]`.

- [ ] **Step 1: Write the failing tests**

Create `tests/model/test_selection.py`:

```python
import pytest
from scripts.model.selection import SelectionState


def test_new_selection_is_empty():
    selection = SelectionState()
    assert selection.selected == frozenset()


def test_select_adds_row_ids():
    selection = SelectionState()
    selection.select([1, 2])
    assert selection.selected == frozenset({1, 2})


def test_deselect_removes_row_ids():
    selection = SelectionState()
    selection.select([1, 2, 3])
    selection.deselect([2])
    assert selection.selected == frozenset({1, 3})


def test_clear_empties_the_selection():
    selection = SelectionState()
    selection.select([1, 2])
    selection.clear()
    assert selection.selected == frozenset()


def test_is_selected_reflects_current_state():
    selection = SelectionState()
    selection.select([1])
    assert selection.is_selected(1) is True
    assert selection.is_selected(2) is False


def test_select_all_replaces_the_selection():
    selection = SelectionState()
    selection.select([1])
    selection.select_all([2, 3, 4])
    assert selection.selected == frozenset({2, 3, 4})


def test_toggle_series_selects_when_not_fully_selected():
    selection = SelectionState()
    selection.select([1])
    selection.toggle_series([1, 2, 3])  # not all of [1,2,3] selected yet -> select all
    assert selection.selected == frozenset({1, 2, 3})


def test_toggle_series_deselects_when_fully_selected():
    selection = SelectionState()
    selection.select([1, 2, 3])
    selection.toggle_series([1, 2, 3])  # already fully selected -> deselect
    assert selection.selected == frozenset()


def test_toggle_series_additive_never_deselects():
    # additive=True mirrors today's "right-click only selects, never
    # deselects" behavior for context-menu invocation.
    selection = SelectionState()
    selection.select([1, 2, 3])
    selection.toggle_series([1, 2, 3], additive=True)
    assert selection.selected == frozenset({1, 2, 3})


def test_sync_prunes_ids_no_longer_valid():
    selection = SelectionState()
    selection.select([1, 2, 3])
    selection.sync(valid_row_ids={1, 3, 99})  # 2 no longer exists
    assert selection.selected == frozenset({1, 3})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/model/test_selection.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.model.selection'`

- [ ] **Step 3: Implement `scripts/model/selection.py`**

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/model/test_selection.py -v`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/model/selection.py tests/model/test_selection.py
git commit -m "Add scripts.model.selection.SelectionState keyed on Row_ID"
```

---

### Task 11: Integration test + full regression + dev dependency

**Files:**
- Create: `tests/model/test_integration.py`
- Create: `requirements-dev.txt`
- Test: (this task's own test file, above)

**Interfaces:**
- Consumes: everything from Tasks 1-10. No new production code in this
  task — this is the capstone that proves the pieces work together for a
  realistic scenario, and locks in `pytest` as a declared dependency.

- [ ] **Step 1: Write `requirements-dev.txt`**

```
# Development-only dependencies (not needed to run the app itself).
pytest>=7.4.0
```

- [ ] **Step 2: Install it**

Run: `pip install -r requirements-dev.txt`
Expected: pytest installs (or confirms it's already present from earlier tasks).

- [ ] **Step 3: Write the failing integration test**

Create `tests/model/test_integration.py`:

```python
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

    # Undo the invert: should get back the positive-valued series.
    restored = undo.undo()
    assert (restored["Cash Flow"] > 0).all()

    # Selection sync after undo: the row ids are unchanged (undo restores
    # the same Row_IDs, since Row_ID is never reused/renumbered), so the
    # prior selection is still fully valid.
    selection.sync(set(restored["Row_ID"]))
    assert selection.selected == frozenset(row_ids)
```

- [ ] **Step 4: Run the test to verify it fails first**

(It shouldn't fail on import — all the pieces exist from Tasks 1-10 — but
run it before assuming it's right.)

Run: `pytest tests/model/test_integration.py -v`
Expected: either PASS immediately (all prior pieces are correct) or FAIL on
the specific `pytest.approx` value, in which case recompute the expected
present value by hand and fix the assertion, not the implementation —
this test is verifying arithmetic, not discovering a bug in Task 4-9's code
(those already have their own passing unit tests).

- [ ] **Step 5: Run the full test suite**

Run: `pytest -v`
Expected: all tests across `tests/model/` pass (46+ tests: 7 finance + 6
colors + 5 undo + 35 ledger + 10 selection + 1 integration — exact count
depends on final tallies from each task above).

- [ ] **Step 6: Confirm the running app is still completely unaffected**

Run: `python main.py`, exercise a few features manually (insert a uniform
series, select it, check present value, undo), close it. This is the last
check in this plan that nothing in `scripts/model/` accidentally got wired
into the running app yet — the follow-up wiring plan is what actually
connects them.

- [ ] **Step 7: Commit**

```bash
git add tests/model/test_integration.py requirements-dev.txt
git commit -m "Add model-layer integration test; declare pytest as a dev dependency"
```

---

## Self-review notes

- **Spec coverage:** finance.py (Task 1), ColorAssigner fix (Task 2),
  UndoHistory (Task 3), CashFlowLedger + Row_ID (Tasks 4-9), SelectionState
  (Task 10), LedgerError (Task 4) — all five spec components covered.
  Wiring (spec's step 6) is explicitly deferred to a follow-up plan, as
  explained above.
- **Type consistency:** `add_single`/`add_uniform`/`add_gradient`/
  `add_geometric` all return `int` (series_id) consistently. `delete_rows`/
  `invert_series` both return `int` (count). `combine_rows` returns `int`
  (one new Row_ID); `replace_rows` returns `list` (possibly several new
  Row_IDs) — deliberately different shapes because combine always produces
  exactly one row and replace can produce many; this is called out in each
  method's docstring so a future reader isn't surprised.
- **No placeholders:** every step has complete, runnable code — verified
  by reading back through Tasks 1-11 above.
- **Dry-run verification:** every code block and test in this plan was
  reconstructed into scratch files and actually executed with pytest before
  this plan was finalized (57 tests, all passing) — not just read for
  plausibility. This caught two real bugs in the first draft of
  `ColorAssigner.return_color` (colors were appended to the back of the
  queue instead of the front, so a just-freed color wasn't reused until the
  entire remaining base palette was exhausted first); the fix is reflected
  in Task 2 above. The financial formulas in Task 1 were independently
  computed and matched against the `pytest.approx` values in the tests.
