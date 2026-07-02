"""Split series module.

Splits a multi-cash-flow series into two separate series at a chosen point
using an interactive slider dialog.
"""
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import ttkbootstrap as tb
from scripts.Create_Table import create_table
from scripts.DialogKit import create_popup, center_popup
from scripts.Theme import COLORS, SPACING, get_fonts
from scripts.Toast import show_toast


def split_selected_series(app):
    """Split the selected series into two separate series at a chosen point using a slider."""
    if not app.selected_indices:
        messagebox.showinfo("Selection Error", "No series selected for splitting.")
        return

    # Ensure all selected indices are within bounds and exist
    if not all(index in app.cash_flows.index for index in app.selected_indices):
        messagebox.showinfo("Selection Error", "Selected series no longer exist.")
        return

    # Get the series ID from the selected indices
    selected_series_ids = app.cash_flows.loc[app.selected_indices, "Series_ID"].unique()

    if len(selected_series_ids) > 1:
        messagebox.showinfo("Selection Error", "Please select only one series to split.")
        return

    series_id = selected_series_ids[0]
    series_data = app.cash_flows[app.cash_flows["Series_ID"] == series_id].sort_values("Period")

    # Check if series has more than 1 entry
    if len(series_data) <= 1:
        messagebox.showinfo("Split Error", "Cannot split a series with length of 1 or less.")
        return

    # Get the periods in the series
    periods = series_data["Period"].tolist()

    # Open dialog to select split point
    show_split_dialog(app, series_id, series_data, periods)


def show_split_dialog(app, series_id, series_data, periods):
    """Display dialog for selecting the split point."""

    def on_split_button_click():
        """Handle the split operation."""
        try:
            # Get the split point index from the slider
            split_idx = slider_var.get()

            # The split point is between periods[split_idx] and periods[split_idx + 1]
            # So the first series includes periods[0] to periods[split_idx] (inclusive)
            # And the second series includes periods[split_idx + 1] to periods[-1] (inclusive)

            split_period = periods[split_idx]

            # Get original series name
            original_name = series_data.iloc[0]["Series_Name"]

            # Create names for the two new series
            series1_name = f"{original_name}_1"
            series2_name = f"{original_name}_2"

            # Get new series IDs
            series1_id = app._get_next_series_id()
            series2_id = app._get_next_series_id()

            # Get the color for the series and assign different colors
            original_color = series_data.iloc[0]["Color"]
            color1 = original_color
            color2 = app.get_next_color()

            # Split the data
            series1_mask = (app.cash_flows["Series_ID"] == series_id) & (app.cash_flows["Period"] <= split_period)
            series2_mask = (app.cash_flows["Series_ID"] == series_id) & (app.cash_flows["Period"] > split_period)

            # Update the first part
            series1_indices = app.cash_flows[series1_mask].index
            app.cash_flows.loc[series1_mask, "Series_ID"] = series1_id
            app.cash_flows.loc[series1_mask, "Series_Name"] = series1_name
            app.cash_flows.loc[series1_mask, "Color"] = pd.Series([color1] * len(series1_indices), index=series1_indices)

            # Update the second part
            series2_indices = app.cash_flows[series2_mask].index
            app.cash_flows.loc[series2_mask, "Series_ID"] = series2_id
            app.cash_flows.loc[series2_mask, "Series_Name"] = series2_name
            app.cash_flows.loc[series2_mask, "Color"] = pd.Series([color2] * len(series2_indices), index=series2_indices)

            # Clear selection and update display
            app.selected_indices = []
            create_table(app, [])
            app.update_plot()
            app.update_canvas()

            top.destroy()
            show_toast(app, f"Split into '{series1_name}' and '{series2_name}'")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while splitting: {str(e)}")
            top.lift()
            top.focus_force()

    def update_split_label(value):
        """Update the label showing the current split position."""
        idx = int(float(value))
        # Safety check (though slider range prevents this)
        if idx + 1 < len(periods):
            split_label.config(text=f"Split between period {periods[idx]} and {periods[idx + 1]}")

    # Create the popup window
    top = create_popup(app, "Split Series")
    fonts = get_fonts()

    # Add instruction label
    instruction_text = "Drag the slider to choose where to split the series:"
    ttk.Label(top, text=instruction_text, font=fonts["body_bold"]).pack(
        padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["sm"])
    )

    # Create a frame for the slider and labels
    slider_frame = ttk.Frame(top)
    slider_frame.pack(padx=SPACING["lg"], pady=SPACING["sm"], fill=tk.X)

    # Add period labels on sides
    ttk.Label(slider_frame, text=f"Period {periods[0]}", font=fonts["body"], foreground=COLORS["muted"]).pack(side=tk.LEFT)
    ttk.Label(slider_frame, text=f"Period {periods[-1]}", font=fonts["body"], foreground=COLORS["muted"]).pack(side=tk.RIGHT)

    # Create slider variable
    slider_var = tk.IntVar(value=0)

    # Create the slider
    slider = tb.Scale(
        top,
        from_=0,
        to=len(periods) - 2,
        orient=tk.HORIZONTAL,
        variable=slider_var,
        length=400,
        bootstyle="primary",
        command=update_split_label
    )
    slider.pack(padx=SPACING["lg"], pady=(0, SPACING["sm"]))

    # Label to show current split position
    split_label = ttk.Label(
        top, text=f"Split between period {periods[0]} and {periods[1]}",
        font=fonts["body_bold"], foreground=COLORS["accent"]
    )
    split_label.pack(padx=SPACING["lg"], pady=(SPACING["xs"], SPACING["lg"]))

    # Add split button
    split_button = tb.Button(top, text="Split", command=on_split_button_click, bootstyle="primary")
    split_button.pack(pady=(0, SPACING["lg"]))

    top.bind('<Return>', lambda e: on_split_button_click())
    center_popup(top)