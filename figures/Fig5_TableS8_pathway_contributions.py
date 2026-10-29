"""Figure 5 and Table S8: relative contribution of co-metabolic (CM), biologically mediated (BM) and metabolic
processes to SMX, Nit-SMX and DeA-SMX transformation, computed for every posterior realization of the PEST++ IES
ensembles (cached in output/cache/rates_<dataset>.npz).

Classification (Fig. 5 caption, Table 1):
  SMX fate:     metabolic R8;  BM R9, R10, R12, R13;  CM R11, R14, R15, R16
  Nit-SMX fate: BM R12;        CM R9, R13
  DeA-SMX fate: BM R10, R12;   CM R11, R14
Shares are instantaneous rate fractions: sum of |rates| in a group / sum over all groups.
Rate columns are taken by name, because the get() slots of R10 and R11 differ between the oxic and the
anoxic/NDL templates.
"""
from common import *
TEND_R = {'oxic_H': 70, 'oxic_T': 70, 'anoxic_H': 28, 'anoxic_T': 28, 'anoxic_NDL': 88}
COMMON = {'R8': 'rate_Ammet', 'R9': 'rateNit', 'R12': 'rateDES_NIT_N', 'R13': 'rateNIT_Smx_N',
          'R14': 'rateDES_Smx_O2', 'R15': 'rate_undet', 'R16': 'undet_smx'}
def rate_cols(ds):
    c = dict(COMMON)
    if ds.startswith('oxic'):
        c.update(R10='rate_Smx_DES_O', R11='rateDes_N')
    else:
        c.update(R10='rateDes_N', R11='rate_Smx_DES_O')
    return c
GROUPS = {'SMX': {'MET': ['R8'], 'BM': ['R9', 'R10', 'R12', 'R13'], 'CM': ['R11', 'R14', 'R15', 'R16']},
          'Nit': {'BM': ['R12'], 'CM': ['R9', 'R13']},
          'DeA': {'BM': ['R10', 'R12'], 'CM': ['R11', 'R14']},
          # sensitivity: SMX fate without the lumped exchange with undetected TPs (R15, R16)
          'SMXmeas': {'MET': ['R8'], 'BM': ['R9', 'R10', 'R12', 'R13'], 'CM': ['R11', 'R14']}}

def run_one(args):
    ds, p, tg = args
    try:
        data, col = fr.simulate(ds, p)
    except Exception:
        return None
    t = data[:, col['Time']]; k = t > 0
    rc = rate_cols(ds)
    return {r: np.interp(tg, t[k], np.abs(data[k, col[h]])) for r, h in rc.items()}

def shares(rates):
    out = {}
    for tgt, grp in GROUPS.items():
        tot = sum(rates[r] for g in grp.values() for r in g)
        for g, rs in grp.items():
            out[f'{tgt}_{g}'] = 100 * sum(rates[r] for r in rs) / np.where(tot > 0, tot, np.nan)
    return out

if __name__ == '__main__':
    res = {}
    for ds in DS:
        fn = os.path.join(CACHE, f'rates_{ds}.npz')
        tg = np.linspace(0.1, TEND_R[ds], 4 * TEND_R[ds])
        if os.path.exists(fn):
            z = np.load(fn); res[ds] = {k: z[k] for k in z.files if k != 't'}; continue
        it, pr, pe, oe, od = ensembles(ds)
        with Pool(int(os.environ.get('NPROC', 2))) as pool:
            out = [o for o in pool.map(run_one, [(ds, r.to_dict(), tg) for _, r in pe.iterrows()]) if o]
        S = [shares(o) for o in out]
        res[ds] = {k: np.array([s[k] for s in S]) for k in S[0]}
        np.savez(fn, t=tg, **res[ds])
        print(ds, 'realizations', len(S), flush=True)

    # ---- Table S8: shares per dataset at 2, 10, 28 and 70 d (within the simulated period) and time-averaged
    KEYS = ['SMX_CM', 'SMX_BM', 'SMX_MET', 'SMXmeas_CM', 'DeA_CM', 'Nit_CM']
    rows = []
    for ds in DS:
        tg = np.load(os.path.join(CACHE, f'rates_{ds}.npz'))['t']
        for tt in [2, 10, 28, 70, 'time-averaged']:
            if tt != 'time-averaged' and tt > TEND_R[ds]:
                continue
            row = dict(dataset=NAME[ds], time_d=tt)
            for k in KEYS:
                v = res[ds][k][:, int(np.argmin(abs(tg - tt)))] if tt != 'time-averaged' else np.nanmean(res[ds][k], axis=1)
                v = v[np.isfinite(v)]
                row[f'{k}_median'] = np.median(v); row[f'{k}_p05'] = np.percentile(v, 5); row[f'{k}_p95'] = np.percentile(v, 95)
            rows.append(row)
    tab = pd.DataFrame(rows); tab.round(1).to_csv(os.path.join(OUT, 'TableS8_pathway_contributions.csv'), index=False)
    print(tab[['dataset', 'time_d'] + [k + '_median' for k in KEYS]].round(1).to_string())
    # time-averaged shares per dataset
    avg = []
    for ds in DS:
        a = {k: np.nanmean(v, axis=1) for k, v in res[ds].items()}
        avg.append(dict(dataset=NAME[ds], **{f'{k}_median': np.nanmedian(v) for k, v in a.items()},
                        **{f'{k}_p05': np.nanpercentile(v, 5) for k, v in a.items()},
                        **{f'{k}_p95': np.nanpercentile(v, 95) for k, v in a.items()}))
    pd.DataFrame(avg).round(1).to_csv(os.path.join(OUT, 'Fig5_pathway_contributions_time_averaged.csv'), index=False)
    print(pd.DataFrame(avg)[['dataset', 'SMX_CM_median', 'SMX_CM_p05', 'SMX_CM_p95', 'SMX_BM_median', 'SMX_MET_median']].round(1).to_string())

    # ---- Fig. 5: median share with 5-95 % band (rows: SMX, Nit-SMX, DeA-SMX)
    fig, ax = plt.subplots(3, 5, figsize=(14, 8), sharey=True)
    for j, ds in enumerate(DS):
        tg = np.load(os.path.join(CACHE, f'rates_{ds}.npz'))['t']
        for i, (tgt, lab) in enumerate([('SMX', 'SMX fate [%]'), ('Nit', 'Nit-SMX fate [%]'), ('DeA', 'DeA-SMX fate [%]')]):
            a = ax[i, j]
            for g, c, ls in [('CM', 'black', '-'), ('BM', '0.55', '--'), ('MET', 'tab:red', ':')]:
                k = f'{tgt}_{g}'
                if k not in res[ds]:
                    continue
                v = res[ds][k]
                a.fill_between(tg, np.nanpercentile(v, 5, 0), np.nanpercentile(v, 95, 0), color=c, alpha=0.15, lw=0)
                a.plot(tg, np.nanmedian(v, 0), ls, color=c, lw=1.5,
                       label={'CM': 'co-metabolic', 'BM': 'biologically mediated', 'MET': 'metabolic (R8)'}[g])
            a.set_ylim(0, 100); a.set_xlim(0, TEND_R[ds])
            if j == 0:
                a.set_ylabel(lab)
            if i == 0:
                a.set_title(NAME[ds], fontsize=11)
            if i == 2:
                a.set_xlabel('Time [d]')
    h, l = ax[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, frameon=False)
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    save(fig, 'Fig5_pathway_contributions_all_datasets.png')
