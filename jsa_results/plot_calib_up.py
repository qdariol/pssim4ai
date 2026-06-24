import matplotlib.pyplot as plt

FIG_SIZE = (5,3)
FONT_SIZE = 16

Colors = {"Computation": "forestgreen", # "#4f7e41ff",
        "Accessing shared memory": "royalblue", #"#4d6eb4ff",
        "Clock gated": "gold", # "#cfd148ff",
        "MicroBlaze": "teal",
        "Private memory interface": "firebrick",
        "MicroBlaze + Private memory interface": "black",
        }

def modelSM(x):
    if x == 0:
        return 1.227
    else:
        return 1.227 + 0.060

# ###############################################
# ###############################################
# 1. Tiles enabled progressively together.
# ###############################################
# ###############################################

X = [0, 1, 2, 3, 4, 5, 6, 7]
Y = {"Computation": [1.217, 1.334, 1.390, 1.442, 1.500, 1.581, 1.629, 1.684],
    #  "Computation_dev": [0.006, 0.005, 0.006, 0.007, 0.006, 0.007, 0.006, 0.006],
    "Accessing shared memory": [1.241, 1.318, 1.357, 1.355, 1.366, 1.360, 1.346, 1.328],
    #  "sharedmem_dev": [0.007, 0.006, 0.008, 0.007, 0.007, 0.007, 0.008, 0.007],
    "Clock gated": [1.206, 1.087, 1.036, 0.987, 0.939, 0.890, 0.847, 0.794]
    #  "clockgating_dev": [0.007, 0.007, 0.006, 0.007, 0.006, 0.006, 0.005, 0.006]
}
Y_model = {"Computation": lambda x: 1.227 + 0.058*x,
            "Accessing shared memory": lambda x: modelSM(x),
            "Clock gated": lambda x: 1.227 - 0.058*x,
            }

plt.figure(figsize=FIG_SIZE)
plt.grid(True, color='grey', linestyle='--', axis='both', zorder=1000)
for key in Y:
    plt.scatter(X, Y[key], label = key, edgecolor = 'black', color=Colors[key])
for key in Y_model:
    plt.plot(X, [Y_model[key](x) for x in X], label = key + " model", ls = '--', color=Colors[key])
plt.ylabel('Power consumption (W)', fontsize = 15, loc="top")
plt.xlabel('Number of tiles enabled', fontsize = 15)
plt.yticks(fontsize = 13)
plt.xticks(fontsize = 13)
# plt.legend(loc='upper center', framealpha=0.5) #"fontsize="small")
plt.tight_layout()
# plt.show()
plt.savefig('calibPlot2.pdf') #, dpi=300, transparent=True, bbox_inches='tight')

# ###############################################
# ###############################################
# 2. Individual tiles
# ###############################################
# ###############################################

X = [0, 1, 2, 3, 4, 5, 6, 7]
X_labels = ["None", "1", "2", "3", "4", "5", "6", "7"]
X_tiles_enabled = [0, 1, 1, 1, 1, 1, 1, 1]
Y = {"Computation": [1.217, 1.323, 1.273, 1.276, 1.280, 1.278, 1.281, 1.288],
    "Accessing shared memory": [1.241, 1.321, 1.280, 1.283, 1.281, 1.290, 1.287, 1.289],
    "Clock gated": [1.206, 1.087, 1.155, 1.158, 1.158, 1.157, 1.163, 1.153]
}
Y_model = {"Computation": lambda x: 1.227 + 0.058*x,
            "Accessing shared memory": lambda x: modelSM(x),
            "Clock gated": lambda x: 1.227 - 0.058*x,
            }

plt.figure(figsize=FIG_SIZE)
plt.grid(True, color='grey', linestyle='--', axis='both', zorder=1000)
for key in Y:
    plt.scatter(X, Y[key], label = key, edgecolor = 'black', color=Colors[key])
for key in Y_model:
    plt.plot(X, [Y_model[key](x) for x in X_tiles_enabled], label='_nolegend_', ls = '--', color=Colors[key]) # label = key + " model",
plt.ylabel('Power consumption (W)', fontsize = 15, loc="top")
plt.xlabel('Individual tile enabled', fontsize = 15)
plt.ylim(1,1.35)
plt.yticks(fontsize = 13)
plt.xticks(X, X_labels, fontsize = 13)

plt.legend(framealpha=0.5, fontsize=10)
plt.tight_layout()
# plt.show()
plt.savefig('calibPlot1.pdf') #, dpi=300, transparent=True, bbox_inches='tight')

# ###############################################
# ###############################################
# 3. Xilinx Power Estimator of tile
# ###############################################
# ###############################################

X = [8,16,32,64,128,256,512,1024,2048]
Y = {
    "MicroBlaze": [0.024, 0.024, 0.025, 0.025, 0.027, 0.029, 0.036, 0.057, 0.076],
    "Private memory interface": [0.001, 0.001, 0.003, 0.005, 0.01, 0.02, 0.04, 0.092, 0.183],
    "MicroBlaze + Private memory interface": [0.025, 0.025, 0.028, 0.03, 0.037, 0.049, 0.076, 0.149, 0.259]
}

plt.figure(figsize=FIG_SIZE)
plt.grid(True, color='grey', linestyle='--', axis='both', zorder=1000)
for key in Y:
    plt.plot(X, Y[key], linestyle='--', marker='o', label = key, markeredgecolor = 'black', color=Colors[key])
plt.ylabel('Power consumption (W)', fontsize = 15, loc="top")
plt.xlabel('Private memory size (kB)', fontsize = 15)
plt.yticks(fontsize = 13)
plt.xticks(fontsize = 12, rotation=30)
plt.legend(loc='upper center', framealpha=0.5) #"fontsize="small")
plt.tight_layout()
plt.savefig('calibPlot3.pdf')
