"""Figure S2: violin plots of the measured concentrations of SMX, DeA-SMX, Nit-SMX, AmMet and the undetected TPs
(SMX mass balance) of the four batch experiments of Ma et al. (2021) (Hehe and Tugou sediments, oxic and anoxic).
Each violin combines the mean concentrations of the Hehe (riverbed) and Tugou (riverbank) sediments at one sampling
time."""
from common import *
import matplotlib.patches as mpatches

SMX0 = 3.9482e-8
ROWS = [0, 10]                      # mean concentrations: Riverbed.H (Hehe) and Riverbank.T (Tugou)
COLS = {'SMX': 3, 'AmMet': 5, 'DeA-SMX': 6, 'Nit-SMX': 7}
TIMES = {'oxic': [2, 14, 28, 70], 'anoxic': [2, 14, 28]}
xl = pd.ExcelFile(os.path.join(MEAS, 'Ma_2021_measurements.xlsx'))
data = {}
for cond, sheet in [('oxic', 0), ('anoxic', 1)]:
    df = pd.read_excel(xl, sheet_name=sheet)
    n = len(TIMES[cond])
    sp = {k: np.array([[df.iloc[r, c + 6 * g] for r in ROWS] for g in range(n)], float) for k, c in COLS.items()}
    sp['Undetected TPs'] = SMX0 - sum(sp[k] for k in COLS)
    data[cond] = sp
titles = ['SMX', 'DeA-SMX', 'Nit-SMX', 'AmMet', 'Undetected TPs']
fig, axes = plt.subplots(1, 5, figsize=(16, 4.5))
for ax, title in zip(axes, titles):
    for cond, off, col in [('anoxic', -0.2, 'lightblue'), ('oxic', 0.2, 'orange')]:
        v = data[cond][title] * 1e9
        parts = ax.violinplot(list(v), positions=np.arange(len(v)) + off, widths=0.3, showmedians=True)
        for pc in parts['bodies']:
            pc.set_facecolor(col); pc.set_edgecolor('black'); pc.set_alpha(0.8)
        ax.plot(np.repeat(np.arange(len(v)) + off, v.shape[1]), v.ravel(), 'k.', ms=3)
    if title == 'SMX':   # initial (input) concentration at t = 0
        ax.plot([-1], [SMX0 * 1e9], 'kx', ms=9, mew=2)
        ax.annotate('input', (-1, SMX0 * 1e9), xytext=(8, -3), textcoords='offset points', fontsize=8, va='top')
        ax.set_xticks(range(-1, 4)); ax.set_xticklabels([0] + TIMES['oxic'])
    else:
        ax.set_xticks(range(4)); ax.set_xticklabels(TIMES['oxic'])
    ax.set_title(title, fontsize=10); ax.set_xlabel('Time [d]')
axes[0].set_ylabel('Concentration [nM]')
fig.legend(handles=[mpatches.Patch(color='lightblue', label='anoxic'), mpatches.Patch(color='orange', label='oxic')],
           loc='lower center', ncol=2, fontsize=9, frameon=False)
fig.tight_layout(rect=[0, 0.06, 1, 1])
save(fig, 'FigS2_measured_concentrations_Ma2021.png', dpi=300)
