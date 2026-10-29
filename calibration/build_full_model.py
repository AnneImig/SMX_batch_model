"""Build the PEST++ IES set-ups of the full model for the five batch datasets
(calibration/full_model/<dataset>; kinetic tolerance 1e-15 mol, see model/forward_run.py).

Observation weights: 1/sigma, sigma = sqrt(SD^2 + (0.1*value)^2 + (0.05*max_species)^2); for values
without a reported SD the SD term is zero. The last term is an absolute floor per species. Undet = SMX(0) - (SMX + DeA-SMX + Nit-SMX + AmMet).
Prior: log-normal around the initial calibrated values (manual calibration supported with PEST), range
+-2 orders of magnitude (+-3 for k9, k10), prior SD = range/4 (log10 space).
"""
import os, sys, json, glob, shutil, numpy as np, pandas as pd, pyemu

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MODEL = os.path.join(REPO, 'model')
MEAS = os.path.join(REPO, 'measurements')
RUNS = os.path.join(HERE, 'full_model')
# ensemble sizes; anoxic-NDL uses 200 because its model runs are the slowest
NREALS = {'oxic_H': 300, 'oxic_T': 300, 'anoxic_H': 300, 'anoxic_T': 300, 'anoxic_NDL': 200}
SEED = 20261025
MA = os.path.join(MEAS, 'Ma_2021_measurements.xlsx')
NDL = glob.glob(os.path.join(MEAS, 'N*dler_2012_measurements.xlsx'))[0]
SMX0 = 3.9482e-8
FLOOR = float(os.environ.get('SIGMA_FLOOR', 0.05))

# initial calibrated parameter values per dataset (prior means), mapped to Table 1 names
RAW = {
    'oxic_H':     [1e-2, 3e-6, 2e1, 5.3e2, 6.82e2, 0, 0, 0, 0.02, 1.6e-07, 1e30, 3e20, 3.5e2, 1.5e6, 29, 0.9, 1.5e-5, 3e3, 0.003],
    'oxic_T':     [1e-2, 1e-5, 22, 1200, 6600, 0, 0, 0, 2e-3, 5.2596e-06, 9e30, 5e21, 9.9e2, 120000, 4.4, 9e-1, 1.65e-05, 14300, 0.01],
    'anoxic_H':   [3e-2, 2e-4, 0, 0, 0, 2.5e3, 4e3, 1.5e-03, 4e-3, 1.6315e-07, 2e26, 1.5e18, 5e3, 1.2e5, 8, 5e-1, 1.5e-05, 2e5, 8],
    'anoxic_T':   [1e-3, 3e-6, 0, 0, 0, 25, 9e2, 1.9e-05, 0.15, 4.6315e-07, 2e28, 8e14, 1.5e2, 3e5, 3, 0.1, 1.5e-05, 5e3, 0.55],
    'anoxic_NDL': [1e-2, 1, 0, 0, 0, 1.2e-1, 3e-1, 3.8e-2, 5e-2, 3.2e-2, 6e7, 1e5, 8, 1.5e4, 3.9e-1, 2, 2.2e-2, 2e2, 4.1],
}
IDX = dict(k1=0, k2=1, k4=2, k5=3, k3=4, k6=5, k7=6, kl_no3=7, k8=8, kl_ch2o=9, k9=10, k10=11, k11=12,
           k12=13, k13=14, k14=15, kl2_ch2o=16, k15=17, k16=18)
OXIC_PARS = ['k1', 'k2', 'k3', 'k4', 'k5', 'k8', 'kl_ch2o', 'k9', 'k10', 'k11', 'k12', 'k13', 'k14', 'kl2_ch2o', 'k15', 'k16']
ANOX_PARS = ['k1', 'k2', 'k6', 'k7', 'kl_no3', 'k8', 'kl_ch2o', 'k9', 'k10', 'k11', 'k12', 'k13', 'k14', 'kl2_ch2o', 'k15', 'k16']

def sig(v, sd):
    return np.sqrt(np.nan_to_num(sd) ** 2 + (0.1 * np.abs(v)) ** 2)

def obs_ma(dataset):
    oxic = dataset.startswith('oxic')
    row = 0 if dataset.endswith('_H') else 10
    df = pd.read_excel(MA, sheet_name=0 if oxic else 1)
    ngrp = 4 if oxic else 3
    T = [2, 14, 28, 70][:ngrp]
    base = {'smx': 3, 'ammet': 5, 'des': 6, 'nit': 7}
    avg = {k: np.array(df.iloc[row, [c + 6 * g for g in range(ngrp)]], float) for k, c in base.items()}
    sd = {k: np.array(df.iloc[row + 1, [c + 6 * g for g in range(ngrp)]], float) for k, c in base.items()}
    avg['undet'] = SMX0 - sum(avg[k] for k in base)
    sd['undet'] = np.sqrt(sum(sd[k] ** 2 for k in base))
    rows = []
    for sp in ['smx', 'des', 'nit', 'ammet', 'undet']:
        for i, t in enumerate(T):
            rows.append((f'{sp}_t{t}', sp, t, avg[sp][i], sig(avg[sp][i], sd[sp][i])))
    if not oxic:
        dN = pd.read_excel(MA, sheet_name=2)
        a, s = (3, 4) if dataset.endswith('_H') else (23, 24)
        for off, sp in [(0, 'nh4'), (30, 'no2'), (60, 'no3')]:
            v = np.array(dN.iloc[a + off, [5, 8]], float); e = np.array(dN.iloc[s + off, [5, 8]], float)
            for t, vv, ee in zip([15, 28], v, e):
                rows.append((f'{sp}_t{t}', sp, t, vv, sig(vv, ee)))
    return rows

def obs_ndl():
    df = pd.read_excel(NDL, sheet_name=0).iloc[1:8]
    rows = []
    for _, r in df.iterrows():
        t = float(r['Lich_Time']); tag = str(t).replace('.', 'p').replace('p0', '')
        for sp, c, e in [('smx', 'Lich_SMX', 'Lich_E_SMX'), ('nit', 'Lich_SMXn', 'Lich_E_SMXn'),
                         ('des', 'Lich_SMXH', 'Lich_E_SMXH'), ('no3', 'Lich_Nitrate', None),
                         ('no2', 'Lich_Nitrite', None), ('doc', 'Lich_DOC', None)]:
            v = float(r[c]); sd = float(r[e]) if e else 0.0
            if v <= 0:
                continue
            rows.append((f'{sp}_t{tag}', sp, t, v, sig(v, sd)))
    return rows

def build(dataset):
    d = os.path.join(RUNS, dataset)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    for f in os.listdir(MODEL):
        if os.path.isfile(os.path.join(MODEL, f)): shutil.copy(os.path.join(MODEL, f), d)
    pars = OXIC_PARS if dataset.startswith('oxic') else ANOX_PARS
    init = {k: RAW[dataset][IDX[k]] for k in pars}
    hw = {k: (3.0 if k in ('k9', 'k10') else 2.0) for k in pars}
    obs = obs_ndl() if dataset == 'anoxic_NDL' else obs_ma(dataset)
    # absolute error floor: 5 % of the largest observed value of each species, so that
    # near-zero observations with tiny relative errors do not dominate the objective function
    vmax = {}
    for n, sp, t, v, s in obs:
        vmax[sp] = max(vmax.get(sp, 0.0), abs(v))
    obs = [(n, sp, t, v, float(np.sqrt(s ** 2 + (FLOOR * vmax[sp]) ** 2))) for n, sp, t, v, s in obs]
    json.dump({'dataset': dataset, 'fixed': {}, 'obs': [[n, sp, t] for n, sp, t, _, _ in obs]},
              open(os.path.join(d, 'variant.json'), 'w'), indent=1)
    with open(os.path.join(d, 'params.dat.tpl'), 'w') as f:
        f.write('ptf ~\n')
        for k in pars:
            f.write(f'{k} ~{k:^24}~\n')
    with open(os.path.join(d, 'params.dat'), 'w') as f:
        for k in pars:
            f.write(f'{k} {init[k]:.6e}\n')
    with open(os.path.join(d, 'sim.dat.ins'), 'w') as f:
        f.write('pif ~\n')
        for n, *_ in obs:
            f.write(f'l1 w !{n}!\n')
    rc = os.system(f'cd "{d}" && python3 forward_run.py')
    assert rc == 0, dataset
    pst = pyemu.Pst.from_io_files(os.path.join(d, 'params.dat.tpl'), os.path.join(d, 'params.dat'),
                                  os.path.join(d, 'sim.dat.ins'), os.path.join(d, 'sim.dat'), pst_path='.')
    par = pst.parameter_data
    for k in pars:
        par.loc[k, ['parval1', 'parlbnd', 'parubnd', 'partrans']] = [init[k], init[k] * 10 ** -hw[k], init[k] * 10 ** hw[k], 'log']
        par.loc[k, 'pargp'] = 'antibiotics' if (k.startswith('kl2') or k == 'kl_ch2o' or (k[1:].isdigit() and int(k[1:]) >= 8)) else 'geochem'
    od = pst.observation_data
    for n, sp, t, v, s in obs:
        # NH4 is not simulated with a sink under anoxic conditions and is not shown in Fig. 3 -> reported, weight 0
        od.loc[n, ['obsval', 'weight', 'obgnme']] = [v, 0.0 if sp == 'nh4' else 1.0 / s, sp]
    pst.model_command = ['python3 forward_run.py']
    pst.control_data.noptmax = 8
    pst.pestpp_options.update({'ies_parameter_ensemble': 'prior.jcb', 'ies_add_base': True,
                               'ies_lambda_mults': [0.1, 1.0, 10.0], 'lambda_scale_fac': [0.75, 1.0],
                               'ies_subset_size': 4, 'ies_bad_phi_sigma': 2.0, 'par_sigma_range': 4,
                               'overdue_giveup_fac': 5})
    pst.pestpp_options['ies_num_reals'] = NREALS[dataset]
    pst.write(os.path.join(d, f'{dataset}.pst'), version=2)
    sim = pd.read_csv(os.path.join(d, 'sim.dat'), sep=r'\s+', header=None, index_col=0)[1]
    r = ((od.obsval - sim.reindex(od.index)) * od.weight) ** 2
    print(dataset, 'npar', pst.npar_adj, 'nobs', pst.nnz_obs, 'phi(published params)', round(r.sum(), 1),
          r.groupby(od.obgnme).sum().round(1).to_dict())

def draw_priors(datasets):
    # 300 log-normal prior realizations per dataset (the first NREALS are used), drawn in a fixed order with one seed
    np.random.seed(SEED)
    for ds in datasets:
        d = os.path.join(RUNS, ds); pst = pyemu.Pst(os.path.join(d, f'{ds}.pst'))
        pe = pyemu.ParameterEnsemble.from_gaussian_draw(pst, pyemu.Cov.from_parameter_data(pst, sigma_range=4), num_reals=300)
        pe.enforce(); pe.to_binary(os.path.join(d, 'prior.jcb'))

if __name__ == '__main__':
    for ds in RAW:
        build(ds)
    draw_priors(list(RAW))
