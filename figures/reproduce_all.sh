#!/bin/bash
# Reproduce all figures and tables of the manuscript and SI from the calibrated ensembles in calibration/.
# Output: output/. Uses the cached posterior simulations in output/cache/ (delete it to recompute with PHREEQC).
set -e
cd "$(dirname "$0")"
for s in Fig2_oxic_model_results.py Fig3_anoxic_model_results.py Fig4_parameter_identifiability.py \
         Fig5_TableS8_pathway_contributions.py FigS2_measured_concentrations.py FigS3-S7_prior_posterior.py \
         TablesS5-S7_parameters_and_fit.py FigS8_TableS9_reduced_model_setups.py FigS9_sorption.py; do
  echo "== $s"; python "$s"
done
