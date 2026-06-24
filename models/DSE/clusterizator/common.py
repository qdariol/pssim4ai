#
# File: common.py
# Date of creation (dd.mm.yyyy): 23.06.2023
# Description: This file provides functions used commonly among the DSE procedures.
# Author: Quentin Dariol
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

import json

PROCESSOR_FREQUENCY = 100000000
DEFAULT_MEMORY_SET = [1024, 256, 256, 256, 256, 256, 256]

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

def GetMaxClusterNumber(layer, max_core_nb):
    '''Return the maximum possible number of clusters that can be generated from the layer passed as argument'''
    return min(layer['features_nb'], max_core_nb)

def GetClusterSize(layer, cluster_number):
    '''Return the list of feature numbers (ie. neurons, or convolution filters) contained in each cluster of the layer
    for a clustering into 'cluster_number' actors'''
    cluster_sizes = [None]*cluster_number
    cluster_modulo = layer['features_nb'] % cluster_number
    base_nb_of_neurons = int((layer['features_nb'] - cluster_modulo)/cluster_number)
    for j in range (0, cluster_number):
        cluster_sizes[j] = base_nb_of_neurons
        if j >= cluster_number-cluster_modulo:
            cluster_sizes[j] += 1
    return cluster_sizes

def GetActorNumberInPartition(partition):
    '''Returns the number of actors in the partition'''
    actor_nb = 0
    for l in range(len(partition)):
        actor_nb += partition[l]
    return actor_nb

def GetActorNumberInMapping(mapping):
    '''Returns the number of actors in the mapping'''
    if type(mapping) is dict:
        mapping = mapping['mapping']
    actor_nb = 0
    for l in range(len(mapping)):
        actor_nb += len(mapping[l])
    return actor_nb

def GetChannelNumberInMapping(mapping):
    '''Returns the number of communication channel in the mapping'''
    if type(mapping) is dict:
        mapping = mapping['mapping']
    channel_nb = 0
    for l in range(len(mapping)):
        if l==0:
            # Input channel is not clustered (C=1) so only clustering of layer l
            channel_nb += len(mapping[l])
        else:
            channel_nb += len(mapping[l])*len(mapping[l-1])
            if l==len(mapping)-1:
                channel_nb += 1 #channel out, note: this works both with and without decoder actor
    return channel_nb

def GetCoreNumber(mapping):
    '''Returns the number of cores in the mapping'''
    if type(mapping) is dict:
        mapping = mapping['mapping']
    core_number = 0
    for mapped in (mapping):
        core_number = max(max(mapped), core_number)
    return core_number

def IsMLP(NN):
    '''Returns True if the considered NN is a MLP (trained with LibFANN), False otherwise'''
    NNisMLP = True
    for l in NN:
        if l['layer_type'] != 'd':
            NNisMLP = False
    return NNisMLP
