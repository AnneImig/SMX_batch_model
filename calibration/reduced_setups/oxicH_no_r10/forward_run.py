"""Forward run for PEST++ IES (all five batch datasets).
Builds the PHREEQC input from the templates in this folder for a given parameter set, runs it with IPhreeqc (phreeqpython) and writes sim.dat with the simulated
observations. Parameter names follow Table 1 of the manuscript:
k3 = oxic DOC mineralization, k4/k5 = nitrification steps I/II, k6/k7 = denitrification,
kl_no3, kl_ch2o, kl2_ch2o = inhibition constants of R7, R8 and R14."""
import json, os, numpy as np
from phreeqpython import PhreeqPython
HERE = os.path.dirname(os.path.abspath(__file__))

# logK from the measured adsorption percentages (Table S2): logK = log10(p / (100 - p)) - 100
LOGK = {'H': ['-100.327', '-101.144', '-101.195', '-101.428'], 'T': ['-100.231', '-100.650', '-100.673', '-100.989']}

def _logk(L, site):
    for ln, v in zip([52, 55, 58, 61], LOGK[site]):
        L[ln] = f'    log_k {v}\n'

def build_oxic(p, site):
    L = open(os.path.join(HERE, 'Oxic_template_undetected_sorption.phrq')).readlines()
    _logk(L, site)
    L[72] = '    pH    7.13\n'
    L[90] = '    Doc     3.28 mg/kgw\n' if site == 'H' else '    Doc     4.66 mg/kgw\n'
    L[77] = '    O(0)\t  8.2 mg/kgw\n' if site == 'H' else '    O(0)\t  8.62 mg/kgw\n'
    L[104] = '       -m0   0.015\n' if site == 'H' else '       -m0 2e-3\n'
    L[105] = f"       -parms     {p['k1']}\n"; L[111] = f"       -parms     {p['k2']}\n"
    L[116] = f"       -parms     {p['k4']}\n"; L[121] = f"       -parms     {p['k5']}\n"
    L[126] = f"       -parms     {p['k3']}\n"
    L[134] = f"       -parms     {p['k8']}     {p['kl_ch2o']}\n"
    L[139] = f"       -parms     {p['k9']}\n"; L[145] = f"       -parms     {p['k10']}\n"
    L[150] = f"       -parms     {p['k11']}\n"; L[155] = f"       -parms     {p['k12']}\n"
    L[160] = f"       -parms     {p['k13']}\n"
    L[165] = f"       -parms     {p['k14']}     {p['kl2_ch2o']}\n"
    L[170] = f"       -parms     {p['k15']}\n"; L[173] = f"       -parms     {p['k16']}\n"
    L[316] = '      -file Results.sel\n'
    return ''.join(L)

def build_anoxic(p, site):
    L = open(os.path.join(HERE, 'Anoxic_template_undetected_sorption.phrq')).readlines()
    _logk(L, site)
    L[71] = '    pH    7.13\n'
    L[86] = '    Doc       3.28 mg/kgw\n' if site == 'H' else '    Doc      4.66 mg/kgw\n'
    L[105] = '       -m0    0.015\n' if site == 'H' else '       -m0   5.3e-3\n'
    L[106] = f"       -parms     {p['k1']}\n"; L[112] = f"       -parms     {p['k2']}\n"
    L[117] = f"       -parms     {p['k6']}\n"
    L[122] = f"       -parms     {p['k7']}     {p['kl_no3']}\n"
    L[130] = f"       -parms     {p['k8']}     {p['kl_ch2o']}\n"
    L[135] = f"       -parms     {p['k9']}\n"; L[141] = f"       -parms     {p['k10']}\n"
    L[146] = f"       -parms     {p['k11']}\n"; L[151] = f"       -parms     {p['k12']}\n"
    L[156] = f"       -parms     {p['k13']}\n"
    L[161] = f"       -parms     {p['k14']}     {p['kl2_ch2o']}\n"
    L[166] = f"       -parms     {p['k15']}\n"; L[169] = f"       -parms     {p['k16']}\n"
    L[301] = '      -file Results.sel\n'
    return ''.join(L)

def build_ndl(p):
    L = open(os.path.join(HERE, 'Noedler_template.phrq')).readlines()
    L[76] = f"       -parms     {p['k1']}\n"; L[82] = f"       -parms    {p['k2']}\n"
    L[87] = f"       -parms    {p['k6']}\n"
    L[92] = f"       -parms    {p['k7']}     {p['kl_no3']}\n"
    L[99] = f"       -parms    {p['k8']}     {p['kl_ch2o']}\n"
    L[105] = f"       -parms     {p['k9']}\n"; L[111] = f"       -parms     {p['k10']}\n"
    L[116] = f"       -parms     {p['k11']}\n"; L[121] = f"       -parms     {p['k12']}\n"
    L[126] = f"       -parms     {p['k13']}\n"
    L[131] = f"       -parms     {p['k14']}     {p['kl2_ch2o']}\n"
    L[136] = f"       -parms     {p['k15']}\n"; L[140] = f"       -parms     {p['k16']}\n"
    L[274] = '      -file Results.sel\n'
    return ''.join(L)

BUILD = {'oxic_H': lambda p: build_oxic(p, 'H'), 'oxic_T': lambda p: build_oxic(p, 'T'),
         'anoxic_H': lambda p: build_anoxic(p, 'H'), 'anoxic_T': lambda p: build_anoxic(p, 'T'),
         'anoxic_NDL': build_ndl}
# simulated column for each observed species
COLS = {'smx': 'Smx', 'des': 'DES', 'nit': 'Nit', 'ammet': 'Ammet', 'undet': 'Undetected',
        'nh4': 'Amonia', 'no2': 'NO2-', 'no3': 'NO3-', 'doc': 'Doc'}

def read_params(fn):
    return {k: float(v) for k, v in (l.split() for l in open(fn) if l.strip())}

KIN_TOL = 1e-15   # mol; PHREEQC default (1e-8) is far above the nM-level SMX/TP amounts and
                  # produced numerical oscillations in the kinetic integration

def set_tolerance(text, tol=KIN_TOL):
    """add '-tol' to every KINETICS reactant (after its -parms line)"""
    out, in_kin = [], False
    for line in text.split('\n'):
        out.append(line)
        u = line.strip().upper()
        if u.startswith('KINETICS'):
            in_kin = True
        elif u.startswith('RATES'):
            in_kin = False
        if in_kin and line.strip().startswith('-parms'):
            out.append(f'       -tol {tol}')
    return '\n'.join(out)

def simulate(dataset, p):
    pp = PhreeqPython(database=os.path.join(HERE, 'phreeqc_P.dat'))
    pp.ip.run_string(set_tolerance(BUILD[dataset](p)))
    arr = pp.ip.get_selected_output_array()
    hdr = arr[0]; data = np.array([[float(x) for x in r] for r in arr[1:]])
    col = {h: i for i, h in enumerate(hdr)}
    return data, col

def sample(data, col, obsdef):
    t = data[:, col['Time']]; k = t > 0
    out = []
    for name, sp, tt in obsdef:
        out.append((name, float(np.interp(tt, t[k], data[k, col[COLS[sp]]]))))
    return out

if __name__ == '__main__':
    os.chdir(HERE)
    cfg = json.load(open('variant.json'))
    p = dict(cfg.get('fixed', {})); p.update(read_params('params.dat'))
    data, col = simulate(cfg['dataset'], p)
    with open('sim.dat', 'w') as f:
        for name, v in sample(data, col, cfg['obs']):
            f.write(f'{name} {v:.8e}\n')
