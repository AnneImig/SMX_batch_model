import subprocess
import os
from datetime import datetime 

import numpy as np
import sys
import configparser

script_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")
# Path to the PHREEQC executable
EXECUTABLE = "phreeqc" 
# read all information from configfile
if len(sys.argv) > 1:
    configfn = sys.argv[1]
else:
    configfn = os.path.join(script_dir,"Controle_file.conf")

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(configfn)

# Flags for program flow
DATABASE  = config.get("system", "DATABASE", fallback=True)
OXIC= config.getboolean("batch", "OXIC", fallback=True)
ANOXIC= config.getboolean("batch", "ANOXIC", fallback=True)
HEHE_BED= config.getboolean("site", "HEHE_BED", fallback=True)
TUGOU_BANK =config.getboolean("site", "TUGOU_BANK", fallback=True) 
NOEDLER =config.getboolean("validation", "NOEDLER", fallback=True) 

open(os.path.join(output_folder, "scr.out"), 'w').close()
files = os.listdir(input_folder)

phrq_file='Noedler.phrq'
phrq_input_file = os.path.join(input_folder, phrq_file)


def run_phreeqc(phrq_input_file,input_folder, output_folder):
    
    
    # Generate a timestamp for the input file
    #timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    out_file_path = os.path.join(output_folder, "output.out")
    SCR = ("    "+output_folder+"/scr.out")

    try:
        # Run PHREEQC using subprocess
        subprocess.run([EXECUTABLE, phrq_input_file, out_file_path, DATABASE,SCR])

    except Exception as e:
        print(f"Error running PHREEQC: {e}")

# Run PHREEQC with the provided input script
run_phreeqc(phrq_input_file, input_folder, output_folder)
