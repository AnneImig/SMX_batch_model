"""code creates PEST files (template of colsim, instruction and pst file)"""


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
from R_get_measured_val import df,df_N,DES,Nitro, SMX, SDZ, SMZ, Ammet,NH4_3,NO2_3,NO3_3

# Convert the lists to DataFrames
SMX_u = pd.DataFrame(SMX)
DES_u = pd.DataFrame(DES)
Nitro_u = pd.DataFrame(Nitro)
Ammet_u = pd.DataFrame(Ammet)

# Set columns
DES_u.columns = SMX_u.columns
Nitro_u.columns = SMX_u.columns
Ammet_u.columns = SMX_u.columns

# Sum the DataFrames
Sum = SMX_u + DES_u + Nitro_u + Ammet_u

# Subtract SMX_init from each element in the Sum DataFrame
SMX_init = 3.9482e-08
Undet_df = SMX_init-Sum
print(Sum, Undet_df)
Undet = Undet_df.values.tolist()

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
SELFILE= config.get("system", "SELFILE",fallback='output/Results.sel')



if OXIC== True:
    phrq_file=  os.path.join(input_folder, "Oxic_template_undetected_sorption.phrq")
    print(f"Modification successful oxic undetected as {phrq_file}")
else:
    phrq_file=  os.path.join(input_folder, "Anoxic_template_undetected_sorption.phrq")
    print(f"Modification successful oxic undetected as {phrq_file}")

ins_file = [file for file in os.listdir(script_dir) if file.endswith('.ins')]
out_file = os.path.join(output_folder,'output.out' )



if os.name == "nt":
    DATABASE = ("c:/phreeqc/database/phreeqc.dat     "  )
    SCR = ("scr.out")
    PHRQCMD = ("C:/phreeqc/bin/Release/phreeqc.exe   ")

else:
    DATABASE = "/Users/anneimig/Documents/Software_executables/Phreeqc/phreeqc-3.5.0-14000/database/phreeqc.dat"
    EXECUTABLE = "phreeqc"
    SCR = ("scr.out")

params = {
    'Hehe_bed_anoxic_sorption': [3e-2, 2e-4,2.5e3, 4e3, 1.5e-03, 4e-3,  1.6315e-07, 2e26, 1.5e18,5e3, 1.2e5, 8, 5e-1,  1.5e-05,  2e5,8],
    'Hehe_bed_oxic_sorption': [1e-3, 1e-4, 2e1, 5e2, 7e2,0.003, 1.6315e-07, 2.5e17, 4e13, 3.5e3, 1e5,19, 0.9,  1.5e-5,5e3,0.005],     
    'Tugou_bank_oxic_sorption': [1e-3, 3e-6, 2e1, 1e3, 6e3, 7e-3, 5.2596e-06, 7e16, 3e22, 9e2, 5e5, 4,  0.9,  1.5e-5,  1.3e4,0.005],   
    'Tugou_bank_anoxic_sorption': [1e-3, 3e-6, 25, 9e2, 1.9e-05, 0.15,  4.6315e-07, 2e28, 8e14,1.5e2,3e5, 3, 0.1,  1.5e-05,  5e3,0.55],   
    }
bounds = {
    # SOM mobilization, DOC oxidation
    "K1":             {"lower": 1e-4,   "upper": 1},
    "K2":             {"lower": 1e-7,   "upper": 1},
    "K3":             {"lower": 1,      "upper": 9e5},

    # Nitrification
    "K4":             {"lower": 1e1,    "upper": 5e4},
    "K5":             {"lower": 1e1,    "upper": 9e3},

    # Denitrification
    "K6":             {"lower": 1,   "upper": 1e7},
    "K7":             {"lower": 1,      "upper": 1e6},
    "K_NO3":          {"lower": 1e-7,   "upper": 9e-2},

    # SMX fate with TP formation and retransformation
    "K8":             {"lower": 1e-6,   "upper": 30},
    "K_DOC":          {"lower": 1.6e-8, "upper": 3e-4},
    "K9":             {"lower": 1e1,    "upper": 1e30},
    "K10":            {"lower": 1e1,    "upper": 1e30},
    "K11":            {"lower": 1,      "upper": 1e5},
    "K12":            {"lower": 15,     "upper": 1e7},
    "K13":            {"lower": 1e-3,   "upper": 500},
    "K14":            {"lower": 1e-3,   "upper": 500},
    "K_DOC2":         {"lower": 1e-7,   "upper": 2e-4},
    "K15":            {"lower": 1,      "upper": 5e5},
    "K16":            {"lower": 1e-5,   "upper": 100},
}


def determine_file_and_params(OXIC, ANOXIC, HEHE_BED,  TUGOU_BANK):

    location_prefix = 'Oxic' if OXIC else 'Anoxic'
    
    location_map = {
        'Hehe_bed': HEHE_BED,
        'Tugou_bank': TUGOU_BANK,
    }

    for location, condition in location_map.items():
        if condition:
            file_name = f"{location_prefix}_{location}_sorption.phrq"
            param_key = f"{location}{'_anoxic' if ANOXIC else '_oxic'}_sorption"
            return file_name, params.get(param_key, None)

    return None, None



def modify_phrq_and_save():
    if  OXIC== True:
        Template_file_path=  os.path.join(input_folder, "Oxic_template_undetected_sorption.phrq")
        print(f"Modification successful oxic undetected as {Template_file_path}")
    else:
        Template_file_path=  os.path.join(input_folder, "Anoxic_template_undetected_sorption.phrq")
        print(f"Modification successful oxic undetected as {Template_file_path}")
    try:
        # Read the content of the .phrq file
        with open(Template_file_path, 'r') as file:
            lines = file.readlines()
        if ANOXIC ==True:
            if HEHE_BED== True: 
                #"DOC adjustments"
                lines[86] = '    Doc       3.28 mg/kgw   \n' #initial DOC molar mass 
                lines[105] = '       -m0    0.015        \n' # initial SOM molar mass #0.0049g/10ml 0.49g/L 490mg/L TOC CH4O 32 g/mol 0.015 mol/L (15% solved in water 2.5 mol/L DOC)
            if TUGOU_BANK== True: 
                #"DOC adjustments"
                lines[86] = '    Doc      4.66 mg/kgw   \n' #initial DOC molar mass 
                lines[105] = '       -m0   5.3e-3          \n' # initial SOM molar mass #0.0017g/10ml 0.17g/L 170mg/L TOC CH4O 32 g/mol 5.3e-3 mol/L (15% solved in water 2.5 mol/L DOC) 
            #Parameter values# 
            lines[106] = '       -parms    $K1               $\n' #k1
            lines[112] = '       -parms    $K2            $   \n' # K2   
            lines[117] = '       -parms    $K6              $  \n'#   '+  f'{parameterlist[4]}     '+f'{parameterlist[5]}\n' # K6   #k_s,Corg  #k_s,NO3 
            lines[122] = '       -parms    $K7     $  $K_NO3    $ \n'#K7  #k_I,NO3 
            lines[130] = '       -parms     $K8       $  $K_DOC            $\n'#K8 #K_(s,SMX)# k_l,Corg   
            lines[135] = '       -parms    $K9           $\n' #K9
            lines[141] = '       -parms    $K10       $\n' #K10
            lines[146] = '       -parms    $K11        $\n' #K11
            lines[151] = '       -parms    $K12           $\n' #K12
            lines[156] = '       -parms     $K13        $\n' #K13
            lines[161] = '       -parms     $K14        $  $K_DOC2           $\n' #K14
            lines[165] = '       -parms    $K15                    $\n' #K15
            lines[168] = '       -parms   $K16           $\n' #K16 
        if OXIC== True:
            if HEHE_BED== True: 
                #"DOC adjustments"
                lines[90] = '    Doc      3.28 mg/kgw     \n' #initial DOC molar mass 
                lines[104] = '       -m0   16          \n' # initial SOM molar mass 
            if TUGOU_BANK== True: 
                #"DOC adjustments"
                lines[90] = '    Doc      4.66 mg/kgw  \n' #initial DOC molar mass 
                lines[104] = '       -m0 2e-3          \n' # initial SOM molar mass 
            lines[105] ='       -parms    $K1             $\n' #k1
            lines[111] = '       -parms    $K2       $\n' #k2   
            lines[116] = '       -parms    $K3              $\n' #k3 
            lines[121] = '       -parms    $K4                 $\n' #k4 
            lines[126] = '       -parms    $K5           $\n' #k5
            lines[134] = '      -parms     $K8          $  $           K_DOC$\n'#K8  
            lines[139] = '       -parms    $K9          $\n' #K9
            lines[145] = '       -parms    $K10         $\n' #K10
            lines[150] = '       -parms    $K11         $\n' #K11
            lines[155] = '       -parms    $K12         $\n' #K12
            lines[160] = '       -parms    $K13         $\n' #K13
            lines[165] = '       -parms    $K14         $  $K_DOC2         $   \n' #K14
            lines[178] = '       -parms    $K15                    $\n' #K15
            lines[181] = '       -parms   $K16           $\n' #K16 
        if TUGOU_BANK== True:
            lines [52]= '    log_k -100.5\n' #Nitro
            lines [55]= '    log_k -100.7\n' #DES
            lines [58]= '    log_k -100.8\n' #Ammet 
            lines [61]= '    log_k -101.04\n' #SMX
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

tpl_file= modify_phrq_and_save()

if OXIC==True:
    rows = [20, 140, 280, 700]
    d_time = [21, 120, 140, 420]
else:
    rows = [20, 140, 280]
    d_time = [21, 120, 140]

def create_c_ins_file():

    obs_labels_dict = {
        'Ammet': [],
        'DES': [],
        'Nitro': [],
        'NH4': [],
        'NO2': [],
        'NO3': [],
        'SMX': [],
        'Undet':[]
    }

    for idx in range(len(d_time)):
        if OXIC:
            obs_labels_dict['Ammet'].append(f'l{d_time[idx]} [AmMet_{rows[idx]}]3:13\n')
            obs_labels_dict['DES'].append(f'l{d_time[idx]} [DES_{rows[idx]}]3:13\n')
            obs_labels_dict['Nitro'].append(f'l{d_time[idx]} [Nitro_{rows[idx]}]3:13\n')
            obs_labels_dict['SMX'].append(f'l{d_time[idx]} [SMX_{rows[idx]}]3:13\n')
            obs_labels_dict['Undet'].append(f'l{d_time[idx]} [Undet_{rows[idx]}]3:13\n')
        else:
            obs_labels_dict['Ammet'].append(f'l{d_time[idx]} [AmMet_{rows[idx]}]3:13\n')
            obs_labels_dict['DES'].append(f'l{d_time[idx]} [DES_{rows[idx]}]3:13\n')
            obs_labels_dict['Nitro'].append(f'l{d_time[idx]} [Nitro_{rows[idx]}]3:13\n')
            obs_labels_dict['NH4'].append(f'l{d_time[idx]} [NH4_{rows[idx]}]3:13\n')
            obs_labels_dict['NO2'].append(f'l{d_time[idx]} [NO2_{rows[idx]}]3:13\n')
            obs_labels_dict['NO3'].append(f'l{d_time[idx]} [NO3_{rows[idx]}]3:13\n')
            obs_labels_dict['SMX'].append(f'l{d_time[idx]} [SMX_{rows[idx]}]3:13\n')
            obs_labels_dict['Undet'].append(f'l{d_time[idx]} [Undet_{rows[idx]}]3:13\n')

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
if OXIC== True:
    nobsgp = '5'  #number of observation groups =ninsfiles
    ninsfle = 5 #number of instruction files
    nobs = ninsfle*len(rows)  
    p_names = ['K1','K2', 'K3','K4','K5','K8','K_DOC','K9','K10','K11','K12','K13','K14','K_DOC2','K15','K16']
else:
    nobsgp='8'
    ninsfle = 8 #number of instruction files
    nobs = ninsfle *len(rows) 
    p_names = ['K1','K2', 'K6','K7','K_NO3','K8','K_DOC','K9','K10','K11','K12','K13','K14','K_DOC2','K15','K16']
npar = '16'    #number of parameters
nprior = '0'  #number of articles of prior information
npargp = "2"   #number of parameter groups
ntpfle = '1'  #number of template files

# Assuming that ANOXIC is a boolean determining the environmental condition
file_name, param_values = determine_file_and_params(OXIC, ANOXIC, HEHE_BED, TUGOU_BANK)


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
# '* singular value decomposition\n'
#     '1\n'
#     '14 5e-7\n'
#     '0\n'
'* parameter groups\n'
    'geochem relative 0.1 0.0 switch 2.0 parabolic\n'
    'antibiotics relative 0.1 0.0 switch 2.0 parabolic\n')

control_data += (
'* parameter data\n')

# Check if valid parameters were returned for the selected location and condition
if param_values is not None:
    for index, name in enumerate(p_names):

        # Get the initial value from the params list based on the key
        init_value = param_values[index]
        # Default value for the 'none' placeholder PARTRANS 
        none_value = "none"
        #check Pestim_Column/SA_Batch_Reactive_Plotting/Ordering_SI_Results.xlsx for odering of parameters
        # for log transformation
        if ANOXIC : 
            # Check if the index is in the specified set
            if index >=5:
                pargp='antibiotics'
            else:
                pargp='geochem'
            if index in {4,0,7, 13,1,14, 12,9}:
                none_value = "fixed"
                parchglim='relative'
                line = f"{name} {none_value} {parchglim} {init_value} {bounds[name]['lower']} {bounds[name]['upper']} {pargp} 1.0 0.0 1\n"
            else:
                none_value = "log"
                parchglim='factor'            
                line = f"{name} {none_value} {parchglim}  {init_value} {bounds[name]['lower']} {bounds[name]['upper']} {pargp} 1.0 0.0 1\n"
            
        control_data += line

    # Now you have `control_data` generated with the correct `init_value` from the selected parameter set
else:
    print("No parameter values found for the selected location and condition.")

control_data += ( 
'* observation groups\n')
if OXIC== True: 
   control_data += ( 
        'gNitro\n'
        'gAmmet\n'
        'gDES\n'
        'gSMX\n'
        'gUndet\n'
        )
else:
    control_data += ( 
        'gNH4\n'
        'gNO2\n'
        'gNO3\n'
        'gNitro\n'
        'gAmmet\n'
        'gDES\n'
        'gSMX\n'
        'gUndet\n'
        )
control_data +=('* observation data\n')



for value in enumerate(rows):
    if OXIC==True:
           # Access the Undet value from the list and extract the scalar
        Undet_value = Undet[value[0]]  # This might be a list or an array
        if isinstance(Undet_value, (list, np.ndarray)):  # Check if it's a list or array
            Undet_value = Undet_value[0]  # Extract the scalar value from the list

        labels = [

            f' AmMet_{value[1]}  {Ammet[value[0]]}   1 gAmmet \n',
            f' DES_{(value[1])}  {DES[value[0]]}   1 gDES \n',
            f' Nitro_{value[1]}  {Nitro[value[0]]}   1 gNitro \n'
            f' SMX_{value[1]}  {SMX[value[0]]}   1 gSMX \n'
            f' Undet_{value[1]}  {Undet_value}   1 gUndet \n'
        ]
    else:
                   # Access the Undet value from the list and extract the scalar
        Undet_value = Undet[value[0]]  # This might be a list or an array
        if isinstance(Undet_value, (list, np.ndarray)):  # Check if it's a list or array
            Undet_value = Undet_value[0]  # Extract the scalar value from the list

        labels = [
            f'NH4_{value[1]} {NH4_3[value[0]]}  1 gNH4 \n',
            f'NO2_{value[1]}  {NO2_3[value[0]]}  1 gNO2 \n',
            f'NO3_{value[1]}  {NO3_3[value[0]]}  1 gNO3 \n',
            f'SMX_{value[1]}  {SMX[value[0]]}   1 gSMX \n',
            f'AmMet_{value[1]}  {Ammet[value[0]]}   1 gAmmet \n',
            f'DES_{(value[1])}  {DES[value[0]]}   1 gDES \n',
            f'Nitro_{value[1]} {Nitro[value[0]]}   1 gNitro \n'
            f'Undet_{value[1]}  {Undet_value}   1 gUndet \n'
        ]
    control_data += ''.join(labels)

  #  control_data += ('C_'+str(index)+ ' ' +str(row['Normalized_measured'])) +' 1 gC\n'
control_data += (
'* model command line\n')
control_data+= "python R2_Run_PHQ.py \n "#EXECUTABLE +  '    '+ os.path.basename(phrq_file)+  '    '+ 'output/output.out'+  '    '+DATABASE+  '    '+SCR+'\n'

control_data += (
    '* model input/output\n'
    f'{os.path.basename(tpl_file)}'+ f' input/{os.path.basename(phrq_file)}\n'
    'Nitro.ins output/Nitro.sel\n'
    'Ammet.ins output/Ammet.sel\n'
    'DES.ins output/DES.sel\n'
    'SMX.ins output/SMX.sel\n'
    'Undet.ins output/Undet.sel\n'
)
if ANOXIC==True:
    control_data+=(
        'NH4.ins output/NH4.sel\n'
        'NO2.ins output/NO2.sel\n'
        'NO3.ins output/NO3.sel\n'
    )
control_file_path1 = os.path.join(script_dir, 'control_log.pst')
control_file_path2 = os.path.join(script_dir, 'control_log2.pst')
control_file_path3 = os.path.join(script_dir, 'control_log2_copy.pst')  # new copy

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

# NEW: Copy the modified file
shutil.copy(control_file_path2, control_file_path3)

