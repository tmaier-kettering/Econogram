"""Invert series module.

Inverts the sign of all cash flows in a selected series, converting inflows
to outflows and vice versa.
"""
import pandas as pd
from tkinter import messagebox
from scripts.Create_Table import create_table


def invert_selected_series(app):
    """Invert the sign of all cash flows in the selected series."""
    if not app.selected_indices:
        messagebox.showinfo("Selection Error", "No series selected for inversion.")
        return

    # Ensure all selected indices are within bounds and exist
    if not all(index in app.cash_flows.index for index in app.selected_indices):
        messagebox.showinfo("Selection Error",
                            "Selected series no longer exist.")
        return

    # Retrieve series IDs based on selected index positions
    selected_series_ids = app.cash_flows.loc[app.selected_indices, "Series_ID"].unique()

    # Invert the cash flow values for all selected series
    for series_id in selected_series_ids:
        series_mask = app.cash_flows["Series_ID"] == series_id
        app.cash_flows.loc[series_mask, "Cash Flow"] = -app.cash_flows.loc[series_mask, "Cash Flow"]

        create_table(app, [])

        # Clear the selection and update all dependent parts
        app.selected_indices = []
        app.update_plot()
        app.update_canvas()  # Ensure canvas is updated to reflect changes
