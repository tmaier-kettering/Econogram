import tkinter as tk
from tkinter import simpledialog, messagebox
import pandas as pd
from scripts.Create_Table import create_table


def calculate_future_value(cash_flow, rate, periods):
    """Calculate the future value of a cash flow using the given rate and periods."""
    return cash_flow * ((1 + rate) ** periods)


def check_cash_flow_position_forward(initial_period, new_period):
    """Ensure that cash flow is not moved backward in time."""
    if new_period < initial_period:
        show_warning_forward()
        return False  # Cancel the operation
    return True  # Allow the operation


def show_warning_forward():
    """Display a warning about moving cash flows backward in time."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showwarning(
        "Warning",
        "You cannot move your cash flow backward in time using the future value function. "
        "Please select the present value function instead."
    )
    root.destroy()


def popup_future_value(app):
    """Calculate and generate future value of selected cash flows."""
    if not app.selected_indices:
        messagebox.showinfo("Info", "Please select a cash flow or series first.")
        return

    try:
        # Validate selection
        valid_indices = app.cash_flows.index.intersection(app.selected_indices)
        if valid_indices.empty:
            messagebox.showinfo("Info", "Selected cash flows are no longer valid.")
            return

        selected_cash_flows = app.cash_flows.loc[valid_indices]

        # Check if the selected items are a single series or multiple items of one series
        series_id_counts = selected_cash_flows["Series_ID"].value_counts()
        if any(series_id_counts > 1):
            for series_id, count in series_id_counts.items():
                if count > 1:
                    # Handle a series with multiple cash flows
                    series_cash_flows = selected_cash_flows[selected_cash_flows["Series_ID"] == series_id]
                    new_period = series_cash_flows["Period"].max()  # Keep it at the last period
                    initial_period = series_cash_flows["Period"].min()

                    # Ensure the cash flow is moved forward in time (just double-checking, you can remove if not necessary)
                    if not check_cash_flow_position_forward(initial_period, new_period):
                        return

                    # Calculate combined future value
                    combined_value = 0
                    for _, row in series_cash_flows.iterrows():
                        cash_flow = row["Cash Flow"]
                        current_period = row["Period"]
                        periods_difference = new_period - current_period
                        combined_value += calculate_future_value(
                            cash_flow, app.interest_rate / 100, periods_difference
                        )

                    if app.makeNewSeries:
                        make_new_series_for_multiple_cash_flow(app, combined_value, new_period, series_cash_flows)
                    else:
                        update_series_for_multiple_cash_flow(app, combined_value, new_period, series_cash_flows,
                                                             series_id)

        else:
            # Handle a single cash flow or series with just one cash flow
            new_period = simpledialog.askinteger("Input", "Enter the period to move the cash flow to:")
            if new_period is not None:

                initial_period = selected_cash_flows["Period"].max()

                # Ensure the cash flow is moved forward in time
                if not check_cash_flow_position_forward(initial_period, new_period):
                    return

                # Calculate future value for the single cash flow
                combined_value = 0
                for _, row in selected_cash_flows.iterrows():
                    cash_flow = row["Cash Flow"]
                    current_period = row["Period"]
                    periods_difference = new_period - current_period
                    combined_value += calculate_future_value(
                        cash_flow, app.interest_rate / 100, periods_difference
                    )

                if app.makeNewSeries:
                    make_new_series_for_single_cash_flow(app, combined_value, new_period, selected_cash_flows)
                else:
                    update_series_for_single_cash_flow(app, combined_value, new_period, selected_cash_flows)

        # Clear and update the table
        create_table(app, [])  # Refresh or reset the displayed table

        # Reset selections and update the plot
        app.selected_indices = []
        for rect in app.selection_rects:
            rect.set_bounds(0, 0, 0, 0)  # Reset highlighted selection
        for text in app.value_texts:
            text.remove()  # Remove any text over chart bars
        app.value_texts = []

        # Update visual plot to reflect changes
        app.update_plot()

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
    except Exception as e:
        # Handle general exceptions gracefully
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def update_series_for_multiple_cash_flow(app, combined_value, new_period, series_cash_flows, series_id):
    # Update the series
    color = series_cash_flows["Color"].iloc[0]  # Assuming color is consistent within a series
    new_entry = pd.DataFrame({
        "Period": [new_period],
        "Cash Flow": [combined_value],
        "Color": [color],
        "Series_ID": [series_id],
        "Series_Name": [series_cash_flows["Series_Name"].iloc[0]]
    })
    app.cash_flows = app.cash_flows.drop(series_cash_flows.index).reset_index(drop=True)
    app.cash_flows = pd.concat([app.cash_flows, new_entry], ignore_index=True)


def make_new_series_for_multiple_cash_flow(app, combined_value, new_period, series_cash_flows):
    # Create a name for the calculated series
    original_series_name = series_cash_flows["Series_Name"].iloc[0]
    rendered_series_name = f"FV of {original_series_name}"
    # Create a new entry for the calculated future value
    new_series_id = app._get_next_series_id()
    color = next(app.colors)  # Assign a new unique color
    new_entry = pd.DataFrame({
        "Period": [new_period],
        "Cash Flow": [combined_value],
        "Color": [color],
        "Series_ID": [new_series_id],
        "Series_Name": [rendered_series_name]
    })
    # Add the calculated future value to the app's cash flows
    app.cash_flows = pd.concat([app.cash_flows, new_entry], ignore_index=True)


def make_new_series_for_single_cash_flow(app, combined_value, new_period, selected_cash_flows):
    # Create a name for the calculated series
    original_series_name = selected_cash_flows["Series_Name"].iloc[0]
    rendered_series_name = f"FV of {original_series_name}"
    # Create a new entry for the calculated future value
    new_series_id = app._get_next_series_id()
    color = next(app.colors)  # Assign a new unique color
    new_entry = pd.DataFrame({
        "Period": [new_period],
        "Cash Flow": [combined_value],
        "Color": [color],
        "Series_ID": [new_series_id],
        "Series_Name": [rendered_series_name]
    })
    # Add the calculated future value to the app's cash flows
    app.cash_flows = pd.concat([app.cash_flows, new_entry], ignore_index=True)


def update_series_for_single_cash_flow(app, combined_value, new_period, selected_cash_flows):
    series_id = selected_cash_flows["Series_ID"].iloc[0]
    series_name = selected_cash_flows["Series_Name"].iloc[0]
    color = selected_cash_flows["Color"].iloc[0]  # Assuming color is consistent within a series
    new_entry = pd.DataFrame({
        "Period": [new_period],
        "Cash Flow": [combined_value],
        "Color": [color],
        "Series_ID": [series_id],
        "Series_Name": [series_name]
    })
    app.cash_flows = app.cash_flows.drop(app.selected_indices).reset_index(drop=True)
    new_entry_cleaned = new_entry.dropna(how='all')
    app.cash_flows = pd.concat([app.cash_flows, new_entry_cleaned], ignore_index=True)
