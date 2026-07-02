"""Shared building blocks for Econogram's input popups.

The series-entry dialogs (Uniform, Single Cash Flow, Gradient, Geometric,
Split) were independently hand-rolling identical popup chrome (icon,
always-on-top, centering) and identical character-level validators. This
module centralizes both, and adds a themed inline error message so a
validation failure doesn't have to interrupt the user with a modal
messagebox on every mistake.
"""
import tkinter as tk
from scripts.UI_Setup import get_asset_path
from scripts.Theme import COLORS, SPACING, get_fonts
from scripts.Motion import fade_in_window, reduced_motion


def create_popup(app, title):
    """Create a themed Toplevel with the app's standard popup chrome."""
    top = tk.Toplevel(app.root)
    top.title(title)
    top.configure(background=COLORS["bg"])

    try:
        icon_path = get_asset_path("app.ico")
        top.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not load icon for '{title}' window: {e}")

    top.attributes('-topmost', True)
    top.bind('<Escape>', lambda e: top.destroy())

    if not reduced_motion(app):
        fade_in_window(top)

    return top


def center_popup(top):
    """Center a popup on screen. Call after all widgets have been added."""
    top.update_idletasks()
    width = top.winfo_reqwidth()
    height = top.winfo_reqheight()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'+{x}+{y}')


def build_form(top):
    """Create the padded, two-column form container used by every dialog."""
    frame = tk.Frame(top, background=COLORS["bg"])
    frame.pack(padx=SPACING["lg"], pady=SPACING["lg"], fill="both", expand=True)
    frame.grid_columnconfigure(1, weight=1, minsize=160)
    return frame


def add_field(form, row, label_text, validate_fn=None, default=None, select_default=False):
    """Add a labeled entry row to a form built with build_form().

    `default` prefills the field with a sensible starting value (e.g. a
    likely Starting Period of 0, or an auto-generated series name) so the
    common case needs fewer keystrokes. `select_default=True` selects the
    prefilled text so typing immediately replaces it, for defaults that
    are a placeholder to overwrite rather than a value to keep.
    """
    fonts = get_fonts()
    tk.Label(form, text=label_text, font=fonts["body"], anchor="w").grid(
        row=row, column=0, sticky="w", padx=(0, SPACING["md"]), pady=SPACING["xs"]
    )

    kwargs = {}
    if validate_fn is not None:
        kwargs["validate"] = "key"
        kwargs["validatecommand"] = (form.register(validate_fn), '%P', '%d')

    entry = tk.Entry(form, **kwargs)
    entry.grid(row=row, column=1, sticky="ew", pady=SPACING["xs"])

    if default is not None:
        entry.insert(0, default)
        if select_default:
            entry.select_range(0, tk.END)
            entry.icursor(tk.END)

    return entry


def add_error_label(form, row, columnspan=2):
    """An inline validation-error message, hidden until show_error() is called."""
    fonts = get_fonts()
    label = tk.Label(
        form, text="", font=fonts["body"], fg=COLORS["negative"],
        background=COLORS["bg"], wraplength=280, justify="left"
    )
    label.grid(row=row, column=0, columnspan=columnspan, sticky="w", pady=(SPACING["xs"], 0))
    label.grid_remove()
    return label


def show_error(error_label, message):
    error_label.config(text=f"⚠ {message}")
    error_label.grid()


def clear_error(error_label):
    error_label.config(text="")
    error_label.grid_remove()


def add_submit_button(form, row, text, command, columnspan=2):
    button = tk.Button(form, text=text, command=command)
    button.grid(row=row, column=0, columnspan=columnspan, pady=(SPACING["md"], 0))
    add_press_feedback(button)
    return button


def add_press_feedback(button):
    """Darken a button a step further on press, for tactile click feedback.

    Tk already swaps to `activebackground` on hover automatically; this
    additionally swaps `activebackground` itself while the mouse button is
    down, then restores it on release.
    """
    hover_color = button.cget("activebackground")

    def on_press(_event):
        button.configure(activebackground=COLORS["accent_active"])

    def on_release(_event):
        button.configure(activebackground=hover_color)

    button.bind("<ButtonPress-1>", on_press, add="+")
    button.bind("<ButtonRelease-1>", on_release, add="+")


# --- Shared character-level validators -------------------------------------
# Used as Tk `validatecommand` targets: return True to allow the edit.

def validate_currency(entry_text, action_type):
    """Allow a negative sign, at most one decimal point, <=2 decimal places."""
    if action_type == '1':
        if entry_text in {'-', '-.', '.'}:
            return True
        if not (
            entry_text.replace('-', '', 1).replace('.', '', 1).isdigit()
            and entry_text.count('-') <= 1
            and entry_text.count('.') <= 1
            and entry_text.find('-') <= 0
        ):
            return False
        if '.' in entry_text and len(entry_text.split('.')[1]) > 2:
            return False
        if len(entry_text) > 10:
            return False
    return True


def validate_integer(entry_text, action_type):
    """Allow a leading negative sign and digits only, while typing."""
    if action_type == '1':
        if entry_text in {'-', ''}:
            return True
        if not (
            entry_text.replace('-', '', 1).isdigit()
            and entry_text.count('-') <= 1
            and entry_text.find('-') <= 0
        ):
            return False
    return True


def validate_series_name(entry_text, action_type, max_len=14):
    if action_type == '1' and len(entry_text) > max_len:
        return False
    return True
