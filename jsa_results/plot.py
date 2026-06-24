import matplotlib as mpl
import matplotlib.pyplot as plt
# import numpy as np
# import operator
import json
from copy import deepcopy

# Bools indicating which plots to draw.
doPlotMode      = True
doPlotApp       = True
doPlotTileNb    = True
doPlotComm      = True
bool_verbose    = True
doPlot          = False

# RESULTS_JSON_FILE = './results_model_evaluation.json'
RESULTS_JSON_FILE = '../results_model_evaluation_anon.json'
FIG_SIZE = (5,3)
FONT_SIZE = 16

# Helper functions
def addLabels(x, y, s):
    for i in range(len(x)):
        plt.text(x[i], y[i], s[i], rotation=70, fontsize=9)

def GetCoreNumber(mapping):
    '''Returns the number of cores in the mapping'''
    core_number = 0
    for mapped in (mapping):
        core_number = max(max(mapped), core_number)
    return core_number

with open(RESULTS_JSON_FILE, 'r') as json_file:
    data = json.load(json_file)

# Definition of colors
# Old
# Colors = {"avg_time"   : "#b2182b", #
#         "max_time"   : "#ef8a62",   #
#         "avg_power"  : '#fddbc7',   #avg_time '#fddbc7'
#         "max_power"  : '#c7eae5',   #
#         "avg_energy" : "#5ab4ac",   #
#         "max_energy" : "#01665e"}   #

Colors = {"avg_time"   : '#fddbc7',
        "avg_power"    : '#ef8a62',
        "avg_energy"   : '#b2182b',
        "max_time"     : '#c7eae5',
        "max_power"    : '#5ab4ac',
        "max_energy"   : '#01665e'}

# ################################################################
# Plot: Interrupt-based + power saving / polling no power saving
# ################################################################
if doPlotMode:
    # A. Prepare data

    total_cg_time           = 0
    max_cg_time             = 0
    total_cg_power          = 0
    max_cg_power            = 0
    total_cg_energy         = 0
    max_cg_energy           = 0
    nb_scenarii             = 0
    total_polling_time      = 0
    max_polling_time        = 0
    total_polling_power     = 0
    max_polling_power       = 0
    total_polling_energy    = 0
    max_polling_energy      = 0

    for scenario in data:

        tmp = abs(scenario["results_CG"]["prediction_error_time"])
        total_cg_time += tmp
        if max_cg_time < tmp:
            max_cg_time = tmp

        tmp = abs(scenario["results_CG"]["prediction_error_power"])
        total_cg_power += tmp
        if max_cg_power < tmp:
            max_cg_power = tmp

        tmp = abs(scenario["results_CG"]["prediction_error_energy"])
        total_cg_energy += tmp
        if max_cg_energy < tmp:
            max_cg_energy = tmp

        tmp = abs(scenario["results_P"]["prediction_error_time"])
        total_polling_time += tmp
        if max_polling_time < tmp:
            max_polling_time = tmp

        tmp = abs(scenario["results_P" ]["prediction_error_power"])
        total_polling_power += tmp
        if max_polling_power < tmp:
            max_polling_power = tmp

        tmp = abs(scenario["results_P"]["prediction_error_energy"])
        total_polling_energy += tmp
        if max_polling_energy < tmp:
            max_polling_energy = tmp

        nb_scenarii += 1

    total_cg_time        = total_cg_time       /nb_scenarii
    total_cg_power       = total_cg_power      /nb_scenarii
    total_cg_energy      = total_cg_energy     /nb_scenarii
    total_polling_time   = total_polling_time  /nb_scenarii
    total_polling_power  = total_polling_power /nb_scenarii
    total_polling_energy = total_polling_energy/nb_scenarii

    print("Power management influence:")
    print("- nb scenarii: "   + '{0:.2f}'.format(nb_scenarii))
    print("- avg CG time: "   + '{0:.2f}'.format(total_cg_time))
    print("- max CG time: "   + '{0:.2f}'.format(max_cg_time))
    print("- avg CG power: "  + '{0:.2f}'.format(total_cg_power))
    print("- max CG power: "  + '{0:.2f}'.format(max_cg_power))
    print("- avg CG energy: " + '{0:.2f}'.format(total_cg_energy))
    print("- max CG energy: " + '{0:.2f}'.format(max_cg_energy))
    print()
    print("- avg polling time: "   + '{0:.2f}'.format(total_polling_time))
    print("- max polling time: "   + '{0:.2f}'.format(max_polling_time))
    print("- avg polling power: "  + '{0:.2f}'.format(total_polling_power))
    print("- max polling power: "  + '{0:.2f}'.format(max_polling_power))
    print("- avg polling energy: " + '{0:.2f}'.format(total_polling_energy))
    print("- max polling energy: " + '{0:.2f}'.format(max_polling_energy))
    print()

    X_labels=["Without" + '\n$M_{n}=$' + str(nb_scenarii), "With" + '\n$M_{n}=$' + str(nb_scenarii)]

    X = [0.7, 1.7, 0.8, 1.8, 0.9, 1.9, 1.1, 2.1, 1.2, 2.2, 1.3, 2.3]
    # X = [x - 0.05 for x in X]
    X = [x - 0.065 for x in X]
    Y = [total_polling_time, total_cg_time, total_polling_power, total_cg_power, total_polling_energy, total_cg_energy, max_polling_time, max_cg_time, max_polling_power, max_cg_power, max_polling_energy, max_cg_energy]
    Y = [y + 0.1 for y in Y]
    Y_labels = [("{:.2f}".format(y_label)) for y_label in Y]
    for i in range(len(Y_labels)):
        while len(Y_labels[i]) < 4:
            Y_labels[i] += '0'

    # B. Plot data
    if doPlot:
        plt.figure(figsize=FIG_SIZE)
        # fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9,7)) #figsize=(9,7))
        # ax1  = ax
        # ax2  = ax.twinx()
        # ax3  = ax.twinx()
        plt.grid(True, color='grey', linestyle='--', axis='y', zorder=1000)
        plt.bar ([0.7, 1.7], [total_polling_time, total_cg_time], label = 'average timing error', edgecolor = 'black', color=Colors['avg_time'],  width = 0.1, hatch='')
        plt.bar ([0.8, 1.8], [total_polling_power, total_cg_power], label = 'average power error', edgecolor = 'black', color=Colors['avg_power'], width = 0.1, hatch='')
        plt.bar ([0.9, 1.9], [total_polling_energy, total_cg_energy], label = 'average energy error', edgecolor = 'black', color=Colors['avg_energy'], width = 0.1, hatch='')

        # MAX
        plt.bar ([1.1, 2.1], [max_polling_time, max_cg_time], label = 'highest timing error', edgecolor = 'black', color=Colors['max_time'],  width = 0.1, hatch='')
        plt.bar ([1.2, 2.2], [max_polling_power, max_cg_power], label = 'highest power error', edgecolor = 'black', color=Colors['max_power'], width = 0.1, hatch='')
        plt.bar ([1.3, 2.3], [max_polling_energy, max_cg_energy], label = 'highest energy error', edgecolor = 'black', color=Colors['max_energy'], width = 0.1, hatch='')

        # addLabels(X, Y, Y_labels) # Commented because looks ugly
        plt.ylim(0,8)
        plt.xlim(0.5,4.25)

        # plt.xlabel('Execution time (cycles)')
        plt.ylabel('Error (%)', fontsize = 16)
        plt.yticks(fontsize = 13)
        plt.xticks([1,2],X_labels, fontsize = 13)
        plt.xlabel('Power management', fontsize = 16)
        plt.legend(loc='right', framealpha=1) #"fontsize="small")
        plt.tight_layout()
        # plt.show()
        plt.savefig('plot_power_mngt.pdf', dpi=300, transparent=True, bbox_inches='tight')

# ################################################################
# Plot: Application-based
# ################################################################
if doPlotApp:

    # No plot for this. (just table) skip.

    ResultsPerANN = {}
    nb_scenarii = 0

    # Get sum of errors for each metric and each application
    for scenario in data:
        if scenario["application"] in ResultsPerANN:

            ResultsPerANN[scenario["application"]]["avg_time"] += abs(scenario["results_CG"]["prediction_error_time"]) + abs(scenario["results_P"]["prediction_error_time"])
            ResultsPerANN[scenario["application"]]["max_time"] = max(max(ResultsPerANN[scenario["application"]]["max_time"], abs(scenario["results_CG"]            ["prediction_error_time"])),abs(scenario["results_P"]["prediction_error_time"]))

            ResultsPerANN[scenario["application"]]["avg_power"] += abs(scenario["results_CG"]["prediction_error_power"]) + abs(scenario["results_P"]["prediction_error_power"])
            ResultsPerANN[scenario["application"]]["max_power"] = max(max(ResultsPerANN[scenario["application"]]["max_power"], abs(scenario["results_CG"]["prediction_error_power"])),abs(scenario["results_P"]["prediction_error_power"]))

            ResultsPerANN[scenario["application"]]["avg_energy"] += abs(scenario["results_CG"]["prediction_error_energy"]) + abs(scenario["results_P"]["prediction_error_energy"])
            ResultsPerANN[scenario["application"]]["max_energy"] = max(max(ResultsPerANN[scenario["application"]]["max_energy"], abs(scenario["results_CG"]["prediction_error_energy"])),abs(scenario["results_P"]["prediction_error_energy"]))

            ResultsPerANN[scenario["application"]]["nb_scenarii"] += 2

        else:

            ResultsPerANN[scenario["application"]] = {}

            ResultsPerANN[scenario["application"]]["avg_time"] = abs(scenario["results_CG"]["prediction_error_time"]) + abs(scenario["results_P"]["prediction_error_time"])
            ResultsPerANN[scenario["application"]]["max_time"] = max(abs(scenario["results_CG"]["prediction_error_time"]),abs(scenario["results_P"]["prediction_error_time"]))

            ResultsPerANN[scenario["application"]]["avg_power"] = abs(scenario["results_CG"]["prediction_error_power"]) + abs(scenario["results_P"]["prediction_error_power"])
            ResultsPerANN[scenario["application"]]["max_power"] = max(abs(scenario["results_CG"]["prediction_error_power"]),abs(scenario["results_P"]["prediction_error_power"]))

            ResultsPerANN[scenario["application"]]["avg_energy"] = abs(scenario["results_CG"]["prediction_error_energy"]) + abs(scenario["results_P"]["prediction_error_energy"])
            ResultsPerANN[scenario["application"]]["max_energy"] = max(abs(scenario["results_CG"]["prediction_error_energy"]),abs(scenario["results_P"]["prediction_error_energy"]))

            ResultsPerANN[scenario["application"]]["nb_scenarii"] = 2

    # Get averaged error
    print("Application influence:")
    for application in ResultsPerANN:
        ResultsPerANN[application]["avg_time"] = ResultsPerANN[application]["avg_time"]/ResultsPerANN[application]["nb_scenarii"]
        ResultsPerANN[application]["avg_power"] = ResultsPerANN[application]["avg_power"]/ResultsPerANN[application]["nb_scenarii"]
        ResultsPerANN[application]["avg_energy"] = ResultsPerANN[application]["avg_energy"]/ResultsPerANN[application]["nb_scenarii"]

        print(" - application: " + application)
        print("    - avg time: "      + '{0:.2f}'.format(ResultsPerANN[application]["avg_time"]))
        print("    - max time: "      + '{0:.2f}'.format(ResultsPerANN[application]["max_time"]))
        print("    - avg power: "     + '{0:.2f}'.format(ResultsPerANN[application]["avg_power"]))
        print("    - max power: "     + '{0:.2f}'.format(ResultsPerANN[application]["max_power"]))
        print("    - avg energy: "    + '{0:.2f}'.format(ResultsPerANN[application]["avg_energy"]))
        print("    - max energy: "    + '{0:.2f}'.format(ResultsPerANN[application]["max_energy"]))
# ################################################################
# Plot: Number of cores
# ################################################################
if doPlotTileNb:
    # A. Prepare data
    resultsPerTile={}
    base_dict = {"nb_scenarii"  : 0,
                "avg_time"     : 0,
                "max_time"     : 0,
                "avg_power"    : 0,
                "max_power"    : 0,
                "avg_energy"   : 0,
                "max_energy"   : 0}

    for scenario in data:
        # nb_scenarii += 1
        tile_nb = str(GetCoreNumber(scenario["mapping"]))
        if not(tile_nb in resultsPerTile):
            resultsPerTile[tile_nb] = deepcopy(base_dict)

        tmp = abs(scenario["results_CG"]["prediction_error_time"])
        resultsPerTile[tile_nb]["avg_time"] += tmp
        resultsPerTile[tile_nb]["max_time"] = max(resultsPerTile[tile_nb]["max_time"], tmp)

        tmp = abs(scenario["results_CG"]["prediction_error_power"])
        resultsPerTile[tile_nb]["avg_power"] += tmp
        resultsPerTile[tile_nb]["max_power"] = max(resultsPerTile[tile_nb]["max_power"], tmp)

        tmp = abs(scenario["results_CG"]["prediction_error_energy"])
        resultsPerTile[tile_nb]["avg_energy"] += tmp
        resultsPerTile[tile_nb]["max_energy"] = max(resultsPerTile[tile_nb]["max_energy"], tmp)

        tmp = abs(scenario["results_P"]["prediction_error_time"])
        resultsPerTile[tile_nb]["avg_time"] += tmp
        resultsPerTile[tile_nb]["max_time"] = max(resultsPerTile[tile_nb]["max_time"], tmp)

        tmp = abs(scenario["results_P" ]["prediction_error_power"])
        resultsPerTile[tile_nb]["avg_power"] += tmp
        resultsPerTile[tile_nb]["max_power"] = max(resultsPerTile[tile_nb]["max_power"], tmp)

        tmp = abs(scenario["results_P"]["prediction_error_energy"])
        resultsPerTile[tile_nb]["avg_energy"] += tmp
        resultsPerTile[tile_nb]["max_energy"] = max(resultsPerTile[tile_nb]["max_energy"], tmp)

        resultsPerTile[tile_nb]["nb_scenarii"] += 2 #For polling and clock gating

    X_labels = {"int": [], "label": []}
    for tile_nb in resultsPerTile:
        resultsPerTile[tile_nb]["avg_time"]   = resultsPerTile[tile_nb]["avg_time"]  /resultsPerTile[tile_nb]["nb_scenarii"]
        resultsPerTile[tile_nb]["avg_power"]  = resultsPerTile[tile_nb]["avg_power"] /resultsPerTile[tile_nb]["nb_scenarii"]
        resultsPerTile[tile_nb]["avg_energy"] = resultsPerTile[tile_nb]["avg_energy"]/resultsPerTile[tile_nb]["nb_scenarii"]
        X_labels["int"].append(int(tile_nb))
        X_labels["label"].append(tile_nb + '\n$M_{n}=$' + str(resultsPerTile[tile_nb]["nb_scenarii"]))
        if bool_verbose:
            print("For tile_nb = " + str(tile_nb) + ":")
            print("    - avg_time:   " + str(resultsPerTile[tile_nb]["avg_time"]))
            print("    - avg_power:  " + str(resultsPerTile[tile_nb]["avg_power"]))
            print("    - avg_energy: " + str(resultsPerTile[tile_nb]["avg_energy"]))
            print("    - max_time:   " + str(resultsPerTile[tile_nb]["max_time"]))
            print("    - max_power:  " + str(resultsPerTile[tile_nb]["max_power"]))
            print("    - max_energy: " + str(resultsPerTile[tile_nb]["max_energy"]))
            print("")

    X = {"avg_time"   : [],
        "max_time"   : [],
        "avg_power"  : [],
        "max_power"  : [],
        "avg_energy" : [],
        "max_energy" : []}
    for x in X_labels['int']:
        X["avg_time"  ].append(x - 0.3)
        X["avg_power" ].append(x - 0.2)
        X["avg_energy"].append(x - 0.1)
        X["max_time"  ].append(x + 0.1)
        X["max_power" ].append(x + 0.2)
        X["max_energy"].append(x + 0.3)

    # B. Plot data
    if doPlot:
        plt.figure(figsize=FIG_SIZE)
        plt.grid(True, color='grey', linestyle='--', axis='y', zorder=1000)

        for key in ["avg_time", "avg_power",  "avg_energy", "max_time", "max_power", "max_energy"]:
            Y = []
            for tile_nb in resultsPerTile:
                Y.append(resultsPerTile[tile_nb][key])
            plt.bar (X[key], Y, label = key, edgecolor = 'black', color=Colors[key],  width = 0.1, hatch='')

        # addLabels(X, Y, Y_labels)
        plt.ylim(0,8)
        # plt.xlabel('Execution time (cycles)')
        plt.ylabel('Error (%)', fontsize = 16)
        plt.xticks(X_labels["int"],X_labels["label"]) #, fontsize = 13)
        plt.yticks(fontsize = 13)
        plt.xlabel('Number of tiles', fontsize = 16)
        # plt.legend()
        plt.tight_layout()
        # plt.show()
        plt.savefig('plot_nb_tiles.pdf', dpi=300, transparent=True, bbox_inches='tight')

# ################################################################
# Plot: Communication amount
# ################################################################
if doPlotComm:
    # A. Prepare data
    resultsPerComm={}
    base_dict = {"nb_scenarii"  : 0,
                "avg_time"     : 0,
                "max_time"     : 0,
                "avg_power"    : 0,
                "max_power"    : 0,
                "avg_energy"   : 0,
                "max_energy"   : 0}
    comm_amounts = {"0-9%":9,
                    "10-19%":19,
                    "20-29%":29,
                    "30-39%":39,
                    "40-59%":59,
                    ">60%"  :100}
    comm_amounts_index = {"0-9%":1,
                        "10-19%":2,
                        "20-29%":3,
                        "30-39%":4,
                        "40-59%":5,
                        ">60%"  :6}

    highest_comm_rate = 0
    for scenario in data:
        for mode in ["results_CG", "results_P"]:
            for comm_amount in comm_amounts:
                highest_comm_rate = max(scenario[mode]["predicted_communication_rate"],highest_comm_rate)
                if scenario[mode]["predicted_communication_rate"] < comm_amounts[comm_amount]:
                    scenario_comm = comm_amount
                    break
            if not(scenario_comm in resultsPerComm):
                resultsPerComm[scenario_comm] = deepcopy(base_dict)

            tmp = abs(scenario[mode]["prediction_error_time"])
            resultsPerComm[scenario_comm]["avg_time"] += tmp
            resultsPerComm[scenario_comm]["max_time"] = max(resultsPerComm[scenario_comm]["max_time"], tmp)

            tmp = abs(scenario[mode]["prediction_error_power"])
            resultsPerComm[scenario_comm]["avg_power"] += tmp
            resultsPerComm[scenario_comm]["max_power"] = max(resultsPerComm[scenario_comm]["max_power"], tmp)

            tmp = abs(scenario[mode]["prediction_error_energy"])
            resultsPerComm[scenario_comm]["avg_energy"] += tmp
            resultsPerComm[scenario_comm]["max_energy"] = max(resultsPerComm[scenario_comm]["max_energy"], tmp)

            resultsPerComm[scenario_comm]["nb_scenarii"] += 1

    if bool_verbose:
        print("Highest comm. rate: " + str(highest_comm_rate))

    X_labels = {"int": [], "label": []}
    for comm_amount in resultsPerComm:
        resultsPerComm[comm_amount]["avg_time"]   = resultsPerComm[comm_amount]["avg_time"]  /resultsPerComm[comm_amount]["nb_scenarii"]
        resultsPerComm[comm_amount]["avg_power"]  = resultsPerComm[comm_amount]["avg_power"] /resultsPerComm[comm_amount]["nb_scenarii"]
        resultsPerComm[comm_amount]["avg_energy"] = resultsPerComm[comm_amount]["avg_energy"]/resultsPerComm[comm_amount]["nb_scenarii"]
        X_labels["int"].append(comm_amounts_index[comm_amount])
        X_labels["label"].append(comm_amount + '\n$M_{n}=$' + str(resultsPerComm[comm_amount]["nb_scenarii"]))
        if bool_verbose:
            print("For comm_amount = " + str(comm_amount) + ":")
            print("    - avg_time:   " + str(resultsPerComm[comm_amount]["avg_time"]))
            print("    - avg_power:  " + str(resultsPerComm[comm_amount]["avg_power"]))
            print("    - avg_energy: " + str(resultsPerComm[comm_amount]["avg_energy"]))
            print("    - max_time:   " + str(resultsPerComm[comm_amount]["max_time"]))
            print("    - max_power:  " + str(resultsPerComm[comm_amount]["max_power"]))
            print("    - max_energy: " + str(resultsPerComm[comm_amount]["max_energy"]))
            print("")

    X = {"avg_time"   : [],
        "max_time"   : [],
        "avg_power"  : [],
        "max_power"  : [],
        "avg_energy" : [],
        "max_energy" : []}

    for x in X_labels['int']:
        X["avg_time"  ].append(x - 0.3)
        X["avg_power" ].append(x - 0.2)
        X["avg_energy"].append(x - 0.1)
        X["max_time"  ].append(x + 0.1)
        X["max_power" ].append(x + 0.2)
        X["max_energy"].append(x + 0.3)

    # B. Plot data
    if doPlot:
        plt.figure(figsize=FIG_SIZE)
        plt.grid(True, color='grey', linestyle='--', axis='y', zorder=1000)

        for key in ["avg_time", "max_time", "avg_power", "max_power", "avg_energy", "max_energy"]:
            Y = []
            for comm_amount in resultsPerComm:
                Y.append(resultsPerComm[comm_amount][key])
            plt.bar (X[key], Y, label = key, edgecolor = 'black', color=Colors[key],  width = 0.1, hatch='')

        # addLabels(X, Y, Y_labels)
        plt.ylim(0,8)
        # plt.xlabel('Execution time (cycles)')
        plt.ylabel('Error (%)', fontsize = 16)
        plt.yticks(fontsize = 13)
        plt.xticks(X_labels["int"],X_labels["label"]) #, fontsize = 11)
        plt.xlabel('Communication rates', fontsize = 16)
        # plt.legend()
        plt.tight_layout()
        # plt.show()
        plt.savefig('plot_comm.pdf', dpi=300, transparent=True, bbox_inches='tight')