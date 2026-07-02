"""Transient, non-blocking confirmation messages ("toasts").

Used for feedback on successful, non-destructive actions (e.g. "Added 6
entries to 'Deposits'") so the user gets a clear acknowledgment without
the interruption of a modal messagebox. Destructive actions keep their
existing confirm-before-acting messagebox pattern rather than a toast.
"""
import tkinter as tk
from scripts.Theme import COLORS, SPACING, get_fonts
from scripts.Motion import reduced_motion

_active_toast = {}


def show_toast(app, message, kind="success", duration_ms=2200):
    root = app.root

    existing = _active_toast.get(root)
    if existing is not None and existing.winfo_exists():
        existing.destroy()

    fonts = get_fonts()
    bg = COLORS["positive"] if kind == "success" else COLORS["accent"]

    toast = tk.Label(
        root, text=message, font=fonts["body_bold"], background=bg, foreground=COLORS["accent_on"],
        padx=SPACING["md"], pady=SPACING["sm"]
    )

    # Clears the status bar (36px + 1px border) and the table's heading row
    # (~34px) so it never sits on top of either.
    target_y = 80
    start_y = target_y if reduced_motion(app) else target_y - 16
    toast.place(relx=1.0, x=-SPACING["lg"], y=start_y, anchor="ne")
    toast.lift()
    _active_toast[root] = toast

    if not reduced_motion(app):
        def slide(i=0, steps=6):
            if not toast.winfo_exists():
                return
            y = _lerp(start_y, target_y, i / steps)
            toast.place_configure(y=int(y))
            if i < steps:
                root.after(15, lambda: slide(i + 1))

        slide()

    def dismiss():
        if toast.winfo_exists():
            toast.destroy()
        if _active_toast.get(root) is toast:
            del _active_toast[root]

    root.after(duration_ms, dismiss)
    return toast


def _lerp(a, b, t):
    return a + (b - a) * t
