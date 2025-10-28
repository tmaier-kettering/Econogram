"""Combine cash flows module.

Combines multiple cash flows occurring in the same period into a single aggregated value.
"""
import pandas as pd
from tkinter import messagebox
from scripts.Create_Table import create_table


def combine_cash_flows(app):
    """Combine multiple cash flows in the same period into a single cash flow."""
    if len(app.selected_indices) < 2:
        messagebox.showinfo("Info", "Please select multiple cash flows in the same period to combine.")
        return

    # Check if the selected cash flows are from the same period
    periods = app.cash_flows.loc[app.selected_indices, "Period"]
    if len(periods.unique()) > 1:
        messagebox.showerror("Error", "Selected cash flows must be in the same period to be combined.")
        return

    try:
        # Calculate the combined cash flow value
        combined_value = app.cash_flows.loc[app.selected_indices, "Cash Flow"].sum()
        period = periods.iloc[0]

        # Extract the selected cash flows
        selected_cash_flows = app.cash_flows.loc[app.selected_indices]

        # Generate a new series ID for the combined entry
        new_series_id = app._get_next_series_id()

        # Combine series names into a single name
        series_name = " + ".join(selected_cash_flows["Series_Name"].unique())

        # Assign a new color using the color manager
        color = app.get_next_color()

        # Create a new entry for the combined cash flow
        new_entry = pd.DataFrame({
            "Period": [period],
            "Cash Flow": [combined_value],
            "Color": [color],
            "Series_ID": [new_series_id],
            "Series_Name": [series_name]
        })

        # Remove the selected cash flows from the DataFrame
        app.cash_flows = app.cash_flows.drop(app.selected_indices).reset_index(drop=True)

        # Add the new combined cash flow entry
        app.cash_flows = pd.concat([app.cash_flows, new_entry], ignore_index=True)

        create_table(app, [])

        # Reset app selections and visuals
        app.selected_indices = []  # Clear selected indices
        for rect in app.selection_rects:
            rect.set_bounds(0, 0, 0, 0)  # Reset highlighted rectangles
        for text in app.value_texts:
            text.remove()  # Remove any text over the bars
        app.value_texts = []

        # Update the application plot with new data
        app.update_plot()

    except Exception as e:
        # Show error message if any exception occurs
        messagebox.showerror("Error", str(e))
