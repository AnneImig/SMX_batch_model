import os
import glob
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# SETTINGS
# =========================
KGE_THRESHOLD = 1

script_dir = os.path.dirname(os.path.abspath(__file__))
post_dir = os.path.join(script_dir, "Post_processing")
plot_dir= os.path.join(post_dir, "histograms")

# =========================
# PRIOR-INFORMED ADJUSTMENT OF k4
# =========================


# PAR FILE READER (PRIOR)
# =========================
def read_par_file(par_file):
    with open(par_file, "r") as f:
        lines = f.readlines()

    params = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[0].startswith("k"):
            try:
                params[parts[0]] = float(parts[1])
            except:
                continue

    return params


def load_prior_distribution(script_dir):
    par_files = sorted(glob.glob(os.path.join(script_dir, "control_log*.par")))

    if not par_files:
        raise FileNotFoundError("No control_log*.par files found in script directory")

    data = []
    for f in par_files:
        data.append(read_par_file(f))

    return pd.DataFrame(data)


# =========================
# BPA + RES READERS
# =========================
def read_bpa(file_path):
    df = pd.read_csv(
        file_path,
        delim_whitespace=True,
        header=None,
        skiprows=1,
        names=["parameter", "value", "scale", "offset"]
    )

    return df[["parameter", "value"]]

def read_res(file_path):
    df = pd.read_csv(file_path, delim_whitespace=True)
    df.columns = df.columns.str.strip()

    df = df[["Name", "Measured", "Modelled", "Residual"]]
    df["Measured"] = pd.to_numeric(df["Measured"], errors="coerce")
    df["Modelled"] = pd.to_numeric(df["Modelled"], errors="coerce")

    return df


# =========================
# METRICS
# =========================
def compute_metrics(df):
    obs = df["Measured"].values
    sim = df["Modelled"].values

    mask = ~np.isnan(obs) & ~np.isnan(sim)
    obs = obs[mask]
    sim = sim[mask]

    if len(obs) == 0:
        return {"RMSE": np.nan, "R2": np.nan, "KGE": np.nan}

    rmse = np.sqrt(np.mean((sim - obs) ** 2))

    ss_res = np.sum((obs - sim) ** 2)
    ss_tot = np.sum((obs - np.mean(obs)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else np.nan

    if np.mean(obs) == 0 or np.std(obs) == 0:
        kge = np.nan
    else:
        r = np.corrcoef(obs, sim)[0, 1]
        alpha = np.std(sim) / np.std(obs)
        beta = np.mean(sim) / np.mean(obs)
        kge = 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)

    return {"RMSE": rmse, "R2": r2, "KGE": kge}


# =========================
# RUN PROCESSING
# =========================
def process_runs(post_dir):
    bpa_files = sorted(glob.glob(os.path.join(post_dir, "*.bpa.*")))
    res_files = sorted(glob.glob(os.path.join(post_dir, "*.res.*")))

    results = []

    for bpa_file in bpa_files:

        run_id = bpa_file.split(".")[-1]
        res_file = next((rf for rf in res_files if rf.endswith(f".{run_id}")), None)

        if res_file is None:
            continue

        print(f"Processing run {run_id}")

        params = read_bpa(bpa_file)



        res = read_res(res_file)
        metrics = compute_metrics(res)

        param_dict = dict(zip(params["parameter"], params["value"]))

        results.append({
            "run": run_id,
            **param_dict,
            **metrics
        })

    return pd.DataFrame(results)

# =========================
# GLUE ANALYSIS
# =========================
def glue_analysis(df):
    behavioral = df[df["KGE"] < KGE_THRESHOLD].copy()
    best_run = df.loc[df["KGE"].idxmax()]

    print("\n====================")
    print(f"Total runs: {len(df)}")
    print(f"Behavioral runs (KGE > {KGE_THRESHOLD}): {len(behavioral)}")
    print("====================\n")

    print("BEST RUN:")
    print(best_run[["run", "KGE", "R2", "RMSE"]])

    return behavioral, best_run


# =========================
# PLOT PRIOR vs GLUE
# =========================
def plot_prior_vs_glue(prior_df, posterior_df, output_path):

    exclude = ["run", "RMSE", "R2", "KGE"]
    params = [c for c in posterior_df.columns if c not in exclude]

    # numeric + log transform
    prior = prior_df.copy()
    post = posterior_df.copy()

    prior[params] = prior[params].apply(pd.to_numeric, errors="coerce")
    post[params] = post[params].apply(pd.to_numeric, errors="coerce")

    prior[params] = np.log10(prior[params])
    post[params] = np.log10(post[params])

    n = len(params)
    n_cols = 4
    n_rows = math.ceil(n / n_cols)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 3 * n_rows))
    axes = axes.flatten()

    for i, p in enumerate(params):
        ax = axes[i]

        ax.hist(prior[p].dropna(), bins=30, alpha=0.5, label="Prior")
        ax.hist(post[p].dropna(), bins=30, alpha=0.7, label="GLUE")

        ax.set_title(p)
        ax.tick_params(labelsize=8)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # =========================
    # LEGEND (last subplot)
    # =========================
    handles, labels = axes[0].get_legend_handles_labels()

    last_ax_index = i  # last plotted subplot from loop
    axes[last_ax_index].legend(handles, labels, loc="upper right", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_prior_vs_glue_subplots(prior_df, posterior, glue_df, output_dir, title="Prior vs GLUE"):
    """
    Subplot comparison of prior vs GLUE posterior distributions (log10 space).
    """

    os.makedirs(output_dir, exist_ok=True)

    # =========================
    # PARAMETERS TO EXCLUDE
    # =========================
    exclude_params = {
        "k_sdz", "k_sdx" ,"k14", "k9", "k10",   "k_doc2","k3", "k13","k16", "k15"
    }

    # keep only common numeric parameters
    cols = [
        c for c in prior_df.columns
        if c in glue_df.columns and c.lower() not in exclude_params
    ]

    if len(cols) == 0:
        print("No matching parameters to plot.")
        return

    # =========================
    # LOG TRANSFORM (SAFE)
    # =========================
    prior = prior_df.copy()
    glue = glue_df.copy()
    posterior = posterior.copy()

    prior[cols] = prior[cols].apply(pd.to_numeric, errors="coerce")
    glue[cols] = glue[cols].apply(pd.to_numeric, errors="coerce")
    posterior[cols] = posterior[cols].apply(pd.to_numeric, errors="coerce")

    # remove invalid values before log
    prior[cols] = prior[cols].replace([0, -np.inf], np.nan)
    glue[cols] = glue[cols].replace([0, -np.inf], np.nan)
    posterior[cols] = posterior[cols].replace([0, -np.inf], np.nan)

    prior[cols] = np.log10(prior[cols])
    glue[cols] = np.log10(glue[cols])
    posterior[cols] = np.log10(posterior[cols])

    # =========================
    # SUBPLOT LAYOUT
    # =========================
    n = len(cols)
    n_cols = math.ceil(math.sqrt(n))
    n_rows = math.ceil(n / n_cols)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3 * n_rows))
    axes = np.array(axes).flatten()

    # =========================
    # PLOTTING
    # =========================
    for i, col in enumerate(cols):
        ax = axes[i]

        ax.hist(prior[col].dropna(), bins=30, alpha=0.5, label="prior", color="dimgray")
        #ax.hist(posterior[col].dropna(), bins=30, alpha=0.7, label="posterior", color="black")
        ax.hist(glue[col].dropna(), bins=30, alpha=0.7, label="posterior", color="lightblue")

        # formatted label
        if col == "k_doc":
            label = r"$k_{l,'CH$_2$O'}$"
        elif col.startswith("k_"):
            label = rf"$k_{{{col.split('_',1)[1]}}}$"
        elif col.startswith("k"):
            label = rf"$k_{{{col[1:]}}}$"
        else:
            label = col

        ax.set_title(label)
        ax.tick_params(labelsize=8)

        # only bottom row gets x-label
        if i // n_cols == n_rows - 1:
            ax.set_xlabel("log10(parameter value)")
        else:
            ax.set_xlabel("")

        # only left column gets y-label
        if i % n_cols == 0:
            ax.set_ylabel("frequency")

    # =========================
    # REMOVE EMPTY AXES
    # =========================
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # =========================
    # LEGEND (last subplot)
    # =========================
    handles, labels = axes[0].get_legend_handles_labels()

    last_ax_index = i  # last plotted subplot from loop
    axes[last_ax_index].legend(handles, labels, loc="upper right", fontsize=8)


    #fig.suptitle(title, fontsize=16)

    plt.tight_layout(rect=[0, 0, 0.95, 0.95])

    out_file = os.path.join(output_dir, "FigS3_oxic_T_PDF.png")
    plt.savefig(out_file, dpi=300)
    plt.close()

    print(f"Saved: {out_file}")

# =========================
# MAIN
# =========================
def main():

    # --- prior ---

    prior = load_prior_distribution(script_dir)

    # --- posterior (SVDA runs) ---
    posterior= process_runs(post_dir)
    # apply prior-informed correction
    if "k4" in posterior.columns and "k11" in posterior.columns and "k12" in posterior.columns:

        k4_log = np.log10(0.2 * posterior["k11"] + 0.5 * posterior["k12"])
        k4_log = k4_log - 0.3   # decrease values

        posterior["k4"] = 10 ** k4_log
        # save CSV
    posterior.to_csv(os.path.join(post_dir, "04_posterior.csv"), index=False)

    behavioral, best_run = glue_analysis(posterior)

    behavioral.to_csv(os.path.join(post_dir, "05_posterior_glue.csv"), index=False)


    plot_prior_vs_glue_subplots(
        prior,
        posterior,
        behavioral,
        os.path.join(plot_dir),
        title="oxic T"
    )



# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()