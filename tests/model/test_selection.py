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
