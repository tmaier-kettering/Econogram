"""Table creation and display module.

Creates and updates the tabular view of cash flows displayed alongside the diagram.
"""
import pandas as pd
import tkinter as tk
from tkinter import ttk


def create_table(app, selected_values):
    # Check if tree exists, if not create it
    if not hasattr(app, 'tree'):
        # Create a container to hold the treeview and scrollbar
        table_container = tk.Frame(app.table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical")

        # Create a Treeview widget with columns in the desired order
        app.tree = ttk.Treeview(table_container, columns=("Series Name", "Period", "Cash Flow"), height=15,
                                show='headings',
                                yscrollcommand=scrollbar.set)
        scrollbar.config(command=app.tree.yview)

        # Set the heading (column titles)
        app.tree.heading("Series Name", text="Series Name")
        app.tree.heading("Period", text="Period")
        app.tree.heading("Cash Flow", text="Cash Flow")

        # Configure column widths
        app.tree.column("Series Name", width=150, anchor='center')
        app.tree.column("Period", width=100, anchor='center')
        app.tree.column("Cash Flow", width=100, anchor='center')

        # Pack the scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pack the tree
        app.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Clear previous table data
    for i in app.tree.get_children():
        app.tree.delete(i)

    # If selected_values is empty, populate with all cash flows
    if not selected_values and hasattr(app, 'cash_flows') and not app.cash_flows.empty:
        selected_values = []
        for _, row in app.cash_flows.iterrows():
            selected_values.append([row['Series_Name'], row['Period'], row['Cash Flow']])

    # Populate the table with values
    if selected_values:
        # Convert selected_values to DataFrame
        df = pd.DataFrame(selected_values, columns=['Series Name', 'Period', 'Cash Flow'])

        # Sort the DataFrame by 'Series Name' ascending and 'Period' descending
        df_sorted = df.sort_values(by=['Series Name', 'Period'], ascending=[True, True])

        # Insert the sorted data into the table
        for index, row in df_sorted.iterrows():
            # Round the cash flow to 2 decimal places and prepend a dollar sign
            rounded_cash_flow = f"${round(row['Cash Flow'], 2):,.2f}"
            app.tree.insert("", "end", values=(row['Series Name'], row['Period'], rounded_cash_flow))
