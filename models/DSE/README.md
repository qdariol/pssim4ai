# Design Space Exploration (DSE)
This folder contains a Python API which allows running the 54 mappings evaluation, as well as the DSE loop.
 - `clusterizator` folder: Contains the Python sub-modules with functions to generate clusterings/mappings, to generate SystemC scenarios and run them, to conduct the DSE exploration loop, etc.
 - `NN` folder: contains `.json` files which describe the Software structure of the considered artificial Neural Networks (NNs).
 - `run` folder: contains the results of the DSE exploration, including `.json` files with all the tested mappings per ANN, and the terminal log in a `.txt` file.
 - `autoscript.sh`: This script is used by the Python API to compile and run SystemC models.
 - `dse.py`: This script runs the DSE loop for the given NNs
 - `mappings_evaluation.py`: This script runs the 54 mappings as presented in the JSA article and compares the estimated quantities with measured data.
 - `results_evaluation_time.txt`: Text file which provides the evaluation time for the 54 mappings, and average evaluation time per mapping.
 - `results_model_evaluation.json`: Data-base which contains the 54 mappings information, with the estimated metrics from the SystemC models, and observed error compared to real measurements.
 - `results_model_evaluation.json`: A graphic .pdf version of the .json data-base.
 - `results_model_evaluation_analytical.json`: Similar data-base but with the results of pure analytical models instead of SystemC simulation.
 - `tested_mappings.json`: Tested mappings with measured metrics (timing, power, energy).