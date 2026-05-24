###########################################################################################################################
'''
Create the phrq files without the GUI
'''
###########################################################################################################################
import os 
import configparser
import sys

print("✓ Script started", flush=True)

# Setup directories
script_dir = os.path.dirname(os.path.abspath(__file__))

# Read config file
if len(sys.argv) > 1:
    configfn = sys.argv[1]
else:
    configfn = os.path.join(script_dir, "Controle_file.conf")

print(f"✓ Reading config: {configfn}", flush=True)

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(configfn)

# Setup paths
SELFILE = config.get("system", "SELFILE", fallback="Results.sel")
sel_file_path = os.path.join(script_dir, SELFILE)

input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

print(f"✓ Input folder: {input_folder}", flush=True)
print(f"✓ Output folder: {output_folder}", flush=True)

# Read ONLY the main distinguishing flags
OXIC = config.getboolean("batch", "OXIC", fallback=True)
ANOXIC = config.getboolean("batch", "ANOXIC", fallback=True)
HEHE_BED = config.getboolean("site", "HEHE_BED", fallback=True)
TUGOU_BANK = config.getboolean("site", "TUGOU_BANK", fallback=True)
NOEDLER = config.getboolean("validation", "NOEDLER", fallback=False)


print(f"✓ Flags loaded: OXIC={OXIC}, ANOXIC={ANOXIC}, HEHE_BED={HEHE_BED}, TUGOU_BANK={TUGOU_BANK}", flush=True)

# ============================================================================
# PARAMETER DICTIONARIES - Simplified by condition and location
# ============================================================================

# All parameters now follow pattern: {location}_{condition}_sorption
params = {
    # OXIC CONDITIONS WITH SORPTION
    'Hehe_bed_oxic_sorption': [1e-2, 3e-6, 2e1, 5.3e2, 6.82e2, 0, 0, 0, 0.02, 1.6e-07, 1e30, 3e20, 3.5e2, 1.5e6, 29, 0.9, 1.5e-5, 3e3, 0.003],
    'Tugou_bank_oxic_sorption': [1e-2, 1e-5, 22, 1200, 6600, 0, 0, 0, 2e-3, 5.2596e-06, 9e30, 5e21, 9.9e2, 120000, 4.4, 9e-1, 1.65e-05, 14300, 0.01],
    
    # ANOXIC CONDITIONS WITH SORPTION
    'Hehe_bed_anoxic_sorption': [3e-2, 2e-4, 0, 0, 0, 2.5e3, 4e3, 1.5e-03, 4e-3, 1.6315e-07, 2e26, 1.5e18, 5e3, 1.2e5, 8, 5e-1, 1.5e-05, 2e5, 8],
    'Tugou_bank_anoxic_sorption': [1e-3, 3e-6, 0, 0, 0, 25, 9e2, 1.9e-05, 0.15, 4.6315e-07, 2e28, 8e14, 1.5e2, 3e5, 3, 0.1, 1.5e-05, 5e3, 0.55],
    
    # NOEDLER 
    'Noedler': [1e-2, 1,0,0,0, 1.2e-1, 3e-1, 3.8e-2, 5e-2, 3.2e-2, 6e7, 1e5, 8, 1.5e4, 3.9e-1, 2,2.2e-2,2e2,4.1],
}

print(f"✓ Parameter sets loaded: {list(params.keys())}", flush=True)

# ============================================================================
# FUNCTION: Determine template file and parameters
# ============================================================================

def determine_template_file(OXIC, ANOXIC, HEHE_BED, TUGOU_BANK, NOEDLER):
    """
    Determine which PHREEQC template file to use based on flags.
    
    Template files have format: [Oxic|Anoxic]_template_undetected_sorption.phrq
    Output files have format: [Oxic|Anoxic]_[location]_sorption.phrq
    
    Returns: (template_filename, output_filename, param_key)
    """
    
    print(f"\n→ Determining template file...", flush=True)
    
    # Handle NOEDLER special case
    if NOEDLER:
        template = "Noedler_template.phrq"
        output = "Noedler.phrq"
        param_key = 'Noedler'
        print(f"  Using NOEDLER template: {template}", flush=True)
        return template, output, param_key
    
    # Determine condition (Oxic or Anoxic)
    if OXIC and not ANOXIC:
        condition = 'Oxic'
    elif ANOXIC and not OXIC:
        condition = 'Anoxic'
    else:
        print(f"  ERROR: Exactly one of OXIC or ANOXIC must be True", flush=True)
        return None, None, None
    
    # Determine location
    if HEHE_BED and not TUGOU_BANK:
        location = 'Hehe_bed'
    elif TUGOU_BANK and not HEHE_BED:
        location = 'Tugou_bank'
    else:
        print(f"  ERROR: Exactly one of HEHE_BED or TUGOU_BANK must be True", flush=True)
        return None, None, None
    
    # Build TEMPLATE filename (with "template" keyword - this is what we READ)
    template_filename = f"{condition}_template_undetected_sorption.phrq"
    
    # Build OUTPUT filename (with location, without "template" - this is what we WRITE)
    output_filename = f"{condition}_{location}_sorption.phrq"
    
    # Build parameter key (without "template")
    param_key = f"{location}_{condition.lower()}_sorption"
    
    print(f"  Condition: {condition}", flush=True)
    print(f"  Location: {location}", flush=True)
    print(f"  Template file (read): {template_filename}", flush=True)
    print(f"  Output file (write): {output_filename}", flush=True)
    print(f"  Parameter key: {param_key}", flush=True)
    
    return template_filename, output_filename, param_key

# ============================================================================
# FUNCTION: Modify and save PHREEQC file
# ============================================================================

def modify_phrq_and_save(parameterlist, template_filename, output_filename):
    """
    Modify PHREEQC template file with parameters and save.
    
    Modifies:
    - log_k values based on location (Hehe_bed vs Tugou_bank)
    - pH and DOC values based on condition (Oxic vs Anoxic)
    - Kinetic parameters
    - Output file path
    """
    
    print(f"\n→ Modifying template...", flush=True)
    
    # Determine template path
    template_path = os.path.join(input_folder, template_filename)
    output_path = os.path.join(input_folder, output_filename)
    
    print(f"  Reading: {template_path}", flush=True)
    print(f"  Will save to: {output_path}", flush=True)
    
    try:
        # Read template
        with open(template_path, 'r') as file:
            lines = file.readlines()
        
        print(f"  ✓ Read {len(lines)} lines", flush=True)
        
        # ================================================================
        # SORPTION log_k VALUES - Based on location only
        # ================================================================
        
        if HEHE_BED:
            lines[52] = '    log_k -100.2\n'     # Nitro
            lines[55] = '    log_k -101.2\n'     # DES
            lines[58] = '    log_k -101.2\n'     # Ammet
            lines[61] = '    log_k -101.45\n'    # SMX
            print(f"  ✓ log_k values set for Hehe_bed", flush=True)
        
        elif TUGOU_BANK:
            lines[52] = '    log_k -100.5\n'     # Nitro
            lines[55] = '    log_k -100.7\n'     # DES
            lines[58] = '    log_k -100.8\n'     # Ammet
            lines[61] = '    log_k -101.04\n'    # SMX
            print(f"  ✓ log_k values set for Tugou_bank", flush=True)
        
        # ================================================================
        # SOLUTION PARAMETERS - Based on condition (OXIC vs ANOXIC)
        # ================================================================
        
        if ANOXIC:
            if HEHE_BED:
                lines[71] = '    pH    7.13\n'
                lines[86] = '    Doc       3.28 mg/kgw\n'
                lines[105] = '       -m0    0.015\n'
            elif TUGOU_BANK:
                lines[71] = '    pH    7.13\n'
                lines[86] = '    Doc      4.66 mg/kgw\n'
                lines[105] = '       -m0   5.3e-3\n'
            
            # ANOXIC kinetic parameters
            lines[106] = f'       -parms     {parameterlist[0]}\n'     # k1
            lines[112] = f'       -parms     {parameterlist[1]}\n'     # K2
            lines[117] = f'       -parms     {parameterlist[5]}\n'     # K6
            lines[122] = f'       -parms     {parameterlist[6]}     {parameterlist[7]}\n'  # K7
            lines[130] = f'       -parms     {parameterlist[8]}     {parameterlist[9]}\n'  # K8
            lines[135] = f'       -parms     {parameterlist[10]}\n'    # K9
            lines[141] = f'       -parms     {parameterlist[11]}\n'    # K10
            lines[146] = f'       -parms     {parameterlist[12]}\n'    # K11
            lines[151] = f'       -parms     {parameterlist[13]}\n'    # K12
            lines[156] = f'       -parms     {parameterlist[14]}\n'    # K13
            lines[161] = f'       -parms     {parameterlist[15]}     {parameterlist[16]}\n'  # K14
            lines[166] = f'       -parms     {parameterlist[17]}\n'    # K15
            lines[169] = f'       -parms     {parameterlist[18]}\n'    # K16
            lines[301] = f'      -file {sel_file_path}\n'
            
            print(f"  ✓ ANOXIC parameters set", flush=True)
        
        elif OXIC:
            if HEHE_BED:
                lines[72] = '    pH    7.13\n'
                lines[90] = '    Doc     3.28 mg/kgw\n'
                lines[77] = '    O(0)\t  8.2 mg/kgw\n'
                lines[104] = '       -m0   0.015\n'
            elif TUGOU_BANK:
                lines[72] = '    pH    7.13\n'
                lines[90] = '    Doc     4.66 mg/kgw\n'
                lines[77] = '    O(0)\t  8.62 mg/kgw\n'
                lines[104] = '       -m0 2e-3\n'
            
            # OXIC kinetic parameters
            lines[105] = f'       -parms     {parameterlist[0]}\n'     # k1
            lines[111] = f'       -parms     {parameterlist[1]}\n'     # K2
            lines[116] = f'       -parms     {parameterlist[2]}\n'     # K3
            lines[121] = f'       -parms     {parameterlist[3]}\n'     # K4
            lines[126] = f'       -parms     {parameterlist[4]}\n'     # K5
            lines[134] = f'       -parms     {parameterlist[8]}     {parameterlist[9]}\n'  # K8
            lines[139] = f'       -parms     {parameterlist[10]}\n'    # K9
            lines[145] = f'       -parms     {parameterlist[11]}\n'    # K10
            lines[150] = f'       -parms     {parameterlist[12]}\n'    # K11
            lines[155] = f'       -parms     {parameterlist[13]}\n'    # K12
            lines[160] = f'       -parms     {parameterlist[14]}\n'    # K13
            lines[165] = f'       -parms     {parameterlist[15]}     {parameterlist[16]}\n'  # K14
            lines[170] = f'       -parms     {parameterlist[17]}\n'    # K15
            lines[173] = f'       -parms     {parameterlist[18]}\n'    # K16
            lines[316] = f'      -file {sel_file_path}\n'
            
            print(f"  ✓ OXIC parameters set", flush=True)
        elif NOEDLER:
            lines[76] = '       -parms    '+  f' {parameterlist[0]}\n' #k1
            lines[82] = '       -parms    '+  f'{parameterlist[1]}     \n' # # K2   
            lines[87] = '       -parms    '+  f'{parameterlist[5]}  \n'#   '+  f'{parameterlist[4]}     '+f'{parameterlist[5]}\n' # K6   #k_s,Corg  #k_s,NO3 
            lines[92] = '       -parms    '+  f'{parameterlist[6]}     '+  f'{parameterlist[7]}\n'#K7  #k_I,NO3 
            lines[99] = '       -parms    '+  f'{parameterlist[8]}     '+  f'{parameterlist[9]}\n'#K8 #K_(s,SMX)# k_l,Corg   
            lines[105] = '       -parms    '+  f' {parameterlist[10]}\n' #K9
            lines[111] = '       -parms    '+  f' {parameterlist[11]}\n' #K10
            lines[116] = '       -parms    '+  f' {parameterlist[12]}\n' #K11
            lines[121] = '       -parms    '+  f' {parameterlist[13]}\n' #K12
            lines[126] = '       -parms    '+  f' {parameterlist[14]}\n' #K13
            lines[131] = '       -parms    '+  f' {parameterlist[15]}     '+  f'{parameterlist[16]}\n' #K14
            lines[136] = '       -parms    '+  f' {parameterlist[17]}\n' #K15
            lines[140] = '       -parms    '+  f' {parameterlist[18]}\n' #K16 
            lines[274] = f'      -file {sel_file_path}\n'
            print(f"  ✓ NOEDLER parameters set", flush=True)
        
        # ================================================================
        # SAVE MODIFIED FILE
        # ================================================================
        
        with open(output_path, 'w') as f:
            f.writelines(lines)
        
        print(f"  ✓ Saved to: {output_path}", flush=True)
        return output_filename
    
    except Exception as e:
        print(f"  ✗ ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main(input_folder, OXIC, ANOXIC, HEHE_BED, TUGOU_BANK, NOEDLER):
    """
    Main workflow:
    1. Determine which template and parameters to use
    2. Modify the template with parameters
    3. Save the output file with location in the name
    """
    
    print(f"\n{'='*70}", flush=True)
    print(f"PHREEQC FILE GENERATOR - SIMPLIFIED", flush=True)
    print(f"{'='*70}", flush=True)
    
    # Check input folder
    if not os.path.exists(input_folder):
        print(f"✗ ERROR: Input folder does not exist: {input_folder}", flush=True)
        return False
    
    files = os.listdir(input_folder)
    print(f"✓ Found {len(files)} files in input folder", flush=True)
    if files:
        print(f"  Files: {files}", flush=True)
    
    # Determine template and parameters
    template_filename, output_filename, param_key = determine_template_file(
        OXIC, ANOXIC, HEHE_BED, TUGOU_BANK, NOEDLER
    )
    
    if template_filename is None:
        print(f"✗ ERROR: Could not determine template file", flush=True)
        return False
    
    # Check if template exists
    template_path = os.path.join(input_folder, template_filename)
    if not os.path.exists(template_path):
        print(f"✗ ERROR: Template file not found: {template_path}", flush=True)
        return False
    
    print(f"✓ Template found: {template_filename}", flush=True)
    
    # Get parameters
    parameters = params.get(param_key, None)
    if parameters is None:
        print(f"✗ ERROR: No parameters found for key: {param_key}", flush=True)
        return False
    
    print(f"✓ Parameters loaded: {len(parameters)} values", flush=True)
    
    # Modify and save
    result_filename = modify_phrq_and_save(parameters, template_filename, output_filename)
    
    if result_filename:
        condition = 'Oxic' if OXIC else 'Anoxic'
        location = 'Hehe_bed' if HEHE_BED else 'Tugou_bank'
        print(f"\n✓ SUCCESS: {condition} + {location} + sorption + undetected", flush=True)
        print(f"  Output: {result_filename}", flush=True)
        print(f"{'='*70}\n", flush=True)
        return True
    else:
        print(f"\n✗ FAILED: Could not create file", flush=True)
        print(f"{'='*70}\n", flush=True)
        return False

# ============================================================================
# RUN MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        success = main(input_folder, OXIC, ANOXIC, HEHE_BED, TUGOU_BANK, NOEDLER)
        if success:
            print("✓ Script completed successfully", flush=True)
        else:
            print("✗ Script encountered errors", flush=True)
    except Exception as e:
        print(f"✗ FATAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
