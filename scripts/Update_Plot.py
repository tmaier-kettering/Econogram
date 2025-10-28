import tkinter as tk
from tkinter import messagebox, simpledialog
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle, Patch, FancyArrow
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scripts.Create_Table import create_table
from scripts.Clear_Graph import clear_graph


def update_plot(app):
    # Initialize or clear previous canvas
    if hasattr(app, 'canvas') and app.canvas:
        app.canvas.get_tk_widget().pack_forget()

    # Create new figure and axes
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.subplots_adjust(right=0.7)
    app.selection_rects = []

    # Ensure there are cash flows to plot
    if not app.cash_flows.empty:
        create_bars(ax, app)
        set_y_limits_with_buffer(ax)
        configure_axes(ax, app)
        add_legend(ax, app)
        configure_event_handling(fig, ax, app)

    # Display the canvas within the GUI
    display_canvas(app, fig)


def create_bars(ax, app):
    # Loop through each period and create arrows for cash flows
    for period in app.cash_flows["Period"].unique():
        period_cash_flows = app.cash_flows[app.cash_flows["Period"] == period].sort_values(
            by="Cash Flow", ascending=False
        )
        bottom_positive, bottom_negative = 0, 0
        for i, row in period_cash_flows.iterrows():
            cash_flow = row["Cash Flow"]
            bottom = bottom_positive if cash_flow >= 0 else bottom_negative
            
            # Create an arrow instead of a bar
            # Arrow parameters
            arrow_width = 0.4  # Width of the arrow shaft
            head_width = 0.6  # Width of the arrow head
            head_length = abs(cash_flow) * 0.1 if cash_flow != 0 else 0.1  # Head length proportional to cash flow
            
            # Create the arrow starting from bottom, pointing up for positive, down for negative
            if cash_flow >= 0:
                # Upward arrow
                arrow = FancyArrow(period, bottom, 0, cash_flow, 
                                 width=arrow_width, 
                                 head_width=head_width, 
                                 head_length=min(head_length, abs(cash_flow) * 0.9),
                                 length_includes_head=True,
                                 color=row["Color"], 
                                 edgecolor='black',
                                 linewidth=0.5)
            else:
                # Downward arrow
                arrow = FancyArrow(period, bottom, 0, cash_flow, 
                                 width=arrow_width, 
                                 head_width=head_width, 
                                 head_length=min(head_length, abs(cash_flow) * 0.9),
                                 length_includes_head=True,
                                 color=row["Color"], 
                                 edgecolor='black',
                                 linewidth=0.5)
            
            ax.add_patch(arrow)
            arrow.set_gid(i)
            
            if cash_flow >= 0:
                bottom_positive += cash_flow
            else:
                bottom_negative += cash_flow


def set_y_limits_with_buffer(ax):
    buffer_percentage = 0.25
    ymin, ymax = ax.get_ylim()
    y_range = ymax - ymin
    ax.set_ylim(bottom=ymin - buffer_percentage * y_range, top=ymax + buffer_percentage * y_range)
    ax.axhline(0, color='black', linewidth=0.5)


def configure_axes(ax, app):
    ax.set_xlabel("Period")
    ax.set_ylabel("Cash Flow")
    ax.set_title("Cash Flow Diagram")
    max_period = app.cash_flows["Period"].max()
    min_period = app.cash_flows["Period"].min()
    tick_interval = 1 if max_period <= 20 else (2 if max_period <= 50 else 5)
    next_tick_mark = ((max_period // tick_interval) + 1) * tick_interval
    ax.set_xticks(range(min(0, min_period), next_tick_mark + 1, tick_interval))
    ax.set_xlim(left=min(-0.5, min_period - 0.5), right=next_tick_mark + 0.5)


def add_legend(ax, app):
    series_info = app.cash_flows[['Series_Name', 'Color']].drop_duplicates().sort_values('Series_Name')
    if not series_info.empty:
        legend_handles = [
            Patch(facecolor=row['Color'], edgecolor='black', label=row["Series_Name"], picker=True)
            for _, row in series_info.iterrows()
        ]
        ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0)


def configure_event_handling(fig, ax, app):
    def on_click(event):
        handle_click(event, ax, app)

    fig.canvas.mpl_connect("button_press_event", on_click)


def handle_click(event, ax, app):
    if event.inaxes:
        try:
            clicked_bar = next((bar for bar in ax.patches if bar.contains(event)[0]), None)
            if clicked_bar:
                if event.button == 3:  # Right-click
                    handle_bar_selection(clicked_bar, ax, app, right_click=True)
                    update_selection_display(ax, app)
                    show_context_menu(event, app)
                    return
                else:  # Left-click
                    handle_bar_selection(clicked_bar, ax, app, right_click=False)
        except KeyError as e:
            print(f"Error: No matching series or invalid bar data - {str(e)}")

    update_selection_display(ax, app)


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
    
    # Add menu items for each operation
    context_menu.add_command(label="Present Value", command=app.popup_present_value)
    context_menu.add_command(label="Future Value", command=app.popup_future_value)
    context_menu.add_command(label="Annual Value", command=app.popup_annual_value)
    context_menu.add_separator()
    context_menu.add_command(label="Combine Cash Flow", command=app.combine_cash_flows)
    context_menu.add_command(label="Invert Series", command=app.invert_selected_series)
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
    for rect in app.selection_rects:
        rect.set_visible(False)
    app.selection_rects.clear()

    selected_values = []
    for patch in ax.patches:
        patch_id = patch.get_gid()
        if patch_id in app.selected_indices:
            # Get the bounding box of the arrow/patch
            bbox = patch.get_extents()
            x0, y0 = bbox.x0, bbox.y0
            width = bbox.width
            height = bbox.height
            
            selection_rect = Rectangle(
                (x0, y0), width, height,
                linewidth=2, edgecolor='r', facecolor='none'
            )
            ax.add_patch(selection_rect)
            app.selection_rects.append(selection_rect)

            period = app.cash_flows.loc[patch_id, "Period"]
            cash_flow_value = app.cash_flows.loc[patch_id, "Cash Flow"]
            series_name = app.cash_flows.loc[patch_id, "Series_Name"]
            selected_values.append([series_name, period, cash_flow_value])

    create_table(app, selected_values) if selected_values else create_table(app, [])
    app.update_canvas()


def display_canvas(app, fig):
    app.canvas = FigureCanvasTkAgg(fig, master=app.graph_frame)
    app.canvas.draw()
    app.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
