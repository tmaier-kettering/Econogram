import pandas as pd
from tkinter import simpledialog, messagebox, Tk
from scripts.Create_Table import create_table


def calculate_present_value(cash_flow, rate, periods):
    """Calculate the present value of a cash flow using the given rate and periods."""
    return cash_flow * ((1 + rate) ** periods)


def check_cash_flow_position(initial_period, new_period):
    """Ensure that cash flow is not moved forward in time."""
    if new_period > initial_period:
        show_warning()
        return False  # Cancel operation
    return True  # Allow operation


def show_warning():
    """Display a warning about moving cash flows forward in time."""
    root = Tk()
    root.withdraw()  # Hide main window
    messagebox.showwarning(
        "Warning",
        "You cannot move your cash flow forward in time using the present value function. "
        "Please select the future value function instead."
    )
    root.destroy()


def popup_present_value(app):
    """Calculate the present value of selected cash flows or series."""
    if not app.selected_indices:
        messagebox.showinfo("Info", "Please select a cash flow or series first.")
        return

    try:
        selected_cash_flows = app.cash_flows.loc[app.selected_indices]

        # Check if the selected cash flows belong to a single series, or if that series has more than one cash flow
        series_id_counts = selected_cash_flows["Series_ID"].value_counts()
        if any(series_id_counts > 1):
            # Handle multiple cash flows within a single series
            for series_id, count in series_id_counts.items():
                if count > 1:
                    series_cash_flows = selected_cash_flows[selected_cash_flows["Series_ID"] == series_id]
                    smallest_period = series_cash_flows["Period"].min()
                    new_period = smallest_period - 1

                    # Ensure cash flow is not being moved forward in time
                    if not check_cash_flow_position(smallest_period, new_period):
                        return  # Stop the operation

                    # Calculate the combined present value
                    combined_value = 0
                    for _, row in series_cash_flows.iterrows():
                        cash_flow = row["Cash Flow"]
                        current_period = row["Period"]
                        periods_difference = new_period - current_period
                        combined_value += calculate_present_value(
                            cash_flow, app.interest_rate / 100, periods_difference
                        )

                    if app.makeNewSeries:
                        make_new_series_for_multiple_cash_flow(app, combined_value, new_period, series_cash_flows)
                    else:
                        update_series_for_multiple_cash_flow(app, combined_value, new_period, series_cash_flows,
                                                             series_id)

        else:
            # Handle single cash flow or one-cash-flow series
            new_period = simpledialog.askinteger("Input", "Enter period to move the cash flow to:")
            if new_period is not None:

                initial_period = selected_cash_flows["Period"].min()

                # Ensure cash flow is not being moved forward in time
                if not check_cash_flow_position(initial_period, new_period):
                    return  # Stop the operation

                # Calculate the combined present value
                combined_value = 0
                for _, row in selected_cash_flows.iterrows():
                    cash_flow = row["Cash Flow"]
                    current_period = row["Period"]
                    periods_difference = new_period - current_period
                    combined_value += calculate_present_value(cash_flow, app.interest_rate / 100, periods_difference)

                if app.makeNewSeries:
                    make_new_series_for_single_cash_flow(app, combined_value, new_period, selected_cash_flows)
                else:
                    update_series_for_single_cash_flow(app, combined_value, new_period, selected_cash_flows)

        # Clear the table and update selections/visualizations
        create_table(app, [])  # Clear or reset the displayed table

        app.selected_indices = []  # Clear selected indices
        for rect in app.selection_rects:
            rect.set_bounds(0, 0, 0, 0)  # Reset selection rectangles
        for text in app.value_texts:
            text.remove()  # Remove any value text over bars
        app.value_texts = []

        # Update the plot to reflect changes
        app.update_plot()

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))


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
    rendered_series_name = f"PV of {original_series_name}"
    # Create a new entry for the calculated present value
    new_series_id = app._get_next_series_id()
    color = app.get_next_color()  # Assign a new unique color
    new_entry = pd.DataFrame({
        "Period": [new_period],
        "Cash Flow": [combined_value],
        "Color": [color],
        "Series_ID": [new_series_id],
        "Series_Name": [rendered_series_name]
    })
    # Add the calculated present value to the app's cash flows
    app.cash_flows = pd.concat([app.cash_flows, new_entry], ignore_index=True)


def make_new_series_for_single_cash_flow(app, combined_value, new_period, selected_cash_flows):
    # Create a name for the calculated series
    original_series_name = selected_cash_flows["Series_Name"].iloc[0]
    rendered_series_name = f"PV of {original_series_name}"
    # Create a new entry for the calculated present value
    new_series_id = app._get_next_series_id()
    color = app.get_next_color()  # Assign a new unique color
    new_entry = pd.DataFrame({
        "Period": [new_period],
        "Cash Flow": [combined_value],
        "Color": [color],
        "Series_ID": [new_series_id],
        "Series_Name": [rendered_series_name]
    })
    # Add the calculated present value to the app's cash flows
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
