"""Reduced model set-ups (Fig. S8 and Table S9), built from the corresponding full-model set-ups in
calibration/reduced_setups/<dataset> (same weights, same prior realizations, 100 realizations, 8 iterations).
The reference full-model set-ups oxic_H, anoxic_H and anoxic_NDL in calibration/reduced_setups are identical
to those in calibration/full_model except for the ensemble size (100 realizations); their prior ensembles
(prior.jcb) are provided and are reused by the reduced set-ups.
  oxicH_no_nitr   nitrification removed (R4, R5: k4 = k5 = 0)
  oxicH_no_undet  undetected TPs removed (R15, R16: k15 = k16 = 0); Undet observations weight 0
  oxicH_no_r10    biologically mediated DeA-SMX formation removed (R10: k10 = 0)
  anoxicH_no_r10, anoxicNDL_no_r10   R10 removed for the anoxic datasets with nitrite/nitrate data
"""
import os, json, shutil, pyemu, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reduced_setups')
import sys
VARIANTS = {'oxicH_no_nitr': ('oxic_H', ['k4', 'k5'], False), 'oxicH_no_undet': ('oxic_H', ['k15', 'k16'], True),
            'oxicH_no_r10': ('oxic_H', ['k10'], False),
            'anoxicH_no_r10': ('anoxic_H', ['k10'], False), 'anoxicNDL_no_r10': ('anoxic_NDL', ['k10'], False)}
for name, (base_ds, off, drop_undet) in VARIANTS.items():
    if len(sys.argv) > 1 and name not in sys.argv[1:]:
        continue
    BASE = os.path.join(ROOT, base_ds)
    d = os.path.join(ROOT, name)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    for f in os.listdir(BASE):
        if os.path.isfile(os.path.join(BASE, f)) and not f.startswith(base_ds.lower() + '.') and f != f'{base_ds}.pst':
            shutil.copy(os.path.join(BASE, f), d)
    pst = pyemu.Pst(os.path.join(BASE, f'{base_ds}.pst'))
    cfg = json.load(open(os.path.join(BASE, 'variant.json')))
    cfg['fixed'] = {k: 0.0 for k in off}
    json.dump(cfg, open(os.path.join(d, 'variant.json'), 'w'), indent=1)
    keep = [p for p in pst.par_names if p not in off]
    with open(os.path.join(d, 'params.dat.tpl'), 'w') as f:
        f.write('ptf ~\n')
        for k in keep:
            f.write(f'{k} ~{k:^24}~\n')
    with open(os.path.join(d, 'params.dat'), 'w') as f:
        for k in keep:
            f.write(f"{k} {pst.parameter_data.loc[k, 'parval1']:.6e}\n")
    os.system(f'cd "{d}" && python3 forward_run.py')
    base = pst
    pst = pyemu.Pst.from_io_files(os.path.join(d, 'params.dat.tpl'), os.path.join(d, 'params.dat'),
                                  os.path.join(d, 'sim.dat.ins'), os.path.join(d, 'sim.dat'), pst_path='.')
    pst.parameter_data.loc[keep, :] = base.parameter_data.loc[keep, pst.parameter_data.columns]
    pst.observation_data.loc[:, :] = base.observation_data.loc[pst.observation_data.index, pst.observation_data.columns]
    pst.model_command = base.model_command
    pst.control_data.noptmax = base.control_data.noptmax
    pst.pestpp_options = dict(base.pestpp_options)
    if drop_undet:
        od = pst.observation_data
        od.loc[od.obgnme == 'undet', 'weight'] = 0.0
    pe = pyemu.ParameterEnsemble.from_binary(pst, os.path.join(BASE, 'prior.jcb'))
    pe = pyemu.ParameterEnsemble(pst, pe._df.loc[:, keep])
    pe.to_binary(os.path.join(d, 'prior.jcb'))
    pst.write(os.path.join(d, f'{name}.pst'), version=2)
    print(name, 'npar', pst.npar_adj, 'nnz obs', pst.nnz_obs)
