import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Exercise Lab3: Network

def calculate_snr(signal_power, noise_power):
    if noise_power > 0:
        return 10 * np.log10(signal_power / noise_power)
    else:
        return np.inf


network = Network(json_file='nodes.json')
network.connect()


path_data = []
for start_node in network.nodes.keys():
    for end_node in network.nodes.keys():
        if start_node != end_node:
            paths = network.find_paths(start_node, end_node)
            for path in paths:
                signal_info = SignalInformation(signal_power=0.001, path=path.copy())
                network.propagate(signal_info)
                snr_db = calculate_snr(signal_info.signal_power, signal_info.noise_power)
                path_str = '->'.join(path)
                path_data.append({
                    'Path': path_str,
                    'Total Latency (s)': signal_info.latency,
                    'Total Noise (W)': signal_info.noise_power,
                    'SNR (dB)': snr_db
                })


df_paths = pd.DataFrame(path_data)
print(df_paths)


network.draw()


# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file
