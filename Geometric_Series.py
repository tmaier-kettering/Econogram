import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os


def popup_geometric_series(app, series_id):
    def validate_cash_flow_input(entry_text, action_type):
        # Allow negative numbers, at most one decimal point, and handle intermediate states
        if action_type == '1':  # If inserting a character
            if entry_text in {'-', '-.', '.'}:  # Allow intermediate input like '-' or '-.' or '.'
                return True
            if not (
                    entry_text.replace('-', '', 1).replace('.', '',
                                                           1).isdigit() and  # Remove '-' and '.' for digit check
                    entry_text.count('-') <= 1 and  # Ensure at most one negative sign
                    entry_text.count('.') <= 1 and  # Ensure at most one decimal point
                    (entry_text.find('-') <= 0)  # Ensure '-' is only at the start
            ):
                return False
            # Check for more than two decimal places
            if '.' in entry_text and len(entry_text.split('.')[1]) > 2:
                return False
            if len(entry_text) > 10:  # Restrict total input length
                return False
        return True

    def validate_numeric_input(entry_text, action_type):
        # Allow only numeric input with a maximum length of 3 characters
        if action_type == '1' and (not entry_text.isdigit() or len(entry_text) >= 4):
            return False
        return True

    def validate_series_name_input(entry_text, action_type):
        # Limit the series name to 15 characters
        if action_type == '1' and len(entry_text) >= 15:
            return False
        return True

    def submit(event=None):
        try:
            # Validate start year input
            try:
                start_year = int(start_year_entry.get())
                if start_year < 0 or start_year > 100:
                    raise ValueError("Starting Year must be an integer between 0 and 100.")
            except ValueError:
                raise ValueError("Starting Year must be an integer between 0 and 100.")

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
                if num_years < 1 or start_year + num_years > 100:
                    raise ValueError("Series Length must maintain the years between 0 and 100.")
            except ValueError:
                raise ValueError("Series Length must maintain the years between 0 and 100.")

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
            color = next(app.colors)

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

        except ValueError as e:
            messagebox.showerror("Input Error", str(e), parent=popup)
            # Ensure the window remains on top and focused
            popup.lift()
            popup.focus_force()

    # Create the popup window
    popup = tk.Toplevel(app.root)
    popup.title("Geometric Series Input")
    
    # Set the window icon
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "app.ico")
        popup.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not load icon for geometric series window: {e}")

    tk.Label(popup, text="Starting Period:").grid(row=0, column=0, padx=10, pady=5)
    start_year_entry = tk.Entry(popup, validate="key",
                                validatecommand=(popup.register(validate_numeric_input), '%P', '%d'))
    start_year_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(popup, text="Initial Cash Flow Amount:").grid(row=1, column=0, padx=10, pady=5)
    initial_value_entry = tk.Entry(popup, validate="key",
                                   validatecommand=(popup.register(validate_cash_flow_input), '%P', '%d'))
    initial_value_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(popup, text="Series Length:").grid(row=2, column=0, padx=10, pady=5)
    num_years_entry = tk.Entry(popup, validate="key",
                               validatecommand=(popup.register(validate_numeric_input), '%P', '%d'))
    num_years_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(popup, text="Growth Rate (%):").grid(row=3, column=0, padx=10, pady=5)
    growth_rate_entry = tk.Entry(popup, validate="key",
                                 validatecommand=(popup.register(validate_cash_flow_input), '%P', '%d'))
    growth_rate_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(popup, text="Series Name:").grid(row=4, column=0, padx=10, pady=5)
    series_name_entry = tk.Entry(popup, validate="key",
                                 validatecommand=(popup.register(validate_series_name_input), '%P', '%d'))
    series_name_entry.grid(row=4, column=1, padx=10, pady=5)

    submit_button = tk.Button(popup, text="Graph", command=submit)
    submit_button.grid(row=5, columnspan=2, pady=10)

    # Bind the "Enter" key to the submit function
    popup.bind('<Return>', submit)
    start_year_entry.bind('<Return>', submit)
    initial_value_entry.bind('<Return>', submit)
    num_years_entry.bind('<Return>', submit)
    growth_rate_entry.bind('<Return>', submit)
    series_name_entry.bind('<Return>', submit)
