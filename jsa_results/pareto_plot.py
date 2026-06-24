import matplotlib as mpl
import matplotlib.pyplot as plt
import json

files = ["../run/CNN_maps_4h.json", 
         "../run/MLP1_maps_4h.json", 
         "../run/MLP2_maps_4h.json", 
         "../run/MLP3_maps_4h.json"
]

# Plot after phase 2
for file in files:  
    simu_times=[]
    simu_powers=[]
    simu_energies=[]
    simu_throughputs=[]
    simu_core_numbers=[]

    with open(file, 'r') as json_file:
        Mappings = json.load(json_file)

    for my_set in Mappings:
        print(file, ": ", len(my_set))
        for mapping in my_set:
            for mode in ["results_CG", "results_P"]:
                simu_times.append(mapping[mode]['p_e2e']/1000)
                simu_energies.append(mapping[mode]['p_energy'])

    plt.figure("")
    plt.scatter(simu_times, simu_energies, marker='o', color='gold', label='Evaluated mappings',  linewidth=0.5, edgecolor='k')
    plt.xlabel('Execution time (thousands of cycles)')
    plt.ylabel('Energy consumption (mJ)')
    plt.grid(True, color='grey', linestyle='--')
    plt.legend() # fontsize='small'
    plot_file = file.replace("../run/","").replace("_maps_4h.json","_pareto")
    plt.savefig(plot_file + ".png", dpi=300, transparent=False, bbox_inches='tight')
    plt.savefig(plot_file + ".pdf", dpi=300, transparent=False, bbox_inches='tight')
    plt.clf()