# PEST Uncertainty Analysis Workflow - README

## Quick Start

This workflow performs parameter uncertainty and sensitivity analysis for **anoxic batch PHREEQC models with sorption**. It uses PEST to calibrate parameters, then GLUE to identify behavioral (best-fit) parameter sets.

**Typical runtime:** 2-7 days (depending on PHREEQC model complexity)

---

## Prerequisites

### Software Required
- **PEST** software suite with these utilities:
  - `parrep` - Parameter file replacement
  - `pest` - Parameter estimation engine
  - `randpar` - Random parameter generation
  - `svdaprep` - Singular value decomposition setup
  - `pnulpar` - Null parameter generator
  - `tempchek` - Template file checker

- **PHREEQC** - Installed and accessible via command line as `phreeqc`

- **Python 3.7+** with:
  ```bash
  pip install numpy pandas matplotlib configparser
  ```

### File Structure Setup

```
your_project/
├── Controle_file.conf                    # ← Configuration file (CRITICAL)
├── utils.py                              # ← Utility functions
│
├── 01_Create_PEST_files_Sorption.py      # ← Stage 1
├── 02_start_UA.py                        # ← Stage 2
├── 03_run_svda.sh                        # ← Stage 3
├── 04_Post_processing.py                 # ← Stage 4
├── 05_run_PHQC_post.sh                   # ← Stage 5
├── 06_Plot_Anoxic_batch_UA.py            # ← Stage 6
│
├── R2_Run_PHQ.py                         # ← PHREEQC runner (used by stage 1)
├── R2_Run_PHQ_copy.py                    # ← PHREEQC runner (used by stage 5)
├── R_get_measured_val.py                 # ← Get measured values from Excel
│
├── input/
│   ├── Anoxic_template_undetected_sorption.phrq    # ← PHREEQC input template
│   ├── Anoxic_Hehe_bed_Sorption.phrq               # ← Site-specific input
│   └── [other .phrq files]
│
├── output/
│   ├── Results.sel                       # ← Main simulation results (created)
│   └── scr.out                           # ← Screen output (created)
│
├── Post_processing/                      # ← Auto-created by workflow
│   ├── case_svda.res.*                   # ← Residual files (1-1000)
│   ├── control_log2.bpa.*                # ← Parameter files (1-1000)
│   ├── Results_*.sel                     # ← Results for each iteration (1-1000)
│   ├── record.dat                        # ← Objective function history
│   ├── 04_posterior.csv                  # ← All parameter sets
│   ├── 05_posterior_glue.csv             # ← Behavioral parameter sets (KGE > 0.7)
│   ├── histograms/
│   │   └── FigS10_anoxic_H_PDF.png       # ← Prior vs posterior plot
│   └── [other PEST output files]
│
├── plots/                                # ← Final visualizations
│   └── [uncertainty band plots]
│
└── [PEST control files - auto-generated]
    ├── control_log.pst
    ├── control_log.par
    ├── control_log2.pst
    ├── control_log2_copy.pst
    ├── case_svda.pst
    ├── *.tpl (template files)
    └── *.ins (instruction files)
```

---

## Configuration: Controle_file.conf

```ini
[system]
DATABASE = bin/phreeqc_P.dat
SELFILE = output/Results.sel

[batch]
OXIC = FALSE
ANOXIC = TRUE


[site]
HEHE_BED = TRUE
TUGOU_BANK = FALSE

[validation]
NOEDLER = FALSE
```

**Key Settings:**
- `DATABASE`: Full path to PHREEQC database file
- `SELFILE`: Output location (relative path OK)
- `ANOXIC = TRUE`: Use anoxic template
- `HEHE_BED = TRUE`: Choose site (only ONE site per run)
- `TUGOU_BANK = FALSE`: Alternative site

---

## Step-by-Step Workflow

### **Stage 1: Create PEST Files**
```bash
python 01_Create_PEST_files_Sorption.py
```

**What happens:**
1. Reads `Anoxic_template_undetected_sorption.tpl` (parameter template)
2. Creates PEST control file: `control_log.pst`
3. Creates instruction file: `*.ins` (for reading PHREEQC output)
4. Configures observations with weights
5. Sets optimization algorithm parameters

**Key Operations:**
- `control_log.pst` links template → observations → algorithm settings
- Observation weights determine which measurements are more important
- `NOPTMAX` controls optimization iterations

**Outputs Created:**
```
control_log.pst              # Main PEST control file
control_log.par              # Initial parameter file
*.tpl                        # Template files
*.ins                        # Instruction files for reading results
```

**Expected time:** < 1 minute

---

### **Stage 2: Initialize Uncertainty Analysis**
```bash
python 02_start_UA.py
```

**What happens:**
1. **PARREP**: Transfers calibrated parameters from `control_log.par` → `control_log2.pst`
2. **PEST (debug)**: Runs initial optimization with `NOPTMAX = -1` (no optimization, just setup)
3. **Creates uncert.dat**: Parameter uncertainty file
4. **SVDAPREP**: Configures singular value decomposition for 1000 runs

**Key Code Section:**
```python
uncertainty_data = (
    'START STANDARD_DEVIATION\n'
    'K1  0.2\n'        # Log-space std dev (±20%)
    'K2 0.2\n'
    'K3 0.2\n'
    'K4 0.2\n'
    'K5 0.2\n'
    'K8 0.8\n'         # Wider uncertainty
    'K_DOC   0.2\n'
    'K9  0.2\n'
    'K10 0.2\n'
    'K11 0.2\n'
    'K12  0.2\n'
    'K13 0.2\n'
    'K14 0.2\n'
    'END STANDARD_DEVIATION\n'
)
```

**Modify uncertainties here** to reflect your confidence in parameter estimates.

**Outputs Created:**
```
uncert.dat                   # Uncertainty file (K values & std devs)
control_log2.pst             # Updated control file
control_log2_copy.pst        # Backup copy
case_svda.pst                # SVDA configuration (1000 runs)
```

**Expected time:** 2-5 minutes

---

### **Stage 3: Run 1000 SVDA Iterations**
```bash
bash 03_run_svda.sh
```

**What happens (in each iteration):**
1. **Delete old files**: `case_svda.pst`, `case_svda.res`
2. **PARREP**: Update control file with perturbed parameters
3. **PEST**: Run single SVDA iteration
4. **Extract objective**: Get sum of squared weighted residuals
5. **Archive**: Copy `case_svda.res` → `Post_processing/case_svda.res.$i`
6. **Archive**: Copy `control_log2.bpa` → `Post_processing/control_log2.bpa.$i`

**Loop configuration:**
```bash
for i in {1..1000}; do  # Change 1000 to desired iterations
```

**What you'll see:**
```
Run 1: PEST optimization...
Run 2: PEST optimization...
...
Run 1000: PEST optimization...
```

**Outputs Created:**
```
Post_processing/record.dat              # Objective function values
Post_processing/case_svda.res.1-1000    # Residual files
Post_processing/control_log2.bpa.1-1000 # Parameter files
```

**Expected time:** 12-48+ hours (depends on model complexity)

---

### **Stage 4: Post-Process & GLUE Filter**
```bash
python 04_Post_processing.py
```

**What happens:**
1. **Load prior**: Read initial parameter distributions from `control_log*.par`
2. **Load posterior**: Read all 1000 parameter sets from `control_log2.bpa.*`
3. **Read residuals**: Extract from `case_svda.res.*`
4. **Compute metrics** for each run:
   - **RMSE** = √(mean squared error)
   - **R²** = Coefficient of determination (0-1)
   - **KGE** = Kling-Gupta Efficiency (-∞ to 1)
5. **GLUE filter**: Keep only runs where **KGE > 0.7** (configurable) based on initial parameter configuration output
6. **Plot**: Prior vs posterior parameter distributions
7. **Export**: CSV files with filtered results

**Key Settings:**
```python
KGE_THRESHOLD = 0.7  # Change this to adjust filter stringency
```


**What the plots show:**
- **Red histograms**: Prior parameter distribution (uniform initial sampling)
- **Blue histograms**: Posterior distribution (behavioral parameter sets)
- **Shift indicates**: Which parameters are constrained by data

**Outputs Created:**
```
Post_processing/04_posterior.csv         # All 1000 parameter sets
Post_processing/05_posterior_glue.csv    # Behavioral sets (KGE > 0.7)
Post_processing/histograms/FigS10_anoxic_H_PDF.png
```

**Console Output Example:**
```
====================
Total runs: 1000
Behavioral runs (KGE > 0.7): 45
====================

BEST RUN:
run       KGE     R2      RMSE
523       0.847   0.721   1.23e-8
```

**Expected time:** 5-15 minutes

---

### **Stage 5: Run PHREEQC for Each Parameter Set**
```bash
bash 05_run_PHQC_post.sh
```

**What happens (for each iteration i = 1 to 1000):**
1. **tempchek**: Creates PHREEQC input file from template
   - Reads: `Anoxic_template_un_sor_Post.tpl`
   - Parameters from: `Post_processing/control_log2.bpa.$i`
   - Output: `input/Anoxic_Hehe_bed_Sorption.phrq`
2. **R2_Run_PHQ_copy.py**: Executes PHREEQC
3. **Copy results**: `output/Results.sel` → `Post_processing/Results_$i.sel`

**What you'll see:**
```
Running PHREEQC for iteration 1...
Running PHREEQC for iteration 2...
...
Running PHREEQC for iteration 1000...
```

**Outputs Created:**
```
Post_processing/Results_1.sel        # Results for iteration 1
Post_processing/Results_2.sel        # Results for iteration 2
...
Post_processing/Results_1000.sel     # Results for iteration 1000
```

**Expected time:** 12-48+ hours (each PHREEQC run = 1-60 seconds)

---

### **Stage 6: Visualize Uncertainty Bands**
```bash
python 06_Plot_Anoxic_batch_UA.py
```

**What happens:**
1. **Load all results**: Reads `Post_processing/Results_*.sel` (1-1000 files)
2. **Extract species** (SMX, DES, Nitro-SMX, etc.) from each run
3. **Calculate percentiles**:
   - 50th percentile (median)
   - 5th & 95th percentile (uncertainty bands)
   - 25th & 75th percentile (inner bands)
4. **Plot vs measured data** with error bars
5. **Save publication-ready figures**

**What the plots show:**
- **Colored bands**: Uncertainty ranges from 1000 model runs
- **Red dots/lines**: Measured data with error bars
- **Darker shading**: Higher model certainty (runs cluster together)
- **Lighter shading**: Lower certainty (runs diverge)

**Outputs Created:**
```
plots/Anoxic_UA_SMX.png
plots/Anoxic_UA_DES.png
plots/Anoxic_UA_Nitro.png
plots/Anoxic_UA_ALL.png
```

**Expected time:** 5-10 minutes

---



## Output Files Reference

| File | Created by | Purpose |
|------|-----------|---------|
| `control_log.pst` | Stage 1 | Main PEST control file |
| `control_log2.pst` | Stage 2 | Updated with best parameters |
| `case_svda.pst` | Stage 2 | SVDA configuration |
| `uncert.dat` | Stage 2 | Parameter uncertainties |
| `Post_processing/record.dat` | Stage 3 | Objective function history |
| `Post_processing/case_svda.res.*` | Stage 3 | Residuals for each run |
| `Post_processing/control_log2.bpa.*` | Stage 3 | Parameters for each run |
| `Post_processing/04_posterior.csv` | Stage 4 | All parameter sets |
| `Post_processing/05_posterior_glue.csv` | Stage 4 | Behavioral sets only |
| `Post_processing/histograms/*.png` | Stage 4 | Prior vs posterior plots |
| `Post_processing/Results_*.sel` | Stage 5 | PHREEQC output per run |
| `plots/*.png` | Stage 6 | Final uncertainty visualizations |

