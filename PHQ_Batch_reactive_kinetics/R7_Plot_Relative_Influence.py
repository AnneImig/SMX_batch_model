import numpy as np
import matplotlib.pyplot as plt
import os
import configparser
import sys
import pandas as pd
import csv

###########################################################################################################################
# Configuration and Setup
###########################################################################################################################

plt.rcParams.update({
    "font.serif": ["Arial"],
    "font.size": 12
})

script_dir = os.path.dirname(os.path.abspath(__file__))

# Read configuration file
if len(sys.argv) > 1:
    configfn = sys.argv[1]
else:
    configfn = os.path.join(script_dir, "Controle_file.conf")

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(configfn)

plot_folder = os.path.join(script_dir, "plots")
os.makedirs(plot_folder, exist_ok=True)

###########################################################################################################################
# Data Loading
###########################################################################################################################

def load_simulation_data(filename):
    """Load simulation results from .sel file."""
    filepath = os.path.join(script_dir, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_csv(filepath, delimiter='\t')


def load_all_datasets():
    """Load all simulation datasets."""
    datasets = {
        'HO': load_simulation_data("output/Hehe_oxic_results.sel"),
        'TO': load_simulation_data("output/Tugou_oxic_results.sel"),
        'HA': load_simulation_data("output/Hehe_anoxic_results.sel"),
        'TA': load_simulation_data("output/Tugou_anoxic_results.sel"),
        'NDL': load_simulation_data("output/NDL_Results.sel"),
    }
    return datasets


###########################################################################################################################
# Data Processing
###########################################################################################################################

def calculate_norm_influence_portions(batch_dataset):
    """
    Calculate normalized biotically mediated and co-metabolic influence portions.
    
    Args:
        batch_dataset (pd.DataFrame): Input dataset with rate constants
        
    Returns:
        tuple: (BM_SMX, BM_Nit, BM_DeA, CoM_SMX, CoM_Nit, CoM_DeA, DOC_SMX)
    """
    
    # SMX fate calculation
    # Biotically mediated: K9, K10, K12, K13
    BM_SMX_cols = batch_dataset.iloc[:, [34, 43, 46, 38]]
    
    # Co-metabolic: K8, K11, K14, K15, K16 (adjust for missing column)
    CoM_SMX_cols = batch_dataset.iloc[:, [32, 39, 49, 52]]
    
    # DOC dependent
    DOC_SMX = batch_dataset.iloc[:, 31]
    
    # Normalize SMX
    sum_SMX = BM_SMX_cols.sum(axis=1) + CoM_SMX_cols.sum(axis=1)
    BM_norm_SMX = (BM_SMX_cols.sum(axis=1) / sum_SMX) * 100
    CoM_norm_SMX = (CoM_SMX_cols.sum(axis=1) / sum_SMX) * 100
    DOC_norm_SMX = (DOC_SMX / sum_SMX) * 100
    
    # DeA-SMX fate calculation
    # Biotically mediated: K10, K12
    BM_DeA_cols = batch_dataset.iloc[:, [43, 46]]
    # Co-metabolic: K11, K14
    CoM_DeA_cols = batch_dataset.iloc[:, [32, 39]]
    
    sum_DeA = BM_DeA_cols.sum(axis=1) + CoM_DeA_cols.sum(axis=1)
    BM_norm_DeA = (BM_DeA_cols.sum(axis=1) / sum_DeA) * 100
    CoM_norm_DeA = (CoM_DeA_cols.sum(axis=1) / sum_DeA) * 100
    
    # Nit-SMX fate calculation
    # Biotically mediated: K12, K38
    BM_Nit_cols = batch_dataset.iloc[:, [46, 38]]
    # Co-metabolic: K9 (K34)
    CoM_Nit_cols = batch_dataset.iloc[:, [34]]
    
    sum_Nit = BM_Nit_cols.sum(axis=1) + CoM_Nit_cols.sum(axis=1)
    BM_norm_Nit = (BM_Nit_cols.sum(axis=1) / sum_Nit) * 100
    CoM_norm_Nit = (CoM_Nit_cols.sum(axis=1) / sum_Nit) * 100
    
    return (BM_norm_SMX, BM_norm_Nit, BM_norm_DeA,
            CoM_norm_SMX, CoM_norm_Nit, CoM_norm_DeA,
            DOC_norm_SMX)


###########################################################################################################################
# Plotting Functions
###########################################################################################################################

def plot_relative_influence(datasets, filename):
    """
    Plot relative influence of biotically mediated and co-metabolic processes.
    
    Args:
        datasets (dict): Dictionary of loaded simulation datasets
        filename (str): Output filename for the plot
    """
    
    # Calculate influence portions for all datasets
    influence_data = {}
    for key, dataset in datasets.items():
        influence_data[key] = calculate_norm_influence_portions(dataset)
    
    # Extract data
    site_order = ['HO', 'TO', 'HA', 'TA', 'NDL']
    site_labels = ['Oxic-H', 'Oxic-T', 'Anoxic-H', 'Anoxic-T', 'Anoxic-NDL']
    
    # Color scheme
    colors_smx = {'BM': 'lightgrey', 'CoM': 'black', 'DOC': 'darkgrey'}
    colors_metabolites = {'BM': 'lightgrey', 'CoM': 'black'}
    
    # Create figure
    fig, axes = plt.subplots(3, 5, figsize=(13, 8))
    
    # Row 0: SMX fate
    for col_idx, site in enumerate(site_order):
        dataset = datasets[site]
        time = dataset.iloc[:, 0]
        BM, _, _, CoM, _, _, DOC = influence_data[site]
        
        axes[0, col_idx].stackplot(time, BM, CoM, DOC,
                                   colors=[colors_smx['BM'], colors_smx['CoM'], colors_smx['DOC']])
        if col_idx == 0:
            axes[0, col_idx].set_ylabel('SMX fate [%]', fontsize=10)
        axes[0, col_idx].set_xlabel('Time [d]', fontsize=10)
        axes[0, col_idx].set_ylim(0, 100)
        axes[0, col_idx].margins(x=0)
        # Add title on top of first row
        axes[0, col_idx].set_title(site_labels[col_idx], fontsize=11, fontweight='bold')
    

    # Row 1: Nit-SMX fate
    for col_idx, site in enumerate(site_order):
        dataset = datasets[site]
        time = dataset.iloc[:, 0]
        _, BM_Nit, _, _, CoM_Nit, _, _ = influence_data[site]
        
        axes[1, col_idx].stackplot(time, BM_Nit, CoM_Nit,
                                   colors=[colors_metabolites['BM'], colors_metabolites['CoM']])
        if col_idx == 0:
            axes[1, col_idx].set_ylabel('Nit-SMX fate [%]', fontsize=10)
        axes[1, col_idx].set_ylim(0, 100)
        axes[1, col_idx].margins(x=0)
    
    # Row 2: DeA-SMX fate
    for col_idx, site in enumerate(site_order):
        dataset = datasets[site]
        time = dataset.iloc[:, 0]
        _, _, BM_DeA, _, _, CoM_DeA, _ = influence_data[site]
        
        axes[2, col_idx].stackplot(time, BM_DeA, CoM_DeA,
                                   colors=[colors_metabolites['BM'], colors_metabolites['CoM']])
        if col_idx == 0:
            axes[2, col_idx].set_ylabel('DeA-SMX fate [%]', fontsize=10)
        axes[2, col_idx].set_xlabel('Time [d]', fontsize=10)
        axes[2, col_idx].set_ylim(0, 100)
        axes[2, col_idx].margins(x=0)
    
    # Set x-axis limits based on site type
    x_limits = {'HO': 72, 'TO': 72, 'HA': 30, 'TA': 30, 'NDL': 93}
    for col_idx, site in enumerate(site_order):
        for row_idx in range(3):
            axes[row_idx, col_idx].set_xlim(0, x_limits[site])
    
    # Layout and save
    plt.subplots_adjust(hspace=0.25, wspace=0.3)
    save_path = os.path.join(plot_folder, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


###########################################################################################################################
# Data Export
###########################################################################################################################

def export_influence_to_csv(datasets, filename):
    """
    Export calculated influence portions to CSV file.
    
    Args:
        datasets (dict): Dictionary of loaded simulation datasets
        filename (str): Output CSV filename
    """
    
    filepath = os.path.join(script_dir, filename)
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(['Site', 'Time', 'BM_SMX [%]', 'CoM_SMX [%]', 'DOC_SMX [%]',
                        'BM_Nit [%]', 'CoM_Nit [%]',
                        'BM_DeA [%]', 'CoM_DeA [%]'])
        
        # Write data for each site
        for site, dataset in datasets.items():
            influence = calculate_norm_influence_portions(dataset)
            BM_SMX, BM_Nit, BM_DeA, CoM_SMX, CoM_Nit, CoM_DeA, DOC_SMX = influence
            time = dataset.iloc[:, 0]
            
            for i in range(len(time)):
                writer.writerow([
                    site,
                    time.iloc[i],
                    BM_SMX.iloc[i],
                    CoM_SMX.iloc[i],
                    DOC_SMX.iloc[i],
                    BM_Nit.iloc[i],
                    CoM_Nit.iloc[i],
                    BM_DeA.iloc[i],
                    CoM_DeA.iloc[i]
                ])
    
    print(f"Influence data exported to: {filepath}")


###########################################################################################################################
# Main Execution
###########################################################################################################################

def main():
    """Main execution function."""
    
    print("Loading simulation data...")
    datasets = load_all_datasets()
    
    print("Generating relative influence plot...")
    plot_relative_influence(datasets, 'R7_Fig7_relativeInf.png')
    
    print("Exporting influence data to CSV...")
    export_influence_to_csv(datasets, 'relative_influence_data.csv')
    
    print("All tasks completed successfully!")


if __name__ == '__main__':
    main()
