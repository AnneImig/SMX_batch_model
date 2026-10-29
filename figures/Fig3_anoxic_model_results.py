"""Figure 3: posterior median and 5-95 % range of the PEST++ IES ensembles against the measurements for the
anoxic-H (a-c), anoxic-T (d-f) and anoxic-NDL (g-i) datasets."""
from common import *

DSA = ['anoxic_H', 'anoxic_T', 'anoxic_NDL']
R = {ds: load(ds) for ds in DSA}
fig, ax = plt.subplots(3, 3, figsize=(16, 11))
L = 'abcdefghi'
for i, ds in enumerate(DSA):
    h1 = panel_tps(ax[i, 0], R[ds], ds, L[3 * i]); h2 = panel_ammet(ax[i, 1], R[ds], ds, L[3 * i + 1])
    h3 = panel_n(ax[i, 2], R[ds], ds, L[3 * i + 2])
    if i == 0:
        H = h1 + h2 + h3
for a in ax[2]:
    a.set_xlabel('Time [d]')
fig.legend(H, [x.get_label() for x in H], loc='lower center', ncol=9, frameon=False, fontsize=9)
fig.tight_layout(rect=[0, 0.04, 1, 1])
save(fig, 'Fig3_anoxic-H_anoxic-T_anoxic-NDL_model_results.png')
