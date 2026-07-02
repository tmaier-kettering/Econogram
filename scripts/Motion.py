"""Small, dependency-free animation helpers for the Tkinter UI.

Kept intentionally simple: short (<=200ms), linear, driven by Tk's
`after()` — no easing libraries, no continuous redraw loops. Every
animation here checks reduced_motion(app) and collapses to an instant
end-state change when the user has turned on Options > Reduce Motion,
since Tkinter has no reliable cross-platform way to read the OS-level
"prefers reduced motion" setting.
"""
import tkinter as tk


def reduced_motion(app):
    var = getattr(app, "reduce_motion", None)
    return bool(var and var.get())


def _lerp(a, b, t):
    return a + (b - a) * t


def fade_in_window(window, duration_ms=140, steps=7):
    """Fade a Toplevel's opacity from 0 to 1. No-op on platforms without
    window alpha support (e.g. most Linux X11 setups)."""
    try:
        window.attributes('-alpha', 0.0)
    except tk.TclError:
        return

    def step(i=0):
        if not window.winfo_exists():
            return
        try:
            window.attributes('-alpha', i / steps)
        except tk.TclError:
            return
        if i < steps:
            window.after(max(1, duration_ms // steps), lambda: step(i + 1))

    step()


def pulse_rects_linewidth(canvas_widget, rects, target_width, start_width=0.4, duration_ms=180, steps=6, on_step=None):
    """Grow a batch of matplotlib patches' outlines together, from
    start_width to target_width, sharing a single redraw per animation
    frame.

    Selecting a whole series (e.g. a 20-period uniform series) can hand
    this dozens of rects at once. Redrawing the canvas once per rect per
    step (an earlier version of this function did that, by looping over
    rects at the call site and animating each independently) turns into
    dozens times steps synchronous full-figure redraws, which is slow
    enough to freeze the UI for multiple seconds. Animating the whole
    batch as one loop keeps the redraw count at `steps` regardless of how
    many bars were selected.
    """
    def step(i=0):
        live_rects = [r for r in rects if r.get_visible()]
        if not live_rects:
            return  # selection changed again before this finished
        t = i / steps
        width = _lerp(start_width, target_width, t)
        for rect in live_rects:
            rect.set_linewidth(width)
        if on_step:
            on_step()
        if i < steps:
            canvas_widget.after(max(1, duration_ms // steps), lambda: step(i + 1))

    step()
