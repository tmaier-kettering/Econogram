"""Annual value calculation module.

Converts a single cash flow into an equivalent uniform series over a specified
number of periods using the specified interest rate.
"""
import tkinter as tk
from tkinter import simpledialog, messagebox
import pandas as pd
from scripts.Create_Table import create_table


def popup_annual_value(app, series_id):
    """Generate uniform annual cash flows from a selected cash flow using the Annual Value (AV) formula."""
    if not app.selected_indices:
        messagebox.showerror("Selection Error", "Please select a single cash flow first.")
        return

    if len(app.selected_indices) > 1:
        messagebox.showerror("Selection Error", "Please select only one cash flow.")
        return

    try:
        # Prompt the user to enter the number of periods
        num_periods = simpledialog.askinteger("Number of Periods", "Enter the number of periods:")
        if num_periods is None or num_periods <= 0:
            messagebox.showerror("Input Error", "Please enter a valid number of periods.")
            return

        # Get the selected cash flow and app settings
        selected_index = app.selected_indices[0]
        selected_cash_flow = app.cash_flows.loc[selected_index, "Cash Flow"]
        selected_period = app.cash_flows.loc[selected_index, "Period"]
        series_name = app.cash_flows.loc[selected_index, "Series_Name"]
        interest_rate = app.interest_rate / 100  # Convert interest rate from percentage to decimal

        # Calculate the annual value (A) based on the selected cash flow (PV) and number of periods
        if interest_rate != 0:
            A = selected_cash_flow * (interest_rate) / (1 - (1 + interest_rate) ** -num_periods)
        else:  # Handle the edge case of zero interest rate
            A = selected_cash_flow / num_periods

        # Update the series name to include a reference to Annual Value
        rendered_series_name = f"AV of {series_name}"  # Use 'AV of' for Annual Value reference

        if app.makeNewSeries:
            # Create a new series with a new color and series ID
            selected_color = app.get_next_color()  # Assign a new unique color for the new cash flows
            new_series_id = app._get_next_series_id()
        else:
            # Use the original series color and ID, and delete the original cash flow
            selected_color = app.cash_flows.loc[selected_index, "Color"]
            new_series_id = app.cash_flows.loc[selected_index, "Series_ID"]
            # Delete the original cash flow
            app.cash_flows = app.cash_flows.drop(app.selected_indices).reset_index(drop=True)

        # Generate the uniform series of cash flows, starting one year after the selected period
        new_cash_flows = pd.DataFrame([{
            "Period": selected_period + period + 1,  # Start one year after the selected period
            "Cash Flow": A,
            "Color": selected_color,  # Assign the color
            "Series_ID": new_series_id,  # Include the series_id for the new cash flows
            "Series_Name": rendered_series_name  # Include the updated series name
        } for period in range(num_periods)])

        # Append the new annual series to the cash flows
        app.cash_flows = pd.concat([app.cash_flows, new_cash_flows], ignore_index=True)

        # Clear and update the table
        create_table(app, [])  # Reset or refresh the table with updated rows

        # Clear selections and update the plot
        app.selected_indices = []
        app.update_plot()

    except Exception as e:
        # Handle unexpected errors gracefully
        messagebox.showerror("Error", f"An error occurred: {str(e)}")