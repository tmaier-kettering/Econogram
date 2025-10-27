from scripts.Clear_Graph import clear_graph
import tkinter as tk
from tkinter import font, messagebox, simpledialog
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

    # Create a PanedWindow for resizable sections (graph and table)
    app.main_paned_window = tk.PanedWindow(app.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    app.main_paned_window.pack(side="top", fill=tk.BOTH, expand=True)
    
    # Create a frame for the graph (will be populated by update_plot)
    app.graph_frame = tk.Frame(app.main_paned_window)
    app.main_paned_window.add(app.graph_frame, stretch="always")
    
    # Create a frame for the table (will be populated by create_table)
    app.table_frame = tk.Frame(app.main_paned_window)
    app.main_paned_window.add(app.table_frame, stretch="never")
    
    # Initialize toggle state for Make New Series
    app.makeNewSeries = False


def create_menu_bar(app):
    """Create a traditional menu bar with File, Edit, Insert, Calculate, Options, and Help menus."""
    menubar = tk.Menu(app.root)
    app.root.config(menu=menubar)
    
    # File Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Clear Graph", command=app.clear_graph)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.root.quit)
    
    # Edit Menu
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Undo", command=app.undo_last_action, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Delete Selection", command=app.delete_selected_series, accelerator="Delete")
    edit_menu.add_separator()
    edit_menu.add_command(label="Combine Cash Flows", command=app.combine_cash_flows)
    
    # Insert Menu
    insert_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Insert", menu=insert_menu)
    insert_menu.add_command(label="Single Cash Flow", command=app.popup_add_single_cash_flow)
    insert_menu.add_command(label="Uniform Series", command=app.popup_uniform_series)
    insert_menu.add_command(label="Gradient Series", command=app.popup_gradient_series)
    insert_menu.add_command(label="Geometric Series", command=app.popup_geometric_series)
    
    # Calculate Menu
    calculate_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Calculate", menu=calculate_menu)
    calculate_menu.add_command(label="Present Value", command=app.popup_present_value)
    calculate_menu.add_command(label="Future Value", command=app.popup_future_value)
    calculate_menu.add_command(label="Annual Value", command=app.popup_annual_value)
    
    # Options Menu
    options_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Options", menu=options_menu)
    options_menu.add_command(label="Set Interest Rate...", command=lambda: prompt_interest_rate_change(app))
    options_menu.add_separator()
    # Add checkbutton for Make New Series toggle
    app.makeNewSeries_var = tk.BooleanVar(value=False)
    options_menu.add_checkbutton(label="Make New Series", variable=app.makeNewSeries_var, 
                                 command=app.toggle_makeNewSeries)
    
    # Help Menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    
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
    help_menu.add_command(label="About", command=lambda: show_help_message(
        "About Cash Flow Diagram", 
        "Cash Flow Diagram\nA tool for analyzing and visualizing cash flows over time."))
    
    # Bind keyboard shortcuts
    app.root.bind('<Control-z>', lambda e: app.undo_last_action())
    app.root.bind('<Delete>', lambda e: app.delete_selected_series())


def create_status_bar(app):
    """Create a status bar at the top to display the interest rate."""
    status_bar = tk.Frame(app.root, relief=tk.SUNKEN, bd=1)
    status_bar.pack(side="top", fill="x")
    
    # Interest rate label
    tk.Label(status_bar, text="Interest Rate:", font=("Arial", 10)).pack(side="left", padx=5)
    app.interest_rate_label = tk.Label(status_bar, text=f"{app.interest_rate}%", font=("Arial", 10, "bold"))
    app.interest_rate_label.pack(side="left", padx=5)


def show_help_message(title, message):
    """Show a help message dialog."""
    messagebox.showinfo(title, message)


def show_series_popup(app):
    # This function is no longer needed since series insertion is now in the Insert menu
    # But keeping it for backward compatibility if called elsewhere
    pass


def prompt_interest_rate_change(app):
    new_rate = tk.simpledialog.askstring("Change Interest Rate", "Enter new interest rate:")
    if new_rate is not None:
        app.update_interest_rate(new_rate)
