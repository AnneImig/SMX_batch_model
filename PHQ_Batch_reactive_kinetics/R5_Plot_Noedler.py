import numpy as np
import matplotlib.pyplot as plt
import os 
import configparser
import sys
import pandas as pd 


print("✓ Script started", flush=True)

# ============================================================================
# SETUP
# ============================================================================

plt.rcParams.update({"font.serif": ["Arial"], "font.size": 12})

script_dir = os.path.dirname(os.path.abspath(__file__))

# Read config
if len(sys.argv) > 1:
    configfn = sys.argv[1]
else:
    configfn = os.path.join(script_dir, "Controle_file.conf")

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(configfn)

# Setup paths
SELFILE = config.get("system", "SELFILE", fallback="Results.sel")
sel_file_path = os.path.join(script_dir, SELFILE)
plot_folder = os.path.join(script_dir, "plots")
os.makedirs(plot_folder, exist_ok=True)

NOEDLER = config.getboolean("validation", "NOEDLER", fallback=True)

print(f"✓ Config loaded: NOEDLER={NOEDLER}", flush=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print(f"✓ Loading modelled data...", flush=True)
try:
    modelled = pd.read_csv(sel_file_path, delimiter='\t')
    modelled.columns = modelled.columns.str.strip()
    print(f"  Shape: {modelled.shape}", flush=True)
except Exception as e:
    print(f"✗ Error: {e}", flush=True)
    exit(1)

# Load measured data
measured = None
if NOEDLER:
    measurement_paths = [
        os.path.join(script_dir, 'No_dler_2012_measurements.xlsx'),
        os.path.join(script_dir, 'Nödler_2012_measurements.xlsx'),
        os.path.join(script_dir, 'Noedler_2012_measurements.xlsx'),
        os.path.join(os.path.dirname(script_dir), 'measurements', 'Nödler_2012_measurements.xlsx'),
    ]
    
    for path in measurement_paths:
        if os.path.exists(path):
            try:
                measured = pd.read_excel(path, sheet_name=0)
                print(f"✓ Found measured data: {path}", flush=True)
                
                # ====== CALCULATE UNDETECTED SMX ======
                # Column 8 is Lich_SMX (measured)
                smx_initial = measured.iloc[0, 8]
                measured['Undetected_measured'] = smx_initial - measured.iloc[:, 8]
                print(f"  ✓ Calculated undetected SMX (initial={smx_initial:.2e})", flush=True)
                break
            except Exception as e:
                print(f"⚠ Error reading {path}: {e}", flush=True)
    
    if measured is None:
        print(f"⚠ Measured data not found", flush=True)
        NOEDLER = False

# ============================================================================
# CONFIGURATION - All plot specs in one place
# ============================================================================

PLOT_CONFIG = {
    (0, 0): {
        'title': 'Nitrogen Species & Organic Carbon',
        'ylabel': 'Concentration [mol/L]',
        'lines': [
            ('NO2-', 'red', '-', 'NO$_{2}^{-}$'),
            ('NO3-', 'blue', '-', 'NO$_{3}^{-}$'),
            ('Doc', 'green', '-', 'CH$_2$O'),     
            ('Docr', 'green', '--', 'DOC'),      
        ],
        'measured_points': [
            ('NO2', 'red', 'o', None, 'NO$_{2}^{-}$'),
            ('NO3', 'blue', 's', None, 'NO$_{3}^{-}$'),
            ('DOC', 'green', '^', None, 'CH$_2$O'),  
        ],
        'secondary': [
            ('HNO2', 'lime', '-', 'HNO$_2$'),
            ('HNO3', 'navy', '-', 'HNO$_3$'),
        ],
    },
    
    (0, 1): {
        'title': 'SMX',
        'ylabel': 'SMX [mol/L]',
        'lines': [
            ('Smx', 'blue', '-'),
            ('Undetected', 'burlywood', '-'),
        ],
        'measured_points': [
            ('SMX', 'red', 's', 0.1),
            ('Undetected_measured', 'burlywood', '^'),
        ],
    },
    
    (0, 2): {
        'title': 'Protonated Nitrogen Species',
        'ylabel': '[mol/L]',
        'lines': [
            ('HNO2', 'lime', '-', 'HNO$_2$'),
            ('HNO3', 'navy', '-', 'HNO$_3$'),
        ],
    },
    
    (1, 0): {
        'title': 'Nit-SMX',
        'ylabel': 'Nit-SMX [mol/L]',
        'lines': [
            ('Nit', 'blue', '-', 'Nit-SMX'),
        ],
        'measured_points': [
            ('Nitro', 'red', 's', 0.1, 'Nit-SMX'),
        ],
        'ylim_min': 0,
    },
    
    (1, 1): {
        'title': 'DES',
        'ylabel': 'DES [mol/L]',
        'lines': [
            ('DES', 'cyan', '-'),
        ],
        'measured_points': [
            ('DES', 'red', 's', 0.1),
        ],
        'ylim_min': 0,
    },
    
    (1, 2): {
        'title': 'AmMet-SMX',
        'ylabel': 'C [mol/L]',
        'lines': [
            ('Ammet', 'blue', '-'),
        ],
    },
    
    (2, 0): {
        'title': 'Rates NIT Metabolites',
        'ylabel': 'Rate',
        'lines': [
            ('rateNit', 'grey', '-', 'R9: SMX$\\to$Nit'),
            ('rateDES_NIT_N', 'grey', '-.', 'R12: DES$\\to$Nit'),
            ('rateNIT_Smx_N', 'purple', '--', 'R13: Nit$\\to$SMX'),
        ],
    },
    
    (2, 1): {
        'title': 'Rates DES Metabolite',
        'ylabel': 'Rate',
        'lines': [
            ('rate_Smx_DES_O', 'red', '-.', 'R11: SMX$\\to$DES'),
            ('rateDes_N', 'green', '-', 'R10: DES$\\to$N'),
            ('rateDES_Smx_O2', 'grey', '--', 'R14: DES$\\to$SMX'),
        ],
    },
    
    (2, 2): {
        'title': 'Rates AmMet metabolite',
        'ylabel': 'Rate',
        'lines': [
            ('rate_Ammet', 'orange', '-', 'R8: SMX-AmMet'),
        ],
    },
}

# Measured column mapping: name -> (column_index, label)
MEASURED_COLS = {
    'NO2': (2, 'NO$_{2}^{-}$'),
    'NO3': (1, 'NO$_{3}^{-}$'),
    'DOC': (3, 'CH$_2$O'),
    'SMX': (8, 'SMX_meas'),
    'DES': (12, 'DES_meas'),
    'Nitro': (10, 'Nit-SMX_meas'),
    'Undetected_measured': ('Undetected_measured', 'Undetected_meas'),
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def add_line(ax, df, col_name, color, linestyle, label=None):
    """Add single line to axis"""
    if col_name not in df.columns:
        return
    ax.plot(df['Time'], df[col_name], color=color, linestyle=linestyle, 
            label=label or col_name, linewidth=1.5)

def add_scatter(ax, x, y, color, marker, label, error_factor=None):
    """Add scatter points with optional error bars"""
    ax.scatter(x, y, color=color, marker=marker, s=60, label=label, zorder=5)
    if error_factor and error_factor > 0:
        yerr = error_factor * np.array(y)
        ax.errorbar(x, y, yerr=yerr, fmt='none', ecolor=color, 
                   capsize=5, capthick=1.5, alpha=0.6)

def format_subplot(ax, title, ylabel, ylim=None, show_grid=False):
    """Apply standard formatting to subplot"""
    ax.set_title(title, fontweight='bold', fontsize=11)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlabel('Time [d]', fontsize=10)
    ax.legend(loc='best', fontsize='small')
    if show_grid:
        ax.grid(True, alpha=0.3)
    else:
        ax.grid(False)
    if ylim:
        ax.set_ylim(ylim)

def format_secondary_axis(ax, title):
    """Format secondary y-axis"""
    ax.set_ylabel(f'{title} [mol/L]', fontsize=9)
    ax.tick_params(axis='y')

# ============================================================================
# MAIN PLOTTING FUNCTION
# ============================================================================

def plot_results(modelled_df, measured_df=None):
    """
    Create all subplots from configuration.
    Zero repetition - config drives everything.
    """
    
    print(f"\n→ Creating plots...", flush=True)
    
    fig, ax = plt.subplots(3, 3, figsize=(16, 12), sharex=True)
    time_mod = modelled_df['Time'].values
    time_meas = measured_df.iloc[:, 0].values if measured_df is not None else None
    
    # Process each subplot
    for (row, col), cfg in PLOT_CONFIG.items():
        axis = ax[row, col]
        
        # Skip empty subplots
        if cfg.get('is_empty'):
            axis.axis('off')
            continue
        
        # Summary subplot
        if cfg.get('is_summary'):
            axis.axis('off')
            summary = f"""Model Summary:
Initial SMX: {modelled_df['Smx'].iloc[0]:.2e} mol/L
Final SMX: {modelled_df['Smx'].iloc[-1]:.2e} mol/L
Duration: {time_mod[-1]:.1f} days
Points: {len(time_mod)}"""
            axis.text(0.05, 0.5, summary, fontsize=10, family='monospace',
                     transform=axis.transAxes)
            continue
        
        # ====== PLOT MODELLED LINES ======
        if 'lines' in cfg:
            for spec in cfg['lines']:
                col_name, color, linestyle = spec[:3]
                label = spec[3] if len(spec) > 3 else None
                add_line(axis, modelled_df, col_name, color, linestyle, label)
        
        # ====== PLOT MEASURED POINTS ======
        if 'measured_points' in cfg and measured_df is not None:
            for spec in cfg['measured_points']:
                meas_name, color, marker = spec[:3]
                error_factor = spec[3] if len(spec) > 3 else None
                custom_label = spec[4] if len(spec) > 4 else None
                
                if meas_name in MEASURED_COLS:
                    col_info = MEASURED_COLS[meas_name]
                    
                    # Handle both numeric column indices and named columns
                    if isinstance(col_info[0], int):
                        col_idx = col_info[0]
                        y_data = measured_df.iloc[:, col_idx].values
                    else:
                        # Named column (e.g., 'Undetected_measured')
                        col_name = col_info[0]
                        y_data = measured_df[col_name].values
                    
                    label = custom_label or col_info[1]
                    add_scatter(axis, time_meas, y_data, color, marker, label, error_factor)
        
        # ====== SECONDARY Y-AXIS ======
        if 'secondary' in cfg:
            ax2 = axis.twinx()
            for spec in cfg['secondary']:
                col_name, color, linestyle = spec[:3]
                label = spec[3] if len(spec) > 3 else col_name
                add_line(ax2, modelled_df, col_name, color, linestyle, label)
            format_secondary_axis(ax2, cfg['title'])
        
        # ====== FORMAT ======
        ylim = None
        if 'ylim_min' in cfg:
            # Auto-calculate max from data
            data_cols = [s[0] for s in cfg.get('lines', [])]
            max_val = max([modelled_df[col].max() for col in data_cols if col in modelled_df.columns])
            ylim = (cfg['ylim_min'], max_val * 1.1)
        
        format_subplot(axis, cfg['title'], cfg['ylabel'], ylim)
    
    # ====== OVERALL FORMATTING ======
    plt.suptitle('Noedler 2012 - Modelled vs Measured (Anoxic Batch)', 
                fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # ====== SAVE ======
    save_path = os.path.join(plot_folder, 'R5_Noedler.png')
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {save_path}", flush=True)
        plt.show()
        return True
    except Exception as e:
        print(f"✗ Error saving: {e}", flush=True)
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    print(f"\n{'='*70}", flush=True)
    print(f"NOEDLER 2012 DATA PLOTTING - CLEAN VERSION", flush=True)
    print(f"{'='*70}", flush=True)
    
    success = plot_results(modelled, measured)
    
    if success:
        print(f"\n✓ Complete!", flush=True)
    else:
        print(f"\n✗ Failed!", flush=True)
    
    print(f"{'='*70}\n", flush=True)

if __name__ == '__main__':
    main()