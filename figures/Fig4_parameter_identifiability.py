"""Figure 4: parameter identifiability 1 - SD_post/SD_prior (standard deviations of the log10 parameter values of
the prior and final posterior ensembles) for all five datasets."""
from common import *

M = pd.DataFrame(index=[NAME[d] for d in DS], columns=ORDER, dtype=float)
for ds in DS:
    it, pr, pe, oe, od = ensembles(ds)
    for p in pe.columns:
        M.loc[NAME[ds], p] = 1 - np.log10(pe[p]).std() / np.log10(pr[p]).std()
M.round(2).to_csv(os.path.join(OUT, 'Fig4_parameter_identifiability.csv'))
fig, ax = plt.subplots(figsize=(12, 3.8))
im = ax.imshow(M.values.astype(float), cmap='viridis', vmin=0, vmax=1, aspect='auto')
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = M.values[i, j]
        if np.isfinite(v):
            ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=7, color='black' if v > 0.55 else 'white')
ax.set_xticks(range(len(ORDER))); ax.set_xticklabels([tex(p) for p in ORDER], fontsize=10)
ax.set_yticks(range(len(DS))); ax.set_yticklabels(M.index, fontsize=10)
cb = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.03); cb.set_label('uncertainty reduction\n1 − SD$_{post}$/SD$_{prior}$')
fig.tight_layout()
save(fig, 'Fig4_parameter_identifiability_all_datasets.png', dpi=300)
print(M.round(2).to_string())
