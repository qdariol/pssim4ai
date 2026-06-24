# Experiments folder
The 'experiments' folder contains the architecture's description of the evaluated mappings in our SystemC executable model.
Files in this folder are in the '.hpp' format. They are included in the '.main.hpp', which itself is included in the 'main.cpp' file.
It is possible to select the tested scenario by uncommenting it in the main.hpp file, and commenting all the others.
Compiling the model using the build.sh script will then build the executable model to simulate this scenario.

Note: The selection of clock gating mode is done in the main.hpp file by specifying the parameter ENABLE_CLOCK_GATING.
"#ifdef ENABLE_CLOCK_GATING 1" : Interrupt-based communications with clock gating
"#ifdef ENABLE_CLOCK_GATING 0" : Polling-based communications without clock gating

# Scenario description
The following scenarios are available:
 - MLP1-[1:7].hpp: tested mappings for the MLP1. MLP1[8:14] do not exist: in fact, they are the same mappings as MLP1-[1:7] but with interrupt comm. + clock gating. The selection of mode (polling or interrupt) is done in main.hpp.
 - MLP2-[15:21].hpp: tested mappings for the MLP2.
  -MLP3-[29:35].hpp: tested mappings for the MLP3.
  -CNN-[43:48].hpp: tested mappings for the CNN.

More information regarding the scenarios, such as the exact mapping, measured evaluated quantities, etc. in the files `models/DSE/tested_mappings.json` and `models/DSE/results_model_evaluation.json`.
