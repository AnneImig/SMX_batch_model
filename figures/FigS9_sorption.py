"""Figure S9: sorption of SMX and its TPs in the four Ma et al. (2021) models.
(a, b) Sorbed fraction simulated with the fitted surface-complexation constants (Table S2) compared with the
adsorption percentages measured in the sorption batch experiments of Ma et al. (2021) (mean and standard deviation).
(c-f) Simulated sorbed amounts over time for the realization closest to the ensemble median (Figs. 2 and 3).
Sorption is linear and instantaneous, so the sorbed fraction does not depend on the calibrated rate constants."""
from common import *

SP = [('Smx', 'Smxsorb', 'SMX'), ('DES', 'Dessorb', 'DeA-SMX'), ('Nit', 'Nitrosorb', 'Nit-SMX'), ('Ammet', 'Ammetsorb', 'AmMet')]
# measured adsorption percentage (mean, SD) of the sorption batch experiments (Table S2; Ma et al., 2021)
MEASURED = {'H': {'SMX': (3.6, 0.0), 'AmMet': (6.0, 11.7), 'DeA-SMX': (6.7, 11.4), 'Nit-SMX': (32.0, 13.1)},
            'T': {'SMX': (9.3, 2.0), 'AmMet': (17.5, 1.7), 'DeA-SMX': (18.3, 7.0), 'Nit-SMX': (37.0, 10.7)}}
DSM = ['oxic_H', 'oxic_T', 'anoxic_H', 'anoxic_T']
sim = {}
for ds in DSM:
    it, pr, pe, oe, od = ensembles(ds)
    t, s = simulate_ensemble(ds, pe, f'posterior_{ds}')
    rep = representative(s, PLOTTED[ds.split('_')[0]])
    data, col = fr.simulate(ds, pe.iloc[rep].to_dict())
    sim[ds] = (data, col)
rows = []
fig = plt.figure(figsize=(14, 7.5))
gs = fig.add_gridspec(2, 4)
for j, site in enumerate(['H', 'T']):
    ax = fig.add_subplot(gs[0, 2 * j:2 * j + 2])
    data, col = sim[f'oxic_{site}']
    x = np.arange(len(SP))
    fsim = []
    for aq, so, lab in SP:
        a, b = data[1:, col[aq]], data[1:, col[so]]
        k = (a + b) > 0
        fsim.append(100 * np.median(b[k] / (a[k] + b[k])))
        m, sd = MEASURED[site][lab]
        rows.append(dict(sediment='Hehe' if site == 'H' else 'Tugou', compound=lab, measured_mean=m, measured_sd=sd,
                         simulated=round(fsim[-1], 1)))
    ax.bar(x - 0.2, [MEASURED[site][l][0] for _, _, l in SP], 0.4, yerr=[MEASURED[site][l][1] for _, _, l in SP],
           color='0.75', capsize=3, label='measured (sorption batch)')
    ax.bar(x + 0.2, fsim, 0.4, color='black', label='model')
    ax.set_xticks(x); ax.set_xticklabels([l for _, _, l in SP]); ax.set_ylabel('Sorbed fraction [%]')
    ax.set_title(f"{'ab'[j]}) {'Hehe riverbed (oxic-H, anoxic-H)' if site == 'H' else 'Tugou riverbank (oxic-T, anoxic-T)'}",
                 loc='left', fontsize=10)
    ax.set_ylim(0, 55)
    if j == 0:
        ax.legend(frameon=False, fontsize=9)
cols = {'Smxsorb': 'black', 'Dessorb': 'green', 'Nitrosorb': 'blue', 'Ammetsorb': 'red'}
for i, ds in enumerate(DSM):
    ax = fig.add_subplot(gs[1, i]); data, col = sim[ds]
    t = data[:, col['Time']]
    for aq, so, lab in SP:
        ax.plot(t, data[:, col[so]] * 1e9, color=cols[so], lw=1.4, label=lab)
    ax.set_title(f"{'cdef'[i]}) {NAME[ds]}", loc='left', fontsize=10); ax.set_xlabel('Time [d]')
    ax.set_xlim(0, TEND[ds])
    if i == 0:
        ax.set_ylabel('Sorbed amount [nmol/kgw]'); ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
save(fig, 'FigS9_sorption.png', dpi=300)
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'FigS9_sorption_measured_vs_model.csv'), index=False)
print(pd.DataFrame(rows).to_string())
