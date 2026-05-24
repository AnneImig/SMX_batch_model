# ###########################################################
# Do all the PEST runs for Results file.
# ###########################################################
for i in {1..1000}; do

  # Update the control file with calibrated parameters
  tempchek input/Oxic_template_undetected_sorption_Post.tpl input/Oxic_Tugou_bank_Sorption.phrq Post_processing/control_log2.bpa.$i
  # Run PHREEQ
  python R2_Run_PHQ_copy.py

  # Copy files for backup
  cp output/Results.sel Post_processing/Results_$i.sel

done