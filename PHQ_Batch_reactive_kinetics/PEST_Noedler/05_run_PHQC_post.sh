# ###########################################################
# Do all the PEST runs for Results file.
# ###########################################################
for i in {1..1000}; do

  # Update the control file with calibrated parameters
  tempchek Noedler_Post.tpl input/Noedler_post.phrq Post_processing/control_log2.bpa.$i
  # Run PHREEQ
  python R2_Run_PHQ.py
  # Extract and append the sum of squared weighted residuals to record.dat

  # Copy files for backup
  cp output/Results.sel Post_processing/Results_$i.sel

done