import tkinter as tk
from tkinter import messagebox
import pandas as pd
from UI_Setup import get_asset_path


def popup_uniform_series(app, series_id):
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

    def on_graph_button_click(event=None):
        try:
            # Validate and parse cash flow amount
            amount = amount_entry.get()
            try:
                amount = float(amount)
                if amount == 0:
                    raise ValueError("Amount must be non-zero.")
            except ValueError:
                raise ValueError("Amount must be a valid number with no other characters besides #'s and a '.'.")

            # Validate and parse starting period
            try:
                start_year = int(start_year_entry.get())
                if start_year < 0 or start_year > 100:
                    raise ValueError("Starting Year must be an integer between 0 and 100.")
            except ValueError:
                raise ValueError("Starting Year must be an integer between 0 and 100.")

            # Validate and parse series length
            try:
                length = int(length_entry.get())
                if length < 1 or start_year + length - 1 > 100:
                    raise ValueError("Length of Series must maintain the years between 0 and 100.")
            except ValueError:
                raise ValueError("Length of Series must maintain the years between 0 and 100.")

            # Validate series name input
            series_name = series_name_entry.get().strip()
            if not series_name:
                raise ValueError("Series name cannot be empty.")

            # Assign a color to the series using the cyclic iterator
            color = next(app.colors)

            # Create uniform cash flow entries
            for period in range(start_year, start_year + length):
                new_entry = pd.DataFrame({
                    "Period": [period],
                    "Cash Flow": [amount],
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
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            # Ensure the popup stays on top and focused
            top.lift()
            top.focus_force()

    # Create the popup window for uniform series input
    top = tk.Toplevel(app.root)
    top.title("Uniform Series Input")
    
    # Set the window icon
    try:
        icon_path = get_asset_path("app.ico")
        top.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not load icon for uniform series window: {e}")
    
    # Make window always on top
    top.attributes('-topmost', True)
    
    # Center the window after widgets are added
    top.update_idletasks()
    width = top.winfo_reqwidth()
    height = top.winfo_reqheight()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'+{x}+{y}')

    # Layout the form fields and labels
    tk.Label(top, text="Cash Flow Amount:").grid(row=0, column=0, padx=10, pady=5)
    amount_entry = tk.Entry(top, validate="key", validatecommand=(top.register(validate_cash_flow_input), '%P', '%d'))
    amount_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(top, text="Starting Period (0-100):").grid(row=1, column=0, padx=10, pady=5)
    start_year_entry = tk.Entry(top, validate="key", validatecommand=(top.register(validate_numeric_input), '%P', '%d'))
    start_year_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(top, text="Series Length:").grid(row=2, column=0, padx=10, pady=5)
    length_entry = tk.Entry(top, validate="key", validatecommand=(top.register(validate_numeric_input), '%P', '%d'))
    length_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(top, text="Series Name:").grid(row=3, column=0, padx=10, pady=5)
    series_name_entry = tk.Entry(top, validate="key",
                                 validatecommand=(top.register(validate_series_name_input), '%P', '%d'))
    series_name_entry.grid(row=3, column=1, padx=10, pady=5)

    graph_button = tk.Button(top, text="Graph", command=on_graph_button_click)
    graph_button.grid(row=4, columnspan=2, pady=10)

    # Bind Enter key for convenience to trigger form submission
    top.bind('<Return>', on_graph_button_click)
    amount_entry.bind('<Return>', on_graph_button_click)
    start_year_entry.bind('<Return>', on_graph_button_click)
    length_entry.bind('<Return>', on_graph_button_click)
    series_name_entry.bind('<Return>', on_graph_button_click)
