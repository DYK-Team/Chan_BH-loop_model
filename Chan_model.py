#
# Simulating a BH-loop using Chan's model: https://ieeexplore.ieee.org/document/75630
# Dr. Dmitriy Makhnovskiy, City College Plymouth, England
# 23.02.2024
#

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import csv
import logging

# Configure logging
logging.basicConfig(filename='simulation_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def read_log_file():
    try:
        with open('simulation_log.log', 'r') as log_file:
            lines = log_file.readlines()
            params_found = False
            params = []
            for line in lines:
                if "Simulation parameters:" in line:
                    params = line.split(':')[1].strip().split(',')
                    if len(params) == 5:  # Ensure the correct number of parameters
                        params_found = True
            if params_found:
                entry_Bs.delete(0, tk.END)
                entry_Bs.insert(0, params[0].split('=')[1])
                entry_Br.delete(0, tk.END)
                entry_Br.insert(0, params[1].split('=')[1])
                entry_Hc.delete(0, tk.END)
                entry_Hc.insert(0, params[2].split('=')[1])
                entry_Hmax.delete(0, tk.END)
                entry_Hmax.insert(0, params[3].split('=')[1])
                entry_N.delete(0, tk.END)
                entry_N.insert(0, params[4].split('=')[1])
                messagebox.showinfo("Parameters Loaded", "Simulation parameters loaded from log file.")
            else:
                messagebox.showwarning("Log File Error", "Invalid format of simulation parameters in log file.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading log file: {str(e)}")

def run_simulation():
    try:
        # Retrieve values from the GUI
        Bs = float(entry_Bs.get())  # Saturation induction (flux density), Tesla (T)
        Br = float(entry_Br.get())  # Residual induction, Tesla (T)
        Hc = float(entry_Hc.get())  # Coercivity, Amperes/meter (A/m)
        Hmax = float(entry_Hmax.get())  # Maximum scanning field, Amperes/meter (A/m)
        N = int(entry_N.get())  # Number of points in the graphs

        # Log input values
        logging.info(f"Simulation parameters: Bs={Bs}, Br={Br}, Hc={Hc}, Hmax={Hmax}, N={N}")

        # Clear log file
        open('simulation_log.log', 'w').close()

        # Write parameters from the current run to log file
        with open('simulation_log.log', 'a') as log_file:
            log_file.write(f"Simulation parameters: Bs={Bs}, Br={Br}, Hc={Hc}, Hmax={Hmax}, N={N}\n")

        # Calculate lists: H (A/m), BH-loop branches B1 (T) and B2(T), and the averaged curve B3 = (B1 + B2) / 2
        # Full (saturated) or minor (unsaturated) BH-loop
        H_values = [-Hmax + 2 * Hmax * i / (N - 1) for i in range(N)]  # Magnetising force, A/m
        # dB - branch vertical adjustment for drawing a minor loop
        dB = Bs * (H_values[N - 1] + Hc) / (abs(H_values[N - 1] + Hc) + Hc * (Bs / Br - 1.0))
        dB = (dB - (Bs * (H_values[N - 1] - Hc) / (abs(H_values[N - 1] - Hc) + Hc * (Bs / Br - 1.0)))) / 2.0
        # The following curves are already vertically adjusted:
        B1_values = [(Bs * (H + Hc) / (abs(H + Hc) + Hc * (Bs / Br - 1.0)) - dB) for H in H_values]  # Upper branch
        B2_values = [(Bs * (H - Hc) / (abs(H - Hc) + Hc * (Bs / Br - 1.0)) + dB) for H in H_values]  # Lower branch
        B3_values = [((B1 + B2) / 2.0) for B1, B2 in zip(B1_values, B2_values)]  # Middle curve

        # Plot BH-loop
        plt.figure()
        plt.plot(H_values, B1_values, label='B1')
        plt.plot(H_values, B2_values, label='B2')
        plt.xlabel('H, A/m')
        plt.ylabel('B, T')
        plt.title('BH-loop: both branches')
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.minorticks_on()
        plt.grid(True, which='minor', linestyle=':', linewidth=0.25)
        plt.show()

        # Plot averaged BH-loop
        plt.figure()
        plt.plot(H_values, B3_values, label='Middle curve')
        plt.xlabel('H, A/m')
        plt.ylabel('B, T')
        plt.title('BH-curve: averaged branches')
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.minorticks_on()
        plt.grid(True, which='minor', linestyle=':', linewidth=0.25)
        plt.show()

        # Save data for the whole BH-loop (both branches)
        with open('BH-loop_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['H, A/m', 'Upper B, T', 'Lower B, T'])
            for H, B1, B2 in zip(H_values, B1_values, B2_values):
                writer.writerow([H, B1, B2])

        # Save data for the averaged BH-loop (middle curve)
        with open('Averaged_BH-loop_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['H, A/m', 'B, T'])
            for H, B3 in zip(H_values, B3_values):
                writer.writerow([H, B3])

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create a tkinter window
window = tk.Tk()
window.title("BH-loop Simulation")

# Create labels and entry fields for input values
tk.Label(window, text="Bs (T):").grid(row=0, column=0)
entry_Bs = tk.Entry(window)
entry_Bs.grid(row=0, column=1)

tk.Label(window, text="Br (T):").grid(row=1, column=0)
entry_Br = tk.Entry(window)
entry_Br.grid(row=1, column=1)

tk.Label(window, text="Hc (A/m):").grid(row=2, column=0)
entry_Hc = tk.Entry(window)
entry_Hc.grid(row=2, column=1)

tk.Label(window, text="Hmax (A/m):").grid(row=3, column=0)
entry_Hmax = tk.Entry(window)
entry_Hmax.grid(row=3, column=1)

tk.Label(window, text="N (Number of points):").grid(row=4, column=0)
entry_N = tk.Entry(window)
entry_N.grid(row=4, column=1)

# Load parameters from log file
btn_load_params = tk.Button(window, text="Load Parameters from Log", command=read_log_file)
btn_load_params.grid(row=5, column=0, columnspan=2, pady=10)

# Create Run and Stop buttons
btn_run = tk.Button(window, text="Run Simulation", command=run_simulation)
btn_run.grid(row=6, column=0, columnspan=2, pady=5)

btn_stop = tk.Button(window, text="Stop Simulation", command=window.destroy)
btn_stop.grid(row=7, column=0, columnspan=2)

# Start the tkinter event loop
window.mainloop()
