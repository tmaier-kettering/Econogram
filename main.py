from PIL._tkinter_finder import tk
from Final_CFD import CashFlowDiagramApp


if __name__ == "__main__":
    root = tk.Tk()
    app = CashFlowDiagramApp(root)
    root.mainloop()