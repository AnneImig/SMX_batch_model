"""code creates PEST files (template of Controle_file.conf, instruction and pst file)"""


import subprocess
import os
import sys
import shutil
import configparser
import tempfile as tf
from string import Template
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
pestim_col=os.path.abspath(os.path.join(parent_dir, os.pardir))
meas_dir= os.path.join(pestim_col,'Measurements')
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")

# read all information from configfile
if len(sys.argv) > 1:
    configfn = sys.argv[1]
else:
    configfn = os.path.join(script_dir,"Controle_file.conf")

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(configfn)

# Flags for program flow
OXIC= config.getboolean("batch", "OXIC", fallback=True)
ANOXIC= config.getboolean("batch", "ANOXIC", fallback=True)

HEHE_BED= config.getboolean("site", "HEHE_BED", fallback=True)
TUGOU_BANK =config.getboolean("site", "TUGOU_BANK", fallback=True) 
NOEDLER =config.getboolean("validation", "NOEDLER", fallback=True) 
SELFILE= config.get("system", "SELFILE",fallback='output/Results.sel')
DATABASE=   config.get("system", "SELFILE",fallback='bin/phreeqc_P.dat')

# Filenames
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir, os.pardir))
meas_dir= os.path.join(parent_dir,'Measurements')
noedler_meas= os.path.join(meas_dir,'Nödler_2012_measurements.xlsx')

phrq_file=  os.path.join(input_folder, "Noedler.phrq")



if os.name == "nt":
    DATABASE = ("c:/phreeqc/database/phreeqc.dat     "  )
    SCR = ("scr.out")
    PHRQCMD = ("C:/phreeqc/bin/Release/phreeqc.exe   ")

else:
    DATABASE = DATABASE
    EXECUTABLE = "phreeqc"
    SCR = ("scr.out")


params = {
    'Hehe_bed_anoxic_sorption': [3e-2, 2e-4,2.5e3, 4e3, 1.5e-03, 4e-3,  1.6315e-07, 2e26, 1.5e18,5e3, 1.2e5, 8, 5e-1,  1.5e-05,  2e5,8],
    'Hehe_bed_oxic_sorption': [1e-3, 1e-4, 2e1, 5e2, 7e2,0.003, 1.6315e-07, 2.5e17, 4e13, 3.5e3, 1e5,19, 0.9,  1.5e-5,5e3,0.005],     
    'Tugou_bank_oxic_sorption': [1e-3, 3e-6, 2e1, 1e3, 6e3, 7e-3, 5.2596e-06, 7e16, 3e22, 9e2, 5e5, 4,  0.9,  1.5e-5,  1.3e4,0.005],   
    'Tugou_bank_anoxic_sorption': [1e-3, 3e-6, 25, 9e2, 1.9e-05, 0.15,  4.6315e-07, 2e28, 8e14,1.5e2,3e5, 3, 0.1,  1.5e-05,  5e3,0.55],   
    }

if NOEDLER ==True: 
    filename= "Noedler.png"
    plottitle='Anoxic Batch Noedler \n'
    Noedler = pd.read_excel(noedler_meas, sheet_name=0)

    NO2_3= Noedler.iloc[0:9, 2].tolist() #[0.00E+00,	3.45E-05	,2.30E-07]#mol/L
    NO3_3= Noedler.iloc[0:9, 1].tolist()
    DOC= Noedler.iloc[ 0:9, 3].tolist()

    SMX=Noedler.iloc[ 0:9,8].tolist()
    DES=Noedler.iloc[0:9, 12].tolist()
    Nitro=Noedler.iloc[0:9, 10].tolist()
    Time_3x_Nspecies=Noedler.iloc[0:9, 0].tolist()

bounds = {
    # SOM mobilization, DOC oxidation
    "K1":             {"lower": 1e-4,   "upper": 1},
    "K2":             {"lower": 1e-7,   "upper": 10},
    "K3":             {"lower": 1,      "upper": 9e5},

    # Nitrification
    "K4":             {"lower": 1e1,    "upper": 5e4},
    "K5":             {"lower": 1e1,    "upper": 9e3},

    # Denitrification
    "K6":             {"lower": 1e-3,   "upper": 1e4},
    "K7":             {"lower": 1e-3,      "upper": 1e4},
    "K_NO3":          {"lower": 1e-7,   "upper": 9},

    # SMX fate with TP formation and retransformation
    "K8":             {"lower": 1e-8,   "upper": 30},
    "K_DOC":          {"lower": 1.6e-8, "upper": 3},
    "K9":             {"lower": 1e1,    "upper": 1e30},
    "K10":            {"lower": 1e1,    "upper": 1e30},
    "K11":            {"lower": 1,      "upper": 1e5},
    "K12":            {"lower": 1500,     "upper": 1e7},
    "K13":            {"lower": 1e-3,   "upper": 500},
    "K14":            {"lower": 1e-3,   "upper": 500},
    "K_DOC2":         {"lower": 1e-7,   "upper": 2},
    "K15":            {"lower": 1,      "upper": 5e5},
    "K16":            {"lower": 1e-5,   "upper": 100},
}


def modify_phrq_and_save():
    Template_file_path=  os.path.join(input_folder, "Noedler.phrq")
    try:
        # Read the content of the .phrq file
        with open(Template_file_path, 'r') as file:
            lines = file.readlines()
        if ANOXIC ==True:
            lines[76] = '       -parms    $K1               $\n' #k1
            lines[82] = '       -parms    $K2            $   \n' # K2   
            lines[87] = '       -parms    $K6              $  \n'#   '+  f'{parameterlist[4]}     '+f'{parameterlist[5]}\n' # K6   #k_s,Corg  #k_s,NO3 
            lines[92] = '       -parms    $K7     $  $K_NO3    $ \n'#K7  #k_I,NO3 
            lines[99] = '       -parms     $K8       $  $K_DOC            $\n'#K8 #K_(s,SMX)# k_l,Corg   
            lines[105] = '       -parms    $K9           $\n' #K9
            lines[111] = '       -parms    $K10       $\n' #K10
            lines[116] = '       -parms    $K11        $\n' #K11
            lines[121] = '       -parms    $K12           $\n' #K12
            lines[126] = '       -parms     $K13        $\n' #K13
            lines[131] = '       -parms     $K14        $  $K_DOC2           $\n' #K14
            lines[135] = '       -parms    $K15                    $\n' #K15
            lines[139] = '       -parms   $K16           $\n' #K16 
          # Check if the old .tpl file exists and delete it
        tpl_file_path = Template_file_path.replace('.phrq', '.tpl')
        if os.path.exists(tpl_file_path):
            os.remove(tpl_file_path)
        tpl_file_name =os.path.basename(tpl_file_path)
        # Save the modified content as a .tpl file with the same name
        output_file_path = os.path.join(script_dir, tpl_file_name)
        
        with open(output_file_path, 'w') as tpl_file:
            tpl_file.write('ptf $\n')  # Adding ptf $ as the first line
            tpl_file.writelines(lines)

        print(f"Modification successful. Saved as {tpl_file_path}")
        return tpl_file_name
    except Exception as e:
        print(f"Error: {e}")

tpl_file =modify_phrq_and_save()

rows = Time_3x_Nspecies
d_time = [2,23,29,51,46,106,161,471]

def create_c_ins_file():

    obs_labels_dict = {
        'DOC': [],
        'DES': [],
        'Nitro': [],
        'SMX': [],
        'NO2': [],
        'NO3': []
    }

    for idx in range(len(d_time)):
        obs_labels_dict['DOC'].append(f'l{d_time[idx]} [DOC_{rows[idx]}]3:13\n')
        obs_labels_dict['DES'].append(f'l{d_time[idx]} [DES_{rows[idx]}]3:13\n')
        obs_labels_dict['Nitro'].append(f'l{d_time[idx]} [Nitro_{rows[idx]}]3:13\n')
        obs_labels_dict['NO2'].append(f'l{d_time[idx]} [NO2_{rows[idx]}]3:13\n')
        obs_labels_dict['NO3'].append(f'l{d_time[idx]} [NO3_{rows[idx]}]3:13\n')
        obs_labels_dict['SMX'].append(f'l{d_time[idx]} [SMX_{rows[idx]}]3:13\n')

    script_dir = os.path.dirname(__file__)  # Assuming the script is in the same directory

    for key, labels in obs_labels_dict.items():
        if labels:  # Check if the list is not empty
            file_path = os.path.join(script_dir, f'{key}.ins')
            with open(file_path, 'w') as file:
                file.write('pif @\n')
                file.write(''.join(labels).strip())  # Write the labels to the file
    return obs_labels_dict

obs_labels_dict = create_c_ins_file()

# PEST CONTROL FILE VARIABLES
 #number of observations

nobsgp='6'
nobs = 6*len(rows) 
ninsfle = 6 #number of instruction files
p_names = ['K1','K2', 'K6','K7','K_NO3','K8','K_DOC','K9','K10','K11','K12','K13','K14','K_DOC2','K15','K16']
npar = '16'    #number of parameters
nprior = '0'  #number of articles of prior information
npargp = "2"   #number of parameter groups
ntpfle = '1'  #number of template files



param_values = [1e-2, 1, 0.12,  0.3, 0.0378, 0.0005,  0.0315, 6e7, 1e5, 8, 1.5e4, 0.39, 2, 0.0215,  2e2, 4.1]   


# PEST CONTROL FILE
control_data = (
'* control data\n'
    'restart estimation\n'
    +str(npar) +' '+str(nobs) +' '+npargp +' '+nprior +' '+nobsgp +'\n'
    +str(ntpfle) +' '+str(ninsfle) +' single point 1 0 0 \n'
    '10 -3 0.3 0.01 10 0 lamforgive noderforgive \n'
    '10 10 0.001 \n'
    '0.1 1 noaui \n'
    '50 0.0005 4 4 0.0005 4 \n'
    '1 0 0 verboserec NOJCOSAVEITN REISAVEITN NOPARSAVEITN \n'

'* parameter groups\n'
    'geochem relative 0.01 0.0 switch 2.0 parabolic\n'
    'antibiotics relative 0.01 0.0 switch 2.0 parabolic\n')

control_data += (
'* parameter data\n')

# Check if valid parameters were returned for the selected location and condition
if param_values is not None:
    for index, name in enumerate(p_names):

        # Get the initial value from the params list based on the key
        init_value = param_values[index]
        # Default value for the 'none' placeholder
        none_value = "log"
        parchglim='factor'
        # If anoxic conditions are true, modify none_value for K7 and K8
        if ANOXIC : 
            # Check if the index is in the specified set
            if index >=5:
                pargp='antibiotics'
            else:
                pargp='geochem'
#p_names = ['K1','K2', 'K6','K7','K_NO3','K8','K_DOC','K9','K10','K11','K12','K13','K14','K_DOC2','K15','K16']
            if index in { 3,15,2,14,11,12,9,4}:
                none_value = "log"
                parchglim='factor'
                line = f"{name} {none_value} {parchglim} {init_value} {bounds[name]['lower']} {bounds[name]['upper']} {pargp} 1.0 0.0 1\n"
            else:
                none_value = "fixed"
                parchglim='relative'
                line = f"{name} {none_value} {parchglim} {init_value} {bounds[name]['lower']} {bounds[name]['upper']} {pargp} 1.0 0.0 1\n"
            
        control_data += line

    # Now you have `control_data` generated with the correct `init_value` from the selected parameter set
else:
    print("No parameter values found for the selected location and condition.")

control_data += ( 
'* observation groups\n')
control_data += ( 
    'gDOC\n'
    'gNO2\n'
    'gNO3\n'
    'gNitro\n'
    'gSMX\n'
    'gDES\n'
    )
control_data +=('* observation data\n')

for value in enumerate(rows):
    labels = [
        f'DOC_{value[1]} {DOC[value[0]]}  1 gDOC \n',
        f'NO2_{value[1]}  {NO2_3[value[0]]}  1 gNO2 \n',
        f'NO3_{value[1]}  {NO3_3[value[0]]}  1 gNO3 \n',
        f'Smx_{value[1]}  {SMX[value[0]]}   1 gSMX \n',
        f'DES_{value[1]}  {DES[value[0]]}   1 gDES \n',
        f'Nitro_{value[1]} {Nitro[value[0]]}   1 gNitro \n'
    ]
    control_data += ''.join(labels)

control_data += (
'* model command line\n')
control_data+= "python R2_Run_PHQ.py \n "#EXECUTABLE +  '    '+ os.path.basename(phrq_file)+  '    '+ 'output/output.out'+  '    '+DATABASE+  '    '+SCR+'\n'
control_data += (
    '* model input/output\n'
    f'{os.path.basename(tpl_file)}'+ f'     input/{os.path.basename(phrq_file)}\n'
    'Nitro.ins output/Nitro.sel\n'
    'SMX.ins output/SMX.sel\n'
    'DES.ins output/DES.sel\n'
)
if ANOXIC==True:
    control_data+=(
        'DOC.ins output/DOC.sel\n'
        'NO2.ins output/NO2.sel\n'
        'NO3.ins output/NO3.sel\n'
    )
control_file_path1 = os.path.join(script_dir, 'control_log.pst')
control_file_path2 = os.path.join(script_dir, 'control_log2.pst')

content = 'pcf\n' + control_data

# Write original file
with open(control_file_path1, 'w') as f1:
    f1.write(content)

# Modify content for second file
modified_content = content.replace(
    '50 0.0005 4 4 0.0005 4',
    '-1 0.0005 4 4 0.0005 4'
)

# Write modified file
with open(control_file_path2, 'w') as f2:
    f2.write(modified_content)