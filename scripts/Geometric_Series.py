"""Geometric series input dialog module.

Provides the dialog for adding geometric cash flow series to the diagram.
A geometric series increases by a constant percentage each period.
"""
import pandas as pd
from scripts.DialogKit import (
    create_popup, center_popup, build_form, add_field, add_error_label,
    show_error, clear_error, add_submit_button,
    validate_currency, validate_integer, validate_series_name,
)
from scripts.Toast import show_toast


def popup_geometric_series(app, series_id):
    def submit(event=None):
        clear_error(error_label)
        try:
            # Validate start year input
            try:
                start_year = int(start_year_entry.get())
            except ValueError:
                raise ValueError("Starting Period must be a valid integer.")

            # Validate initial value input with conversion to float
            initial_value = initial_value_entry.get()
            try:
                initial_value = float(initial_value)
                if initial_value == 0:
                    raise ValueError("Initial value must be non-zero.")
            except ValueError:
                raise ValueError("Initial value must be a valid number with no other characters besides #'s and a '.'.")

            # Validate series length input
            try:
                num_years = int(num_years_entry.get())
                if num_years < 1:
                    raise ValueError("Series Length must be at least 1.")
            except ValueError:
                raise ValueError("Series Length must be at least 1.")

            # Validate growth rate input with conversion to float
            growth_rate = growth_rate_entry.get()
            try:
                growth_rate = float(growth_rate)
            except ValueError:
                raise ValueError("Growth rate must be a valid number with no other characters besides #'s and a '.'.")

            # Convert growth rate percentage to decimal
            growth_rate /= 100.0

            # Validate series name input
            series_name = series_name_entry.get().strip()
            if not series_name:
                raise ValueError("Series name cannot be empty.")

            # Use a single color for all cash flows
            color = app.get_next_color()

            # Calculate the geometric series
            cash_flows = []
            for year in range(start_year, start_year + num_years):
                cash_flow_value = initial_value * ((1 + growth_rate) ** (year - start_year))
                cash_flows.append({
                    "Period": year,
                    "Cash Flow": cash_flow_value,
                    "Color": color,
                    "Series_ID": series_id,
                    "Series_Name": series_name
                })

            # Convert to DataFrame and ensure it has no all-NA columns
            new_cash_flows = pd.DataFrame(cash_flows).dropna(axis=1, how='all')

            # Update the app's cash flows
            app.cash_flows = app.cash_flows.dropna(axis=1, how='all')
            app.cash_flows = pd.concat([app.cash_flows, new_cash_flows], ignore_index=True)

            # Clear selections and update the plot
            app.selected_indices = []
            app.update_plot()
            popup.destroy()
            show_toast(app, f"Added {num_years} entries to '{series_name}'")

        except ValueError as e:
            show_error(error_label, str(e))

    # Create the popup window
    popup = create_popup(app, "Geometric Series Input")
    form = build_form(popup)

    start_year_entry = add_field(form, 0, "Starting Period:", validate_integer, default="0")
    initial_value_entry = add_field(form, 1, "Initial Cash Flow Amount:", validate_currency)
    num_years_entry = add_field(form, 2, "Series Length:", validate_integer)
    growth_rate_entry = add_field(form, 3, "Growth Rate (%):", validate_currency)
    series_name_entry = add_field(
        form, 4, "Series Name:", validate_series_name,
        default=f"Series {series_id}", select_default=True
    )

    error_label = add_error_label(form, 5)
    add_submit_button(form, 6, "Graph", submit)

    # Bind the "Enter" key to the submit function
    popup.bind('<Return>', submit)
    start_year_entry.bind('<Return>', submit)
    initial_value_entry.bind('<Return>', submit)
    num_years_entry.bind('<Return>', submit)
    growth_rate_entry.bind('<Return>', submit)
    series_name_entry.bind('<Return>', submit)

    start_year_entry.focus_set()
    center_popup(popup)
