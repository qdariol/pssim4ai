#
# File: mapping_evaluation.py
# Description: Runs the mapping evaluation. The mapping to evaluate are described in the tested_mappings.json file,
#              which also contains the measured quantities (timing, power and energy). The results are output in
#              the results_model_evaluation.json file.
# Author:  Quentin Dariol
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

# User specified arguments
DO_ANALYTICAL_MODELS = False # Analytical models for comparison with the proposed flow.

# Max number of cores in the target platform (Default if unspecified: 7)
# Warning: the SystemC models only support up to 7 tiles.
USER_DEF_MAX_CORE = 7

# Platform specs
USER_DEF_MEMORY_SIZE_TAB = [1024,256,256,256,256,256,256]

# User specified variables: allows to perform the whole evaluation of mappings, and to obtain general statistics
DO_EVALUATION_MAPPINGS = True
DO_REPORT_EVALUATION_TIME = True
DO_STATS = True

# oooOOOooo

# Import packages
import json
from clusterizator import phase2
import glob
import os
from datetime import datetime
import numpy as np
if DO_ANALYTICAL_MODELS:
    from clusterizator import anon

################################################################################
################################################################################

# Encoder to transform np.integer into int for JSON file dumping
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# Load Neural Network (NN) definition
USER_DEF_NN_FILES = sorted(glob.glob("./NN/*.json"))
NN = {}
for nnfile in USER_DEF_NN_FILES:
    string_name_nn = nnfile.replace('./NN/', '').replace('.json', '')
    with open(nnfile, 'r') as json_file:
        NN[string_name_nn] = json.load(json_file)

################################################################################
################################################################################

if DO_EVALUATION_MAPPINGS:

    evaluation_time_tab = []

    with open('./tested_mappings.json', 'r') as json_file:
        data = json.load(json_file)

    # Store starting time
    startTime = datetime.now()
    mapping_counter = 0

    for mapping in data:
        if not(DO_ANALYTICAL_MODELS):
            str_hpp_file = mapping["application"] + '-' + str(mapping["id"]) + '.hpp'

            # If the .hpp file does not exist, create it
            if not(os.path.exists(phase2.PATH_TO_SYSTEMC + "/experiments/" + str_hpp_file)):
                phase2.CreateExperimentHPP(phase2.PATH_TO_SYSTEMC + "/experiments/" + str_hpp_file, \
                                        NN[mapping["application"]], mapping['mapping'])

            # Evaluate with polling
            startTime_mapping = datetime.now()
            mapping_counter = mapping_counter + 1
            print("Simulating " + str_hpp_file + " Polling")
            tmp_mapping = phase2.EvaluateSystemCMapping("/" + str_hpp_file, 'P', USER_DEF_MEMORY_SIZE_TAB)
            mapping['results_P']['predicted_time']               = tmp_mapping['p_e2e']
            mapping['results_P']['predicted_computation_rate']   = tmp_mapping['computation_rate']
            mapping['results_P']['predicted_rdwr_rate']          = tmp_mapping['rdwr_rate']
            mapping['results_P']['predicted_wait_rate']          = tmp_mapping['wait_rate']
            mapping['results_P']['predicted_communication_rate'] = tmp_mapping['comm_rate']
            mapping['results_P']['predicted_power']              = tmp_mapping['p_power']
            mapping['results_P']['predicted_energy']             = tmp_mapping['p_energy']
            # Error evaluation
            if 'measured_time' in mapping['results_P']:
                mapping['results_P']["prediction_error_time"] = ((float(mapping['results_P']['predicted_time']) \
                - float(mapping['results_P']['measured_time'])) / float(mapping['results_P']['measured_time']))*100
            if 'measured_power' in mapping['results_P']:
                mapping['results_P']["prediction_error_power"] = ((mapping['results_P']['predicted_power'] \
                - mapping['results_P']['measured_power']) / mapping['results_P']['measured_power'])*100
            if 'measured_energy' in mapping['results_P']:
                mapping['results_P']["prediction_error_energy"] = ((mapping['results_P']['predicted_energy'] \
                - mapping['results_P']['measured_energy']) / mapping['results_P']['measured_energy'])*100
            evaluation_time_tab.append(datetime.now() - startTime_mapping)

            # Evaluate with interrupt + clock gating
            startTime_mapping = datetime.now()
            mapping_counter = mapping_counter + 1
            print("Simulating " + str_hpp_file + " Clock gated")
            tmp_mapping = phase2.EvaluateSystemCMapping("/" + str_hpp_file, 'CG', USER_DEF_MEMORY_SIZE_TAB)
            mapping['results_CG']['predicted_time']               = tmp_mapping['p_e2e']
            mapping['results_CG']['predicted_computation_rate']   = tmp_mapping['computation_rate']
            mapping['results_CG']['predicted_rdwr_rate']          = tmp_mapping['rdwr_rate']
            mapping['results_CG']['predicted_wait_rate']          = tmp_mapping['wait_rate']
            mapping['results_CG']['predicted_communication_rate'] = tmp_mapping['comm_rate']
            mapping['results_CG']['predicted_power']              = tmp_mapping['p_power']
            mapping['results_CG']['predicted_energy']             = tmp_mapping['p_energy']
            # Error evaluation
            if 'measured_time' in mapping['results_CG']:
                mapping['results_CG']["prediction_error_time"] = ((float(mapping['results_CG']['predicted_time']) \
                - float(mapping['results_CG']['measured_time'])) / float(mapping['results_CG']['measured_time']))*100
            if 'measured_power' in mapping['results_CG']:
                mapping['results_CG']["prediction_error_power"] = ((mapping['results_CG']['predicted_power'] \
                - mapping['results_CG']['measured_power']) / mapping['results_CG']['measured_power'])*100
            if 'measured_energy' in mapping['results_CG']:
                mapping['results_CG']["prediction_error_energy"] = ((mapping['results_CG']['predicted_energy'] \
                - mapping['results_CG']['measured_energy']) / mapping['results_CG']['measured_energy'])*100
            evaluation_time_tab.append(datetime.now() - startTime_mapping)

            # Print total mapping evaluation time
            if DO_REPORT_EVALUATION_TIME:
                total_mapping_eval_time = datetime.now() - startTime
                print('Mapping evaluation terminated! Total execution time: ' + str(total_mapping_eval_time))
                print('Average evaluation time per mapping: ' + str(total_mapping_eval_time/mapping_counter))
                print('Maximum evaluation time: ' + str(max(evaluation_time_tab)))
                print('Minimum evaluation time: ' + str(min(evaluation_time_tab)))

            # Save data
            with open('./results_model_evaluation.json', 'w') as fout:
                json.dump(data, fout, sort_keys=True, indent=4, cls=NpEncoder)
        else:
            # startTime = datetime.now()
            for mode in ["P", "CG"]:
                # Second returned parameter is throughput, which is disregarded in this approach. Hence the empty variable.
                empty = 0
                mode_str = 'results_' + mode
                mapping[mode_str]['predicted_time'], empty, mapping[mode_str]['predicted_power'], mapping[mode_str]['predicted_energy'] =\
                    anon.EvaluateMappingManuscript(NN[mapping['application']], mapping['mapping'], mode, USER_DEF_MEMORY_SIZE_TAB)
                mapping[mode_str]['predicted_time'] = int(mapping[mode_str]['predicted_time'])
                # mapping["anon_error_e2e"] = ((mapping['anon_e2e']-float(mapping['m_e2e']))/float(mapping['m_e2e']))*100
                # mapping["anon_error_throughput"] = ((mapping['anon_throughput']-float(mapping['m_throughput']))/float(mapping['m_throughput']))*100
                # mapping["anon_error_power"] = ((mapping['anon_power']-float(mapping['m_power']))/float(mapping['m_power']))*100
                # mapping["anon_error_energy_e2e"] = ((mapping['anon_energy_e2e']-float(mapping['m_energy_e2e']))/float(mapping['m_energy_e2e']))*100

                # Error evaluation
                if 'measured_time' in mapping[mode_str]:
                    mapping[mode_str]["prediction_error_time"] = ((float(mapping[mode_str]['predicted_time']) \
                    - float(mapping[mode_str]['measured_time'])) / float(mapping[mode_str]['measured_time']))*100
                if 'measured_power' in mapping[mode_str]:
                    mapping[mode_str]["prediction_error_power"] = ((mapping[mode_str]['predicted_power'] \
                    - mapping[mode_str]['measured_power']) / mapping[mode_str]['measured_power'])*100
                if 'measured_energy' in mapping[mode_str]:
                    mapping[mode_str]["prediction_error_energy"] = ((mapping[mode_str]['predicted_energy'] \
                    - mapping[mode_str]['measured_energy']) / mapping[mode_str]['measured_energy'])*100

            with open('./results_model_evaluation_anon.json', 'w') as fout:
                json.dump(data, fout, sort_keys=True, indent=4, cls=NpEncoder)
            # print('anon_validation.py script execution time: ' + str(datetime.now() - startTime))




if DO_STATS:
    if not(DO_ANALYTICAL_MODELS):
        with open('./results_model_evaluation.json', 'r') as json_file:
            data = json.load(json_file)
    else:
        with open('./results_model_evaluation_anon.json', 'r') as json_file:
            data = json.load(json_file)

    counter = 0
    max_error_energy = 0
    max_error_time = 0
    max_error_power = 0
    avg_error_energy = 0
    avg_error_time = 0
    avg_error_power = 0

    for mapping in data:
        counter = counter+1
        # Energy
        avg_error_energy = avg_error_energy+abs(mapping['results_P']["prediction_error_energy"])
        if(abs(mapping['results_P']["prediction_error_energy"])>max_error_energy):
            max_error_energy = abs(mapping['results_P']["prediction_error_energy"])
        # Time
        avg_error_time = avg_error_time+abs(mapping['results_P']["prediction_error_time"])
        if(abs(mapping['results_P']["prediction_error_time"])>max_error_time):
            max_error_time = abs(mapping['results_P']["prediction_error_time"])
        # Power
        avg_error_power = avg_error_power+abs(mapping['results_P']["prediction_error_power"])
        if(abs(mapping['results_P']["prediction_error_power"])>max_error_power):
            max_error_power = abs(mapping['results_P']["prediction_error_power"])

    avg_error_time = avg_error_time/counter
    avg_error_power = avg_error_power/counter
    avg_error_energy = avg_error_energy/counter

    print("avg_error_time: " + '{0:.2f}'.format(avg_error_time) + ' %')
    print("avg_error_power: " + '{0:.2f}'.format(avg_error_power)+ ' %')
    print("avg_error_energy: " + '{0:.2f}'.format(avg_error_energy)+ ' %')
    print("max_error_time: " + '{0:.2f}'.format(max_error_time)+ ' %')
    print("max_error_power: " + '{0:.2f}'.format(max_error_power)+ ' %')
    print("max_error_energy: " + '{0:.2f}'.format(max_error_energy)+ ' %')

    if (DO_ANALYTICAL_MODELS):
        with open('./results_model_evaluation.json', 'r') as json_file:
            simu_data = json.load(json_file)

        for simu_mapping in simu_data:
            for mapping in data:
                if (mapping["id"] == simu_mapping["id"]):
                    for mode in ["results_P", "results_CG"]:
                        mapping[mode]["predicted_communication_rate"] = simu_mapping[mode]["predicted_communication_rate"]
                    break

        with open('./results_model_evaluation_anon.json', 'w') as fout:
            json.dump(data, fout, sort_keys=True, indent=4, cls=NpEncoder)