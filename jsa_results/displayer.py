import json

with open('./results_model_evaluation.json', 'r') as json_file:
    data = json.load(json_file)

print("Application ; Mapping ; Mode ; Communication % ; Timing error % ; Power error % ; Energy error %")
for mapping in data:
    for mode in ["P", "CG"]:
        mode_str = "results_" + mode
        print(mapping["application"] + " ; " + \
              str(mapping["mapping"]) + " ; " + \
              mode + " ; " + \
              '{0:.0f}'.format(mapping[mode_str]["predicted_communication_rate"]) + " ; " + \
              '{0:.2f}'.format(mapping[mode_str]["prediction_error_time"]) + " ; " + \
              '{0:.2f}'.format(mapping[mode_str]["prediction_error_power"]) + " ; " + \
              '{0:.2f}'.format(mapping[mode_str]["prediction_error_energy"]) + " ; "
              )