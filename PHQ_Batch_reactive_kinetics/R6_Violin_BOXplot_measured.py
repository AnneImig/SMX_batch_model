import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import configparser
import sys
import pandas as pd

###########################################################################################################################
# Configuration and Setup
###########################################################################################################################

# Set LaTeX rendering for text
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

# Setup directories
plot_folder = os.path.join(script_dir, "plots")
os.makedirs(plot_folder, exist_ok=True)

# Read Excel file
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
meas_dir= os.path.join(parent_dir,'measurements')
excel_file_path = os.path.join(meas_dir,'Ma_2021_measurements.xlsx')

# Configuration flags

###########################################################################################################################
# Load Data
###########################################################################################################################

def load_data(excel_file_path):
    """Load data from Excel file."""
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel file not found: {excel_file_path}")
    
    df_anoxic = pd.read_excel(excel_file_path, sheet_name=1)
    df_anoxic.reset_index(drop=True, inplace=True)
    
    df_oxic = pd.read_excel(excel_file_path, sheet_name=0)
    df_oxic.reset_index(drop=True, inplace=True)
    
    return df_anoxic, df_oxic


def extract_metabolite_data(df_anoxic, df_oxic, row_values):
    """Extract metabolite concentration data from DataFrames."""
    # Anoxic data
    SMX_anoxic = df_anoxic.iloc[row_values, [3, 9, 15]]
    DES_anoxic = df_anoxic.iloc[row_values, [6, 12, 18]]
    Nitro_anoxic = df_anoxic.iloc[row_values, [7, 13, 19]]
    SMZ_anoxic = df_anoxic.iloc[row_values, [4, 10, 16]]
    SDZ_anoxic = df_anoxic.iloc[row_values, [2, 8, 14]]
    Ammet_anoxic = df_anoxic.iloc[row_values, [5, 11, 17]]
    
    # Oxic data
    SMX_oxic = df_oxic.iloc[row_values, [3, 9, 15, 21]]
    DES_oxic = df_oxic.iloc[row_values, [6, 12, 18, 24]]
    Nitro_oxic = df_oxic.iloc[row_values, [7, 13, 19, 25]]
    SMZ_oxic = df_oxic.iloc[row_values, [4, 10, 16, 22]]
    SDZ_oxic = df_oxic.iloc[row_values, [2, 8, 14, 20]]
    Ammet_oxic = df_oxic.iloc[row_values, [5, 11, 17, 23]]
    
    # Standardize column names
    DES_anoxic.columns = SMX_anoxic.columns
    Ammet_anoxic.columns = SMX_anoxic.columns
    Nitro_anoxic.columns = SMX_anoxic.columns
    
    DES_oxic.columns = SMX_oxic.columns
    Ammet_oxic.columns = SMX_oxic.columns
    Nitro_oxic.columns = SMX_oxic.columns
    
    # Calculate undetected (sum of known metabolites)
    SMX_init = 3.9482e-08
    Sum_anoxic = SMX_anoxic + DES_anoxic + Nitro_anoxic + Ammet_anoxic
    Undet_anoxic = SMX_init - Sum_anoxic
    
    Sum_oxic = SMX_oxic + DES_oxic + Nitro_oxic + Ammet_oxic
    Undet_oxic = SMX_init - Sum_oxic
    
    return {
        'anoxic': [SMX_anoxic, DES_anoxic, Nitro_anoxic, Ammet_anoxic, Undet_anoxic],
        'oxic': [SMX_oxic, DES_oxic, Nitro_oxic, Ammet_oxic, Undet_oxic]
    }


###########################################################################################################################
# Plotting Functions
###########################################################################################################################

def plot_1_row_violin_subplots(anoxic_dataframes, oxic_dataframes, titles, filename, plottitle):
    """
    Plot violin plots in a single row comparing anoxic and oxic conditions.
    """
    num_plots = len(anoxic_dataframes)
    fig, axes = plt.subplots(nrows=1, ncols=num_plots, figsize=(14, 6))
    
    SMX_init = 3.95e-8
    
    for i in range(num_plots):
        anoxic_df = anoxic_dataframes[i]
        oxic_df = oxic_dataframes[i]
        title = titles[i]
        
        # Plot anoxic data
        parts_anoxic = axes[i].violinplot(
            anoxic_df.values,
            positions=np.arange(len(anoxic_df.columns)) - 0.2,
            widths=0.3,
            showmedians=True
        )
        for pc in parts_anoxic['bodies']:
            pc.set_facecolor('lightblue')
            pc.set_edgecolor('black')
        
        # Plot oxic data
        parts_oxic = axes[i].violinplot(
            oxic_df.values,
            positions=np.arange(len(oxic_df.columns)) + 0.2,
            widths=0.3,
            showmedians=True
        )
        for pc in parts_oxic['bodies']:
            pc.set_facecolor('orange')
            pc.set_edgecolor('black')
        
        # Add input marker on first plot only
        if i == 0:
            axes[i].scatter(
                x=[0],
                y=[SMX_init],
                color='black',
                label='Input',
                marker='x',
                s=200,
                zorder=5
            )
            axes[i].annotate(
                "Input",
                xy=(0, SMX_init),
                xytext=(0.2, SMX_init * 0.95),
                fontsize=9,
                color='black'
            )
        
        axes[i].set_title(title, fontsize=10, loc='center', pad=10)
        axes[i].set_xticks(np.arange(len(oxic_df.columns)))
        axes[i].set_xticklabels([1, 15, 27, 70])
        axes[i].set_xlabel('Time [d]')
        
        if i == 0:
            axes[i].set_ylabel('C [mol/L]')
    
    # Create legend
    anoxic_patch = mpatches.Patch(color='lightblue', label='Anoxic')
    oxic_patch = mpatches.Patch(color='orange', label='Oxic')
    axes[-1].legend(
        handles=[anoxic_patch, oxic_patch],
        loc='upper left',
        fontsize=9,
        markerscale=1.5,
        labelspacing=0.5
    )
    
    fig.subplots_adjust(wspace=0.3)
    save_path = os.path.join(plot_folder, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


###########################################################################################################################
# Main Function
###########################################################################################################################

def main():
    """Main execution function."""
    
    # Load data
    print("Loading data from Excel file...")
    df_anoxic, df_oxic = load_data(excel_file_path)
    
    # Select rows based on configuration

    row_paper = [0, 1, 10, 11]
    print("Using Hehe and Tugou sites")
    metabolite_data = extract_metabolite_data(df_anoxic, df_oxic, row_paper)

    # Extract data
    anoxic_data = metabolite_data['anoxic']
    oxic_data = metabolite_data['oxic']
    titles = ['SMX', 'DeA-SMX', 'Nitro-SMX', 'AmMet', 'Undetected']
    
    # Generate plots
    print("Generating plots...")
    plot_1_row_violin_subplots(
        anoxic_data,
        oxic_data,
        titles,
        'R6_FigS1_Violinplot_measured_row.png',
        'Metabolite Distribution'
    )
    
    
    print("All plots generated successfully!")


if __name__ == '__main__':
    main()