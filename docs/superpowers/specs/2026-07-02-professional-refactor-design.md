# Econogram Professional-Standard Refactor — Design

## Background

Econogram is a Tkinter + matplotlib desktop app for building engineering-economics
cash flow diagrams. It was written by novice programmers and, while functional,
has architecture, error-handling, and consistency problems typical of code
written without a data/UI separation in mind. There is currently zero automated
test coverage anywhere in the repository.

This document scopes a refactor to bring the codebase to a professional
standard, focused on architecture, error handling, and test coverage.

## Findings (what's actually wrong)

**Architecture:** There is no separation between data, business logic, and UI.
Every dialog/action module (`Uniform_Series.py`, `Present_Value.py`, etc.) reads
and mutates `app.cash_flows` (a raw pandas DataFrame) directly. `CashFlowDiagramApp`
is a god object holding Tkinter widgets, undo history, color-assignment state,
and the data model together. Financial math is inlined inside functions that
also drive Tkinter dialogs and mutate the DataFrame, so almost nothing can be
unit-tested without a live Tk root and a rendered matplotlib canvas.

**Correctness smells that follow from that architecture:**
- Selection (`app.selected_indices`) is tracked as raw DataFrame positional
  indices, but several operations call `.reset_index(drop=True)` after
  mutating, which can silently invalidate stored indices.
- `_save_state()` (undo) is called both before and after most actions, from
  different files, in a way that reads as defensive/uncertain rather than
  deliberate — it happens to still work today only because of a dedup guard.
- `ColorManager`'s fallback color generator (used once the base 20-color
  palette is exhausted) does not check its generated color against colors
  already in use; it just assumes golden-ratio hue spacing won't collide.
- DataFrame mutation style is inconsistent: some call sites use
  `df.drop(..., inplace=True)`, others use `df = df.drop(...).reset_index(...)`
  for the same kind of operation, depending on which file you're in.

**Tooling gap:** no tests, no linter config, no pinned dependency versions, no CI.

**Naming:** module files use `Capitalized_Snake_Case.py` (e.g. `Uniform_Series.py`),
which isn't PEP8. Real but cosmetic, and renaming touches every import in the
codebase.

## Scope decision

In scope: **architecture extraction + the correctness fixes it surfaces + test
coverage for the new model layer.**

Explicitly deferred (not part of this refactor unless separately requested):
- Tooling/CI setup (linter config, pinned versions, GitHub Actions).
- The module-renaming cleanup (`Uniform_Series.py` → `uniform_series.py`).

These were flagged during design review as real but lower-priority; revisit
after the architecture work lands.

## Architecture

New `scripts/model/` package. None of these modules import `tkinter` or
`matplotlib` — that's the point, it's what makes them unit-testable in
isolation.

- **`ledger.py` — `CashFlowLedger`.** Owns the `cash_flows` DataFrame. One
  method per mutation that exists today: `add_single`, `add_uniform`,
  `add_gradient`, `add_geometric`, `delete`, `invert`, `split`, `combine`,
  `clear`, plus a read-only `as_dataframe()` for rendering. Every row gets a
  permanent **`Row_ID`** assigned at insert time — monotonically increasing,
  never reused or reset — distinct from `Series_ID` (groups rows into a
  series) and distinct from the DataFrame's positional index (which shifts
  under `reset_index`). This is the structural fix for the selection-fragility
  smell.
- **`selection.py` — `SelectionState`.** Holds selected `Row_ID`s (not
  positional indices). `select` / `deselect` / `toggle_series` / `select_all`
  / `clear`, plus `sync(valid_row_ids)` to prune stale ids after a ledger
  mutation.
- **`undo.py` — `UndoHistory`.** `collections.deque(maxlen=5)` of ledger
  snapshots. One clear rule for when a checkpoint is taken (after a mutation
  completes), replacing the current scattered pre/post calls.
- **`colors.py` — `ColorAssigner`.** Same role as today's `ColorManager`,
  fixed so the fallback generator checks the candidate color against colors
  already in use and perturbs on collision instead of assuming one won't
  happen.
- **`finance.py`.** Pure functions: `present_value`, `future_value`,
  `annual_value`. Extracts the Annual Value formula that's currently inlined
  in `popup_annual_value`, alongside the PV/FV functions that already exist
  as free functions today.

## Data flow

A UI dialog collects raw input (Entry widget strings), converts/validates
types, then calls exactly one `CashFlowLedger` method (e.g.
`ledger.add_uniform(...)`). On success, a single coordinator method —
`app.record_change()` — does everything that today is hand-copied across
9 files: take an undo checkpoint, prune the selection to still-valid
`Row_ID`s, trigger a re-render, close the dialog, show the toast. This
replaces the current pattern where each dialog reimplements its own version
of "what happens after a successful edit."

## Error handling

A `LedgerError` exception type replaces the current mix of bare `ValueError`s
with hand-parsed message strings and broad `except Exception` blocks that
quietly swallow real bugs. Business-rule violations (empty series name,
zero-length series, "can't move a cash flow forward in time with Present
Value") become explicit raises from the ledger/finance layer. The UI layer's
job shrinks to: catch `LedgerError`, show the message in the inline error
label already built in `DialogKit`; anything else propagates as a real
traceback during development instead of being masked by a catch-all.

## Testing strategy

New `tests/` directory using `pytest` (added as a dev dependency). Coverage
targets the model layer, since that's where the actual risk lives:

- **`CashFlowLedger`**: construct in isolation, add every series type, assert
  resulting rows/values, test delete/invert/split/combine, assert bad input
  raises `LedgerError` with the right message. No Tk root, no matplotlib
  canvas.
- **`SelectionState`**: select/deselect/toggle/prune, in isolation.
- **`UndoHistory`**: checkpoint/undo/cap-at-5 behavior.
- **`ColorAssigner`**: exhaust the base palette, assert no collisions across
  N generated colors beyond it — a property-style test that would have
  caught the current bug.
- **`finance.py`**: PV/FV/AV against known textbook values, plus the
  zero-interest-rate edge case.
- **`DialogKit` validators** (`validate_currency`, `validate_integer`,
  `validate_series_name`): already pure string→bool functions, cheap to
  cover, gate all user input.

Explicitly out of scope: automated GUI tests (mocking Tkinter dialog submit
handlers, simulating matplotlib mouse events for coverage purposes). The UI
layer stays verified the way it has been through the polish phases — manual
runs with screenshot checks — since after this refactor dialogs become thin
glue (collect input → call one ledger method → `app.record_change()`), and
that glue is not where the risk lives.

## Sequencing

Confirmed with the user: **incremental, always-working.** The app stays fully
functional and manually verified after every step; no big-bang cutover.
Intended order (refined further in the implementation plan):

1. `finance.py` extraction — lowest risk, already semi-separated, immediate
   test value.
2. `ColorAssigner` fix — isolated, low blast radius.
3. `UndoHistory` — isolated, low blast radius, fixes the double-save smell.
4. `CashFlowLedger` + stable `Row_ID` — highest value, touches the most call
   sites; the big one.
5. `SelectionState` — depends on `Row_ID` existing.
6. Wire UI dialogs to the new ledger/selection/undo, removing the duplicated
   post-mutation boilerplate from each dialog file.

## Process notes

- All refactor work happens on branch `refactor/professional-standard`
  (created from `master`), per explicit user instruction.
- Work proceeds via TDD: no refactor of code lacking test coverage without
  adding tests first, per user instruction. Code review between tasks;
  nothing is considered done until verified working, not just changed.
