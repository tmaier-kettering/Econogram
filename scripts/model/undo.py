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
