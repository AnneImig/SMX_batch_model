#!/bin/bash

# ###########################################################
# Delete an existing record file.
# ###########################################################
rm -f record.dat
touch record.dat

# ###########################################################
# Do all the PEST runs.
# ###########################################################
for i in {1..1000}; do
  del case_svda.pst
  del case_svda.res
  # Update the control file with calibrated parameters
  parrep control_log$i.par control_log2_copy.pst control_log2.pst

  # Run PEST
  pest case_svda

  # Extract and append the sum of squared weighted residuals to record.dat
  grep -i "Sum of squared weighted residuals" case_svda.rec >> Post_processing/record.dat

  # Copy files for backup
  #cp case_svda.rec Post_processing_Anoxic_Hehe/case_svda.rec.$i
  cp case_svda.res Post_processing/case_svda.res.$i #record the res values for statistics calculation
  cp control_log2.bpa Post_processing/control_log2.bpa.$i
done
