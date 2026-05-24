# ###########################################################
# Do all the PEST runs for Results file.
# ###########################################################
for i in {1..1000}; do

  # Update the control file with calibrated parameters
  tempchek Anoxic_template_un_sor_Post.tpl input/Anoxic_Hehe_bed_Sorption.phrq Post_processing/control_log2.bpa.$i
  # Run PHREEQ
  python R2_Run_PHQ_copy.py

  # Copy files for backup
  cp output/Results.sel Post_processing/Results_$i.sel

done