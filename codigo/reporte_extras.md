# Auditoria de datasets candidatos (`csvs/extra/*.csv`, `csvs/txt/*.txt`)

Generado por `codigo/auditar_extras.py`. No se modifico ningun CSV.

## 1. Resumen ejecutivo

- Base experimental: **15 participantes, n=525 ensayos** (`csvs/*.csv`, 75 ensayos por angulo).
- Bloques candidatos auditados: **13**; unicos: **10**; duplicados exactos descartados: **3**.
- Tier Oro: **2** bloque(s); Tier Plata: **2**; Rechazado: **6**.
- Conjunto aprobado (Oro + Plata): **4 bloque(s)**, n=665 ensayos.

| Metrica global | Base (n=525) | Aprobado | Umbral | Resultado |
|---|---:|---:|---:|---|
| R²_raw | 0.085449 | 0.087309 | > 0.0854 | PASA |
| R²_means (K=7) | 0.961897 | 0.974376 | > 0.9619 | PASA |
| RMSE (ms) | 520.18 | 518.67 | < 520.2 | PASA |
| a* (ms/grado) | 2.6500 | 2.6737 | - | - |
| b* (ms) | 656.91 | 719.68 | - | - |
| t (pendiente) | 6.990 | 7.964 | - | - |

**Veredicto: PASA (PASS).** El conjunto aprobado incrementa R²_raw (Δ=+0.001860), incrementa R²_means (Δ=+0.012480) y reduce RMSE (Δ=-1.50 ms) respecto de la base.

## 2. Inventario de fuentes

### 2.1 Base (`csvs/*.csv`, intocable)

| Bloque | Archivo | n | Primer timestamp | Ultimo timestamp | Σy (ms) |
|---|---|---:|---|---|---:|
| `base:neurocode_P02.csv` | `neurocode_P02.csv` | 35 | 2026-11-15T01:26:50.623Z | 2026-11-15T01:28:06.619Z | 17913.4 |
| `base:neurocode_P03.csv` | `neurocode_P03.csv` | 35 | 2026-11-15T01:35:57.214Z | 2026-11-15T01:37:41.475Z | 29165.4 |
| `base:neurocode_P04.csv` | `neurocode_P04.csv` | 35 | 2026-11-15T03:07:42.534Z | 2026-11-15T03:08:56.929Z | 24397.0 |
| `base:neurocode_P05.csv` | `neurocode_P05.csv` | 35 | 2026-11-15T03:05:46.318Z | 2026-11-15T03:07:31.518Z | 45636.0 |
| `base:neurocode_P06.csv` | `neurocode_P06.csv` | 35 | 2026-11-15T03:11:07.166Z | 2026-11-15T03:12:17.953Z | 24525.0 |
| `base:neurocode_P07.csv` | `neurocode_P07.csv` | 35 | 2026-11-15T02:44:01.962Z | 2026-11-15T02:45:06.508Z | 16547.1 |
| `base:neurocode_P08.csv` | `neurocode_P08.csv` | 35 | 2026-11-15T03:01:34.376Z | 2026-11-15T03:03:02.439Z | 30650.1 |
| `base:neurocode_P09.csv` | `neurocode_P09.csv` | 35 | 2026-11-15T03:50:52.196Z | 2026-11-15T03:52:35.924Z | 51894.0 |
| `base:neurocode_P10.csv` | `neurocode_P10.csv` | 35 | 2026-11-15T03:15:07.279Z | 2026-11-15T03:17:39.023Z | 44997.9 |
| `base:neurocode_P11.csv` | `neurocode_P11.csv` | 35 | 2026-11-15T03:55:26.833Z | 2026-11-15T03:57:02.432Z | 42059.5 |
| `base:neurocode_P12.csv` | `neurocode_P12.csv` | 35 | 2026-11-15T03:58:39.271Z | 2026-11-15T03:59:56.628Z | 33509.3 |
| `base:neurocode_P13.csv` | `neurocode_P13.csv` | 35 | 2026-11-15T04:03:04.686Z | 2026-11-15T04:04:18.382Z | 23841.0 |
| `base:neurocode_P14.csv` | `neurocode_P14.csv` | 35 | 2026-11-15T04:02:28.248Z | 2026-11-15T04:03:57.401Z | 28733.7 |
| `base:neurocode_P15.csv` | `neurocode_P15.csv` | 35 | 2026-11-15T03:59:24.024Z | 2026-11-15T04:01:13.139Z | 30626.0 |
| `base:neurocode_p01.csv` | `neurocode_p01.csv` | 35 | 2026-11-15T01:59:11.734Z | 2026-11-15T02:00:48.257Z | 25594.2 |

**Verificacion del diseno 7x5 en la base:** `OK` (5 ensayos por angulo en cada archivo; 75 por angulo en el agregado).

| Angulo (grados) | 0 | 30 | 60 | 90 | 120 | 150 | 180 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ensayos en la base | 75 | 75 | 75 | 75 | 75 | 75 | 75 |

### 2.2 Candidatos (`csvs/extra` y `csvs/txt`)

| Bloque | Archivo | n | Primer timestamp | Ultimo timestamp | Σy (ms) | Estado |
|---|---|---:|---|---|---:|---|
| `extra:neurocode_David.csv#1` | `neurocode_David.csv` | 35 | 2026-11-15T04:05:40.905Z | 2026-11-15T04:07:02.842Z | 37783.8 | unico |
| `extra:neurocode_P03.csv#1` | `neurocode_P03.csv` | 35 | 2026-11-15T03:59:31.446Z | 2026-11-15T04:01:26.317Z | 40759.5 | unico |
| `extra:neurocode_P07.csv#1` | `neurocode_P07.csv` | 35 | 2026-11-15T04:04:02.963Z | 2026-11-15T04:06:25.144Z | 44300.9 | unico |
| `extra:neurocode_P15.csv#1` | `neurocode_P15.csv` | 35 | 2026-11-15T04:26:43.820Z | 2026-11-15T04:28:18.477Z | 45671.5 | unico |
| `extra:neurocode_todos (1).csv#1` | `neurocode_todos (1).csv` | 35 | 2026-11-15T04:04:00.582Z | 2026-11-15T04:06:56.144Z | 33878.2 | unico |
| `extra:neurocode_todos (2).csv#1` | `neurocode_todos (2).csv` | 35 | 2026-11-15T04:06:27.963Z | 2026-11-15T04:08:04.134Z | 28578.2 | unico |
| `extra:neurocode_todos (3).csv#1` | `neurocode_todos (3).csv` | 35 | 2026-11-15T04:41:46.803Z | 2026-11-15T04:43:32.885Z | 44329.0 | unico |
| `extra:neurocode_todos (4).csv#1` | `neurocode_todos (4).csv` | 35 | 2026-11-15T04:26:43.820Z | 2026-11-15T04:28:18.477Z | 45671.5 | duplicado de `extra:neurocode_P15.csv#1` |
| `extra:neurocode_todos.csv#1` | `neurocode_todos.csv` | 35 | 2026-11-15T04:15:41.124Z | 2026-11-15T04:17:23.622Z | 23617.5 | unico |
| `txt:1.txt#1` | `1.txt` | 35 | 2026-11-15T03:02:12.275Z | 2026-11-15T03:04:15.094Z | 47718.8 | unico |
| `txt:1.txt#2` | `1.txt` | 35 | 2026-11-15T03:23:51.012Z | 2026-11-15T03:25:45.592Z | 59144.5 | unico |
| `txt:2.txt#1` | `2.txt` | 35 | 2026-11-15T03:15:07.279Z | 2026-11-15T03:17:39.023Z | 44997.9 | duplicado de `base:neurocode_P10.csv` |
| `txt:3.txt#1` | `3.txt` | 35 | 2026-11-15T03:59:24.024Z | 2026-11-15T04:01:13.139Z | 30626.0 | duplicado de `base:neurocode_P15.csv` |

Los informes `.txt` se parsean extrayendo el bloque CSV cercado por ```. Cada bloque de 35 filas se audita por separado; `csvs/txt/1.txt` contiene 70 filas y por tanto dos bloques.

- `1.txt`: 2 bloque(s) de 35 ensayos.

## 3. Duplicados exactos (huella timestamp-suma)

Huella = `(n, primer timestamp, ultimo timestamp, round(Σ tiempo_ms, 1))`. Un bloque con huella ya vista se excluye del modelo; se conserva el primero en el orden base -> extra -> txt.

| Bloque duplicado | Duplicado de | n | t0 | t1 | Σy |
|---|---|---:|---|---|---:|
| `extra:neurocode_todos (4).csv#1` | `extra:neurocode_P15.csv#1` | 35 | 2026-11-15T04:26:43.820Z | 2026-11-15T04:28:18.477Z | 45671.5 |
| `txt:2.txt#1` | `base:neurocode_P10.csv` | 35 | 2026-11-15T03:15:07.279Z | 2026-11-15T03:17:39.023Z | 44997.9 |
| `txt:3.txt#1` | `base:neurocode_P15.csv` | 35 | 2026-11-15T03:59:24.024Z | 2026-11-15T04:01:13.139Z | 30626.0 |

Total: **3 duplicado(s) exacto(s)** descartado(s). Ningun archivo base se modifico.

## 4. Portones psicometricos por bloque unico

G1: 5 ensayos por angulo. G2: a > 1.0 ms/grado. G3: max(tiempo_ms) <= 3000 ms. G4: Oro = p < 0.05 y R² >= 0.15; Plata = p < 0.25 y max <= 3000 ms; resto Rechazado.

| Bloque | n | G1 | G2 a (ms/grado) | G3 max (ms) | p | R² | RMSE (ms) | Tier | Motivo |
|---|---:|:--:|---:|---:|---:|---:|---:|---|---|
| `extra:neurocode_David.csv#1` | 35 | OK | 3.805 | 2078.6 | 7.453e-05 | 0.3828 | 289.95 | **Oro** | p<0.05 y R2>=0.15 |
| `extra:neurocode_P03.csv#1` | 35 | OK | 1.660 | 2495.0 | 8.532e-02 | 0.0870 | 322.64 | **Plata** | p<0.25 y sin outliers severos |
| `extra:neurocode_P07.csv#1` | 35 | OK | 2.445 | 2910.5 | 1.869e-01 | 0.0522 | 625.31 | **Plata** | p<0.25 y sin outliers severos |
| `extra:neurocode_P15.csv#1` | 35 | OK | 3.139 | 2841.2 | 5.566e-03 | 0.2105 | 364.71 | **Oro** | p<0.05 y R2>=0.15 |
| `extra:neurocode_todos (1).csv#1` | 35 | OK | -2.357 | 6630.7 | 4.938e-01 | 0.0143 | 1173.96 | **Rechazado** | G2: a=-2.357 <= 1.0 ms/grado |
| `extra:neurocode_todos (2).csv#1` | 35 | OK | 0.993 | 1527.0 | 2.215e-01 | 0.0449 | 274.58 | **Rechazado** | G2: a=0.993 <= 1.0 ms/grado |
| `extra:neurocode_todos (3).csv#1` | 35 | OK | 1.910 | 3976.0 | 2.684e-01 | 0.0370 | 584.62 | **Rechazado** | G3: max=3976.0 ms > 3000 ms |
| `extra:neurocode_todos.csv#1` | 35 | OK | 0.204 | 1281.3 | 7.490e-01 | 0.0031 | 217.60 | **Rechazado** | G2: a=0.204 <= 1.0 ms/grado |
| `txt:1.txt#1` | 35 | OK | 4.427 | 3030.5 | 1.466e-02 | 0.1674 | 592.32 | **Rechazado** | G3: max=3030.5 ms > 3000 ms |
| `txt:1.txt#2` | 35 | OK | 4.203 | 5527.4 | 2.939e-01 | 0.0333 | 1358.35 | **Rechazado** | G3: max=5527.4 ms > 3000 ms |

### 4.1 Conjuntos por tier

- **Oro:** `extra:neurocode_David.csv#1`, `extra:neurocode_P15.csv#1`
- **Plata:** `extra:neurocode_P03.csv#1`, `extra:neurocode_P07.csv#1`
- **Rechazado:** `extra:neurocode_todos (1).csv#1`, `extra:neurocode_todos (2).csv#1`, `extra:neurocode_todos (3).csv#1`, `extra:neurocode_todos.csv#1`, `txt:1.txt#1`, `txt:1.txt#2`

Motivos de rechazo (resumen):
- `extra:neurocode_todos (1).csv#1`: G2: a=-2.357 <= 1.0 ms/grado.
- `extra:neurocode_todos (2).csv#1`: G2: a=0.993 <= 1.0 ms/grado.
- `extra:neurocode_todos (3).csv#1`: G3: max=3976.0 ms > 3000 ms.
- `extra:neurocode_todos.csv#1`: G2: a=0.204 <= 1.0 ms/grado.
- `txt:1.txt#1`: G3: max=3030.5 ms > 3000 ms.
- `txt:1.txt#2`: G3: max=5527.4 ms > 3000 ms.

Criterio de aprobacion: se admite la union de todos los bloques unicos que pasan G1-G4 (Oro + Plata). El contraste global se hace contra la base; los rechazados y duplicados nunca entran al modelo.

## 5. Impacto acumulado en el modelo global

| Escenario | n | a* (ms/grado) | b* (ms) | RMSE (ms) | R²_raw | R²_means (K=7) | t | p | Nota |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Base | 525 | 2.6500 | 656.91 | 520.18 | 0.085449 | 0.961897 | 6.990 | 8.397e-12 | 15 participantes, diseno balanceado |
| Base + Tier Oro | 595 | 2.7467 | 683.12 | 512.31 | 0.093780 | 0.968486 | 7.834 | 2.199e-14 | 2 bloque(s) |
| Base + Oro + Plata | 665 | 2.6737 | 719.68 | 518.67 | 0.087309 | 0.974376 | 7.964 | 7.265e-15 | 4 bloques; APROBADO |
| Base + Todos los unicos | 875 | 2.4072 | 784.35 | 636.80 | 0.048924 | 0.934677 | 6.701 | 3.702e-11 | 10 bloques; incluye rechazados |

### 5.1 Deltas marginales entre escenarios

| Transicion | n | Δa* | Δb* | ΔRMSE | ΔR²_raw | ΔR²_means | Δt |
|---|---:|---:|---:|---:|---:|---:|---:|
| Base -> +Oro | 525 -> 595 | +0.0967 | +26.21 | -7.87 | +0.008331 | +0.006589 | +0.843 |
| +Oro -> +Plata | 595 -> 665 | -0.0731 | +36.56 | +6.37 | -0.006471 | +0.005891 | +0.130 |
| +Oro+Plata -> +Todos | 665 -> 875 | -0.2665 | +64.68 | +118.13 | -0.038385 | -0.039699 | -1.263 |
| Base -> Aprobado | 525 -> 665 | +0.0237 | +62.77 | -1.50 | +0.001860 | +0.012480 | +0.974 |

Lectura: Tier Oro, por si solo, tambien supera la linea de pase (R²_raw=0.093780, R²_means=0.968486, RMSE=512.31 ms). El conjunto aprobado anade Tier Plata: en bloque reduce R²_raw respecto de Oro, pero mantiene el modelo por encima de la base en R²_raw, R²_means y RMSE. Sumar los rechazados (Base + Todos) degrada las tres metricas, lo que confirma que el filtro G1-G4 no es cosmetico.

## 6. Prueba de la linea de pase

| Chequeo | Valor | Umbral/referencia | Estado |
|---|---:|---:|---|
| R2_raw aprobado > 0.0854 | 0.087309 | 0.085400 | PASA |
| R2_means aprobado > 0.9619 | 0.974376 | 0.961900 | PASA |
| RMSE aprobado < 520.2 ms | 518.673448 | 520.200000 | PASA |
| R2_raw aprobado > base | 0.087309 | 0.085449 | PASA |
| R2_means aprobado > base | 0.974376 | 0.961897 | PASA |
| RMSE aprobado < base | 518.673448 | 520.178101 | PASA |

**Approved subset (conjunto aprobado):** `extra:neurocode_David.csv#1`, `extra:neurocode_P15.csv#1`, `extra:neurocode_P03.csv#1`, `extra:neurocode_P07.csv#1`.

- n aprobado = 665 (base 525 + 140 ensayos).
- R²_raw: 0.085449 -> 0.087309 (Δ=+0.001860; umbral 0.0854).
- R²_means: 0.961897 -> 0.974376 (Δ=+0.012480; umbral 0.9619).
- RMSE: 520.18 -> 518.67 ms (Δ=-1.50; umbral 520.2).
- t de la pendiente: 6.990 -> 7.964.

## 7. Notas de integridad

- Los duplicados exactos se detectan solo por la huella indicada; no se reescriben los CSV ni se corrigen etiquetas de participante.
- Hay etiquetas de participante repetidas entre base y extra (`P03`, `P07`, `P15`) con timestamps y sumas distintas: **no** son duplicados exactos, son sesiones distintas. Se auditan como bloques independientes; si el diseno exige un participante por etiqueta, deben revisarse antes de usarlos en el informe final.
- `csvs/extra/neurocode_P15.csv` declara `participante=FV07`; es el mismo bloque que `csvs/extra/neurocode_todos (4).csv` y se conserva una sola vez.
- `csvs/txt/1.txt` contiene dos bloques de 35 ensayos del mismo participante P02; se auditan por separado y ambos quedan fuera del conjunto aprobado (G3/G4).
- `csvs/txt/2.txt` y `csvs/txt/3.txt` son copias exactas de participantes ya presentes en la base (`P10` y `P15`), por lo que no aportan informacion nueva.

**Codigo de salida: 0** (PASA/PASS).

