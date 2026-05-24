import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import os 
import configparser
from datetime import datetime 
import sys
import pandas as pd 
from matplotlib.ticker import MaxNLocator, FuncFormatter, ScalarFormatter


###########################################################################################################################
'''
Create graphs of the measured and modelled data from the columns 
'''
###########################################################################################################################
# Set LaTeX rendering for text
plt.rcParams.update({
    "font.serif": ["Arial"],
    "font.size": 17
})

script_dir = os.path.dirname(os.path.abspath(__file__))

# read all information from configfile
if len(sys.argv) > 1:
    configfn = sys.argv[1]
else:
    configfn = os.path.join(script_dir,"Controle_file.conf")

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(configfn)


SELFILE= config.get("system", "SELFILE", fallback=True)
sel_file_path = os.path.join(script_dir,SELFILE )


plot_folder = os.path.join(script_dir, "plots_calibrated")
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")
sel_folder = os.path.join(script_dir, "Sel_files")


os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

N_COL= config.get("column", "col_no", fallback=4)

#open the measurement file specified in Control_file.config

OXIC= config.getboolean("batch", "OXIC", fallback=True)
ANOXIC= config.getboolean("batch", "ANOXIC", fallback=True)
HEHE_BED= config.getboolean("site", "HEHE_BED", fallback=True)
TUGOU_BANK =config.getboolean("site", "TUGOU_BANK", fallback=True) 
NOEDLER =config.getboolean("validation", "NOEDLER", fallback=True) 
AMMET=config.getboolean("batch", "AMMET", fallback=True) 


parent_dir1 = os.path.abspath(os.path.join(script_dir, os.pardir))
parent_dir = os.path.abspath(os.path.join(parent_dir1, os.pardir))
meas_dir= os.path.join(parent_dir,'Measurements')
excel_file_path = os.path.join(meas_dir, 'Ma_2021_measurements.xlsx')



SMX_x_anoxic=[0, 2, 14, 28,70]
anoxic_specific_points_x = [2, 14, 28,70]
specific_points_x = [2, 14, 28]
Time_3x_Nspecies = [0,15,28]
DO_meas_time=[1,4,7,11,14,20,30]

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

def get_measured_values(average, std, av_N,std_N):
    global NH4_3, NO2_3, NO3_3,NH4_3_std, NO2_3_std, NO3_3_std, DES_meas, std_deviations_Des, Nitro_anoxic_specific_points_y
    global std_deviations_Nitro, SMX_meas, SMX_std_deviations_N, Ammet_oxic_y, std_deviations_Ammet
    global SDZ, SDZ_std, SMZ, SMZ_std,O2,  Undet_meas
    NH4_3= df_N.iloc[av_N, [2, 5, 8]].tolist()#[0, 3.57E-04	,1.92E-04]#mol/L
    print(NH4_3)
    NH4_3_std= df_N.iloc[std_N, [2, 5, 8]].tolist()
    print(NH4_3_std)
    NO2_3= df_N.iloc[av_N+30, [2, 5, 8]].tolist()#[0.00E+00,	3.45E-05	,2.30E-07]#mol/L
    print(df_N.iloc[33,5])
    NO2_3_std= df_N.iloc[std_N+30, [2, 5, 8]].tolist()#[2.19E-04	,1.30E-04	,8.81E-05]#mol/L
    NO3_3= df_N.iloc[av_N+60, [ 5, 8]].tolist()
    print(NO3_3)
    NO3_3_std= df_N.iloc[av_N+60, [ 5, 8]].tolist()
    NO3_3.insert(0,0.000218854 )
    NO3_3_std.insert(0,0)
    print(NO3_3)    
    DES_meas= df.iloc[average, [6, 12, 18,25]].tolist()
    std_deviations_Des = df.iloc[std, [6, 12, 18,25]].tolist()
    print(std_deviations_Des)

    Nitro_anoxic_specific_points_y = df.iloc[average, [7, 13, 19,25]].tolist()
    print(Nitro_anoxic_specific_points_y)
    std_deviations_Nitro = df.iloc[std, [7,13,19,25]].tolist()
    print(std_deviations_Nitro)

    SMX_meas =df.iloc[average, [3,9,15,21]].tolist()
    
    SMX_std_deviations_N = df.iloc[std, [3,9,15,21]].tolist()
    SMX_std_deviations_N.insert(0, 0)
    Ammet_oxic_y = df.iloc[average, [5,11,17,23]].tolist()
    std_deviations_Ammet= df.iloc[std, [5,11,17,23]].tolist()
    print(Ammet_oxic_y)

    SMZ=df.iloc[average, [4, 10, 16,22]].tolist()
    SDZ= df.iloc[average, [2, 8, 14,20]].tolist()
    SMZ_std=df.iloc[std, [4, 10, 16,22]].tolist()
    SDZ_std= df.iloc[std, [2, 8, 14,20]].tolist()
    SDZ.insert(0, 3.95E-08)
    SMZ.insert(0, 3.95E-08)
    SDZ_std.insert(0, 0)
    SMZ_std.insert(0, 0)
    
    SMX_init= 3.95E-08
    # # 'Calculate the Undet /measured/ concentrtaion for mass balance to plot it'
    #undet 
    SMX_u = pd.DataFrame(SMX_meas)
    DES_u = pd.DataFrame(DES_meas)
    Nitro_u = pd.DataFrame(Nitro_anoxic_specific_points_y)
    Ammet_u = pd.DataFrame(Ammet_oxic_y)

    # # # Set columns
    DES_u.columns = SMX_u.columns
    Nitro_u.columns = SMX_u.columns
    Ammet_u.columns = SMX_u.columns

    # # # Sum the DataFrames
    Sum = SMX_u + DES_u + Nitro_u + Ammet_u

    # # # Subtract SMX_init from each element in the Sum DataFrame
    SMX_init = 3.9482e-08
    Undet_df = SMX_init-Sum
    print(Sum, Undet_df)
    Undet_mea = Undet_df.values.tolist()
    # Flatten the list and remove NaN values
    Undet_meas = [float(value[0]) for value in Undet_mea if not np.isnan(value[0])]
    SMX_meas.insert(0, 3.95E-08)


if HEHE_BED ==True: 
    get_measured_values(0,1,3,4)
    DO_meas=[8.2,	7.78	,8.02	,7.84	,7.76	,7.4,	7.12]
    DO_mol_L = [x / 32000 for x in DO_meas]

    filename= "Oxic_Hehe_Bed_Sorption.png"
    plottitle='Oxic Batch Hehe Riverbed inkl. Sorption\n'


if TUGOU_BANK == True: 
    get_measured_values(10,11,23,24)
    DO_meas=[8.62,	9	,9.15	,8.88	,8.86	,8.38,	8.41]
    DO_mol_L = [x / 32000 for x in DO_meas]

    filename= "Oxic_Tugou_Bank_Sorption.png"
    plottitle='Oxic Tugou riverbank incl. sorption\n'


Postprocessing_results_path= os.path.join(script_dir, "Post_processing")
# output_file = '02_extracted_modelled_values.txt'
# output_file_dir= os.path.join(Postprocessing_results_path,output_file)
# all_mod_values = pd.read_csv(output_file_dir)

def process_sel_files(directory):
     data_arrays = []
     for filename in os.listdir(Postprocessing_results_path):
         if filename.startswith('Results_') and filename.endswith('.sel'):
             file_path = os.path.join(Postprocessing_results_path, filename)
             with open(file_path, 'r') as file:
                 data = np.loadtxt(file,skiprows=1)
                 data_arrays.append(data)
     return data_arrays


def process_each_interes(col_number):
    data_arrays = []
    time_column = None  # Placeholder for the Time column

    # Iterate over files in the directory
    for idx, filename in enumerate(os.listdir(Postprocessing_results_path)):
        if filename.startswith('Results_') and filename.endswith('.sel'):
            file_path = os.path.join(Postprocessing_results_path, filename)
            with open(file_path, 'r') as file:
                data = np.loadtxt(file, skiprows=1)
                # Append the desired column to data_arrays
                data_arrays.append(data[:, col_number])
    
    # Combine data arrays into a DataFrame
    df = pd.DataFrame(data_arrays).T
    
    # Add the Time column to the DataFrame (displayed once)
    df.insert(0, 'Time', time_column)  # Insert Time as the first column

    # Calculate mean and standard deviation across columns
    df['mean'] = df.mean(axis=1)
    df['std_dev'] = df.std(axis=1)
    df['min'] = df.min(axis=1)
    df['max'] = df.max(axis=1)

    df['lower_bound'] = df['mean'] - df['std_dev']
    df['upper_bound'] = df['mean'] + df['std_dev']
    return df

HNO2= process_each_interes(7)
NO2 = process_each_interes(6)
NO3 = process_each_interes(5)
DOC= process_each_interes(1)
SMX = process_each_interes(24)
DES = process_each_interes(28)
Nitro = process_each_interes(33)
Ammet = process_each_interes(27)
Undet= process_each_interes(48)
DO=process_each_interes(3)

data_arrays = process_sel_files(Postprocessing_results_path)

def convert_to_float(data):
    """
    Converts data to float. Handles NumPy arrays, lists, and pandas.Series gracefully.
    """
    if isinstance(data, np.ndarray):
        return data.astype(float)
    elif isinstance(data, list):
        return [float(x) for x in data]
    elif isinstance(data, pd.Series):
        return data.astype(float).to_numpy()
    else:
        raise ValueError(f"Unsupported data type for conversion: {type(data)}")

def plot_species(ax, species_data, x_measured, measured_values, measured_std, label, colors, linestyle='solid'):
    """
    Plots the mean, upper and lower bounds for a species, including optional measured data with error bars.

    Parameters:
        ax: Matplotlib Axes object
        species_data: Dictionary with keys 'mean', 'upper_bound', and 'lower_bound'
        x_measured: List of measured x values
        measured_values: List of measured y values
        measured_std: List of standard deviations for error bars (optional)
        label: Label for the species
        colors: Tuple of colors for the plots (line color, fill color)
        linestyle: Line style for the mean plot (default is 'solid')
    """
    # Convert species data to float if necessary
    mean = convert_to_float(species_data['mean'])
    upper = convert_to_float(species_data['max'])
    lower = convert_to_float(species_data['min'])

    # Plot the mean and confidence interval
    line, = ax.plot(Time, mean, color=colors[0], label=label, linestyle=linestyle)
    ax.fill_between(Time, lower, upper, color=colors[1], alpha=0.2)

    scatter = None
    if measured_values:
        scatter = ax.scatter(x_measured, measured_values, color=colors[0], marker='s')
        if measured_std:
            for i, x_point in enumerate(x_measured):
                ax.errorbar(x_point, measured_values[i], yerr=measured_std[i], color=colors[0], capsize=5, capthick=1.5)

    return line, scatter

def plot_summarized_paper(data_arrays, filename):
    """
    Function to plot summarized paper data.
    """
    # Colors for different species
    colors = {
        'HNO2': ('black', 'gray'),
        'NO2': ( 'blue','lightblue'),
        'NO3': ( 'green','lightgreen'),
        'SMX': ('black', 'gray'),
        'DES': ( 'green','limegreen'),
        'Nitro': ( 'blue','deepskyblue'),
        'DOC': ('black', 'dimgrey'),
        'Ammet': ( 'red','coral'),
        'Undet':('gray', 'gainsboro'),
        'DO':('gray', 'gainsboro')
    }

    fig, ax = plt.subplots(1, 3, figsize=(15, 6), sharex=True)
    fig.suptitle("oxic-T", fontsize=20, y=0.98,x=0.0, ha='left',fontweight='bold')

    for i, data in enumerate(data_arrays):
        if i == 0:  # Only plot for i=0
            global Time
            Time = convert_to_float(data[:, 0])  # Ensure Time is a float array
            # Disable scientific notation for x-axis
    # Set x-axis to display integer values
    for subplot in ax:
        subplot.set_xlabel('Time [d]')
        #subplot.set_ylabel('[mol/L]')
        
    # Set x-axis ticks to integers
        subplot.xaxis.set_major_locator(MaxNLocator(integer=True))
        # Disable scientific notation by formatting the x-axis labels as plain integers
        subplot.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))
        # Set the y-axis to use scientific notation
        scalar_formatter = ScalarFormatter()
        scalar_formatter.set_scientific(True)  # Ensure scientific notation is used
        scalar_formatter.set_powerlimits((-3, 3))  # Set where to switch between scientific and plain notation
        subplot.yaxis.set_major_formatter(scalar_formatter)

        # Optional: Adjust the font size of the scientific notation offset (e.g., x10^-5)
        subplot.yaxis.get_offset_text().set_fontsize(17)

        if subplot == ax[0]:
            subplot.text(0.95, 0.95, 'c)', transform=subplot.transAxes, fontsize=17, verticalalignment='top', horizontalalignment='right')
        elif subplot == ax[1]:
            subplot.text(0.95, 0.95, 'd)', transform=subplot.transAxes, fontsize=17, verticalalignment='top', horizontalalignment='right')
        elif subplot == ax[2]:
            subplot.text(0.15, 0.95, 'f)', transform=subplot.transAxes, fontsize=17, verticalalignment='top', horizontalalignment='right')


    # Plot 1: SMX, DES, Nitro, Undet
    ax3 = ax[0].twinx()
    lines_2 = [
        plot_species(ax[0], SMX, SMX_x_anoxic, SMX_meas, SMX_std_deviations_N, 'SMX', colors['SMX']),
        plot_species(ax[0], Undet, anoxic_specific_points_x , Undet_meas,  [], 'Undet', colors['Undet'], linestyle='dotted'),
        plot_species(ax[0], DES, anoxic_specific_points_x, DES_meas, std_deviations_Des, 'DeA-SMX', colors['DES']),
        plot_species(ax3, Nitro, anoxic_specific_points_x, Nitro_anoxic_specific_points_y, std_deviations_Nitro, 'Nit-SMX', colors['Nitro'])
        

    ]
    handles_2 = [handle for line, scatter in lines_2 for handle in (line, scatter) if handle]
    ax[0].legend(handles=handles_2, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3,fontsize=17)
    #ax3.set_ylabel('Nit-SMX [mol/L]')
    ax[0].set_ylim(0,4.10e-8)
    ax3.set_ylim(0,1.5e-10)
    ax[0].set_xlim(-0.5,72)
    ax3.set_xlim(-0.5,72)
    ax[0].set_ylabel('[mol/L]')
    ax3.tick_params(axis='y', colors='blue') 
    ax[0].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax3.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))


    # Plot 2: DOC, AmMet, and DO with separate y-axes for DOC and AmMet
    ax4 = ax[1].twinx()  # Second y-axis for AmMet

    # Plot species
    lines_3 = [
        plot_species(ax[1], DOC, anoxic_specific_points_x, [], [], r'CH$_2$O', colors['DOC'], linestyle='dashdot'),  # DOC on ax5
        plot_species(ax4, Ammet, anoxic_specific_points_x, Ammet_oxic_y, std_deviations_Ammet, 'AmMet', colors['Ammet']),  # AmMet on ax4
        plot_species(ax[1], DO, DO_meas_time, DO_mol_L, [], 'DO', colors['DO'], linestyle='--'),  # DO on ax[1]
    ]

    # Collect handles for legend
    handles_3 = [handle for line, scatter in lines_3 for handle in (line, scatter) if handle]
    ax[1].legend(handles=handles_3, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=17)


    # Set limits
    ax4.set_ylim(0, 0.5e-8)
    ax[1].set_ylim(1e-5, 1e-04)
    ax[1].set_xlim(0, 72)
    ax4.set_xlim(0, 72)
    ax4.tick_params(axis='y', colors='red') 


    # Use scientific notation for y-axes
    ax[1].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax4.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))

    ax4.yaxis.get_offset_text().set_position((1, 1.05))   # Slightly above default

    formatter4 = ScalarFormatter(useMathText=True)
    formatter4.set_powerlimits((-3, 3))
    ax4.yaxis.set_major_formatter(formatter4)

    formatter1 = ScalarFormatter(useMathText=True)
    formatter1.set_powerlimits((-3, 3))
    ax[1].yaxis.set_major_formatter(formatter1)


    # Plot 3: DO
        # Plot for Subplot 1
    ax1 = ax[2].twinx()
    lines_1, scatters_1 = [], []
    lines_1.append(plot_species(ax[2], NO2, Time_3x_Nspecies,  [], [], r'$NO_{2}$', colors['NO2'],linestyle='dashdot'))
    lines_1.append(plot_species(ax[2], NO3, Time_3x_Nspecies, [], [], r'$NO_{3}$', colors['NO3'],linestyle='dashdot'))
    lines_1.append(plot_species(ax1, HNO2, Time_3x_Nspecies, [], [],  r'$HNO_{2}$', colors['HNO2'],linestyle='dashdot'))

  # Combine legends for Subplot 1
    handles, labels = [], []
    for line, scatter in lines_1:
        handles.append(line)
        if scatter:
            handles.append(scatter)
    ax[2].legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.2),ncol=2)
    ax1.tick_params(axis='y', colors='blue')  
    ax[2].set_ylim(-0.1e-4,1.0e-4)
    ax1.set_ylim(-0.1e-16,3e-16)
    ax[2].set_xlim(-0.5,30)
    ax1.set_xlim(-0.5,30)
    
    ax[2].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax[2].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax[2].yaxis.get_major_formatter().set_powerlimits((-3, 3))
    #fig.suptitle(plottitle, fontsize=16)
    fig.tight_layout()
    save_path = os.path.join(plot_folder, filename)
    plt.savefig(save_path)

plot_summarized_paper(data_arrays,filename='R08_Fig3_Tugou_oxic.png')

    
