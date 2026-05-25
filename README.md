#  Reactive model for SMX antibiotics 
The repository provides python and PHREEQC codes that have been used to model sulfamethoxazole antibiotic and metabolite measurements documented in the publications:
Ma, Y., Modrzynski, J.J., Yang, Y., Aamand, J., Zheng, Y., 2021. Redox-dependent biotransformation of sulfonamide antibiotics exceeds sorption and mineralization: Evidence from incubation of sediments from a reclaimed water-affected river. Water Research 205, 117616. https://doi.org/10.1016/j.watres.2021.117616 

Nödler, K., Licha, T., Barbieri, M., Pérez, S., 2012. Evidence for the microbially mediated abiotic formation of reversible and non-reversible sulfamethoxazole transformation products during denitrification. Water Research 46, 2131–2139. https://doi.org/10.1016/j.watres.2012.01.028

A publication with the results is submitted to Environmental International:
Modeling reveals co-metabolic metabolite formation during redox-dependent transformation key to the fate of sulfamethoxazole in groundwater by Imig et al. 2026

# Intallation
To install the required environment, use the provided `environment.yml`. 


```bash
conda env create -f environment.yml
conda activate ttd_analysis
```
or with mamba
```bash
mamba env create -f environment.yml
mamba activate ttd_analysis
```
# Run the code
 PHREEQC executable must be available as a path variable. In the Controle_file.conf user settings can be made, e.g. selecting the model for a specific dataset and plotting information. 
In the folder PHQ_Batch_reactive_kinetics, you can find the protocol to run the PHREEQC input files for the different models (anoxic-H, anoxic-T, oxic-H, oxic-T, anoxic-NDL). 


#### 1. R1_Create_Phrq_files.py
**Purpose**: Create and prepare the PHREEQC input files for undetected (undeterminable) compounds and sorption calculations.

**What it does**:
- Initializes the PHREEQC database reference
- Generates input files for sorption equilibrium calculations
- Sets up baseline parameters for reactive transport modeling

**Must run first** - This script establishes the foundation for all subsequent analyses.

**Run**:
```bash
python R1_Create_PHRQ_Files.py [Controle_file.conf]
```

---

#### 2. R2_Run_PHQ.py
**Purpose**: Execute PHREEQC simulations for all configured batch experiments.

**What it does**:
- Runs reactive transport calculations using PHREEQC
- Processes sorption equilibrium reactions
- Calculates aqueous speciation and solubility
- Generates output files (`.sel`) with simulation results
- Executes for all combinations of sites and conditions based on configuration

**Must run second** - This generates the simulation results that downstream scripts analyze.

**Run**:
```bash
python R2_Run_PHQ.py [Controle_file.conf]
```

---

### Stage 2: Conditional (Based on Configuration)

After Stages 1 and 2, run any combination of the following scripts based on your `Controle_file.conf` settings:

#### 3. R3_Plot_Oxic_batch_Sorption.py
**Purpose**: Visualize oxic batch experiment results.

**Runs when**:
- `[batch] OXIC = TRUE`

**Generates plots for**:
- SMX degradation kinetics under oxic conditions
- Metabolite formation (DeA-SMX, Nitro-SMX, AmMet)


---

#### 4. R4_Plot_Anoxic_batch.py
**Purpose**: Visualize anoxic batch experiment results.

**Runs when**:
- `[batch] ANOXIC = TRUE`

**Generates plots for**:
- SMX degradation kinetics under anoxic conditions
- Metabolite formation (DeA-SMX, Nitro-SMX, AmMet)

---

#### 5. R5_Plot_Noedler.py
**Purpose**: Validate results against Noedler et al. literature data.

**Runs when**:
- `[validation] NOEDLER = TRUE`

**Generates plots for**:
- Model validation against published experimental data
- Metabolite formation (DeA-SMX, Nitro-SMX, AmMet)

---
# PEST Uncertainty Analysis
For three models one oxic, one anoxic and the Noedler model we have supplied the example files to run the Uncertainty analysis with PEST.in the folder PHQ_Batch_reactive_kinetics/PEST_Hehe_anoxic/README.md one can find a specific guide on how to run the uncertainty analysis. 


# Sensitivity Analysis with Sobol 
Sensitivity analysis files are stored in the Sensitivity_Analysis_SMX_batch folder. The readme.md file in the repository explains the workflow. 

## Acknowledgements
We acknowledge the support of Florian Konrad (Technical University Munich and Stadtwerke Munich https://www.researchgate.net/profile/Florian-Konrad-3) with the sensitivity analysis code.


Please don't hesitate to contact us, if you are interested in more details and procedures.
