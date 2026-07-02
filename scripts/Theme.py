"""Design tokens and theming for the Econogram desktop UI.

Defines the color palette, type scale, and spacing scale used across the
app, and applies them to both classic Tk widgets (via the option database)
and ttk widgets (via ttk.Style). The palette extends the deep-navy brand
color already used in assets/logo.png and assets/banner.png rather than
inventing a new one.

Because Tk's option database cascades to every classic-tk widget created
anywhere in the app (menus, popups, entries, buttons), calling apply_theme()
once at startup themes the existing popup dialogs without needing to edit
each dialog module individually.
"""
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

COLORS = {
    "bg": "#F4F6F9",            # app window background
    "surface": "#FFFFFF",       # entries, table, popups
    "surface_alt": "#EEF1F6",   # zebra striping / recessed areas
    "border": "#D7DCE3",
    "ink": "#1A1D23",           # primary text
    "muted": "#4B5565",         # secondary text (>=4.5:1 on bg/surface)
    "accent": "#1B2A4A",        # brand navy, from the logo/banner
    "accent_hover": "#24365E",
    "accent_active": "#101A30",
    "accent_on": "#FFFFFF",     # text/icons drawn on top of accent
    "focus": "#3B6CE0",
    "positive": "#1E7B4D",      # cash inflow
    "negative": "#B3261E",      # cash outflow
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 20,
    "xl": 32,
}

_FONT_CANDIDATES = ["Segoe UI", "Helvetica Neue", "Helvetica", "Arial"]

_cache = {}


def _pick_family():
    if "family" in _cache:
        return _cache["family"]
    available = set(tkfont.families())
    family = next((c for c in _FONT_CANDIDATES if c in available), "TkDefaultFont")
    _cache["family"] = family
    return family


def get_fonts():
    """Build (and cache) the app's type scale. Requires a Tk root to exist."""
    if "scale" in _cache:
        return _cache["scale"]
    family = _pick_family()
    mono_family = "Consolas" if "Consolas" in tkfont.families() else family
    scale = {
        "body": tkfont.Font(family=family, size=10),
        "body_bold": tkfont.Font(family=family, size=10, weight="bold"),
        "heading": tkfont.Font(family=family, size=12, weight="bold"),
        "mono": tkfont.Font(family=mono_family, size=10),
    }
    _cache["scale"] = scale
    return scale


def apply_theme(root):
    """Apply the Econogram design tokens to the whole app."""
    fonts = get_fonts()
    body = fonts["body"]
    button_font = fonts["body_bold"]

    root.configure(background=COLORS["bg"])
    root.option_clear()

    root.option_add("*Font", body)
    root.option_add("*Background", COLORS["bg"])
    root.option_add("*Foreground", COLORS["ink"])

    root.option_add("*Toplevel.Background", COLORS["bg"])
    root.option_add("*Frame.Background", COLORS["bg"])

    root.option_add("*Label.Background", COLORS["bg"])
    root.option_add("*Label.Foreground", COLORS["ink"])

    root.option_add("*Entry.Background", COLORS["surface"])
    root.option_add("*Entry.Foreground", COLORS["ink"])
    root.option_add("*Entry.insertBackground", COLORS["ink"])
    root.option_add("*Entry.relief", "flat")
    root.option_add("*Entry.highlightThickness", 1)
    root.option_add("*Entry.highlightBackground", COLORS["border"])
    root.option_add("*Entry.highlightColor", COLORS["focus"])
    root.option_add("*Entry.disabledBackground", COLORS["surface_alt"])

    root.option_add("*Button.Background", COLORS["accent"])
    root.option_add("*Button.Foreground", COLORS["accent_on"])
    root.option_add("*Button.activeBackground", COLORS["accent_hover"])
    root.option_add("*Button.activeForeground", COLORS["accent_on"])
    root.option_add("*Button.relief", "flat")
    root.option_add("*Button.font", button_font)
    root.option_add("*Button.padX", 16)
    root.option_add("*Button.padY", 7)
    root.option_add("*Button.cursor", "hand2")
    root.option_add("*Button.borderWidth", 0)
    # Keep a visible focus ring (in the brand focus color) for keyboard nav
    # rather than stripping it for a flatter look.
    root.option_add("*Button.highlightThickness", 2)
    root.option_add("*Button.highlightBackground", COLORS["bg"])
    root.option_add("*Button.highlightColor", COLORS["focus"])

    root.option_add("*Menu.Background", COLORS["surface"])
    root.option_add("*Menu.Foreground", COLORS["ink"])
    root.option_add("*Menu.activeBackground", COLORS["accent"])
    root.option_add("*Menu.activeForeground", COLORS["accent_on"])
    root.option_add("*Menu.font", body)
    root.option_add("*Menu.borderWidth", 1)

    root.option_add("*Scale.Background", COLORS["bg"])
    root.option_add("*Scale.troughColor", COLORS["border"])
    root.option_add("*Scale.foreground", COLORS["ink"])
    root.option_add("*Scale.activeBackground", COLORS["accent_hover"])
    root.option_add("*Scale.highlightThickness", 0)

    root.option_add("*PanedWindow.Background", COLORS["border"])
    root.option_add("*PanedWindow.sashRelief", "flat")

    _configure_ttk(root, fonts)


def _configure_ttk(root, fonts):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=COLORS["bg"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["ink"], font=fonts["body"])

    style.configure(
        "TScrollbar",
        background=COLORS["surface_alt"],
        troughcolor=COLORS["bg"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["muted"],
        relief="flat",
    )
    style.map("TScrollbar", background=[("active", COLORS["border"])])

    style.configure(
        "Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["ink"],
        rowheight=26,
        font=fonts["body"],
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["accent"],
        foreground=COLORS["accent_on"],
        font=fonts["body_bold"],
        relief="flat",
        padding=(8, 6),
    )
    style.map("Treeview.Heading", background=[("active", COLORS["accent_hover"])])
    style.map(
        "Treeview",
        background=[("selected", COLORS["accent"])],
        foreground=[("selected", COLORS["accent_on"])],
    )
