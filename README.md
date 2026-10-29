# Reactive model of redox-dependent co-metabolic SMX biodegradation

Code, data and calibration results for

> Imig, A., Rodríguez-Escales, P., Ma, Y., Zheng, Y. Redox-dependent co-metabolic biodegradation of a semi-persistent antibiotic sulfamethoxazole demonstrated by modeling. Submitted to *Environmental Pollution*.

The reaction network (16 kinetic and 6 equilibrium reactions) is implemented in PHREEQC and calibrated with the iterative ensemble smoother PEST++ IES against five batch datasets:

| Dataset | Source | Conditions |
|---|---|---|
| oxic-H | Ma et al. (2021), Hehe riverbed sediment | oxic |
| oxic-T | Ma et al. (2021), Tugou riverbank sediment | oxic |
| anoxic-H | Ma et al. (2021), Hehe riverbed sediment | anoxic |
| anoxic-T | Ma et al. (2021), Tugou riverbank sediment | anoxic |
| anoxic-NDL | Nödler et al. (2012) | anoxic, denitrifying |

## Repository structure

| Folder | Content |
|---|---|
| `measurements/` | Measured data of Ma et al. (2021) and Nödler et al. (2012) |
| `model/` | PHREEQC templates, database and `forward_run.py`, which builds and runs the PHREEQC input (IPhreeqc via `phreeqpython`) for a given parameter set |
| `calibration/full_model/` | PEST++ IES set-ups and results of the full model for all five datasets (300 realizations; 200 for anoxic-NDL) |
| `calibration/reduced_setups/` | PEST++ IES set-ups and results of the reduced model set-ups and their full-model reference (100 realizations each) |
| `figures/` | One script per figure or table of the manuscript and Supporting Information |
| `output/` | Figures and tables produced by the scripts; `output/cache/` holds the simulated time series of all posterior realizations |

Each calibration folder contains the PEST++ control file (`<dataset>.pst`), template, instruction and observation files, the prior ensemble (`prior.jcb`), and in `master/` the prior (iteration 0) and final parameter and observation ensembles, the phi history and the PEST++ record file.

## Figures and tables

| Figure / table | Script (`figures/`) | Output (`output/`) |
|---|---|---|
| Fig. 1 | drawing | `figures/drawings/Fig1_reaction_network.png` |
| Fig. 2 | `Fig2_oxic_model_results.py` | `Fig2_oxic-H_oxic-T_model_results.png` |
| Fig. 3 | `Fig3_anoxic_model_results.py` | `Fig3_anoxic-H_anoxic-T_anoxic-NDL_model_results.png` |
| Fig. 4 | `Fig4_parameter_identifiability.py` | `Fig4_parameter_identifiability_all_datasets.png`, `.csv` |
| Fig. 5, Table S8 | `Fig5_TableS8_pathway_contributions.py` | `Fig5_pathway_contributions_all_datasets.png`, `TableS8_pathway_contributions.csv` |
| Fig. S1 | drawing | `figures/drawings/FigS1_conceptual_model.png` |
| Fig. S2 | `FigS2_measured_concentrations.py` | `FigS2_measured_concentrations_Ma2021.png` |
| Figs. S3–S7 | `FigS3-S7_prior_posterior.py` | `FigS3_oxic-H_prior_posterior.png`, `FigS4_oxic-T_…`, `FigS5_anoxic-H_…`, `FigS6_anoxic-T_…`, `FigS7_anoxic-NDL_…` |
| Tables S5–S7 | `TablesS5-S7_parameters_and_fit.py` | `TableS5_parameters_oxic.csv`, `TableS6_parameters_anoxic.csv`, `TableS7_model_data_agreement.csv` |
| Fig. S8, Table S9 | `FigS8_TableS9_reduced_model_setups.py` | `FigS8_oxic-H_reduced_model_setups.png`, `TableS9_reduced_model_setups.csv` |
| Fig. S9 | `FigS9_sorption.py` | `FigS9_sorption.png`, `FigS9_sorption_measured_vs_model.csv` |

## Installation

```bash
conda env create -f environment.yml
conda activate smx_batch_model
```

## Reproducing the figures and tables

```bash
bash figures/reproduce_all.sh
```

This takes a few minutes, because the simulated time series of the posterior realizations are read from `output/cache/`. If the cache is deleted, the scripts re-run all posterior realizations with PHREEQC (several hours; set `NPROC` to the number of cores to use).

## Re-running the calibration (optional)

Requires the PEST++ IES executable (https://github.com/usgs/pestpp). With 2 agents the full-model calibration takes about 12 h.

```bash
cd calibration
python build_full_model.py                       # builds calibration/full_model/<dataset> and the prior ensembles
PESTPP_IES=/path/to/pestpp-ies NAGENTS=4 bash run_pestpp_ies.sh full_model
python build_reduced_setups.py                   # reduced set-ups from the 100-realization reference set-ups
PESTPP_IES=/path/to/pestpp-ies NAGENTS=4 bash run_pestpp_ies.sh reduced_setups
```

Then delete `output/cache/` and run `bash figures/reproduce_all.sh`.

## Data sources
- Ma, Y., Modrzynski, J.J., Yang, Y., Aamand, J., Zheng, Y., 2021. Redox-dependent biotransformation of sulfonamide antibiotics exceeds sorption and mineralization: Evidence from incubation of sediments from a reclaimed water-affected river. Water Research 205, 117616. https://doi.org/10.1016/j.watres.2021.117616
- Nödler, K., Licha, T., Barbieri, M., Pérez, S., 2012. Evidence for the microbially mediated abiotic formation of reversible and non-reversible sulfamethoxazole transformation products during denitrification. Water Research 46, 2131–2139. https://doi.org/10.1016/j.watres.2012.01.028

## License
CC BY-NC 4.0 (see `LICENSE`).
