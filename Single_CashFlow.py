import pandas as pd
import tkinter as tk
from tkinter import messagebox
from UI_Setup import get_asset_path


def popup_add_single_cash_flow(app, series_id):
    def validate_cash_flow_input(entry_text, action_type):
        # Allow negative numbers and at most one decimal point; also handle intermediate states
        if action_type == '1':  # If we're inserting a character
            if entry_text in {'-', '-.', '.'}:  # Allow '-' or '-.' or '.' during input
                return True
            if not (
                    entry_text.replace('-', '', 1).replace('.', '', 1).isdigit() and  # Allows '-' and '.'
                    entry_text.count('-') <= 1 and  # Only one negative sign
                    entry_text.count('.') <= 1 and  # Only one decimal point
                    (entry_text.find('-') <= 0)  # Negative sign must be at the first position
            ):
                return False
            # Check for more than two decimal places
            if '.' in entry_text and len(entry_text.split('.')[1]) > 2:
                return False
            if len(entry_text) > 10:  # Limit total input length
                return False
        return True

    def validate_period_input(entry_text, action_type):
        # Allow only numeric input with a maximum of 3 characters
        if action_type == '1' and (not entry_text.isdigit() or len(entry_text) >= 4):
            return False
        return True

    def validate_series_name_input(entry_text, action_type):
        # Limit the series name to 15 characters
        if action_type == '1' and len(entry_text) >= 15:
            return False
        return True

    def on_graph_button_click(event=None):
        try:
            # Validate period input
            try:
                period = int(period_entry.get())
                if period < 0 or period > 100:
                    raise ValueError("Period must be an integer between 0 and 100.")
            except ValueError:
                raise ValueError("Period must be an integer between 0 and 100.")

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

            # Fetch the next color from the cyclic iterator in app
            color = next(app.colors)

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
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            # Ensure the window stays on top and focused
            top.lift()
            top.focus_force()

    # Create a top-level window
    top = tk.Toplevel(app.root)
    top.title("Single Cash Flow Input")
    
    # Set the window icon
    try:
        icon_path = get_asset_path("app.ico")
        top.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not load icon for single cash flow window: {e}")
    
    # Make window always on top
    top.attributes('-topmost', True)
    
    # Center the window
    top.update_idletasks()
    width = top.winfo_reqwidth()
    height = top.winfo_reqheight()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'+{x}+{y}')

    # Arrange the widgets using grid layout
    tk.Label(top, text="Cash Flow Amount:").grid(row=0, column=0, padx=10, pady=5)
    cash_flow_entry = tk.Entry(top, validate="key",
                               validatecommand=(top.register(validate_cash_flow_input), '%P', '%d'))
    cash_flow_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(top, text="Period (0-100):").grid(row=1, column=0, padx=10, pady=5)
    period_entry = tk.Entry(top, validate="key", validatecommand=(top.register(validate_period_input), '%P', '%d'))
    period_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(top, text="Series Name:").grid(row=2, column=0, padx=10, pady=5)
    series_name_entry = tk.Entry(top, validate="key",
                                 validatecommand=(top.register(validate_series_name_input), '%P', '%d'))
    series_name_entry.grid(row=2, column=1, padx=10, pady=5)

    graph_button = tk.Button(top, text="Graph", command=on_graph_button_click)
    graph_button.grid(row=3, columnspan=2, pady=10)

    # Bind the "Enter" key to the on_graph_button_click function for convenience
    top.bind('<Return>', on_graph_button_click)
    # Additionally bind the "Enter" key on specific entry widgets
    cash_flow_entry.bind('<Return>', on_graph_button_click)
    period_entry.bind('<Return>', on_graph_button_click)
    series_name_entry.bind('<Return>', on_graph_button_click)
