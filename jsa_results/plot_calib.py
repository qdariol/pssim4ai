import matplotlib.pyplot as plt

FIG_SIZE = (5,3)
FONT_SIZE = 16

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
Colors = {"Computation": "forestgreen", # "#4f7e41ff",
        "Accessing shared memory": "royalblue", #"#4d6eb4ff",
        "Clock gated": "gold" # "#cfd148ff",
        }

plt.figure(figsize=FIG_SIZE)
plt.grid(True, color='grey', linestyle='--', axis='both', zorder=1000)
for key in Y:
    plt.scatter(X, Y[key], label = key, edgecolor = 'black', color=Colors[key])
for key in Y_model:
    plt.plot(X, [Y_model[key](X[x]) for x in X], label = key + " model", ls = '--', color=Colors[key])
plt.ylabel('Power consumption (W)', fontsize = 15)
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

# ###############################################
# ###############################################
# 3. Xilinx Power Estimator of tile
# ###############################################
# ###############################################