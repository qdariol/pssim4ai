#
# File: phase1.py
# Date of creation (dd.mm.yyyy): 28.02.2023
# Description: This file contains functions to generate a NN clustering/mapping. The generation is optimized through the use
#              of a Branch and Bound algorithm (often refered to as BB in the code).
# Author: Quentin Dariol
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

import copy
import numpy as np
import operator
import json
from timeit import default_timer as timer
import time, threading

# From clusterizator module
from clusterizator import common
from clusterizator import anon
from clusterizator import phase2

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

################################################################################

def GetClusterizableDict(NN, max_core_nb):
    '''Return a dictionnary containing all clusterizable layers of NN accessible through their index in NN, and with their
    maximum number of clusters'''
    C = {}
    index_list = []
    for l in range(len(NN)):
        if ((NN[l]['layer_type']=='d') or (NN[l]['layer_type']=='c')): #If layer is clusterizable
            C[l]=common.GetMaxClusterNumber(NN[l], max_core_nb)
            index_list.append(l)
    C['index_list']=index_list
    return C

def GenerateFirstMapping(NN, clustering, platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET):
    ''' Return the first mapping from a provided clustering'''
    mapping = {'mapping':[],'memory':[], 'parent_mapping_id':None, 'bool_isParent':False,
               'bool_isFirstMapping':True, 'bool_isNaiveMapping':False}
    for c in range(len(clustering)):
        mapping['mapping'].append([1 for i in range(clustering[c])])
        # If the last layer is clusterized, we need to add the decoder actor
        if (c == len(clustering)-1) and (clustering[c] > 1):
            mapping['mapping'].append([1])
    # Get memory estimate for mapping
    if platformIsFixed:
        mapping['memory'] = memorysizetab
    else:
        mapping['memory'] = anon.GetMemoryEstimateForMapping(NN, mapping['mapping'])
    return {**phase2.EvaluateMappingSimu(NN, mapping['mapping'], mapping['memory']),**mapping}

def GenerateNaiveMapping(NN, clustering, platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET):
    ''' Return the naive mapping implementation from a provided clustering'''
    mapping = {'mapping':[],'memory':[], 'parent_mapping_id':None, 'bool_isParent':False,
               'bool_isFirstMapping':False, 'bool_isNaiveMapping':True}
    for c in range(len(clustering)):
        mapping['mapping'].append([i+1 for i in range(clustering[c])])
        # If the last layer is clusterized, we need to add the decoder actor
        if (c == len(clustering)-1) and (clustering[c] > 1):
            mapping['mapping'].append([1])
    # Get memory estimate for mapping
    if platformIsFixed:
        mapping['memory'] = memorysizetab
    else:
        mapping['memory'] = anon.GetMemoryEstimateForMapping(NN, mapping['mapping'])
    return {**phase2.EvaluateMappingSimu(NN, mapping['mapping'], mapping['memory']),**mapping}

################################################################################
# BRANCH AND BOUND CLUSTERING SEARCH
################################################################################

def GetNextClusteringBB(NN, partition, max_core_nb):
    '''Return the next partitioning based on a provided partitioning, by increasing the clustering number of the lattest
    layer of NN'''
    selected_partition = {}
    selected_partition['partition'] = copy.deepcopy(partition)
    selected_partition['perks'] = 1.7976931348623157e+308
    partition_at_test = copy.deepcopy(selected_partition)
    clusterizable_dict = GetClusterizableDict(NN, max_core_nb)
    #Generate each branch partitioning
    for l in range(len(NN)):
        #If layer is clusterizable (i.e. its index is in clusterizable_dict)
        if (l in clusterizable_dict):
            #If the clustering is lower than the maximum clustering, increase it and evaluate to see if it beats the
            #current best
            if (partition_at_test['partition'][l] < clusterizable_dict[l]):
                partition_at_test['partition'][l] += 1

                partition_at_test['perks'] = \
                anon.EvaluteCostPartitioningExtended(NN, partition_at_test['partition'], l, max_core_nb)

                if (partition_at_test['perks'] < selected_partition['perks']):
                    selected_partition['partition'] = copy.deepcopy(partition_at_test['partition'])
                    selected_partition['perks'] = copy.deepcopy(partition_at_test['perks'])

                partition_at_test['partition'][l] -= 1

    # If the best partition is the same as the input, it means that there are no better partitions
    if (selected_partition['partition'] == partition):
        return None
    else:
        return selected_partition['partition']

def GenerateClusteringsBB(NN, max_core_nb):
    '''Generate all interesting clusterings using the Branch & Bound algorithm and a simple cost function (only latency)'''
    Clusterings = []
    clustering = [1 for i in range(len(NN))]
    # While the last partition has not been reached (None), then get all the Clusterings
    while(clustering != None):
        Clusterings.append(clustering)
        clustering = GetNextClusteringBB(NN, clustering, max_core_nb)
    # Revert the order of the Clusterings table before returning
    # This way most elaborated clusterings (i.e. those obtained at the end of the exploration) come first during mapping
    # exploration
    return Clusterings[::-1]


################################################################################
# Branch & Bound mapping generation with evaluation using SystemC
################################################################################

def GetNextMappingBBSimu(NN, mapping, mapping_id, max_core, platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET,\
    Branches_mappings=[]):
    '''Return the next mapping based on a provided mapping,
    by evaluating possibilities and choosing the best with BB algorithm'''
    Branches = []

    for l in range(len(NN)):
        # Mapping upgrade #1: Cluster upgrade - For each layer, check if all clusters (actors) are mapped on diff. cores.
        # Example: Cluster_start = [1, 1, 1, 1, 1] => Cluster_final = [1, 2, 3, 4, 5]
        for a in range(len(mapping['mapping'][l])):
            if (mapping['mapping'][l][a]<a+1):
                new_map={}
                new_map['mapping']=copy.deepcopy(mapping['mapping'])
                new_map['mapping'][l][a]+=1
                if any(new_map['mapping']==old_map for old_map in Branches_mappings):
                    continue # Avoid redundancy, if the mapping is already in the list of mappings, ignore it.
                Branches_mappings.append(new_map['mapping'])
                new_map['parent_mapping_id']=mapping_id
                new_map['bool_isParent']=False
                new_map['bool_isFirstMapping']=False
                new_map['bool_isNaiveMapping']=False
                new_map['memory'] = anon.GetMemoryEstimateForMapping(NN, new_map['mapping'])
                Branches.append({**phase2.EvaluateMappingSimu(NN, new_map['mapping'], new_map['memory']),**new_map})

        # Mapping upgrade #2: Layer upgrade - Check if all layers are mapped onto different cores
        # Example: Mapping_start = [[1], [1,1], [1], [1]] => Mapping_final = [[1], [2, 2], [3], [4]]
        if (mapping['mapping'][l][0]<l+1):
            if(mapping['mapping'][l][len(mapping['mapping'][l])-1] < max_core):
                new_map={}
                new_map['mapping']=copy.deepcopy(mapping['mapping'])
                for a in range(len(mapping['mapping'][l])):
                    new_map['mapping'][l][a]+=1
                if any(new_map['mapping']==old_map for old_map in Branches_mappings):
                    continue # Avoid redundancy, if the mapping is already in the list of mappings, ignore it.
                Branches_mappings.append(new_map['mapping'])
                new_map['parent_mapping_id']=mapping_id
                new_map['bool_isParent']=False
                new_map['bool_isFirstMapping']=False
                new_map['bool_isNaiveMapping']=False
                new_map['memory'] = anon.GetMemoryEstimateForMapping(NN, new_map['mapping'])
                Branches.append({**phase2.EvaluateMappingSimu(NN, new_map['mapping'], new_map['memory']),**new_map})

    return Branches


def GetMappingsBBSimu(NN, user_def_maxcore, bool_PlatformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET,
    Mappings=[], ExplorationTimeLimit=300, clustering=[],
    bool_PeriodicSaves=False, PeriodicSavesTimer=180, PeriodSavesOutputFile='dse_tmp.json',
    bool_doMultipleClusteringsMode=False):
    '''Generate mappings for a given partition using BB with the maximum core number being fixed by the user. Arguments:
          - NN                      -> Neural network specs loaded from file

          - user_def_maxcore        -> Maximum number of cores in the platform. Must be defined by the user.

          - bool_PlatformIsFixed    -> (Optional) Boolean. Is the platform fixed during exploration or should the platform be
                                    dimensioned as the same time as the mapping are explored? Default is False.

          - memorysizetab           -> (Optional) When bool_PlatformIsFixed = True, please specify the platform specifications.
                                    Default is defined as global variable common.DEFAULT_MEMORY_SET.

          - Mappings                -> (Optional) If resuming from a previous run, provide in this argument the table with
                                    previous mappings. Default value: []

          - ExplorationTimeLimit    -> (Optional) Time limit spent in exploration, over this time, function is exited.
                                    In seconds. Default: 300.

          - clustering              -> (Optional) If Mappings=[], then a clustering of NN must be provided, to generate the
                                    first mapping from this clustering. Default value: []

          - bool_PeriodicSaves      -> (Optional) Activates periodic saving of the mappings in a JSON file. Default: False.

          - PeriodicSavesTimer      -> (Optional) Specifies how often saves in JSON file are done when bool_PeriodicSaves=True.
                                    In seconds. Default: 180.

          - PeriodSavesOutputFile   -> (Optional) Specifies path to the JSON file used for saves when bool_PeriodicSaves=True.
                                    Default: 'dse_tmp.json'

          - bool_doMultipleClusteringsMode -> (Optional) This mode lets the user use a table of table of mappings in the
                                    Mappings variable, instead of a simple table of mappings. This allows to have a different
                                    table for each clustering, and explore more elements of various complexity.
                                    Default: False
    '''
    # A mapping must be a list (layer) of lists (actors issued from clustering),
    # with the associated core on which the actor is mapped: mapping = [[1], [1,1], ... ]
    actor_nb = common.GetActorNumberInPartition(clustering)
    max_core = min(user_def_maxcore, actor_nb)
    Mapping_maps = []

    # If no mapping yet (no previous run)
    # Generate the first mapping and naive mapping
    if Mappings==[]:
        if clustering==[]:
            raise ValueError('Empty mapping and clustering inputs in GetMappingsBBSimu. Cannot proceed with the exploration.')
        else:
            Mappings.append(GenerateNaiveMapping(NN, clustering, bool_PlatformIsFixed, memorysizetab))
            Mappings.append(GenerateFirstMapping(NN, clustering, bool_PlatformIsFixed, memorysizetab))
            Mapping_maps.append(Mappings[0]['mapping'])
            Mapping_maps.append(Mappings[1]['mapping'])

    # Perform the mapping search using Branch and bound algorithm
    start = timer()
    end = timer()
    while(end - start < ExplorationTimeLimit):

        # If saves are enabled and time between saves is elapsed: do a new save.
        if(bool_PeriodicSaves) and (end - start > PeriodicSavesTimer):
            with open(PeriodSavesOutputFile, 'w') as fout:
                json.dump(Mappings, fout, sort_keys=True, indent=4, cls=common.NpEncoder)
            if bool_doMultipleClusteringsMode:
                mapping_number=0
                for i in range(len(Mappings)):
                    mapping_number+=len(Mappings[i])
            else:
                mapping_number=len(Mappings)

            print("Periodic save done at: " + str(int(end - start)) + "s. " + str(mapping_number) + " mappings saved.")
            PeriodicSavesTimer+=PeriodicSavesTimer

        # Determine the currently best mapping, from which we can then develop next branches.
        best_score = float("inf")
        best_id = 1
        if bool_doMultipleClusteringsMode:
            best_id_clustering = 0
            # This mode allows working with a table of Mappings, each Mappings[i] table is a list of Mappings generated from
            # the same clustering. But Mappings[i] and Mappings[i+1] correspond to different clusterings.
            for i in range(len(Mappings)):
                for j in range(len(Mappings[i])):
                    if not(Mappings[i][j]['bool_isNaiveMapping']) and not(Mappings[i][j]['bool_isParent']):
                        if (Mappings[i][j]['results_P']['p_energy'] < best_score):
                            best_score = Mappings[i][j]['results_P']['p_energy']
                            best_id_clustering = i
                            best_id = j
                        if (Mappings[i][j]['results_CG']['p_energy'] < best_score):
                            best_score = Mappings[i][j]['results_CG']['p_energy']
                            best_id_clustering = i
                            best_id = j
            # If after checking all Mappings, the best id is still 1 and Mapping 1 was already used to generate Branches, it's over
            if (best_id_clustering==0) and (best_id==1) and (Mappings[best_id_clustering][best_id]['bool_isParent']):
                print("GetMappingsBBSimu: Exploration terminated - no new branches can be generated. Time: " + \
                      str(int(end - start)) + "s.")
                break
            else:
                # Generate the new branches from the current best mapping
                Mappings[best_id_clustering][best_id]['bool_isParent']=True
                Mappings_tmp = GetNextMappingBBSimu(NN, Mappings[best_id_clustering][best_id], best_id, max_core, \
                bool_PlatformIsFixed, memorysizetab, Mapping_maps)
                for i in range(len(Mappings_tmp)):
                    Mappings[best_id_clustering].append(Mappings_tmp[i])
                end = timer()
        else:
            for i in range(len(Mappings)):
                if not(Mappings[i]['bool_isNaiveMapping']) and not(Mappings[i]['bool_isParent']):
                    if (Mappings[i]['results_P']['p_energy'] < best_score):
                        best_score = Mappings[i]['results_P']['p_energy']
                        best_id = i
                    if (Mappings[i]['results_CG']['p_energy'] < best_score):
                        best_score = Mappings[i]['results_CG']['p_energy']
                        best_id = i
            # If after checking all Mappings, the best id is still 1 and Mapping 1 was already used to generate Branches, it's over
            if (best_id==1) and (Mappings[best_id]['bool_isParent']):
                print("GetMappingsBBSimu: Exploration terminated - no new branches can be generated. Time: " + \
                      str(int(end - start)) + "s.")
                break
            else:
                # Generate the new branches from the current best mapping
                Mappings[best_id]['bool_isParent']=True
                Mappings_tmp = GetNextMappingBBSimu(NN, Mappings[best_id], best_id, max_core, bool_PlatformIsFixed, memorysizetab,\
                Mapping_maps)
                for i in range(len(Mappings_tmp)):
                    Mappings.append(Mappings_tmp[i])
                end = timer()
    return Mappings

################################################################################
################################################################################
################################################################################
################################################################################
#
# Starting from here, deprecated functions!!!
#
################################################################################
################################################################################
################################################################################
################################################################################
# "NAIVE" EXHAUSTIVE GENERATION - NO SCORE EVALUATION SYSTEM
################################################################################
################################################################################
################################################################################

def GetNextClustering(NN, clustering, clusterizable_dict):
    '''Return the next clustering based on a provided clustering, by increasing the clustering number of the lattest
    layer of NN'''
    new_clustering = copy.deepcopy(clustering)
    #Layers are parsed in reverse to handle first the lattest layers
    for l in range(len(NN)-1, -1, -1):
        #If layer is clusterizable (i.e. its index is in clusterizable_dict)
        if (l in clusterizable_dict):
            #If the clustering is lower than the maximum clustering, increase it and return the clustering as is
            if (new_clustering[l] < clusterizable_dict[l]):
                new_clustering[l]+=1
                return new_clustering
            #If the clustering has reached the maximum value, then...
            else:
                #If this is the last clusterizable layer,
                #then it means that all the clusterings have been already obtained, so return None.
                if(l == min(clusterizable_dict['index_list'])):
                    return None
                #If this is not the last layer, then reset the value to 1 and continue the loop
                else:
                    new_clustering[l]=1
    return new_clustering


def GenerateAllClusterings(NN, max_core_nb):
    '''Generate all possible clusterings of a given NN, with the maximum layer clustering being fixed by the user defined
    maximum number of cores in the circuit'''
    Clusterings = []
    clustering = [1 for i in range(len(NN))]
    C = GetClusterizableDict(NN, max_core_nb)
    # While the last clustering has not been reached (None), then get all the Clusterings
    while(clustering != None):
        Clusterings.append(clustering)
        clustering = GetNextClustering(NN, clustering, C)
    return Clusterings


def GetNextMapping(mapping, max_core):
    '''Return the next mapping based on a provided mapping,
    by increasing the tile number of the lattest actor of NN'''
    new_map = copy.deepcopy(mapping)
    actor_number = common.GetActorNumberInMapping(mapping)
    #Actors are parsed in reverse
    for l in range(len(new_map)-1, -1, -1):
        for a in range(len(new_map[l])-1, -1, -1):
            if (new_map[l][a] < min(max_core, actor_number)):
                new_map[l][a]+=1
                return new_map
            #If the clustering has reached the maximum value, then...
            else:
                #If this is the first actor
                #then it means that all the mappings have been already obtained, so return None.
                if (l==0) and (a==0):
                    return None
                #If this is not the last actor, then reset the value to 1 and continue the loop
                else:
                    new_map[l][a]=1
                    actor_number = actor_number-1
    return new_map

def GenerateAllMappings(NN, partition, user_def_maxcore):
    '''Generate all possible mappings for a given partition, with the maximum core number being fixed by the user'''
    Mappings = []
    actor_nb = common.GetActorNumberInPartition(partition)
    max_core = min(user_def_maxcore, actor_nb)
    # Generate first mapping
    selected_map = {}
    selected_map['mapping'] = []
    for c in range(len(partition)):
        selected_map['mapping'].append([1 for i in range(partition[c])])
        # If the last layer is clusterized, we need to add the decoder actor
        if (c == len(partition)-1) and (partition[c] > 1):
            selected_map['mapping'].append([1])
    # Until the last mapping is reached
    while(selected_map['mapping']!=None):
        # Evaluate mapping memory size
        selected_map['memory'] = anon.GetMemoryEstimateForMapping(NN, selected_map['mapping'])
        # For both polling and clock gating
        for mode in ['P', 'CG']:
            # Evaluate mapping memory size and metrics
            selected_map['mode'] = mode
            selected_map['anon_latency'], selected_map['anon_throughput'],\
            selected_map['anon_power'], selected_map['anon_energy'] = \
            anon.EvaluateMappingManuscript(NN, selected_map['mapping'], mode, selected_map['memory'])
            # Append mapping
            Mappings.append(copy.deepcopy(selected_map))
        # Generate next mapping
        selected_map['mapping'] = GetNextMapping(selected_map['mapping'], max_core)

    return Mappings


def GetNextMappingBB(NN, mapping, max_core, mode, platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET):
    '''Return the next mapping based on a provided mapping,
    by evaluating possibilities and choosing the best with BB algorithm'''

    common.GetActorNumberInMapping(mapping)
    selected_map = copy.deepcopy(mapping)
    map_at_test = copy.deepcopy(mapping['mapping'])
    count_previous_actors = 0
    C = GetClusterizableDict(NN, max_core)

    for l in range(len(NN)):
        for a in range(len(map_at_test[l])):
            count_previous_actors+=1

            # max_core-len(map_at_test[l])+a+1 ensures the possibility that all clusters can be mapped on different cores
            if (map_at_test[l][a] < min(count_previous_actors, max_core-len(map_at_test[l])+a+1)):

                # In tmp we store the mapping of actor a from layer l, so that we can restore it at the end of the test,
                # and just try to mutate another actor's mapping independently at next for loop iteration.
                tmp = map_at_test[l][a]

                # Evolve the mapping
                if a == 0:
                    map_at_test[l][a]+=1
                else:
                    if (map_at_test[l][a]<map_at_test[l][a-1]+1) and (map_at_test[l][a-1]+1 <= max_core):
                        map_at_test[l][a]=map_at_test[l][a-1]+1

                # Get memory estimate for mapping
                if not(platformIsFixed):
                    memorysizetab = anon.GetMemoryEstimateForMapping(NN, map_at_test)

                perf_at_test = anon.EvaluateMappingManuscript(NN, map_at_test, mode, memorysizetab)

                # Selection test: if the energy or the latency are lower, then select the new one
                if (perf_at_test[3] < selected_map['anon_energy']) or (perf_at_test[0] < selected_map['anon_latency']):
                    selected_map['mapping'] = copy.deepcopy(map_at_test)
                    selected_map['memory'] = copy.deepcopy(memorysizetab)
                    selected_map['anon_latency'], selected_map['anon_throughput'], selected_map['anon_power'],\
                    selected_map['anon_energy'] = perf_at_test

                # As promised, the value is restored.
                map_at_test[l][a] = tmp

    # If the input mapping is the best mapping, it means that the next mapping doesn't exist => None is returned.
    if selected_map == mapping:
        return None
    # Else the better mapping is returned
    else:
        return selected_map

################################################################################

def ForceUpgradeMapping(NN, mapping, max_core, mode, platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET):
    '''Avoid too fast convergence by forcing the raise of core_number in the mapping'''
    selected_map = copy.deepcopy(mapping)
    core = common.GetCoreNumber(selected_map)
    C = GetClusterizableDict(NN, max_core)
    # Two things are possible here:
    # 1. We can force all clusters from a layer to execute on different cores
    # 2. We can force other layers to have a core number increase
    #
    # We focus 1. in priority (what is the use of clustering if not to parallelize the execution of actors?)
    # Then 2. (which should mainly increase throughput at the cost of power)
    for l in range(len(NN)):
        # Check 1.
        if l in C:
            for a in range(len(selected_map['mapping'][l])):
                if a == 0:
                    cluster_core_nb = selected_map['mapping'][l][a]+1
                else:
                    if (selected_map['mapping'][l][a] < min(cluster_core_nb, max_core)):
                        selected_map['mapping'][l][a] = min(cluster_core_nb, max_core)
                        cluster_core_nb += 1
                        # If we exceed now the core number when entering the function, we return the mapping,
                        # else we continue

                        if common.GetCoreNumber(selected_map) > core:

                            # Get memory estimate for mapping
                            if not(platformIsFixed):
                                selected_map['memory'] = anon.GetMemoryEstimateForMapping(NN, selected_map['mapping'])

                            selected_map['anon_latency'],\
                            selected_map['anon_throughput'],\
                            selected_map['anon_power'],\
                            selected_map['anon_energy']\
                             = anon.EvaluateMappingManuscript(NN, selected_map['mapping'], mode, memorysizetab)

                            return selected_map
                            #TODO: add the list of all clusters on separated cores, review these things

    # Check 2.
    count_previous_actors=0
    for l in range(len(NN)):
        for a in range(len(selected_map['mapping'][l])):
            count_previous_actors+=1
            if count_previous_actors == core+1:
            # ~ and (selected_map['mapping'][l][a] < min(count_previous_actors, max_core-len(map_at_test[l])+a+1)):
                selected_map['mapping'][l][a] += 1

                # Get memory estimate for mapping
                if not(platformIsFixed):
                    selected_map['memory'] = anon.GetMemoryEstimateForMapping(NN, selected_map['mapping'])

                selected_map['anon_latency'],\
                selected_map['anon_throughput'],\
                selected_map['anon_power'],\
                selected_map['anon_energy']\
                = anon.EvaluateMappingManuscript(NN, selected_map['mapping'], mode, selected_map['memory'])

                return selected_map

    # If we didn't return before, something went wrong.
    raise Exception("Something went wrong in ForceUpgradeMapping function in clusterizator_appetizer.py")

################################################################################

def GetMappingsBB(NN, partition, user_def_maxcore, mode, platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET):
    '''Generate mappings for a given partition using BB with the maximum core number being fixed by the user'''

    # A mapping must be a list (layer) of lists (actors issued from clustering),
    # with the associated core on which the actor is mapped: mapping = [[1], [1,1], ... ]
    Mappings = []
    actor_nb = common.GetActorNumberInPartition(partition)
    max_core = min(user_def_maxcore, actor_nb)

    # Generate first mapping
    mapping = { 'mapping':[],
                'memory':[],
                'mapping_index':1,
                'anon_latency':0,
                'anon_throughput':0,
                'anon_power':0,
                'anon_energy':0,
                'mode':mode
              }

    for c in range(len(partition)):
        mapping['mapping'].append([1 for i in range(partition[c])])
        # If the last layer is clusterized, we need to add the decoder actor
        if (c == len(partition)-1) and (partition[c] > 1):
            mapping['mapping'].append([1])

    # Get memory estimate for mapping
    if platformIsFixed:
        mapping['memory'] = memorysizetab
    else:
        mapping['memory'] = anon.GetMemoryEstimateForMapping(NN, mapping['mapping'])

    # Evaluate the first mapping
    mapping['anon_latency'], mapping['anon_throughput'], mapping['anon_power'], mapping['anon_energy']  =\
    anon.EvaluateMappingManuscript(NN, mapping['mapping'], 'P', mapping['memory'])

    # Perform the mapping search using Branch and bound algorithm
    satisfied = False
    while(not(satisfied)):
        while(mapping!=None):
            Mappings.append(mapping)
            mapping = GetNextMappingBB(NN, mapping, max_core, mode, platformIsFixed, memorysizetab)
            #TODO: tmp?? Avoid crash (what the hell is this)
            if (len(Mappings)>100):
                satisfied = True
                return Mappings
        # If the maximum number of cores has not been reached and the Branch and Bound algorith wants to exit, force the
        # mapping upgrade.
        if (common.GetCoreNumber(Mappings[len(Mappings)-1])\
        != min(max_core, common.GetActorNumberInMapping(Mappings[len(Mappings)-1]))):
            mapping = ForceUpgradeMapping(NN,Mappings[len(Mappings)-1],user_def_maxcore, mode,platformIsFixed,memorysizetab)
        else:
            satisfied = True
    return Mappings
    #TODO:
    # ~ #Note: No assumption that clusters from a same layer must be mapped on different cores

################################################################################

def GetNNBestMappings(NN, max_core, platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET):
    '''
    Return the best mappings and their performance, power, energy for the provided NN and maximum number of cores
    If doReport is set to True, then also provides report about the exploration
    '''
    startTime = datetime.now()

    exhaustive_P = GenerateAllClusterings(NN, max_core)
    BB_P = GenerateClusteringsBB(NN, max_core)

    print('- DSE P1 report:')
    print('    - Number of possible NN clusterings: ' + str(len(exhaustive_P)))
    print('    - Number of Branch & Bound selected NN clusterings: ' + str(len(BB_P)))

    total_nb_mappings = 0
    mappings = []
    for p in range(len(BB_P)):
        for mode in ['P', 'CG']:
            tmp_mappings = GetMappingsBB(NN, BB_P[p], max_core, mode, platformIsFixed, memorysizetab)
            for mapping in tmp_mappings:
                mappings.append(mapping)
            total_nb_mappings += len(tmp_mappings)
    print('    - Number of Branch & Bound selected mappings: ' + str(total_nb_mappings))

    mappings = SelectEliteMappings(mappings, max_core)

    print('    - Number of mappings passed to DSE phase 2 (mappings with highest score, max 500): ' + str(len(mappings)))

    print('    - 10 best mappings so far: ')
    for i in range(10):
        print("        * Rank " + str(i) + " - Mapping: " + str(mappings[i]['mapping']) + " - Score: " + str(mappings[i]['anon_score']))

    print('- Phase 1 finished! Execution time: ' + str(datetime.now() - startTime))
    print('')

    return mappings

################################################################################
################################################################################
################################################################################

def SelectEliteMappings(TheMappings, max_core):
    '''
    Return the 'elite' mappings, based on criterias fixed by the user. For the moment, the mappings optimize the score, which
    is defined as energy x latency
    '''
    # Ideas: add an argument 'MIN_MAPPINGS', if we are under this number of mappings, we perform a new loop to find the pareto
    # from the remaining mappings, etc.

    #Left TODO: Return max 200 mappings with best score, sorted by score

    # Only select if there are more than 200 Mappings

    sum_score = 0
    paretoMappings = []
    Mappings = copy.deepcopy(TheMappings)
    # ~ Mappings = sorted(Mappings, key=lambda d: d['anon_score'])
    # ~ paretoMappings.append(copy.deepcopy(Mappings[0]))
    # ~ for mapping in Mappings:
        # ~ if mapping['anon_energy'] < paretoMappings[-1]['anon_energy']:
            # ~ paretoMappings.append(copy.deepcopy(mapping))

    # Since there are not enough selected elite mappings using this method, we also introduce the notion of score and select
    # mappings that optimize the score.
    # In this case, the score is energy x latency, and we select the mappings that minimize it.
    for mapping in Mappings:
        mapping['anon_score'] = mapping['anon_energy'] * mapping['anon_latency']
        # ~ sum_score += mapping['anon_score']
    # ~ average_score = sum_score/len(Mappings)
    Mappings = sorted(Mappings, key=lambda d: d['anon_score'])
    if len(TheMappings) < 500:
        paretoMappings = Mappings
    else:
        paretoMappings = Mappings[:500]

    return paretoMappings



################################################################################
################################################################################
################################################################################

def DoManuscriptClusteringEval(NN, max_core):

    def split(a, n):
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    totalTimeBB = datetime.now()
    clusterBB = GenerateClusteringsBB(NN, max_core)
    totalTimeBB = datetime.now() - totalTimeBB

    totalTimeExo = datetime.now()
    clusterExo = GenerateAllClusterings(NN, max_core)
    totalTimeExo = datetime.now() - totalTimeExo

    print("Total number of BB search clusterings: " + str(len(clusterBB)) + " | total generation time: " \
          + str(totalTimeBB))
    print("Total number of exhaustive search clusterings: " + str(len(clusterExo)) + " | total generation time: " \
          + str(totalTimeExo))
    print("")

    for i in range(len(clusterBB)):
        clusterBB[i] = {'clustering': clusterBB[i], 'score': anon.EvaluateCostPartitioning(NN, clusterBB[i])}
    for i in range(len(clusterExo)):
        clusterExo[i] = {'clustering': clusterExo[i], 'score': anon.EvaluateCostPartitioning(NN, clusterExo[i])}

    clusterExo = sorted(clusterExo, key=lambda d: d['score'])
    clusterExoSplit = list(split(clusterExo, 100))

    results = []
    if len(clusterExo)>100:
        results.append({'score_threshold_low':0,  'score_threshold_high':1})
        results.append({'score_threshold_low':1,  'score_threshold_high':5})
        results.append({'score_threshold_low':5,  'score_threshold_high':10})
        results.append({'score_threshold_low':10, 'score_threshold_high':25})
        results.append({'score_threshold_low':25, 'score_threshold_high':50})
        results.append({'score_threshold_low':50, 'score_threshold_high':100})
    else:
        for i in range(1, len(clusterExo)):
            results.append({'score_threshold_low':i-1,  'score_threshold_high':i})

    for result in results:
        p_counter = 0
        p_index_low = int(result['score_threshold_low']) #int(result['score_threshold_low']*len(clusterExo)/100)
        p_index_high = int(result['score_threshold_high']) #int(result['score_threshold_high']*len(clusterExo)/100)
        if p_index_high == len(clusterExo):
            p_index_high = p_index_high-1
        for i in range(len(clusterBB)):
            for j in range(p_index_low, p_index_high):
                if (clusterBB[i] in clusterExoSplit[j]):
                    p_counter += 1
        p_counter_percent = 0
        cluster_exo_nb = 0
        for j in range(p_index_low, p_index_high):
            cluster_exo_nb += len(clusterExoSplit[j])
        if cluster_exo_nb != 0:
            p_counter_percent = p_counter*100/(cluster_exo_nb)

        print(" - Clusterings with score in " + "[" + str((result['score_threshold_low'])) + " , " \
              + str(result['score_threshold_high']) + "] % best interval" + " => BB found " + format(p_counter_percent, ".2f")\
              + " % of those clusterings (" + str(p_counter) + "/" + str(cluster_exo_nb) + ")")
    print('')
    if len(clusterExo)>100:
        for i in range(min(10,len(clusterExo))):
            clusteringWasFound = False
            if clusterExo[i] in clusterBB:
                clusteringWasFound = True
            print("Clustering ranked " + str(i+1) + " found : " + str(clusteringWasFound))

    return

#######################################################################

def DoManuscriptMappingEval(nn, NN, max_core):

    def split(a, n):
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    clusterings = GenerateClusteringsBB(NN, max_core)

    mappingsBB = []
    mappingsExo = []

    for clustering in clusterings:
        # Exhaustive search
        totalTimeExo = datetime.now()
        for mapping in GenerateAllMappings(NN, clustering, max_core):
            mappingsExo.append(mapping)
        totalTimeExo = datetime.now() - totalTimeExo
        # BB enhanced search
        totalTimeBB = datetime.now()
        for mapping in GetMappingsBB(NN, clustering, max_core, 'P'):
            mappingsBB.append(mapping)
        for mapping in GetMappingsBB(NN, clustering, max_core, 'CG'):
            mappingsBB.append(mapping)
        totalTimeBB = datetime.now() - totalTimeBB

    print("Total number of BB search mappings: " + str(len(mappingsBB)) + " | total generation time: " \
          + str(totalTimeBB))
    print("Total number of exhaustive search mappings: " + str(len(mappingsExo)) + " | total generation time: " \
          + str(totalTimeExo))
    print("")

    for mapping in mappingsBB:
        mapping['anon_score'] = mapping['anon_energy'] * mapping['anon_latency']
    for mapping in mappingsExo:
        mapping['anon_score'] = mapping['anon_energy'] * mapping['anon_latency']

    mappingsExo = sorted(mappingsExo, key=lambda d: d['anon_score'])
    mappingsExoSplit = list(split(mappingsExo, 100))

    results = []
    if len(mappingsExo)>100:
        results.append({'score_threshold_low':0,  'score_threshold_high':1})
        results.append({'score_threshold_low':1,  'score_threshold_high':5})
        results.append({'score_threshold_low':5,  'score_threshold_high':10})
        results.append({'score_threshold_low':10, 'score_threshold_high':25})
        results.append({'score_threshold_low':25, 'score_threshold_high':50})
        results.append({'score_threshold_low':50, 'score_threshold_high':100})
    else:
        for i in range(1, len(mappingsExo)):
            results.append({'score_threshold_low':i-1,  'score_threshold_high':i})

    for result in results:
        p_counter = 0
        p_index_low = int(result['score_threshold_low'])
        p_index_high = int(result['score_threshold_high'])
        if p_index_high == len(mappingsExo):
            p_index_high = p_index_high-1
        for i in range(len(mappingsBB)):
            for j in range(p_index_low, p_index_high):
                for k in range(len( mappingsExoSplit[j])):
                    if (mappingsBB[i]['mapping'] == mappingsExoSplit[j][k]['mapping']):
                        p_counter += 1
        p_counter_percent = 0
        mapping_exo_nb = 0
        for j in range(p_index_low, p_index_high):
            mapping_exo_nb += len(mappingsExoSplit[j])
        if mapping_exo_nb != 0:
            p_counter_percent = p_counter*100/(mapping_exo_nb)

        print(" - Mappings with score in " + "[" + str((result['score_threshold_low'])) + " , " \
              + str(result['score_threshold_high']) + "] % best interval" + " => BB found " + format(p_counter_percent, ".2f")\
              + " % of those mappings (" + str(p_counter) + "/" + str(mapping_exo_nb) + ")")
    print('')

    for i in range(len(mappingsExo)):
        mappingWasFound = False
        for mappingBB in mappingsBB:
            if mappingsExo[i]['mapping'] == mappingBB['mapping']:
                mappingWasFound = True
                mappingsExo[i]['mappingIsFoundByBB'] = True
        if (len(mappingsExo)>100) and (i<=10):
            print("Mapping ranked " + str(i+1) + " found : " + str(mappingWasFound))

    # Save the results in JSON files
    with open('./results_test/' + nn + '_test2_result.json', 'w') as fout:
        json.dump(mappingsExo, fout, sort_keys=True, indent=4, cls=NpEncoder)

    return

#######################################################################

def DoManuscriptDSEAnaSimuComparison(nn, NN, max_core):

    def split(a, n):
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    clusterings = GenerateClusteringsBB(NN, max_core)

    mappingsSimu = []
    mappingsExo = []

    for clustering in clusterings:
        # Start time
        startTimeExo = datetime.now()
        for mapping in GenerateAllMappings(NN, clustering, max_core):
            mappingsExo.append(mapping)
        totalTimeExo = datetime.now() - startTimeExo
        # End time

        # Mappings Simu
        # Start time
        startTimeSimu = datetime.now()
        for mapping in GetMappingsBBSimu(NN, clustering, max_core, 'P'):
            mappingsSimu.append(mapping)
        for mapping in GetMappingsBBSimu(NN, clustering, max_core, 'CG'):
            mappingsSimu.append(mapping)
        totalTimeSimu = datetime.now() - startTimeSimu
        # End time

    print("Total number of simulation-based BB search mappings: " + str(len(mappingsSimu)) + " | total generation time: " \
          + str(totalTimeSimu))
    print("Total number of exhaustive search mappings: " + str(len(mappingsExo)) + " | total generation time: " \
          + str(totalTimeExo))
    print("")

    for mapping in mappingsSimu:
        mapping['anon_score'] = mapping['anon_energy'] * mapping['anon_latency']
    for mapping in mappingsExo:
        mapping['anon_score'] = mapping['anon_energy'] * mapping['anon_latency']

    mappingsExo = sorted(mappingsExo, key=lambda d: d['anon_score'])
    mappingsExoSplit = list(split(mappingsExo, 100))

    results = []
    if len(mappingsExo)>100:
        results.append({'score_threshold_low':0,  'score_threshold_high':1})
        results.append({'score_threshold_low':1,  'score_threshold_high':5})
        results.append({'score_threshold_low':5,  'score_threshold_high':10})
        results.append({'score_threshold_low':10, 'score_threshold_high':25})
        results.append({'score_threshold_low':25, 'score_threshold_high':50})
        results.append({'score_threshold_low':50, 'score_threshold_high':100})
    else:
        for i in range(1, len(mappingsExo)):
            results.append({'score_threshold_low':i-1,  'score_threshold_high':i})

    for result in results:
        p_counter = 0
        p_index_low = int(result['score_threshold_low'])
        p_index_high = int(result['score_threshold_high'])
        if p_index_high == len(mappingsExo):
            p_index_high = p_index_high-1
        for i in range(len(mappingsSimu)):
            for j in range(p_index_low, p_index_high):
                for k in range(len( mappingsExoSplit[j])):
                    if (mappingsSimu[i]['mapping'] == mappingsExoSplit[j][k]['mapping']):
                        p_counter += 1
        p_counter_percent = 0
        mapping_exo_nb = 0
        for j in range(p_index_low, p_index_high):
            mapping_exo_nb += len(mappingsExoSplit[j])
        if mapping_exo_nb != 0:
            p_counter_percent = p_counter*100/(mapping_exo_nb)

        print(" - Mappings with score in " + "[" + str((result['score_threshold_low'])) + " , " \
              + str(result['score_threshold_high']) + "] % best interval" + " => BB found " + format(p_counter_percent, ".2f")\
              + " % of those mappings (" + str(p_counter) + "/" + str(mapping_exo_nb) + ")")
    print('')

    for i in range(min(10,len(mappingsExo))):
        mappingWasFound = False
        for mappingBB in mappingsSimu:
            if mappingsExo[i]['mapping'] == mappingBB['mapping']:
                mappingWasFound = True
                mappingsExo[i]['mappingIsFoundBySimu'] = True
                mappingsExo[i]['p_latency'] = mappingBB['anon_latency']
                mappingsExo[i]['p_throughput'] = mappingBB['anon_throughput']
                mappingsExo[i]['p_power'] = mappingBB['anon_power']
                mappingsExo[i]['p_energy'] = mappingBB['anon_energy']
        if (len(mappingsExo)>100) and (i<=10):
            print("Mapping ranked " + str(i+1) + " found : " + str(mappingWasFound))

    # Save the results in JSON files
    with open('./results_test/' + nn + '_test3_result.json', 'w') as fout:
        json.dump(mappingsExo, fout, sort_keys=True, indent=4, cls=NpEncoder)

    return

################################################################################

def GetNaiveSimuMappingEval(NN, user_def_maxcore, mode='CG', platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET):
    '''Test naive mappings using simulation for the considered NN'''

    mapping_1 = { 'mapping':[],
                'memory':[],
                'mapping_index':1,
                'anon_latency':0,
                'anon_throughput':0,
                'anon_power':0,
                'anon_energy':0,
                'mode':mode
              }

    mapping_2 = { 'mapping':[],
                'memory':[],
                'mapping_index':1,
                'anon_latency':0,
                'anon_throughput':0,
                'anon_power':0,
                'anon_energy':0,
                'mode':mode
              }

    j = 1
    for layer in NN:
        # 1
        if 'features_nb' in layer:
            mapping_1['mapping'].append([i+1 for i in range(common.GetMaxClusterNumber(layer, user_def_maxcore))])
        else:
            mapping_1['mapping'].append([1])
        # 2
        mapping_2['mapping'].append([j])
        j = min(j+1, user_def_maxcore)

    # Decoder mapping 1 - there is always a decoder because last layer is always dense, and unless it has only 1 neuron,
    # then it needs decoder (mapping 1 is max cluster every layer)
    mapping_1['mapping'].append([1])

    # Get memory estimate for mappings
    if platformIsFixed:
        mapping_1['memory'] = memorysizetab
        mapping_2['memory'] = memorysizetab
    else:
        mapping_1['memory'] = anon.GetMemoryEstimateForMapping(NN, mapping_1['mapping'])
        mapping_2['memory'] = anon.GetMemoryEstimateForMapping(NN, mapping_2['mapping'])

    print('mapping 1: ' + str(mapping_1))
    print('\nmapping 2: ' + str(mapping_2))

    # Evaluate the first mapping
    mapping_1['anon_latency'], mapping_1['anon_throughput'], mapping_1['anon_power'], mapping_1['anon_energy']  =\
    phase2.EvaluateMappingSimu(NN, mapping_1['mapping'], 'CG', mapping_1['memory'])
    mapping_2['anon_latency'], mapping_2['anon_throughput'], mapping_2['anon_power'], mapping_2['anon_energy']  =\
    phase2.EvaluateMappingSimu(NN, mapping_2['mapping'], 'CG', mapping_2['memory'])

    mapping_1['score'] = mapping_1['anon_latency']*mapping_1['anon_energy']
    mapping_2['score'] = mapping_2['anon_latency']*mapping_2['anon_energy']

    print('mapping 1: ' + str(mapping_1))
    print('\nmapping 2: ' + str(mapping_2))
    return

################################################################################

#DEPRECATED
def ForceUpgradeMappingSimu(NN, mapping, max_core, mode, platformIsFixed=False, memorysizetab=common.DEFAULT_MEMORY_SET):
    '''Deprecated: Avoid too fast convergence by forcing the raise of core_number in the mapping'''
    selected_map = copy.deepcopy(mapping)
    core = common.GetCoreNumber(selected_map)
    C = GetClusterizableDict(NN, max_core)
    # Two things are possible here:
    # 1. We can force all clusters from a layer to execute on different cores
    # 2. We can force other layers to have a core number increase
    #
    # We focus 1. in priority (what is the use of clustering if not to parallelize the execution of actors?)
    # Then 2. (which should mainly increase throughput at the cost of power)
    for l in range(len(NN)):
        # Check 1.
        if l in C:
            for a in range(len(selected_map['mapping'][l])):
                if a == 0:
                    cluster_core_nb = selected_map['mapping'][l][a]+1
                else:
                    if (selected_map['mapping'][l][a] < min(cluster_core_nb, max_core)):
                        selected_map['mapping'][l][a] = min(cluster_core_nb, max_core)
                        cluster_core_nb += 1
                        # If we exceed now the core number when entering the function, we return the mapping,
                        # else we continue

                        if common.GetCoreNumber(selected_map) > core:

                            # Get memory estimate for mapping
                            if not(platformIsFixed):
                                selected_map['memory'] = anon.GetMemoryEstimateForMapping(NN, selected_map['mapping'])

                            selected_map['anon_latency'],\
                            selected_map['anon_throughput'],\
                            selected_map['anon_power'],\
                            selected_map['anon_energy']\
                             = phase2.EvaluateMappingSimu(NN, selected_map['mapping'], mode, memorysizetab)

                            return selected_map
                            #TODO: add the list of all clusters on separated cores, review these things

    # Check 2.
    count_previous_actors=0
    for l in range(len(NN)):
        for a in range(len(selected_map['mapping'][l])):
            count_previous_actors+=1
            if count_previous_actors == core+1:
            # ~ and (selected_map['mapping'][l][a] < min(count_previous_actors, max_core-len(map_at_test[l])+a+1)):
                selected_map['mapping'][l][a] += 1

                # Get memory estimate for mapping
                if not(platformIsFixed):
                    selected_map['memory'] = anon.GetMemoryEstimateForMapping(NN, selected_map['mapping'])

                selected_map['anon_latency'],\
                selected_map['anon_throughput'],\
                selected_map['anon_power'],\
                selected_map['anon_energy']\
                = phase2.EvaluateMappingSimu(NN, selected_map['mapping'], mode, selected_map['memory'])

                return selected_map

    # If we didn't return before, something went wrong.
    raise Exception("Something went wrong in ForceUpgradeMapping function in clusterizator_appetizer.py")

################################################################################

################################################################################
################################################################################
################################################################################
