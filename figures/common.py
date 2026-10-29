"""Shared paths and helper functions for the figure and table scripts.

The scripts read the PEST++ IES ensembles in calibration/ and write the figures and tables to output/.
Simulated time series of the posterior realizations are cached in output/cache/ (they are provided with
the repository; delete the cache to recompute them with PHREEQC, which takes several hours).
"""
import os, sys, glob, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from multiprocessing import Pool
from scipy.stats.mstats import hdquantiles

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEAS = os.path.join(REPO, 'measurements')
CAL = os.path.join(REPO, 'calibration')
OUT = os.path.join(REPO, 'output')
CACHE = os.path.join(OUT, 'cache')
os.makedirs(CACHE, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, 'model'))
import forward_run as fr  # noqa: E402

DS = ['oxic_H', 'oxic_T', 'anoxic_H', 'anoxic_T', 'anoxic_NDL']
NAME = {'oxic_H': 'oxic-H', 'oxic_T': 'oxic-T', 'anoxic_H': 'anoxic-H', 'anoxic_T': 'anoxic-T', 'anoxic_NDL': 'anoxic-NDL'}
TEND = {'oxic_H': 70, 'oxic_T': 70, 'anoxic_H': 30, 'anoxic_T': 30, 'anoxic_NDL': 90}
SERIES = ['Smx', 'DES', 'Nit', 'Ammet', 'Undetected', 'Doc', 'O2', 'NO3-', 'NO2-', 'HNO2', 'Amonia']
ORDER = ['k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7', 'kl_no3', 'k8', 'kl_ch2o', 'k9', 'k10', 'k11', 'k12', 'k13', 'k14',
         'kl2_ch2o', 'k15', 'k16']
TEX = {'kl_ch2o': r'$K_{l,CH_2O}$', 'kl2_ch2o': r"$K_{l',CH_2O}$", 'kl_no3': r'$K_{l,NO_3^-}$'}
TXT = {'kl_no3': 'Kl,NO3', 'kl_ch2o': 'Kl,CH2O', 'kl2_ch2o': "Kl',CH2O"}


def tex(p):
    return TEX.get(p, f'$k_{{{p[1:]}}}$')


# ------------------------------------------------------------------ ensembles
def final_iteration(master, case):
    return max(int(f.split('.')[-3]) for f in glob.glob(os.path.join(master, f'{case}.*.par.csv')))


def ensembles(case, group='full_model', it=None):
    """prior and posterior parameter ensembles, posterior observation ensemble and observation data"""
    d = os.path.join(CAL, group, case); m = os.path.join(d, 'master')
    it = final_iteration(m, case) if it is None else it
    rd = lambda f: pd.read_csv(os.path.join(m, f), index_col=0).apply(pd.to_numeric, errors='coerce')
    pr, pe, oe = rd(f'{case}.0.par.csv'), rd(f'{case}.{it}.par.csv'), rd(f'{case}.{it}.obs.csv')
    pe = pe.loc[pe.index.intersection(oe.index)]
    od = pd.read_csv(glob.glob(os.path.join(d, '*.obs_data.csv'))[0]).set_index('obsnme')
    return it, pr, pe, oe, od


def phi(oe, od):
    """weighted sum of squared residuals per realization (total and per observation group)"""
    nz = od[od.weight > 0]
    r = ((oe[nz.index] - nz.obsval) * nz.weight) ** 2
    return r.sum(axis=1), r.T.groupby(nz.obgnme).sum().T


# ------------------------------------------------------------------ posterior simulations
def _sim_one(a):
    ds, p, tg = a
    try:
        data, col = fr.simulate(ds, p)
    except Exception:
        return None
    t = data[:, col['Time']]; k = t > 0
    return {s: np.interp(tg, np.r_[0, t[k]], np.r_[data[0, col[s]], data[k, col[s]]]) for s in SERIES}


def simulate_ensemble(ds, pe, cache_name, fixed=None):
    """time series of all posterior realizations (cached in output/cache/<cache_name>.npz)"""
    fn = os.path.join(CACHE, f'{cache_name}.npz')
    if os.path.exists(fn):
        z = np.load(fn); return z['t'], {k: z[k] for k in SERIES}
    tg = np.linspace(0, TEND[ds], 4 * TEND[ds] + 1)
    args = []
    for _, row in pe.iterrows():
        p = row.to_dict(); p.update(fixed or {}); args.append((ds, p, tg))
    with Pool(int(os.environ.get('NPROC', 2))) as pool:
        outs = pool.map(_sim_one, args)
    sims = {k: np.array([o[k] for o in outs if o is not None]) for k in SERIES}
    np.savez(fn, t=tg, **sims)
    return tg, sims


def representative(s, keys):
    """index of the posterior realization closest to the pointwise ensemble median (mean squared deviation over
    time, each series scaled by the maximum of its median); used as the line in Figs. 2, 3 and S8, because a
    pointwise median combines different realizations at different times and is therefore not smooth"""
    d = np.zeros(len(s[keys[0]]))
    for k in keys:
        med = np.median(s[k], 0); sc = np.abs(med).max() or 1.0
        d += (((s[k] - med) / sc) ** 2).mean(1)
    return int(np.argmin(d))


PLOTTED = {'oxic': ['Smx', 'DES', 'Nit', 'Undetected', 'Ammet', 'Doc', 'O2'],
           'anoxic': ['Smx', 'DES', 'Nit', 'Undetected', 'Ammet', 'Doc', 'NO3-', 'NO2-', 'HNO2'],
           'ndl': ['Smx', 'DES', 'Nit', 'Doc', 'NO3-', 'NO2-', 'HNO2']}


def load(ds):
    it, pr, pe, oe, od = ensembles(ds)
    t, s = simulate_ensemble(ds, pe, f'posterior_{ds}')
    rep = representative(s, PLOTTED['ndl' if ds == 'anoxic_NDL' else ds.split('_')[0]])
    print(f'{NAME[ds]}: iteration {it}, {len(s["Smx"])} posterior realizations, representative realization {rep}')
    return dict(it=it, pr=pr, pe=pe, oe=oe, od=od, t=t, s=s, rep=rep, n_all=len(s['Smx']))


# ------------------------------------------------------------------ plotting helpers
C = dict(smx='black', des='green', nit='blue', undet='0.4', ammet='red', doc='0.2', o2='0.2', no2='deepskyblue',
         no3='limegreen', hno2='navy')


def quantiles(a, p=(0.05, 0.95)):
    """5th and 95th percentiles over the realizations at each time, estimated with the Harrell-Davis quantile
    estimator (a weighted average of all order statistics), which avoids the jagged edges of the empirical
    percentiles of a finite ensemble"""
    q = np.asarray(hdquantiles(a, prob=list(p), axis=0))
    return q[0], q[1]


def band(ax, t, a, color, label, scale=1.0, ls='-', rep=None):
    """5-95 % range of all realizations (shaded) and the representative realization (line)"""
    a = a * scale
    lo, hi = quantiles(a)
    ax.fill_between(t, lo, hi, color=color, alpha=0.18, lw=0)
    return ax.plot(t, a[rep] if rep is not None else np.median(a, 0), ls, color=color, lw=1.4, label=label)[0]


def meas(ax, od, sp, color, scale=1.0, marker='s'):
    o = od[od.obgnme == sp]
    if len(o) == 0:
        return None
    tt = [float(n.split('_t')[1].replace('p', '.')) for n in o.index]
    s = np.where(o.weight > 0, 1 / o.weight.replace(0, np.nan), np.nan)
    return ax.errorbar(tt, o.obsval * scale, yerr=np.nan_to_num(s) * scale, fmt=marker, color=color, ms=4, capsize=2,
                       zorder=5)


def do_meas(ds):
    """measured dissolved oxygen (not used for calibration)"""
    x = pd.read_excel(os.path.join(MEAS, 'Ma_2021_measurements.xlsx'), sheet_name=3, header=None)
    c = 2 if ds == 'oxic_H' else 7
    return np.array(x.iloc[3:10, 1], float), np.array(x.iloc[13:20, c], float)


def panel_tps(ax, R, ds, letter):
    t, s, od = R['t'], R['s'], R['od']
    sc = 1e9 if ds != 'anoxic_NDL' else 1e6
    h = [band(ax, t, s['Smx'], C['smx'], 'SMX', sc, rep=R['rep']), band(ax, t, s['DES'], C['des'], 'DeA-SMX', sc, rep=R['rep'])]
    if ds != 'anoxic_NDL':
        h.append(band(ax, t, s['Undetected'], C['undet'], 'Undet', sc, ':', rep=R['rep']))
    for sp in ['smx', 'des', 'undet']:
        meas(ax, od, sp, C[sp], sc)
    ax2 = ax.twinx()
    h.append(band(ax2, t, s['Nit'], C['nit'], 'Nit-SMX', sc, rep=R['rep']))
    meas(ax2, od, 'nit', C['nit'], sc)
    unit = 'nM' if sc == 1e9 else 'µM'
    ax.set_ylabel(f'SMX, DeA-SMX, Undet [{unit}]')
    ax2.set_ylabel(f'Nit-SMX [{unit}]', color=C['nit'])
    ax.set_title(f'{letter}) {NAME[ds]}', loc='left', fontsize=10)
    return h


def panel_ammet(ax, R, ds, letter):
    t, s, od = R['t'], R['s'], R['od']
    h = [band(ax, t, s['Doc'], C['doc'], 'CH$_2$O', 1e3, '-.', rep=R['rep'])]
    if ds.startswith('oxic'):
        h.append(band(ax, t, s['O2'], C['o2'], 'DO', 1e3, '--', rep=R['rep']))
        dm = do_meas(ds); ax.plot(dm[0], dm[1] * 1e3, 'o', color=C['o2'], ms=3, mfc='white')
    if ds == 'anoxic_NDL':
        meas(ax, od, 'doc', C['doc'], 1e3, 'o')
    ax.set_ylabel('CH$_2$O, DO [mM]')
    if ds != 'anoxic_NDL':
        ax2 = ax.twinx()
        h.append(band(ax2, t, s['Ammet'], C['ammet'], 'AmMet', 1e9, rep=R['rep']))
        meas(ax2, od, 'ammet', C['ammet'], 1e9)
        ax2.set_ylabel('AmMet [nM]', color=C['ammet'])
    ax.set_title(f'{letter}) {NAME[ds]}', loc='left', fontsize=10)
    return h


def panel_n(ax, R, ds, letter):
    t, s, od = R['t'], R['s'], R['od']
    h = [band(ax, t, s['NO3-'], C['no3'], 'Nitrate', 1e3, rep=R['rep']), band(ax, t, s['NO2-'], C['no2'], 'Nitrite', 1e3, ':', rep=R['rep'])]
    meas(ax, od, 'no3', C['no3'], 1e3); meas(ax, od, 'no2', C['no2'], 1e3)
    ax.set_ylabel('Nitrate, nitrite [mM]')
    ax2 = ax.twinx()
    h.append(band(ax2, t, s['HNO2'], C['hno2'], 'HNO$_2$', 1e9, '--', rep=R['rep']))
    ax2.set_ylabel('HNO$_2$ [nM]', color=C['hno2'])
    ax.set_title(f'{letter}) {NAME[ds]}', loc='left', fontsize=10)
    return h


def save(fig, name, dpi=600):
    fn = os.path.join(OUT, name)
    fig.savefig(fn, dpi=dpi); plt.close(fig)
    print('saved', os.path.relpath(fn, REPO))
