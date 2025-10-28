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
            selected_index = split_listbox.curselection()
            if not selected_index:
                messagebox.showerror("Selection Error", "Please select a split point.")
                top.lift()
                top.focus_force()
                return
            
            # Get the split point index (this is the index in the listbox)
            split_idx = selected_index[0]
            
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
            
            # Get the color for the series
            original_color = series_data.iloc[0]["Color"]
            color1 = original_color
            color2 = next(app.colors)
            
            # Split the data
            series1_mask = (app.cash_flows["Series_ID"] == series_id) & (app.cash_flows["Period"] <= split_period)
            series2_mask = (app.cash_flows["Series_ID"] == series_id) & (app.cash_flows["Period"] > split_period)
            
            # Update the first part
            app.cash_flows.loc[series1_mask, "Series_ID"] = series1_id
            app.cash_flows.loc[series1_mask, "Series_Name"] = series1_name
            app.cash_flows.loc[series1_mask, "Color"] = color1
            
            # Update the second part
            app.cash_flows.loc[series2_mask, "Series_ID"] = series2_id
            app.cash_flows.loc[series2_mask, "Series_Name"] = series2_name
            app.cash_flows.loc[series2_mask, "Color"] = color2
            
            # Clear selection and update display
            app.selected_indices = []
            create_table(app, [])
            app.update_plot()
            app.update_canvas()
            
            top.destroy()
            messagebox.showinfo("Success", f"Series split into '{series1_name}' and '{series2_name}'.")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while splitting: {str(e)}")
            top.lift()
            top.focus_force()
    
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
    instruction_text = "Select where to split the series:"
    tk.Label(top, text=instruction_text, font=("Arial", 10, "bold")).pack(padx=10, pady=10)
    
    # Create listbox with scrollbar for split options
    frame = tk.Frame(top)
    frame.pack(padx=10, pady=5)
    
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    split_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, height=min(10, len(periods) - 1), width=40)
    split_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar.config(command=split_listbox.yview)
    
    # Populate the listbox with split options
    for i in range(len(periods) - 1):
        split_text = f"Between period {periods[i]} and {periods[i + 1]}"
        split_listbox.insert(tk.END, split_text)
    
    # Add split button
    split_button = tk.Button(top, text="Split", command=on_split_button_click)
    split_button.pack(pady=10)
    
    # Center the window
    top.update_idletasks()
    width = top.winfo_reqwidth()
    height = top.winfo_reqheight()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'+{x}+{y}')
