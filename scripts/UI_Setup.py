"""User interface setup and configuration module.

This module handles the creation and configuration of the main application UI,
including menus, status bars, and event bindings.
"""
import webbrowser

from scripts.Clear_Graph import clear_graph
from scripts.Theme import COLORS, SPACING, get_fonts, is_dark, toggle_dark_mode
import tkinter as tk
from tkinter import font, messagebox, simpledialog, ttk
import os


def get_asset_path(filename):
    """Get the absolute path to an asset file.

    This function searches upward from the current script directory to find an 'assets'
    directory (so assets can live at the project root). It also supports PyInstaller
    bundles (sys._MEIPASS) and tries to use the git repo root as a fallback. If nothing
    is found it returns a sensible relative path (which may not exist).
    """
    import sys
    import subprocess

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # If running from a PyInstaller bundle, assets may be in _MEIPASS
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidate = os.path.join(meipass, "assets", filename)
        if os.path.exists(candidate):
            return candidate

    # Walk upward from this file looking for an 'assets' directory that contains the file
    cur_dir = script_dir
    root = os.path.abspath(os.sep)
    while True:
        candidate = os.path.join(cur_dir, "assets", filename)
        if os.path.exists(candidate):
            return candidate
        if cur_dir == root:
            break
        parent = os.path.dirname(cur_dir)
        if parent == cur_dir:
            break
        cur_dir = parent

    # Try to find repo root via git and look for assets there
    try:
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=script_dir,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        candidate = os.path.join(git_root, "assets", filename)
        if os.path.exists(candidate):
            return candidate
    except Exception:
        # git not available or not a git repo — ignore
        pass

    # Final fallback: assume assets is one level up from this script (common if moved into 'scripts')
    return os.path.abspath(os.path.join(script_dir, "..", "assets", filename))


def setup_ui(app):
    # Create the menu bar
    create_menu_bar(app)

    # Create a status bar at the top for interest rate display
    create_status_bar(app)

    # Create a PanedWindow for resizable sections (graph and table).
    # Stays classic tk: ttkbootstrap doesn't offer a materially different
    # PanedWindow, and the sash is already themed via option_add.
    app.main_paned_window = tk.PanedWindow(
        app.root, orient=tk.HORIZONTAL, sashrelief=tk.FLAT, sashwidth=6,
        background=COLORS["border"], bd=0
    )
    app.main_paned_window.pack(side="top", fill=tk.BOTH, expand=True)

    # Create a frame for the graph (will be populated by update_plot)
    app.graph_frame = ttk.Frame(app.main_paned_window)
    app.main_paned_window.add(app.graph_frame, stretch="always")

    # Create a frame for the table (will be populated by create_table)
    app.table_frame = ttk.Frame(app.main_paned_window)
    app.main_paned_window.add(app.table_frame, stretch="never")

    # Initialize toggle state for Make New Series
    app.makeNewSeries = False


def create_menu_bar(app):
    """Create a traditional menu bar with File, Edit, Insert, Calculate, Options, and Help menus."""
    menubar = tk.Menu(app.root)
    app.root.config(menu=menubar)

    # File Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu, underline=0)
    file_menu.add_command(label="Clear Graph", command=app.clear_graph, underline=0)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.root.quit, underline=0)

    # Edit Menu
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu, underline=0)
    edit_menu.add_command(label="Undo", command=app.undo_last_action, accelerator="Ctrl+Z", underline=0)
    edit_menu.add_command(label="Delete Selection", command=app.delete_selected_series, accelerator="Delete",
                          underline=0)
    edit_menu.add_command(label="Invert Series", command=app.invert_selected_series, underline=0)
    edit_menu.add_command(label="Split Series", command=app.split_selected_series, underline=1)
    edit_menu.add_separator()
    edit_menu.add_command(label="Combine Cash Flows", command=app.combine_cash_flows, underline=0)
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=app.select_all, accelerator="Ctrl+A", underline=0)
    edit_menu.add_command(label="Deselect All", command=app.deselect_all, accelerator="Esc", underline=7)
    # Reflect real availability instead of always being clickable and
    # bouncing back a "please select something" messagebox.
    edit_menu.config(postcommand=lambda: _update_edit_menu_state(app, edit_menu))

    # Insert Menu
    insert_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Insert", menu=insert_menu, underline=0)
    insert_menu.add_command(label="Single Cash Flow", command=app.popup_add_single_cash_flow, underline=0)
    insert_menu.add_command(label="Uniform Series", command=app.popup_uniform_series, underline=0)
    insert_menu.add_command(label="Gradient Series", command=app.popup_gradient_series, underline=0)
    insert_menu.add_command(label="Geometric Series", command=app.popup_geometric_series, underline=1)

    # Calculate Menu
    calculate_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Calculate", menu=calculate_menu, underline=0)
    calculate_menu.add_command(label="Present Value", command=app.popup_present_value, underline=0)
    calculate_menu.add_command(label="Future Value", command=app.popup_future_value, underline=0)
    calculate_menu.add_command(label="Annual Value", command=app.popup_annual_value, underline=0)
    calculate_menu.config(postcommand=lambda: _update_calculate_menu_state(app, calculate_menu))

    # Options Menu
    options_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Options", menu=options_menu, underline=0)
    options_menu.add_command(label="Set Interest Rate...", command=lambda: prompt_interest_rate_change(app),
                             underline=0)
    options_menu.add_separator()
    # Add checkbutton for Make New Series toggle
    app.makeNewSeries_var = tk.BooleanVar(value=False)
    options_menu.add_checkbutton(label="Make New Series", variable=app.makeNewSeries_var,
                                 command=app.toggle_makeNewSeries, underline=0)

    options_menu.add_separator()
    # Collapses popup fades/pulses/toast slides to instant state changes.
    # There's no reliable cross-platform way to read the OS "prefers
    # reduced motion" setting from Tkinter, so this is an explicit toggle.
    app.reduce_motion = tk.BooleanVar(value=False)
    options_menu.add_checkbutton(label="Reduce Motion", variable=app.reduce_motion, underline=0)

    options_menu.add_separator()
    app.dark_mode_var = tk.BooleanVar(value=is_dark())
    options_menu.add_checkbutton(
        label="Dark Mode", variable=app.dark_mode_var,
        command=lambda: _on_toggle_dark_mode(app), underline=0
    )

    # Help Menu
    # (mnemonics skipped here: with 17 topic entries the letters run out
    # fast and collisions stop being worth tracking for a menu that's
    # mostly browsed with the mouse rather than the keyboard)
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu, underline=0)

    # Add help topics to the Help menu
    help_menu.add_command(label="Present Value", command=lambda: show_help_message(
        "Present Value",
        "Present Value calculates the equivalent worth of a series of cash flows at a point before the series begins, using a specified interest rate. For cash flow series with multiple payments (uniform, gradient, or geometric), this point is one period before the first payment. For a single cash flow, the point of reference can be any period before the payment."))

    help_menu.add_command(label="Future Value", command=lambda: show_help_message(
        "Future Value",
        "Future Value calculates the equivalent worth of a series of cash flows at a point after the series ends, using a specified interest rate. For cash flow series with multiple payments (uniform, gradient, or geometric), this point is one period after the final payment. For a single cash flow, the point of reference can be any period after the payment."))

    help_menu.add_command(label="Annual Value", command=lambda: show_help_message(
        "Annual Value",
        "Annual Value calculates the equivalent uniform annual worth of a series of cash flows over its duration, using a specified interest rate. For cash flow series with multiple payments (uniform, gradient, or geometric), this value represents a consistent annual amount spanning the series. For a single cash flow, it distributes the value evenly across the specified periods."))

    help_menu.add_command(label="Combining Cash Flows", command=lambda: show_help_message(
        "Combining Cash Flows",
        "This function sums single cash flows that occur in the same period."))

    help_menu.add_command(label="Interest Rate", command=lambda: show_help_message(
        "Interest Rate",
        "The interest rate is the global time value of money across the entire program and applies to all functions."))

    help_menu.add_separator()

    help_menu.add_command(label="Single Cash Flow", command=lambda: show_help_message(
        "Single Cash Flow",
        "A single cash flow is an individual financial transaction involving a one-time payment or receipt of money at a specific point in time."))

    help_menu.add_command(label="Uniform Series", command=lambda: show_help_message(
        "Uniform Series",
        "A uniform or annual series is a series of constant values over a set number of periods."))

    help_menu.add_command(label="Gradient Series", command=lambda: show_help_message(
        "Gradient Series",
        "A gradient series is a series that increases by a set value across the length of the series. The first value in the series is always 0."))

    help_menu.add_command(label="Geometric Series", command=lambda: show_help_message(
        "Geometric Series",
        "A geometric series is a series that increases by a set percentage, known as the growth percentage, across the length of the series."))

    help_menu.add_separator()

    help_menu.add_command(label="FAQs", command=lambda: show_help_message(
        "FAQs",
        "1. If your problem includes a negative period, consider reframing the problem with your most negative value being set as Period 0.\n\n2. If the problem requires multiple interest rates, you are able to manipulate the cash flow to its final point and change the interest rate for the other parts of the problem.\n\n3. Just note that any changes across periods will involve the current interest rate displayed at the top of the screen."))

    help_menu.add_separator()
    help_menu.add_command(label="About", command=_open_help_docs)

    # Bind keyboard shortcuts
    app.root.bind('<Control-z>', lambda e: app.undo_last_action())
    app.root.bind('<Delete>', lambda e: app.delete_selected_series())
    app.root.bind('<Control-a>', lambda e: app.select_all())
    app.root.bind('<Escape>', lambda e: app.deselect_all())


def _valid_selected_indices(app):
    """Selected indices that still exist in the current cash_flows table."""
    if not app.selected_indices or app.cash_flows.empty:
        return []
    return list(app.cash_flows.index.intersection(app.selected_indices))


def _update_edit_menu_state(app, edit_menu):
    """Enable/disable Edit menu items to reflect what's actually doable."""
    selected = _valid_selected_indices(app)
    has_selection = bool(selected)
    has_undo = len(app.state_history) > 1

    can_split = False
    if has_selection:
        series_ids = set(app.cash_flows.loc[selected, "Series_ID"])
        if len(series_ids) == 1:
            series_id = next(iter(series_ids))
            can_split = len(app.cash_flows[app.cash_flows["Series_ID"] == series_id]) > 1

    edit_menu.entryconfig("Undo", state=tk.NORMAL if has_undo else tk.DISABLED)
    edit_menu.entryconfig("Delete Selection", state=tk.NORMAL if has_selection else tk.DISABLED)
    edit_menu.entryconfig("Invert Series", state=tk.NORMAL if has_selection else tk.DISABLED)
    edit_menu.entryconfig("Split Series", state=tk.NORMAL if can_split else tk.DISABLED)
    edit_menu.entryconfig("Combine Cash Flows", state=tk.NORMAL if len(selected) >= 2 else tk.DISABLED)
    edit_menu.entryconfig("Select All", state=tk.NORMAL if not app.cash_flows.empty else tk.DISABLED)
    edit_menu.entryconfig("Deselect All", state=tk.NORMAL if has_selection else tk.DISABLED)


def _update_calculate_menu_state(app, calculate_menu):
    """Enable/disable Calculate menu items based on whether anything is selected."""
    state = tk.NORMAL if _valid_selected_indices(app) else tk.DISABLED
    for label in ("Present Value", "Future Value", "Annual Value"):
        calculate_menu.entryconfig(label, state=state)


def create_status_bar(app):
    """Create a status bar at the top to display the interest rate."""
    fonts = get_fonts()
    status_bar = ttk.Frame(app.root, style="Surface.TFrame", height=36)
    status_bar.pack(side="top", fill="x")
    app.status_bar = status_bar

    # A 1px bottom border instead of a sunken bevel, in line with the flat
    # theme used everywhere else.
    separator = ttk.Frame(app.root, style="Border.TFrame", height=1)
    separator.pack(side="top", fill="x")

    # Interest rate label
    ttk.Label(
        status_bar, text="Interest Rate", font=fonts["body"],
        background=COLORS["surface"], foreground=COLORS["muted"]
    ).pack(side="left", padx=(SPACING["md"], SPACING["xs"]), pady=SPACING["xs"])
    app.interest_rate_label = ttk.Label(
        status_bar, text=f"{app.interest_rate}%", font=fonts["body_bold"],
        background=COLORS["surface"], foreground=COLORS["accent"]
    )
    app.interest_rate_label.pack(side="left", padx=(0, SPACING["md"]), pady=SPACING["xs"])


def _open_help_docs():
    webbrowser.open("https://github.com/tmaier-kettering/Econogram")

def show_help_message(title, message):
    """Show a help message dialog."""
    messagebox.showinfo(title, message)


def show_series_popup(app):
    # This function is no longer needed since series insertion is now in the Insert menu
    # But keeping it for backward compatibility if called elsewhere
    pass


def _on_toggle_dark_mode(app):
    """Swap the active palette and redraw everything that caches colors
    outside of Tk's own widget system (the matplotlib chart, the table's
    row-tag colors) -- toggle_dark_mode() itself only handles the ttk
    Style engine and the remaining classic-tk options."""
    from scripts.Create_Table import retheme_table

    def redraw():
        retheme_table(app)
        app.update_plot()

    toggle_dark_mode(app.dark_mode_var.get(), on_retheme=redraw)


def prompt_interest_rate_change(app):
    new_rate = simpledialog.askstring("Change Interest Rate", "Enter new interest rate:")
    if new_rate is not None and new_rate.strip():
        app.update_interest_rate(new_rate)