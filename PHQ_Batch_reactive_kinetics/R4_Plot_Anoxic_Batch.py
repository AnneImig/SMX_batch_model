import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os 
import configparser
from datetime import datetime 
import sys
import pandas as pd 

###########################################################################################################################
'''
Create graphs of the measured and modelled data from anoxic batch experiments
Updated with proper chemical formula notation and simplified configuration
'''
###########################################################################################################################
# Set LaTeX rendering for text
plt.rcParams.update({
    "font.serif": ["Arial"],
    "font.size": 12
})

script_dir = os.path.dirname(os.path.abspath(__file__))

# read all information from configfile
if len(sys.argv) > 1:
    configfn = sys.argv[1]
else:
    configfn = os.path.join(script_dir,"Controle_file.conf")

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(configfn)

SELFILE = config.get("system", "SELFILE", fallback=True)
sel_file_path = os.path.join(script_dir, SELFILE)
output = pd.read_csv(sel_file_path, delimiter='\t')

input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")
plot_folder = os.path.join(script_dir, "plots")
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(plot_folder, exist_ok=True)

N_COL = config.get("column", "col_no", fallback=4)

# Read configuration flags
OXIC = config.getboolean("batch", "OXIC", fallback=True)
ANOXIC = config.getboolean("batch", "ANOXIC", fallback=True)
HEHE_BED = config.getboolean("site", "HEHE_BED", fallback=True)
TUGOU_BANK = config.getboolean("site", "TUGOU_BANK", fallback=True)
NOEDLER = config.getboolean("validation", "NOEDLER", fallback=False)

# Load measurement data
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
meas_dir = os.path.join(parent_dir, 'measurements')
excel_file_path = os.path.join(meas_dir, 'Ma_2021_measurements.xlsx')

# Measured data points
SMX_x_anoxic = [0, 2, 14, 28]
anoxic_specific_points_x = [2, 14, 28]
specific_points_x = [2, 14, 28, 70]
Time_3x_Nspecies = [0, 15, 28]

if os.path.exists(excel_file_path): 
    df = pd.read_excel(excel_file_path, sheet_name=1)
    df.reset_index(drop=True, inplace=True)
    print("DataFrame after reading ANOXIC excel file:")
    print(df.head())
    df_N = pd.read_excel(excel_file_path, sheet_name=2)
    print(df_N.head())

def get_measured_values(average, std, av_N, std_N):
    global NH4_3, NO2_3, NO3_3, NH4_3_std, NO2_3_std, NO3_3_std
    global DES_anoxic_specific_points_y, std_deviations_Des, Nitro_anoxic_specific_points_y
    global std_deviations_Nitro, smx_measured_N_batch, SMX_std_deviations_N
    global Ammet_oxic_y, std_deviations_Ammet
    global SDZ, SDZ_std, SMZ, SMZ_std
    
    NH4_3 = df_N.iloc[av_N, [2, 5, 8]].tolist()
    print(NH4_3)
    NH4_3_std = df_N.iloc[std_N, [2, 5, 8]].tolist()
    print(NH4_3_std)
    NO2_3 = df_N.iloc[av_N+30, [2, 5, 8]].tolist()
    print(df_N.iloc[33, 5])
    NO2_3_std = df_N.iloc[std_N+30, [2, 5, 8]].tolist()
    NO3_3 = df_N.iloc[av_N+60, [5, 8]].tolist()
    print(NO3_3)
    NO3_3_std = df_N.iloc[av_N+60, [5, 8]].tolist()
    NO3_3.insert(0, 0.000218854)
    NO3_3_std.insert(0, 0)
    print(NO3_3)    
    
    DES_anoxic_specific_points_y = df.iloc[average, [6, 12, 18]].tolist()
    print(DES_anoxic_specific_points_y)
    std_deviations_Des = df.iloc[std, [6, 12, 18]].tolist()
    print(std_deviations_Des)

    Nitro_anoxic_specific_points_y = df.iloc[average, [7, 13, 19]].tolist()
    print(Nitro_anoxic_specific_points_y)
    std_deviations_Nitro = df.iloc[std, [7, 13, 19]].tolist()
    print(std_deviations_Nitro)

    smx_measured_N_batch = df.iloc[average, [3, 9, 15]].tolist()
    smx_measured_N_batch.insert(0, 3.95E-08)
    SMX_std_deviations_N = df.iloc[std, [3, 9, 15]].tolist()
    SMX_std_deviations_N.insert(0, 0)
    
    Ammet_oxic_y = df.iloc[average, [5, 11, 17]].tolist()
    std_deviations_Ammet = df.iloc[std, [5, 11, 17]].tolist()


# Determine which site and load measured values
if HEHE_BED == True: 
    get_measured_values(0, 1, 3, 4)
    filename = "R4_Anoxic_Hehe_Bed_Sorption.png"
    plottitle = 'R4_Anoxic Hehe riverbed incl. sorption\n'


elif TUGOU_BANK == True: 
    get_measured_values(10, 11, 23, 24)
    filename = "R4_Anoxic_Tugou_Bank_Sorption.png"
    plottitle = 'R4_Anoxic Batch Tugou Riverbank incl. Sorption\n'


def sub_blank_plot_mod(df, filename):

    fig, ax = plt.subplots(3, 3, figsize=(16, 13), sharex=True)
    print('Plotting all SMX including DES, NIT and AMMET')

    # ========================================
    # [0,0] Nitrogen species & DOC
    # ========================================
    ax[0, 0].scatter(Time_3x_Nspecies, NH4_3, color='violet', label='meas_NH$_4^+$')
    ax[0, 0].plot(df.iloc[:, 0], df.iloc[:, 4], color='violet', label='NH$_4^+$')
    for i, x_point in enumerate(Time_3x_Nspecies):
        ax[0, 0].errorbar(x_point, NH4_3[i], yerr=NH4_3_std[i], color='violet', capsize=5, capthick=1.5)
    
    ax[0, 0].plot(df.iloc[:, 0], df.iloc[:, 6], color='red', label='NO$_2^-$')
    ax[0, 0].scatter(Time_3x_Nspecies, NO2_3, color='red', label='meas_NO$_2^-$')
    for i, x_point in enumerate(Time_3x_Nspecies):
        ax[0, 0].errorbar(x_point, NO2_3[i], yerr=NO2_3_std[i], color='red', capsize=5, capthick=1.5)
    
    ax[0, 0].plot(df.iloc[:, 0], df.iloc[:, 5], color='blue', label='NO$_3^-$')
    ax[0, 0].scatter(Time_3x_Nspecies, NO3_3, color='blue', label='meas_NO$_3^-$')
    for i, x_point in enumerate(Time_3x_Nspecies):
        ax[0, 0].errorbar(x_point, NO3_3[i], yerr=NO3_3_std[i], color='blue', capsize=5, capthick=1.5)
    
    ax[0, 0].plot(df.iloc[:, 0], df.iloc[:, 1], color='green', label='DOC')
    ax[0, 0].plot(df.iloc[:, 0], df.iloc[:, 2], linestyle='-.', color='green', label='CH$_2$O')

    ax1 = ax[0, 0].twinx()
    ax1.plot(df.iloc[:, 0], df.iloc[:, 7], color='lime', label='HNO$_2$')
    ax1.plot(df.iloc[:, 0], df.iloc[:, 37], color='navy', label='HNO$_3$')
    ax1.set_ylabel('HNO$_2$/HNO$_3$ (mol/L)', color='lime')
    
    handles1, labels1 = ax[0, 0].get_legend_handles_labels()
    handles2, labels2 = ax1.get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2
    ax[0, 0].legend(handles, labels, loc='upper right', fontsize='small')
    ax1.tick_params(axis='y', color='green')
    ax[0, 0].set_ylim(0, max(NO3_3)*1.1)  
    ax1.set_ylim(0, max(df.iloc[:, 7])*1.1) 
    ax[0, 0].set_ylabel('N/DOC species [mol/L]') 
    ax[0, 0].set_title('Nitrogen species/DOC')

    # ========================================
    # [0,1] SMX
    # ========================================
    color3 = 'blue'

    smx, = ax[0, 1].plot(df.iloc[:, 0], df.iloc[:, 24], color=color3, label='SMX')

    ax[0, 1].plot(df.iloc[:, 0], df.iloc[:, 48], color=color3, linestyle='dotted', label='Undet')
    ax[0, 1].scatter(SMX_x_anoxic, smx_measured_N_batch, color='red', marker='s', label='SMX_meas')
    for i, x_point in enumerate(SMX_x_anoxic):
        ax[0, 1].errorbar(x_point, smx_measured_N_batch[i], yerr=SMX_std_deviations_N[i], color='red', capsize=5, capthick=1.5)
    
    ax[0, 1].set_ylabel('SMX [mol/L]')
    ax[0, 1].set_title('SMX')
    ax[0, 1].legend()

    # ========================================
    # [1,0] DES
    # ========================================
    color2 = 'green'
    metabolite_plot, = ax[1, 0].plot(df.iloc[:, 0], df.iloc[:, 28], color='blue', label='DES')
    ax[1, 0].scatter(anoxic_specific_points_x, DES_anoxic_specific_points_y, color='red', marker='s', label='meas_Des')
    for i, x_point in enumerate(anoxic_specific_points_x):
        ax[1, 0].errorbar(x_point, DES_anoxic_specific_points_y[i], yerr=std_deviations_Des[i], color='red', capsize=5, capthick=1.5)
    
    ax[1, 0].set_ylabel('C (mol/L)')
    ax[1, 0].set_title('DES-SMX')
    ax[1, 0].set_ylim(0, max(df.iloc[:, 28])*1.1)
    ax[1, 0].legend(loc='upper right', fontsize='small')

    # ========================================
    # [2,0] DES Rates
    # ========================================
    ax[2, 0].plot(df.iloc[:, 0], df.iloc[:, 32], color='red', linestyle='-.', label='R11: SMX$\\to$DES')
    ax[2, 0].plot(df.iloc[:, 0], df.iloc[:, 46], color='green', label='R12: DES$\\to$N')
    ax[2, 0].plot(df.iloc[:, 0], df.iloc[:, 39], color='grey', linestyle='dotted', label='R14: DES$\\to$SMX')

    ax[2, 0].set_xlabel('time [d]')
    ax[2, 0].legend(loc='upper right', fontsize='small')
    ax[2, 0].set_title('Rates DES Metabolite')

    # ========================================
    # [1,1] Nitro-SMX
    # ========================================
    ax[1, 1].plot(df.iloc[:, 0], df.iloc[:, 33], color='blue', label='Nit-SMX')
    ax[1, 1].scatter(anoxic_specific_points_x, Nitro_anoxic_specific_points_y, color='red', marker='s', label='meas_Nit-SMX')

    for i, x_point in enumerate(anoxic_specific_points_x):
        ax[1, 1].errorbar(x_point, Nitro_anoxic_specific_points_y[i], yerr=std_deviations_Nitro[i], color='red', capsize=5, capthick=1.5)

    ax[1, 1].set_ylabel('Nit-SMX (mol/L)', color='black')
    ax[1, 1].set_title('Nit-SMX')
    ax[1, 1].set_ylim(0, max(df.iloc[:, 33])*1.1) 
    ax[1, 1].legend(loc='upper right', fontsize='small')

    # ========================================
    # [2,1] Nitro Rates
    # ========================================
    ax[2, 1].plot(df.iloc[:, 0], df.iloc[:, 34], color='grey', linestyle='-.', label='R9: SMX$\\to$Nit')
    ax[2, 1].plot(df.iloc[:, 0], df.iloc[:, 46], color='green', linestyle='-', label='R12: DES$\\to$Nit')

    ax2 = ax[2, 1].twinx()
    ax2.plot(df.iloc[:, 0], df.iloc[:, 38], color='purple', linestyle='--', label='R13: Nit$\\to$SMX')

    handles1, labels1 = ax[2, 1].get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2
    ax[2, 1].legend(handles, labels, loc='upper right', fontsize='small')
    ax[2, 1].set_title('Rates NIT Metabolites')

    ax[2, 1].set_ylabel('Rates')
    ax[2, 1].set_xlabel('time [d]')
    ax[2, 1].set_ylim(0, max(df.iloc[:, 34])*1.1)


        # ========================================
        # [2,2] AmMet Rate
        # ========================================
    ax[2, 2].plot(df.iloc[:, 0], df.iloc[:, 31], color='orange', label='R8: SMX$\\to$AmMet')
    ax[2, 2].set_ylabel('Rate')
    ax[2, 2].set_title('Rate AmMet Formation')
    ax[2, 2].set_ylim(0, max(df.iloc[:, 31])*1.1)
    ax[2, 2].legend(loc='upper left', fontsize='small')

    # ========================================
    # [1,2] AmMet
    # ========================================
    ax[1, 2].plot(df.iloc[:, 0], df.iloc[:, 27], color='blue', label='AmMet')
    ax[1, 2].scatter(anoxic_specific_points_x, Ammet_oxic_y, color='green', marker='s', label='meas_AmMet')
    for i, x_point in enumerate(anoxic_specific_points_x):
        ax[1, 2].errorbar(x_point, Ammet_oxic_y[i], yerr=std_deviations_Ammet[i], color='green', capsize=5, capthick=1.5)

    ax[1, 2].set_ylabel('C (mol/L)', color='black')
    ax[1, 2].set_title('AmMet-SMX')
    ax[1, 2].set_ylim(0, max(Ammet_oxic_y)*1.5)
    ax[1, 2].legend(loc='upper left', fontsize='small')


    # ========================================
    # [0,2] Sorbed Species
    # ========================================
    ax[0, 2].plot(df.iloc[:, 0], df.iloc[:, 52], color='violet', label='SMX_Sorbed')
    ax[0, 2].plot(df.iloc[:, 0], df.iloc[:, 53], color='blue', label='AmMet_Sorbed')
    ax[0, 2].plot(df.iloc[:, 0], df.iloc[:, 54], color='green', label='Nitro_Sorbed')
    ax[0, 2].plot(df.iloc[:, 0], df.iloc[:, 55], color='darkred', label='Des_Sorbed')

    ax[0, 2].set_ylabel('Sorbed Antibiotics (mol/L)', color='black')
    ax[0, 2].set_ylim(0, max(df.iloc[:, 52])*1.1)  
    ax[0, 2].legend(loc='upper right', fontsize='small')
    ax[0, 2].set_title('Sorbed')

    
    plt.suptitle(plottitle, fontsize=16)
    plt.tight_layout(rect=[0.03, 0.03, 0.8, 1])
    save_path = os.path.join(plot_folder, filename)
    plt.savefig(save_path, dpi=300)
    print(f'Plot saved to: {save_path}')
    plt.show()

def main():
    """Main function to load data and generate plots."""
    sub_blank_plot_mod(output, filename)

if __name__ == '__main__':
    main()
