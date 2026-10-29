"""Figure S8 and Table S9: independent PEST++ IES calibration of reduced model set-ups (100 realizations each),
compared with the full model calibrated from the same prior realizations (calibration/reduced_setups).
Lines show the realization closest to the ensemble median, shaded areas the 5-95 % range of all realizations."""
from common import *
import json

G = 'reduced_setups'
OXIC = {'oxic_H': 'Full model', 'oxicH_no_nitr': 'Without nitrification (R4, R5)',
        'oxicH_no_undet': 'Without undetected TPs (R15, R16)', 'oxicH_no_r10': 'Without biologically mediated DeA-SMX (R10)'}
# anoxic-H: 8 iterations + 4 continued iterations (convergence of the set-up without R10); anoxic-NDL: compared at iteration 7
ANOX = [('anoxic-H', 'anoxic_H', 'Full model', 12), ('anoxic-H', 'anoxicH_no_r10', 'Without R10', 12),
        ('anoxic-NDL', 'anoxic_NDL', 'Full model', 7), ('anoxic-NDL', 'anoxicNDL_no_r10', 'Without R10', 7)]
SP = ['smx', 'des', 'nit', 'ammet', 'undet', 'no3', 'no2', 'doc']


def row(dataset, case, label, it):
    it, pr, pe, oe, od = ensembles(case, G, it)
    tot, grp = phi(oe, od); g = grp.median()
    return dict(dataset=dataset, setup=label, iteration=it, adjustable_parameters=pe.shape[1],
                observations=int((od.weight > 0).sum()), realizations=len(pe), phi_median=tot.median(), phi_min=tot.min(),
                **{f'phi_{k}_median': g.get(k, np.nan) for k in SP}), pe


rows, sims, reps = [], {}, {}
for case, label in OXIC.items():
    r, pe = row('oxic-H', case, label, None); rows.append(r)
    fixed = json.load(open(os.path.join(CAL, G, case, 'variant.json'))).get('fixed', {})
    t, s = simulate_ensemble('oxic_H', pe, f'reduced_{case}', fixed)
    sims[case] = s; reps[case] = representative(s, ['Smx', 'DES', 'Nit', 'Ammet'] + (['Undetected'] if case != 'oxicH_no_undet' else []))
for dataset, case, label, it in ANOX:
    rows.append(row(dataset, case, label, it)[0])
tab = pd.DataFrame(rows)
tab.to_csv(os.path.join(OUT, 'TableS9_reduced_model_setups.csv'), index=False, float_format='%.4g')
print(tab.round(1).to_string())

# colours distinct from the species colours of Figs. 2 and 3 (black, green, blue, red, grey)
COL = {'oxic_H': '#6a3d9a', 'oxicH_no_nitr': '#ff7f00', 'oxicH_no_undet': '#8c510a', 'oxicH_no_r10': '#e7298a'}
LS = {'oxic_H': '-', 'oxicH_no_nitr': ':', 'oxicH_no_undet': '--', 'oxicH_no_r10': '-.'}
PAN = [('Smx', 'SMX', 'smx'), ('DES', 'DeA-SMX', 'des'), ('Nit', 'Nit-SMX', 'nit'), ('Ammet', 'AmMet', 'ammet'),
       ('Undetected', 'Undetected TPs', 'undet')]
od = ensembles('oxic_H', G)[4]
fig, axes = plt.subplots(1, 5, figsize=(18, 3.9))
for ax, (h, lab, key) in zip(axes, PAN):
    for case in OXIC:
        if case == 'oxicH_no_undet' and key == 'undet':
            continue
        a = sims[case][h] * 1e9
        lo, hi = quantiles(a)
        ax.fill_between(t, lo, hi, color=COL[case], alpha=0.12, lw=0)
        ax.plot(t, a[reps[case]], LS[case], color=COL[case], lw=1.5, label=OXIC[case])
    o = od.loc[[f'{key}_t{x}' for x in [2, 14, 28, 70]]]
    ax.errorbar([2, 14, 28, 70], o.obsval * 1e9, yerr=1e9 / o.weight, fmt='o', color='k', ms=4, capsize=2, zorder=5)
    ax.set_title(lab); ax.set_xlabel('Time [d]')
axes[0].set_ylabel('Concentration [nM]')
hd, lb = axes[0].get_legend_handles_labels()
fig.legend(hd, lb, loc='lower center', ncol=4, frameon=False, fontsize=9)
fig.tight_layout(rect=[0, 0.1, 1, 1])
save(fig, 'FigS8_oxic-H_reduced_model_setups.png')
