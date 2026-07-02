"""Plot update and rendering module.

Handles the creation and updating of the cash flow diagram visualization
using matplotlib.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib import patheffects
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scripts.Create_Table import create_table
from scripts.Clear_Graph import clear_graph
from scripts.Theme import COLORS
from scripts.Motion import reduced_motion, pulse_rects_linewidth
import matplotlib.ticker as mtick


def update_plot(app):
    # Initialize or clear previous canvas
    if hasattr(app, 'canvas') and app.canvas:
        app.canvas.get_tk_widget().pack_forget()

    # Create new figure and axes, themed to match the app chrome rather
    # than matplotlib's default white/gray look.
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["surface"])
    fig.subplots_adjust(right=0.7)
    app.selection_rects = []

    # Ensure there are cash flows to plot
    if not app.cash_flows.empty:
        create_bars(ax, app)
        set_y_limits_with_buffer(ax)
        configure_axes(ax, app)
        add_legend(ax, app)
    else:
        draw_empty_state(ax)

    # Configure event handling regardless of whether there are cash flows
    # This ensures the right-click context menu works even on an empty graph
    configure_event_handling(fig, ax, app)

    # Display the canvas within the GUI
    display_canvas(app, fig)


def draw_empty_state(ax):
    """A first-run hint instead of a bare, unlabeled 0-1 axes box."""
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.text(
        0.5, 0.55, "No cash flows yet",
        ha="center", va="center", transform=ax.transAxes,
        fontsize=15, fontweight="bold", color=COLORS["ink"]
    )
    ax.text(
        0.5, 0.47, "Right-click the chart, or use the Insert menu, to add your first cash flow.",
        ha="center", va="center", transform=ax.transAxes,
        fontsize=10, color=COLORS["muted"]
    )


def create_bars(ax, app):
    # Loop through each period and create bars for cash flows
    for period in app.cash_flows["Period"].unique():
        period_cash_flows = app.cash_flows[app.cash_flows["Period"] == period].sort_values(
            by="Cash Flow", ascending=False
        )
        bottom_positive, bottom_negative = 0, 0
        for i, row in period_cash_flows.iterrows():
            cash_flow = row["Cash Flow"]
            bottom = bottom_positive if cash_flow >= 0 else bottom_negative
            bar = ax.bar(period, cash_flow, bottom=bottom, color=row["Color"], align='center')[0]
            if cash_flow >= 0:
                bottom_positive += cash_flow
            else:
                bottom_negative += cash_flow
            bar.set_gid(i)


def set_y_limits_with_buffer(ax):
    buffer_percentage = 0.25
    ymin, ymax = ax.get_ylim()
    y_range = ymax - ymin
    ax.set_ylim(bottom=ymin - buffer_percentage * y_range, top=ymax + buffer_percentage * y_range)
    ax.axhline(0, color=COLORS["ink"], linewidth=1)


def configure_axes(ax, app):
    ax.set_xlabel("Period", color=COLORS["ink"], fontsize=10)
    ax.set_ylabel("Dollars", color=COLORS["ink"], fontsize=10)
    ax.set_title("Cash Flow Diagram", color=COLORS["ink"], fontsize=13, fontweight="bold", pad=12)

    # Format y-axis ticks with dollar sign and comma separators, two decimal places
    # Use StrMethodFormatter instead of FuncFormatter so we don't need ticklabel_format
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.2f}"))

    max_period = app.cash_flows["Period"].max()
    min_period = app.cash_flows["Period"].min()
    tick_interval = 1 if max_period <= 20 else (2 if max_period <= 50 else 5)
    next_tick_mark = ((max_period // tick_interval) + 1) * tick_interval
    ax.set_xticks(range(min(0, min_period), next_tick_mark + 1, tick_interval))
    ax.set_xlim(left=min(-0.5, min_period - 0.5), right=next_tick_mark + 0.5)

    ax.tick_params(colors=COLORS["muted"], labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(COLORS["border"])
    ax.grid(axis='y', color=COLORS["border"], linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)


def add_legend(ax, app):
    series_info = app.cash_flows[['Series_Name', 'Color']].drop_duplicates().sort_values('Series_Name')
    if not series_info.empty:
        legend_handles = [
            Patch(facecolor=row['Color'], edgecolor=COLORS["border"], label=row["Series_Name"])
            for _, row in series_info.iterrows()
        ]
        legend = ax.legend(
            handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0,
            frameon=True, facecolor=COLORS["surface"], edgecolor=COLORS["border"]
        )
        # Legend rendering creates its own handle artists rather than
        # reusing the Patch objects passed in above, so picker/gid have to
        # be set on legend.legend_handles (the artists actually on screen)
        # for clicks on the legend to be pickable at all.
        for handle, text in zip(legend.legend_handles, legend.get_texts()):
            series_name = text.get_text()
            text.set_color(COLORS["ink"])
            handle.set_picker(True)
            handle.set_gid(series_name)
            text.set_picker(True)
            text.set_gid(series_name)


def configure_event_handling(fig, ax, app):
    def on_click(event):
        handle_click(event, ax, app)

    def on_pick(event):
        handle_legend_pick(event, ax, app)

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("pick_event", on_pick)


def handle_click(event, ax, app):
    if event.inaxes:
        try:
            clicked_bar = next((bar for bar in ax.patches if bar.contains(event)[0]), None)
            if clicked_bar:
                if event.button == 3:  # Right-click on a bar
                    handle_bar_selection(clicked_bar, ax, app, right_click=True)
                    update_selection_display(ax, app)
                    show_context_menu(event, app)
                    return
                else:  # Left-click on a bar
                    handle_bar_selection(clicked_bar, ax, app, right_click=False)
            else:
                # Click on blank space
                if event.button == 3:  # Right-click on blank space
                    show_insert_menu(event, app)
                    return
                else:  # Left-click on blank space clears the selection
                    app.selected_indices = []
        except KeyError as e:
            print(f"Error: No matching series or invalid bar data - {str(e)}")

    update_selection_display(ax, app)


def handle_legend_pick(event, ax, app):
    """Selecting a series by clicking its legend swatch or label, mirroring
    the selection behavior of clicking one of its bars."""
    series_name = event.artist.get_gid()
    if not series_name:
        return

    series_indices = app.cash_flows[app.cash_flows["Series_Name"] == series_name].index.tolist()
    if not series_indices:
        return

    mouse_event = event.mouseevent
    right_click = getattr(mouse_event, "button", None) == 3
    toggle_series_selection(series_indices, app, right_click=right_click)
    update_selection_display(ax, app)

    if right_click:
        show_context_menu(mouse_event, app)


def rename_series(app):
    """Rename the selected series."""
    if not app.selected_indices:
        messagebox.showwarning("No Selection", "Please select a cash flow to rename.")
        return
    
    # Get the series ID and current name from the first selected index
    first_selected_idx = app.selected_indices[0]
    series_id, current_name = app.cash_flows.loc[first_selected_idx, ['Series_ID', 'Series_Name']]
    
    # Prompt for new name
    new_name = simpledialog.askstring("Rename Series", 
                                      f"Enter new name for '{current_name}':",
                                      initialvalue=current_name)
    
    if new_name and new_name.strip():
        # Update all rows with this series ID
        app.cash_flows.loc[app.cash_flows["Series_ID"] == series_id, "Series_Name"] = new_name.strip()
        app.update_plot()


def show_context_menu(event, app):
    """Display a context menu with cash flow operations."""
    # Create context menu
    context_menu = tk.Menu(app.root, tearoff=0)
    
    # Check if selected series has length > 1
    show_split_option = False
    if app.selected_indices:
        selected_series_ids = app.cash_flows.loc[app.selected_indices, "Series_ID"].unique()
        if len(selected_series_ids) == 1:
            series_id = selected_series_ids[0]
            series_data = app.cash_flows[app.cash_flows["Series_ID"] == series_id]
            if len(series_data) > 1:
                show_split_option = True
    
    # Add menu items for each operation
    context_menu.add_command(label="Present Value", command=app.popup_present_value)
    context_menu.add_command(label="Future Value", command=app.popup_future_value)
    context_menu.add_command(label="Annual Value", command=app.popup_annual_value)
    context_menu.add_separator()
    context_menu.add_command(label="Combine Cash Flow", command=app.combine_cash_flows)
    context_menu.add_command(label="Invert Series", command=app.invert_selected_series)
    if show_split_option:
        context_menu.add_command(label="Split Series", command=app.split_selected_series)
    context_menu.add_separator()
    context_menu.add_command(label="Rename", command=lambda: rename_series(app))
    context_menu.add_separator()
    context_menu.add_command(label="Delete Selection", command=app.delete_selected_series)
    context_menu.add_command(label="Clear", command=lambda: clear_graph(app))
    context_menu.add_command(label="Undo", command=app.undo_last_action)
    
    # Display the menu at the cursor position
    x = app.root.winfo_pointerx()
    y = app.root.winfo_pointery()
    context_menu.tk_popup(x, y)
    context_menu.grab_release()


def show_insert_menu(event, app):
    """Display a context menu with insert options for new series."""
    # Create context menu
    insert_menu = tk.Menu(app.root, tearoff=0)
    
    # Add menu items for each insert operation
    insert_menu.add_command(label="Single Cash Flow", command=app.popup_add_single_cash_flow)
    insert_menu.add_command(label="Uniform Series", command=app.popup_uniform_series)
    insert_menu.add_command(label="Gradient Series", command=app.popup_gradient_series)
    insert_menu.add_command(label="Geometric Series", command=app.popup_geometric_series)
    
    # Display the menu at the cursor position
    x = app.root.winfo_pointerx()
    y = app.root.winfo_pointery()
    insert_menu.tk_popup(x, y)
    insert_menu.grab_release()


def handle_bar_selection(clicked_bar, ax, app, right_click=False):
    bar_id = clicked_bar.get_gid()
    cash_flow_row = app.cash_flows.loc[bar_id] if bar_id is not None else None

    if cash_flow_row is not None:
        series_indices = app.cash_flows[
            app.cash_flows["Series_ID"] == cash_flow_row['Series_ID']].index.tolist()
        is_single_cash_flow_series = len(series_indices) == 1

        if is_single_cash_flow_series:
            toggle_single_cash_flow_selection(bar_id, app, right_click)
        else:
            toggle_series_selection(series_indices, app, right_click)


def toggle_single_cash_flow_selection(bar_id, app, right_click=False):
    # Toggle selection of a single cash flow
    # On right-click, only select (don't deselect if already selected)
    if bar_id in app.selected_indices:
        if not right_click:
            app.selected_indices.remove(bar_id)
    else:
        app.selected_indices.append(bar_id)


def toggle_series_selection(series_indices, app, right_click=False):
    # Toggle selection of a series
    # On right-click, only select (don't deselect if already selected)
    if all(index in app.selected_indices for index in series_indices):
        if not right_click:
            app.selected_indices = [index for index in app.selected_indices if index not in series_indices]
    else:
        app.selected_indices.extend(index for index in series_indices if index not in app.selected_indices)


def update_selection_display(ax, app):
    # Track which bars were already selected before this call, so newly
    # selected bars can get a brief "pop" instead of appearing static.
    previously_selected = getattr(app, "_previous_selection_ids", set())
    currently_selected = set(app.selected_indices)
    newly_selected = currently_selected - previously_selected
    app._previous_selection_ids = currently_selected

    for rect in app.selection_rects:
        rect.set_visible(False)
    app.selection_rects.clear()

    selected_values = []
    new_rects = []
    for bar in ax.patches:
        bar_id = bar.get_gid()
        if bar_id in app.selected_indices:
            # Selection color is intentionally not red: red is already used
            # for negative cash flows in the table, and reusing it here
            # would read as an error/warning rather than "selected". A white
            # halo stroke keeps the outline visible even when a bar's own
            # fill color happens to be close to the focus blue (tab20
            # includes several blues).
            selection_rect = Rectangle(
                (bar.get_x(), bar.get_y()), bar.get_width(), bar.get_height(),
                linewidth=2, edgecolor=COLORS["focus"], facecolor='none'
            )
            selection_rect.set_path_effects([
                patheffects.withStroke(linewidth=4, foreground=COLORS["surface"])
            ])
            ax.add_patch(selection_rect)
            app.selection_rects.append(selection_rect)
            if bar_id in newly_selected:
                new_rects.append(selection_rect)

            period = app.cash_flows.loc[bar_id, "Period"]
            cash_flow_value = app.cash_flows.loc[bar_id, "Cash Flow"]
            series_name = app.cash_flows.loc[bar_id, "Series_Name"]
            selected_values.append([series_name, period, cash_flow_value])

    create_table(app, selected_values) if selected_values else create_table(app, [])
    app.update_canvas()

    if new_rects and not reduced_motion(app):
        canvas = app.canvas
        canvas_widget = canvas.get_tk_widget()
        # draw_idle (coalesced, deferred) rather than the synchronous
        # update_canvas()/draw() used elsewhere: this runs once per
        # animation frame regardless of selection size, and a forced
        # synchronous full redraw at animation-frame rate is unnecessarily
        # heavy.
        pulse_rects_linewidth(canvas_widget, new_rects, target_width=2, on_step=canvas.draw_idle)


def display_canvas(app, fig):
    app.canvas = FigureCanvasTkAgg(fig, master=app.graph_frame)
    app.canvas.draw()
    app.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
