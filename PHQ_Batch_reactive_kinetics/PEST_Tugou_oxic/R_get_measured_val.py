
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
Create graphs of the measured and modelled data from the columns 
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



plot_folder = os.path.join(script_dir, "plots")
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

N_COL= config.get("column", "col_no", fallback=4)

#open the measurement file specified in Control_file.config
OXIC= config.getboolean("batch", "OXIC", fallback=True)
ANOXIC= config.getboolean("batch", "ANOXIC", fallback=True)
SORPTION= config.getboolean("batch", "SORPTION", fallback=True)
HEHE_BED= config.getboolean("site", "HEHE_BED", fallback=True)
TUGOU_BANK =config.getboolean("site", "TUGOU_BANK", fallback=True) 
NOEDLER =config.getboolean("validation", "NOEDLER", fallback=True) 
SELFILE= config.get("system", "SELFILE",fallback=True)


parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
pestim_col=os.path.abspath(os.path.join(parent_dir, os.pardir))
meas_dir= os.path.join(pestim_col,'Measurements')
excel_file_path = os.path.join(meas_dir, 'Ma_2021_measurements.xlsx')


SMX_x_anoxic=[0, 2, 14, 28,70]
anoxic_specific_points_x = [2, 14, 28,70]
specific_points_x = [2, 14, 28]
Time_3x_Nspecies = [0,15,28]

if os.path.exists(excel_file_path): 
    if OXIC== True: 
        df = pd.read_excel(excel_file_path, sheet_name=0)
        df.reset_index(drop=True, inplace=True)
        print("DataFrame after reading Oxic excel file:")
    if ANOXIC== True: 
        df = pd.read_excel(excel_file_path, sheet_name=1)
        df.reset_index(drop=True, inplace=True)
        print("DataFrame after reading ANOXIC excel file:")
    print(df.head())
    df_N= pd.read_excel(excel_file_path, sheet_name=2)
    print(df_N.head())
else:
    print(f"Warning: Excel file not found at {excel_file_path}")
    df_N = None  # <-- Add this

def get_measured_values(average, std, av_N,std_N):
    global NH4_3, NO2_3, NO3_3,NH4_3_std, NO2_3_std, NO3_3_std, DES, std_deviations_Des, Nitro
    global std_deviations_Nitro, SMX, SMX_std_deviations_N, Ammet, std_deviations_Ammet
    global SDZ, SDZ_std, SMZ, SMZ_std

    NH4_3= df_N.iloc[av_N, [2, 5, 8]].tolist()#[0, 3.57E-04	,1.92E-04]#mol/L
    NH4_3_std= df_N.iloc[std_N, [2, 5, 8]].tolist()
    NO2_3= df_N.iloc[av_N+30, [2, 5, 8]].tolist()#[0.00E+00,	3.45E-05	,2.30E-07]#mol/L
    print(df_N.iloc[33,5])
    NO2_3_std= df_N.iloc[std_N+30, [2, 5, 8]].tolist()#[2.19E-04	,1.30E-04	,8.81E-05]#mol/L
    NO3_3= df_N.iloc[av_N+60, [ 5, 8]].tolist()
    NO3_3_std= df_N.iloc[av_N+60, [ 5, 8]].tolist()
    NO3_3.insert(0,0.000218854 )
    NO3_3_std.insert(0,0) 

    if OXIC== True: 
        DES= df.iloc[average, [6, 12, 18,24]].tolist()
        std_deviations_Des = df.iloc[std, [6, 12, 18,24]].tolist()
        Nitro= df.iloc[average, [7, 13, 19,25]].tolist()
        std_deviations_Nitro = df.iloc[std, [7,13,19,25]].tolist()
        SMX =df.iloc[average, [3,9,15,21]].tolist()
        SMX.insert(0, 3.95E-08)
        SMX_std_deviations_N = df.iloc[std, [3,9,15,21]].tolist()
        SMX_std_deviations_N.insert(0, 0)
        Ammet = df.iloc[average, [5,11,17,23]].tolist()
        std_deviations_Ammet= df.iloc[std, [5,11,17,23]].tolist()
        SDZ= df.iloc[average, [2, 8, 14,20]].tolist()
        SMZ=df.iloc[std, [4, 10, 16,22]].tolist()
        SDZ.insert(0, 0)
        SMZ.insert(0, 0)

    if ANOXIC== True: 
        DES= df.iloc[average, [6, 12, 18]].tolist()
        Nitro= df.iloc[average, [7, 13, 19]].tolist()
        SMX =df.iloc[average, [3,9,15]].tolist()
        SMX.insert(0, 3.95E-08)
        SMZ=df.iloc[average, [4, 10, 16]].tolist()
        SDZ= df.iloc[average, [2, 8, 14]].tolist()
        SMZ_std=df.iloc[std, [4, 10, 16]].tolist()
        SDZ_std= df.iloc[std, [2, 8, 14]].tolist()
        Ammet= df.iloc[average, [5,11,17]].tolist()
        std_deviations_Ammet= df.iloc[std, [5,11,17]].tolist()
        SDZ.insert(0, 3.95E-08)
        SMZ.insert(0, 3.95E-08)
        SDZ_std.insert(0, 0)
        SMZ_std.insert(0, 0)



if HEHE_BED ==True: 
    get_measured_values(0,1,3,4)

    filename= "Oxic_Hehe_Bed_Sorption.png"
    plottitle='Oxic Batch Hehe Riverbed inkl. Sorption\n'


if TUGOU_BANK == True: 
    get_measured_values(10,11,23,24)

    filename= "Oxic_Tugou_Bank_Sorption.png"
    plottitle='Oxic Batch Tugou Riverbank inkl. Sorption\n'

