#
# Simulating a BH-loop using Chan's model: https://ieeexplore.ieee.org/document/75630
# Dr. Dmitriy Makhnovskiy, City College Plymouth, England
# Project and reports at GitHub: https://github.com/DmitriyMakhnovskiy/Chan_BH-loop_model
# created 23.02.2024; updated 03.03.2024
#

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import csv
import logging
from scipy.interpolate import interp1d

mu_0 = 1.25663706212e-6  # vacuum magnetic permeability

# Other parameters used for simulations:
# Hc - coercivity without a gap, A/m
# Hmax - maximum magnetization (+/-) when drawing the BH-loop
# Br - residual induction, Tesla (T)
# Bs - saturation induction, T
# Lm - length of the magnetic core (single loop) without a gap, m
# Lg - length of the gap, m
# S - cross-section of the magnetic core, m^2

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
                    if len(params) == 8:  # Ensure the correct number of parameters
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
                entry_Lm.delete(0, tk.END)
                entry_Lm.insert(0, params[5].split('=')[1])
                entry_Lg.delete(0, tk.END)
                entry_Lg.insert(0, params[6].split('=')[1])
                entry_S.delete(0, tk.END)
                entry_S.insert(0, params[7].split('=')[1])
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
        Lm = float(entry_Lm.get())  # Length of the magnetic core without a gap, m
        Lg = float(entry_Lg.get())  # Length of the gap, m
        S = float(entry_S.get())  # Cross-section of the magnetic core, m^2

        # Log input values
        logging.info(f"Simulation parameters: Bs={Bs}, Br={Br}, Hc={Hc}, Hmax={Hmax}, N={N}, Lm={Lm}, Lg={Lg}, S={S}")

        # Clear log file
        open('simulation_log.log', 'w').close()

        # Write parameters from the current run to log file
        with open('simulation_log.log', 'a') as log_file:
            log_file.write(f"Simulation parameters: Bs={Bs}, Br={Br}, Hc={Hc}, Hmax={Hmax}, N={N}, Lm={Lm}, Lg={Lg}, S={S}\n")

        # UNGAPPED BH-loop: saturated or minor (unsaturated)
        # Calculate lists: H (A/m), BH-loop consisting of the branches B1(T) and B2(T)
        H_values = [-Hmax + 2 * Hmax * i / (N - 1) for i in range(N)]  # Magnetising force, A/m

        # dB - branch vertical adjustment for drawing a minor loop
        dB = Bs * (H_values[N - 1] + Hc) / (abs(H_values[N - 1] + Hc) + Hc * (Bs / Br - 1.0))
        dB = (dB - (Bs * (H_values[N - 1] - Hc) / (abs(H_values[N - 1] - Hc) + Hc * (Bs / Br - 1.0)))) / 2.0

        # The following curves are vertically adjusted:
        B1_values = [(Bs * (H + Hc) / (abs(H + Hc) + Hc * (Bs / Br - 1.0)) - dB) for H in H_values]  # Upper branch
        B2_values = [(Bs * (H - Hc) / (abs(H - Hc) + Hc * (Bs / Br - 1.0)) + dB) for H in H_values]  # Lower branch

        # Find the new Hc if considering a minor BH-loop
        interp_func = interp1d(B2_values, H_values, kind='cubic')  # cubic-spline interpolation
        Hcm = float(interp_func(0))  # Hc_ungapped

        # GAPPED BH-loop: saturated or minor (unsaturated)
        mu1_values = [(B / (mu_0 * (H + Hcm))) for H, B in zip(H_values, B1_values)]  # Relative permeability for B1
        mu1_values = [1.0 if value < 1.0 else value for value in mu1_values]  # Checking the condition mu >=1
        mu2_values = [(B / (mu_0 * (H - Hcm))) for H, B in zip(H_values, B2_values)]  # Relative permeability for B2
        mu2_values = [1.0 if value < 1.0 else value for value in mu2_values]  # Checking the condition mu >=1

        R1_values = [(Lm / (S * mu_0 * mu) + Lg / (S * mu_0)) for mu in mu1_values]  # Reluctance for the upper branch
        R2_values = [(Lm / (S * mu_0 * mu) + Lg / (S * mu_0)) for mu in mu2_values]  # Reluctance for the lower branch

        # dB - branch vertical adjustment for drawing a minor loop
        dB = ((H_values[N - 1] + Hcm) / (S * R1_values[N - 1]) - (H_values[N - 1] - Hcm) / (S * R2_values[N - 1])) * Lm / 2.0

        B1_gapped_values = [((H + Hcm) * Lm / (S * R) - dB) for H, R in zip(H_values, R1_values)]  # Upper branch
        B2_gapped_values = [((H - Hcm) * Lm / (S * R) + dB) for H, R in zip(H_values, R2_values)]  # Lower branch

        # Find Hc for the gapped BH-loop
        interp_func = interp1d(B2_gapped_values, H_values, kind='cubic')  # cubic-spline interpolation
        Hcg = float(interp_func(0))  # Hc_gapped

        # Plot the ungapped BH-loop
        plt.figure()
        plt.plot(H_values, B1_values, label='B+')
        plt.plot(H_values, B2_values, label='B-')
        plt.xlabel('H, A/m')
        plt.ylabel('B, T')
        plt.title('Ungapped BH-loop: both branches')
        legend_title = f'Hc = {round(Hcm, 2)} A/m'
        plt.legend(title=legend_title, loc='lower right')  # Set the location of the legend
        plt.grid(True)
        plt.minorticks_on()
        plt.grid(True, which='minor', linestyle=':', linewidth=0.25)
        plt.show()

        # Save data for the whole BH-loop (both branches)
        with open('Ungapped_BH-loop_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['H, A/m', 'Upper B, T', 'Lower B, T'])
            for H, B1, B2 in zip(H_values, B1_values, B2_values):
                writer.writerow([H, B1, B2])

        # Plot the gapped BH-loop
        plt.figure()
        plt.plot(H_values, B1_gapped_values, label='B+')
        plt.plot(H_values, B2_gapped_values, label='B-')
        plt.xlabel('H, A/m')
        plt.ylabel('B, T')
        plt.title('Gapped BH-loop: both branches')
        legend_title = f'Hc = {round(Hcg, 2)} A/m'
        plt.legend(title=legend_title, loc='lower right')  # Set the location of the legend
        plt.grid(True)
        plt.minorticks_on()
        plt.grid(True, which='minor', linestyle=':', linewidth=0.25)
        plt.show()

        # Save data for the whole BH-loop (both branches)
        with open('Gapped_BH-loop_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['H, A/m', 'Upper B, T', 'Lower B, T'])
            for H, B1, B2 in zip(H_values, B1_values, B2_values):
                writer.writerow([H, B1, B2])

        # Plot both the ungapped and gapped BH-loops
        plt.figure()
        plt.plot(H_values, B1_values, label='B+')
        plt.plot(H_values, B2_values, label='B-')
        plt.plot(H_values, B1_gapped_values, '--', label='B+ (gapped)')
        plt.plot(H_values, B2_gapped_values, '--', label='B- (gapped)')
        plt.xlabel('H, A/m')
        plt.ylabel('B, T')
        plt.title('Ungapped and gapped BH-loops')
        legend_title = f'Hc_ungapped = {round(Hcm, 2)} A/m \nHc_gapped = {round(Hcg, 2)} A/m'
        plt.legend(title=legend_title, loc='lower right')
        plt.grid(True)
        plt.minorticks_on()
        plt.grid(True, which='minor', linestyle=':', linewidth=0.25)
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create a tkinter window
window = tk.Tk()
window.title("BH-loop Simulation")

# Set the width of the window
window.geometry("300x290")  # Adjust width as needed

# Create labels and entry fields for input values
tk.Label(window, text="Saturation induction, Bs (T):").grid(row=0, column=0)
entry_Bs = tk.Entry(window, width=15)
entry_Bs.grid(row=0, column=1)

tk.Label(window, text="Residual induction, Br (T):").grid(row=1, column=0)
entry_Br = tk.Entry(window, width=15)
entry_Br.grid(row=1, column=1)

tk.Label(window, text="Coercivity, Hc (A/m):").grid(row=2, column=0)
entry_Hc = tk.Entry(window, width=15)
entry_Hc.grid(row=2, column=1)

tk.Label(window, text="Magnetizing force, Hmax (A/m):").grid(row=3, column=0)
entry_Hmax = tk.Entry(window, width=15)
entry_Hmax.grid(row=3, column=1)

tk.Label(window, text="Number of points, N:").grid(row=4, column=0)
entry_N = tk.Entry(window, width=15)
entry_N.grid(row=4, column=1)

tk.Label(window, text="Core length, Lm (m):").grid(row=5, column=0)
entry_Lm = tk.Entry(window, width=15)
entry_Lm.grid(row=5, column=1)

tk.Label(window, text="Gap length, Lg (m):").grid(row=6, column=0)
entry_Lg = tk.Entry(window, width=15)
entry_Lg.grid(row=6, column=1)

tk.Label(window, text="Core cross-section, S (m^2):").grid(row=7, column=0)
entry_S = tk.Entry(window, width=15)
entry_S.grid(row=7, column=1)

# Load parameters from log file
btn_load_params = tk.Button(window, text="Load Parameters from Log", command=read_log_file)
btn_load_params.grid(row=8, column=0, columnspan=2, pady=10)

# Create Run and Stop buttons
btn_run = tk.Button(window, text="Run Simulation", command=run_simulation)
btn_run.grid(row=9, column=0, columnspan=2, pady=5)

btn_stop = tk.Button(window, text="Stop Simulation", command=window.destroy)
btn_stop.grid(row=10, column=0, columnspan=2)

# Start the tkinter event loop
window.mainloop()
