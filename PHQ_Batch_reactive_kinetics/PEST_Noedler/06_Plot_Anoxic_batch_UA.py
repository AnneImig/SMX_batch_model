
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


Postprocessing_results_path= os.path.join(script_dir, 'Post_processing')
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")
plot_folder = os.path.join(script_dir, "plots_calibrated")
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(plot_folder, exist_ok=True)


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
noedler_meas = os.path.join(parent_dir, 'Nödler_2012_measurements.xlsx')

Noedler = pd.read_excel(noedler_meas, sheet_name=0)


if NOEDLER ==True: 
    filename= "Noedler.png"
    Noedler = pd.read_excel(noedler_meas, sheet_name=0)

    NO2_meas= Noedler.iloc[0:9, 2].tolist() #[0.00E+00,	3.45E-05	,2.30E-07]#mol/L
    NO2_meas_std=[value * 0.1 for value in NO2_meas]
    NO3_meas= Noedler.iloc[0:9, 1].tolist()
    NO3_meas_std=[value * 0.1 for value in NO3_meas]
    DOC_meas= Noedler.iloc[ 0:9, 3].tolist()
    DOC_meas_std=[value * 0.1 for value in DOC_meas]

    SMX_meas=Noedler.iloc[ 0:9,8].tolist()
    SMX_meas_std=[value * 0.1 for value in SMX_meas]
    DES_meas=Noedler.iloc[0:9, 12].tolist()
    DES_meas_std=[value * 0.1 for value in DES_meas]
    Nitro_meas=Noedler.iloc[0:9, 10].tolist()
    Nitro_meas_std=[value * 0.1 for value in Nitro_meas]
    Time_3x_Nspecies=Noedler.iloc[0:9, 0].tolist()
    'Calculate the Undet /measured/ concentrtaion for mass balance to plot it'
    #undet 
    SMX_u = pd.DataFrame(SMX_meas)
    DES_u = pd.DataFrame(DES_meas)
    Nitro_u = pd.DataFrame(Nitro_meas)

    # Set columns
    DES_u.columns = SMX_u.columns
    Nitro_u.columns = SMX_u.columns

    # Sum the DataFrames
    Sum = SMX_u + DES_u + Nitro_u 

    # Subtract SMX_init from each element in the Sum DataFrame
    SMX_init = 4e-6
    Undet_df = SMX_init-Sum
    print(Sum, Undet_df)
    Undet_mea = Undet_df.values.tolist()
    # Flatten the list and remove NaN values
    Undet_meas = [float(value[0]) for value in Undet_mea if not np.isnan(value[0])]


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

def process_sel_files(directory):
     data_arrays = []
     for filename in os.listdir(Postprocessing_results_path):
         if filename.startswith('Results_') and filename.endswith('.sel'):
             file_path = os.path.join(Postprocessing_results_path, filename)
             with open(file_path, 'r') as file:
                 data = np.loadtxt(file,skiprows=1)
                 data_arrays.append(data)
     return data_arrays



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
    upper = convert_to_float(species_data['upper_bound'])
    lower = convert_to_float(species_data['lower_bound'])

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
    fig.suptitle("anoxic-NDL", fontsize=20, y=0.98,x=0.0, ha='left',fontweight='bold')
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
            subplot.text(0.95, 0.95, 'g)', transform=subplot.transAxes, fontsize=17, verticalalignment='top', horizontalalignment='right')
        elif subplot == ax[1]:
            subplot.text(0.95, 0.95, 'h)', transform=subplot.transAxes, fontsize=17, verticalalignment='top', horizontalalignment='right')
        elif subplot == ax[2]:
            subplot.text(0.95, 0.95, 'i)', transform=subplot.transAxes, fontsize=17, verticalalignment='top', horizontalalignment='right')
    # Plot 1: SMX, DES, Nitro

    lines_2 = [
        plot_species(ax[0], SMX, Time_3x_Nspecies, SMX_meas,  SMX_meas_std, 'SMX', colors['SMX']),
        plot_species(ax[0], Nitro, Time_3x_Nspecies, Nitro_meas, Nitro_meas_std, 'Nit-SMX', colors['Nitro']),
        plot_species(ax[0], DES, Time_3x_Nspecies, DES_meas, DES_meas_std, 'DeA-SMX', colors['DES']),
        plot_species(ax[0], Undet,Time_3x_Nspecies , Undet_meas,  [], 'Undet', colors['Undet'], linestyle='dotted'),

    ]
    # Combine legends for Subplot 1
    handles, labels = [], []
    for line, scatter in lines_2:
        handles.append(line)
        if scatter:
            handles.append(scatter)

    handles = [h for h in handles if not h.get_label().startswith('_')]
    ax[0].legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    ax[0].set_ylabel('[mol/L]')
    ax[0].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax[0].set_xlim(-1, 90)
    ax[0].set_ylim(-0.1e-6, 4.5e-6)
    ax[0].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))

      # Plot 2: DOC and Ammet
    ax4 = ax[1].twinx()
    lines_3 = [
        plot_species(ax[1], DOC, Time_3x_Nspecies, DOC_meas, DOC_meas_std, r'CH$_2$O', colors['DOC'],linestyle='dashdot'),
        plot_species(ax4, Ammet, Time_3x_Nspecies, [], [],'AmMet', colors['Ammet'])
   ]
    handles_2 = [handle for line, scatter in lines_3 for handle in (line, scatter) if handle]
    # Add this filter:
    handles_2 = [h for h in handles_2 if not h.get_label().startswith('_')]
    ax[1].legend(handles=handles_2, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)

    ax4.set_xlim(-1, 90)
    ax4.set_ylim(0, 3.2e-8)
    ax[1].set_ylim(0,0.085)
    ax4.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax4.tick_params(axis='y', colors='red')  
    ax[1].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    # Plot 3: HNO2, NO2, NO3

    ax1 = ax[2].twinx()
    lines_1, scatters_1 = [], []
    lines_1.append(plot_species(ax[2], NO2, Time_3x_Nspecies, NO2_meas, NO2_meas_std, r'$NO_{2}$', colors['NO2'], linestyle='dashdot')),
    lines_1.append(plot_species(ax1, HNO2, Time_3x_Nspecies, [], [], r'$HNO_{2}$',colors['HNO2'],linestyle='dashdot')),
    lines_1.append(plot_species(ax[2], NO3, Time_3x_Nspecies, NO3_meas,NO3_meas_std,r'$NO_{3}$',colors['NO3'],linestyle='dashdot'))
    # Combine legends 
    handles_3, labels = [], []
    for line, scatter in lines_1:
        handles_3.append(line)
        if scatter:
            handles_3.append(scatter)
    handles_3 = [h for h in handles_3 if not h.get_label().startswith('_')]
    ax[2].legend(handles=handles_3, loc='upper center', bbox_to_anchor=(0.5, -0.2),ncol=2)
    #ax1.set_ylabel(r'$HNO_{2} [mol/L]$')
    ax1.set_xlim(-1, 90)
    ax1.set_ylim(-0.1e-6,2.5e-4)
    ax[2].set_ylim(-0.1e-6,0.085)
    ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax1.tick_params(axis='y', colors='blue')  
    fig.tight_layout()
    fig.subplots_adjust(wspace=0.33)
    save_path = os.path.join(plot_folder, filename)
    plt.savefig(save_path)
    plt.show()




def plot_cum_sorption(data_arrays,sorption_filename):
    for i, data in enumerate(data_arrays):
        plt.plot(data[:, 0], data[:, 52], color='blue', label='SMX_Sorbed' if i == 0 else "")
        plt.plot(data[:, 0], data[:, 53], color='violet', label='Ammet_Sorbed' if i == 0 else "")
        plt.plot(data[:, 0], data[:, 54], color='green', label='Nitro_Sorbed' if i == 0 else "")
        plt.plot(data[:, 0], data[:, 55], color='grey', label='DeA_Sorbed' if i == 0 else "")

    plt.yscale('log')
    plt.ylabel('Sorbed Antibiotics (mol/L)', color='black')
    plt.ylim(10**-17, max(data[:, 52]) * 10)  # Assuming max for the first data array
    plt.legend(loc='upper right', fontsize='small')
    #plt.title('Sorbed2')
    plt.gcf().set_facecolor((232/255, 232/255, 232/255))

    plt.tight_layout()
    
    save_path = os.path.join(plot_folder, sorption_filename)

    plt.savefig(save_path)
    plt.show() 




  


def main():
    data_arrays = process_sel_files(Postprocessing_results_path)

    plot_summarized_paper(data_arrays,filename='R6_Fig4_Noedler.png')
    #plot_nitrogen_species(output, 'Nitrogen_species.png')
    #plot_DOC(output, 'DOC.png')

if __name__ == '__main__':
    main()