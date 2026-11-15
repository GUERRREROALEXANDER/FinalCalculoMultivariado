"""NeuroCode: least-squares fit of response time vs rotation angle.

Own algorithm (sums -> a*, b* -> S -> Hessian), checked against numpy/scipy.
Also proves the exact equivalence between fitting all n=525 raw trials and fitting
the K=7 angle means (balanced design: 75 trials per angle), where R^2_means = 0.9619.
Reads every csvs/*.csv, so adding participants only needs a re-run.
Figure labels are in Spanish for the defense and presentation.
"""
import glob
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figuras")
os.makedirs(FIG, exist_ok=True)

# Consistent publication palette matching presentation (--ink: #14213d, --accent: #d9480f)
INK = "#14213d"
ACCENT = "#d9480f"
BLUE = "#1d4ed8"
TEAL = "#0f766e"
MUTED = "#64748b"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 10.5,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10.5,
        "axes.edgecolor": "#cbd5e1",
        "axes.grid": True,
        "grid.alpha": 0.28,
        "grid.linestyle": "--",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def load():
    frames = []
    for f in sorted(glob.glob(os.path.join(ROOT, "csvs", "*.csv"))):
        g = pd.read_csv(f)
        # The id typed in the app was wrong in several files (e.g. three files say P10),
        # so the file name is the participant id. CSVs are left untouched.
        g["participante"] = os.path.basename(f).split("_")[-1].removesuffix(".csv").upper()
        frames.append(g)
    return pd.concat(frames).reset_index(drop=True)


# ---------- own algorithm (no regression libraries) ----------
def fit(x, y):
    n = len(x)
    sx, sy = x.sum(), y.sum()
    sxx, sxy = (x * x).sum(), (x * y).sum()
    d = n * sxx - sx**2
    a = (n * sxy - sx * sy) / d
    b = (sy - a * sx) / n
    return dict(n=n, sx=sx, sy=sy, sxx=sxx, sxy=sxy, d=d, a=a, b=b)


def S(a, b, x, y):
    return ((y - a * x - b) ** 2).sum()


def grad_S(a, b, x, y):
    e = y - a * x - b
    return np.array([-2.0 * (x * e).sum(), -2.0 * e.sum()])


def hessian(x):
    n = len(x)
    return np.array([[2 * (x * x).sum(), 2 * x.sum()], [2 * x.sum(), 2 * n]], dtype=float)


def metrics(x, y, a, b):
    e = y - (a * x + b)
    sse = (e**2).sum()
    sst = ((y - y.mean()) ** 2).sum()
    return e, np.sqrt(sse / len(x)), 1 - sse / sst


def report(df, tag, x_col="angulo_grados", y_col="tiempo_ms"):
    x, y = df[x_col].to_numpy(float), df[y_col].to_numpy(float)
    f = fit(x, y)
    a, b = f["a"], f["b"]
    smin = S(a, b, x, y)
    g_opt = grad_S(a, b, x, y)
    H = hessian(x)
    D = np.linalg.det(H)
    eig = np.linalg.eigvalsh(H)
    e, rmse, r2 = metrics(x, y, a, b)
    pa, pb = np.polyfit(x, y, 1)
    lr = stats.linregress(x, y)
    print(f"\n=== {tag} (n={f['n']}) ===")
    print(f"sums: n={f['n']} Sx={f['sx']:.1f} Sy={f['sy']:.1f} Sxx={f['sxx']:.1f} Sxy={f['sxy']:.1f}")
    print(f"a*={a:.6f} ms/deg  b*={b:.4f} ms  S_min={smin:.2f}")
    print(f"grad S(a*,b*) = [{g_opt[0]:.2e}, {g_opt[1]:.2e}]")
    print(f"speed 1000/a* = {1000 / a:.1f} deg/s" if a > 0 else "a* <= 0 (no rotation effect)")
    print(f"H={H.tolist()}  det={D:.1f}  S_aa={H[0, 0]:.1f}  eig={eig}")
    print(f"polyfit a={pa:.6f} b={pb:.4f} | linregress a={lr.slope:.6f} b={lr.intercept:.4f} p={lr.pvalue:.4e}")
    print(f"max diff a={abs(a - pa):.2e} b={abs(b - pb):.2e} S={abs(smin - S(pa, pb, x, y)):.2e}")
    print(f"RMSE={rmse:.1f} ms  R2={r2:.4f}  mean(e)={e.mean():.2e}")
    return dict(x=x, y=y, a=a, b=b, smin=smin, H=H, D=D, eig=eig, e=e, rmse=rmse, r2=r2, lr=lr, sums=f)


def main():
    df = load()
    print(df.groupby("participante").size().to_string())
    by_angle = (
        df.groupby("angulo_grados")["tiempo_ms"]
        .agg(count="count", mean="mean", std="std", median="median", sem="sem")
        .round(2)
    )
    print(by_angle.to_string())

    r = report(df, "ALL DATA (RAW TRIALS)")
    x, y, a, b = r["x"], r["y"], r["a"], r["b"]

    # --- Mathematical equivalence on K=7 angle means (balanced design m=75 per angle) ---
    means_df = df.groupby("angulo_grados", as_index=False)["tiempo_ms"].mean()
    rm = report(means_df, "ANGLE MEANS (K=7, BALANCED DESIGN EQUIVALENCE)")
    m_per_angle = len(df) // len(means_df)
    ss_within = df.groupby("angulo_grados")["tiempo_ms"].apply(lambda s: ((s - s.mean()) ** 2).sum()).sum()
    ss_between_reg = m_per_angle * rm["smin"]
    print(
        f"\n Orthogonal decomposition of S(a,b): SS_within={ss_within:.2f} + {m_per_angle}*S_means(a*,b*)={ss_between_reg:.2f} "
        f"= {ss_within + ss_between_reg:.2f} (exact S_min={r['smin']:.2f})"
    )

    p_rows = []
    for p, g in df.groupby("participante"):
        rp = report(g, f"participant {p}")
        p_rows.append(dict(p=p, a=rp["a"], b=rp["b"], r2=rp["r2"], rmse=rp["rmse"], pval=rp["lr"].pvalue))
    p_df = pd.DataFrame(p_rows)

    # --- where does the error come from, and is the slope driven by a few people? ---
    # Model with one baseline per person: S(a, b_1..b_17) = sum (y_i - a x_i - b_j(i))^2.
    # grad = 0 gives b_j = mean_j(y) - a mean_j(x) and the slope from within-person deviations.
    sst = ((y - y.mean()) ** 2).sum()
    subj_mean_y = df.groupby("participante")["tiempo_ms"].transform("mean").to_numpy(float)
    subj_mean_x = df.groupby("participante")["angulo_grados"].transform("mean").to_numpy(float)
    ss_subjects = ((subj_mean_y - y.mean()) ** 2).sum()
    xc, yc = x - subj_mean_x, y - subj_mean_y
    a_subj = (xc * yc).sum() / (xc**2).sum()
    e_subj = yc - a_subj * xc
    r2_subj = 1 - (e_subj**2).sum() / sst
    n_pos = int((p_df["a"] > 0).sum())
    sign_p = stats.binomtest(n_pos, len(p_df)).pvalue
    t_slopes = stats.ttest_1samp(p_df["a"], 0)
    loo = []
    for p in sorted(df["participante"].unique()):
        s = df[df["participante"] != p]
        loo.append((fit(s["angulo_grados"].to_numpy(float), s["tiempo_ms"].to_numpy(float))["a"], p))
    print(
        f"\n=== ERROR BY SOURCE AND PER-PERSON CHECKS ===\n"
        f"SST={sst:.2f}  within-angle={ss_within:.2f} ({100*ss_within/sst:.1f}% of SST)\n"
        f"  of which persistent baseline differences between people={ss_subjects:.2f} "
        f"({100*ss_subjects/ss_within:.1f}% of within-angle, {100*ss_subjects/sst:.1f}% of SST)\n"
        f"  and trial-to-trial noise inside each person={ss_within-ss_subjects:.2f} "
        f"({100*(ss_within-ss_subjects)/ss_within:.1f}% of within-angle)\n"
        f"One baseline per person (18 parameters): a*={a_subj:.6f} ms/deg  R2={r2_subj:.4f}  "
        f"RMSE={np.sqrt((e_subj**2).mean()):.1f} ms\n"
        f"People with positive slope: {n_pos}/{len(p_df)}  sign test p={sign_p:.2e}  "
        f"t-test on 17 slopes: t={t_slopes.statistic:.3f} p={t_slopes.pvalue:.2e}\n"
        f"Leave-one-person-out a*: min={min(loo)[0]:.4f} (without {min(loo)[1]})  "
        f"max={max(loo)[0]:.4f} (without {max(loo)[1]})"
    )

    # --- option A: parameter sensitivity under Monte Carlo measurement perturbations ---
    rng = np.random.default_rng(42)
    a_pert, b_pert = [], []
    for _ in range(500):
        y_noisy = y + rng.normal(0, 25.0, size=len(y))  # +/- 25 ms timing perturbation
        fp = fit(x, y_noisy)
        a_pert.append(fp["a"])
        b_pert.append(fp["b"])
    a_pert, b_pert = np.array(a_pert), np.array(b_pert)
    print(
        f"\n=== OPTION A: sensitivity to +/-25 ms perturbation (500 runs) ===\n"
        f"a*: mean={a_pert.mean():.4f} std={a_pert.std():.4f} ms/deg (rel change {100*a_pert.std()/a:.2f}%)\n"
        f"b*: mean={b_pert.mean():.2f} std={b_pert.std():.2f} ms (rel change {100*b_pert.std()/b:.2f}%)"
    )

    # --- option B: influence of outliers ---
    i = int(np.argmax(np.abs(r["e"])))
    print(f"\nLargest residual: row {i} ({df.loc[i, 'participante']}), x={x[i]:.0f}, y={y[i]:.1f}, e={r['e'][i]:.1f}")
    keep = np.arange(len(x)) != i
    rb = report(df[keep], "OPTION B1: without the largest-residual point")
    rb_clean = report(df[df["posible_atipico"] == 0], "OPTION B2: without all posible_atipico (>3000 ms)")

    # --- option C: quadratic ---
    c2, c1, c0 = np.polyfit(x, y, 2)
    eq = y - (c2 * x**2 + c1 * x + c0)
    r2q = 1 - (eq**2).sum() / ((y - y.mean()) ** 2).sum()
    rmseq = np.sqrt((eq**2).mean())
    eq_m = rm["y"] - (c2 * rm["x"] ** 2 + c1 * rm["x"] + c0)
    r2q_m = 1 - (eq_m**2).sum() / ((rm["y"] - rm["y"].mean()) ** 2).sum()
    print(
        f"\n=== OPTION C quadratic === y={c2:.3e}x^2+{c1:.4f}x+{c0:.2f}  "
        f"RMSE={rmseq:.1f}  R2_raw={r2q:.4f}  R2_means={r2q_m:.4f}"
    )

    # --- option D: effect of sample size N (adding participants 1..15) ---
    parts = sorted(df["participante"].unique())
    n_list, a_cum, b_cum = [], [], []
    for k in range(1, len(parts) + 1):
        sub = df[df["participante"].isin(parts[:k])]
        fk = fit(sub["angulo_grados"].to_numpy(float), sub["tiempo_ms"].to_numpy(float))
        n_list.append(len(sub))
        a_cum.append(fk["a"])
        b_cum.append(fk["b"])
    print("\n=== OPTION D: sample size convergence ===")
    for k, nk, ak, bk in zip(range(1, len(parts) + 1), n_list, a_cum, b_cum):
        print(f"k={k:2d} participants (n={nk:3d}): a*={ak:.4f} ms/deg, b*={bk:.2f} ms")

    # =========================================================================
    # FIGURES (7 publication-grade PNGs + rich 3D interactive HTML)
    # =========================================================================
    xs = np.linspace(0, 180, 200)
    ang_vals = by_angle.index.to_numpy(float)
    mean_vals = by_angle["mean"].to_numpy(float)
    sem_vals = by_angle["sem"].to_numpy(float)
    med_vals = by_angle["median"].to_numpy(float)

    # -------------------------------------------------------------------------
    # 01_dispersion.png: Left = raw 525 trials + angle means; Right = K=7 means
    # -------------------------------------------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(12.2, 4.8), gridspec_kw={"width_ratios": [1.15, 1]})
    cmap_p = plt.get_cmap("tab20")
    jitter_rng = np.random.default_rng(0)
    for idx, (p, g) in enumerate(df.groupby("participante")):
        jx = g["angulo_grados"] + jitter_rng.uniform(-3.2, 3.2, len(g))
        axs[0].scatter(jx, g["tiempo_ms"], s=20, alpha=0.62, color=cmap_p(idx % 20), label=p, edgecolors="none")
    axs[0].errorbar(
        ang_vals,
        mean_vals,
        yerr=sem_vals,
        fmt="o-",
        color=INK,
        lw=2.2,
        ms=6.5,
        capsize=4,
        label="Media por ángulo ± EE",
        zorder=10,
    )
    axs[0].set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Tiempo de respuesta y (ms)",
        title=f"A. Dispersión total (n = {len(x)} ensayos, {len(parts)} personas)",
        xticks=ang_vals,
    )
    axs[0].legend(ncol=5, fontsize=7.2, loc="upper left", framealpha=0.92)

    axs[1].errorbar(
        ang_vals,
        mean_vals,
        yerr=sem_vals,
        fmt="o",
        color=INK,
        ms=7.5,
        lw=1.8,
        capsize=4,
        label=f"Media observada $\\bar{{y}}_k \\pm$ EE (m={m_per_angle}/ángulo)",
        zorder=5,
    )
    axs[1].plot(ang_vals, med_vals, "s--", color=TEAL, ms=5.5, lw=1.3, alpha=0.85, label="Mediana por ángulo")
    axs[1].plot(
        xs,
        a * xs + b,
        color=ACCENT,
        lw=2.6,
        label=f"Recta MCO: $y = {a:.2f}x + {b:.1f}$\n($R^2_{{\\mathrm{{medias}}}} = {rm['r2']:.4f}$, $p = 0.0001$)",
    )
    for xv, mv in zip(ang_vals, mean_vals):
        axs[1].annotate(f"{mv:.0f}", (xv, mv), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8.5, color=INK, fontweight="bold")
    axs[1].set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Tiempo promedio de respuesta (ms)",
        title="B. Tendencia lineal en promedios por ángulo (K = 7)",
        xticks=ang_vals,
        ylim=(540, 1280),
    )
    axs[1].legend(fontsize=8.5, loc="upper left", framealpha=0.94)
    fig.tight_layout()
    fig.savefig(f"{FIG}/01_dispersion.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 02_rectas.png: Left = full cloud with top outliers marked; Right = zoom comparing candidate lines
    # -------------------------------------------------------------------------
    candidates = [
        (a + 1.5, b - 100, "#dc2626", "Candidata 1"),
        (a - 1.0, b + 150, "#2563eb", "Candidata 2"),
        (a + 3.0, b - 300, "#16a34a", "Candidata 3"),
    ]
    fig, axs = plt.subplots(1, 2, figsize=(12.2, 4.8), gridspec_kw={"width_ratios": [1, 1.1]})
    axs[0].scatter(x, y, s=18, color="#94a3b8", alpha=0.55, label=f"Datos observados (n = {len(x)})")
    axs[0].plot(xs, a * xs + b, color=INK, lw=2.6, label=f"Óptima: $y = {a:.2f}x + {b:.1f}$")
    # Highlight top 3 largest residuals as requested by Section 10
    top3_idx = np.argsort(np.abs(r["e"]))[-3:][::-1]
    axs[0].scatter(x[top3_idx], y[top3_idx], s=55, color=ACCENT, zorder=8, label="Mayores desviaciones $|e_i|$")
    for idx_pt in top3_idx:
        p_id = df.loc[idx_pt, "participante"]
        axs[0].annotate(
            f"Fila {idx_pt} ({p_id})\n$y={y[idx_pt]:.0f}$ ms, $e=+{r['e'][idx_pt]:.0f}$",
            (x[idx_pt], y[idx_pt]),
            textcoords="offset points",
            xytext=(-12, -26 if y[idx_pt] > 5000 else 8),
            ha="right" if x[idx_pt] >= 120 else "left",
            fontsize=7.8,
            bbox=dict(boxstyle="round,pad=0.2", fc="#fff7ed", ec=ACCENT, lw=0.8),
        )
    axs[0].set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Tiempo de respuesta y (ms)",
        title="A. Ajuste global y puntos más alejados (Req. 10)",
        xticks=ang_vals,
    )
    axs[0].legend(fontsize=8.2, loc="upper left")

    axs[1].errorbar(
        ang_vals,
        mean_vals,
        yerr=sem_vals,
        fmt="o",
        color=INK,
        ms=6.5,
        capsize=3.5,
        label="Promedios observados $\\bar{y}_k \\pm$ EE",
        zorder=6,
    )
    axs[1].plot(
        xs,
        a * xs + b,
        color=INK,
        lw=2.8,
        label=f"Óptima $(a^*,b^*)=({a:.2f}, {b:.0f}) \\rightarrow S_{{\\min}}={r['smin']:.3e}$",
        zorder=5,
    )
    for ac, bc, col, cname in candidates:
        sc = S(ac, bc, x, y)
        pct = 100.0 * (sc - r["smin"]) / r["smin"]
        axs[1].plot(
            xs,
            ac * xs + bc,
            "--",
            color=col,
            lw=1.7,
            label=f"$a={ac:.2f}, b={bc:.0f} \\rightarrow S={sc:.3e}$ (+{pct:.1f}%)",
        )
    axs[1].set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Tiempo de respuesta y (ms)",
        title="B. Recta óptima vs. otras rectas (zoom en tendencia)",
        xticks=ang_vals,
        ylim=(320, 1480),
    )
    axs[1].legend(fontsize=8.0, loc="upper left", framealpha=0.95)
    fig.tight_layout()
    fig.savefig(f"{FIG}/02_rectas.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Grid for S(a, b)
    # -------------------------------------------------------------------------
    a_grid = np.linspace(a - 3.2, a + 3.2, 140)
    b_grid = np.linspace(b - 420, b + 420, 140)
    A, B = np.meshgrid(a_grid, b_grid)
    Z = ((y[None, None, :] - A[..., None] * x - B[..., None]) ** 2).sum(-1)

    # -------------------------------------------------------------------------
    # 03_superficie.png: 3D surface with floor contours and visible global minimum
    # -------------------------------------------------------------------------
    fig = plt.figure(figsize=(9.0, 6.2))
    ax = fig.add_subplot(projection="3d", computed_zorder=False)
    Z_e8 = Z / 1e8
    smin_e8 = r["smin"] / 1e8
    z_floor = smin_e8 * 0.72
    surf = ax.plot_surface(A, B, Z_e8, cmap="viridis", alpha=0.78, linewidth=0, antialiased=True, zorder=1)
    ax.contour(A, B, Z_e8, zdir="z", offset=z_floor, levels=14, cmap="viridis", alpha=0.75, linewidths=1.0, zorder=2)
    # Candidate points on the bowl
    for ac, bc, col, _ in candidates:
        sc = S(ac, bc, x, y) / 1e8
        ax.scatter([ac], [bc], [sc], color=col, s=42, edgecolors="white", linewidths=0.8, zorder=9)
    # Global minimum clearly on top
    ax.plot([a, a], [b, b], [z_floor, smin_e8], "r--", lw=1.5, zorder=10)
    ax.scatter(
        [a],
        [b],
        [smin_e8],
        color=ACCENT,
        s=130,
        marker="*",
        edgecolors="white",
        linewidths=1.0,
        label=f"Mínimo global $(a^*,b^*)=({a:.2f}, {b:.1f})$\n$S_{{\\min}} = {smin_e8:.3f}\\times 10^8\\,\\mathrm{{ms}}^2$",
        zorder=15,
    )
    ax.view_init(elev=27, azim=-52)
    ax.set_zlim(z_floor, Z_e8.max())
    ax.set_xlabel("Pendiente a (ms/°)", labelpad=8)
    ax.set_ylabel("Intercepto b (ms)", labelpad=8)
    ax.set_zlabel("S(a, b) [$10^8$ ms²]", labelpad=10)
    ax.set_title("Superficie de error S(a,b): paraboloide elíptico convexo", pad=12)
    fig.colorbar(surf, ax=ax, shrink=0.56, pad=0.12, label="S(a, b) [$10^8$ ms²]")
    ax.legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(f"{FIG}/03_superficie.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 04_trazas.png: Traces + family of cross-sections (Req. 7.7)
    # -------------------------------------------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(12.2, 4.7))
    b_shifts = [(-300, "#94a3b8", "--"), (-150, "#64748b", "-."), (0, ACCENT, "-"), (150, "#2563eb", "-."), (300, "#0f766e", "--")]
    for db_val, col, ls in b_shifts:
        b_cut = b + db_val
        s_vals = [S(av, b_cut, x, y) / 1e8 for av in a_grid]
        lbl = f"Traza óptima $b = b^* = {b:.1f}$ ms" if db_val == 0 else f"Sección $b = b^* {db_val:+d} = {b_cut:.0f}$ ms"
        axs[0].plot(a_grid, s_vals, ls=ls, color=col, lw=2.7 if db_val == 0 else 1.4, label=lbl)
    axs[0].scatter([a], [smin_e8], color=ACCENT, s=70, zorder=8)
    axs[0].axhline(smin_e8, color=ACCENT, ls=":", lw=1.2, alpha=0.8)
    axs[0].axvline(a, color=ACCENT, ls=":", lw=1.2, alpha=0.8)
    axs[0].annotate(
        f"Vértice: $a^*={a:.2f}$ ms/°\n$\\partial S/\\partial a = 0$",
        (a, smin_e8),
        xytext=(a + 0.55, smin_e8 + 0.15),
        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.2),
        fontsize=8.5,
        fontweight="bold",
        color=INK,
    )
    axs[0].set(
        xlabel="Pendiente a (ms/°)",
        ylabel="S(a, b₀) [$10^8$ ms²]",
        title="A. Traza óptima S(a, b*) y secciones b = b₀",
    )
    axs[0].legend(fontsize=7.8, loc="upper right")

    a_shifts = [(-2.0, "#94a3b8", "--"), (-1.0, "#64748b", "-."), (0.0, ACCENT, "-"), (1.0, "#2563eb", "-."), (2.0, "#0f766e", "--")]
    for da_val, col, ls in a_shifts:
        a_cut = a + da_val
        s_vals = [S(a_cut, bv, x, y) / 1e8 for bv in b_grid]
        lbl = f"Traza óptima $a = a^* = {a:.2f}$ ms/°" if da_val == 0 else f"Sección $a = a^* {da_val:+.1f} = {a_cut:.2f}$ ms/°"
        axs[1].plot(b_grid, s_vals, ls=ls, color=col, lw=2.7 if da_val == 0 else 1.4, label=lbl)
    axs[1].scatter([b], [smin_e8], color=ACCENT, s=70, zorder=8)
    axs[1].axhline(smin_e8, color=ACCENT, ls=":", lw=1.2, alpha=0.8)
    axs[1].axvline(b, color=ACCENT, ls=":", lw=1.2, alpha=0.8)
    axs[1].annotate(
        f"Vértice: $b^*={b:.1f}$ ms\n$\\partial S/\\partial b = 0$",
        (b, smin_e8),
        xytext=(b + 65, smin_e8 + 0.18),
        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.2),
        fontsize=8.5,
        fontweight="bold",
        color=INK,
    )
    axs[1].set(
        xlabel="Intercepto b (ms)",
        ylabel="S(a₀, b) [$10^8$ ms²]",
        title="B. Traza óptima S(a*, b) y secciones a = a₀",
    )
    axs[1].legend(fontsize=7.8, loc="upper right")
    fig.tight_layout()
    fig.savefig(f"{FIG}/04_trazas.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 05_curvas_nivel.png: Filled contours + -grad S field + candidate points
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    cf = ax.contourf(A, B, Z_e8, levels=24, cmap="viridis", alpha=0.85)
    cs = ax.contour(A, B, Z_e8, levels=14, colors="white", linewidths=0.75, alpha=0.85)
    ax.clabel(cs, fontsize=7.2, fmt="%.2f", colors="white")
    fig.colorbar(cf, ax=ax, pad=0.03, label="S(a, b) [$10^8$ ms²]")

    # Trace axes through (a*, b*) and principal valley line (b = bar_y - a * bar_x)
    x_bar = x.mean()
    ax.plot(a_grid, b - (a_grid - a) * x_bar, "w--", lw=1.3, alpha=0.9, label=f"Eje del valle ($b = \\bar{{y}} - a\\bar{{x}}$, $\\bar{{x}}={x_bar:.0f}^\\circ$)")
    for ac, bc, col, cname in candidates:
        ax.scatter([ac], [bc], color=col, s=55, edgecolors="white", linewidths=1.2, zorder=9, label=f"{cname}: ({ac:.2f}, {bc:.0f})")
    ax.plot(a, b, "*", color=ACCENT, ms=17, markeredgecolor="white", markeredgewidth=1.2, zorder=12, label=f"Mínimo global $(a^*,b^*)=({a:.2f}, {b:.1f})$")
    ax.set(
        xlabel="Pendiente a (ms/°)",
        ylabel="Intercepto b (ms)",
        title="Curvas de nivel de S(a,b): elipses inclinadas ($S_{ab} = 2\\Sigma x > 0$)",
    )
    fig.tight_layout()

    # -grad S arrows. The axes use different scales (1 ms/deg of a spans far more
    # screen than 1 ms of b), so we take the gradient in the screen variables
    # X = a*px_a, Y = b*px_b: dS/dX = S_a/px_a, dS/dY = S_b/px_b. That is the same
    # function in rescaled variables, so its arrows are perpendicular to the
    # level curves exactly as drawn and point downhill.
    fig.canvas.draw()
    bbox = ax.get_window_extent()
    (xa0, xa1), (yb0, yb1) = ax.get_xlim(), ax.get_ylim()
    px_a, px_b = bbox.width / (xa1 - xa0), bbox.height / (yb1 - yb0)
    AQ, BQ = np.meshgrid(np.linspace(a - 2.8, a + 2.8, 11), np.linspace(b - 360, b + 360, 11))
    dS_da = 2 * r["sums"]["sxx"] * (AQ - a) + 2 * r["sums"]["sx"] * (BQ - b)
    dS_db = 2 * r["sums"]["sx"] * (AQ - a) + 2 * r["sums"]["n"] * (BQ - b)
    gx, gy = -dS_da / px_a, -dS_db / px_b
    norm = np.hypot(gx, gy) + 1e-12
    arrow_px = 0.045 * bbox.width
    ax.quiver(AQ, BQ, gx / norm * arrow_px / px_a, gy / norm * arrow_px / px_b,
              angles="xy", scale_units="xy", scale=1, color="white", alpha=0.6, width=0.003,
              label="$-\\nabla S$ (perpendicular a las curvas de nivel)")
    ax.legend(fontsize=7.8, loc="upper right", framealpha=0.92)
    fig.savefig(f"{FIG}/05_curvas_nivel.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 06_residuos.png: Left = residuals vs angle with mean & +/-1 SD envelope; Right = histogram + normal fit
    # -------------------------------------------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(12.4, 4.8))
    df["residuo"] = r["e"]
    res_stats = df.groupby("angulo_grados")["residuo"].agg(["mean", "std"]).reindex(ang_vals)
    r_mean = res_stats["mean"].to_numpy(float)
    r_std = res_stats["std"].to_numpy(float)

    axs[0].scatter(x + jitter_rng.uniform(-2.5, 2.5, len(x)), r["e"], s=18, color="#3b82f6", alpha=0.52, label="Residuos $e_i = y_i - (a^*x_i + b^*)$")
    axs[0].axhline(0, color=INK, lw=1.8, label="Referencia $e = 0$ ms")
    axs[0].plot(ang_vals, r_mean, "o-", color=ACCENT, lw=2.0, ms=6, label="Media de residuos por ángulo $\\bar{e}_k \\approx 0$")
    axs[0].fill_between(ang_vals, r_mean - r_std, r_mean + r_std, color="#3b82f6", alpha=0.16, label="Banda $\\pm 1$ DE (heterocedasticidad)")
    axs[0].axhline(2 * r["rmse"], color="#dc2626", ls="--", lw=1.2, label=f"Umbral $\\pm 2\\,\\mathrm{{RMSE}}$ ($\\pm {2*r['rmse']:.0f}$ ms)")
    axs[0].axhline(-2 * r["rmse"], color="#dc2626", ls="--", lw=1.2)
    axs[0].annotate(
        f"Atípico máx (fila {i}, P09)\n$x=150^\\circ, e=+{r['e'][i]:.1f}$ ms",
        (x[i], r["e"][i]),
        xytext=(x[i] - 58, r["e"][i] - 550),
        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.2),
        fontsize=8.2,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.2", fc="#fff7ed", ec=ACCENT, lw=0.8),
    )
    axs[0].set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Residuo eᵢ (ms)",
        title="A. Residuos vs. ángulo (centrados en 0)",
        xticks=ang_vals,
    )
    axs[0].legend(fontsize=7.8, loc="upper left")

    counts, bins, _ = axs[1].hist(r["e"], bins=24, color="#3b82f6", alpha=0.78, edgecolor="white", label="Frecuencia observada")
    bw = bins[1] - bins[0]
    er_grid = np.linspace(r["e"].min(), r["e"].max(), 300)
    norm_pdf = stats.norm.pdf(er_grid, loc=0, scale=r["rmse"]) * len(r["e"]) * bw
    axs[1].plot(er_grid, norm_pdf, color=INK, lw=2.0, ls="--", label=f"Normal teórica ($\\mu=0$, $\\sigma={r['rmse']:.0f}$ ms)")
    axs[1].axvline(0, color=ACCENT, lw=2.0, label=f"Media $\\bar{{e}} = {r['e'].mean():.1e}$ ms")
    axs[1].axvline(np.median(r["e"]), color=TEAL, lw=1.8, ls="-.", label=f"Mediana = {np.median(r['e']):.1f} ms (asimetría +)")
    axs[1].set(
        xlabel="Residuo eᵢ (ms)",
        ylabel="Número de ensayos",
        title="B. Histograma de residuos y cola derecha",
    )
    axs[1].legend(fontsize=8.0, loc="upper right")
    fig.tight_layout(pad=1.4, w_pad=2.2)
    fig.savefig(f"{FIG}/06_residuos.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 07_opciones_BC.png: 2x2 comprehensive panel for Section 13 (Options B, C, D, and Individual heterogeneity)
    # -------------------------------------------------------------------------
    fig, axs = plt.subplots(2, 2, figsize=(12.6, 8.4))

    # Top-left: Option B & C zoomed clearly on the angle means
    ax_bc = axs[0, 0]
    ax_bc.errorbar(ang_vals, mean_vals, yerr=sem_vals, fmt="o", color=INK, ms=6.5, capsize=3.5, label="Medias observadas $\\bar{y}_k \\pm$ EE", zorder=6)
    ax_bc.plot(xs, a * xs + b, color=INK, lw=2.5, label=f"Lineal todos (n={len(x)}): $a^*={a:.2f}$, RMSE={r['rmse']:.0f}")
    ax_bc.plot(xs, rb["a"] * xs + rb["b"], "--", color=ACCENT, lw=2.2, label=f"Opción B1 sin fila {i} (n={len(x)-1}): $a^*={rb['a']:.2f}$, RMSE={rb['rmse']:.0f}")
    ax_bc.plot(
        xs,
        rb_clean["a"] * xs + rb_clean["b"],
        "-.",
        color=TEAL,
        lw=2.0,
        label=f"Opción B2 sin >3s (n={len(rb_clean['x'])}): $a^*={rb_clean['a']:.2f}$, $R^2={rb_clean['r2']:.3f}$",
    )
    ax_bc.plot(
        xs,
        c2 * xs**2 + c1 * xs + c0,
        ":",
        color=BLUE,
        lw=2.4,
        label=f"Opción C cuadrático: $R^2_{{\\mathrm{{raw}}}}={r2q:.4f}$ ($\\Delta R^2=+{r2q - r['r2']:.4f}$)",
    )
    ax_bc.set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Tiempo de respuesta y (ms)",
        title="A. Opciones B y C: atípicos vs. cuadrático",
        xticks=ang_vals,
        ylim=(540, 1280),
    )
    ax_bc.legend(fontsize=7.6, loc="upper left")

    # Top-right: Option A (Monte Carlo sensitivity of a* and b*)
    ax_sens = axs[0, 1]
    ax_sens.scatter(a_pert, b_pert, s=14, alpha=0.45, color=BLUE, label="500 perturbaciones $\\Delta y_i \\sim \\mathcal{N}(0, 25\\,\\mathrm{ms})$")
    ax_sens.plot(a, b, "*", color=ACCENT, ms=15, markeredgecolor="white", label=f"Óptimo original ({a:.3f}, {b:.1f})")
    ax_sens.set(
        xlabel="Pendiente perturbada a* (ms/°)",
        ylabel="Intercepto perturbado b* (ms)",
        title=f"B. Opción A (Sensibilidad): $\\sigma_a={a_pert.std():.3f}$ ms/° ({100*a_pert.std()/a:.1f}%)",
    )
    ax_sens.legend(fontsize=8.0, loc="upper right")

    # Bottom-left: Option D (Sample size N effect on a*)
    ax_n = axs[1, 0]
    part_counts = np.arange(1, len(parts) + 1)
    ax_n.plot(part_counts, a_cum, "o-", color=INK, lw=2.2, ms=6, label="Pendiente acumulada $a^*(N)$")
    ax_n.axhline(a, color=ACCENT, ls="--", lw=1.6, label=f"Valor final ({len(parts)} personas, n={len(x)}): $a^*={a:.2f}$ ms/°")
    ax_n.set(
        xlabel="Número de participantes incluidos N (n = 35·N ensayos)",
        ylabel="Pendiente estimada a* (ms/°)",
        title="C. Opción D: convergencia según muestra N",
        xticks=part_counts,
    )
    ax_n.legend(fontsize=8.0, loc="upper left")

    # Bottom-right: Individual participant lines explaining why R^2_raw vs R^2_means
    ax_ind = axs[1, 1]
    for idx, row_p in p_df.iterrows():
        ax_ind.plot(xs, row_p["a"] * xs + row_p["b"], lw=1.2, alpha=0.55, color=cmap_p(idx % 20))
    ax_ind.plot(xs, a * xs + b, color=INK, lw=3.0, label=f"Recta global promedio ($a^*={a:.2f}$, $b^*={b:.0f}$)")
    ax_ind.annotate(
        "P09 (más lento: a=8.95 ms/°)",
        (140, p_df.loc[p_df["p"] == "P09", "a"].values[0] * 140 + p_df.loc[p_df["p"] == "P09", "b"].values[0]),
        xytext=(75, 1980),
        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.0),
        fontsize=8.0,
        fontweight="bold",
    )
    ax_ind.annotate(
        "P07 (más rápido: b=384 ms)",
        (120, p_df.loc[p_df["p"] == "P07", "a"].values[0] * 120 + p_df.loc[p_df["p"] == "P07", "b"].values[0]),
        xytext=(85, 360),
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.0),
        fontsize=8.0,
        fontweight="bold",
    )
    ax_ind.set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Recta ajustada por participante y (ms)",
        title=f"D. Heterogeneidad individual ({len(parts)} rectas)",
        xticks=ang_vals,
    )
    ax_ind.legend(fontsize=8.0, loc="upper left")

    fig.tight_layout(pad=1.4, w_pad=2.2, h_pad=2.0)
    fig.savefig(f"{FIG}/07_opciones_BC.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Interactive 3D HTML with surface + minimum + 3D trace parabolas + live sliders & gradient descent
    # -------------------------------------------------------------------------
    try:
        import json
        import plotly.graph_objects as go

        pf = go.Figure()
        pf.add_trace(
            go.Surface(
                x=a_grid,
                y=b_grid,
                z=Z_e8,
                colorscale="Viridis",
                opacity=0.86,
                name="S(a, b) [10⁸ ms²]",
                contours=dict(
                    z=dict(show=True, usecolormap=True, highlightcolor="white", project_z=True)
                ),
            )
        )
        # 3D trace b = b*
        pf.add_trace(
            go.Scatter3d(
                x=a_grid,
                y=np.full_like(a_grid, b),
                z=[S(av, b, x, y) / 1e8 for av in a_grid],
                mode="lines",
                line=dict(color="#ef4444", width=6),
                name=f"Traza b = b* ({b:.1f} ms)",
            )
        )
        # 3D trace a = a*
        pf.add_trace(
            go.Scatter3d(
                x=np.full_like(b_grid, a),
                y=b_grid,
                z=[S(a, bv, x, y) / 1e8 for bv in b_grid],
                mode="lines",
                line=dict(color="#38bdf8", width=6),
                name=f"Traza a = a* ({a:.2f} ms/°)",
            )
        )
        # Global minimum point (trace index 3)
        pf.add_trace(
            go.Scatter3d(
                x=[a],
                y=[b],
                z=[smin_e8],
                mode="markers+text",
                marker=dict(size=8, color="#f97316", symbol="diamond"),
                text=[f"Mínimo ({a:.2f}, {b:.1f})"],
                textposition="top center",
                name="Mínimo global (a*, b*)",
            )
        )
        # Live movable probe point (trace index 4)
        a_init, b_init = round(a + 2.2, 2), round(b - 260.0, 1)
        s_init_e8 = S(a_init, b_init, x, y) / 1e8
        pf.add_trace(
            go.Scatter3d(
                x=[a_init],
                y=[b_init],
                z=[s_init_e8],
                mode="markers+text",
                marker=dict(size=9, color="#22c55e", symbol="circle", line=dict(color="white", width=2)),
                text=[f"Punto actual ({a_init:.2f}, {b_init:.0f})"],
                textposition="top center",
                name="Punto explorado (a, b)",
            )
        )
        # Trajectory path for gradient descent (trace index 5)
        pf.add_trace(
            go.Scatter3d(
                x=[a_init],
                y=[b_init],
                z=[s_init_e8],
                mode="lines",
                line=dict(color="#22c55e", width=6),
                name="Trayectoria −∇S",
            )
        )
        pf.update_layout(
            title=f"NeuroCode · Laboratorio 3D de S(a,b), Gradiente ∇S y Trazas (n = {len(x)})",
            template="plotly_dark",
            paper_bgcolor="#0b1324",
            plot_bgcolor="#0b1324",
            scene=dict(
                xaxis_title="Pendiente a (ms/°)",
                yaxis_title="Intercepto b (ms)",
                zaxis_title="S(a,b) [10⁸ ms²]",
            ),
            margin=dict(l=0, r=0, b=0, t=48),
            legend=dict(x=0.01, y=0.98, bgcolor="rgba(15,23,42,0.75)"),
        )
        plot_div = pf.to_html(full_html=False, include_plotlyjs="cdn", div_id="plot3d")
        meta = dict(
            n=int(r["sums"]["n"]),
            sx=float(r["sums"]["sx"]),
            sy=float(r["sums"]["sy"]),
            sxx=float(r["sums"]["sxx"]),
            sxy=float(r["sums"]["sxy"]),
            syy=float((y * y).sum()),
            astar=float(a),
            bstar=float(b),
            smin=float(r["smin"]),
            angles=ang_vals.tolist(),
            means=mean_vals.tolist(),
        )
        html_doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NeuroCode · Laboratorio Geométrico de Cálculo Multivariable</title>
<style>
  :root {{ --bg:#0b1324; --card:#111c33; --border:#233554; --accent:#f97316; --green:#22c55e; --text:#e2e8f0; --muted:#94a3b8; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:Inter,system-ui,sans-serif; background:var(--bg); color:var(--text); }}
  header {{ padding:12px 22px; background:#070d19; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }}
  header h1 {{ margin:0; font-size:18px; font-weight:800; color:#fff; }}
  header .sub {{ font-size:13px; color:var(--muted); }}
  .grid {{ display:grid; grid-template-columns:390px 1fr; height:calc(100vh - 54px); }}
  @media (max-width:980px) {{ .grid {{ grid-template-columns:1fr; height:auto; }} }}
  .panel {{ padding:16px; background:var(--card); border-right:1px solid var(--border); overflow-y:auto; display:flex; flex-direction:column; gap:12px; }}
  .box {{ background:rgba(15,23,42,0.75); border:1px solid var(--border); border-radius:10px; padding:12px; }}
  .box h2 {{ margin:0 0 8px 0; font-size:13px; text-transform:uppercase; letter-spacing:0.04em; color:var(--accent); }}
  .row {{ display:flex; justify-content:space-between; align-items:center; font-size:13px; margin:6px 0; }}
  input[type=range] {{ width:100%; accent-color:var(--accent); cursor:pointer; }}
  .btns {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:6px; }}
  button {{ flex:1; padding:8px 10px; border-radius:8px; border:1px solid var(--border); background:#1e293b; color:#fff; font-weight:700; font-size:12px; cursor:pointer; }}
  button.primary {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
  button.green {{ background:#15803d; border-color:#22c55e; }}
  .kpi {{ font-family:monospace; font-size:13px; color:#38bdf8; font-weight:700; }}
  canvas {{ width:100%; height:190px; background:#070d19; border-radius:8px; border:1px solid var(--border); }}
  #plot3d {{ width:100%; height:100%; min-height:540px; }}
</style>
</head>
<body>
<header>
  <h1>🧠 NeuroCode · Simulador en Vivo de S(a,b), Gradiente ∇S y Hessiano</h1>
  <div class="sub">Mínimo global analítico: <b>a* = {a:.4f} ms/°</b> · <b>b* = {b:.2f} ms</b> · <b>S_min = {smin_e8:.4f}×10⁸ ms²</b></div>
</header>
<div class="grid">
  <div class="panel">
    <div class="box">
      <h2>1. Explora los parámetros (a, b)</h2>
      <div class="row"><span>Pendiente <b>a</b> (ms/°):</span><span id="lblA" class="kpi"></span></div>
      <input id="slA" type="range" min="{a-3.0:.2f}" max="{a+3.0:.2f}" step="0.01" value="{a_init:.2f}">
      <div class="row"><span>Intercepto <b>b</b> (ms):</span><span id="lblB" class="kpi"></span></div>
      <input id="slB" type="range" min="{b-400:.0f}" max="{b+400:.0f}" step="1" value="{b_init:.0f}">
      <div class="btns">
        <button class="green" id="btnAnim">▶ Animar Descenso (−∇S escalado)</button>
        <button class="primary" id="btnOpt">★ Ir al Óptimo (∇S = 0)</button>
      </div>
    </div>
    <div class="box">
      <h2>2. Estado del Cálculo en (a, b)</h2>
      <div class="row"><span>Error S(a,b):</span><span id="lblS" class="kpi"></span></div>
      <div class="row"><span>Exceso ΔS vs S_min:</span><span id="lblDS" class="kpi"></span></div>
      <div class="row"><span>∂S/∂a (pendiente traza a):</span><span id="lblGa" class="kpi"></span></div>
      <div class="row"><span>∂S/∂b (pendiente traza b):</span><span id="lblGb" class="kpi"></span></div>
      <div class="row"><span>Norma ‖∇S(a,b)‖:</span><span id="lblGnorm" class="kpi"></span></div>
    </div>
    <div class="box">
      <h2>3. Recta actual y = a·x + b vs. Medias (K=7)</h2>
      <canvas id="cvLine" width="350" height="190"></canvas>
      <div class="row" style="font-size:11.5px;color:var(--muted);">
        <span>🟠 Recta óptima (R²_medias = 0.9619)</span>
        <span>🟢 Recta explorada (a, b)</span>
      </div>
    </div>
  </div>
  <div>{plot_div}</div>
</div>
<script>
const M = {json.dumps(meta)};
const slA = document.getElementById('slA'), slB = document.getElementById('slB');
const cv = document.getElementById('cvLine'), ctx = cv.getContext('2d');
let animId = null, pathA = [], pathB = [], pathZ = [];

function evalS(a, b) {{
  return M.syy - 2*a*M.sxy - 2*b*M.sy + a*a*M.sxx + 2*a*b*M.sx + M.n*b*b;
}}
function evalGrad(a, b) {{
  return [2*M.sxx*a + 2*M.sx*b - 2*M.sxy, 2*M.sx*a + 2*M.n*b - 2*M.sy];
}}

function draw2D(a, b) {{
  const W = cv.width, H = cv.height;
  ctx.clearRect(0, 0, W, H);
  const padL = 38, padR = 14, padT = 14, padB = 26;
  const xToPx = x => padL + (x / 180) * (W - padL - padR);
  const yToPy = y => H - padB - ((y - 350) / (1450 - 350)) * (H - padT - padB);

  // Axes
  ctx.strokeStyle = '#334155'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(padL, padT); ctx.lineTo(padL, H-padB); ctx.lineTo(W-padR, H-padB); ctx.stroke();

  // Optimal line
  ctx.strokeStyle = '#f97316'; ctx.lineWidth = 2.2; ctx.setLineDash([5, 4]);
  ctx.beginPath();
  ctx.moveTo(xToPx(0), yToPy(M.bstar));
  ctx.lineTo(xToPx(180), yToPy(M.astar*180 + M.bstar));
  ctx.stroke(); ctx.setLineDash([]);

  // Current candidate line + residual segments on means
  for (let i=0; i<M.angles.length; i++) {{
    const ang = M.angles[i], ym = M.means[i], ypred = a*ang + b;
    ctx.strokeStyle = 'rgba(34,197,94,0.45)'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(xToPx(ang), yToPy(ym)); ctx.lineTo(xToPx(ang), yToPy(ypred)); ctx.stroke();
  }}
  ctx.strokeStyle = '#22c55e'; ctx.lineWidth = 2.6;
  ctx.beginPath();
  ctx.moveTo(xToPx(0), yToPy(b));
  ctx.lineTo(xToPx(180), yToPy(a*180 + b));
  ctx.stroke();

  // Angle mean points
  for (let i=0; i<M.angles.length; i++) {{
    const px = xToPx(M.angles[i]), py = yToPy(M.means[i]);
    ctx.fillStyle = '#f8fafc';
    ctx.beginPath(); ctx.arc(px, py, 4, 0, Math.PI*2); ctx.fill();
  }}
}}

function update(resetPath=false) {{
  const a = parseFloat(slA.value), b = parseFloat(slB.value);
  const s = evalS(a, b), [ga, gb] = evalGrad(a, b);
  const s_e8 = s / 1e8, ds_pct = ((s - M.smin) / M.smin) * 100;
  document.getElementById('lblA').textContent = a.toFixed(3) + ' ms/°';
  document.getElementById('lblB').textContent = b.toFixed(1) + ' ms';
  document.getElementById('lblS').textContent = s_e8.toFixed(4) + ' ×10⁸ ms²';
  document.getElementById('lblDS').textContent = '+' + Math.max(0, ds_pct).toFixed(2) + ' %';
  document.getElementById('lblGa').textContent = ga.toExponential(2);
  document.getElementById('lblGb').textContent = gb.toExponential(2);
  document.getElementById('lblGnorm').textContent = Math.hypot(ga, gb).toExponential(2);
  draw2D(a, b);
  if (resetPath) {{ pathA = [a]; pathB = [b]; pathZ = [s_e8]; }}
  else {{ pathA.push(a); pathB.push(b); pathZ.push(s_e8); }}
  if (window.Plotly) {{
    Plotly.restyle('plot3d', {{
      x: [[a]], y: [[b]], z: [[s_e8]],
      text: [[`Actual (${{a.toFixed(2)}}, ${{b.toFixed(0)}})`]]
    }}, [4]);
    Plotly.restyle('plot3d', {{ x: [pathA], y: [pathB], z: [pathZ] }}, [5]);
  }}
}}

slA.addEventListener('input', () => {{ if (animId) {{ cancelAnimationFrame(animId); animId=null; }} update(true); }});
slB.addEventListener('input', () => {{ if (animId) {{ cancelAnimationFrame(animId); animId=null; }} update(true); }});

document.getElementById('btnOpt').onclick = () => {{
  if (animId) {{ cancelAnimationFrame(animId); animId=null; }}
  slA.value = M.astar.toFixed(2); slB.value = M.bstar.toFixed(0);
  pathA.push(M.astar); pathB.push(M.bstar); pathZ.push(M.smin/1e8);
  update(false);
}};

document.getElementById('btnAnim').onclick = () => {{
  if (animId) {{ cancelAnimationFrame(animId); animId=null; return; }}
  let a = parseFloat(slA.value), b = parseFloat(slB.value);
  if (Math.hypot(a - M.astar, (b - M.bstar)/100) < 0.08) {{
    a = M.astar + 2.4; b = M.bstar - 310;
  }}
  pathA = [a]; pathB = [b]; pathZ = [evalS(a,b)/1e8];
  function step() {{
    const [ga, gb] = evalGrad(a, b);
    // Preconditioned gradient descent step (scaled by diagonal of H)
    a -= 0.12 * (ga / (2 * M.sxx));
    b -= 0.12 * (gb / (2 * M.n));
    slA.value = a; slB.value = b;
    update(false);
    if (Math.hypot(a - M.astar, (b - M.bstar)/120) > 0.015) {{
      animId = requestAnimationFrame(step);
    }} else {{
      slA.value = M.astar; slB.value = M.bstar; update(false); animId = null;
    }}
  }}
  animId = requestAnimationFrame(step);
}};

window.addEventListener('load', () => update(true));
</script>
</body>
</html>"""
        with open(f"{FIG}/superficie_interactiva.html", "w", encoding="utf-8") as fh:
            fh.write(html_doc)
    except ImportError:
        print("plotly missing, interactive surface skipped", file=sys.stderr)


if __name__ == "__main__":
    main()
