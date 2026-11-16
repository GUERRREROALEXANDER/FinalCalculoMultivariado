"""NeuroCode: least-squares fit of response time vs rotation angle.

Own algorithm (sums -> a*, b* -> S -> Hessian), checked against numpy/scipy.
Also proves the exact equivalence between fitting all n=595 raw trials and fitting
the K=7 angle means (balanced design: 85 trials per angle), where R^2_means = 0.9685.
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
        "font.size": 13,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.labelsize": 13.5,
        "xtick.labelsize": 12.5,
        "ytick.labelsize": 12.5,
        "legend.fontsize": 11,
        "axes.edgecolor": "#cbd5e1",
        "axes.grid": True,
        "grid.alpha": 0.28,
        "grid.linestyle": "--",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def save_panels(fig, axs, name, dpi=220):
    """Guarda la figura completa (`name.png`) y cada panel por separado (`name_A.png`, `_B`, ...).

    Los paneles sueltos se proyectan mucho mas grandes en las diapositivas.
    """
    fig.savefig(f"{FIG}/{name}.png", dpi=dpi)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    for k, ax in enumerate(np.ravel(axs)):
        bb = ax.get_tightbbox(rend).transformed(fig.dpi_scale_trans.inverted()).padded(0.08)
        fig.savefig(f"{FIG}/{name}_{chr(65 + k)}.png", dpi=dpi, bbox_inches=bb)


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


# ---------------------------------------------------------------------------
# Interactive lab: light UCC theme, one colour ramp shared by every view, offline assets
# ---------------------------------------------------------------------------
LAB_RAMP = [(255, 238, 194), (251, 207, 128), (242, 154, 76), (217, 87, 58), (156, 44, 74), (79, 24, 64)]  # cream -> amber -> red -> burgundy
LAB_T_SCALE = 1.1  # sqrt scale of the level map and the studio view: t = sqrt((S - Smin) / Smin) / 1.1
LAB_INK, LAB_MUTED, LAB_HAIR, LAB_GRID, LAB_PANEL = "#1a1a1a", "#46565e", "#c9dbe2", "#dbe6ea", "#f0f6f7"
# overlay colours (markers, traces): cool, so they stand out on the warm surface ramp
LAB_HOLO, LAB_MIN, LAB_PROBE, LAB_GRAD, LAB_TRACE_A = "#257aa2", "#0072b2", "#009e73", "#6a3d9a", "#7d8b93"  # blue, green, purple, grey: 4 clearly different hues
LAB_FONT = "CMU Serif, Georgia, serif"
FONT_DIR = os.path.join(ROOT, "presentacion", "assets", "fonts")
VENDOR_DIR = os.path.join(ROOT, "codigo", "vendor", "three-0.170.0")
STUDIO_DIR = os.path.join(ROOT, "codigo", "studio")


def _b64(path):
    import base64

    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("ascii")


def _lab_fonts_css():
    """CMU Serif / CMU Typewriter (same as the Beamer deck) embedded so the lab works offline."""
    faces = [("CMU Serif", 400, "cmu-serif-500-roman.woff2"), ("CMU Serif", 700, "cmu-serif-700-roman.woff2"),
             ("CMU Typewriter", 400, "cmu-typewriter-text-500-roman.woff2")]
    return "\n".join(
        f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:normal;font-display:swap;'
        f'src:url(data:font/woff2;base64,{_b64(os.path.join(FONT_DIR, f))}) format("woff2")}}'
        for fam, w, f in faces)


def _lab_studio_html():
    """Import map (data: URLs, no network) + the module that mounts the three.js studio view."""
    import json

    def js(path):
        return "data:text/javascript;base64," + _b64(path)

    imports = {
        "three": js(os.path.join(VENDOR_DIR, "three.module.min.js")),
        "three/addons/OrbitControls.js": js(os.path.join(VENDOR_DIR, "OrbitControls.js")),
        "three/addons/RoomEnvironment.js": js(os.path.join(VENDOR_DIR, "RoomEnvironment.js")),
        "three/addons/CSS2DRenderer.js": js(os.path.join(VENDOR_DIR, "CSS2DRenderer.js")),
        "studio/core": js(os.path.join(STUDIO_DIR, "studio_core.js")),
        "studio/view": js(os.path.join(STUDIO_DIR, "studio_view.js")),
    }
    boot = """
(async () => {
  try {
    const gl = document.createElement('canvas').getContext('webgl2');
    if (!gl) throw new Error('WebGL2 unavailable');
    const { mountStudio } = await import('studio/view');
    const v = mountStudio(document.getElementById('viewStudio'), M);
    NC.views.push(v);
    if (NC.state) v.update(NC.state);
    NC.studioReady = true;
  } catch (e) {
    NC.studioFailed = true;
    if (NC.showData) NC.showData();
    console.warn('studio view disabled:', e && e.message);
  }
})();
"""
    return ('<script type="importmap">' + json.dumps({"imports": imports}) + '</script>\n'
            '<script type="module">' + boot + '</script>')


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

    # --- Mathematical equivalence on K=7 angle means (balanced design m=85 per angle) ---
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
    # 01_dispersion.png: Left = raw 595 trials + angle means; Right = K=7 means
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
        title=f"A. Los {len(x)} ensayos ({len(parts)} personas)",
        xticks=ang_vals,
    )
    axs[0].set_ylim(0, 7900)
    axs[0].legend(ncol=6, fontsize=9.5, loc="upper left", framealpha=0.92, columnspacing=0.8, handletextpad=0.2)

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
        axs[1].annotate(f"{mv:.0f}", (xv, mv), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=11.5, color=INK, fontweight="bold")
    axs[1].set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Tiempo promedio de respuesta (ms)",
        title="B. Promedios por ángulo (K = 7)",
        xticks=ang_vals,
        ylim=(540, 1520),
    )
    axs[1].legend(fontsize=10.5, loc="upper left", framealpha=0.94)
    fig.tight_layout()
    save_panels(fig, axs, "01_dispersion")
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
            fontsize=10.8,
            bbox=dict(boxstyle="round,pad=0.2", fc="#fff7ed", ec=ACCENT, lw=0.8),
        )
    axs[0].set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Tiempo de respuesta y (ms)",
        title="A. Ajuste global y atípicos",
        xticks=ang_vals,
    )
    axs[0].legend(fontsize=10.5, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, framealpha=0.95)

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
        title="B. Recta óptima vs. otras rectas",
        xticks=ang_vals,
        ylim=(320, 1480),
    )
    axs[1].legend(fontsize=10.5, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=1, framealpha=0.95)
    fig.tight_layout()
    save_panels(fig, axs, "02_rectas")
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
    ax.legend(loc="upper left", fontsize=11.5)
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
        fontsize=11.5,
        fontweight="bold",
        color=INK,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=ACCENT, lw=1.0),
    )
    axs[0].set(
        xlabel="Pendiente a (ms/°)",
        ylabel="S(a, b₀) [$10^8$ ms²]",
        title="A. Traza óptima S(a, b*) y secciones b = b₀",
    )
    axs[0].legend(fontsize=10.8, loc="upper right")

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
        fontsize=11.5,
        fontweight="bold",
        color=INK,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=ACCENT, lw=1.0),
    )
    axs[1].set(
        xlabel="Intercepto b (ms)",
        ylabel="S(a₀, b) [$10^8$ ms²]",
        title="B. Traza óptima S(a*, b) y secciones a = a₀",
    )
    axs[1].legend(fontsize=10.8, loc="upper right")
    fig.tight_layout()
    save_panels(fig, axs, "04_trazas")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 05_curvas_nivel.png: Filled contours + -grad S field + candidate points
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    cf = ax.contourf(A, B, Z_e8, levels=24, cmap="viridis", alpha=0.85)
    cs = ax.contour(A, B, Z_e8, levels=14, colors="white", linewidths=0.75, alpha=0.85)
    ax.clabel(cs, fontsize=10.2, fmt="%.2f", colors="white")
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
    ax.legend(fontsize=9.5, loc="lower left", framealpha=0.95)
    ax.annotate(
        f"MÍNIMO GLOBAL\n$\\nabla S=\\mathbf{{0}}$ en ({a:.2f}, {b:.1f})",
        (a, b), xytext=(a - 2.9, b + 330), fontsize=13, fontweight="bold", color=INK,
        arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2.2),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=ACCENT, lw=1.5),
    )
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
        xytext=(186, r["e"][i] - 1100), ha="right",
        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.2),
        fontsize=11.2,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.2", fc="#fff7ed", ec=ACCENT, lw=0.8),
    )
    axs[0].set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Residuo eᵢ (ms)",
        title="A. Residuos vs. ángulo (centrados en 0)",
        xticks=ang_vals,
    )
    axs[0].set_ylim(-1300, 5600)
    axs[0].legend(fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, framealpha=0.95)

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
    axs[1].legend(fontsize=11.0, loc="upper right")
    fig.tight_layout(pad=1.4, w_pad=2.2)
    save_panels(fig, axs, "06_residuos")
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
    ax_bc.legend(fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=1)

    # Top-right: Option A (Monte Carlo sensitivity of a* and b*)
    ax_sens = axs[0, 1]
    ax_sens.scatter(a_pert, b_pert, s=14, alpha=0.45, color=BLUE, label="500 perturbaciones $\\Delta y_i \\sim \\mathcal{N}(0, 25\\,\\mathrm{ms})$")
    ax_sens.plot(a, b, "*", color=ACCENT, ms=15, markeredgecolor="white", label=f"Óptimo original ({a:.3f}, {b:.1f})")
    ax_sens.set(
        xlabel="Pendiente perturbada a* (ms/°)",
        ylabel="Intercepto perturbado b* (ms)",
        title=f"B. Opción A (Sensibilidad): $\\sigma_a={a_pert.std():.3f}$ ms/° ({100*a_pert.std()/a:.1f}%)",
    )
    ax_sens.legend(fontsize=11.0, loc="upper right")

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
    ax_n.set_ylim(-0.3, 4.6)
    ax_n.legend(fontsize=10.5, loc="upper left")

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
        fontsize=11.0,
        fontweight="bold",
    )
    ax_ind.annotate(
        "P07 (más rápido: b=384 ms)",
        (120, p_df.loc[p_df["p"] == "P07", "a"].values[0] * 120 + p_df.loc[p_df["p"] == "P07", "b"].values[0]),
        xytext=(85, 360),
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.0),
        fontsize=11.0,
        fontweight="bold",
    )
    ax_ind.set(
        xlabel="Ángulo de rotación x (°)",
        ylabel="Recta ajustada por participante y (ms)",
        title=f"D. Heterogeneidad individual ({len(parts)} rectas)",
        xticks=ang_vals,
    )
    ax_ind.legend(fontsize=11.0, loc="upper left")

    fig.tight_layout(pad=1.4, w_pad=2.2, h_pad=2.0)
    save_panels(fig, axs, "07_opciones_BC")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 08_puente.png: bridge between the point (a,b) on the S map and the line y = ax + b
    # -------------------------------------------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(13.4, 5.6))
    axs[0].contourf(A, B, Z_e8, levels=24, cmap="viridis", alpha=0.85)
    axs[0].contour(A, B, Z_e8, levels=10, colors="white", linewidths=0.7, alpha=0.8)
    pts = [(a, b, ACCENT, "Óptima", "*")] + [(ac, bc, col, cname, "o") for ac, bc, col, cname in candidates]
    for ac, bc, col, cname, mk in pts:
        axs[0].plot(ac, bc, mk, color=col, ms=19 if mk == "*" else 12, markeredgecolor="white", markeredgewidth=1.5, zorder=9)
        axs[0].annotate(f"{cname}\nS={S(ac, bc, x, y) / 1e8:.2f}$\\times10^8$", (ac, bc), xytext=(-10, 10) if ac > 5 else (9, 9), textcoords="offset points",
                        ha="right" if ac > 5 else "left", fontsize=11.5, fontweight="bold", color="white", zorder=10)
    axs[0].set(xlabel="Pendiente a (ms/°)", ylabel="Intercepto b (ms)", title="A. Un punto (a, b) de la superficie…")
    axs[1].errorbar(ang_vals, mean_vals, yerr=sem_vals, fmt="o", color=INK, ms=8, capsize=4, zorder=6, label="Medias por ángulo")
    for ac, bc, col, cname, mk in pts:
        axs[1].plot(xs, ac * xs + bc, color=col, lw=3.4 if mk == "*" else 2.2, ls="-" if mk == "*" else "--",
                    label=f"{cname}: $y={ac:.2f}x+{bc:.0f}$")
    axs[1].set(xlabel="Ángulo de rotación x (°)", ylabel="Tiempo y (ms)", title="B. …es UNA recta y = ax + b", xticks=ang_vals, ylim=(320, 1480))
    axs[1].legend(fontsize=11, loc="upper left")
    fig.tight_layout()
    save_panels(fig, axs, "08_puente")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 09_doble_r2.png: why R2_raw = 0.094 while R2_means = 0.9685 with the SAME line
    # -------------------------------------------------------------------------
    ss_reg = r["r2"] * sst
    ss_lack = m_per_angle * rm["smin"]
    parts_ss = [("Explicado por\nla recta", ss_reg, ACCENT), ("Falta de ajuste\nde la recta", ss_lack, "#f59e0b"), ("Variación DENTRO\ndel mismo ángulo", ss_within, "#94a3b8")]
    fig, axs = plt.subplots(1, 2, figsize=(13.4, 5.4), gridspec_kw={"width_ratios": [1.25, 1]})
    cum = 0.0
    txt_pos = {0: (1.0, 0.78, "left"), 1: (30.0, 0.78, "left"), 2: (55, 0.0, "center")}
    for k, (lab, v, col) in enumerate(parts_ss):
        pct = 100 * v / sst
        axs[0].barh([0], [pct], left=[cum], color=col, edgecolor="white", height=0.5)
        tx, ty, ha = txt_pos[k]
        label = {0: f"Explicado por\nla recta: {pct:.1f} %", 1: f"Falta de ajuste\nde la recta: {pct:.1f} %", 2: f"Dentro del mismo ángulo: {pct:.1f} %"}[k]
        if k == 2:
            axs[0].text(tx, ty, label, ha=ha, va="center", fontsize=16, fontweight="bold", color="white")
        else:
            axs[0].annotate(label, (cum + pct / 2, 0.25), xytext=(tx, ty), ha=ha, va="center", fontsize=15, fontweight="bold", color=INK,
                            arrowprops=dict(arrowstyle="-|>", color=col, lw=2.2), bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=col, lw=1.6))
        cum += pct
    axs[0].set(xlim=(0, 100), ylim=(-0.4, 1.2), yticks=[], xlabel="% de la variación total SST de los 595 ensayos",
               title=f"A. $R^2_{{\\mathrm{{raw}}}}={r['r2']:.4f}$: casi todo el error es intra-ángulo")
    axs[0].grid(False)
    axs[1].errorbar(ang_vals, mean_vals, yerr=sem_vals, fmt="o", color=INK, ms=9, capsize=4, label="Medias (ruido promediado)", zorder=6)
    axs[1].plot(xs, a * xs + b, color=ACCENT, lw=3.2, label=f"MISMA recta: $y={a:.2f}x+{b:.0f}$")
    axs[1].set(xlabel="Ángulo de rotación x (°)", ylabel="Tiempo promedio (ms)", xticks=ang_vals, ylim=(540, 1280),
               title=f"B. $R^2_{{\\mathrm{{medias}}}}={rm['r2']:.4f}$ con los mismos a*, b*")
    axs[1].legend(fontsize=11.5, loc="upper left")
    fig.tight_layout()
    save_panels(fig, axs, "09_doble_r2")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 10_pendientes.png: the 17 individual slopes vs the global slope
    # -------------------------------------------------------------------------
    ps = p_df.sort_values("a").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(11.5, 6.0))
    cols = [ACCENT if v > 0 else "#64748b" for v in ps["a"]]
    ax.barh(ps["p"], ps["a"], color=cols, edgecolor="white")
    ax.axvline(a, color=INK, lw=3, ls="--")
    ax.text(a + 0.08, 0.2, f"Global a* = {a:.2f}", fontsize=14, fontweight="bold", color=INK, va="bottom")
    ax.axvline(0, color="black", lw=1.2)
    for yy, (pid, v) in enumerate(zip(ps["p"], ps["a"])):
        ax.text(v + (0.1 if v >= 0 else -0.1), yy, f"{v:.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=12, bbox=dict(fc="white", ec="none", pad=1.0, alpha=0.85))
    ax.set(xlabel="Pendiente individual a_j (ms/°)", ylabel="Participante",
           title=f"{n_pos} de {len(p_df)} personas tienen pendiente positiva (test de signos p = {sign_p:.1e})",
           xlim=(min(-1.2, ps['a'].min() - 0.6), ps['a'].max() + 1.2))
    ax.grid(axis="y", alpha=0)
    fig.tight_layout()
    fig.savefig(f"{FIG}/10_pendientes.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 11_elipses_centradas.png: original vs centered x~ = x - mean(x)  (tilted -> aligned)
    # -------------------------------------------------------------------------
    xc_all = x - x.mean()
    cstar = y.mean()
    C_grid = np.linspace(cstar - 420, cstar + 420, 140)
    A2, C2 = np.meshgrid(a_grid, C_grid)
    Zc = ((y[None, None, :] - A2[..., None] * xc_all - C2[..., None]) ** 2).sum(-1) / 1e8
    fig, axs = plt.subplots(1, 2, figsize=(13.4, 5.6))
    for ax_, XX, YY, ZZ, c0, ttl, lab in [
        (axs[0], A, B, Z_e8, b, f"A. Original: x en grados\n$S_{{ab}}=2\\Sigma x={2 * x.sum():,.0f}\\neq 0$ → INCLINADAS", "Intercepto b (ms)"),
        (axs[1], A2, C2, Zc, cstar, "B. Centrado: $\\tilde{x}=x-90^\\circ$\n$S_{a\\tilde{b}}=2\\Sigma\\tilde{x}=0$ → ENDEREZADAS", "Intercepto centrado $\\tilde{b}$ (ms)"),
    ]:
        ax_.contourf(XX, YY, ZZ, levels=24, cmap="viridis", alpha=0.85)
        ax_.contour(XX, YY, ZZ, levels=10, colors="white", linewidths=0.8, alpha=0.9)
        ax_.plot(a, c0, "*", color=ACCENT, ms=20, markeredgecolor="white", markeredgewidth=1.4, zorder=9)
        ax_.set(xlabel="Pendiente a (ms/°)", ylabel=lab, title=ttl)
    axs[0].annotate(f"$b^*={b:.0f}$", (a, b), xytext=(a + 0.6, b + 250), color="white", fontsize=13, fontweight="bold", arrowprops=dict(arrowstyle="->", color="white", lw=1.6))
    axs[1].annotate(f"$\\tilde{{b}}^*=\\bar{{y}}={cstar:.0f}$", (a, cstar), xytext=(a + 0.6, cstar + 250), color="white", fontsize=13, fontweight="bold", arrowprops=dict(arrowstyle="->", color="white", lw=1.6))
    fig.tight_layout()
    save_panels(fig, axs, "11_elipses_centradas")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # 12_cerebro_vs_cpu.png: brain (linear in theta) vs CPU (rotation matrix, O(1)); schematic
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.plot(xs, a * xs + b, color=ACCENT, lw=4, label=f"Cerebro: $t={b:.0f}+{a:.2f}\\,\\theta$ ms (medido)")
    ax.errorbar(ang_vals, mean_vals, yerr=sem_vals, fmt="o", color=INK, ms=8, capsize=4, zorder=6, label="Medias observadas")
    ax.axhline(b, color=BLUE, lw=4, ls="--", label="CPU: $R(\\theta)\\mathbf{v}$ en tiempo constante, $O(1)$ (esquema)")
    ax.fill_between(xs, b, a * xs + b, color=ACCENT, alpha=0.12)
    ax.annotate(f"Costo por rotar: {a:.2f} ms por cada grado\n(≈ {1000 / a:.0f} °/s)", (150, a * 150 + b), xytext=(52, 1130),
                fontsize=14, fontweight="bold", color=INK, arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2.2),
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=ACCENT, lw=1.6))
    ax.set(xlabel="Ángulo de rotación θ (°)", ylabel="Tiempo (ms)", xticks=ang_vals, ylim=(450, 1300),
           title="Cerebro: analógico, crece con θ · CPU: matriz 2D, no depende de θ")
    ax.legend(fontsize=12.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(f"{FIG}/12_cerebro_vs_cpu.png", dpi=220)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Interactive lab (light UCC theme): Plotly "Datos" view + three.js "Estudio" view
    # Trace order is a contract with the template JS: 0 surface, 1 b=b*, 2 a=a*, 3 minimum,
    # 4 probe, 5 trail, 6 -grad S.
    # -------------------------------------------------------------------------
    try:
        import json
        import plotly.graph_objects as go

        n_stops = len(LAB_RAMP)
        colorscale = [[i / (n_stops - 1), f"rgb({c[0]},{c[1]},{c[2]})"] for i, c in enumerate(LAB_RAMP)]
        t_surf = np.sqrt(np.maximum(Z - r["smin"], 0.0) / r["smin"]) / LAB_T_SCALE   # same colour as the map
        cb_t = [0.0, 0.25, 0.5, 0.75, 1.0]
        cb_txt = [f"{smin_e8 * (1 + (LAB_T_SCALE * tv) ** 2):.2f}" for tv in cb_t]

        pf = go.Figure()
        pf.add_trace(
            go.Surface(
                x=a_grid,
                y=b_grid,
                z=Z_e8,
                surfacecolor=t_surf,
                cmin=0.0,
                cmax=1.0,
                colorscale=colorscale,
                customdata=Z_e8,
                hovertemplate="a = %{x:.2f} ms/°<br>b = %{y:.0f} ms<br>S = %{customdata:.3f} ×10⁸<extra></extra>",
                showlegend=False,
                lighting=dict(ambient=0.55, diffuse=0.75, specular=0.08, roughness=0.85, fresnel=0.1),
                lightposition=dict(x=100, y=200, z=1000),
                colorbar=dict(
                    tickvals=cb_t, ticktext=cb_txt, tickfont=dict(size=13, color=LAB_MUTED),
                    thickness=12, len=0.55, x=0.985, outlinewidth=0, ticks="",
                ),
                contours=dict(
                    z=dict(show=True, usecolormap=False, color="rgba(70,25,40,0.45)", width=1,
                           start=float(np.ceil(smin_e8 * 5) / 5), end=float(Z_e8.max()), size=0.2, project_z=True,
                           highlight=True, highlightcolor=LAB_HOLO, highlightwidth=3)
                ),
            )
        )
        pf.add_trace(  # trace b = b*
            go.Scatter3d(
                x=a_grid, y=np.full_like(a_grid, b), z=[S(av, b, x, y) / 1e8 for av in a_grid],
                mode="lines", line=dict(color=LAB_MIN, width=5), name=f"Traza b = b* ({b:.1f} ms)",
            )
        )
        pf.add_trace(  # trace a = a*
            go.Scatter3d(
                x=np.full_like(b_grid, a), y=b_grid, z=[S(a, bv, x, y) / 1e8 for bv in b_grid],
                mode="lines", line=dict(color=LAB_TRACE_A, width=5), name=f"Traza a = a* ({a:.2f} ms/°)",
            )
        )
        pf.add_trace(  # global minimum
            go.Scatter3d(
                x=[a], y=[b], z=[smin_e8], mode="markers+text",
                marker=dict(size=7, color=LAB_MIN, symbol="diamond", line=dict(color="white", width=2)),
                text=[f"Mínimo ({a:.2f}, {b:.1f})"], textposition="top center",
                textfont=dict(size=13, color=LAB_INK, family=LAB_FONT), name="Mínimo global (a*, b*)",
            )
        )
        a_init, b_init = round(a + 2.2, 2), round(b - 260.0, 1)
        s_init_e8 = S(a_init, b_init, x, y) / 1e8
        pf.add_trace(  # live probe
            go.Scatter3d(
                x=[a_init], y=[b_init], z=[s_init_e8], mode="markers+text",
                marker=dict(size=8, color=LAB_PROBE, symbol="circle", line=dict(color="white", width=2)),
                text=[f"({a_init:.2f}, {b_init:.0f})"], textposition="top center",
                textfont=dict(size=13, color=LAB_INK, family=LAB_FONT), name="Punto explorado (a, b)",
            )
        )
        pf.add_trace(  # trail
            go.Scatter3d(
                x=[a_init], y=[b_init], z=[s_init_e8], mode="lines",
                line=dict(color=LAB_PROBE, width=5), name="Trayectoria −∇S",
            )
        )
        pf.add_trace(  # -grad S
            go.Scatter3d(
                x=[a_init, a_init], y=[b_init, b_init], z=[s_init_e8, s_init_e8], mode="lines",
                line=dict(color=LAB_GRAD, width=9), name="−∇S (dirección de máximo descenso)",
            )
        )

        def axis(title):
            return dict(
                title=dict(text=title, font=dict(size=16, color=LAB_INK, family=LAB_FONT)),
                tickfont=dict(size=14, color=LAB_MUTED, family=LAB_FONT),
                gridcolor=LAB_GRID, linecolor=LAB_HAIR, zerolinecolor=LAB_HAIR,
                showbackground=True, backgroundcolor=LAB_PANEL, showspikes=False,
            )

        pf.update_layout(
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(family=LAB_FONT, size=14, color=LAB_INK),
            scene=dict(
                bgcolor="#ffffff",
                aspectmode="manual",
                aspectratio=dict(x=1.1, y=1.1, z=0.65),
                camera=dict(eye=dict(x=1.55, y=-1.35, z=0.95)),
                xaxis=axis("Pendiente a (ms/°)"),
                yaxis=axis("Intercepto b (ms)"),
                zaxis=axis("S(a,b) [10⁸ ms²]"),
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            hoverlabel=dict(bgcolor="#ffffff", bordercolor=LAB_HAIR, font=dict(family=LAB_FONT, size=13, color=LAB_INK)),
            legend=dict(orientation="h", x=0.01, y=0.01, xanchor="left", yanchor="bottom",
                        bgcolor="rgba(255,255,255,0.9)", bordercolor=LAB_HAIR, borderwidth=1,
                        font=dict(size=13, family=LAB_FONT)),
        )
        plot_div = pf.to_html(full_html=False, include_plotlyjs=True, div_id="plot3d",
                              default_height="100%", default_width="100%",
                              config=dict(displaylogo=False, responsive=True))
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
            ramp=[list(c) for c in LAB_RAMP],
        )
        meta.update(ssw=float(ss_within), m=int(m_per_angle), xbar=float(x.mean()), ybar=float(y.mean()))
        with open(os.path.join(ROOT, "codigo", "simulador_template.html"), encoding="utf-8") as fh:
            template = fh.read()
        html_doc = (
            template.replace("__META__", json.dumps(meta))
            .replace("/*__FONTS__*/", _lab_fonts_css())
            .replace("<!--__STUDIO__-->", _lab_studio_html())
            .replace("__PLOT3D__", plot_div)   # last: the Plotly bundle is huge
        )
        with open(f"{FIG}/superficie_interactiva.html", "w", encoding="utf-8") as fh:
            fh.write(html_doc)
    except ImportError:
        print("plotly missing, interactive surface skipped", file=sys.stderr)


if __name__ == "__main__":
    main()
