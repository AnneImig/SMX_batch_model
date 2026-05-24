"""



Basic Setup for a Sobol Sensitivity Analysis

Can be adapted to different models look for parts with: user-input

Install a normal conda with python 2.7 and the following packages:
    conda install -c conda-forge salib
    conda install plotly
    conda install -c plotly plotly-orca psutil requests
    conda install pillow

Navigate directory to Python File Directory or some modules(e.g. progressbar) will not be found


"""

import numpy as np
import sys
import configparser
import pandas as pd
from SALib.sample import saltelli
from SALib.analyze import sobol
import os
import time
import subprocess
import tempfile as tf
sys.path.append(os.getcwd())
from progressbar import print_progress
import basic_func
from shutil import copyfile
from Utils import R2

############################################################
#Functions:
############################################################

'''user-input'''
script_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")

# read all information from configfile
if len(sys.argv) > 1: 
    configfn = sys.argv[1]
else:
    configfn = os.path.join(script_dir,"Controle_file.conf")

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(configfn)


OXIC= config.getboolean("batch", "OXIC", fallback=True)
ANOXIC= config.getboolean("batch", "ANOXIC", fallback=True)

DATABASE  = config.get("system", "DATABASE", fallback=True)
SELFILE =config.get("system", "SELFILE", fallback=True) 

HEHE_BED= config.getboolean("site", "HEHE_BED", fallback=True)
TUGOU_BANK =config.getboolean("site", "TUGOU_BANK", fallback=True) 
NOEDLER =config.getboolean("validation", "NOEDLER", fallback=True) 

if HEHE_BED and ANOXIC:
    model_name='Hehe_anoxic'
elif HEHE_BED and OXIC:
    model_name="Hehe_oxic" 
elif TUGOU_BANK and ANOXIC:
    model_name="Tugou_anoxic"
elif TUGOU_BANK and OXIC:
    model_name="Tugou_oxic"
else:
    model_name="Noedler"

#make a new folder to save all the model results into:
if os.path.isdir(os.path.join(script_dir,f'm_results_{model_name}')) == False:
    os.mkdir(os.path.join(script_dir,f'm_results_{model_name}'))
resultdir = os.path.join(script_dir,f'm_results_{model_name}') 

if os.path.isdir(os.path.join(script_dir,f'output_{model_name}')) == False:
    os.mkdir(os.path.join(script_dir,f'output_{model_name}'))
outputdir = os.path.join(script_dir,f'output_{model_name}')
sel_file_path=os.path.join(outputdir,'Results.sel')

def generate_inputf(parameterlist,script_dir,input_folder, n=0):
    #make a new folder to save all the model input files into:
    if os.path.isdir(os.path.join(script_dir,f'Sobol_input_{model_name}')) == False:
        os.mkdir(os.path.join(script_dir,f'Sobol_input_{model_name}'))
    inputdir = os.path.join(script_dir,f'Sobol_input_{model_name}')
    
    if OXIC== True:
        phrq_file=os.path.join(input_folder, "Oxic_template_undetected_sorption.phrq")
        print
        print('Oxic template choosen')
        print
    elif NOEDLER==True:
        phrq_file=os.path.join(input_folder, "Noedler.phrq")
        print
        print('Noedler template choosen')
        print 
    else:
        phrq_file=os.path.join(input_folder, "Anoxic_template_undetected_sorption.phrq")
        print
        print('Anoxic template choosen')
        print
    lines=None
    try:
        # Read the content of the .phrq file
        with open(phrq_file, 'r') as file:
                lines = file.readlines()
        if ANOXIC ==True:
            lines[106] = '       -parms    '+  f' {parameterlist[0]}\n' #k1
            lines[112] = '       -parms    '+  f'{parameterlist[1]}     \n' # # K2   
            lines[117] = '       -parms    '+  f'{parameterlist[2]}  \n'#   '+  f'{parameterlist[4]}     '+f'{parameterlist[5]}\n' # K6   #k_s,Corg  #k_s,NO3 
            lines[122] = '       -parms    '+  f'{parameterlist[3]}     '+  f'{parameterlist[4]}\n'#K7  #k_I,NO3 
            lines[130] = '       -parms    '+  f'{parameterlist[5]}     '+  f'{parameterlist[6]}\n'#K8 #K_(s,SMX)# k_l,Corg   
            lines[135] = '       -parms    '+  f' {parameterlist[7]}\n' #K9
            lines[141] = '       -parms    '+  f' {parameterlist[8]}\n' #K10
            lines[146] = '       -parms    '+  f' {parameterlist[9]}\n' #K11
            lines[151] = '       -parms    '+  f' {parameterlist[10]}\n' #K12
            lines[156] = '       -parms    '+  f' {parameterlist[11]}\n' #K13
            lines[161] = '       -parms    '+  f' {parameterlist[12]} '+  f'{parameterlist[13]}\n' #K14
            lines[166] = '       -parms    '+  f' {parameterlist[14]}\n' #K15
            lines[169] =  '	     -parms    '+  f' {parameterlist[15]}\n' #K16
            lines[301] = '	-file    '+ f'{sel_file_path}\n'
        if OXIC== True:
            lines[105] = '       -parms    '+  f' {parameterlist[0]}\n' #k1
            lines[111] = '       -parms    '+  f'{parameterlist[1]}     \n' # # K2    
            lines[116] = '       -parms    '+  f'{parameterlist[2]}   \n' #K3 #K_s,C_org  #k_s,O2DOC
            lines[121] = '       -parms    '+  f'{parameterlist[3]}   \n'#K4 #k_s,O2,NH4 #k_s,NH4 
            lines[126] = '       -parms    '+  f'{parameterlist[4]} \n'# K5   #ks,O2,NO3 #ks,NO2
            lines[134] = '       -parms    '+  f'{parameterlist[5]}     '+  f'{parameterlist[6]}\n'#K8 #K_(s,SMX)# k_l,Corg   
            lines[139] = '       -parms    '+  f' {parameterlist[7]}\n' #K9
            lines[145] = '       -parms    '+  f' {parameterlist[8]}\n' #K10
            lines[150] = '       -parms    '+  f' {parameterlist[9]}\n' #K11
            lines[155] = '       -parms    '+  f' {parameterlist[10]}\n' #K12
            lines[160] = '       -parms    '+  f' {parameterlist[11]}\n' #K13
            lines[165] = '       -parms    '+  f' {parameterlist[12]} '+  f'{parameterlist[13]}\n'  #K14
            lines[170] = '       -parms    '+  f' {parameterlist[14]}\n' #K15
            lines[173] =  '	     -parms    '+  f' {parameterlist[15]}\n' #K16
            lines[316] = '	-file    '+ f'{sel_file_path}\n'
        if NOEDLER ==True:
            lines[76] = '       -parms    '+  f' {parameterlist[0]}\n' #k1
            lines[82] = '       -parms    '+  f'{parameterlist[1]}     \n' # # K2   
            lines[87] = '       -parms    '+  f'{parameterlist[2]}  \n'#   '+  f'{parameterlist[4]}     '+f'{parameterlist[5]}\n' # K6   #k_s,Corg  #k_s,NO3 
            lines[92] = '       -parms    '+  f'{parameterlist[3]}     '+  f'{parameterlist[4]}\n'#K7  #k_I,NO3 
            lines[99] = '       -parms    '+  f'{parameterlist[5]}     '+  f'{parameterlist[6]}\n'#K8 #K_(s,SMX)# k_l,Corg   
            lines[105] = '       -parms    '+  f' {parameterlist[7]}\n' #K9
            lines[111] = '       -parms    '+  f' {parameterlist[8]}\n' #K10
            lines[116] = '       -parms    '+  f' {parameterlist[9]}\n' #K11
            lines[121] = '       -parms    '+  f' {parameterlist[10]}\n' #K12
            lines[126] = '       -parms    '+  f' {parameterlist[11]}\n' #K13
            lines[131] = '       -parms    '+  f' {parameterlist[12]} '+  f'{parameterlist[13]}\n' #K14
            lines[136] = '       -parms    '+  f' {parameterlist[14]}\n' #K15
            lines[140] =  '	     -parms    '+  f' {parameterlist[15]}\n' #K16
            lines[273] = '	-file    '+ f'{sel_file_path}\n'
        if HEHE_BED== True: 
            lines [52]= '    log_k -99.07\n' #Nitro
            lines [55]= '    log_k -99.53\n' #DES 
            lines [58]= '    log_k -99.8\n' #Ammet 
            lines [61]= '    log_k -100.43\n' #SMX 

        if TUGOU_BANK== True: 
            lines[76]= '    Doc       1e-5\n ' 
            lines [52]= '    log_k -99.98\n' #Nitro
            lines [55]= '    log_k -99.26\n' #DES
            lines [58]= '    log_k -99.5\n' #Ammet 
            lines [61]= '    log_k -99.99\n' #SMX
    except Exception as e:
        print(f"Error: {e}")

    if lines:
        # Save it with an individual name to the input folder:
        savename = os.path.join(inputdir, f'inputf_{model_name}.phrq')
        try:
            with open(savename, 'w') as file:
                file.writelines(lines)
            print(f'Input file {n} successfully created.')
        except Exception as e:
            print(f"Error while saving the file: {e}")
            return None
        
        return savename
    else:
        print("No lines were read from the input file.")
        return None
        


def run_your_code_get_result(X,script_dir,sel_file_path, add_samplenumber,n=0):
    #generate inputfile:
    inputfile = generate_inputf(X,script_dir,input_folder,n=n)

    
    if os.name == "nt":
        DATABASE = ("D:/phreeqc/database/phreeqc.dat     "  )
        SCR = ("    scr.out")
        EXECUTABLE = ("D:/phreeqc/exec/Release/phreeqc.exe   ")
        INPUT=os.path.join(script_dir,'m_input/',inputfile)
        OUTPUT=os.path.join(script_dir, f"output\{filename_without_extension}.out")
    else:
        DATABASE= "/Users/SMX_batch_model/bin/phreeqc_P.dat"
        EXECUTABLE = "phreeqc" 
        INPUT=os.path.join(script_dir,f'm_input_{model_name}/',inputfile)
        SCR = ("    scr.out")
        OUTPUT=os.path.join(outputdir, "Results.out")

    # os.chdir(terminaldir)
    # with open('terminal_out_'+str(n)+'.txt','w') as f:
    #     subprocess.call( [EXECUTABLE,INPUT , OUTPUT, DATABASE, SCR], stdin=f, stdout=f, stderr=f)
   
    
    subprocess.call( [EXECUTABLE,INPUT , OUTPUT, DATABASE, SCR]) #, stdin=f, stdout=f, stderr=f)
    #read the model output into df and prepare:
    df_modelresult = pd.read_table(sel_file_path, engine="python")#sep=r"\t\s+",
    
    #contruct a filename and save it
    output_fname = 'm_result_'+add_samplenumber+'_'+str(n)+'.csv'
    df_modelresult.to_csv(os.path.join(resultdir,output_fname))
    os.chdir(script_dir)
    
    return df_modelresult, output_fname



############################################################
#Set up Sensitivity problem:
############################################################

# Define the model inputs
    
'''user-input'''
'''insert variable names, number of variables and ranges here:'''

if OXIC==True:
    no_var = 16
    p_names = ['K1','K2', 'K3','K4','K5','K8','KL_DOC','K9','K10','K11','K12','K13','K14','Kl_NO3','K15','K16']
    problem = {'num_vars': no_var,
            'names': p_names,
            'bounds': [[1e-3, 1],   #K1
                        [1e-6,1e-2],   #K2
                        [1e2,5e4],  #K3
                        [1e2, 9e5], #K4
                        [1e2, 9e5], #K5
                        [3e-2,3e-1], #K8
                        [1.6315e-07,3e-4], #'KL_DOC'
                        [1e11,1e17], #K9
                        [1e9,1e15], #K10
                        [10,1e5], #K11
                        [1.5e1,1e7], #K12
                        [1e-2,5e2], #K13
                        [1e-2,5e2], #K14
                        [1e-7,2e-4], #K_lNO3
                        [1,5e5], #K15
                        [1,5e2]] #K16
            }
if ANOXIC==True or NOEDLER ==True:
    no_var=16
    p_names = ['K1','K2', 'K6','K7','KL_NO3','K8','KL_DOC','K9','K10','K11','K12','K13','K14','Kl_NO3','K15','K16']
    problem = {'num_vars': no_var,
            'names': p_names,
            'bounds': [[1e-3, 1],   #K1
                        [1e-6,1e-2],   #K2
                        [1e2,1e4],  #K6
                        [10, 1e4], #K7
                        [1e2, 9e5], #Kl_NO3
                        [3e-2,3e-1], #K8
                        [1.6315e-07,3e-4], #'Kl_DOC'
                        [1e11,1e17], #K9
                        [1e9,1e15], #K10
                        [10,1e5], #K11
                        [1.5e1,1e7], #K12
                        [1e-2,5e2], #K13
                        [1e-2,5e2], #K14
                        [1e-7,2e-4], #K_lNO3
                        [1,5e5], #K15
                        [1,5e2]] #K16
            }
# Restart yes no ?

Restart = False
#do the sensitivity analysis for multiple 
# 
# 
# 
# 
# 
# 
# 
# 
#  sample sizes to test convergence:
'''user-input'''
'''define the sample sizes here to check for convergence, these will be analyzed one after the other'''


#sample_variation = [50,100,200,300,600,800,1200]
sample_variation = [2]
#specify the save path here, a new folder will be generated inside:
#script_dir = os.getcwd()
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))


if os.path.isdir(os.path.join(script_dir,f'output_{model_name}')) == False:
    os.mkdir(os.path.join(script_dir,f'output_{model_name}'))
terminaldir = os.path.join(script_dir,f'output_{model_name}')
sel_file_path=os.path.join(terminaldir,'Results.sel')


#generate empty dataframes for Sobol indices sotring:
df_ST = pd.DataFrame()
df_S1 = pd.DataFrame()
df_S2 = pd.DataFrame()
df_ST['names']=df_S1['names']=p_names

df_ST_conf = pd.DataFrame()
df_S1_conf = pd.DataFrame()
df_S2_conf = pd.DataFrame()
df_ST_conf['names']=df_S1_conf['names']=p_names

already_sampled = df_ST.columns.tolist()

#First setting up Folder for saving or restarting:
soboldir = os.path.join(script_dir, f'SobolInformation_{model_name}')
os.makedirs(soboldir, exist_ok=True)

if Restart == True:
    #Load all Sobol restart infos
    os.chdir(soboldir)
    df_ST = pd.read_csv('df_ST.csv',index_col = 0)
    df_S1 = pd.read_csv('df_S1.csv',index_col = 0)
    df_S2 = pd.read_csv('df_S2.csv',index_col = 0)
    df_ST_conf = pd.read_csv('df_ST_conf.csv',index_col = 0)
    df_S1_conf = pd.read_csv('df_S1_conf.csv',index_col = 0)
    df_S2_conf = pd.read_csv('df_S2_conf.csv',index_col = 0)
    already_sampled = df_ST.columns.tolist()
    del already_sampled[0:1]


#starting the actual Sensitivity Analysis here:
for eachsamplenumber in sample_variation:
    

    #checking if restart information exists
    #if the sample number was already calculated skip it and check the next one:
    no_samples = (no_var*2+2)*eachsamplenumber
    
    if (str(no_samples) in already_sampled) == False:    
        param_values = saltelli.sample(problem, eachsamplenumber)#generates N*(2*D+2)samples D = number of inputs = 6; N = userinput
        
        Y = np.zeros([param_values.shape[0]])
        
        #generate empty df to store parametercombinations and corresponding filenames:
        df_head = pd.DataFrame(data = param_values,columns = p_names)
        df_head['filenames']=np.nan
        df_head['R2']=np.nan 
    
        
        #just some console output and convenience stuff:
        print
        print(str(no_samples)+' satelli samples generated!')
        print('Start calculating models for these samples:')
        print
        l = len(param_values)
        t1 = time.time()
        print_progress(0, l, prefix = 'Progress:', suffix = 'Complete', bar_length = 50)
        
        
        
        for i, X in enumerate(param_values):
            
            #Calculate your model with parameter combination X here:
            
            generate_inputf(X,script_dir,input_folder)
            result_df, output_fname = run_your_code_get_result(X,script_dir,sel_file_path, str(eachsamplenumber),n=i) 
            df_head.loc[i,'filenames']=output_fname
            
            #Calculate your final parameter(f_val) from the mdoel results here:
            if len(result_df)<280:
                f_val=0
                Y[i]=f_val
                df_head.loc[i,'R2']=f_val
                df_head.loc[i,'filenames']=output_fname
            else:
                if OXIC ==True:
                    rows= [20,140,280,700] 
                    from R_get_measured_val import DES, Nitro,SMX, Ammet
                    meas=DES+Ammet+Nitro+SMX
                else:
                    rows=[20,140,280]                
                    from R_get_measured_val import DES, Nitro,SMX,SMX,SDZ,SMZ, Ammet
                    meas=DES+Ammet+Nitro+SMX

                mod_DES=result_df.iloc[rows, 28].tolist()
                mod_Nitro=result_df.iloc[rows, 33].tolist()
                mod_Ammet=result_df.iloc[rows, 27].tolist()
                mod_SMX=result_df.iloc[rows, 24].tolist()
                mod= mod_DES+mod_Ammet+mod_Nitro +mod_SMX
            
                mod_series=pd.Series(mod)
                meas_series=pd.Series(meas)
                print(f"Modeled values (mod_series):\n{mod}")
                print(f"Measured values (meas_series):\n{meas}")

                f_val = R2 (meas_series, mod_series)#calc_final_value_from_model_result(result_df,script_dir)
            #save the final value to correpsonding head file line:
                df_head.loc[i,'R2']=f_val 
            
            #Save it to array:
                Y[i] = f_val
            
            
            
            
            #just some console output and convenience stuff:
            #update progressbar:
            print_progress(i + 1, l, prefix = 'Progress:', suffix = 'Complete', bar_length = 50)
        
        
        
        
        
        
        #Do the Sobol Analysis here:
        Si = sobol.analyze(problem, Y)
            
    
        #storing sobol indices
        df_S1[no_samples]=Si['S1']
        df_ST[no_samples]=Si['ST']
        df_secondorder = pd.DataFrame(Si['S2'])
        df_secondorder['sample_no']=no_samples
        df_S2 = pd.concat([df_S2,df_secondorder])
        
        #storing confidence intervals:
        df_S1_conf[no_samples]=Si['S1_conf']
        df_ST_conf[no_samples]=Si['ST_conf']
        df_secondorder_conf = pd.DataFrame(Si['S2_conf'])
        df_secondorder_conf['sample_no']=no_samples
        df_S2_conf = pd.concat([df_S2_conf,df_secondorder_conf])
    
        #save this information to csv
        #for every iteration of this for loop the saved files will be updated/overridden:
    
        #saving sobol indices to csv:
        df_S1.to_csv(os.path.join(soboldir,'df_S1.csv'))
        df_S2.to_csv(os.path.join(soboldir,'df_S2.csv'))
        df_ST.to_csv(os.path.join(soboldir,'df_ST.csv'))
        
        
        #saving sobol confidence intervals to csv:
        df_S1_conf.to_csv(os.path.join(soboldir,'df_S1_conf.csv'))
        df_S2_conf.to_csv(os.path.join(soboldir,'df_S2_conf.csv'))
        df_ST_conf.to_csv(os.path.join(soboldir,'df_ST_conf.csv'))
        
        
        
        #save headfile information to csv
        #for every iteration of this for loop a new headfile will be saved, see sample_variation:
        if os.path.isdir(os.path.join(script_dir,'Headfiles')) == False:
                os.mkdir(os.path.join(script_dir,'Headfiles'))
        
        headdir = os.path.join(script_dir,'Headfiles')
        headname = 'head_'+str(eachsamplenumber)+'.csv'
        df_head.to_csv(os.path.join(headdir,headname))
        
        
        #just some console output and convenience stuff:
        t2 = time.time()
        t_s=basic_func.tidy(t2-t1,4)
        t_m=basic_func.tidy((t2-t1)/60,3)
        t_h=basic_func.tidy((t2-t1)/3600,2)
        print
        print(str(t_s)+'s/'+str(t_m)+'m/'+str(t_h)+'h elapsed to finish sample batch')
        print



#just some console output and convenience stuff:
print 
print('Everything done! Sensitivity Analysis finished :)')
print



