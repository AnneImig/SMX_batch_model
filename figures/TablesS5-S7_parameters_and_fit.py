"""Tables S5-S7: initial (prior mean) values and posterior median and 5-95 % range of all parameters
(S5 oxic, S6 anoxic) and the model-data agreement of the posterior ensembles (S7)."""
from common import *

rows, fit = [], []
for ds in DS:
    it, pr, pe, oe, od = ensembles(ds)
    base = pd.read_csv(glob.glob(os.path.join(CAL, 'full_model', ds, '*.par_data.csv'))[0]).set_index('parnme')
    for p in [c for c in ORDER if c in pe.columns]:
        q = np.log10(pe[p])
        rows.append(dict(dataset=NAME[ds], parameter=TXT.get(p, p), initial=base.loc[p, 'parval1'],
                         prior_min=base.loc[p, 'parlbnd'], prior_max=base.loc[p, 'parubnd'],
                         posterior_median=10 ** q.median(), posterior_p05=10 ** q.quantile(.05),
                         posterior_p95=10 ** q.quantile(.95)))
    tot, grp = phi(oe, od)
    g = grp.median()
    fit.append(dict(dataset=NAME[ds], posterior_realizations=len(pe), observations=int((od.weight > 0).sum()),
                    phi_median=tot.median(), phi_p05=tot.quantile(.05), phi_p95=tot.quantile(.95),
                    **{f'phi_{k}_median': g.get(k, np.nan) for k in ['smx', 'des', 'nit', 'ammet', 'undet', 'no3', 'no2', 'doc']}))
par = pd.DataFrame(rows)
par[par.dataset.str.startswith('oxic')].to_csv(os.path.join(OUT, 'TableS5_parameters_oxic.csv'), index=False, float_format='%.4g')
par[par.dataset.str.startswith('anoxic')].to_csv(os.path.join(OUT, 'TableS6_parameters_anoxic.csv'), index=False, float_format='%.4g')
pd.DataFrame(fit).to_csv(os.path.join(OUT, 'TableS7_model_data_agreement.csv'), index=False, float_format='%.4g')
print(pd.DataFrame(fit).round(1).to_string())
