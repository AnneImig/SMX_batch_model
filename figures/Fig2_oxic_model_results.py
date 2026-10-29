"""Figure 2: posterior median and 5-95 % range of the PEST++ IES ensembles against the measurements for the
oxic-H (a, b) and oxic-T (c, d) datasets."""
from common import *

R = {ds: load(ds) for ds in ['oxic_H', 'oxic_T']}
fig, ax = plt.subplots(2, 2, figsize=(11, 7.5))
for i, (ds, (l1, l2)) in enumerate(zip(['oxic_H', 'oxic_T'], [('a', 'b'), ('c', 'd')])):
    h1 = panel_tps(ax[i, 0], R[ds], ds, l1); h2 = panel_ammet(ax[i, 1], R[ds], ds, l2)
for a in ax[1]:
    a.set_xlabel('Time [d]')
fig.legend(h1 + h2, [x.get_label() for x in h1 + h2], loc='lower center', ncol=7, frameon=False, fontsize=9)
fig.tight_layout(rect=[0, 0.05, 1, 1])
save(fig, 'Fig2_oxic-H_oxic-T_model_results.png')
