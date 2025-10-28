import tkinter as tk
from tkinter import messagebox
import pandas as pd
from scripts.Create_Table import create_table
from scripts.UI_Setup import get_asset_path


def split_selected_series(app):
    """Split the selected series into two separate series at a chosen point."""
    if not app.selected_indices:
        messagebox.showinfo("Selection Error", "No series selected for splitting.")
        return

    # Ensure all selected indices are within bounds and exist
    if not all(index in app.cash_flows.index for index in app.selected_indices):
        messagebox.showinfo("Selection Error", "Selected series no longer exist.")
        return

    # Get the series ID from the selected indices
    selected_series_ids = app.cash_flows.loc[app.selected_indices, "Series_ID"].unique()

    if len(selected_series_ids) > 1:
        messagebox.showinfo("Selection Error", "Please select only one series to split.")
        return

    series_id = selected_series_ids[0]
    series_data = app.cash_flows[app.cash_flows["Series_ID"] == series_id].sort_values("Period")

    # Check if series has more than 1 entry
    if len(series_data) <= 1:
        messagebox.showinfo("Split Error", "Cannot split a series with length of 1 or less.")
        return

    # Get the periods in the series
    periods = series_data["Period"].tolist()

    # Open dialog to select split point
    show_split_dialog(app, series_id, series_data, periods)


def show_split_dialog(app, series_id, series_data, periods):
    """Display dialog for selecting the split point."""

    def on_split_button_click():
        """Handle the split operation."""
        try:
            # Get the split point index from the slider
            split_idx = slider_var.get()

            # The split point is between periods[split_idx] and periods[split_idx + 1]
            # So the first series includes periods[0] to periods[split_idx] (inclusive)
            # And the second series includes periods[split_idx + 1] to periods[-1] (inclusive)

            split_period = periods[split_idx]

            # Get original series name
            original_name = series_data.iloc[0]["Series_Name"]

            # Create names for the two new series
            series1_name = f"{original_name}_1"
            series2_name = f"{original_name}_2"

            # Get new series IDs
            series1_id = app._get_next_series_id()
            series2_id = app._get_next_series_id()

            # Get the color for the series and assign different colors
            original_color = series_data.iloc[0]["Color"]
            color1 = original_color
            color2 = next(app.colors)

            # Split the data
            series1_mask = (app.cash_flows["Series_ID"] == series_id) & (app.cash_flows["Period"] <= split_period)
            series2_mask = (app.cash_flows["Series_ID"] == series_id) & (app.cash_flows["Period"] > split_period)

            # Update the first part
            series1_indices = app.cash_flows[series1_mask].index
            app.cash_flows.loc[series1_mask, "Series_ID"] = series1_id
            app.cash_flows.loc[series1_mask, "Series_Name"] = series1_name
            app.cash_flows.loc[series1_mask, "Color"] = pd.Series([color1] * len(series1_indices), index=series1_indices)

            # Update the second part
            series2_indices = app.cash_flows[series2_mask].index
            app.cash_flows.loc[series2_mask, "Series_ID"] = series2_id
            app.cash_flows.loc[series2_mask, "Series_Name"] = series2_name
            app.cash_flows.loc[series2_mask, "Color"] = pd.Series([color2] * len(series2_indices), index=series2_indices)

            # Clear selection and update display
            app.selected_indices = []
            create_table(app, [])
            app.update_plot()
            app.update_canvas()

            top.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while splitting: {str(e)}")
            top.lift()
            top.focus_force()

    def update_split_label(value):
        """Update the label showing the current split position."""
        idx = int(float(value))
        # Safety check (though slider range prevents this)
        if idx + 1 < len(periods):
            split_label.config(text=f"Split between period {periods[idx]} and {periods[idx + 1]}")

    # Create the popup window
    top = tk.Toplevel(app.root)
    top.title("Split Series")

    # Set the window icon
    try:
        icon_path = get_asset_path("app.ico")
        top.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not load icon for split series window: {e}")

    # Make window always on top
    top.attributes('-topmost', True)

    # Add instruction label
    instruction_text = "Drag the slider to choose where to split the series:"
    tk.Label(top, text=instruction_text, font=("Arial", 10, "bold")).pack(padx=20, pady=(15, 5))

    # Create a frame for the slider and labels
    slider_frame = tk.Frame(top)
    slider_frame.pack(padx=20, pady=10, fill=tk.X)

    # Add period labels on sides
    tk.Label(slider_frame, text=f"Period {periods[0]}", font=("Arial", 9)).pack(side=tk.LEFT)
    tk.Label(slider_frame, text=f"Period {periods[-1]}", font=("Arial", 9)).pack(side=tk.RIGHT)

    # Create slider variable
    slider_var = tk.IntVar(value=0)

    # Create the slider
    slider = tk.Scale(
        top,
        from_=0,
        to=len(periods) - 2,
        orient=tk.HORIZONTAL,
        variable=slider_var,
        length=400,
        showvalue=False,
        command=update_split_label
    )
    slider.pack(padx=20, pady=(0, 10))

    # Label to show current split position
    split_label = tk.Label(top, text=f"Split between period {periods[0]} and {periods[1]}", font=("Arial", 10))
    split_label.pack(padx=20, pady=(5, 15))

    # Add split button
    split_button = tk.Button(top, text="Split", command=on_split_button_click, font=("Arial", 10, "bold"))
    split_button.pack(pady=(0, 15))

    # Center the window
    top.update_idletasks()
    width = top.winfo_reqwidth()
    height = top.winfo_reqheight()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'+{x}+{y}')