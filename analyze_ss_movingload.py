# install matplotlib from "pip install matplotlib"
# install numpy from "pip install numpy"
# install tkinter from "pip install tkinter"

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to analyze beam
def analyze_beam(L, W1, W2, x):
    step = 0.01  # Step size for moving load
    positions = np.arange(0, L - x + step, step)  # Possible positions of the first load
    # RA_vals = Reaction at A 
    # RB_vals = Reaction at B
    # SF_vals = SHEAR FORCE 
    # BM_vals = Bending Moment 
    RA_vals, RB_vals, SF_vals, BM_vals = [], [], [], [] # List to store the computed values 
    SF_01, BM_01 = 0, 0 # Intialize specific values to be calculated 

    for pos in positions:
        pos_W1 = pos # position of load W1
        pos_W2 = pos + x # position of load W2

        # Calculate reactions using statics
        RA = ((W1 * (L - pos_W1)) + (W2 * (L - pos_W2))) / L
        RB = W1 + W2 - RA
        # Append respective lists 
        RA_vals.append(RA)
        RB_vals.append(RB)

        # Calculate shear force at mid-span
        mid = L / 2
        SF = RA - (W1 if pos_W1 < mid else 0) - (W2 if pos_W2 < mid else 0)
        SF_vals.append(SF)

        # Calculate shear force when center of load is at mid-span
        if abs(mid - (pos_W1 + pos_W2)/2) < step:
            SF_01 = SF

        # Calculate BM_01 when W1 is at 0 m
        if abs(pos_W1) < step:
            BM_01 = RA * pos_W1

        # Calculate bending moment at W1 position
        BM = RA * pos_W1 - W1 * 0 - (W2 * (pos_W2 - pos_W1)) if pos_W2 <= L else 0
        BM_vals.append(BM)

    # Find max values and corresponding positions
    SF_max = max(SF_vals, key=abs)
    SF_max_loc = positions[np.argmax(np.abs(SF_vals))]
    BM_max = max(BM_vals)
    BM_max_loc = positions[np.argmax(BM_vals)]

    # Results to be printed 
    result = f"""
RESULTS (scroll within the box to see all the calculated values of all the parameters)\n
"""
    result += f"Maximum Reaction at A:\t\t\t\t\t\t{max(RA_vals):.2f} kN\n\n"
    result += f"Maximum Reaction at B:\t\t\t\t\t\t{max(RB_vals):.2f} kN\n\n"
    result += f"Bending Moment BM_01 (W1 at 0 m):\t\t\t\t\t\t{BM_01:.2f} kNm\n\n"
    result += f"Shear Force SF_01 (Center):\t\t\t\t\t\t{SF_01:.2f} kN\n\n"
    result += f"Maximum Shear Force SF_max:\t\t\t\t\t\t{SF_max:.2f} kN at a distance (y) {SF_max_loc:.2f} m from A\n\n"
    result += f"Maximum Bending Moment BM_max:\t\t\t\t\t\t{BM_max:.2f} kNm at a distance (z) {BM_max_loc:.2f} m from A"

    return result, positions, RA_vals, RB_vals, SF_vals, BM_vals

# GUI Setup
def launch_gui():
    def on_submit():
        try:
            # Get user input and onvert to float
            L = float(entry_L.get())
            W1 = float(entry_W1.get())
            W2 = float(entry_W2.get())
            x = float(entry_x.get())
            # validate that x < L
            if x >= L:
                messagebox.showerror("Input Error", "Distance x must be less than beam length L.")
                return

            # Perform analysis
            result, positions, RA_vals, RB_vals, SF_vals, BM_vals = analyze_beam(L, W1, W2, x)

            # Display result
            result_text.config(state='normal')
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, result)
            result_text.config(state='disabled')

            # Plot results
            plot_graphs(positions, RA_vals, RB_vals, SF_vals, BM_vals)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
# Function to plot graphs 
    def plot_graphs(positions, RA_vals, RB_vals, SF_vals, BM_vals):
        fig.clf()

        # Reaction Graph
        ax1 = fig.add_subplot(311)
        ax1.plot(positions, RA_vals, label='RA', color='blue')
        ax1.plot(positions, RB_vals, label='RB', color='green')
        ax1.set_ylabel('Reactions (kN)')
        ax1.set_title('Influence Line for Reactions')
        ax1.grid(True)
        ax1.legend()

        # Shear Force Graph
        ax2 = fig.add_subplot(312)
        ax2.plot(positions, SF_vals, label='Shear Force', color='orange')
        ax2.axhline(0, color='black', linestyle='--')
        ax2.set_ylabel('Shear Force (kN)')
        ax2.set_title('Shear Force vs Load Position')
        ax2.grid(True)
        ax2.legend()

        # Bending Moment Graph
        ax3 = fig.add_subplot(313)
        ax3.plot(positions, BM_vals, label='Bending Moment', color='red')
        ax3.set_ylabel('Bending Moment (kNm)')
        ax3.set_xlabel('Position of W1 (m)')
        ax3.set_title('Bending Moment vs Load Position')
        ax3.grid(True)
        ax3.legend()

        # Rotate x-axis labels and add spacing
        plt.setp(ax3.get_xticklabels(), rotation=45)
        fig.tight_layout(pad=5.0)

        # Render updated canvas
        canvas.draw()

    # Tkinter GUI layout
    root = tk.Tk()
    root.title("Moving Load Beam Analysis")
    root.geometry("1100x900")

    # Scrollable frame setup
    canvas_main = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas_main.yview)
    scrollable_frame = tk.Frame(canvas_main)

    scrollable_frame.bind("<Configure>", lambda e: canvas_main.configure(scrollregion=canvas_main.bbox("all")))
    canvas_main.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_main.configure(yscrollcommand=scrollbar.set)

    canvas_main.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Input Fields
    input_frame = tk.Frame(scrollable_frame)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Beam Length L (m):").grid(row=0, column=0, padx=5, pady=5)
    entry_L = tk.Entry(input_frame)
    entry_L.grid(row=0, column=1)

    tk.Label(input_frame, text="Load W1 (kN):").grid(row=0, column=2, padx=5, pady=5)
    entry_W1 = tk.Entry(input_frame)
    entry_W1.grid(row=0, column=3)

    tk.Label(input_frame, text="Load W2 (kN):").grid(row=1, column=0, padx=5, pady=5)
    entry_W2 = tk.Entry(input_frame)
    entry_W2.grid(row=1, column=1)

    tk.Label(input_frame, text="Distance x (m):").grid(row=1, column=2, padx=5, pady=5)
    entry_x = tk.Entry(input_frame)
    entry_x.grid(row=1, column=3)
# Submit button to trigger analysis 
    tk.Button(scrollable_frame, text="Analyze Beam", command=on_submit, bg='lightblue').pack(pady=10)

    # Text box to display results
    result_text = tk.Text(scrollable_frame, height=10, width=110, wrap=tk.WORD)
    result_text.config(state='disabled')
    result_text.pack(pady=10)

    # Plotting Area of matplotlib graphs 
    fig = plt.Figure(figsize=(10, 7), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
    canvas.get_tk_widget().pack(pady=(10, 50))  # Add extra space below last graph
    
    # start GUI event loop
    root.mainloop() 

# Run the application
launch_gui()
