#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import matplotlib.cm as cm
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import basic_func
import plotly.express as px
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as colors


# Define folder names
folders = ['SobolInformation_Hehe_oxic', 'SobolInformation_Tugou_oxic', 'SobolInformation_Hehe_anoxic','SobolInformation_Tugou_anoxic',  'SobolInformation_Noedler']
names= ['oxic-H','oxic-T', 'anoxic-H', 'anoxic-T','anoxic-NDL']

# Determine script directory
script_dir = os.path.dirname(os.path.abspath(__file__))


# Define color map and fixed colors for datasets
datasets = ['K1', 'K2','K5', 'K3', 'K4',  'K6', 'K7','KL_NO3','K8', 'KL_DOC', 'K9', 'K10', 'K11', 'K12', 'K13', 'K14', 'Kl_NO3','K15','K16']
cma = cm.tab20
color_mapping = {name: cma(i / len(datasets)) for i, name in enumerate(datasets)}

# Track legend inclusion globally across subplots
legend_included = {name: False for name in datasets}
legend_rename = {
    'Kl_NO3': 'Kl`_CH$_2$O'    # Add more renames as needed
}
K1_values = []
K1_conf_values = []
    # Extract the last values for all datasets

last_values = {name: [] for name in datasets}

# Loop over each folder
for i, folder in enumerate(folders):
    cdir = os.path.join(script_dir, folder)
    os.chdir(cdir)

    # Read data
    df_ST = pd.read_csv('df_ST.csv')
    df_ST_conf = pd.read_csv('df_ST_conf.csv')
    if '68' in df_ST.columns:
        df_ST = df_ST.drop(columns=['68'])
        df_ST_conf = df_ST_conf.drop(columns=['68'])
    df_ST = df_ST.drop_duplicates(subset=['names'])
    print(df_ST[df_ST['names'] == 'K14'])

    # Loop through each dataset to extract the last value
    for dataset_name in datasets:
        # Filter rows for the dataset
            # Print out the rows to debug

        dataset_row = df_ST[df_ST['names'] == dataset_name]
        #conf_dataset_row = df_ST_conf[df_ST_conf['names'] == dataset_name]
        if not dataset_row.empty:  # Check if the dataset exists in the file
            last_value = dataset_row.iloc[-1, -1]  # Last row, last column
            last_values[dataset_name].append(last_value)
        else:
            last_values[dataset_name].append(None)  # Append None if the dataset is missing

normalized_values = {}
for dataset_name, values in last_values.items():
    # Filter out None values for normalization
    valid_values = [v for v in values if v is not None]

    if valid_values:  # Check if there are valid values
        min_value = min(valid_values)
        max_value = max(valid_values)
        if max_value > min_value:  # Perform Min-Max Normalization
            normalized = [(v - min_value) / (max_value - min_value) if v is not None else None for v in values]
        else:
            normalized = [0 if v is not None else None for v in values]  # Normalize to 0 if all values are the same
    else:
        normalized = [None] * len(values)  # No valid values, keep None

    normalized_values[dataset_name] = normalized




# Flatten the list of all last values and filter out None values to find global min and max
all_last_values = [v for values in last_values.values() for v in values if v is not None]

# Calculate global minimum and maximum
if all_last_values:  # Ensure there are values to normalize
    global_min = min(all_last_values)
    global_max = max(all_last_values)

    # Avoid division by zero if all values are the same
    if global_max > global_min:
        normalized_values = {
            dataset_name: [
                (v - global_min) / (global_max - global_min) if v is not None else None
                for v in values
            ]
            for dataset_name, values in last_values.items()
        }
    else:
        # If all values are identical, normalize to 0
        normalized_values = {
            dataset_name: [0 if v is not None else None for v in values]
            for dataset_name, values in last_values.items()
        }
else:
    # If no valid values exist, set normalized values to empty or None
    normalized_values = {dataset_name: [None] * len(values) for dataset_name, values in last_values.items()}

# Print normalized values for debugging
print("\nNormalized Values Based on Global Min-Max:")
for name, values in normalized_values.items():
    print(f"{name}: {values}")


# 2. Normalized values als CSV speichern
df_normalized = pd.DataFrame(normalized_values, index=names).T
df_normalized.index.name = 'dataset'
df_normalized.to_csv(os.path.join(script_dir, 'normalized_values.csv'))
print("\nGespeichert: normalized_values.csv")
print(df_normalized)

def create_heatmap(normalized_values, x_labels, datasets, names, script_dir, file_name="03_Figure5_heatmap.png"):
    """
    Generate a heatmap for normalized Sobol indices and save it as a PNG file.

    Parameters:
    - normalized_values: dict, dictionary with dataset names as keys and lists of normalized values as values.
    - x_labels: dict, mapping of parameter names to LaTeX-formatted labels.
    - datasets: list, ordered list of dataset names to control column order.
    - names: list, names for heatmap rows (e.g., "Value 1", "Value 2").
    - script_dir: str, base directory where the output file will be saved.
    - file_name: str, name of the output heatmap image file (default: "heatmap.png").
    """
    # Prepare data for the heatmap
    heatmap_data = []
    for dataset_name, values in normalized_values.items():
        for i, value in enumerate(values):
            if value is not None:  # Exclude None values
                heatmap_data.append({'Dataset': dataset_name, 'Position': f'Value {i+1}', 'Normalized Value': value})

    df_heatmap = pd.DataFrame(heatmap_data)

    # Pivot the DataFrame to prepare for heatmap
    df_pivot = df_heatmap.pivot(index="Dataset", columns="Position", values="Normalized Value")
    df_pivot_swapped = df_pivot.T  # Transpose to swap axes
    df_pivot_swapped.index = names  # Set custom y-axis labels
    df_pivot_swapped = df_pivot_swapped[datasets]  # Reindex columns for custom order

    # Create the heatmap
    plt.figure(figsize=(10, 8))  # Adjust size if needed
    ax = sns.heatmap(
        df_pivot_swapped,
        annot=True,
        fmt='.2e',
        cmap='viridis',
        cbar_kws={'label': 'Normalized total SI'},
        linewidths=0.5,
        vmin=0,
        vmax=1,
        square=False,
        norm=colors.PowerNorm(gamma=0.15),
        annot_kws={"rotation": 90,"fontsize": 6},
    )

    # Update x-axis labels with LaTeX formatting
    # Set x-ticks and labels
    tick_positions = range(len(df_pivot_swapped.columns))
    new_x_labels = [x_labels.get(label, label) for label in df_pivot_swapped.columns]

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(new_x_labels, rotation=45, ha='center')

    # Show ticks and labels on both top and bottom
    ax.tick_params(axis='x', top=True, labeltop=True, bottom=True, labelbottom=True)


    # Y ticks
    plt.yticks(rotation=0)

    # Customize colorbar
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=6)

    # Remove x-axis label
    ax.set_xlabel('', fontsize=10, ha='center')

    # Adjust layout and save plot
    plt.subplots_adjust(left=0.3, right=0.907, top=0.40, bottom=0.11, hspace=0.2, wspace=0.2)
    output_dir = os.path.join(script_dir, 'combined_sobol_plots')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_png = os.path.join(output_dir, file_name)
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.show()

    # Print the output path for debugging purposes
    print(f"Plot saved to: {output_png}")


# Define the mapping for x-axis labels with LaTeX formatting
    'WARNING: renamed K3, K4, and K5 because of the later changing of ordering in the manuscript but not in the codes'
x_labels = {
    'K1': r'$k_{1}$',     'K2': r'$k_{2}$',     'K3': r'$k_{4}$',     'K4': r'$k_{5}$',
    'K5': r'$k_{3}$',     'K6': r'$k_{6}$',     'K7': r'$k_{7}$',     'KL_NO3': r'$k_{l, NO_3^-}$',  # Correct for KL_NO3
    'K8': r'$k_{8}$',     'KL_DOC': r'$k_{l,CH_2O}$',     'K9': r'$k_{9}$',     'K10': r'$k_{10}$',
    'K11': r'$k_{11}$',     'K12': r'$k_{12}$',     'K13': r'$k_{13}$',     'K14': r'$k_{14}$',
    'Kl_NO3': r'$k_{l\prime, CH_2O}$',  # Same for Kl_NO3
    'K15': r'$k_{15}$',     'K16': r'$k_{16}$'
}

create_heatmap(normalized_values, x_labels, datasets, names, script_dir)

