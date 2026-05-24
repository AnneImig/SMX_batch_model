#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import matplotlib.cm as cm
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import basic_func
import plotting_stuff as pls

# Define folder names
folders = ['SobolInformation_Hehe_oxic', 'SobolInformation_Tugou_oxic','SobolInformation_Hehe_anoxic','SobolInformation_Tugou_anoxic',  'SobolInformation_Noedler']
names= ['oxic-H','oxic-T',[],'oxic-T', 'anoxic-T','anoxic-NDL', ]
# Determine script directory
script_dir = os.path.dirname(os.path.abspath(__file__))


# Define color map and fixed colors for datasets
datasets = ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7','KL_NO3','K8', 'KL_DOC', 'K9', 'K10', 'K11', 'K12', 'K13', 'K14', 'Kl_NO3', 'K14', 'K15','K16'] 
cma = cm.tab20
color_mapping = {name: cma(i / len(datasets)) for i, name in enumerate(datasets)}

# Track legend inclusion globally across subplots
legend_included = {name: False for name in datasets}
legend_rename = {
    'K1': r'$K_{1}$', 'K2': r'$K_{2}$', 'K3': r'$K_{4}$', 'K4': r'$K_{5}$',
    'K5': r'$K_{3}$', 'K6': r'$K_{6}$', 'K7': r'$K_{7}$', 'KL_NO3': r'$K_{l, NO_3^-}$',
    'K8': r'$K_{8}$', 'KL_DOC': r'$K_{l,CH_2O}$', 'K9': r'$K_{9}$', 'K10': r'$K_{10}$',
    'K11': r'$K_{11}$', 'K12': r'$K_{12}$', 'K13': r'$K_{13}$', 'K14': r'$K_{14}$',
    'Kl_NO3': r'$K_{l\prime, CH_2O}$', 'K15': r'$K_{15}$', 'K16': r'$K_{16}$'
}
# Initialize 2x3 subplot
fig = make_subplots(
    rows=2, cols=3,  # 2 rows and 3 columns
    subplot_titles=names, #[f"Data from {folder}" for folder in folders],
    shared_xaxes=False,
    shared_yaxes=False,
    vertical_spacing=0.1,  # Reduce vertical space (0.05 is a small value)
    horizontal_spacing=0.1  # Reduce horizontal space (0.05 is a small value)
)
# Loop over each folder
for i, folder in enumerate(folders):
    cdir = os.path.join(script_dir, folder)
    os.chdir(cdir)

    # Read data

    df_ST = pd.read_csv('df_ST.csv')
    df_ST_conf = pd.read_csv('df_ST_conf.csv')

# Exclude small sample size because it will only show a lot of variability and make the plot hard to read
    if '68' in df_ST.columns:
        df_ST = df_ST.drop(columns=['68'])
        df_ST_conf = df_ST_conf.drop(columns=['68'])
    # Extract x values (sample sizes) and sort
    x = df_ST.columns.tolist()
    x = [float(i) for i in x if i.isdigit()]
    x_sorted = sorted(x)
    sortingindex = [x.index(each) for each in x_sorted]

    # Variable names
    l_names = df_ST['names'].tolist()


    # Get the subplot row and column indices
    if i < 2:  # First two folders go in the first row
        row = 1
        col = i +1  # Columns 1 and 2 for the first row
    else:  # Remaining folders go in the second row
        row = 2
        col = (i - 2) +1  # Columns 1, 2, and 3 for the second row


    # Create traces for this folder
    for eachname in l_names:
        legend_label = legend_rename.get(eachname, eachname)  # Default to `eachname` if not in the dictionary

        # Extract y-values and sort them
        
        y_ST = df_ST.loc[df_ST['names'] == eachname, :].drop(df_ST.columns[[0, 1]], axis=1).values.flatten().tolist()
        y_ST = [y_ST[i] for i in sortingindex]

        y_ST_conf = df_ST_conf.loc[df_ST_conf['names'] == eachname, :].drop(df_ST_conf.columns[[0, 1]], axis=1).values.flatten().tolist()
        y_ST_conf = [y_ST_conf[i] for i in sortingindex]

        # Use the fixed color mapping
        if eachname in color_mapping:
            c = color_mapping[eachname]
        else:
            c = (0, 0, 0)  # Default to black if not found in mapping
        rgb = "rgb(%s, %s, %s)" % (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))

        # Add trace for this variable
        traces = pls.make_scatter_traces_withconfidence(
            [], x_sorted, y_ST, y_ST_conf, legend_label, rgb, style="solid"
        )
        for trace in traces:
            # Show legend only for the first instance of eachname
            trace.showlegend = not legend_included[eachname]
            legend_included[eachname] = True
            fig.add_trace(trace, row=row, col=col)
            # Update x-axis labels with LaTeX formatting


# Layout adjustments
fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12),
    autosize=True,
    showlegend=True,
    legend=dict(
    x=1.1,  # Set the x-position to the far right of the plot (1 is far right)
    y=0,  # Set the y-position to the bottom of the plot (0 is at the bottom)
    xanchor='right',  # Anchor the legend to the right side
    yanchor='bottom'  # Anchor the legend to the bottom side
    )
)
# Custom subplot axis settings
for i in range(1, 4):  # Rows
    for j in range(1, 4):  # Columns
        fig.update_xaxes(
            title_text="Number of Samples" if i == 2 else "",
            showgrid=True, gridcolor="lightgray", row=i, col=j,
            showline=True, linecolor='black', ticks="outside"
        )
        fig.update_yaxes(
            title_text="Sensitivity Index" if j == 1 else "",
            showgrid=True, gridcolor="lightgray", row=i, col=j,
            type="log",  # Set y-axis to logarithmic scale
            range=[-22, 1],  # Set y-axis range from 10^-3 to 10^1
            showline=True, linecolor='black', ticks="outside",
            tickformat=".1e"  # Display tick labels in scientific notation
        )

# Save the plot as PNG
output_dir = os.path.join(script_dir, 'combined_sobol_plots')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_png = os.path.join(output_dir, "02_Fig_S7_combined_sensitivity_plot.png")
fig.write_image(output_png, width=1200, height=1100)

print(f"Plot saved as PNG at: {output_png}")
