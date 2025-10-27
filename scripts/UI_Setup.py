from scripts.Clear_Graph import clear_graph
import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import os


def get_asset_path(filename):
    """Get the absolute path to an asset file.
    
    Args:
        filename: Name of the file in the assets folder
        
    Returns:
        Absolute path to the asset file
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "assets", filename)


def setup_ui(app):
    # Define a font style for buttons
    button_font = font.Font(size=10, weight="bold")
    plus_question_button_font = font.Font(size=14, weight="bold")  # Larger font for plus and question symbol

    # Define button options excluding the plus and question buttons
    button_options = {
        'font': button_font,
        'borderwidth': 2,
        'highlightthickness': 2,
        'highlightbackground': 'black',
        'highlightcolor': 'black'
    }

    # Add banner at the top
    add_banner(app)

    # Create a container for buttons
    app.button_container = tk.Frame(app.root)
    app.button_container.pack(side="top", fill="x", pady=1)

    # Create frames for the top and bottom rows of operation buttons
    top_button_frame = tk.Frame(app.button_container)
    top_button_frame.pack(side="top", pady=1, anchor='n')  # Reduced vertical spacing

    bottom_button_frame = tk.Frame(app.button_container)
    bottom_button_frame.pack(side="top", pady=1, anchor='n')  # Row for bottom buttons

    # Top row buttons
    create_operation_buttons_top_row(app, top_button_frame, button_options, plus_question_button_font)

    # Bottom row buttons
    app.toggle_makeNewSeries_button = create_operation_buttons_bottom_row(app, bottom_button_frame, button_options)

    # Create a PanedWindow for resizable sections (graph and table)
    app.main_paned_window = tk.PanedWindow(app.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    app.main_paned_window.pack(side="top", fill=tk.BOTH, expand=True)
    
    # Create a frame for the graph (will be populated by update_plot)
    app.graph_frame = tk.Frame(app.main_paned_window)
    app.main_paned_window.add(app.graph_frame, stretch="always")
    
    # Create a frame for the table (will be populated by create_table)
    app.table_frame = tk.Frame(app.main_paned_window)
    app.main_paned_window.add(app.table_frame, stretch="never")


def add_banner(app):
    """Add the banner image to the top of the window."""
    try:
        banner_path = get_asset_path("banner_trans.png")
        banner_image = Image.open(banner_path)
        
        # Scale the banner to a reasonable width (e.g., 600 pixels wide)
        target_width = 600
        aspect_ratio = banner_image.height / banner_image.width
        target_height = int(target_width * aspect_ratio)
        # Use Image.Resampling.LANCZOS for newer Pillow versions, fallback to Image.LANCZOS
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS
        banner_image = banner_image.resize((target_width, target_height), resample_filter)
        
        # Convert to PhotoImage
        banner_photo = ImageTk.PhotoImage(banner_image)
        
        # Create a label to hold the banner
        banner_label = tk.Label(app.root, image=banner_photo)
        banner_label.image = banner_photo  # Keep a reference to prevent garbage collection
        banner_label.pack(side="top", pady=5)
    except Exception as e:
        print(f"Could not load banner: {e}")


def create_operation_buttons_top_row(app, frame, options, plus_question_button_font):
    # Create buttons with reduced padding, size, and layout
    present_value_button = tk.Button(frame, text="Present Value", command=app.popup_present_value, height=1, **options)
    present_value_button.pack(side="left", padx=2)

    future_value_button = tk.Button(frame, text="Future Value", command=app.popup_future_value, height=1, **options)
    future_value_button.pack(side="left", padx=2)

    annual_value_button = tk.Button(frame, text="Annual Value", command=app.popup_annual_value, height=1, **options)
    annual_value_button.pack(side="left", padx=2)

    combine_cash_flow_button = tk.Button(frame, text="Combine Cash Flow", command=app.combine_cash_flows, height=1,
                                         **options)
    combine_cash_flow_button.pack(side="left", padx=2)

    # Create '+' and '?' buttons on the top row
    create_plus_button(app, frame, plus_question_button_font)
    create_question_button(app, frame, plus_question_button_font)


# Create the compact bottom row buttons
def create_operation_buttons_bottom_row(app, frame, options):
    # Create buttons with reduced padding, size, and layout for the bottom row
    delete_button = tk.Button(frame, text="Delete Selection", command=app.delete_selected_series, height=1, **options)
    delete_button.pack(side="left", padx=2)

    clear_button = tk.Button(frame, text="Clear", command=lambda: clear_graph(app), height=1, **options)
    clear_button.pack(side="left", padx=2)

    undo_button = tk.Button(frame, text="Undo", command=app.undo_last_action, height=1, **options)
    undo_button.pack(side="left", padx=2)

    toggle_makeNewSeries_button = tk.Button(frame, text="Make New Series", command=app.toggle_makeNewSeries, height=1, **options, relief="raised")
    toggle_makeNewSeries_button.pack(side="left", padx=2)

    # Interest rate section placed on the right
    create_interest_rate_frame(app, frame)

    return toggle_makeNewSeries_button


def create_plus_button(app, frame, plus_question_button_font):
    # Create a canvas to draw the circular plus button
    plus_canvas = tk.Canvas(frame, width=45, height=45, highlightthickness=0)
    plus_canvas.pack(side="left", padx=5)

    # Draw a circle (oval with equal sides) as the button's background
    plus_canvas.create_oval(5, 5, 40, 40, fill='green', outline='')

    # Place a '+' symbol in the center of the circle
    plus_canvas.create_text(23, 23, text="+", font=plus_question_button_font, fill='white', anchor="center")

    # Bind click event to the canvas to trigger show_series_popup
    plus_canvas.bind("<Button-1>", lambda _: show_series_popup(app))


def create_question_button(app, frame, plus_question_button_font):
    # Create a canvas to draw the circular question button
    question_canvas = tk.Canvas(frame, width=45, height=45, highlightthickness=0)
    question_canvas.pack(side="left", padx=5)

    # Draw a circle (oval with equal sides) as the button's background
    question_canvas.create_oval(5, 5, 40, 40, fill='purple', outline='')

    # Place a '?' symbol in the center of the circle
    question_canvas.create_text(23, 23, text="?", font=plus_question_button_font, fill='white', anchor="center")

    # Bind click event to the canvas for a potential help or info popup
    question_canvas.bind("<Button-1>", lambda _: display_help(app))


def create_interest_rate_frame(app, frame):
    # Container frame for interest rate controls
    interest_rate_frame = tk.Frame(frame)
    interest_rate_frame.pack(side="right", padx=10)  # Positioned on the far right of the bottom frame

    # Interest rate label
    app.interest_rate_label = tk.Label(interest_rate_frame, text=f"{app.interest_rate}%", font=("Arial", 10, "bold"))
    app.interest_rate_label.pack(side="right", padx=5)

    # Button to update the interest rate
    update_rate_button = tk.Button(interest_rate_frame, text="Interest Rate",
                                   command=lambda: prompt_interest_rate_change(app))
    update_rate_button.pack(side="right", padx=5)


def display_help(app):
    # Create a help popup window with buttons
    help_window = tk.Toplevel()
    help_window.title("Help Menu")
    help_window.geometry("250x350")
    
    # Set the window icon
    try:
        icon_path = get_asset_path("app.ico")
        help_window.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not load icon for help window: {e}")
    
    # Make window always on top
    help_window.attributes('-topmost', True)
    
    # Center the window
    help_window.update_idletasks()
    width = help_window.winfo_width()
    height = help_window.winfo_height()
    x = (help_window.winfo_screenwidth() // 2) - (width // 2)
    y = (help_window.winfo_screenheight() // 2) - (height // 2)
    help_window.geometry(f'{width}x{height}+{x}+{y}')
    
    font.Font(size=20)
    def show_help_message(title, message):
        tk.messagebox.showinfo(title, message)

    # Create buttons for each help topic
    help_topics = [
        ("Present Value", "Present Value calculates the equivalent worth of a series of cash flows at a point before the series begins, using a specified interest rate. For cash flow series with multiple payments (uniform, gradient, or geometric), this point is one period before the first payment. For a single cash flow, the point of reference can be any period before the payment."),
        ("Future Value", "Future Value calculates the equivalent worth of a series of cash flows at a point after the series ends, using a specified interest rate. For cash flow series with multiple payments (uniform, gradient, or geometric), this point is one period after the final payment. For a single cash flow, the point of reference can be any period after the payment."),
        ("Annual Value", "Annual Value calculates the equivalent uniform annual worth of a series of cash flows over its duration, using a specified interest rate. For cash flow series with multiple payments (uniform, gradient, or geometric), this value represents a consistent annual amount spanning the series. For a single cash flow, it distributes the value evenly across the specified periods."),
        ("Combining Cash Flows", "This function sums single cash flows that occur in the same period."),
        ("Interest Rate", "The interest rate is the global time value of money across the entire program and applies to all functions."),
        ("Single Cash Flow", "A single cash flow is an individual financial transaction involving a one-time payment or receipt of money at a specific point in time."),
        ("Uniform Series", "A uniform or annual series is a series of constant values over a set number of periods."),
        ("Gradient Series", "A gradient series is a series that increases by a set value across the length of the series. The first value in the series is always 0."),
        ("Geometric Series", "A geometric series is a series that increases by a set percentage, known as the growth percentage, across the length of the series."),
        ("FAQs", "1. If your problem includes a negative period, consider reframing the problem with your most negative value being set as Period 0.                                                                                 2. If the problem requires multiple interest rates, you are able to manipulate the cash flow to its final point and change the interest rate for the other parts of the problem.                        3. Just note that any changes across periods will involve the current interest rate displayed at the top of the screen.")]

    for topic, message in help_topics:
        tk.Button(help_window, text=topic, command=lambda t=topic, m=message: show_help_message(t, m)).pack(pady=5)

def show_series_popup(app):
    # Create a new, smaller window popup for selecting series
    popup_window = tk.Toplevel()
    popup_window.title("Select Series")
    popup_window.geometry("200x150")  # Reduced size
    
    # Set the window icon
    try:
        icon_path = get_asset_path("app.ico")
        popup_window.iconbitmap(icon_path)
    except Exception as e:
        print(f"Could not load icon for series popup: {e}")
    
    # Make window always on top
    popup_window.attributes('-topmost', True)

    # Center the popup window
    popup_window.update_idletasks()
    width = popup_window.winfo_width()
    height = popup_window.winfo_height()
    x = (popup_window.winfo_screenwidth() // 2) - (width // 2)
    y = (popup_window.winfo_screenheight() // 2) - (height // 2)
    popup_window.geometry(f'{width}x{height}+{x}+{y}')

    # Add buttons for each series type in the popup
    single_cash_flow_button = tk.Button(popup_window, text="Single Cash Flow",
                                        command=lambda: [app.popup_add_single_cash_flow(), popup_window.destroy()])
    single_cash_flow_button.pack(pady=5)

    uniform_series_button = tk.Button(popup_window, text="Uniform Series",
                                      command=lambda: [app.popup_uniform_series(), popup_window.destroy()])
    uniform_series_button.pack(pady=5)

    gradient_series_button = tk.Button(popup_window, text="Gradient Series",
                                       command=lambda: [app.popup_gradient_series(), popup_window.destroy()])
    gradient_series_button.pack(pady=5)

    geometric_series_button = tk.Button(popup_window, text="Geometric Series",
                                        command=lambda: [app.popup_geometric_series(), popup_window.destroy()])
    geometric_series_button.pack(pady=5)


def prompt_interest_rate_change(app):
    new_rate = tk.simpledialog.askstring("Change Interest Rate", "Enter new interest rate:")
    if new_rate is not None:
        app.update_interest_rate(new_rate)
