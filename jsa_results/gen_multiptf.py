

import json
from copy import deepcopy

PROCESSOR_FREQUENCY = 100000000

test_mappings_multiptf = [
    {'id': 6, 'id_CG': 13, 'results_P': {"measured_power": 1.1439E+00}, "results_CG":{"measured_power": 1.1310E+00}, "memory-map": [2048]},
    {'id': 6, 'id_CG': 13, 'results_P': {"measured_power": 9.9063E-01}, 'results_CG':{"measured_power": 9.9210E-01}, "memory-map": [1024]},
    {'id': 6, 'id_CG': 13, 'results_P': {"measured_power": 9.0088E-01}, 'results_CG':{"measured_power": 9.0229E-01}, "memory-map": [512]},
    {'id': 15, 'id_CG': 22, 'results_P': {"measured_power": 1.1368E+00}, "results_CG":{"measured_power": 1.1310E+00}, "memory-map": [2048]},
    {'id': 15, 'id_CG': 22, 'results_P': {"measured_power": 9.8967E-01}, 'results_CG':{"measured_power": 9.8997E-01}, "memory-map": [1024]},
    {'id': 15, 'id_CG': 22, 'results_P': {"measured_power": 8.9831E-01}, 'results_CG':{"measured_power": 9.0183E-01}, "memory-map": [512]},
    {'id': 46, 'id_CG': 52, 'results_P': {"measured_power": 1.1593E+00}, "results_CG":{"measured_power": 1.1630E+00}, "memory-map": [2048]},
    {'id': 46, 'id_CG': 52, 'results_P': {"measured_power": 1.0030E+00}, 'results_CG':{"measured_power": 1.0030E+00}, "memory-map": [1024]},
    {'id': 46, 'id_CG': 52, 'results_P': {"measured_power": 9.0722E-01}, 'results_CG':{"measured_power": 9.0537E-01}, "memory-map": [512]},
    {'id': 4, 'id_CG': 11, 'results_P': {"measured_power": 9.4060E-01}, 'results_CG':{"measured_power": 9.1519E-01}, "memory-map": [64, 64, 64]},
    {'id': 18, 'id_CG': 25, 'results_P': {"measured_power": 9.4330E-01}, 'results_CG':{"measured_power": 9.3922E-01}, "memory-map": [64, 64, 64]},
    {'id': 47, 'id_CG': 53, 'results_P': {"measured_power": 1.1814E+00}, 'results_CG':{"measured_power": 1.0353E+00}, "memory-map": [1024, 512, 512, 256, 256]},
    {'id': 30, 'results_P':{"measured_power": 8.9067E-01},  "memory-map": [64, 64], 'id_CG': 37, 'results_CG':{"measured_power": 8.9558E-01}}
]

RESULTS_JSON_FILE = "tested_mappings.json"
with open(RESULTS_JSON_FILE, 'r') as json_file:
    test_mappings = json.load(json_file)

new_scenarii = []

for mapping_multiptf in test_mappings_multiptf:
    for mapping in test_mappings:
        if mapping_multiptf["id"] == mapping["id"]:
            mapping_multiptf["application"] = mapping["application"]
            mapping_multiptf["mapping"] = mapping["mapping"]
            mapping_multiptf["results_CG"]["measured_time"] = mapping["results_CG"]["measured_time"]
            mapping_multiptf["results_P" ]["measured_time"]  = mapping["results_P"]["measured_time"]
            mapping_multiptf["results_P" ]["measured_energy"]  = mapping_multiptf["results_P"]["measured_power"]*mapping["results_P"]["measured_time"]*(1/PROCESSOR_FREQUENCY)*1000
            #*1000 to show in mJ instead of J
            mapping_multiptf["results_CG"]["measured_energy"]  = mapping_multiptf["results_CG"]["measured_power"]*mapping["results_CG"]["measured_time"]*(1/PROCESSOR_FREQUENCY)*1000
            #*1000 to show in mJ instead of J
            new_scenarii.append(deepcopy(mapping_multiptf))
            break

# Save data
with open('./tested_mappings_multiptf.json', 'w') as fout:
    json.dump(new_scenarii, fout, sort_keys=True, indent=4)