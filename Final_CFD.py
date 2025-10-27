from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle
from Update_Plot import update_plot
from UI_Setup import setup_ui, get_asset_path
from Uniform_Series import popup_uniform_series
from Combine_CashFlows import combine_cash_flows
from Single_CashFlow import popup_add_single_cash_flow
from Gradient_Series import popup_gradient_series
from Present_Value import popup_present_value
from Future_Value import popup_future_value
from Annual_Value import popup_annual_value
from Geometric_Series import popup_geometric_series
from Delete_Series import delete_selected_series
from Clear_Graph import clear_graph
from Create_Table import create_table


class CashFlowDiagramApp:
    def __init__(self, root):
        self.toggle_makeNewSeries_button = None
        self.root = root
        self.root.title("Cash Flow Diagram")
        
        # Set the application icon
        try:
            icon_path = get_asset_path("app.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")

        self.state_history = []  # Track previous states for undo functionality
        self.cash_flows = pd.DataFrame(columns=["Period", "Cash Flow", "Color", "Series_ID"])
        self.interest_rate = 5.0

        # Updated to use cycle for cycling through colors
        self.colors = cycle(plt.colormaps["tab20"].colors)

        self.selected_indices = []
        self.value_texts = []
        self.selection_rects = []

        self.makeNewSeries = False

        self.canvas = None
        self.next_series_id = 0

        setup_ui(self)
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

    def select_series(self, series_id):
        self.selected_indices = self.cash_flows[self.cash_flows["Series_ID"] == series_id].index.tolist()
        self.update_canvas()

    def delete_selected_series(self):
        self._save_state()
        delete_selected_series(self)

    def undo_last_action(self):
        if len(self.state_history) > 1:
            self.state_history.pop()
            self.cash_flows = self.state_history[-1].copy()
            create_table(self, [])
            self.update_plot()  # Ensure the plot is updated
        else:
            messagebox.showinfo("Undo", "No more actions to undo.")

    def toggle_makeNewSeries(self):
        self.makeNewSeries = not self.makeNewSeries
        if self.toggle_makeNewSeries_button.config('relief')[-1] == 'sunken':
            self.toggle_makeNewSeries_button.config(relief="raised")
        else:
            self.toggle_makeNewSeries_button.config(relief="sunken")

    def clear_graph(self):
        self._save_state()
        clear_graph(self)

