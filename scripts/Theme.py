"""Design tokens and theming for the Econogram desktop UI.

Powered by ttkbootstrap: a custom light/dark theme pair built from the
existing brand palette (still the deep-navy from assets/logo.png and
assets/banner.png), registered with ttkbootstrap's Style engine so every
ttk.*/ttkbootstrap widget in the app picks up modern flat-design styling
(richer hover/pressed states, modern Treeview/scrollbar rendering) instead
of the plain ttk "clam" theme used previously.

A handful of widgets stay classic tk (native Menu can't be themed by any
ttk engine on any platform; PanedWindow's sash is simple enough to keep as
direct option_add) -- everything else in the app was converted to ttk
widgets so the Style engine below actually reaches it.
"""
import tkinter as tk
from tkinter import font as tkfont
from ttkbootstrap.style import Style, ThemeDefinition, Colors as TbColors

LIGHT_COLORS = {
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

# Same brand hue family, lifted in lightness/saturation so it reads clearly
# against near-black surfaces -- the light-mode navy would nearly vanish on
# a dark background. Contrast-checked (WCAG AA) against its own bg/surface.
DARK_COLORS = {
    "bg": "#12151A",
    "surface": "#1A1F27",
    "surface_alt": "#212733",
    "border": "#2E3642",
    "ink": "#E7EAEE",
    "muted": "#9BA5B4",
    "accent": "#4C6FC7",
    "accent_hover": "#5470BE",
    "accent_active": "#3A57A3",
    "accent_on": "#FFFFFF",
    "focus": "#6C8EE8",
    "positive": "#3FB876",
    "negative": "#EA6259",
}

# A single mutable dict object, never reassigned. Every
# `from scripts.Theme import COLORS` elsewhere in the app binds to this
# object, so toggle_dark_mode()'s in-place mutation is automatically
# visible everywhere without touching those files' imports.
COLORS = dict(LIGHT_COLORS)

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 20,
    "xl": 32,
}

_FONT_CANDIDATES = ["Segoe UI", "Helvetica Neue", "Helvetica", "Arial"]

_cache = {}
_state = {"dark": False, "root": None}


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


def is_dark() -> bool:
    return _state["dark"]


def _build_theme_definition(name, colors, themetype):
    tb_colors = TbColors(
        primary=colors["accent"],
        secondary=colors["muted"],
        success=colors["positive"],
        info=colors["focus"],
        warning=colors["negative"],
        danger=colors["negative"],
        light=colors["surface_alt"],
        dark=colors["ink"],
        bg=colors["bg"],
        fg=colors["ink"],
        selectbg=colors["accent"],
        selectfg=colors["accent_on"],
        border=colors["border"],
        inputfg=colors["ink"],
        inputbg=colors["surface"],
        active=colors["accent_hover"],
    )
    return ThemeDefinition(name=name, colors=tb_colors, themetype=themetype)


def apply_theme(root):
    """Apply the Econogram design tokens to the whole app.

    Registers both the light and dark ttkbootstrap themes up front (so
    toggling later is just a theme_use() swap) and activates light mode.
    """
    _state["root"] = root
    _state["dark"] = False
    COLORS.clear()
    COLORS.update(LIGHT_COLORS)
    fonts = get_fonts()

    root.option_clear()

    style = Style()
    style.register_theme(_build_theme_definition("econogram-light", LIGHT_COLORS, "light"))
    style.register_theme(_build_theme_definition("econogram-dark", DARK_COLORS, "dark"))
    style.theme_use("econogram-light")

    _configure_ttk_extras(style, fonts)
    _apply_classic_tk_options(root, fonts)
    root.configure(background=COLORS["bg"])


def toggle_dark_mode(on: bool, on_retheme=None):
    """Swap the active palette and re-theme everything already on screen.

    Mutating COLORS in place only affects *future* widget creation; this
    also re-applies the palette to the ttk Style engine and the remaining
    classic-tk options. `on_retheme` is an optional no-arg callback for
    things that cache colors outside Tk's own widget system entirely (the
    matplotlib chart, Treeview row-tag colors) -- those need to be
    explicitly redrawn, since changing the ttk theme doesn't touch them.
    """
    _state["dark"] = on
    COLORS.clear()
    COLORS.update(DARK_COLORS if on else LIGHT_COLORS)

    style = Style.get_instance()
    style.theme_use("econogram-dark" if on else "econogram-light")
    _configure_ttk_extras(style, get_fonts())

    root = _state["root"]
    if root is not None:
        _apply_classic_tk_options(root, get_fonts())
        root.configure(background=COLORS["bg"])

    if on_retheme is not None:
        on_retheme()


def _configure_ttk_extras(style, fonts):
    """Widget-specific tweaks the theme engine doesn't cover by default.

    ttk.Frame doesn't accept a direct `background=` kwarg the way classic
    tk.Frame does (confirmed: it raises "unknown option -background") --
    any frame that needs a color other than the theme's default window
    background has to go through a named style like these instead.
    """
    style.configure("Treeview", rowheight=26, font=fonts["body"])
    style.configure("Treeview.Heading", font=fonts["body_bold"], padding=(8, 6))
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure("Border.TFrame", background=COLORS["border"])


def _apply_classic_tk_options(root, fonts):
    """The few widgets that stay classic tk: native Menu, and PanedWindow's
    sash (simple enough not to need a ttk equivalent)."""
    root.option_add("*Menu.Background", COLORS["surface"])
    root.option_add("*Menu.Foreground", COLORS["ink"])
    root.option_add("*Menu.activeBackground", COLORS["accent"])
    root.option_add("*Menu.activeForeground", COLORS["accent_on"])
    root.option_add("*Menu.font", fonts["body"])
    root.option_add("*Menu.borderWidth", 1)

    root.option_add("*PanedWindow.Background", COLORS["border"])
    root.option_add("*PanedWindow.sashRelief", "flat")
