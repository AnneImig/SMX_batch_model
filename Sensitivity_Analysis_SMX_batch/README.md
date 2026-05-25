# Sobol Sensitivity Analysis for PHREEQC Batch Models

## Overview

This workflow performs **Global Sensitivity Analysis (GSA)** using the **Sobol method** to identify which parameters have the greatest impact on model outputs (SMX fate, metabolite formation, etc.) in PHREEQC batch reaction systems.

The analysis consists of **3 stages**:

1. **Run Sobol Sampling & Analysis** → `01_SA_PHQ_Batch.py`
2. **Plot Sensitivity Results** → `02_Plotting_SI_results.py`
3. **Generate Heatmap Visualization** → `03_Plotting_Heatmap.py`

---



## 1. Configure Your Analysis

Edit `Controle_file.conf`:

```ini
[batch]
OXIC = TRUE        # or FALSE for anoxic
ANOXIC = FALSE     # or TRUE for anoxic

[site]
HEHE_BED = TRUE    # Choose ONE site
TUGOU_BANK = FALSE

[validation]
NOEDLER = FALSE    # Reference/validation site
```

### 2. Run Analysis

```bash
cd /path/to/sensitivity_analysis

# Stage 1: Run Sobol sampling (1-2 hours)
python 01_SA_PHQ_Batch.py

# Stage 2: Plot sensitivity indices
python 02_Plotting_SI_results.py

# Stage 3: Generate heatmap
python 03_Plotting_Heatmap.py
```

---

## Directory Structure

```
sensitivity_analysis/
├── Controle_file.conf              # ← Configuration file
├── 01_SA_PHQ_Batch.py              # ← Stage 1: Sobol analysis
├── 02_Plotting_SI_results.py       # ← Stage 2: Plot results
├── 03_Plotting_Heatmap.py          # ← Stage 3: Generate heatmap
│
├── R_get_measured_val.py           # Load measured data
├── basic_func.py                   # Utility functions
├── plotting_stuff.py               # Plotly visualization tools
├── progressbar.py                  # Progress bar display
├── FiraMono-Medium.otf             # Font file for plots
│
├── input/
│   ├── Anoxic_Hehe_bed_Sorption.phrq
│   ├── Anoxic_Tugou_bank_Sorption.phrq
│   ├── Oxic_Hehe_bed_Sorption.phrq
│   └── Oxic_Tugou_bank_Sorption.phrq
│
├── output/                          # Auto-created
│   ├── Results.sel                 # PHREEQC results
│   └── scr.out                     # Screen output
│
├── SobolInformation_Hehe_oxic/     # Auto-created per site/condition
│   ├── df_ST.csv                   # Total-order indices
│   ├── df_ST_conf.csv              # Confidence intervals
│   └── [other Sobol outputs]
│
├── SobolInformation_Tugou_oxic/
├── SobolInformation_Hehe_anoxic/
├── SobolInformation_Tugou_anoxic/
├── SobolInformation_Noedler/
│
└── combined_sobol_plots/           # Final outputs
    ├── 02_Fig_S7_combined_sensitivity_plot.png
    ├── 03_Figure5_heatmap.png
    └── normalized_values.csv
```

---

## Stage 1: Run Sobol Sensitivity Analysis

### Command

```bash
python 01_SA_PHQ_Batch.py
```

### What It Does

1. **Defines Problem Space**
   - 16-19 parameters with bounds (min/max values)
   - Parameters: K1-K16 (rate constants, partition coefficients, etc.)

2. **Generates Sobol Samples**
   - Uses **Saltelli sampling** for convergence
   - Creates N × (2M + 2) sample sets
   - M = number of parameters (16-19)
   - N = base sample size (typically 256, 512, 1024)
   - Example: N=1024, M=16 → ~33,792 PHREEQC runs

3. **Runs PHREEQC for Each Sample**
   - For each parameter set:
     - Creates input file from template
     - Runs PHREEQC simulation
     - Extracts output (SMX concentration, DES, Nit, etc.)
     - Shows progress bar

4. **Analyzes Results Using Sobol**
   - Calculates S₁ (first-order indices)
   - Calculates ST (total-order indices)
   - Computes confidence intervals
   - Saves results to CSV files

5. **Creates Output Folders**
   - `SobolInformation_Hehe_oxic/`
   - `SobolInformation_Tugou_oxic/`
   - `SobolInformation_Hehe_anoxic/`
   - `SobolInformation_Tugou_anoxic/`
   - `SobolInformation_Noedler/`

### Key Configuration (in script)

```python
# USER INPUT: Number of samples
N = 1024  # Increase for better convergence, decrease for faster testing

# Problem definition (parameters and bounds)
problem = {
    'num_vars': 16,  # or 19 depending on condition
    'names': ['K1', 'K2', 'K3', ..., 'K16'],
    'bounds': [
        [1e-4, 1e-2],    # K1: abiotic decay
        [1e-6, 1e-3],    # K2: secondary decay
        [1e1, 1e4],      # K3: nitrification (OXIC)
        # ... rest of parameters
    ]
}



### Output Files

```
SobolInformation_[site]_[condition]/
├── df_S1.csv              # S₁ (first-order) indices
├── df_S1_conf.csv         # S₁ confidence intervals
├── df_ST.csv              # ST (total-order) indices
├── df_ST_conf.csv         # ST confidence intervals
├── df_delta.csv           # Δ (moment-independent) indices
├── df_delta_conf.csv      # Δ confidence intervals
└── phreeqc.log            # PHREEQC execution log
```

### Typical Runtime

- **N=256 samples**: 4-8 hours
- **N=512 samples**: 8-16 hours
- **N=1024 samples**: 16-32 hours

Runtime depends on:
- PHREEQC model complexity (5-60 sec per run)
- Number of parameters (16 vs 19)
- System performance

### Progress Display

```
Progress: |████████████████░░░░░░░░░░░░░░░░░░░░| 45.3% Complete
Running PHREEQC for sample 1234 of 2730...
Time remaining: ~3 hours
```

---

## Stage 2: Plot Sensitivity Results

### Command

```bash
python 02_Plotting_SI_results.py
```

### What It Does

1. **Loads Sobol Results**
   - Reads `df_ST.csv` and `df_ST_conf.csv` from each site folder
   - Extracts sensitivity indices across sample sizes

2. **Creates Multi-Panel Figure**
   - 2×3 subplot grid (6 subplots for 5 sites + 1 extra)
   - Each subplot: One site/condition combination
   - X-axis: Number of samples (sample size)
   - Y-axis: Sensitivity index (ST, log scale)
   - Shows convergence behavior

3. **Convergence Visualization**
   - Parameters that converge (flat line) = robust results
   - Parameters still fluctuating = need more samples
   - Helps assess sampling adequacy

4. **Applies Styling**
   - LaTeX-formatted parameter labels
   - Color-coded by parameter
   - Legend outside plots
   - Log scale for clarity

### Acknowledgements
We acknowledge Florian Konrads (Technical University Munich and Stadtwerke Munich) support with the sensivity analysis code. 