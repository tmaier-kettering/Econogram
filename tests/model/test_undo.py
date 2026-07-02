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
