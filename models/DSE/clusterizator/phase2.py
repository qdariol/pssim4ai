#
# File: phase2.py
# Date of creation (dd.mm.yyyy): 08.03.2023
# Description: Functions for the second phase of the DSE of neural networks on embedded multi-core platforms
# Author: Quentin Dariol
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

import sys
import os
import os.path
import copy
import json
import numpy as np
# ~ import copy
import fileinput
from re import search
import subprocess

# ~ sys.path.insert(0, './clusterizator/')
from clusterizator import common as co
from clusterizator import trace_decoder as td

################################################################################
# Clusterizator phase 2 (SystemC) main functions
#    - CreateExperimentHPP: '''Generates the experiment.hpp file for the specified NN mapping'''
#
#    - Internal use only:
#         - __debug_clusterizator_phase2:
#           '''Internal function used to test and validate SystemC file generation and simulation'''
################################################################################

################################################################################

# Global variables
# Path to SystemC simulation model folder - Note to user: you might need to update this with your own setup.
PATH_TO_SYSTEMC = '../MessageLevelSystemCModel'
PATH_TO_EXPERIMENTS = PATH_TO_SYSTEMC + '/experiments'

################################################################################

def __GetChannels(NN, mapping):
    '''Internal: Returns the list of all channels for a mapping of NN'''
    channels = []
    for l in range(len(NN)):
        cluster = len(mapping[l])

        # Sender
        str_senders = []
        if l == 0:
            str_senders = ['input']
        else:
            cluster_previous = len(mapping[l-1])
            for c in range(cluster_previous):
                str_senders.append('l' + str(l) + 'c' + str(c+1))

        # Receiver
        str_receivers = []
        cluster = len(mapping[l])

        for c in range(cluster):
            str_receivers.append('l' + str(l+1) + 'c' + str(c+1))

        # Now writing the events
        for str_sender in str_senders:
            for str_receiver in str_receivers:
                channels.append(str_sender + '_' + str_receiver)

        # Output channel (SDF graph sink) and decoder
        # This comes in addition to the rest of the channels
        if l == len(NN)-1:
            # By default no decoder
            doDecoder = False

            # Sender
            str_senders = []
            for c in range(cluster):
                str_senders.append('l' + str(l+1) + 'c' + str(c+1))

            # If cluster == 1: no need for decoder.
            if cluster == 1:
                # Receiver
                str_receivers = ['output']
            # Else additional decoder actor is implemented to pick up all channels from the clusterized output layer
            # and output a single channel
            else:
                # Receiver
                str_receivers = ['decoder']
                doDecoder = True

            # Now writing the events
            for str_sender in str_senders:
                for str_receiver in str_receivers:
                    channels.append(str_sender + '_' + str_receiver)

            # Decoder actor
            if doDecoder:
                str_sender = 'decoder'
                str_receiver = 'output'
                channels.append(str_sender + '_' + str_receiver)

    return channels

################################################################################

def __GetChannelsForActor(NN, mapping, l, c):
    '''Internal: Returns a dictionnary containing the list of read and write channels for an actor'''

    # This function is very much like the __GetChannels except we know the layer_nb and cluster_nb that we need.
    channels = {'read':[], 'write':[]}

    # ~~~oooOooo~~~
    # 1. Channels to read from the previous layer of considered actor: channels['read']

    # Receiver
    # The receiver is our specified layer, specified cluster c
    # If l is one index further than the total number of layers (len(NN)) then it means it is the decoder
    if l == len(NN):
        str_receiver = 'decoder'
    else:
        str_receiver = 'l' + str(l+1) + 'c' + str(c+1)

    # If first layer, the channel is with the input layer. isInput tag enabled.
    if l == 0:
        str_sender = 'input'
        channel = {}
        channel['channel_name'] = str_sender + '_' + str_receiver
        channel['nb_tokens'] = "INPUT_TOKENS_SIZE"
        channel['isInput'] = 1
        channel['isDecoder'] = 0
        channel['isOutput'] = 0
        channels['read'].append(channel)
    else:
        cluster_previous = len(mapping[l-1])
        for cc in range(cluster_previous):
            channel = {}
            str_sender = "l" + str(l) + "c" + str(cc+1)
            channel['channel_name'] = str_sender + '_' + str_receiver
            channel['nb_tokens'] = "L" + str(l) + "_C" + str(cc+1)
            channel['isInput'] = 0
            channel['isDecoder'] = 0
            channel['isOutput'] = 0
            channels['read'].append(channel)

    # ~~~oooOooo~~~
    # 2. Channels to write from the next layer of considered actor: channels['write']

    # Sender
    # The sender is our specified layer, specified cluster
    # If l is one index further than the total number of layers (len(NN)) then it means it is the decoder
    if l == len(NN):
        str_sender = 'decoder'
    else:
        str_sender = 'l' + str(l+1) + 'c' + str(c+1)

    channel = {}

    if l == len(NN):
        # If the actor is the decoder
        str_receiver = 'output'
        channel['channel_name'] = str_sender + '_' + str_receiver
        channel['nb_tokens'] = "L" + str(l) + "_TOTAL_TOKENS_OUT"
        channel['isInput'] = 0
        channel['isDecoder'] = 0
        channel['isOutput'] = 1
        channels['write'].append(channel)

    elif l == len(NN)-1:
        # If l is the last layer, then the channel links to either the output if cluster=1, or the decoder otherwise.
        if len(mapping[l]) == 1:
            # If cluster == 1: no decoder, send directly to output
            str_receiver = 'output'
            channel['channel_name'] = str_sender + '_' + str_receiver
            channel['nb_tokens'] = "L" + str(l+1) + "_C" + str(c+1)
            channel['isInput'] = 0
            channel['isDecoder'] = 1
            channel['isOutput'] = 1
            channels['write'].append(channel)
        else:
            # If last layer has clustering > 1, then the decoder is
            channel = {}
            str_receiver = 'decoder'
            channel['channel_name'] = str_sender + '_' + str_receiver
            channel['nb_tokens'] = "L" + str(l+1) + "_C" + str(c+1)
            channel['isInput'] = 0
            channel['isDecoder'] = 1
            channel['isOutput'] = 0
            channels['write'].append(channel)


    else:
        # If this is not the last layer
        cluster_next = len(mapping[l+1])
        for cc in range(cluster_next):
            channel = {}
            str_receiver = "l" + str(l+2) + "c" + str(cc+1)
            channel['channel_name'] = str_sender + '_' + str_receiver
            channel['nb_tokens'] = "L" + str(l+1) + "_C" + str(c+1)
            channel['isInput'] = 0
            channel['isDecoder'] = 0
            channel['isOutput'] = 0
            channels['write'].append(channel)

    return channels

################################################################################

def CreateExperimentHPP(pathToOutputFile, NN, mapping):
    '''Generates the experiment.hpp file for the specified NN mapping'''
    f = open(pathToOutputFile, "w")

    # ~~~oooOooo~~~
    # Header
    f.write("#ifndef EXPERIMENT_HPP\r\n")
    f.write("#define EXPERIMENT_HPP\r\n\r\n")

    f.write("#include <iostream>\r\n")
    f.write("#include <cstdlib>\r\n")
    f.write("#include <fstream>\r\n")
    f.write("#include <tile.hpp>\r\n")
    f.write("#include <channel.hpp>\r\n")
    f.write("#include <utils.hpp>\r\n\r\n\r\n")

    # ~~~oooOooo~~~
    # Cluster sizes definition
    f.write("/** Cluster sizes definition **/\r\n\r\n")
    for l in range(len(NN)):
        if l == 0:
            tmp_string = "#define INPUT_TOKENS_SIZE " + str(np.prod(NN[l]['token_in'])) + "\r\n"
            f.write(tmp_string)
        # cluster = number of clusters in the mapping for the layer l
        cluster = len(mapping[l])

        if (NN[l]['layer_type'] == 'c'):
            tmp_string = "#define L" + str(l+1) + "_TOTAL_TOKENS_OUT " + str(np.prod(NN[l]["token_process_in"])) + "\r\n"
            f.write(tmp_string)
            tmp_string = "#define L" + str(l+1) + "_CONV_FILTER_SIZE " + str(np.prod(NN[l]["filter_dim"])) + "\r\n"
            f.write(tmp_string)
            tmp_string = "#define L" + str(l+1) + "_CONV_NB_FILTERS " + str(np.prod(NN[l]["features_nb"])) + "\r\n"
            f.write(tmp_string)
            cluster_sizes = co.GetClusterSize(NN[l], cluster)
            for c in range (cluster):
                tmp_string = "#define L" + str(l+1) + "_C" + str(c+1) + " " + str(cluster_sizes[c]) + "\r\n"
                f.write(tmp_string)
        elif (NN[l]['layer_type'] == 'd'):
            tmp_string = "#define L" + str(l+1) + "_TOTAL_TOKENS_OUT " + str(NN[l]['features_nb']) + "\r\n"
            f.write(tmp_string)
            cluster_sizes = co.GetClusterSize(NN[l], cluster)
            for c in range (cluster):
                tmp_string = "#define L" + str(l+1) + "_C" + str(c+1) + " " + str(cluster_sizes[c]) + "\r\n"
                f.write(tmp_string)
        elif (NN[l]['layer_type'] == 'p'):
            tmp_string = "#define L" + str(l+1) + "_TOTAL_TOKENS_OUT " + str(np.prod(NN[l]['token_out'])) + "\r\n"
            f.write(tmp_string)
            tmp_string = "#define L" + str(l+1) + "_C" + str(1) + " " + str(np.prod(NN[l]['token_out'])) + "\r\n"
            f.write(tmp_string)
    f.write("\r\n")

    # ~~~oooOooo~~~
    # Delay definition
    f.write("/** Delay definition **/\r\n\r\n")
    for l in range(len(NN)):
        cluster = len(mapping[l])
        for c in range (cluster):

            # Common part
            tmp_string = "auto Delay_L" + str(l+1) + "_C" + str(c+1) + " = DelayVector("

            # If the NN is a MLP (contains only dense layers) thus trained with LibFANN
            if co.IsMLP(NN):
                # if first layer, the token number #defined value is slightly different
                if l==0:
                    tmp_string += "INPUT_TOKENS_SIZE, L" + str(l+1) + "_C" + str(c+1) + ");\r\n"
                else:
                    tmp_string += "L" + str(l) +"_TOTAL_TOKENS_OUT, L" + str(l+1) + "_C" + str(c+1) + ");\r\n"
                f.write(tmp_string)

            elif (NN[l]["layer_type"] == 'c'):
                tmp_string += "L" + str(l+1) + "_C" + str(c+1) + ", "
                tmp_string += "L" + str(l+1) + "_TOTAL_TOKENS_OUT" + ", "
                tmp_string += "L" + str(l+1) + "_CONV_FILTER_SIZE" + ", "
                tmp_string += "CONVOLUTION, RELU);\r\n"
                f.write(tmp_string)

            elif (NN[l]["layer_type"] == 'd'):
                # if first layer, the token number #defined value is slightly different
                if l==0:
                    tmp_string += "INPUT_TOKENS_SIZE, L" + str(l+1) + "_C" + str(c+1) + ", "
                else:
                    tmp_string += "L" + str(l) +"_TOTAL_TOKENS_OUT, L" + str(l+1) + "_C" + str(c+1) + ", "
                tmp_string += "DENSE, RELU);\r\n"
                f.write(tmp_string)

            elif (NN[l]["layer_type"] == 'p'):
                tmp_string += "L" + str(l) + "_CONV_NB_FILTERS" + ", "
                tmp_string += "L" + str(l) + "_TOTAL_TOKENS_OUT" + ", "
                tmp_string += "MAXPOOLING, NONE);\r\n"
                f.write(tmp_string)

            else:
                tmp_string += str(NN[l]["delay"][0]) + ", OTHER);\r\n"

    f.write("\r\n")

    # ~~~oooOooo~~~
    # Event definition
    f.write("/** Event definition **/\r\n\r\n")
    f.write("sc_core::sc_event   ")
    IsFirstEvent = True

    # Get the list of channels
    channels = __GetChannels(NN, mapping)
    last_channel = channels[-1]

    for channel in channels:
        # First event: different spacing. The generated file will be cleaner for the reader.
        if IsFirstEvent:
            IsFirstEvent = False
            str_tmp = "write_" + channel + ', '
        else :
            str_tmp = "                    write_" + channel + ', '
        f.write(str_tmp)
        str_tmp = str_tmp.replace("write_", "read_")
        str_tmp = str_tmp.replace("                    ", "")
        str_tmp += '\r\n'
        # Last event: comma , at the end of the line replaced by semi-column ;
        if (channel == last_channel):
            str_tmp = str_tmp.replace(",", ";")
        f.write(str_tmp)

    f.write("\r\n")

    # ~~~oooOooo~~~
    # Buffer availability definition
    f.write("/** Buffer availability definition **/\r\n\r\n")
    for channel in channels:
        f.write("bool buff_" + channel + " = 1;\r\n")
    f.write("\r\n")

    # ~~~oooOooo~~~
    # Latency definition
    f.write("/** Main latency markers definition **/\r\n\r\n")
    f.write("double t_latency = 0;\r\n")
    f.write("sc_core::sc_time start[1000000];\r\n")
    f.write("sc_core::sc_time stop[1000000];\r\n")
    f.write("sc_core::sc_time latency[1000000];\r\n\r\n\r\n\r\n\r\n")

    # ~~~oooOooo~~~
    # Tile and mapping declaration
    # Note: regardless of the mapping, the current simulation's structure support 7 tiles. They must all be declared.
    # If the tile's mapping is empty, the tile won't be in the execution traces and won't be considered by the power model.
    f.write("/** Tiles and mapping **/\r\n\r\n")
    for t in range(7):

        tile_name = "MB" + str(t)

        # Tile initialization
        str_tmp = "class MB" + str(t) + " : public Tile\r\n{\r\n    public:\r\n        "
        str_tmp += "MB" + str(t) + '() : Tile(sc_core::sc_module_name("' + tile_name + '")) {};\r\n    '
        str_tmp += "protected:\r\n        void Execute();\r\n};\r\n\r\n"
        f.write(str_tmp)

        # Mapping declaration
        str_tmp = "void " + tile_name + "::Execute()\r\n{\r\n    for(int i = 0; i < num_iter; i++)\r\n    {\r\n"
        f.write(str_tmp)

        # Parsing all actors (clusters of each layer)
        # We take len(mapping) this time to also have the decoder actor
        for l in range(len(mapping)):
            cluster = len(mapping[l])
            for c in range(cluster):
                # If this actor is mapped onto tile t
                if mapping[l][c] == t+1:

                    doSink = False

                    # If this is the very first actor of the graph, add the graph source (iteration start marker)
                    if (l == 0):
                        if (c == 0):
                            f.write('        //Source\r\n        std::cout << i << ",ITERATION,START," << sc_core::' \
                            + 'sc_time_stamp().value()/1000 << std::endl;\r\n\r\n')

                    # Comment to help the reader identify actors
                    # if l==len(NN), the actor is the decoder
                    if l == len(NN):
                        f.write('        // Actor Decoder\r\n')
                    else:
                        f.write('        // Actor L' + str(l+1) + '_C' + str(c+1) + '\r\n')

                    # If this is the first actor: then generate the source of SDF graph and IT START
                    # Get actor's channels
                    channels = __GetChannelsForActor(NN, mapping, l, c)

                    # Comm channels read
                    for channel in channels['read']:
                        str_tmp = "        buff_" + channel['channel_name'] + ' = this->ReadTokens(read_' \
                                  + channel['channel_name'] + ', write_' + channel['channel_name'] + ', buff_' \
                                  + channel['channel_name'] + ', ' + str(channel['isInput']) + ', ' + channel['nb_tokens'] \
                                  + ', t_r_loop, i, ENABLE_CLOCK_GATING);\r\n'
                        f.write(str_tmp)

                    if l == len(NN):
                        # If this actor is the decoder (it is one layer more than the last layer of the NN)
                        # No computation time delay
                        pass
                    else:
                        # Delay of actor
                        str_tmp = '        std::cout << i << ",' + tile_name + ','
                        str_tmp += 'L' + str(l+1) + '_C' + str(c+1) + ',START,"'
                        str_tmp += " << sc_core::sc_time_stamp().value()/1000 << std::endl;\r\n"
                        str_tmp += "        sc_core::wait(Delay_L" + str(l+1) + "_C" + str(c+1) + ".GetDelay());\r\n"
                        str_tmp += '        std::cout << i << ",' + tile_name + ','
                        str_tmp += 'L' + str(l+1) + '_C' + str(c+1) + ',STOP,"'
                        str_tmp += " << sc_core::sc_time_stamp().value()/1000 << std::endl;\r\n"
                        f.write(str_tmp)

                    # Comm channels write
                    for channel in channels['write']:
                        str_tmp = "        buff_" + channel['channel_name'] + ' = this->WriteTokens(read_' \
                                  + channel['channel_name'] + ', write_' + channel['channel_name'] + ', buff_' \
                                  + channel['channel_name'] + ', ' + str(channel['isOutput']) + ', ' + channel['nb_tokens'] \
                                  + ', t_r_loop, i, ENABLE_CLOCK_GATING);\r\n'
                        f.write(str_tmp)
                        if channel['isOutput'] == 1:
                            doSink = True

                    if doSink:
                        f.write('\r\n        //Sink\r\n        std::cout << i << ",ITERATION,STOP," << sc_core::' \
                        + 'sc_time_stamp().value()/1000 << std::endl;')

                    f.write('\r\n')

        str_tmp = "    }\r\n}\r\n\r\n"
        f.write(str_tmp)

    # ~~~oooOooo~~~
    # Close the file and return
    f.write('#endif')
    f.close()
    return

################################################################################

def EvaluateSystemCMapping(scenario_file_name, mode, memorysizetab):
    # Mapping found
    mappingIsFound = False
    comment_character = "//~ "
    include_exp = "#include <experiments"

    # Security delete tmp.txt in case it wasn't in previous runs
    run_cmd = "rm tmp.txt 2> /dev/null"
    subprocess.run(run_cmd, shell=True)

    # Open the file f
    f = open(PATH_TO_SYSTEMC + '/main.hpp', mode='r')

    # Read all lines
    lines = f.read()
    lines = lines.split("\n")
    for i in range(len(lines)):

        #  Check and select operating mode in main.hpp
        if ("#define ENABLE_CLOCK_GATING" in lines[i]):
            if (mode=='CG'): #Interrupt with clock gating
                if ("ENABLE_CLOCK_GATING 0" in lines[i]):
                    lines[i] = lines[i].replace("0", "1")
            else: #Polling without clock gating
                if ("ENABLE_CLOCK_GATING 1" in lines[i]):
                    lines[i] = lines[i].replace("1", "0")

        # Unselect all scenarios except the one we want
        elif include_exp in lines[i]:
            if scenario_file_name in lines[i]:
                mappingIsFound = True
                if comment_character in lines[i]:
                    lines[i] = lines[i].lstrip(comment_character)
            elif not(comment_character in lines[i]):
                lines[i] = comment_character + lines[i]

        # If we reach the #endif at the end of the file and the mapping was not found, add the line
        elif ("#endif" in lines[i]) and (not(mappingIsFound)):
            mappingIsFound = True
            lines[i] = include_exp + scenario_file_name + ">\r\n\r\n" + lines[i]

        # Add return to line back to all lines
        lines[i] = lines[i] + '\r\n'

    # Popping the unnecessary empty lines at the end of the file
    while not("#endif" in lines[-1]):
        lines.pop()

    # Rewrite the file
    f.close()
    f = open(PATH_TO_SYSTEMC + '/main.hpp',mode='w')
    for line in lines:
        f.write(line)
    f.close()

    # Run the mapping
    run_cmd = "./autoscript.sh -m " + mode + " 2> /dev/null"
    os.system(run_cmd)

    td.TraceDecoder(PATH_TO_SYSTEMC + "/out.csv", mode) #


    # The execution data of the mapping are output to tmp.txt in the same folder as where the DSE python script is launched.
    # We read into it to extract the systemC predicted metrics.
    current_scenario = {}
    with open('./tmp.txt') as f:
        for line in f:
            if ("Average execution time" in line):
                line = line.split()
                current_scenario["p_execution_time"] = float(line[len(line)-1])

            if ("Average end to end latency" in line):
                line = line.split()
                current_scenario["p_e2e"] = float(line[len(line)-1])

            if ("Average throughput" in line):
                line = line.split()
                current_scenario["p_throughput"] = float(line[len(line)-1])

            if ("Average computation rate per tile" in line):
                line = line.split()
                current_scenario["computation_rate"] = float(line[len(line)-1])

            if ("Average RdWr" in line):
                line = line.split()
                current_scenario["rdwr_rate"] = float(line[len(line)-1])

            if ("Average waiting" in line):
                line = line.split()
                current_scenario["wait_rate"] = float(line[len(line)-1])

            if ("Average communication rate" in line):
                line = line.split()
                current_scenario["comm_rate"] = float(line[len(line)-1])

            if ("Total predicted power consumption" in line):
                line = line.split()
                current_scenario["p_power"] = float(line[len(line)-1])

            if ("Total predicted energy consumption" in line):
                line = line.split()
                current_scenario["p_energy"] = float(line[len(line)-1])

            if ("Simulation + trace_decoder.py execution time" in line):
                line = line.split()
                current_scenario["simulation_time"] = float(line[len(line)-2])

    # Delete tmp.txt
    run_cmd = "rm tmp.txt out.csv 2> /dev/null"
    subprocess.run(run_cmd, shell=True)

    return current_scenario

################################################################################

def EvaluateMappingSimu(NN, map_at_test, memorysizetab):
    '''Return end to end latency, throughput, power and energy predicted using the SystemC models for the mapping at test.
    This function relies on the phase2.py scripts.'''
    mapping_name = '/dse_mapping.hpp'
    path_to_mapping = PATH_TO_EXPERIMENTS + mapping_name
    mapping_to_return = {}
    mapping_to_return['mapping']=map_at_test

    CreateExperimentHPP(path_to_mapping, NN, map_at_test)
    mapping_to_return['results_P'] = EvaluateSystemCMapping(mapping_name, 'P', memorysizetab)
    mapping_to_return['results_CG'] = EvaluateSystemCMapping(mapping_name, 'CG', memorysizetab)

    return mapping_to_return

################################################################################


def doDSEPhase2(NN, result_json):
    '''This function performs the DSE phase 2 by evaluating mappings using SystemC simulation. It takes as input the results
    from the DSE phase 1 which contains the mapping, and returns the results with the new evaluation predictions'''
    # For all scenarios in result_json
    print('- DSE P2 report:')
    count = 0
    for scenario in result_json:
        mapping_name = 'dse_m' + str(scenario['mapping_index']) + '.hpp'
        path_to_mapping = PATH_TO_EXPERIMENTS + '/' + mapping_name
        # Create hpp file
        CreateExperimentHPP(path_to_mapping, NN, scenario['mapping'])
        # Simulate scenario and get metrics from simulation
        tmp_scenario = EvaluateSystemCMapping(mapping_name, scenario['mode'], scenario["memory"])
        for key in tmp_scenario:
            scenario[key] = tmp_scenario[key]
        print("    - Mapping " + str(count) + "/" + str(len(result_json)) + ": done")
        count += 1
    # Return the result_json with new estimations from SystemC simulation
    return result_json

################################################################################

def __debug_clusterizator_phase2():
    '''Internal function used to test and validate SystemC file generation and simulation'''

    # NN to test, comment the one you don't want
    NN_TO_BE_TESTED = 'MLP2'
    # ~ NN_TO_BE_TESTED = 'CNN'

    pathToOutputFile = './tmp.hpp'
    nn_file = './NN/' + NN_TO_BE_TESTED +'.json'

    with open(nn_file, 'r') as json_file:
        NN = json.load(json_file)

    if NN_TO_BE_TESTED == 'MLP2':
        scenarii = [{'mapping_index':1, 'mapping':[[1, 2, 3],[1, 2, 3],[1, 2, 3],[1]], 'mode': 'CG', 'memory':[64, 64, 64]}]
        # ~ {'mapping_index':2, 'mapping':[[1, 2, 3],[1, 2, 3],[1]], 'mode': 'CG', 'memory':[64, 64, 64]},
        # ~ {'mapping_index':3, 'mapping':[[1],[1],[1]], 'mode': 'CG', 'memory':[256]},
        # ~ {'mapping_index':4, 'mapping':[[1, 2, 3],[1, 2, 3],[1, 2, 3],[1]], 'mode': 'P', 'memory':[64, 64, 64]},
        # ~ {'mapping_index':5, 'mapping':[[1, 2, 3],[1, 2, 3],[1]], 'mode': 'P', 'memory':[64, 64, 64]},
        # ~ {'mapping_index':6, 'mapping':[[1],[1],[1]], 'mode': 'P', 'memory':[256]}]
    else:
        scenarii = [{'mapping_index':1, 'mapping':[[1, 1, 1, 1, 1],[1],[1],[1]], 'mode':'CG'}]

    print(doDSEPhase2(NN, scenarii))

################################################################################

# Debug
# ~ __debug_clusterizator_phase2()


