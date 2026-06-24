# pSSim4AI project open source repository
The pSSim4AI project introduces a hybrid modeling flow for early timing and energy prediction of Artificial Neural Networks (ANNs) mappings on edge multi-core platforms. The flow combines Electronic System Level (ESL) simulation in SystemC TLM, analytical computation and communication models, and a detailed calibration approach through measurements. This enables achieving high prediction accuracy and speed while offering good re-applicability accross settings.

The proposed models are fast (<2s evaluation time) and accurate (>97% accuracy on timing, >93% on energy), tested across a wide range of neural network application mappings and settings (54 mappings with e.g. different number of processing cores, communication rates, power management settings). We provide a Design Space Exploration (DSE) flow, which shows up to 24% improvement in inference time and 16% in energy compared to baseline implementation.

Find out more in our [2026 Journal of Systems Architecture article](https://doi.org/10.1016/j.sysarc.2026.103738).

![figures/overview_flow.png](https://github.com/qdariol/pssim4ai/blob/main/figures/overview_flow.png)

Figure - Proposed modeling and Design Space Exploration (DSE) flow in the scope of the pSSim4AI project

## List of folders
The pSSim4AI project open source Git repository is organized as follows:
* `./figures`: Contains the flow figure.
* `./jsa_results`: Contains the results as presented in our JSA article. Contains also Python scripts which are used to display the results.
* `./models`: Contains the proposed models and the DSE flow.
  * `./models/DSE`: This folder contains a Python API which allows automatically running the model evaluation (54 mappings tested in our JSA article) and the DSE loop. It also contains the data presented in our article. It is recommended to use the scripts in this folder to run our experiments.
  * `./models/MessageLevelSystemCModel`: implementation of the SystemC modeling flow. We recommend to use the API in the DSE folder to run our SystemC models.

## Dependencies
* GNU/Linux with bash
* g++ or clang++ (10.0.0) with C++14 support
* SystemC (2.3.2 or 2.3.3)
* Python 3.6.9

## Contributors
This project was led in 2020-2023 in collaboration between the Institute Systems Engineering for Future Mobility (DLR-SE), Oldenburg, Germany and the Institut d'Électronique et des Technologies du numéRique (IETR) UMR CNRS 6164, Nantes Université, Nantes, France.

* Quentin Dariol:
  * Adaptation of the SystemC timing modeling flow from pSSim4MC project for ANNs
    * Computation time model for ANNs,
    * Recalibration of communication time model for interrupt-based + clock gating communications,
    * Prediction and measurement for various mappings of 4 different ANNs applications.
  * Implementation of clock gating on the interrupt-based version of the pSSim4MC platform,
  * Power and energy modeling flow for ANNs on multi-core platforms,
  * Design Space Exploration and evaluation automation.
* Research work supervised by Sebastien Le Nours, Sebastien Pillement, Kim Grüttner, Domenik Helms and Ralf Stemmer.
* Elements from the pSSim4MC project:
  * Ralf Stemmer: base framework in SystemC, implementation platform prototype, tools for the implementation of SDF applications on multi-core platforms, communication time model.
    * The contributions of Ralf Stemmer will be available on the following Zenodo repository: <https://zenodo.org/record/7976829>
    * Ralf Stemmer supervised bachelor work that led to the creation of the interrupt-based version of the prototype platform.
  * Hai Dang Vu: Communication time model, base framework in SystemC.

## Publications
You can read more on this project on the following publications:

### PhD thesis
- [**PhDThesis'2023:** Early Timing and Energy Prediction and Optimization of Artificial Neural Networks on Multi-Core Platforms, Nantes Université](https://theses.hal.science/tel-04390337v1)

### International journal article
- [**JSA'2026:** A Measurement-Based Calibration Approach for Highly Scalable Timing and Energy Modeling of EdgeAI Multi-Core Systems](https://doi.org/10.1016/j.sysarc.2026.103738)

### Lectures in international conferences
- [**RAPIDO'2023:** Fast Yet Accurate Timing and Power Prediction of Artificial Neural Networks Deployed on Clock-Gated Multi-Core Platforms](https://dx.doi.org/10.1145/3579170.3579263)
- [**SAMOS'2022:** A Hybrid Performance Prediction Approach for Fully-Connected Artificial Neural Networks on Multi-core Platforms](https://dx.doi.org/10.1007/978-3-031-15074-6_16)

### Poster presentations
- [**GRETSI'2023:** Early Performance and Energy Prediction of Neural Networks Deployed on Multi-Core Platforms](https://hal.science/hal-04186902)
- [**GDRSOC'2022:** Hybrid Performance Prediction Models for Fully-Connected Neural Networks on MPSoC](https://hal.science/hal-03758026)
- [**GDRSOC'2021:** A Measurement-based Performance Evaluation Framework for Neural Networks on MPSoC](https://hal.science/hal-03248152)

### Technical report
- [**TechReport'2022:** Setup of an Experimental Framework for Performance Modeling and Prediction of Embedded Multicore AI Architectures](https://hal.science/hal-03546804)

## License
The pSSim4AI open source repository is released under the BSD-3-Clause license, a free software license approved by the open source initative.