#
# File: trace_decoder.py
# Description: This script decodes the traces issued by the SystemC models and provides: the average time spent in the
#              different phases (comp, rdwr, wait) by tiles, the power and energy consumption, the E2E latency and throughput.
# Author: Quentin Dariol
#
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

import sys
import copy
import statistics
# ~ import numpy as np
# ~ from sklearn import preprocessing
## ~ import numpy as np

#######################################
#######################################
# MANAGING SCRIPT ARGUMENTS
#######################################
#######################################

# Default values
selected_power_mode = 'P'
net_file = ''
TILE_NB = 7
UseNewPowerModel = True
CONSIDERED_PLATFORM = 1

for i in range (1,len(sys.argv)):
    if (sys.argv[i] == "-h") or (sys.argv[i] == "--help"):
        print ("trace_decoder.py usage:")
        print ("            -f, --file  PATH_TO_TRACE_FILE")
        print ("                Required: Sets the path to the .csv file containing trace simulation results.")
        print ("            -m, --mode  MODE")
        print ("                Optional: Sets power model mode. MODE=P for polling mode (default), MODE=CG for interrupt+clock gating mode")
        print ("            -p, --platform  CONSIDERED_PLATFORM")
        print ("                Optional: Sets the selected platform index between 1 and 5. Default is 1. Platforms differ in tile number and memory sizes.")
        print ("")
        print ("Example: trace_decoder.py -f out.csv -m CG")
        exit()
    if (sys.argv[i] == "-f") or (sys.argv[i] == "-file"):
        try:
            i=i+1
            net_file = sys.argv[i]
        except (IndexError,ValueError) as e:
            print ("Usage: python trace_decoder.py -f PATH_TO_TRACE_FILE")
            print ("Use -h for help")
            exit()
    if (sys.argv[i] == "-m") or (sys.argv[i] == "--mode"):
        try:
            i=i+1
            if (sys.argv[i]=='P') or (sys.argv[i]=='CG'):
                selected_power_mode = sys.argv[i]
            else:
                print("Error: Wrong value for MODE.")
                print("Use -h or --help for help")
                exit()
        except (IndexError,ValueError) as e:
            print ("Usage: python trace_decoder.py -f PATH/TO/TRACE/FILE.csv")
            print ("Use -h or --help for help")
    if (sys.argv[i] == "-p") or (sys.argv[i] == "--platform"):
        try:
            i=i+1
            if (int(sys.argv[i])>=1) and (int(sys.argv[i])<6) and (sys.argv[i].isdigit()):
                CONSIDERED_PLATFORM = int(sys.argv[i])
            else:
                print("Error: Wrong value for CONSIDERED_PLATFORM.")
                print("Use -h or --help for help")
                exit()
        except (IndexError,ValueError) as e:
            print ("Usage: python trace_decoder.py -f PATH/TO/TRACE/FILE.csv")
            print ("Use -h or --help for help")

if (net_file == ''):
    print ("Error: You did not specify the path to the trace file.")
    print ("Usage: python trace_decoder.py -f PATH/TO/TRACE/FILE.csv")
    print ("Use -h or --help for help")
    exit()


#######################################
#######################################
# Extracting info from out.csv file
#######################################
#######################################

# If ITERATION_NB not set by user, get the iteration number directly from the trace.
# Note: User-fixed ITERATION_NB is currently not implemented, can be done manually by setting ITERATION_NB below (uncomment)
ITERATION_NB = 0
with open(net_file) as f:
    for line in f:
        tmp_line = line.replace('\n','').split(',')
        current_iteration = int(tmp_line[0])
        if current_iteration>ITERATION_NB:
            ITERATION_NB = current_iteration
ITERATION_NB = ITERATION_NB+1
# ~ ITERATION_NB = 1

# Initialization of variables
mb_in_scenario = [False for i in range (TILE_NB)] # Will be set True if MicroBlaze is active in the scenario
mb_has_actors  = [False for i in range (TILE_NB)] # Will be set True if MicroBlaze has actors (in some scenarios tiles have 'empty' actors, with only communication channels that take time)
mb_has_rdwrs   = [False for i in range (TILE_NB)]
mb_has_waits   = [False for i in range (TILE_NB)]
emptylist_startstop = [[],[]]
mb_comp_markers_start=[[] for i in range (TILE_NB)]
mb_rdwr_markers_start=[[] for i in range (TILE_NB)]
mb_wait_markers_start=[[] for i in range (TILE_NB)]
mb_comp_markers_stop =[[] for i in range (TILE_NB)]
mb_rdwr_markers_stop =[[] for i in range (TILE_NB)]
mb_wait_markers_stop =[[] for i in range (TILE_NB)]
iteration_markers = []
list_of_events = []
for i in range (ITERATION_NB):
    iteration_markers.append(copy.deepcopy(emptylist_startstop))

# Parse trace generated by simulation
with open(net_file) as f:
    for line in f:
        # Preprocessing and iteration number identification
        tmp_line = line.replace('\n','').split(',')
        current_iteration = int(tmp_line[0])
        if(current_iteration < ITERATION_NB):  #or ((ITERATION_NB==1) and (current_iteration==CONSIDERED_ITERATION)):
            # Iteration start and stop
            if "ITERATION" in line:
                if "START" in line:
                    iteration_markers[current_iteration][0]=int(tmp_line[3])
                if "STOP" in line:
                    iteration_markers[current_iteration][1]=int(tmp_line[3])

            # MicroBlaze activity
            if "MB" in line:
                mb_number = int(tmp_line[1].replace('MB',''))
                mb_in_scenario[mb_number]=True
                tmp = []
                tmp.append(int(tmp_line[4]))
                tmp.append(tmp_line[3])
                list_of_events.append(int(tmp_line[4]))
                if ('POLLING' in line) or ('WAITING' in line):   #Note: 'POLLING' marker is deprecated
                    # ~ mb_wait_markers[current_iteration][mb_number].append(tmp)
                    if "START" in line:
                        mb_wait_markers_start[mb_number].append(int(tmp_line[4]))
                    elif "STOP" in line:
                        mb_wait_markers_stop[mb_number].append(int(tmp_line[4]))
                elif "COMM" in line:
                        # ~ mb_rdwr_markers[current_iteration][mb_number].append(tmp)
                    if "START" in line:
                        mb_rdwr_markers_start[mb_number].append(int(tmp_line[4]))
                    elif "STOP" in line:
                        mb_rdwr_markers_stop[mb_number].append(int(tmp_line[4]))
                else:
                    # ~ mb_comp_markers[current_iteration][mb_number].append(tmp)
                    mb_has_actors[mb_number]=True
                    if "START" in line:
                        mb_comp_markers_start[mb_number].append(int(tmp_line[4]))
                    if "STOP" in line:
                        mb_comp_markers_stop[mb_number].append(int(tmp_line[4]))


# INSTANT WAITING COMPLETION FIX:
#   Sometimes the START and STOP time are equal for WAITING activity (the token is available and the tile skips the WAITING
#   to proceed directly with the COMM). This must be patched before the trace evaluation.
waiting_entries_to_delete = []
for n in range (TILE_NB):
    if mb_in_scenario[n]:
        for i in range (len(mb_wait_markers_start[n])):
            if mb_wait_markers_start[n][i] == mb_wait_markers_stop[n][i]:
                waiting_entries_to_delete.append((n,i))
for element in reversed(waiting_entries_to_delete):
    mb_wait_markers_start[element[0]].pop(element[1])
    mb_wait_markers_stop[element[0]].pop(element[1])

# Same with RDWR
#   Read and Write delays can be equal to 0 when using ANALYTICAL MODEL ONLY - ANON mode (which sets COMM time to 0).
rdwr_entries_to_delete = []
for n in range (TILE_NB):
    if mb_in_scenario[n]:
        for i in range (len(mb_rdwr_markers_start[n])):
            if mb_rdwr_markers_start[n][i] == mb_rdwr_markers_stop[n][i]:
                rdwr_entries_to_delete.append((n,i))
for element in reversed(rdwr_entries_to_delete):
    mb_rdwr_markers_start[element[0]].pop(element[1])
    mb_rdwr_markers_stop[element[0]].pop(element[1])

# CHECK IF MICROBLAZES ACTUALLY HAVE WAITS AND COMMS (AFTER REMOVAL OF DELAYS = 0)
for n in range (TILE_NB):
    if mb_in_scenario[n]:
        if (len(mb_rdwr_markers_start[n]) != 0):
            mb_has_rdwrs[n] = True
        if (len(mb_wait_markers_start[n]) != 0):
            mb_has_waits[n] = True

### Sort all event markers
list_of_events=sorted(list_of_events)
### Remove redundant markers
list_of_events = list(dict.fromkeys(list_of_events))



#######################################
#######################################
# EXECUTION TIME, E2E LATENCY AND THROUGHPUT
#######################################
#######################################

# Info for user
print (" ")
print ("Note: All presented durations are in processor cycles (clock frequency = 100 MHz), power consumptions in W, energy in mJ. Computation, RdWr and waiting rates are in %\n")
print ("Number of iterations in trace: ", ITERATION_NB)


# Execution time, end to end latency and throughput
execution_time = []
e2e_latency = []
total_execution_time = iteration_markers[ITERATION_NB-1][1]
for i in range (ITERATION_NB):
    execution_time.append(iteration_markers[i][1]-iteration_markers[i][0])
    if (i>0):
        e2e_latency.append(iteration_markers[i][1]-iteration_markers[i-1][1])

avg_execution_time = statistics.mean(execution_time)

print ("Average execution time: ", avg_execution_time)
if (ITERATION_NB > 1):
    avg_e2e_latency = statistics.mean(e2e_latency)
    print ("Average end to end latency: ", avg_e2e_latency)
    PROCESSOR_FREQUENCY = 100000000 #100MHz in Hz
    # Throughput is defined as number of outputs per second
    # Throughput = 1s / ((E2E in processor cycles)*(Period of the processor clock))
    avg_throughput=1/(avg_e2e_latency*(1/PROCESSOR_FREQUENCY))
    print ("Average throughput: ", avg_throughput)



#######################################
#######################################
# UTILIZATION RATES OF TILES
#######################################
#######################################

mb_total_wait_time = [0. for k in range (TILE_NB)]
mb_total_rdwr_time = [0. for k in range (TILE_NB)]
mb_total_comp_time = [0. for k in range (TILE_NB)]
avg_comp = 0
avg_rdwr = 0
avg_wait = 0

TILE_NB_USED = 0
for mb_number in range (TILE_NB):
    if mb_in_scenario[mb_number]:
        TILE_NB_USED += 1

# For every MicroBlaze present in scenario, we compute the total computation, read/write and wait time
for n in range (TILE_NB):
    if mb_in_scenario[n]:
        for j in range (len(mb_comp_markers_start[n])):
            mb_total_comp_time[n] += mb_comp_markers_stop[n][j]-mb_comp_markers_start[n][j]
        for j in range (len((mb_rdwr_markers_start[n]))):
            mb_total_rdwr_time[n] += mb_rdwr_markers_stop[n][j]-mb_rdwr_markers_start[n][j]
        for j in range (len((mb_wait_markers_start[n]))):
            mb_total_wait_time[n] += mb_wait_markers_stop[n][j]-mb_wait_markers_start[n][j]

for n in range (TILE_NB):
    if mb_in_scenario[n]:
        # We obtain the comp., rdwr and wait rates per tiles.
        mb_total_comp_time[n] = mb_total_comp_time[n]/total_execution_time
        mb_total_wait_time[n] = mb_total_wait_time[n]/total_execution_time
        mb_total_rdwr_time[n] = mb_total_rdwr_time[n]/total_execution_time
        # Normalize for all tiles (some tiles finish before the simulation end which results to utilization < 100%)
        if (mb_total_comp_time[n] + mb_total_wait_time[n] + mb_total_rdwr_time[n] < 1):
            tmp_array1 = [mb_total_comp_time[n], mb_total_rdwr_time[n], mb_total_wait_time[n]]
            tmp_array2 = [mb_total_comp_time[n], mb_total_rdwr_time[n], mb_total_wait_time[n]]
            for element in tmp_array2:
                element = (element - min(tmp_array1)) / (max(tmp_array1) - min(tmp_array1))
            mb_total_comp_time[n] = tmp_array2[0]
            mb_total_rdwr_time[n] = tmp_array2[1]
            mb_total_wait_time[n] = tmp_array2[2]
        # Compute average rates in regards to all tiles in scenario.
        avg_comp += mb_total_comp_time[n]
        avg_rdwr += mb_total_rdwr_time[n]
        avg_wait += mb_total_wait_time[n]

if TILE_NB_USED > 0:
    avg_comp = avg_comp/TILE_NB_USED*100
    avg_rdwr = avg_rdwr/TILE_NB_USED*100
    avg_wait = avg_wait/TILE_NB_USED*100

    print("Average computation rate per tile: " + str(avg_comp))
    print("Average RdWr transaction rate per tile: " + str(avg_rdwr))
    print("Average waiting (for tokens) rate per tile: " + str(avg_wait))
    print("Average communication rate (waiting+RdWr) per tile: " + str(avg_rdwr+avg_wait))



#######################################
#######################################
# POWER ESTIMATION
#######################################
#######################################

## Generate list of MB power states

### State X  = MicroBlaze OFF, not used in this application
### State A  = MicroBlaze computing actor
### State C  = MicroBlaze in communications (RDWR)
### State P  = MicroBlaze in polling

### By default all OFF at all events
list_of_mb_power_states = [['X' for i in range (TILE_NB)] for event in list_of_events]

ct_w = [0 for i in range (TILE_NB)]
ct_c = [0 for i in range (TILE_NB)]
ct_a = [0 for i in range (TILE_NB)]

found = False

for n in range (TILE_NB):
    if (mb_in_scenario[n]):
        for i in range (len(list_of_events)):
            # WAITING
            # If the marker in list of event matches the marker in mb_wait_marker, the MB is currently in wait mode.
            if (mb_has_waits[n]):
                # ~ print(n, ct_w[n])
                if (list_of_events[i] == mb_wait_markers_start[n][ct_w[n]]):
                    list_of_mb_power_states[i][n] = 'P'
                    found = True
                elif (list_of_events[i] > mb_wait_markers_start[n][ct_w[n]]):
                    while (ct_w[n] < len(mb_wait_markers_start[n])-1) \
                    and (list_of_events[i] > mb_wait_markers_start[n][ct_w[n]]):
                        ct_w[n] += 1
            # RDWR
            if (mb_has_rdwrs[n]):
                if ((list_of_events[i] == mb_rdwr_markers_start[n][ct_c[n]])):
                    list_of_mb_power_states[i][n] = 'C'
                    found = True
                elif (list_of_events[i] > mb_rdwr_markers_start[n][ct_c[n]]):
                    while (ct_c[n] < len(mb_rdwr_markers_start[n])-1) \
                    and (list_of_events[i] > mb_rdwr_markers_start[n][ct_c[n]]):
                        if (ct_c[n] < (len(mb_rdwr_markers_start[n])-1)):
                            ct_c[n] += 1
            # ACTOR
            if (mb_has_actors[n]):
                if ((list_of_events[i] == mb_comp_markers_start[n][ct_a[n]])):
                    list_of_mb_power_states[i][n] = 'A'
                    found = True
                elif (list_of_events[i] > mb_comp_markers_start[n][ct_a[n]]):
                    while (ct_a[n] < len(mb_comp_markers_start[n])-1) \
                    and (list_of_events[i] > mb_comp_markers_start[n][ct_a[n]]):
                        if (ct_a[n] < (len(mb_comp_markers_start[n])-1)):
                            ct_a[n] += 1
            # NOT FOUND
            if (not(found)) and (i>0):
                # If the tile has actually finished its workload for the specified number of iterations, go back to 'X'
                if  (ct_w[n] == len(mb_wait_markers_start[n])-1) \
                and (ct_c[n] == len(mb_rdwr_markers_start[n])-1) \
                and (ct_a[n] == len(mb_comp_markers_start[n])-1):
                    list_of_mb_power_states[i][n] = 'X'
                # Else it means that it didn't change state at this event
                else:
                    list_of_mb_power_states[i][n] = list_of_mb_power_states[i-1][n]
            found = False

########################################
########################################
# OLD POWER MODEL (WORKING)
########################################
########################################

if not(UseNewPowerModel):
    # Interrupt-based + Clock gating
    if (selected_power_mode=='CG'):
        print("Clock gating power model used.")
        list_of_power = [1.26 for event in list_of_events]
        for j in range (len(list_of_events)):
            bram_currently_used = False
            for mb in range (0,7):
                if list_of_mb_power_states[j][mb] == 'A':
                    list_of_power[j] += 0.058
                elif list_of_mb_power_states[j][mb] == 'C':
                    if not(bram_currently_used):
                        bram_currently_used = True
                        list_of_power[j] += 0.063
                elif list_of_mb_power_states[j][mb] == 'P':
                    list_of_power[j] += -0.058
    else: # Polling mode
        print("Polling power model used.")
        list_of_power = [1.227 for event in list_of_events]
        for j in range (len(list_of_events)):
            bram_currently_used = False
            for mb in range (0,7):
                if list_of_mb_power_states[j][mb] == 'A':
                    list_of_power[j] += 0.058
                elif list_of_mb_power_states[j][mb] == ('C' or 'P'):
                    if not(bram_currently_used):
                        bram_currently_used = True
                        list_of_power[j] += 0.063
    ## Processing total power consumption
    total_power = 0.
    for j in range (len(list_of_events)-1):
        total_power += list_of_power[j]*(list_of_events[j+1]-list_of_events[j])
    if total_execution_time > 0:
        total_power = total_power / total_execution_time
        total_energy = total_power*(avg_execution_time*(1/PROCESSOR_FREQUENCY))*1000 #*1000 to show in mJ instead of J
        print ("Total predicted power consumption:", total_power)
        print ("Total predicted energy consumption:", total_energy)
    else:
        print ("Total predicted power consumption:", total_power)


########################################
########################################
# REFINED POWER MODEL (NEW, STILL WIP)
########################################
########################################

if UseNewPowerModel:
    PLATFORMS_TO_CONSIDER = []
    # If no event in the list: this means that the user wants to test the platform without activity.
    # We return the static power consumption of all considered platforms.
    if len(list_of_events) == 0:
        PLATFORMS_TO_CONSIDER = [1, "2a", "2b", "2c", 3, 4, 5]
    elif (CONSIDERED_PLATFORM == 2): #If platform 2 (aka singlecore) we have to repeat for the different memory sizes of PTF2
        PLATFORMS_TO_CONSIDER = ["2a", "2b", "2c"]
    else:
        PLATFORMS_TO_CONSIDER.append(CONSIDERED_PLATFORM)

    # Delta (dynamic consumption)
    # lambdas
    lambda_comp  =  1 # 1.953125  # 1.367 ; 1.940
    lambda_cg    = -1 # -1.953125   #-1.367 ; -1.940
    lambda_sm    =  1.09 # 2.121497844827586  # 1.485 ; 2.121
    lambda_static = 1 # 1.57596982
    # ptile
    p_tile_delta = 0.00011636
    # Commented because all other versions of the platform use the interrupt-based platform no matter what.
    # ~ p_tile_fix_pol = 0.031
    p_tile_fix =  0.031 #0.036
    # ~ p_tile_fix_cg = 0.1 #0.036
    # Fixed (static consumption)
    p_static_fix = 0.678 #1.010
    contribution_cg_static = 0.033

    memorysizetab = {
    1:[1024, 256, 256, 256, 256, 256, 256], #PTF1: the main platform version and also the default one
    3:[64, 64, 64],
    4:[512, 256, 256, 128, 128],
    5:[64, 64],
    "2a":[2048],
    "2b":[1024],
    "2c":[512]
    }

    def GetStaticConsumption(n_core, mode, platform):
        result = p_static_fix + n_core*p_tile_fix
        for n in range(n_core):
            result += lambda_static*p_tile_delta*memorysizetab[platform][n]
        if (platform != 1) or (mode == 'CG'):
            result += contribution_cg_static
        return result

    def GetTileConsumption(memory):
        # ~ return p_tile_delta*memory
        # Not working, so here's another proposition. Use without the lambdas. Just use -1* if clock gating.
        # ~ return 3.26e-05*memory + 0.0497
        return 0.058 #0.058

    for platform in PLATFORMS_TO_CONSIDER:
        print("Considered platform: " + str(platform) + " | Tile number in platform: " + str(len(memorysizetab[platform])) + " | Memory sizes: " + str(memorysizetab[platform]))
        # Interrupt-based + Clock gating
        if (selected_power_mode=='CG'):
            print("Clock gating power model used.")
            list_of_power = [GetStaticConsumption(len(memorysizetab[platform]), 'CG', platform) for event in list_of_events]
            for j in range (len(list_of_events)):
                sharedmem_power = 0
                mbnb_accessing_sharedmem = 0
                for mb in range (0,7):
                    if list_of_mb_power_states[j][mb] == 'A':
                        list_of_power[j] += lambda_comp*GetTileConsumption(memorysizetab[platform][mb])
                    elif list_of_mb_power_states[j][mb] == 'C':
                        mbnb_accessing_sharedmem += 1
                        sharedmem_power += lambda_sm*GetTileConsumption(memorysizetab[platform][mb])
                    elif list_of_mb_power_states[j][mb] == 'P':
                        list_of_power[j] += lambda_cg*GetTileConsumption(memorysizetab[platform][mb])
                # If shared mem is currently accessed, add average power consumption of MB accessing the memory
                if mbnb_accessing_sharedmem != 0:
                    list_of_power[j] += sharedmem_power/mbnb_accessing_sharedmem

        else: # Polling mode
            print("Polling power model used.")
            list_of_power = [GetStaticConsumption(len(memorysizetab[platform]), 'P', platform) for event in list_of_events]
            for j in range (len(list_of_events)):
                sharedmem_power = 0
                mbnb_accessing_sharedmem = 0
                for mb in range (0,7):
                    if list_of_mb_power_states[j][mb] == 'A':
                        list_of_power[j] += GetTileConsumption(memorysizetab[platform][mb])
                    elif list_of_mb_power_states[j][mb] == ('C' or 'P'):
                        mbnb_accessing_sharedmem += 1
                        sharedmem_power += GetTileConsumption(memorysizetab[platform][mb])
                if mbnb_accessing_sharedmem != 0:
                    list_of_power[j] += sharedmem_power/mbnb_accessing_sharedmem

        ## Processing total power consumption
        total_power = 0.
        for j in range (len(list_of_events)-1):
            total_power += list_of_power[j]*(list_of_events[j+1]-list_of_events[j])
        # If no event: the user wants to check the static consumption. Return the static consumption.
        if len(list_of_events) == 0:
            total_power = GetStaticConsumption(len(memorysizetab[platform]), selected_power_mode, platform)


        if total_execution_time > 0:
            total_power = total_power / total_execution_time
            total_energy = total_power*(avg_execution_time*(1/PROCESSOR_FREQUENCY))*1000 #*1000 to show in mJ instead of J
            print ("Total predicted power consumption - platform " + str(platform) +" : " + str(total_power))
            print ("Total predicted energy consumption - platform " + str(platform) +" : " + str(total_energy))
        else:
            print ("Total predicted power consumption - platform " + str(platform) +" : " + str(total_power))
