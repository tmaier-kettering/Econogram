"""Gradient series input dialog module.

Provides the dialog for adding gradient cash flow series to the diagram.
A gradient series increases by a constant amount each period, starting from zero.
"""
import pandas as pd
from scripts.DialogKit import (
    create_popup, center_popup, build_form, add_field, add_error_label,
    show_error, clear_error, add_submit_button,
    validate_currency, validate_integer, validate_series_name,
)
from scripts.Toast import show_toast


def popup_gradient_series(app, series_id):
    def on_graph_button_click(event=None):
        clear_error(error_label)
        try:
            # Validate and parse gradient amount
            gradient_value = gradient_value_entry.get()
            try:
                gradient_value = float(gradient_value)
            except ValueError:
                raise ValueError("Gradient value must be a valid number.")

            # Validate and parse starting period
            try:
                start_year = int(start_year_entry.get())
            except ValueError:
                raise ValueError("Starting Period must be a valid integer.")

            # Validate and parse series length
            try:
                length = int(length_entry.get())
                if length < 1:
                    raise ValueError("Length of Series must be at least 1.")
            except ValueError:
                raise ValueError("Length of Series must be at least 1.")

            # Validate series name input
            series_name = series_name_entry.get().strip()
            if not series_name:
                raise ValueError("Series name cannot be empty.")

            # Assign a color to the series using the color manager
            color = app.get_next_color()

            # Create gradient cash flow entries
            for i in range(length):
                period = start_year + i
                cash_flow = gradient_value * i  # Calculate cash flow for each period
                new_entry = pd.DataFrame({
                    "Period": [period],
                    "Cash Flow": [cash_flow],
                    "Color": [color],
                    "Series_ID": [series_id],
                    "Series_Name": [series_name]
                })

                new_entry_filtered = new_entry.dropna(axis=1, how='all')

                # Update the application's cash flows
                app.cash_flows = app.cash_flows.dropna(axis=1, how='all')
                app.cash_flows = pd.concat([app.cash_flows, new_entry_filtered], ignore_index=True)

            # Update the application plot and close the popup
            app.update_plot()
            top.destroy()
            show_toast(app, f"Added {length} entries to '{series_name}'")
        except ValueError as e:
            show_error(error_label, str(e))

    # Create the popup window for gradient series input
    top = create_popup(app, "Gradient Series Input")
    form = build_form(top)

    gradient_value_entry = add_field(form, 0, "Gradient Amount:", validate_currency)
    start_year_entry = add_field(form, 1, "Starting Period:", validate_integer, default="0")
    length_entry = add_field(form, 2, "Series Length:", validate_integer)
    series_name_entry = add_field(
        form, 3, "Series Name:", validate_series_name,
        default=f"Series {series_id}", select_default=True
    )

    error_label = add_error_label(form, 4)
    add_submit_button(form, 5, "Graph", on_graph_button_click)

    # Bind Enter key for convenience to trigger form submission
    top.bind('<Return>', on_graph_button_click)
    gradient_value_entry.bind('<Return>', on_graph_button_click)
    start_year_entry.bind('<Return>', on_graph_button_click)
    length_entry.bind('<Return>', on_graph_button_click)
    series_name_entry.bind('<Return>', on_graph_button_click)

    gradient_value_entry.focus_set()
    center_popup(top)
