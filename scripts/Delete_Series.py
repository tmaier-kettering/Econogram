"""Delete series module.

Provides functionality to delete selected cash flow series from the diagram.
"""
import pandas as pd
from tkinter import messagebox
from scripts.Create_Table import create_table  # Ensure the import at the top


def delete_selected_series(app):
    if not app.selected_indices:
        messagebox.showinfo("Selection Error", "No series selected for deletion.")
        return

    # Ensure all selected indices are within bounds and exist
    if not all(index in app.cash_flows.index for index in app.selected_indices):
        messagebox.showinfo("Selection Error",
                            "No series selected for deletion.")
        return

    # Retrieve series IDs based on selected index positions
    selected_series_ids = app.cash_flows.loc[app.selected_indices, "Series_ID"].unique()

    if messagebox.askyesno("Confirmation", "Are you sure you want to delete these series?"):
        # Remove series from cash_flows where Series_ID is in selected_series_ids
        app.cash_flows.drop(index=app.selected_indices, inplace=True)

        # Clear the table by calling create_table with an empty list
        create_table(app, [])

        # Clear the selection and update all dependent parts
        app.selected_indices = []
        app.update_plot()
        app.update_canvas()  # Ensure canvas is updated to reflect changes
