"""Table creation and display module.

Creates and updates the tabular view of cash flows displayed alongside the diagram.
"""
import pandas as pd
import tkinter as tk
from tkinter import ttk
from scripts.Theme import COLORS, get_fonts


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

        # Configure column widths. Cash Flow is right-aligned since it's a
        # money column; Series Name reads better left-aligned.
        app.tree.column("Series Name", width=150, anchor='w')
        app.tree.column("Period", width=100, anchor='center')
        app.tree.column("Cash Flow", width=100, anchor='e')

        # Zebra striping and sign coloring for at-a-glance scanning of
        # inflows vs. outflows.
        app.tree.tag_configure('evenrow', background=COLORS["surface"])
        app.tree.tag_configure('oddrow', background=COLORS["surface_alt"])
        app.tree.tag_configure('positive', foreground=COLORS["positive"])
        app.tree.tag_configure('negative', foreground=COLORS["negative"])

        # Pack the scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack the tree
        app.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Placeholder shown when there's nothing selected, so an empty
        # table reads as "nothing selected yet" rather than "broken".
        app.table_hint = tk.Label(
            table_container, text="Select cash flows on the chart to see their details here.",
            font=get_fonts()["body"], fg=COLORS["muted"], background=COLORS["surface"],
            wraplength=220, justify="center"
        )

    # Clear previous table data
    for i in app.tree.get_children():
        app.tree.delete(i)

    # Populate the table with selected values
    if selected_values:
        # Convert selected_values to DataFrame
        df = pd.DataFrame(selected_values, columns=['Series Name', 'Period', 'Cash Flow'])

        # Sort the DataFrame by 'Series Name' ascending and 'Period' ascending
        df_sorted = df.sort_values(by=['Series Name', 'Period'], ascending=[True, True])

        # Insert the sorted data into the table
        for position, (index, row) in enumerate(df_sorted.iterrows()):
            # Round the cash flow to 2 decimal places and prepend a dollar sign
            rounded_cash_flow = f"${round(row['Cash Flow'], 2):,.2f}"
            stripe_tag = 'evenrow' if position % 2 == 0 else 'oddrow'
            sign_tag = 'positive' if row['Cash Flow'] >= 0 else 'negative'
            app.tree.insert(
                "", "end", values=(row['Series Name'], row['Period'], rounded_cash_flow),
                tags=(stripe_tag, sign_tag)
            )
        app.table_hint.place_forget()
    else:
        app.table_hint.place(relx=0.5, rely=0.5, anchor="center")
