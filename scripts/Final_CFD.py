import tkinter as tk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scripts.Update_Plot import update_plot
from scripts.UI_Setup import setup_ui, get_asset_path
from scripts.Uniform_Series import popup_uniform_series
from scripts.Combine_CashFlows import combine_cash_flows
from scripts.Single_CashFlow import popup_add_single_cash_flow
from scripts.Gradient_Series import popup_gradient_series
from scripts.Present_Value import popup_present_value
from scripts.Future_Value import popup_future_value
from scripts.Annual_Value import popup_annual_value
from scripts.Geometric_Series import popup_geometric_series
from scripts.Delete_Series import delete_selected_series
from scripts.Invert_Series import invert_selected_series
from scripts.Split_Series import split_selected_series
from scripts.Clear_Graph import clear_graph
from scripts.Create_Table import create_table


class ColorManager:
    """Manages color assignment for cash flow series, ensuring unique and reusable colors."""
    
    def __init__(self):
        # Base color palette from matplotlib's tab20
        self.base_colors = list(plt.colormaps["tab20"].colors)
        # Pool of available colors (initially all base colors)
        self.available_colors = self.base_colors.copy()
        # Track colors currently in use
        self.used_colors = set()
    
    def get_color(self):
        """Get a color for a new series."""
        # If we have available colors from the base palette or returned colors, use them
        if self.available_colors:
            color = self.available_colors.pop(0)
        else:
            # Generate a new distinct color using HSV color space
            color = self._generate_new_color()
        
        self.used_colors.add(color)
        return color
    
    def return_color(self, color):
        """Return a color to the available pool when a series is deleted."""
        if color in self.used_colors:
            self.used_colors.remove(color)
            # Only add to available pool if it's not already there
            if color not in self.available_colors:
                self.available_colors.append(color)
    
    def return_colors_not_in_dataframe(self, cash_flows_df):
        """Return colors that are no longer used in the DataFrame."""
        if cash_flows_df.empty:
            # All colors should be available
            self.available_colors = self.base_colors.copy()
            self.used_colors.clear()
        else:
            # Get colors currently in use
            current_colors = set(cash_flows_df["Color"].unique())
            # Return colors that are no longer in use
            for color in list(self.used_colors):
                if color not in current_colors:
                    self.return_color(color)
    
    def _generate_new_color(self):
        """Generate a new distinct color when base palette is exhausted."""
        # Use a deterministic but varied approach based on number of colors generated
        num_extra_colors = len(self.used_colors) - len(self.base_colors)
        
        # Generate color using HSV for better distribution
        # Vary hue primarily, with some saturation and value variation
        hue = (num_extra_colors * 0.618033988749895) % 1.0  # Golden ratio for good distribution
        saturation = 0.6 + (num_extra_colors % 3) * 0.15  # Vary between 0.6, 0.75, 0.9
        value = 0.7 + (num_extra_colors % 2) * 0.2  # Vary between 0.7 and 0.9
        
        # Convert HSV to RGB
        rgb = mcolors.hsv_to_rgb([hue, saturation, value])
        return tuple(rgb)
    
    def reset(self):
        """Reset the color manager to initial state."""
        self.available_colors = self.base_colors.copy()
        self.used_colors.clear()


class CashFlowDiagramApp:
    def __init__(self, root):
        self.toggle_makeNewSeries_button = None
        self.root = root
        self.root.title("Econogram")
        
        # Set the application icon
        try:
            icon_path = get_asset_path("app.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Maximize the window (cross-platform approach)
        try:
            # Try Windows/Mac method
            self.root.state('zoomed')
        except tk.TclError:
            # For Linux/Unix, use attributes
            try:
                self.root.attributes('-zoomed', True)
            except tk.TclError:
                # Fallback: set geometry to screen size
                self.root.update_idletasks()
                width = self.root.winfo_screenwidth()
                height = self.root.winfo_screenheight()
                self.root.geometry(f'{width}x{height}+0+0')

        self.state_history = []  # Track previous states for undo functionality
        self.cash_flows = pd.DataFrame(columns=["Period", "Cash Flow", "Color", "Series_ID"])
        self.interest_rate = 5.0

        # Color manager for robust color assignment
        self.color_manager = ColorManager()

        self.selected_indices = []
        self.value_texts = []
        self.selection_rects = []

        self.makeNewSeries = False

        self.canvas = None
        self.next_series_id = 0

        setup_ui(self)
        create_table(self, [])  # Create empty table at startup
        self._save_state()
        self.update_plot()

    def update_canvas(self):
        if self.canvas:
            self.canvas.draw()

    def update_interest_rate(self, new_rate):
        try:
            rate = float(new_rate)
            if -100 <= rate <= 100:
                self.interest_rate = rate
                self.interest_rate_label.config(text=f"{self.interest_rate}%")
            else:
                messagebox.showerror("Input Error", "Please enter a number between -100 and 100.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number.")

    def _save_state(self):
        if not self.state_history or not self.cash_flows.equals(self.state_history[-1]):
            if len(self.state_history) >= 5:
                self.state_history.pop(0)
            self.state_history.append(self.cash_flows.copy())

    def combine_cash_flows(self):
        self._save_state()
        combine_cash_flows(self)
        self._cleanup_colors()

    def popup_uniform_series(self):
        self._save_state()
        popup_uniform_series(self, self._get_next_series_id())

    def popup_add_single_cash_flow(self):
        self._save_state()
        popup_add_single_cash_flow(self, self._get_next_series_id())

    def popup_gradient_series(self):
        self._save_state()
        popup_gradient_series(self, self._get_next_series_id())

    def popup_present_value(self):
        self._save_state()
        popup_present_value(self)

    def popup_future_value(self):
        self._save_state()
        popup_future_value(self)

    def popup_annual_value(self):
        self._save_state()
        popup_annual_value(self, self._get_next_series_id())

    def popup_geometric_series(self):
        self._save_state()
        popup_geometric_series(self, self._get_next_series_id())

    def update_plot(self):
        self._save_state()
        update_plot(self)

    def _get_next_series_id(self):
        self.next_series_id += 1
        return self.next_series_id
    
    def get_next_color(self):
        """Get the next available color for a new series."""
        return self.color_manager.get_color()
    
    def _cleanup_colors(self):
        """Clean up colors that are no longer in use."""
        self.color_manager.return_colors_not_in_dataframe(self.cash_flows)

    def select_series(self, series_id):
        self.selected_indices = self.cash_flows[self.cash_flows["Series_ID"] == series_id].index.tolist()
        self.update_canvas()

    def delete_selected_series(self):
        self._save_state()
        delete_selected_series(self)
        self._cleanup_colors()

    def invert_selected_series(self):
        self._save_state()
        invert_selected_series(self)

    def split_selected_series(self):
        self._save_state()
        split_selected_series(self)

    def undo_last_action(self):
        if len(self.state_history) > 1:
            self.state_history.pop()
            self.cash_flows = self.state_history[-1].copy()
            self._cleanup_colors()
            create_table(self, [])
            self.update_plot()  # Ensure the plot is updated
        else:
            messagebox.showinfo("Undo", "No more actions to undo.")

    def toggle_makeNewSeries(self):
        # Update the makeNewSeries based on the menu checkbutton state
        if hasattr(self, 'makeNewSeries_var'):
            self.makeNewSeries = self.makeNewSeries_var.get()
        else:
            # Fallback for backward compatibility
            self.makeNewSeries = not self.makeNewSeries

    def clear_graph(self):
        self._save_state()
        clear_graph(self)
        self._cleanup_colors()

