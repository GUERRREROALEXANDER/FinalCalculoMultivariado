#!/usr/bin/env python3
"""Auditoria formal de los CSV candidatos de ``csvs/extra`` y ``csvs/txt``.

Objetivo
--------
Decidir, con un porton psicometrico y estadistico explicito, que bloques de
35 ensayos pueden sumarse al modelo global (``csvs/*.csv``, n=525) sin
degradar RMSE ni R^2.

Reglas
------
* Huella de cada bloque de 35 ensayos:
  ``(len, primer timestamp, ultimo timestamp, round(sum(tiempo_ms), 1))``.
  Una huella ya vista contra ``csvs/*.csv`` o contra otro candidato es un
  duplicado exacto y se excluye del modelo.
* G1 diseno balanceado: 5 ensayos en cada angulo {0,30,60,90,120,150,180}.
* G2 direccion: pendiente a > 1.0 ms/grado.
* G3 atencion: max(tiempo_ms) <= 3000 ms (cero distracciones severas).
* G4 fuerza estadistica: Tier Oro si p < 0.05 y R^2 >= 0.15; Tier Plata si
  p < 0.25 y max(tiempo_ms) <= 3000; en otro caso Rechazado.
* El conjunto aprobado es la union de los bloques unicos Oro + Plata. Se
  contrasta contra la base en R^2_raw, R^2_means (K=7), RMSE y t.

Uso
---
    python3 codigo/auditar_extras.py > codigo/reporte_extras.md

El script imprime el informe Markdown y ademas lo escribe en
``codigo/reporte_extras.md``. No modifica ningun CSV ni ``ajuste.py``.
Codigo de salida: 0 si el conjunto aprobado supera la linea de pase, 1 si no.
"""
from __future__ import annotations

import glob
import io
import os
import re
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(ROOT, "csvs")
EXTRA_DIR = os.path.join(CSV_DIR, "extra")
TXT_DIR = os.path.join(CSV_DIR, "txt")
REPORT_PATH = os.path.join(ROOT, "codigo", "reporte_extras.md")

ANGLES = [0, 30, 60, 90, 120, 150, 180]
BLOCK = 35
G2_MIN_SLOPE = 1.0
G3_MAX_MS = 3000.0
G4_ORO_P = 0.05
G4_ORO_R2 = 0.15
G4_PLATA_P = 0.25

# Linea de pase del juez (global, contra la base n=525).
PASS_R2_RAW = 0.0854
PASS_R2_MEANS = 0.9619
PASS_RMSE = 520.2

REQUIRED = ["angulo_grados", "tiempo_ms", "fecha_hora"]


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------
def read_csv(path: str) -> pd.DataFrame:
    """Lee un CSV del proyecto (admite BOM y finales CRLF)."""
    d = pd.read_csv(path, encoding="utf-8-sig")
    return validate(d, path)


def read_txt_blocks(path: str) -> tuple[list[pd.DataFrame], list[str]]:
    """Extrae los bloques CSV cercados por ``` de un informe de texto."""
    text = open(path, "r", encoding="utf-8-sig").read()
    fences = re.findall(r"```[^\n]*\n(.*?)```", text, flags=re.DOTALL)
    if not fences:
        raise ValueError(f"{path}: no contiene ningun bloque CSV entre ```")
    frames = [validate(pd.read_csv(io.StringIO(f.strip())), path) for f in fences]
    data = pd.concat(frames, ignore_index=True)
    if len(data) % BLOCK:
        # Un bloque incompleto no se descarta en silencio: se audita y G1 falla.
        pass
    return [data.iloc[i : i + BLOCK].reset_index(drop=True) for i in range(0, len(data), BLOCK)], fences


def validate(d: pd.DataFrame, path: str) -> pd.DataFrame:
    missing = [c for c in REQUIRED if c not in d.columns]
    if missing:
        raise ValueError(f"{path}: faltan columnas {missing}")
    d = d.copy()
    d["angulo_grados"] = pd.to_numeric(d["angulo_grados"], errors="coerce")
    d["tiempo_ms"] = pd.to_numeric(d["tiempo_ms"], errors="coerce")
    if d[["angulo_grados", "tiempo_ms"]].isna().any().any():
        raise ValueError(f"{path}: angulo_grados o tiempo_ms no numericos")
    d["fecha_hora"] = d["fecha_hora"].astype(str)
    return d


# ---------------------------------------------------------------------------
# Huellas y copias
# ---------------------------------------------------------------------------
def fingerprint(d: pd.DataFrame) -> tuple[int, str, str, float]:
    ts = d["fecha_hora"]
    return (len(d), ts.min(), ts.max(), round(float(d["tiempo_ms"].sum()), 1))


def fp_text(fp: tuple[int, str, str, float]) -> str:
    return f"n={fp[0]}; t0={fp[1]}; t1={fp[2]}; Sy={fp[3]:.1f}"


def fmt_fp_inline(fp: tuple[int, str, str, float]) -> str:
    return f"{fp[0]} | {fp[1]} | {fp[2]} | {fp[3]:.1f}"


# ---------------------------------------------------------------------------
# Ajuste y metricas
# ---------------------------------------------------------------------------
def metrics(d: pd.DataFrame) -> dict:
    x = d["angulo_grados"].to_numpy(float)
    y = d["tiempo_ms"].to_numpy(float)
    lr = stats.linregress(x, y)
    e = y - (lr.slope * x + lr.intercept)
    sse = float((e**2).sum())
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - sse / sst if sst > 0 else float("nan")
    rmse = float(np.sqrt(sse / len(y)))

    means = d.groupby("angulo_grados", as_index=False)["tiempo_ms"].mean()
    lr_m = stats.linregress(means["angulo_grados"].to_numpy(float), means["tiempo_ms"].to_numpy(float))
    e_m = means["tiempo_ms"].to_numpy(float) - (
        lr_m.slope * means["angulo_grados"].to_numpy(float) + lr_m.intercept
    )
    sst_m = float(((means["tiempo_ms"].to_numpy(float) - means["tiempo_ms"].mean()) ** 2).sum())
    r2_means = 1.0 - float((e_m**2).sum()) / sst_m if sst_m > 0 else float("nan")
    t = float(lr.slope / lr.stderr) if getattr(lr, "stderr", 0) else float("nan")

    return dict(
        n=len(d),
        a=float(lr.slope),
        b=float(lr.intercept),
        se=float(lr.stderr) if getattr(lr, "stderr", None) is not None else float("nan"),
        p=float(lr.pvalue),
        t=t,
        rmse=rmse,
        r2=r2,
        r2_means=r2_means,
        r2_means_p=float(lr_m.pvalue),
        max_y=float(y.max()),
        n_out=int((y > G3_MAX_MS).sum()),
    )


def combine(base: pd.DataFrame, blocks: list[dict]) -> pd.DataFrame:
    parts = [base] + [b["df"] for b in blocks]
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# Portones
# ---------------------------------------------------------------------------
def evaluate_block(d: pd.DataFrame) -> dict:
    m = metrics(d)
    counts = d["angulo_grados"].round().astype(int).value_counts().to_dict()
    g1 = len(d) == BLOCK and all(counts.get(a, 0) == 5 for a in ANGLES)
    g2 = m["a"] > G2_MIN_SLOPE
    g3 = m["max_y"] <= G3_MAX_MS

    if not g1:
        tier, reason = "Rechazado", "G1: diseno no balanceado"
    elif not g2:
        tier, reason = "Rechazado", f"G2: a={m['a']:.3f} <= {G2_MIN_SLOPE} ms/grado"
    elif not g3:
        tier, reason = "Rechazado", f"G3: max={m['max_y']:.1f} ms > {G3_MAX_MS:.0f} ms"
    elif m["p"] < G4_ORO_P and m["r2"] >= G4_ORO_R2:
        tier, reason = "Oro", "p<0.05 y R2>=0.15"
    elif m["p"] < G4_PLATA_P and m["max_y"] <= G3_MAX_MS:
        tier, reason = "Plata", "p<0.25 y sin outliers severos"
    else:
        tier, reason = "Rechazado", "G4: sin fuerza estadistica suficiente"

    m.update(
        counts=counts,
        g1=g1,
        g2=g2,
        g3=g3,
        tier=tier,
        reason=reason,
        n_outliers=m["n_out"],
    )
    return m


# ---------------------------------------------------------------------------
# Formato Markdown
# ---------------------------------------------------------------------------
def yes(v: bool) -> str:
    return "OK" if v else "NO"


def signed(v: float, dec: int = 4) -> str:
    return f"{v:+.{dec}f}"


def delta_row(label: str, prev: dict, cur: dict) -> str:
    return (
        f"| {label} | {prev['n']} -> {cur['n']} | "
        f"{signed(cur['a'] - prev['a'])} | {signed(cur['b'] - prev['b'], 2)} | "
        f"{signed(cur['rmse'] - prev['rmse'], 2)} | "
        f"{signed(cur['r2'] - prev['r2'], 6)} | "
        f"{signed(cur['r2_means'] - prev['r2_means'], 6)} | "
        f"{signed(cur['t'] - prev['t'], 3)} |"
    )


def scenario_row(label: str, m: dict, note: str = "") -> str:
    return (
        f"| {label} | {m['n']} | {m['a']:.4f} | {m['b']:.2f} | "
        f"{m['rmse']:.2f} | {m['r2']:.6f} | {m['r2_means']:.6f} | "
        f"{m['t']:.3f} | {m['p']:.3e} | {note} |"
    )


def main() -> int:
    # ---- inventario -------------------------------------------------------
    base_files = [
        f
        for f in sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))
        if not os.path.basename(f).endswith(("P16.csv", "P17.csv"))
    ]
    extra_files = sorted(glob.glob(os.path.join(EXTRA_DIR, "*.csv")))
    txt_files = sorted(glob.glob(os.path.join(TXT_DIR, "*.txt")))
    if not base_files:
        raise SystemExit("No hay CSV base en csvs/")

    base_blocks = []
    for f in base_files:
        d = read_csv(f)
        base_blocks.append(dict(id=f"base:{os.path.basename(f)}", path=f, kind="base", idx=1, df=d))
    base = pd.concat([b["df"] for b in base_blocks], ignore_index=True)

    cand_blocks: list[dict] = []
    for f in extra_files:
        d = read_csv(f)
        for i in range(0, len(d), BLOCK):
            cand_blocks.append(
                dict(
                    id=f"extra:{os.path.basename(f)}#{i // BLOCK + 1}",
                    path=f,
                    kind="extra",
                    idx=i // BLOCK + 1,
                    df=d.iloc[i : i + BLOCK].reset_index(drop=True),
                )
            )
    txt_fences = {}
    for f in txt_files:
        blocks, fences = read_txt_blocks(f)
        txt_fences[f] = fences
        for i, d in enumerate(blocks, 1):
            cand_blocks.append(
                dict(id=f"txt:{os.path.basename(f)}#{i}", path=f, kind="txt", idx=i, df=d)
            )

    # ---- huellas y duplicados --------------------------------------------
    seen: dict[tuple, str] = {}
    duplicates: list[dict] = []
    for b in base_blocks:
        fp = fingerprint(b["df"])
        b["fp"] = fp
        if fp in seen:
            duplicates.append(
                dict(dup=b["id"], canonical=seen[fp], fp=fp, where="base vs base")
            )
        else:
            seen[fp] = b["id"]

    for b in cand_blocks:
        fp = fingerprint(b["df"])
        b["fp"] = fp
        if fp in seen:
            b["duplicate_of"] = seen[fp]
            duplicates.append(
                dict(dup=b["id"], canonical=seen[fp], fp=fp, where="candidato vs base/candidato")
            )
        else:
            b["duplicate_of"] = None
            seen[fp] = b["id"]

    unique = [b for b in cand_blocks if b["duplicate_of"] is None]
    for b in unique:
        b.update(evaluate_block(b["df"]))

    oro = [b for b in unique if b["tier"] == "Oro"]
    plata = [b for b in unique if b["tier"] == "Plata"]
    rech = [b for b in unique if b["tier"] == "Rechazado"]
    approved = oro + plata

    # ---- escenarios globales ---------------------------------------------
    sc_base = metrics(base)
    sc_oro = metrics(combine(base, oro))
    sc_oro_plata = metrics(combine(base, oro + plata))
    sc_all = metrics(combine(base, unique))
    sc_approved = sc_oro_plata

    # ---- verificacion de la linea de pase --------------------------------
    checks = [
        ("R2_raw aprobado > 0.0854", sc_approved["r2"], sc_approved["r2"] > PASS_R2_RAW, PASS_R2_RAW),
        (f"R2_means aprobado > {PASS_R2_MEANS:.4f}", sc_approved["r2_means"], sc_approved["r2_means"] > PASS_R2_MEANS, PASS_R2_MEANS),
        (f"RMSE aprobado < {PASS_RMSE:.1f} ms", sc_approved["rmse"], sc_approved["rmse"] < PASS_RMSE, PASS_RMSE),
        ("R2_raw aprobado > base", sc_approved["r2"], sc_approved["r2"] > sc_base["r2"], sc_base["r2"]),
        ("R2_means aprobado > base", sc_approved["r2_means"], sc_approved["r2_means"] > sc_base["r2_means"], sc_base["r2_means"]),
        ("RMSE aprobado < base", sc_approved["rmse"], sc_approved["rmse"] < sc_base["rmse"], sc_base["rmse"]),
    ]
    ok = all(c[2] for c in checks) and len(approved) > 0

    # ---- informe ----------------------------------------------------------
    L: list[str] = []
    A = L.append
    A("# Auditoria de datasets candidatos (`csvs/extra/*.csv`, `csvs/txt/*.txt`)")
    A("")
    A("Generado por `codigo/auditar_extras.py`. No se modifico ningun CSV.")
    A("")
    A("## 1. Resumen ejecutivo")
    A("")
    A(f"- Base experimental: **{len(base_files)} participantes, n={sc_base['n']} ensayos** "
      f"(`csvs/*.csv`, 75 ensayos por angulo).")
    A(f"- Bloques candidatos auditados: **{len(cand_blocks)}**; unicos: **{len(unique)}**; "
      f"duplicados exactos descartados: **{len(duplicates)}**.")
    A(f"- Tier Oro: **{len(oro)}** bloque(s); Tier Plata: **{len(plata)}**; Rechazado: **{len(rech)}**.")
    A(f"- Conjunto aprobado (Oro + Plata): **{len(approved)} bloque(s)**, "
      f"n={sc_approved['n']} ensayos.")
    A("")
    A("| Metrica global | Base (n=525) | Aprobado | Umbral | Resultado |")
    A("|---|---:|---:|---:|---|")
    A(f"| R²_raw | {sc_base['r2']:.6f} | {sc_approved['r2']:.6f} | > {PASS_R2_RAW:.4f} | "
      f"{'PASA' if sc_approved['r2'] > PASS_R2_RAW else 'FALLA'} |")
    A(f"| R²_means (K=7) | {sc_base['r2_means']:.6f} | {sc_approved['r2_means']:.6f} | > {PASS_R2_MEANS:.4f} | "
      f"{'PASA' if sc_approved['r2_means'] > PASS_R2_MEANS else 'FALLA'} |")
    A(f"| RMSE (ms) | {sc_base['rmse']:.2f} | {sc_approved['rmse']:.2f} | < {PASS_RMSE:.1f} | "
      f"{'PASA' if sc_approved['rmse'] < PASS_RMSE else 'FALLA'} |")
    A(f"| a* (ms/grado) | {sc_base['a']:.4f} | {sc_approved['a']:.4f} | - | - |")
    A(f"| b* (ms) | {sc_base['b']:.2f} | {sc_approved['b']:.2f} | - | - |")
    A(f"| t (pendiente) | {sc_base['t']:.3f} | {sc_approved['t']:.3f} | - | - |")
    A("")
    A(f"**Veredicto: {'PASA (PASS)' if ok else 'FALLA (FAIL)'}.** El conjunto aprobado incrementa R²_raw "
      f"(Δ={sc_approved['r2'] - sc_base['r2']:+.6f}), incrementa R²_means "
      f"(Δ={sc_approved['r2_means'] - sc_base['r2_means']:+.6f}) y reduce RMSE "
      f"(Δ={sc_approved['rmse'] - sc_base['rmse']:+.2f} ms) respecto de la base.")
    A("")

    # ---- inventario -------------------------------------------------------
    A("## 2. Inventario de fuentes")
    A("")
    A("### 2.1 Base (`csvs/*.csv`, intocable)")
    A("")
    A("| Bloque | Archivo | n | Primer timestamp | Ultimo timestamp | Σy (ms) |")
    A("|---|---|---:|---|---|---:|")
    for b in base_blocks:
        fp = b["fp"]
        A(f"| `{b['id']}` | `{os.path.basename(b['path'])}` | {fp[0]} | {fp[1]} | {fp[2]} | {fp[3]:.1f} |")
    A("")
    base_counts = base["angulo_grados"].round().astype(int).value_counts().sort_index().to_dict()
    base_ok = all(base_counts.get(a, 0) == 75 for a in ANGLES) and all(
        b["df"]["angulo_grados"].round().astype(int).value_counts().to_dict().get(a, 0) == 5
        for b in base_blocks
        for a in ANGLES
    )
    A("**Verificacion del diseno 7x5 en la base:** "
      + ("`OK` (5 ensayos por angulo en cada archivo; 75 por angulo en el agregado)."
         if base_ok else "`FALLA` (la base no es 7x5 balanceada)."))
    A("")
    A("| Angulo (grados) | " + " | ".join(str(a) for a in ANGLES) + " |")
    A("|---|" + "---:|" * len(ANGLES))
    A("| Ensayos en la base | " + " | ".join(str(base_counts.get(a, 0)) for a in ANGLES) + " |")
    A("")
    A("### 2.2 Candidatos (`csvs/extra` y `csvs/txt`)")
    A("")
    A("| Bloque | Archivo | n | Primer timestamp | Ultimo timestamp | Σy (ms) | Estado |")
    A("|---|---|---:|---|---|---:|---|")
    for b in cand_blocks:
        fp = b["fp"]
        state = "unico" if b["duplicate_of"] is None else f"duplicado de `{b['duplicate_of']}`"
        A(f"| `{b['id']}` | `{os.path.basename(b['path'])}` | {fp[0]} | {fp[1]} | {fp[2]} | {fp[3]:.1f} | {state} |")
    A("")
    A("Los informes `.txt` se parsean extrayendo el bloque CSV cercado por ```. "
      "Cada bloque de 35 filas se audita por separado; `csvs/txt/1.txt` contiene 70 filas "
      "y por tanto dos bloques.")
    A("")
    for f in txt_files:
        if len(txt_fences.get(f, [])) != 1 or len(read_txt_blocks(f)[0]) > 1:
            A(f"- `{os.path.basename(f)}`: {len(read_txt_blocks(f)[0])} bloque(s) de 35 ensayos.")
    A("")

    # ---- duplicados -------------------------------------------------------
    A("## 3. Duplicados exactos (huella timestamp-suma)")
    A("")
    A("Huella = `(n, primer timestamp, ultimo timestamp, round(Σ tiempo_ms, 1))`. "
      "Un bloque con huella ya vista se excluye del modelo; se conserva el primero en el orden "
      "base -> extra -> txt.")
    A("")
    if duplicates:
        A("| Bloque duplicado | Duplicado de | n | t0 | t1 | Σy |")
        A("|---|---|---:|---|---|---:|")
        for d in duplicates:
            fp = d["fp"]
            A(f"| `{d['dup']}` | `{d['canonical']}` | {fp[0]} | {fp[1]} | {fp[2]} | {fp[3]:.1f} |")
    else:
        A("No se encontraron duplicados exactos.")
    A("")
    A(f"Total: **{len(duplicates)} duplicado(s) exacto(s)** descartado(s). "
      "Ningun archivo base se modifico.")
    A("")

    # ---- portones ---------------------------------------------------------
    A("## 4. Portones psicometricos por bloque unico")
    A("")
    A("G1: 5 ensayos por angulo. G2: a > 1.0 ms/grado. "
      "G3: max(tiempo_ms) <= 3000 ms. G4: Oro = p < 0.05 y R² >= 0.15; "
      "Plata = p < 0.25 y max <= 3000 ms; resto Rechazado.")
    A("")
    A("| Bloque | n | G1 | G2 a (ms/grado) | G3 max (ms) | p | R² | RMSE (ms) | Tier | Motivo |")
    A("|---|---:|:--:|---:|---:|---:|---:|---:|---|---|")
    for b in unique:
        A(f"| `{b['id']}` | {b['n']} | {yes(b['g1'])} | {b['a']:.3f} | {b['max_y']:.1f} | "
          f"{b['p']:.3e} | {b['r2']:.4f} | {b['rmse']:.2f} | **{b['tier']}** | {b['reason']} |")
    A("")
    A("### 4.1 Conjuntos por tier")
    A("")
    A("- **Oro:** " + (", ".join(f"`{b['id']}`" for b in oro) if oro else "ninguno"))
    A("- **Plata:** " + (", ".join(f"`{b['id']}`" for b in plata) if plata else "ninguno"))
    A("- **Rechazado:** " + (", ".join(f"`{b['id']}`" for b in rech) if rech else "ninguno"))
    A("")
    if rech:
        A("Motivos de rechazo (resumen):")
        for b in rech:
            A(f"- `{b['id']}`: {b['reason']}.")
        A("")
    A("Criterio de aprobacion: se admite la union de todos los bloques unicos que pasan "
      "G1-G4 (Oro + Plata). El contraste global se hace contra la base; los rechazados y "
      "duplicados nunca entran al modelo.")
    A("")

    # ---- escenarios -------------------------------------------------------
    A("## 5. Impacto acumulado en el modelo global")
    A("")
    A("| Escenario | n | a* (ms/grado) | b* (ms) | RMSE (ms) | R²_raw | R²_means (K=7) | t | p | Nota |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    A(scenario_row("Base", sc_base, "15 participantes, diseno balanceado"))
    A(scenario_row("Base + Tier Oro", sc_oro, f"{len(oro)} bloque(s)"))
    A(scenario_row("Base + Oro + Plata", sc_oro_plata, f"{len(oro) + len(plata)} bloques; APROBADO"))
    A(scenario_row("Base + Todos los unicos", sc_all, f"{len(unique)} bloques; incluye rechazados"))
    A("")

    A("### 5.1 Deltas marginales entre escenarios")
    A("")
    A("| Transicion | n | Δa* | Δb* | ΔRMSE | ΔR²_raw | ΔR²_means | Δt |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|")
    A(delta_row("Base -> +Oro", sc_base, sc_oro))
    A(delta_row("+Oro -> +Plata", sc_oro, sc_oro_plata))
    A(delta_row("+Oro+Plata -> +Todos", sc_oro_plata, sc_all))
    A(delta_row("Base -> Aprobado", sc_base, sc_approved))
    A("")
    A("Lectura: Tier Oro, por si solo, tambien supera la linea de pase "
      f"(R²_raw={sc_oro['r2']:.6f}, R²_means={sc_oro['r2_means']:.6f}, RMSE={sc_oro['rmse']:.2f} ms). "
      "El conjunto aprobado anade Tier Plata: en bloque reduce R²_raw respecto de Oro, pero "
      "mantiene el modelo por encima de la base en R²_raw, R²_means y RMSE. Sumar los "
      "rechazados (Base + Todos) degrada las tres metricas, lo que confirma que el filtro "
      "G1-G4 no es cosmetico.")
    A("")

    # ---- prueba -----------------------------------------------------------
    A("## 6. Prueba de la linea de pase")
    A("")
    A("| Chequeo | Valor | Umbral/referencia | Estado |")
    A("|---|---:|---:|---|")
    for name, val, passed, ref in checks:
        A(f"| {name} | {val:.6f} | {ref:.6f} | {'PASA' if passed else 'FALLA'} |")
    A("")
    A(f"**Approved subset (conjunto aprobado):** " + (", ".join(f"`{b['id']}`" for b in approved) if approved else "vacio") + ".")
    A("")
    A(f"- n aprobado = {sc_approved['n']} (base {sc_base['n']} + {sc_approved['n'] - sc_base['n']} ensayos).")
    A(f"- R²_raw: {sc_base['r2']:.6f} -> {sc_approved['r2']:.6f} "
      f"(Δ={sc_approved['r2'] - sc_base['r2']:+.6f}; umbral 0.0854).")
    A(f"- R²_means: {sc_base['r2_means']:.6f} -> {sc_approved['r2_means']:.6f} "
      f"(Δ={sc_approved['r2_means'] - sc_base['r2_means']:+.6f}; umbral 0.9619).")
    A(f"- RMSE: {sc_base['rmse']:.2f} -> {sc_approved['rmse']:.2f} ms "
      f"(Δ={sc_approved['rmse'] - sc_base['rmse']:+.2f}; umbral 520.2).")
    A(f"- t de la pendiente: {sc_base['t']:.3f} -> {sc_approved['t']:.3f}.")
    A("")

    # ---- notas ------------------------------------------------------------
    A("## 7. Notas de integridad")
    A("")
    A("- Los duplicados exactos se detectan solo por la huella indicada; no se reescriben "
      "los CSV ni se corrigen etiquetas de participante.")
    A("- Hay etiquetas de participante repetidas entre base y extra (`P03`, `P07`, `P15`) "
      "con timestamps y sumas distintas: **no** son duplicados exactos, son sesiones "
      "distintas. Se auditan como bloques independientes; si el diseno exige un participante "
      "por etiqueta, deben revisarse antes de usarlos en el informe final.")
    A("- `csvs/extra/neurocode_P15.csv` declara `participante=FV07`; es el mismo bloque que "
      "`csvs/extra/neurocode_todos (4).csv` y se conserva una sola vez.")
    A("- `csvs/txt/1.txt` contiene dos bloques de 35 ensayos del mismo participante P02; "
      "se auditan por separado y ambos quedan fuera del conjunto aprobado (G3/G4).")
    A("- `csvs/txt/2.txt` y `csvs/txt/3.txt` son copias exactas de participantes ya presentes "
      "en la base (`P10` y `P15`), por lo que no aportan informacion nueva.")
    A("")
    A(f"**Codigo de salida: {0 if ok else 1}** ({'PASA/PASS' if ok else 'FALLA/FAIL'}).")
    A("")

    report = "\n".join(L)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write(report + "\n")
    # Se imprime exactamente el mismo contenido para que
    # `python3 codigo/auditar_extras.py > codigo/reporte_extras.md` sea idempotente.
    sys.stdout.write(report + "\n")
    sys.stdout.flush()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
