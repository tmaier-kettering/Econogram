"""Clear graph functionality module.

Provides the functionality to clear all cash flows from the diagram.
"""
from tkinter import messagebox
from scripts.Create_Table import create_table  # Ensure the import at the top


def clear_graph(app):
    # Ask for confirmation before clearing
    user_confirmed = messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the graph and all data?")

    if user_confirmed:
        # Clear the DataFrame
        app.cash_flows = app.cash_flows.iloc[0:0]  # Reset to an empty DataFrame

        # Clear any selection indices and rectangles
        app.selected_indices = []
        if hasattr(app, 'selection_rects'):
            for rect in app.selection_rects:
                rect.set_visible(False)
            app.selection_rects.clear()

        # Clear the canvas
        if app.canvas:
            app.canvas.get_tk_widget().pack_forget()
            app.canvas = None

        # Clear the table by calling create_table with an empty list
        create_table(app, [])

        # Save the state after clearing
        app._save_state()

        # Update the plot to reflect changes
        app.update_plot()
