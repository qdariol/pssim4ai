import json
import copy
import os
from copy import deepcopy

if False:
    with open('./results_multiptf.json', 'r') as json_file:
        data = json.load(json_file)

    data_per_ptf = {}
    base_dict = {
        "counter" : 0,
        "max_error_energy" : 0,
        "max_error_time" : 0,
        "max_error_power" : 0,
        "avg_error_energy" : 0,
        "avg_error_time" : 0,
        "avg_error_power" : 0
    }
    for mapping in data:
        ptf = str(mapping["memory_map"])
        if not(ptf in data_per_ptf):
            data_per_ptf[ptf] = deepcopy(base_dict)

        data_per_ptf[ptf]["counter"] += 1
        # Power
        data_per_ptf[ptf]["avg_error_power"]  += abs(mapping["error_power"])
        data_per_ptf[ptf]["max_error_power"]  =  max(data_per_ptf[ptf]["max_error_power"],abs(mapping["error_power"]))
        # Energy
        data_per_ptf[ptf]["avg_error_energy"] += abs(mapping["error_energy"])
        data_per_ptf[ptf]["max_error_energy"] =  max(data_per_ptf[ptf]["max_error_energy"],abs(mapping["error_energy"]))

    for ptf in data_per_ptf:
        data_per_ptf[ptf]["avg_error_power"]  = data_per_ptf[ptf]["avg_error_power"] / data_per_ptf[ptf]["counter"]
        data_per_ptf[ptf]["avg_error_energy"] = data_per_ptf[ptf]["avg_error_energy"] / data_per_ptf[ptf]["counter"]
        print("PTF: " + ptf)
        print(" - scenario_count: " + str(data_per_ptf[ptf]["counter"]))
        print(" - avg_error_power: " + '{0:.2f}'.format(data_per_ptf[ptf]["avg_error_power"])+ ' %')
        print(" - avg_error_energy: " + '{0:.2f}'.format(data_per_ptf[ptf]["avg_error_energy"])+ ' %')
        print(" - max_error_power: " + '{0:.2f}'.format(data_per_ptf[ptf]["max_error_power"])+ ' %')
        print(" - max_error_energy: " + '{0:.2f}'.format(data_per_ptf[ptf]["max_error_energy"])+ ' %')
        print("")

if True:
    p_tile_delta = 0.00011636 # Contribution dependent on the memory size
    p_tile_fix =  0.031 # Contribution fixed per tile
    p_static_fix = 0.678 # Contribution fixed per platform
    contribution_cg_static = 0.033

    platforms = [
        {
            "memory_tab": [1024, 256, 256, 256, 256, 256, 256],
            "measured_static_power": 1.2450E+00
        },
        {
            "memory_tab": [512, 256, 256, 128, 128],
            "measured_static_power": 1.0096E+00
        },
        {
            "memory_tab": [64, 64, 64],
            "measured_static_power": 8.5483E-01
        },
        {
            "memory_tab": [64, 64],
            "measured_static_power": 8.2708E-01
        },
        {
            "memory_tab": [2048],
            "measured_static_power": 9.9594E-01
        },
        {
            "memory_tab": [1024],
            "measured_static_power": 8.9907E-01
        },
        {
            "memory_tab": [512],
            "measured_static_power": 8.1953E-01
        }
]

    def GetStaticConsumption(platform):
        result = p_static_fix + len(platform)*p_tile_fix
        for n in range(len(platform)):
            result += p_tile_delta*platform[n]
        result += contribution_cg_static
        return result

    for platform in platforms:
        platform["predicted_static_power"] = GetStaticConsumption(platform["memory_tab"])
        platform["error_static_power"] = ((platform["predicted_static_power"] - platform["measured_static_power"]) / platform["measured_static_power"])*100

    # Save data
    with open('./results_static_multiptf.json', 'w') as fout:
        json.dump(platforms, fout, sort_keys=True, indent=4)