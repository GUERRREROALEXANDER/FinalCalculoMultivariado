"""NeuroCode: least-squares fit of response time vs rotation angle.

Own algorithm (sums -> a*, b* -> S -> Hessian), checked against numpy/scipy.
Reads every csvs/*.csv, so adding P04-P06 only needs a re-run.
Figure labels are in Spanish because the professor reads them.
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
    return dict(n=n, sx=sx, sy=sy, sxx=sxx, sxy=sxy, a=a, b=b)


def S(a, b, x, y):
    return ((y - a * x - b) ** 2).sum()


def hessian(x):
    n = len(x)
    return np.array([[2 * (x * x).sum(), 2 * x.sum()], [2 * x.sum(), 2 * n]])


def metrics(x, y, a, b):
    e = y - (a * x + b)
    sse = (e**2).sum()
    sst = ((y - y.mean()) ** 2).sum()
    return e, np.sqrt(sse / len(x)), 1 - sse / sst


def report(df, tag):
    x, y = df["angulo_grados"].to_numpy(float), df["tiempo_ms"].to_numpy(float)
    f = fit(x, y)
    a, b = f["a"], f["b"]
    smin = S(a, b, x, y)
    H = hessian(x)
    D = np.linalg.det(H)
    eig = np.linalg.eigvalsh(H)
    e, rmse, r2 = metrics(x, y, a, b)
    pa, pb = np.polyfit(x, y, 1)
    lr = stats.linregress(x, y)
    print(f"\n=== {tag} (n={f['n']}) ===")
    print(f"sums: n={f['n']} Sx={f['sx']:.1f} Sy={f['sy']:.1f} Sxx={f['sxx']:.1f} Sxy={f['sxy']:.1f}")
    print(f"a*={a:.6f} ms/deg  b*={b:.4f} ms  S_min={smin:.2f}")
    print(f"speed 1000/a* = {1000 / a:.1f} deg/s" if a > 0 else "a* <= 0 (no rotation effect)")
    print(f"H={H.tolist()}  det={D:.1f}  S_aa={H[0, 0]:.1f}  eig={eig}")
    print(f"polyfit a={pa:.6f} b={pb:.4f} | linregress a={lr.slope:.6f} b={lr.intercept:.4f} p={lr.pvalue:.4f}")
    print(f"max diff a={abs(a - pa):.2e} b={abs(b - pb):.2e} S={abs(smin - S(pa, pb, x, y)):.2e}")
    print(f"RMSE={rmse:.1f} ms  R2={r2:.4f}  mean(e)={e.mean():.2e}")
    return dict(x=x, y=y, a=a, b=b, smin=smin, H=H, e=e, rmse=rmse, r2=r2)


def main():
    df = load()
    print(df.groupby("participante").size().to_string())
    print(df.groupby("angulo_grados")["tiempo_ms"].agg(["count", "mean", "std", "median"]).round(1).to_string())
    r = report(df, "ALL DATA")
    x, y, a, b = r["x"], r["y"], r["a"], r["b"]

    for p, g in df.groupby("participante"):
        report(g, f"participant {p}")

    # --- option B: influence of the biggest outlier ---
    i = int(np.argmax(np.abs(r["e"])))
    print(f"\nLargest residual: row {i}, x={x[i]:.0f}, y={y[i]:.1f}, e={r['e'][i]:.1f}")
    keep = np.arange(len(x)) != i
    rb = report(df[keep], "OPTION B: without the largest-residual point")

    # --- option C: quadratic ---
    c2, c1, c0 = np.polyfit(x, y, 2)
    eq = y - (c2 * x**2 + c1 * x + c0)
    r2q = 1 - (eq**2).sum() / ((y - y.mean()) ** 2).sum()
    print(f"\n=== OPTION C quadratic === y={c2:.3e}x^2+{c1:.4f}x+{c0:.2f}  RMSE={np.sqrt((eq**2).mean()):.1f}  R2={r2q:.4f}")

    # --- figures ---
    rng = np.random.default_rng(0)
    xs = np.linspace(0, 180, 100)
    cols = {"P01": "#1f77b4", "P02": "#d62728", "P03": "#2ca02c"}

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for p, g in df.groupby("participante"):
        ax.scatter(g["angulo_grados"] + rng.uniform(-3, 3, len(g)), g["tiempo_ms"], s=22, alpha=0.7, label=p, color=cols.get(p))
    ax.set(xlabel="Ángulo de rotación x (°)", ylabel="Tiempo de respuesta y (ms)", title="Diagrama de dispersión")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{FIG}/01_dispersion.png", dpi=200)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(x, y, s=18, color="gray", alpha=0.6, label="datos")
    ax.plot(xs, a * xs + b, "k", lw=2.5, label=f"óptima: y={a:.2f}x+{b:.0f}")
    for da, db, c in [(1.5, -100, "tab:red"), (-1, 150, "tab:blue"), (3, -300, "tab:green")]:
        ax.plot(xs, (a + da) * xs + (b + db), "--", color=c, lw=1.2, label=f"a={a + da:.2f}, b={b + db:.0f}  S={S(a + da, b + db, x, y):.2e}")
    ax.set(xlabel="x (°)", ylabel="y (ms)", title="Recta óptima vs otras rectas")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{FIG}/02_rectas.png", dpi=200)

    A, B = np.meshgrid(np.linspace(a - 3, a + 3, 120), np.linspace(b - 400, b + 400, 120))
    Z = ((y[None, None, :] - A[..., None] * x - B[..., None]) ** 2).sum(-1)

    fig = plt.figure(figsize=(7, 5.5))
    ax = fig.add_subplot(projection="3d")
    ax.plot_surface(A, B, Z, cmap="viridis", alpha=0.85, linewidth=0)
    ax.scatter([a], [b], [r["smin"]], color="red", s=60)
    ax.set(xlabel="a (ms/°)", ylabel="b (ms)", zlabel="S(a,b)", title="Superficie de error S(a,b)")
    fig.tight_layout()
    fig.savefig(f"{FIG}/03_superficie.png", dpi=200)

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].plot(A[0], [S(av, b, x, y) for av in A[0]])
    axs[0].axvline(a, color="r", ls=":")
    axs[0].set(xlabel="a", ylabel="S(a, b*)", title="Traza b = b*")
    axs[1].plot(B[:, 0], [S(a, bv, x, y) for bv in B[:, 0]])
    axs[1].axvline(b, color="r", ls=":")
    axs[1].set(xlabel="b", ylabel="S(a*, b)", title="Traza a = a*")
    fig.tight_layout()
    fig.savefig(f"{FIG}/04_trazas.png", dpi=200)

    fig, ax = plt.subplots(figsize=(6.5, 5))
    cs = ax.contour(A, B, Z, levels=20, cmap="viridis")
    ax.clabel(cs, fontsize=6, fmt="%.1e")
    ax.plot(a, b, "r*", ms=14, label="(a*, b*)")
    ax.set(xlabel="a (ms/°)", ylabel="b (ms)", title="Curvas de nivel de S(a,b)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{FIG}/05_curvas_nivel.png", dpi=200)

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].scatter(x, r["e"], s=18)
    axs[0].axhline(0, color="k")
    axs[0].set(xlabel="x (°)", ylabel="residuo e (ms)", title="Residuos vs ángulo")
    axs[1].hist(r["e"], bins=15, edgecolor="k")
    axs[1].set(xlabel="e (ms)", ylabel="frecuencia", title="Histograma de residuos")
    fig.tight_layout()
    fig.savefig(f"{FIG}/06_residuos.png", dpi=200)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(x, y, s=18, color="gray", alpha=0.6, label="datos")
    ax.plot(xs, a * xs + b, "k", lw=2, label="lineal (todos)")
    ax.plot(xs, rb["a"] * xs + rb["b"], "--", color="tab:red", label="lineal (sin atípico)")
    ax.plot(xs, c2 * xs**2 + c1 * xs + c0, color="tab:blue", label="cuadrático")
    ax.set(xlabel="x (°)", ylabel="y (ms)", title="Análisis adicional: opciones B y C")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{FIG}/07_opciones_BC.png", dpi=200)

    try:
        import plotly.graph_objects as go

        pf = go.Figure(go.Surface(x=A[0], y=B[:, 0], z=Z, colorscale="Viridis"))
        pf.add_trace(go.Scatter3d(x=[a], y=[b], z=[r["smin"]], mode="markers", marker=dict(size=6, color="red"), name="mínimo"))
        pf.update_layout(title="S(a,b) interactiva", scene=dict(xaxis_title="a (ms/°)", yaxis_title="b (ms)", zaxis_title="S"))
        pf.write_html(f"{FIG}/superficie_interactiva.html")
    except ImportError:
        print("plotly missing, interactive surface skipped", file=sys.stderr)


if __name__ == "__main__":
    main()
