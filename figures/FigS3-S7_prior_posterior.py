"""Figures S3-S7: prior and posterior distributions of all adjustable parameters for each dataset
(S3 oxic-H, S4 oxic-T, S5 anoxic-H, S6 anoxic-T, S7 anoxic-NDL)."""
from common import *
import math

for n, ds in zip(range(3, 8), DS):
    it, pr, pe, oe, od = ensembles(ds)
    cols = [c for c in ORDER if c in pe.columns]; nc = 4; nr = math.ceil(len(cols) / nc)
    fig, axs = plt.subplots(nr, nc, figsize=(13, 2.6 * nr)); axs = axs.flatten()
    for a, p in zip(axs, cols):
        lp, lq = np.log10(pr[p].dropna()), np.log10(pe[p].dropna())
        bins = np.linspace(min(lp.min(), lq.min()), max(lp.max(), lq.max()), 16)
        a.hist(lp, bins=bins, color='0.75', label='prior'); a.hist(lq, bins=bins, color='black', alpha=0.8, label='posterior')
        a.set_title(tex(p), fontsize=10); a.tick_params(labelsize=8)
    for a in axs[len(cols):]:
        a.axis('off')
    axs[0].legend(fontsize=8, frameon=False)
    fig.supxlabel('log$_{10}$(parameter value)', fontsize=10); fig.supylabel('number of realizations', fontsize=10)
    fig.tight_layout()
    save(fig, f'FigS{n}_{NAME[ds]}_prior_posterior.png', dpi=300)
