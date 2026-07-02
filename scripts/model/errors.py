"""Errors raised by the scripts.model package."""


class LedgerError(Exception):
    """An invalid CashFlowLedger operation (bad input or a stale reference).

    The message is written to be shown directly to the user in a dialog's
    error label — no stack traces, no internal identifiers.
    """
