# Econogram Help Documentation

This guide provides detailed information about all features and functionality in Econogram.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Interest Rate](#interest-rate)
4. [Cash Flow Series](#cash-flow-series)
5. [Calculation Functions](#calculation-functions)
6. [Editing Operations](#editing-operations)
7. [Working with Python](#working-with-python)
8. [Frequently Asked Questions](#frequently-asked-questions)

## Getting Started

### Running the Standalone Executable

1. Download the latest .exe file from the [Releases](https://github.com/tmaier-kettering/Econogram/releases/latest) page
2. Double-click the .exe file to launch the application
3. No installation or additional software is required

The application window will open maximized, displaying a blank cash flow diagram on the left and an empty table on the right.

## Interface Overview

Econogram's interface consists of:

- **Menu Bar**: Access to all functions organized by category
- **Status Bar**: Displays the current interest rate
- **Graph Panel**: Visual cash flow diagram showing periods (x-axis) and cash flow amounts (y-axis)
- **Table Panel**: Tabular view of selected cash flows with period, amount, and series information

### Menu Structure

- **File**: Clear graph, exit application
- **Edit**: Undo, delete, invert series, split series, combine cash flows
- **Insert**: Add new cash flow series
- **Calculate**: Perform time value of money calculations
- **Options**: Set interest rate, toggle "Make New Series" mode
- **Help**: Context-sensitive help and documentation links

### Keyboard Shortcuts

- **Ctrl+Z**: Undo last action
- **Delete**: Delete selected series

## Interest Rate

The interest rate is a global setting that applies to all time value of money calculations throughout the application.

### Setting the Interest Rate

1. Go to **Options → Set Interest Rate**
2. Enter a value between -100 and 100 (as a percentage)
3. The current rate is always displayed in the status bar at the top of the window

### Interest Rate Behavior

- The interest rate affects all Present Value, Future Value, and Annual Value calculations
- Changing the interest rate does not automatically recalculate existing series
- The rate can be changed at any time between operations
- Default interest rate is 5.0%

## Cash Flow Series

Econogram supports four types of cash flow series:

### Single Cash Flow

A single cash flow is a one-time payment or receipt at a specific period.

**To add a single cash flow:**

1. Go to **Insert → Single Cash Flow**
2. Enter the cash flow amount (can be negative for outflows)
3. Enter the period (any whole number, positive or negative)
4. Enter a series name (up to 14 characters)
5. Click **Graph** or press Enter

**Inputs:**
- **Cash Flow Amount**: Any positive or negative number (up to 2 decimal places, max 10 characters)
- **Period**: Any integer (whole number), positive, negative, or zero
- **Series Name**: Descriptive text (max 14 characters)

**Notes:**
- Positive values represent cash inflows (displayed as upward bars)
- Negative values represent cash outflows (displayed as downward bars)
- Zero values are not permitted

### Uniform Series

A uniform series is a sequence of equal cash flows occurring at regular intervals over multiple periods.

**To add a uniform series:**

1. Go to **Insert → Uniform Series**
2. Enter the cash flow amount (constant for all periods)
3. Enter the starting period (any whole number, positive or negative)
4. Enter the series length (number of periods)
5. Enter a series name
6. Click **Graph** or press Enter

**Inputs:**
- **Cash Flow Amount**: Constant value for each period (can be negative)
- **Starting Period**: Any integer (whole number), positive, negative, or zero
- **Series Length**: Number of consecutive periods (must be at least 1)
- **Series Name**: Descriptive text (max 14 characters)

**Example:**
- Amount: $1000
- Starting Period: 5
- Length: 10
- Result: $1000 cash flows at periods 5, 6, 7, 8, 9, 10, 11, 12, 13, and 14

**Example with negative starting period:**
- Amount: $500
- Starting Period: -3
- Length: 7
- Result: $500 cash flows at periods -3, -2, -1, 0, 1, 2, and 3

**Notes:**
- All cash flows in the series have the same value
- The series will be displayed in a single color

### Gradient Series

A gradient series is a sequence where each cash flow increases by a constant amount (the gradient) from the previous period. The first value in the series is always zero.

**To add a gradient series:**

1. Go to **Insert → Gradient Series**
2. Enter the gradient amount (constant increase per period)
3. Enter the starting period
4. Enter the series length
5. Enter a series name
6. Click **Graph** or press Enter

**Inputs:**
- **Gradient Amount**: Constant increase per period (can be negative for decreasing series)
- **Starting Period**: Any integer (whole number), positive, negative, or zero
- **Series Length**: Number of periods (must be at least 1)
- **Series Name**: Descriptive text (max 14 characters)

**Formula:**
Cash flow at period n = Gradient × (n - starting_period)

**Example:**
- Gradient: $100
- Starting Period: 2
- Length: 5
- Result:
  - Period 2: $0
  - Period 3: $100
  - Period 4: $200
  - Period 5: $300
  - Period 6: $400

**Notes:**
- The first cash flow is always zero
- Each subsequent cash flow increases by the gradient amount
- Negative gradients create decreasing series
- The entire series is displayed in a single color

### Geometric Series

A geometric series is a sequence where each cash flow increases by a constant percentage (growth rate) from the previous period.

**To add a geometric series:**

1. Go to **Insert → Geometric Series**
2. Enter the starting period
3. Enter the initial cash flow amount
4. Enter the series length
5. Enter the growth rate as a percentage
6. Enter a series name
7. Click **Graph** or press Enter

**Inputs:**
- **Starting Period**: Any integer (whole number), positive, negative, or zero
- **Initial Cash Flow Amount**: First value in the series (can be negative)
- **Series Length**: Number of periods (must be at least 1)
- **Growth Rate (%)**: Percentage increase per period (can be negative)
- **Series Name**: Descriptive text (max 14 characters)

**Formula:**
Cash flow at period n = Initial × (1 + growth_rate)^(n - starting_period)

**Example:**
- Starting Period: 1
- Initial Amount: $1000
- Length: 4
- Growth Rate: 10%
- Result:
  - Period 1: $1000
  - Period 2: $1100
  - Period 3: $1210
  - Period 4: $1331

**Notes:**
- Growth rate is entered as a percentage (e.g., 10 for 10%)
- Negative growth rates create decreasing series
- The entire series is displayed in a single color

## Calculation Functions

Econogram provides three time value of money calculation functions. All calculations use the global interest rate displayed in the status bar.

### Present Value (PV)

Present Value calculates the equivalent worth of cash flows at a point before the series begins.

**Behavior for different series types:**

- **Series with multiple cash flows** (uniform, gradient, geometric): The present value is calculated at one period before the first payment. This is automatic and does not require user input for the period.

- **Single cash flow**: You can specify any period before the cash flow to calculate the present value.

**To calculate present value:**

1. Click on a cash flow series in the table to select it
2. Go to **Calculate → Present Value**
3. For single cash flows: Enter the target period (must be less than or equal to the current period)
4. The calculated value will replace or supplement the original series (depending on "Make New Series" setting)

**Formula:**
PV = Cash Flow × (1 + i)^-n

Where:
- i = interest rate (as decimal)
- n = number of periods from target period to cash flow

**Important Notes:**
- You cannot move cash flows forward in time using Present Value
- If you attempt this, you'll receive a warning to use Future Value instead
- Present value moves money backward in time (discounting)

**Make New Series Mode:**
- When enabled: Creates a new series named "PV of [original series name]" with a new color
- When disabled: Replaces the original series with the calculated value

### Future Value (FV)

Future Value calculates the equivalent worth of cash flows at a point after the series ends.

**Behavior for different series types:**

- **Series with multiple cash flows** (uniform, gradient, geometric): The future value is calculated at the final payment period. This is automatic and does not require user input for the period.

- **Single cash flow**: You can specify any period after the cash flow to calculate the future value.

**To calculate future value:**

1. Click on a cash flow series in the table to select it
2. Go to **Calculate → Future Value**
3. For single cash flows: Enter the target period (must be greater than or equal to the current period)
4. The calculated value will replace or supplement the original series

**Formula:**
FV = Cash Flow × (1 + i)^n

Where:
- i = interest rate (as decimal)
- n = number of periods from cash flow to target period

**Important Notes:**
- You cannot move cash flows backward in time using Future Value
- If you attempt this, you'll receive a warning to use Present Value instead
- Future value moves money forward in time (compounding)

**Make New Series Mode:**
- When enabled: Creates a new series named "FV of [original series name]" with a new color
- When disabled: Replaces the original series with the calculated value

### Annual Value (AV)

Annual Value converts a single cash flow into an equivalent uniform series over a specified number of periods. The resulting uniform series starts one period after the selected cash flow.

**To calculate annual value:**

1. Click on a **single cash flow** in the table to select it
2. Go to **Calculate → Annual Value**
3. Enter the number of periods for the uniform series
4. The original cash flow will be converted to a uniform series

**Requirements:**
- Only works with a single selected cash flow
- Cannot be used on series with multiple cash flows
- The number of periods (n) specifies how many payment periods in the resulting uniform series (must be at least 1)
- The uniform series will start one period after the selected cash flow's period

**Formula (when interest rate ≠ 0):**
A = PV × [i / (1 - (1 + i)^-n)]

Where:
- PV = present value (selected cash flow)
- i = interest rate (as decimal)
- n = number of periods

**Formula (when interest rate = 0):**
A = PV / n

**Example:**
- Selected cash flow: $5000 at period 3
- Number of periods: 5
- Interest rate: 5%
- Result: Uniform series of ~$1155.75 at periods 4, 5, 6, 7, 8

**Make New Series Mode:**
- When enabled: Creates a new series named "AV of [original series name]" with a new color, keeping the original
- When disabled: Replaces the original cash flow with the uniform series

## Editing Operations

### Selecting Series

Click on any row in the table to select a cash flow series. Selected series are highlighted in the table and on the graph.

### Undo

**Edit → Undo** or **Ctrl+Z**

Undoes the last action. Econogram maintains a history of the last 5 states, allowing you to step backward through recent changes.

**What can be undone:**
- Adding new cash flow series
- Deleting series
- Combining cash flows
- Calculating PV, FV, or AV
- Inverting or splitting series

### Delete Selection

**Edit → Delete Selection** or **Delete key**

Deletes the currently selected cash flow series from the diagram.

### Invert Series

**Edit → Invert Series**

Multiplies all cash flows in the selected series by -1, converting inflows to outflows and vice versa.

**Use case:**
- Converting costs to revenues or vice versa
- Changing the perspective of the analysis

### Split Series

**Edit → Split Series**

Splits a multi-cash-flow series into two separate series at a chosen point using a slider interface.

**Use cases:**
- Dividing a series into two parts for separate analysis
- Preparing for selective calculations on part of a series
- Creating flexibility for different manipulations of series components

**Notes:**
- The first part retains the original color
- The second part gets a new color
- Both parts are named with "_1" and "_2" suffixes
- This operation cannot be applied to series with only one cash flow

### Combine Cash Flows

**Edit → Combine Cash Flows**

Combines selected cash flows that occur in the same period into a single aggregated cash flow.

**Behavior:**
- Select multiple cash flows from the same period
- The selected cash flows are added together
- The resulting combined cash flow gets a new series ID and color
- Original selected cash flows are removed
- The combined series is named by joining the original series names with " + "

**Use cases:**
- Simplifying complex diagrams by combining related cash flows
- Creating a net cash flow view for a specific period
- Preparing for calculations on the combined effect

**Example:**
- Select two cash flows at Period 5: +$1000 (Series A), -$300 (Series B)
- After combining: Period 5: +$700 (Series A + Series B)

### Clear Graph

**File → Clear Graph**

Removes all cash flows from the diagram, resetting to a blank state. The interest rate is preserved.

### Make New Series Toggle

**Options → Make New Series**

This is a toggle setting that affects how calculation functions (PV, FV, AV) behave:

- **Enabled** (checked): Calculations create new series alongside the original
- **Disabled** (unchecked): Calculations replace the original series

**When to use:**
- Enable when you want to compare original and calculated values
- Disable when you want to transform cash flows through sequential calculations
- Useful for building complex cash flow transformations

## Working with Python

While Econogram is primarily distributed as a standalone executable, developers and advanced users can run it from the Python source code.

### Requirements

- Python 3.8 or higher
- Required packages (install via pip):
  - pandas >= 2.0.0
  - matplotlib >= 3.7.0
  - tkinter (usually included with Python)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tmaier-kettering/Econogram.git
   cd Econogram
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Project Structure

```
Econogram/
├── main.py                    # Application entry point
├── scripts/
│   ├── Final_CFD.py          # Main application class
│   ├── UI_Setup.py           # User interface setup
│   ├── Update_Plot.py        # Graph rendering
│   ├── Create_Table.py       # Table display
│   ├── Single_CashFlow.py    # Single cash flow dialog
│   ├── Uniform_Series.py     # Uniform series dialog
│   ├── Gradient_Series.py    # Gradient series dialog
│   ├── Geometric_Series.py   # Geometric series dialog
│   ├── Present_Value.py      # PV calculation
│   ├── Future_Value.py       # FV calculation
│   ├── Annual_Value.py       # AV calculation
│   ├── Combine_CashFlows.py  # Combine operation
│   ├── Delete_Series.py      # Delete operation
│   ├── Invert_Series.py      # Invert operation
│   ├── Split_Series.py       # Split operation
│   └── Clear_Graph.py        # Clear operation
├── assets/
│   ├── app.ico               # Application icon
│   ├── example.png           # Screenshot
│   └── [other graphics]
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
└── README.md                 # Project overview
```

### Code Overview

The application is built with tkinter for the GUI and matplotlib for graphing. Cash flows are stored in a pandas DataFrame with columns:
- **Period**: Time period (any integer)
- **Cash Flow**: Dollar amount
- **Color**: RGB color tuple for display
- **Series_ID**: Unique identifier for the series
- **Series_Name**: User-provided name

## Frequently Asked Questions

### Handling Negative Periods

**Q: Can I use negative periods (e.g., period -5)?**

A: Yes, Econogram supports any positive or negative whole number for periods, including zero. You can enter negative periods directly when adding cash flows or series.

### Multiple Interest Rates

**Q: How do I handle problems with different interest rates for different time periods?**

A: Since Econogram uses a single global interest rate, you'll need to manually calculate intermediate values:

1. Use the first interest rate and calculate values up to a transition point
2. Change the global interest rate
3. Continue calculations from the transition point with the new rate

**Note:** When moving cash flows across periods, the calculation always uses the current global interest rate.

### Series Naming

**Q: Why is the series name limited to 14 characters?**

A: The character limit ensures series names display properly in the table without wrapping or truncation. Choose concise, descriptive names like "Initial Cost", "Revenue", "O&M Costs", etc.

### Calculation Precision

**Q: How many decimal places does Econogram use?**

A: Econogram uses standard floating-point precision internally. Display and input are limited to 2 decimal places for cash flow amounts. Interest rates can also have 2 decimal places.

### Saving Work

**Q: Can I save my cash flow diagram?**

A: The current version does not include save/load functionality. You can take screenshots of your diagram and use the table view to record cash flow values. Future versions may include export capabilities.

### Exporting Data

**Q: How can I export the table data?**

A: Currently, Econogram does not have built-in export features. You can manually transcribe data from the table view or take screenshots. The table displays all relevant information including periods, amounts, and series names.

### Color Coding

**Q: Can I change the colors of cash flow series?**

A: Colors are automatically assigned from a predefined color palette to ensure visual distinction between series. Manual color selection is not currently available.

### Keyboard Navigation

**Q: What keyboard shortcuts are available?**

A: 
- **Ctrl+Z**: Undo last action
- **Delete**: Delete selected series
- **Enter**: Submit values in dialog boxes

Menu items can also be accessed using Alt+[menu letter] on Windows.

### Error Messages

**Q: What does "You cannot move your cash flow forward in time using the present value function" mean?**

A: This means you're trying to calculate a present value at a period that comes after the cash flow, which would actually be a future value. Use the Future Value function instead.

## Additional Resources

- GitHub Repository: https://github.com/tmaier-kettering/Econogram
- Issue Tracker: https://github.com/tmaier-kettering/Econogram/issues
- License: MIT License (see LICENSE file)

## Support

For bug reports or feature requests, please open an issue on the GitHub repository. This is an open-source educational tool provided as-is without warranty.
