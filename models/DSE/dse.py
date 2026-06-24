#
# File: dse.py
# Date of creation (dd.mm.yyyy): 08.03.2023
# Description: This python script handles the whole DSE process for the app. in the NN folder given NN and USER_DEF_MAX_CORE
# Author: Quentin Dariol
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

import json
from clusterizator import common
from clusterizator import phase1
import glob
from timeit import default_timer as timer
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# Load Neural Network (NN) definition
USER_DEF_NN_FILES = sorted(glob.glob("./NN/*.json"))
# ~ USER_DEF_NN_FILES = ['./NN/CNN.json']

# Max number of cores in the target platform (Default if unspecified: 7)
# Warning: the SystemC models only support up to 7 tiles.
USER_DEF_MAX_CORE = 7

# Platform specs
USER_DEF_PTF_IS_FIXED_BOOL = False
USER_DEF_MEMORY_SIZE_TAB = [1024,256,256,256,256,256,256]

DO_EVALUATION_MAPPINGS = False
DO_STATS = True

# Timers in seconds
TIMER_FIRST_ROUND = 4*60
TIMER_TOTAL = 2*60*60
PERIODIC_SAVE_TIMER = 60

# Do Activities Booleans
BOOL_DO_DSE = False
BOOL_DO_DSE_RESUME_PHASE2 = False
BOOL_DO_PLOT = True
BOOL_DO_REPORT = True

################################################################################
################################################################################

# Plot after phase 2
def doPlotPhase2(nn, Mappings):
    simu_times=[]
    simu_energies=[]
    simu_core_numbers=[]

    for m in range(len(Mappings)):
        for mapping in (Mappings[m]):
            simu_times.append(mapping['results_CG']['p_e2e']/1e6)
            simu_times.append(mapping['results_P']['p_e2e']/1e6)
            simu_energies.append(mapping['results_CG']['p_energy'])
            simu_energies.append(mapping['results_P']['p_energy'])
            simu_core_numbers.append(common.GetCoreNumber(mapping))
            simu_core_numbers.append(common.GetCoreNumber(mapping))

    plt.figure("")
    plt.scatter(simu_times, simu_energies, marker='o', color='gold', linewidth=0.25, edgecolor='k', s=15)
    plt.xlabel('Latency (cycles)')
    plt.ylabel('Energy consumption (mJ)')
    plt.grid(True, color='grey', linestyle='--')
    plt.savefig('results/' + nn + '_simu_pareto.pdf', dpi=300, transparent=True, bbox_inches='tight')
    plt.clf()

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(5, 4))
    ax[0].scatter(simu_core_numbers, simu_times,     marker='o', color='yellow', linewidth=0.25, edgecolor='k', s=15) # s=10
    ax[1].scatter(simu_core_numbers, simu_energies,   marker='o', color='green', linewidth=0.25, edgecolor='k', s=15)
    ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    ax[1].xaxis.set_major_locator(MaxNLocator(integer=True))
    ax[0].grid(True, color='grey', linestyle='--')
    ax[1].grid(True, color='grey', linestyle='--')
    ax[0].set_title("Latency (Cycles)")
    ax[1].set_title("Energy consumption (mJ)")
    ax[1].set_xlabel("Number of tiles used")

    fig.tight_layout()
    plt.savefig('results/' + nn + '_simu_dse_plot.pdf', dpi=300, transparent=True, bbox_inches='tight')
    plt.clf()

NN = {}
for nnfile in USER_DEF_NN_FILES:
    string_name_nn = nnfile.replace('./NN/', '').replace('.json', '')
    with open(nnfile, 'r') as json_file:
        NN[string_name_nn] = json.load(json_file)

for nn in NN:
    print("Currently processing the " + nn)
    if BOOL_DO_DSE:
        if BOOL_DO_DSE_RESUME_PHASE2:
            with open('run/' + nn + '_maps.json','r') as json_file:
                Mappings = json.load(json_file)
            end = 0
            start = 0
        else:
            Clusterings=phase1.GenerateClusteringsBB(NN[nn], USER_DEF_MAX_CORE)
            Mappings = []
            start = timer()
            for clustering in Clusterings:
                # Explore mapping possibilities of each clusterings for 5 minutes.
                Mappings.append(phase1.GetMappingsBBSimu(NN[nn], USER_DEF_MAX_CORE, bool_PlatformIsFixed=False,\
                Mappings=[], ExplorationTimeLimit=TIMER_FIRST_ROUND, clustering=clustering, bool_PeriodicSaves=True,\
                PeriodicSavesTimer=PERIODIC_SAVE_TIMER, PeriodSavesOutputFile='run/tmp_' + nn + '_maps.json'))
                with open('run/' + nn + '_maps.json', 'w') as fout:
                    json.dump(Mappings, fout, sort_keys=True, indent=4, cls=common.NpEncoder)
                print('First phase exploration done for one of the clusterings.')
            end = timer()
            print("First phase entirely completed. Now performing additional exploration.")

        print("Starting or re-Starting second phase: exploring mappings from multiple clusterings simultaneously")
        start2 = timer()
        # Explore more until 2 hours mark
        Mappings=phase1.GetMappingsBBSimu(NN[nn], USER_DEF_MAX_CORE, bool_PlatformIsFixed=False,\
        Mappings=Mappings, ExplorationTimeLimit=TIMER_TOTAL-(end - start), bool_PeriodicSaves=True,\
        PeriodicSavesTimer=PERIODIC_SAVE_TIMER*3, PeriodSavesOutputFile='run/tmp_' + nn + '_maps.json',\
        bool_doMultipleClusteringsMode=True)
        with open('run/' + nn + '_maps_4h.json', 'w') as fout:
            json.dump(Mappings, fout, sort_keys=True, indent=4, cls=common.NpEncoder)
        print("Second phase entirely completed. Results stored in the run folder. Time spent:" + str(int((timer()-start2)/60)) + "min.")

    if BOOL_DO_REPORT:
        with open('run/' + nn + '_maps_4h.json','r') as json_file:
            Mappings = json.load(json_file)
        map_list = []
        mapping_nb=0
        for m in range(len(Mappings)):
            for mapping in (Mappings[m]):
                mapping_nb += 1
                # Naive mapping obtained with Highest clustering + clock gating
                if (mapping['bool_isNaiveMapping']) and (m==0):
                    naive_score = mapping['results_CG']['p_energy']
                    print("Naive mapping: " + str(mapping['mapping']))
                    map_list.append({'mapping': mapping['mapping'],
                    'p_e2e': mapping['results_CG']['p_e2e'],
                    'p_energy': mapping['results_CG']['p_energy'],
                    'mode': 'CG',
                    'memory':mapping['memory'],
                    'bool_isNaiveMapping': True})
                else:
                    map_list.append({'mapping': mapping['mapping'],
                    'p_e2e': mapping['results_CG']['p_e2e'],
                    'p_energy': mapping['results_CG']['p_energy'],
                    'mode': 'CG',
                    'memory':mapping['memory'],
                    'bool_isNaiveMapping': False})
                    map_list.append({'mapping': mapping['mapping'],
                    'p_e2e': mapping['results_P']['p_e2e'],
                    'p_energy': mapping['results_P']['p_energy'],
                    'mode': 'P',
                    'memory':mapping['memory'],
                    'bool_isNaiveMapping': False})


        map_list = sorted(map_list, key=lambda d: d['p_energy'])
        energy_best=map_list[0]['p_energy']
        latency_best = float("inf")
        for i in range(len(map_list)):
            if (map_list[i]['p_e2e']<latency_best):
                latency_best = map_list[i]['p_e2e']
                index_latency_best = i

        if(naive_score>energy_best):
            print("The naive implementation IS beaten!")
        else:
            print("The naive implementation IS NOT beaten!")

        print("List of best mappings found that optimized energy:")
        p_found = False
        cg_found = False
        naive_found=False
        index_latency_best_found = False
        for i in range(0,10):
            print("    - n." + str(i+1) + " - Mapping: " + str(map_list[i]['mapping']) + " | Mode: " + (map_list[i]['mode']) +\
            " | Energy: " + "%.2f" %  (map_list[i]['p_energy']) + " mJ, Diff:" + "%.2f" % \
            (((map_list[i]['p_energy']-energy_best)/energy_best)*100) + " %.     | Latency: " + "%.2f" % (map_list[i]['p_e2e']) +\
            " cycles, Diff: " + "%.2f" % (((map_list[i]['p_e2e']-latency_best)/latency_best)*100) + " %." +\
            "    | Platform dimensions: " + str(map_list[i]['memory']))
            if (map_list[i]['bool_isNaiveMapping']):
                naive_found=True
                print("      ↪ This is the naive mapping.")
            if (map_list[i]['mode'])=='P':
                p_found=True
            if (map_list[i]['mode'])=='CG':
                cg_found=True
            if (i==0):
                print("      ↪ This is the mapping with the best energy.")
            if (i==index_latency_best):
                print("      ↪ This is the mapping with the best latency.")
                index_latency_best_found = True

        i=10
        while(not(p_found) or not(cg_found) or not(naive_found)):
            if ((map_list[i]['mode'])=='P') and (not(p_found)):
                p_found=True
                print('    ...')
                print("    - n." + str(i+1) + " - Mapping: " + str(map_list[i]['mapping']) + " | Mode: " + (map_list[i]['mode']) +\
                " | Energy: " + "%.2f" %  (map_list[i]['p_energy']) + " mJ, Diff:" + "%.2f" % \
                (((map_list[i]['p_energy']-energy_best)/energy_best)*100) + " %.     | Latency: " + "%.2f" % (map_list[i]['p_e2e']) +\
                " cycles, Diff: " + "%.2f" % (((map_list[i]['p_e2e']-latency_best)/latency_best)*100) + " %."+\
                "    | Platform dimensions: " + str(map_list[i]['memory']))
            if (map_list[i]['mode'])=='CG' and (not(cg_found)):
                cg_found=True
                print('    ...')
                print("    - n." + str(i+1) + " - Mapping: " + str(map_list[i]['mapping']) + " | Mode: " + (map_list[i]['mode']) +\
                " | Energy: " + "%.2f" %  (map_list[i]['p_energy']) + " mJ, Diff:" + "%.2f" % \
                (((map_list[i]['p_energy']-energy_best)/energy_best)*100) + " %.     | Latency: " + "%.2f" % (map_list[i]['p_e2e']) +\
                " cycles, Diff: " + "%.2f" % (((map_list[i]['p_e2e']-latency_best)/latency_best)*100) + " %."+\
                "    | Platform dimensions: " + str(map_list[i]['memory']))
            if (map_list[i]['bool_isNaiveMapping']) and (not(naive_found)):
                naive_found=True
                print('    ...')
                print("    - n." + str(i+1) + " - Mapping: " + str(map_list[i]['mapping']) + " | Mode: " + (map_list[i]['mode']) +\
                " | Energy: " + "%.2f" %  (map_list[i]['p_energy']) + " mJ, Diff:" + "%.2f" % \
                (((map_list[i]['p_energy']-energy_best)/energy_best)*100) + " %.     | Latency: " + "%.2f" % (map_list[i]['p_e2e']) +\
                " cycles, Diff: " + "%.2f" % (((map_list[i]['p_e2e']-latency_best)/latency_best)*100) + " %."+
                "    | Platform dimensions: " + str(map_list[i]['memory']))
                print("      ↪ This is the naive mapping.")
            i+=1

        print("")
        print("Number of mappings explored: " + str(mapping_nb))

        print("")
        print("~~ooOoo~~")
        print("")

    if BOOL_DO_PLOT:
        with open('run/' + nn + '_maps.json','r') as json_file:
            Mappings = json.load(json_file)
        doPlotPhase2(nn, Mappings)

