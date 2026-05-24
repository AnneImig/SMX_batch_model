import subprocess 
import os 
from utils import runpestsuit
import shutil

# Run in Debug mode because of the pest runs beeing run 2#

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Define the source file and destination file
source_file = "control.pst"
destination_file = "control2.pst"

try:
    # Copy the file
    shutil.copy(source_file, destination_file)
    print(f"File copied successfully: {source_file} -> {destination_file}")
except FileNotFoundError:
    print(f"Error: The file '{source_file}' does not exist.")
except PermissionError:
    print("Error: Permission denied. Check your access rights.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# ######################################################
# ############    Step 1: Run PARREP    ################
# ######################################################

# Define the PEST control file and the parameter file
pst_file = "control.pst"  # Your PEST control file
par_file = "control.par"  # File with the calibrated parameters
pst_file_new = "control2.pst"  # File with the calibrated parameters
PARREP= ["parrep", par_file, pst_file, pst_file_new]

runpestsuit(PARREP)
# #########################################################
# # Step 1b: Run pest with pst_file_new NOPTMAX set to-1 # 
# #########################################################
with open(pst_file_new, 'r') as file:
    lines = file.readlines()
lines [8]= '-1 0.0005 4 4 0.0005 4\n'
with open(pst_file_new, 'w') as file:
    file.writelines(lines)
print(f"Line 8 in {pst_file_new} has been replaced successfully.")
PEST=["pest", pst_file_new]
#runpestsuit (PEST)

# Define the source file and destination file
source_file2 = "control2.pst"
destination_file2 = "control2_copy.pst"

try:
    # Copy the file
    shutil.copy(source_file2, destination_file2)
    print(f"File copied successfully: {source_file2} -> {destination_file2}")
except FileNotFoundError:
    print(f"Error: The file '{source_file2}' does not exist.")
# #########################################################
# # Step 2: Run RANDPAR # 
# # choose log uniform distrbution
# #########################################################

# PEST uncertainty file generation#
uncertainty_data = (
'START STANDARD_DEVIATION\n'
    'K1  0.2\n'
    'K2 0.2\n'
    'K3 0.2\n'
    'K4 0.2\n'
    'K5 0.2\n'
    'K6 0.2\n'
    'K7 0.2\n'
    'K_NO3 0.2\n'
    'K8 0.8\n'
    'K_DOC   0.2\n'
    'K9  0.2\n'
    'K10 0.2\n'
    'K11 0.2\n'
    'K12    0.2\n'
    'K13 0.2\n'
    'K14 0.2\n'
    'K15 0.2\n'
    'K16 0.2\n'
'END STANDARD_DEVIATION\n'
'\n'
)

uncert_file_path = os.path.join(script_dir, 'uncert.dat')
with open(uncert_file_path, 'w') as uncertainty_file:
    uncertainty_file.write( uncertainty_data)
uncertainty_file.close()
print("Uncertainty file has been succesfully created.\n")

#########################################################
# Step 3: Run PNULPAR# 
#########################################################

#########################################################
# Step 4: Run SVDAPREP# 
#########################################################

#after running SVDAPREP change case_svda.pst file 
super_pst= 'case_svda.pst'
with open(super_pst, 'r') as file:
    lines = file.readlines()
lines[5] ='  0.01       -3.0000      0.3  0.03  10       999  lamforgive\n'
lines [8]= '50 0.0005 4 4 0.0005 4\n'
lines[9]=('1  1  1  1 nojcosaveitn noreisaveitn\n'
'* singular value decomposition\n'
    ' 1\n'
     '14 5e-7\n'
     '0\n')
with open(super_pst, 'w') as file:
    file.writelines(lines)
print(f"Lines in {super_pst} have been replaced successfully.")
