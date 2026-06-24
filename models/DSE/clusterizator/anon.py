#
# File: anon.py
# Date of creation (dd.mm.yyyy): 07.02.23
# Description: This module contains the ANalytical ONly (ANON) models. They correspond to "best case" models that are faster
#              to execute than the SystemC models but also low in accuracy.
# Author: Quentin Dariol
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

import numpy as np
from clusterizator import phase1 as phase1
from clusterizator import common as common
import copy

################################################################################
################################################################################
################################################################################

# Default polling
t_r=8                      # //read
t_p=8                      # //polling
t_w=5                      # //write
t_rl=14                    # //wait to the next read
t_wl=13                    # //wait to the next write
t_pl=7                     # //wait to the next polling
t_r_loop=22                # //t_r_loop=t_r+t_rl
t_w_loop=18                # //t_w_loop=t_w+t_wl
t_p_loop=15                # //t_p_loop=t_p+t_pl
t_pr_r=15                  # //t_pre_read
t_po_r=11                  # //t_post_read
t_pr_w=15                  # //t_pre_write
t_po_w=9                   # //t_post_write
t_init_r=15                # //t_init_read
t_init_w=16                # //t_init_write

NNisMLP = False

################################################################################

def SwitchPollingInterruptCommDelays(communication_mode):
    global t_p, t_pl, t_p_loop, t_init_r, t_init_w
    if communication_mode == "P": #polling-based communications
        t_p=8
        t_pl=7
        t_p_loop=15
        t_init_r=15
        t_init_w=16
    else: #CG or I: interrupt-based communications
        t_p=0
        t_pl=0
        t_p_loop=0
        t_init_r=15+333
        t_init_w=16+333
    return

################################################################################

def SwitchDenseDelaysMlpCnn(NN):
    global NNisMLP
    NNisMLP = True
    for l in NN:
        if l['layer_type'] != 'd':
            NNisMLP = False
    return

################################################################################

def DelayOffsetRead(numTokens):
    return (t_init_r + t_p + t_pr_r + t_r*numTokens+t_rl*(numTokens-1)+t_po_r+t_w)

################################################################################

def DelayOffsetWrite(numTokens):
    return (t_init_w + t_p + t_pr_r + t_w*numTokens+t_wl*(numTokens-1)+t_po_w+t_w)

################################################################################
################################################################################
################################################################################

#TODO: Update of CNN model

def GetFunctionDelayConv(features, input_size, filter_size):
    delay_coefA=77
    delay_coefB=631.3270408163265   #sig: 42+73+43540 # new relu: 631.3270408163265 # old relu:42+73+109.422
    delay_coefC=28
    delay = delay_coefC + features*input_size*(delay_coefB + filter_size*delay_coefA)
    return delay

################################################################################

def GetFunctionDelayDense(input_size, nb_neuron):
    if(NNisMLP):
        delay_coefA= 47
        delay_coefB= 146
        delay_coefC= 39
    else:
        delay_coefA= 50.00094763#40
        delay_coefB= 105.64417806876287#43540
        delay_coefC= 31.145031640157413#39
    delay = nb_neuron * ((input_size) * delay_coefA + delay_coefB) + delay_coefC
    return delay

################################################################################

def GetFunctionDelayPoll(input_size):
    delay = 100*input_size
    return delay

################################################################################
################################################################################
################################################################################

# Delta (dynamic consumption)
# lambdas
lambda_comp  =  1
lambda_cg    = -1
lambda_sm    =  1.09
lambda_static = 1
p_tile_delta = 0.00011636
p_tile_fix =  0.031
p_static_fix = 0.678
contribution_cg_static = 0.033
p_tile_dynamic = 0.058

################################################################################

def GetStaticPowerConsumption(memorysizetab, communication_mode):
    n_core = len(memorysizetab)
    result = p_static_fix + n_core*p_tile_fix
    for n in range(n_core):
        result += lambda_static*p_tile_delta*memorysizetab[n]
    #TODO: Force it to CG for the validation of the power model on other platforms?
    if (communication_mode == 'CG'):
        result += contribution_cg_static
    return result

################################################################################

def GetPowerConsumption(percent_comp_core, percent_rdwr_core, percent_wait_core, memorysizetab, communication_mode):
    P_total = GetStaticPowerConsumption(memorysizetab, communication_mode)
    n_core = len(percent_comp_core)
    for n in range(n_core):
        P_total += percent_comp_core[n]*lambda_comp*p_tile_dynamic #Power consumption in Computation phase
        P_total += percent_rdwr_core[n]*lambda_sm*p_tile_dynamic #Power consumption in Rd/Wr phase
        if communication_mode == 'P':
            P_total += percent_wait_core[n]*lambda_sm*p_tile_dynamic  #Power consumption in Wait phase - Polling (P)
        else:
            P_total += percent_wait_core[n]*lambda_cg*p_tile_dynamic  #Power consumption in Wait phase - Clock Gating (CG)
    return P_total

################################################################################
################################################################################
################################################################################

def GetMemoryEstimateForMapping(NN, mapping):
    '''Return a table containing memory needs in kb per core for a provided mapping of NN'''
    core_nb = common.GetCoreNumber(mapping)
    mem_tab = [0]*core_nb
    for t in range (core_nb):
        # Step1: For every core, we compute the memory needed
        # .vectors => SW/HW exceptions handling, reset handling, etc.
        mem_tab[t] += 128 #128=x80
        # .text
        mem_tab[t] += 8192 + 512*common.GetActorNumberInMapping(mapping) #8192=x2000 and 512=x200
        # .init, .fini, .ctors, .dtors, .rodata, .sdata2 => Marginal contribution
        # .data => weights + input image
        for l in range(len(NN)):
            # Only convolution and dense have weights
            if (NN[l]['layer_type']=='d') or (NN[l]['layer_type']=='c'):
                cluster = len(mapping[l])
                cluster_size_tab = common.GetClusterSize(NN[l],cluster)
                for c in range(cluster):
                    if mapping[l][c]-1 == t:
                        if NN[l]['layer_type']=='d':
                            # 4x because weights are in float32 format => 4 bytes needed to store each individual weight
                            # +1 for bias
                            mem_tab[t] += 4*(np.prod(NN[l]['token_in'])+1)*cluster_size_tab[c]
                        else: #conv
                            # weight
                            mem_tab[t] += 4*np.prod(NN[l]["filter_dim"])*common.GetClusterSize(NN[l],cluster)[c]
                            # bias
                            mem_tab[t] += 4*np.prod(NN[l]['token_process_in'])*common.GetClusterSize(NN[l],cluster)[c]
        # .sdata, .sbss are marginal. .bss contributes always 0x100 memory = 256
        mem_tab[t] += 256
        # .heap => always x800=2048
        mem_tab[t] += 2048
        # .stack
        #   => tokens (but important to note that we optimize the memory used for tokens by re-using buffers when possible)
        #   => comm. channels. Comm channels are mapped in shared memory, we only store the first address and token_size in
        # local (so 2x4 bytes words)
        # The stack must be minimum 8K to ensure that enough space is available for functions to execute
        tmp_channel_m = 2*4*common.GetChannelNumberInMapping(mapping)
        tmp_token_m = 0
        for l in range(len(NN)):
            if l==0:
                tmp_token_m += 4*np.prod(NN[l]["token_in"])
            tmp_token_m += 4*2*np.prod(NN[l]["token_out"])
        mem_tab[t] += max(8192, tmp_token_m + tmp_channel_m)

        # Step2: We normalize the memory in kilobytes (the power model is based on memory in kilobytes).
        mem_tab[t] = mem_tab[t]/1024
        if mem_tab[t] < 32:
            mem_tab[t] = 32
        elif mem_tab[t] < 64:
            mem_tab[t] = 64
        elif mem_tab[t] < 128:
            mem_tab[t] = 128
        elif mem_tab[t] < 256:
            mem_tab[t] = 256
        elif mem_tab[t] < 512:
            mem_tab[t] = 512
        elif mem_tab[t] < 1024:
            mem_tab[t] = 1024
        elif mem_tab[t] < 2048:
            mem_tab[t] = 2048
        else:
            # Raise error: the memory needed is too big and this is not supported by the modeling flow
            raise ValueError("Private memory needed for tile exceeds maximum size")

    return mem_tab



################################################################################
################################################################################
################################################################################

def EvaluteCostPartitioningExtended(NN, P, l, max_core):
    tmp1 = EvaluateCostPartitioning(NN, P)
    max_cluster = common.GetMaxClusterNumber(NN[l], max_core)
    if (P[l] < max_cluster):
        P2 = copy.deepcopy(P)
        P2[l] = max_cluster
        tmp2 = EvaluateCostPartitioning(NN, P2)
        return min(tmp1, tmp2)
    else:
        return tmp1

################################################################################

def EvaluateCostPartitioning(NN, P, Bool_ConsiderCommunications=False):
    # NN: Neural network at test
    # P : partitioning at test (set of clusters)

    # 21.06.2023: Update => Removal of communication for clustering cost estimation. Let's select all clusterings and let the
    # evaluation of mapping integrate communication workload estimation.
    # 23.07.2023: Update => Communications are back babyyy
    # 15.11.2024: Update => Communications ARE REMOVED AGAIN HAHAAHAHAHAHAHAH
    #             Added an optional argument boolean Bool_ConsiderCommunications. When True, communications are considered.
    for l in range(len(NN)):
        cluster = P[l]
        tmp_comp = 0
        if Bool_ConsiderCommunications:
            tmp_comm = DelayOffsetRead(np.prod(NN[l]['token_in'])) + DelayOffsetWrite(np.prod(NN[l]['token_out']))
        if(NN[l]['layer_type']=='c'):
            if cluster==1:
                tmp_comp = GetFunctionDelayConv(NN[l]['features_nb'], np.prod(NN[l]['token_process_in']) \
                , np.prod(NN[l]['filter_dim']))
            else:
                # Look into the cluster mapping
                if Bool_ConsiderCommunications:
                    tmp_comm = cluster*DelayOffsetRead(np.prod(NN[l]['token_in'])) \
                                + DelayOffsetWrite(np.prod(NN[l]['token_out']))
                cluster_sizes = common.GetClusterSize(NN[l], cluster)
                tmp_comp = GetFunctionDelayConv(max(cluster_sizes), np.prod(NN[l]['token_process_in']),\
                                                np.prod(NN[l]['filter_dim']))

        elif(NN[l]['layer_type']=='d'):
            if cluster==1:
                tmp_comp = GetFunctionDelayDense(np.prod(NN[l]['token_in']), NN[l]['features_nb'])
            else:
                if Bool_ConsiderCommunications:
                    tmp_comm = cluster*DelayOffsetRead(np.prod(NN[l]['token_in'])) \
                    + DelayOffsetWrite(np.prod(NN[l]['token_out']))
                cluster_sizes = common.GetClusterSize(NN[l], cluster)
                tmp_comp = GetFunctionDelayDense(np.prod(NN[l]['token_in']), max(cluster_sizes))

        elif(NN[l]['layer_type']=='p'):
            tmp_comp = GetFunctionDelayPoll(np.prod(NN[l]['token_in']))

        else:
            tmp_comp = NN[l]['delay']

        total = tmp_comp
        if Bool_ConsiderCommunications:
            total+=tmp_comm

    return(total)

################################################################################

def EvaluateMappingManuscript(NN, MAP, mode, memorysizetab):

    # Variable init
    # TODO: Create function to get n_core from the MAP and use it to know how much core are used
    n_core              = len(memorysizetab)
    total_comp_core     = [0]*n_core
    total_rdwr_core     = [0]*n_core
    total_wait_core     = [0]*n_core
    percent_comp_core   = [0]*n_core
    percent_rdwr_core   = [0]*n_core
    percent_wait_core   = [0]*n_core
    total_comp          = 0
    total_comm          = 0

    # Switch the base delays / power consumptions to the right mode and C library (LibFANN for MLPs, CNN_CPP for CNNs)
    SwitchPollingInterruptCommDelays(mode)
    SwitchDenseDelaysMlpCnn(NN)

    # For every layer in the NN
    for l in range(len(NN)):

        # cluster = number of clusters in the mapping for the layer l
        cluster = len(MAP[l])

        # Convolution
        if(NN[l]['layer_type']=='c'):
            if cluster==1:
                total_comp_core[MAP[l][0]-1] += GetFunctionDelayConv(NN[l]['features_nb'], np.prod(NN[l]['token_process_in']), np.prod(NN[l]['filter_dim']))
                total_rdwr_core[MAP[l][0]-1] += DelayOffsetRead(np.prod(NN[l]['token_in'])) + DelayOffsetWrite(np.prod(NN[l]['token_out']))
            else:
                # If the layer is clusterized, we obtain the size of the clusters using the function ca.common.GetClusterSize
                # We then predict the execution time of each cluster with associated comm based on which core executes them
                cluster_sizes = common.GetClusterSize(NN[l], cluster)
                for a in range(cluster):
                    total_comp_core[MAP[l][a]-1] += GetFunctionDelayConv((cluster_sizes[a]), np.prod(NN[l]['token_process_in']), np.prod(NN[l]['filter_dim']))
                    total_rdwr_core[MAP[l][a]-1] += DelayOffsetRead(np.prod(NN[l]['token_in'])) + DelayOffsetWrite(np.prod(NN[l]['token_out']))

        # Dense
        elif(NN[l]['layer_type']=='d'):
            if cluster==1:
                total_comp_core[MAP[l][0]-1] += GetFunctionDelayDense(np.prod(NN[l]['token_in']),NN[l]['features_nb'])
                total_rdwr_core[MAP[l][0]-1] += DelayOffsetRead(np.prod(NN[l]['token_in'])) + DelayOffsetWrite(np.prod(NN[l]['token_out']))
            else:
                cluster_sizes = common.GetClusterSize(NN[l], cluster)
                for a in range(len(MAP[l])):
                    total_comp_core[MAP[l][a]-1] += GetFunctionDelayDense(np.prod(NN[l]['token_in']), cluster_sizes[a])
                    total_rdwr_core[MAP[l][a]-1] += DelayOffsetRead(np.prod(NN[l]['token_in'])) + DelayOffsetWrite(np.prod(NN[l]['token_out']))

        # Pooling
        elif(NN[l]['layer_type']=='p'):
            total_comp_core[MAP[l][0]-1] += GetFunctionDelayPoll(np.prod(NN[l]['token_in']))
            total_rdwr_core[MAP[l][0]-1] += DelayOffsetRead(np.prod(NN[l]['token_in'])) + DelayOffsetWrite(np.prod(NN[l]['token_out']))

        # NOT USED ANYMORE: Layer is something else, in that case the delay is directly provided
        else:
            total_comp_core[MAP[l][0]-1] += NN[l]['delay']
            total_rdwr_core[MAP[l][0]-1] += DelayOffsetRead(np.prod(NN[l]['token_in'])) + DelayOffsetWrite(np.prod(NN[l]['token_out']))

        # Decoder actor
        if (l == len(NN)-1) and (cluster > 1):
            # If the last layer is 'clusterized', a decoder actor is implemented to collect all outputs, which increases
            # the communication time. The decoder actor has marginal computation time.
            total_rdwr_core[MAP[l+1][0]-1] += DelayOffsetRead(np.prod(NN[l]['token_out'])) + DelayOffsetWrite(np.prod(NN[l]['token_out']))


    # E2E and Throughput prediction
    e2e = max(total_comp_core) + max(total_rdwr_core)
    throughput=1/(e2e*(1/common.PROCESSOR_FREQUENCY))

    for t in range(n_core):
        # The time spent waiting predicted by the ANON model is the total exec time minus the comp and rdwr time of the core
        total_wait_core[t] = e2e - total_comp_core[t] - total_rdwr_core[t]
        if total_wait_core[t] == e2e:
            total_wait_core[t] = 0
        # Computing the percentage of time spent in the different phases for each core for power prediction
        percent_comp_core[t] = total_comp_core[t]/e2e
        percent_rdwr_core[t] = total_rdwr_core[t]/e2e
        percent_wait_core[t] = total_wait_core[t]/e2e

    # Power prediction
    power = GetPowerConsumption(percent_comp_core, percent_rdwr_core, percent_wait_core, memorysizetab, mode)

    # Energy prediction
    # Energy is power integrated over time. Since we take the average power (constant), we can do power*time.
    # *1000 to have energy in mJ instead of J
    energy = power*e2e/common.PROCESSOR_FREQUENCY*1000

    return(e2e,throughput,power,energy)

################################################################################
