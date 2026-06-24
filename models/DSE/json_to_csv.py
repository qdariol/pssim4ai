#
# File: json_to_csv.py
# Description: This python script outputs the .json databases, typically used to store mapping data
#              such as predictions vs measurements, into a .csv file.
#
# Usage: In this script, first set the environment variable DO_DSE = False/True. This variable allows
#        specifying whether the data to be dumped in .csv file should be VALIDATION (False) or DSE
#        (True) data.
#
#        Then, to use the script, run the following commands in command prompt:
#        1.  rm out.csv
#        2.  python json_to_csv.py >> out.csv
#
#        Command 1. ensures the out.csv file does not exist prior, which ensures that only the relevant
#        data will be contained in the resulting file.
#
# Author: Quentin Dariol
# License: 3-clause BSD license, Copyright 2026 - Quentin Dariol, Ralf Stemmer, Sébastien Le Nours, Sébastien Pillement,
#          Kim Grüttner, Domenik Helms - IETR UMR CNRS 6164, Nantes Université & German Aerospace Center (DLR e. V.)
#

# USER: Set the environment variable DO_DSE
DO_DSE = True

import json
import operator

if DO_DSE:
    json_file = './dse_results.json'
else:
    json_file = './result.json'

with open(json_file, 'r') as jf:
    data = json.load(jf)

if DO_DSE:
    print("APPLICATION; CLUSTERING; NB_TILES_USED; MODE; TIMING (CYCLES); POWER (W); ENERGY (uJ)") #TIMING ERROR ANALYTICAL, POWER ERROR ANALYTICAL, ENERGY ERROR ANALYTICAL
    for element in data:
        print(  element['application'],
                element['clustering'],
                element['tiles_used'],
                element['mode'],
                element['execution_time'],
                element['p_power'],
                '{0:.3f}'.format(element['execution_time']*element['p_power']*0.00001), #execution time in cycles @100MHz => 10ns period. Conversion to mJ => *0.00001
                sep='; '
        )
else:
    print("MAPPING_ID; APPLICATION; CLUSTERING; MAPPING; POWER MNG; COMP RATE; RDWR RATE; WAIT RATE; TIMING ERROR SIMULATION; POWER ERROR SIMULATION; ENERGY ERROR SIMULATION") #TIMING ERROR ANALYTICAL, POWER ERROR ANALYTICAL, ENERGY ERROR ANALYTICAL
    for element in data:
        if 'clustering' in element:
            tmp = element['clustering']
        else:
            tmp = 0
        print(  element['mapping_index'],
                element['manuscript_application'],
                tmp,
                element['mapping'],
                element['mode'],
                '{0:.0f}'.format(element['computation_rate']),
                '{0:.0f}'.format(element['rdwr_rate']),
                '{0:.0f}'.format(element['wait_rate']),
                '{0:.2f}'.format(element["error_e2e"]),
                '{0:.2f}'.format(element["error_power"]),
                '{0:.2f}'.format(element["error_energy_e2e"]),
                sep='; '
        )
