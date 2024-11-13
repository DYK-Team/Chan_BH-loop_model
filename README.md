A Python program with a graphical user interface (GUI), Chan_model.py, has been developed to implement and reproduce Chan's model, a widely recognized approach for simulating the magnetic hysteresis behaviour of ferromagnetic cores. This tool provides the capability to simulate B-H loops (magnetic flux density vs. magnetic field intensity) in magnetic cores under various conditions, including configurations with and without an air gap. The program offers an intuitive interface that allows users to define key parameters, such as the core material properties, gap size, and excitation conditions. By leveraging Chan's model, it accurately predicts the nonlinear hysteresis behaviour of the core material, capturing essential features like coercivity, remanence, and saturation.

For more information on Chan's model, please refer to: https://ieeexplore.ieee.org/document/75630

This model is used for simulating non-linear behaviour of transformers in LTspice: https://www.allaboutcircuits.com/technical-articles/simulating-non-linear-transformers-in-ltspice/ See the attached report "A case study on magnetic cores_All.pdf".

Output files of Chan_model.py (algorithm with GUI): "Ungapped_BH-loop_data.csv" and "Gapped_BH-loop_data.csv". Input parameters from the previous program run are saved in "simulation_log.log" (do not delete this file!) and can be called from GUI.

"A case study on magnetic cores_All.pdf" is the main report with all necessary files attached.

"Nonlinear_transformer_model_for_circuit_simulation.pdf" is the original Chan's paper.

"Magnetic circuits.ppsx" is a Power Point Slide Show (PPS) on magnetic circuits for college students. It can be seen after downloading.

"Introduction to electrodynamics.ppsx" is a Power Point Slide Show (PPS) on electromagnetic principles for college students. It can be seen after downloading.

The folder "LTspice_Non-linear_Transformer" contains the LTspice simulation file for a non-linear transformer. 
