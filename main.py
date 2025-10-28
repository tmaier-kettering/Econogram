"""Main entry point for the Econogram application.

This module initializes and launches the Econogram desktop application,
a tool for creating and analyzing cash flow diagrams used in engineering economics.
"""
import tkinter as tk
from scripts.Final_CFD import CashFlowDiagramApp


if __name__ == "__main__":
    root = tk.Tk()
    app = CashFlowDiagramApp(root)
    root.mainloop()