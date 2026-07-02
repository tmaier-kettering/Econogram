"""Single cash flow input dialog module.

Provides the dialog for adding individual single cash flows to the diagram.
"""
import pandas as pd
from scripts.DialogKit import (
    create_popup, center_popup, build_form, add_field, add_error_label,
    show_error, clear_error, add_submit_button,
    validate_currency, validate_integer, validate_series_name,
)
from scripts.Toast import show_toast


def popup_add_single_cash_flow(app, series_id):
    def on_graph_button_click(event=None):
        clear_error(error_label)
        try:
            # Validate period input
            try:
                period = int(period_entry.get())
            except ValueError:
                raise ValueError("Period must be a valid integer.")

            # Validate and convert cash flow input to float
            cash_flow = cash_flow_entry.get()
            try:
                cash_flow = float(cash_flow)
                if cash_flow == 0:
                    raise ValueError("Cash flow must be non-zero.")
            except ValueError:
                raise ValueError(
                    "Cash flow must be a valid number with no other characters besides #'s and a '.'.")

            # Validate series name input
            series_name = series_name_entry.get().strip()
            if not series_name:
                raise ValueError("Series name cannot be empty.")

            # Fetch the next color from the color manager
            color = app.get_next_color()

            # Create a new DataFrame entry with the validated inputs
            new_entry = pd.DataFrame({
                "Period": [period],
                "Cash Flow": [cash_flow],
                "Color": [color],  # Use the next color in the cycle
                "Series_ID": [series_id],
                "Series_Name": [series_name]
            })

            # Filter out all-NA columns in the new entry
            new_entry_filtered = new_entry.dropna(axis=1, how='all')

            # Ensure app.cash_flows does not have all-NA columns
            app.cash_flows = app.cash_flows.dropna(axis=1, how='all')

            # Concatenate the filtered DataFrames
            app.cash_flows = pd.concat([app.cash_flows, new_entry_filtered], ignore_index=True)
            app.update_plot()
            top.destroy()
            show_toast(app, f"Added 1 entry to '{series_name}'")
        except ValueError as e:
            show_error(error_label, str(e))

    # Create a top-level window
    top = create_popup(app, "Single Cash Flow Input")
    form = build_form(top)

    cash_flow_entry = add_field(form, 0, "Cash Flow Amount:", validate_currency)
    period_entry = add_field(form, 1, "Period:", validate_integer, default="0")
    series_name_entry = add_field(
        form, 2, "Series Name:", validate_series_name,
        default=f"Series {series_id}", select_default=True
    )

    error_label = add_error_label(form, 3)
    add_submit_button(form, 4, "Graph", on_graph_button_click)

    # Bind the "Enter" key to the on_graph_button_click function for convenience
    top.bind('<Return>', on_graph_button_click)
    cash_flow_entry.bind('<Return>', on_graph_button_click)
    period_entry.bind('<Return>', on_graph_button_click)
    series_name_entry.bind('<Return>', on_graph_button_click)

    cash_flow_entry.focus_set()
    center_popup(top)
