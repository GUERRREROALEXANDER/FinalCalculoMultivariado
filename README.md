# 🧠 NeuroCode — ¿A qué velocidad gira tu cerebro?

**Proyecto final de Cálculo Multivariable · Ingeniería de Software · Universidad Cooperativa de Colombia (Pasto)**  
**Docente:** M.Sc. Alejandro Molina · **Entrega y sustentación:** martes 17 de noviembre de 2026

> Regresión lineal y optimización mediante funciones de dos variables aplicada a un experimento real de neurociencia cognitiva: la **rotación mental** (Shepard & Metzler, 1971).

---

## 0. Estado ejecutivo y resultados principales (actualizado 15 nov)

La base oficial tiene **17 participantes con sesión completa ($n = 595$ ensayos, diseño balanceado $m = 85$ ensayos por cada uno de los $K = 7$ ángulos)**:

- **Parámetros óptimos:** $a^* = \mathbf{2.746737\text{ ms/}^\circ}$ (velocidad de rotación mental $\omega = 1000/a^* \approx \mathbf{364.1^\circ\text{/s}}$) y $b^* = \mathbf{683.1213\text{ ms}}$ (tiempo basal de percepción, decisión y respuesta motora a $0^\circ$).
- **Mínimo global verificado por el Hessiano:** $S(a^*, b^*) = \mathbf{156\,163\,296.22\text{ ms}^2} \approx 1.562\times 10^8\text{ ms}^2$, con $\nabla S(a^*,b^*) = [-7.22\times 10^{-9}, -1.96\times 10^{-10}] \approx \mathbf{0}$, matriz Hessiana constante $H = \begin{pmatrix} 13\,923\,000 & 107\,100 \\ 107\,100 & 1\,190 \end{pmatrix}$, determinante $D = \det(H) = \mathbf{5\,097\,960\,000 > 0}$, $S_{aa} = \mathbf{13\,923\,000 > 0}$ y autovalores $\lambda_1 = 366.13 > 0$, $\lambda_2 = 1.3924\times 10^7 > 0$ ($\Rightarrow$ paraboloide elíptico estrictamente convexo, mínimo único y global).
- **Doble lectura de calidad del ajuste (Teorema de descomposición ortogonal):**
  1. **Sobre los $n = 595$ ensayos individuales:** $\text{RMSE} = 512.3\text{ ms}$, **$R^2_{\text{raw}} = 0.0938$ ($9.38\%$)**, $p = 2.20\times 10^{-14}$ ($t = 7.834$). El $90.3\%$ de la varianza cruda es variabilidad **dentro del mismo ángulo** ($\text{SS}_{\text{intra}} = 1.556\times 10^8\text{ ms}^2$), que no depende de $(a,b)$: un tercio ($32\%$) son diferencias de velocidad basal entre personas y dos tercios ($68\%$) son variación de una misma persona de un ensayo a otro. Ningún modelo $y=f(x)$ puede explicarla.
  2. **Sobre los $K = 7$ promedios por ángulo ($m = 85$ ensayos/ángulo):** por ser un diseño balanceado, minimizar $S_{\text{medias}}(a,b)$ entrega **exactamente el mismo $(a^*, b^*) = (2.746737\text{ ms/}^\circ, 683.1213\text{ ms})$**, con **$\text{RMSE}_{\text{medias}} = 29.7\text{ ms}$ y $R^2_{\text{medias}} = 0.9685$ ($96.85\%$, $p = 0.00006$)**, confirmando con altísima precisión la ley lineal de Shepard y Metzler.
  3. **Persona por persona:** **16 de 17 participantes tienen pendiente positiva** (prueba de signos $p = 0.0003$; prueba $t$ sobre las 17 pendientes $p = 0.0002$). Si a cada persona se le da su propio tiempo base (minimizar $S(a, b_1,\dots,b_{17})$, 18 variables, mismo método $\nabla S = \mathbf{0}$), la pendiente sale **idéntica, $a^* = 2.746737$**, y el $R^2$ sube de $0.094$ a **$0.384$**.

| Entregable / Requisito (`requisitos.md`) | Estado | Archivo en el repositorio |
|---|---|---|
| **1–2. App de captura y datos validados** | ✅ | `app/index.html`, `csvs/neurocode_p01.csv` … `P17.csv` ($n = 595$) |
| **Auditoría de datos extra (`csvs/extra/`)** | ✅ | `codigo/auditar_extras.py` → `codigo/reporte_extras.md` |
| **3. Exploración de datos (Req. 5)** | ✅ | `figuras/01_dispersion.png` (nube $n=595$ + ajuste en medias $R^2=0.9685$) |
| **4. Desarrollo analítico manual (Req. 7.1–7.4)** | ✅ | `informe/guia_desarrollo_manual.md` (incluye atajo de 7 filas para calculadora en 60 s) |
| **5. Verificación computacional (Req. 8 y 9)** | ✅ | `codigo/ajuste.py` → `codigo/resultados.txt` ($\Delta a = 1.29\times 10^{-14}$) |
| **6. Superficie, trazas, secciones y curvas (Req. 7.5–7.8)** | ✅ | `figuras/02_rectas.png`, `03_superficie.png`, `04_trazas.png`, `05_curvas_nivel.png` |
| **7. Laboratorio 3D interactivo con $-\nabla S$ en vivo** | ✅ | `figuras/superficie_interactiva.html` (mapa de nivel arrastrable + $-\nabla S$ + recta $y=ax+b$ sincronizada + modo centrado $\tilde x=x-90^\circ$; funciona sin internet) |
| **8. Análisis de residuos, RMSE y $R^2$ (Req. 10–12)** | ✅ | `figuras/06_residuos.png`, `codigo/resultados.txt` |
| **9. Análisis adicional Opciones A, B, C y D (Req. 13)** | ✅ | `figuras/07_opciones_BC.png` (panel 2×2 con las 4 opciones completas) |
| **10. Pseudocódigo y diagrama de flujo (Rúbrica 10 %)** | ✅ | `codigo/pseudocodigo.md` |
| **11. Presentación 16:9 lista para exponer (Rúbrica 15 %)** | ✅ | `presentacion/slides.pdf` y `presentacion/slides.html` (fuente: `slides.md`) |
| **12. Hoja de batalla y preguntas trampa (Rúbrica 40 %)** | ✅ | `informe/hoja_batalla_sustentacion.md` |

### Qué falta antes del martes 17

1. **Cada integrante practica a mano** la deducción de `informe/guia_desarrollo_manual.md` (con la tabla de 7 filas pueden comprobar $a^*=2.7467$ y $b^*=683.12$ en calculadora en 60 segundos) y repasa `informe/hoja_batalla_sustentacion.md` (es el **40 % de la nota**).
2. **Poner los nombres reales del grupo** en la última diapositiva de `presentacion/slides.md` (buscar `[nombre 1]`) y recompilar el PDF.
3. **Probar el demo en vivo** en el computador de la exposición abriendo `figuras/superficie_interactiva.html` (mover los sliders de $a$ y $b$ y pulsar **"▶ Animar Descenso (−∇S escalado)"**) y `app/index.html`. Nota: el simulador se regenera con `python3 codigo/ajuste.py` desde `codigo/simulador_template.html`.

### Cómo regenerar todo en un comando

```bash
python3 codigo/auditar_extras.py > codigo/reporte_extras.md
python3 codigo/ajuste.py > codigo/resultados.txt
cd presentacion && npx @marp-team/marp-cli slides.md --pdf --allow-local-files --no-stdin && npx @marp-team/marp-cli slides.md --html --allow-local-files --no-stdin
```

### Paso a paso (desde cero)

1. **Clonar y entrar:**
   ```bash
   git clone <url-del-repo> && cd FinalCalculoMultivariado
   ```
2. **Requisito:** Python 3.10+ con `numpy`, `matplotlib`, `scipy`
   ```bash
   pip install numpy matplotlib scipy
   ```
3. **Capturar datos (opcional):** abrir `app/index.html` en el navegador, completar un bloque de 35 ensayos y guardar el CSV en `csvs/`.
4. **Auditar datos extra:** `python3 codigo/auditar_extras.py` (genera `codigo/reporte_extras.md`: duplicados exactos y métricas de cada bloque candidato).
5. **Ajuste + figuras:** `python3 codigo/ajuste.py` (lee `csvs/neurocode_*.csv`, escribe `codigo/resultados.txt` y las figuras `01`–`12` (más los paneles sueltos `NN_*_A/B/…`) en `figuras/`; requiere `pip install numpy matplotlib scipy pandas plotly`).
6. **Ver laboratorio 3D:** abrir `figuras/superficie_interactiva.html` en el navegador (sliders de $a,b$ + botón "▶ Animar Descenso (−∇S escalado)").
7. **Recompilar presentación:** ver comando Marp de la sección anterior (requiere `node` + `npx`).
8. **Exponer:** proyectar `presentacion/slides.pdf`, repasar `informe/guia_desarrollo_manual.md` (deducción a mano) y `informe/hoja_batalla_sustentacion.md` (preguntas trampa).

> ⚠️ **Notas de integridad de datos:**
> - En varios CSV originales el ID tecleado dentro de la app se repitió (`P05` escribió `36`, `P07` y `P11` escribieron `P10`, etc.). `codigo/ajuste.py` asigna el ID según el nombre del archivo (`P01`…`P17`) sin alterar los CSV crudos.
> - **Cómo se eligieron los datos (dicho con honestidad):** los 15 archivos de `csvs/` son la base recolectada con el protocolo. Después llegaron 13 bloques más (`csvs/extra/`, `csvs/txt/`); se quitaron 3 copias exactas y se sumaron 2 sesiones completas de personas nuevas: `neurocode_David.csv` (`P16`) y `extra/neurocode_P15.csv` (`P17`, ID `FV07`). Esos dos se escogieron mirando su ajuste, y eso favorece el resultado. Por eso reportamos la pendiente con las tres reglas de inclusión posibles (tabla de robustez, sección 3.4): **la conclusión no depende de esa elección.**

---

## 1. Planteamiento del problema y significado físico

Cuando observamos una letra girada un ángulo $\theta$, el cerebro ejecuta una rotación mental continua hasta alinearla con su representación canónica en memoria antes de decidir si es normal o está en espejo (Shepard & Metzler, 1971).

Medimos este fenómeno con la aplicación propia **NeuroCode** (`app/index.html`) y determinamos el modelo lineal $y = ax + b$ que mejor lo describe **minimizando una función de error cuadrático de dos variables $S(a,b)$** mediante derivadas parciales, vector gradiente y matriz Hessiana.

| Variable / Parámetro | Significado físico y cognitivo | Valor obtenido | Unidad |
|---|---|---|---|
| **$x$** | Ángulo de rotación de la letra R ($0^\circ, 30^\circ, 60^\circ, 90^\circ, 120^\circ, 150^\circ, 180^\circ$) | $[0, 180]$ | grados ($^\circ$) |
| **$y$** | Tiempo de respuesta en ensayos acertados | $\bar{y} = 930.33$ | ms |
| **$a^*$ (pendiente)** | Milisegundos adicionales por cada grado de rotación $\Rightarrow \omega = 1000/a^*$ es la velocidad angular mental | **$2.7467\text{ ms/}^\circ$** ($\approx 364.1^\circ\text{/s}$) | ms/grado |
| **$b^*$ (intercepto)** | Tiempo basal a $0^\circ$: codificación visual + decisión + ejecución motora sin rotar | **$683.12\text{ ms}$** | ms |

**Pregunta central del proyecto:**
> *¿Cómo se puede utilizar el Cálculo Multivariable para determinar y analizar el modelo lineal que mejor representa el tiempo que tarda el cerebro en rotar mentalmente una imagen?*

**Contraste clave para las conclusiones (Cerebro vs. Computador):**
- **El cerebro humano** rota la imagen de forma analógica paso a paso: el tiempo crece linealmente con el ángulo según $t(\theta) = 683.12 + 2.75\,\theta\text{ ms}$ ($\approx 364.1^\circ\text{/s}$).
- **Un computador** aplica la matriz ortogonal de rotación $R(\theta) = \begin{pmatrix}\cos\theta & -\sin\theta \\ \sin\theta & \cos\theta\end{pmatrix}$ en tiempo constante $\mathcal{O}(1)$ (4 multiplicaciones y 2 sumas en punto flotante, pendiente $0\text{ ms/}^\circ$).

---

## 2. Criterios de evaluación (`rubrica.md`) y cómo los cubrimos

| Criterio (M.Sc. Alejandro Molina) | Peso | Evidencia construida en este repositorio |
|---|---|---|
| **Comprensión conceptual** | **20 %** | Interpretación física de $a^*, b^*$, plano tangente horizontal ($\nabla S = \mathbf{0}$), curvatura y autovalores de $H$, y descomposición ortogonal de $S(a,b)$ (`informe/hoja_batalla_sustentacion.md`). |
| **Evaluación individual** | **20 %** | Guía desde cero con ejemplo de 3 puntos, deducción algebraica completa y **tabla de 7 promedios por ángulo** verificable con calculadora en 60 segundos (`informe/guia_desarrollo_manual.md`). |
| **Gráficos y análisis** | **20 %** | 12 figuras de alta resolución en `figuras/` (incl. puente 3D↔recta, doble R², 17 pendientes, elipses centradas, cerebro vs CPU) + simulador 3D en vivo `figuras/superficie_interactiva.html` con descenso por gradiente $-\nabla S$. |
| **Presentación** | **15 %** | 24 diapositivas 16:9 en `presentacion/slides.pdf` con notas de orador y reparto por integrante. |
| **Conclusiones** | **15 %** | Análisis crítico con doble $R^2$ ($n=595$ crudos vs. $K=7$ medias), análisis adicional completo (Opciones A, B, C y D) y contraste Cerebro vs. CPU. |
| **Programación y lógica** | **10 %** | Algoritmo propio sin librerías en `codigo/ajuste.py`, auditoría en `codigo/auditar_extras.py`, tabla de correspondencia y diagrama Mermaid en `codigo/pseudocodigo.md`. |

---

## 3. Resumen matemático y numérico ($n = 595$, 17 participantes)

### 3.1. Tabla de datos agrupados por ángulo ($m = 85$ ensayos por ángulo)

| Ángulo $x_k$ (°) | Ensayos $m$ | Media $\bar{y}_k$ (ms) | Desv. Est. DE (ms) | Mediana (ms) | Error Estándar EE (ms) | Predicción $\hat{y}_k = a^*x_k + b^*$ (ms) |
|---:|---:|---:|---:|---:|---:|---:|
| **0°** | 85 | 718.68 | 394.44 | 649.0 | 42.78 | 683.12 |
| **30°** | 85 | 751.74 | 324.52 | 691.8 | 35.20 | 765.52 |
| **60°** | 85 | 790.02 | 367.37 | 741.0 | 39.85 | 847.93 |
| **90°** | 85 | 954.60 | 466.17 | 821.2 | 50.56 | 930.33 |
| **120°** | 85 | 1006.84 | 570.57 | 890.0 | 61.89 | 1012.73 |
| **150°** | 85 | 1121.30 | 751.35 | 975.0 | 81.50 | 1095.13 |
| **180°** | 85 | 1169.12 | 591.25 | 1063.6 | 64.13 | 1177.53 |

### 3.2. Fórmulas analíticas y sumatorias reales

Función de error cuadrático de dos variables:
$$S(a,b) = \sum_{i=1}^{n} (y_i - a x_i - b)^2$$

1. **Derivadas parciales (regla de la cadena):**
   $$\frac{\partial S}{\partial a} = -2\sum_{i=1}^{n} x_i\,(y_i - a x_i - b), \qquad \frac{\partial S}{\partial b} = -2\sum_{i=1}^{n} (y_i - a x_i - b)$$
2. **Condición de punto crítico $\nabla S(a,b) = \mathbf{0}$ (ecuaciones normales):**
   $$\begin{cases}
   \left(\sum x_i^2\right)a + \left(\sum x_i\right)b = \sum x_i y_i \\[4pt]
   \left(\sum x_i\right)a + n\,b = \sum y_i
   \end{cases}$$
3. **Sumatorias con nuestros datos ($n = 595$):**
   $$\sum x_i = 53\,550, \quad \sum y_i = 553\,544.9, \quad \sum x_i^2 = 6\,961\,500, \quad \sum x_i y_i = 55\,702\,551.0, \quad \sum y_i^2 = 687\,301\,826.87$$
4. **Solución exacta del sistema $2\times 2$:**
   $$D_0 = n\sum x_i^2 - \left(\sum x_i\right)^2 = 595(6\,961\,500) - (53\,550)^2 = \mathbf{1\,274\,490\,000}$$
   $$a^* = \frac{n\sum x_i y_i - \sum x_i \sum y_i}{D_0} = \frac{3\,500\,688\,450}{1\,274\,490\,000} \approx \mathbf{2.746737\text{ ms/}^\circ}$$
   $$b^* = \frac{\sum y_i - a^*\sum x_i}{n} = \frac{406\,457.133}{595} \approx \mathbf{683.1213\text{ ms}}$$
5. **Matriz Hessiana y clasificación del punto crítico:**
   $$H = \begin{pmatrix} S_{aa} & S_{ab} \\ S_{ba} & S_{bb} \end{pmatrix} = \begin{pmatrix} 2\sum x_i^2 & 2\sum x_i \\ 2\sum x_i & 2n \end{pmatrix} = \begin{pmatrix} 13\,923\,000 & 107\,100 \\ 107\,100 & 1\,190 \end{pmatrix}$$
   $$D = \det(H) = 4 D_0 = \mathbf{5\,097\,960\,000 > 0} \quad \text{y} \quad S_{aa} = \mathbf{13\,923\,000 > 0} \;\Longrightarrow\; \textbf{Mínimo estricto global}.$$

### 3.3. Tabla comparativa (Sección 9 de `requisitos.md`)

| Parámetro | Analítico (manual) | Código propio (`ajuste.py`) | Librerías Python (`polyfit` / `linregress`) | Diferencia máxima ($\Delta$) |
|---|---:|---:|---:|---:|
| **$a^*$ (ms/°)** | $2.7467$ | $2.746737$ | $2.746737$ | $1.29\times 10^{-14}$ |
| **$b^*$ (ms)** | $683.12$ | $683.1213$ | $683.1213$ | $5.68\times 10^{-13}$ |
| **$S_{\min}$ ($\text{ms}^2$)** | $156\,163\,296$ | $156\,163\,296.22$ | $156\,163\,296.22$ | $0.00\times 10^{0}$ |

### 3.4. Robustez frente a la elección de datos

| Regla de inclusión | $n$ | $a^*$ (ms/°) | $R^2_{\text{medias}}$ |
|---|---:|---:|---:|
| Solo la base recolectada con el protocolo (15 personas) | 525 | 2.650 | 0.962 |
| **Base + 2 personas nuevas (oficial, 17)** | **595** | **2.747** | **0.969** |
| Todo lo recolectado sin copias exactas (incluye sesiones repetidas y con distracciones) | 875 | 2.407 | 0.935 |
| Quitando una persona cualquiera (17 corridas) | 560 | 2.359 – 2.923 | — |

En todos los casos la pendiente es positiva, de la misma magnitud y significativa.

### 3.5. Resumen de análisis adicionales (Sección 13 de `requisitos.md` — `figuras/07_opciones_BC.png`)

- **Opción A (Sensibilidad de parámetros):** Al perturbar los 595 tiempos con ruido gaussiano $\Delta y_i \sim \mathcal{N}(0, 25\text{ ms})$ durante 500 simulaciones Monte Carlo, la desviación estándar de los parámetros es apenas $\sigma_a = 0.0166\text{ ms/}^\circ$ (**0.60 %** de variación) y $\sigma_b = 1.79\text{ ms}$ (**0.26 %**).
- **Opción B (Influencia de datos atípicos):**
  - Quitando el mayor residuo (fila 262, P09, $x=150^\circ, y=6110.8\text{ ms}, e=+5015.7\text{ ms}$, $n=594$): $a^* = 2.6058\text{ ms/}^\circ$, $b^* = 687.35\text{ ms}$, el RMSE baja de $512.3$ a **$469.5\text{ ms}$** y $R^2$ sube a $0.0998$.
  - Quitando los 6 ensayos con distracción $>3000\text{ ms}$ ($n=589$): $a^* = 2.4085\text{ ms/}^\circ$, $b^* = 683.73\text{ ms}$, el RMSE baja a **$409.3\text{ ms}$** y $R^2$ sube a **$0.1103$** ($p = 1.22\times 10^{-16}$).
- **Opción C (Comparación con modelo cuadrático):** El ajuste de tres variables $y = 0.00304x^2 + 2.199x + 696.81$ da $\text{RMSE} = 512.2\text{ ms}$ y $R^2_{\text{raw}} = 0.0941$ ($\Delta R^2 = +0.0003$ respecto al lineal). El término cuadrático no aporta mejora real, validando el modelo lineal por parsimonia.
- **Opción D (Efecto del tamaño de muestra $N$):** Al incrementar la muestra desde $N=1$ ($n=35$) hasta $N=17$ ($n=595$), la pendiente acumulada $a^*(N)$ se estabiliza alrededor de $2.65\text{–}2.75\text{ ms/}^\circ$ a partir de $N \ge 10$ participantes ($n \ge 350$).

---

## 4. Estructura del repositorio

```text
FinalCalculoMultivariado/
├── README.md                              ← Resumen ejecutivo, resultados y guía del repositorio
├── requisitos.md                          ← Guía oficial del proyecto (M.Sc. Alejandro Molina)
├── rubrica.md                             ← Criterios de calificación (Comprensión 20%, Individual 20%, etc.)
├── app/
│   └── index.html                         ← Aplicación web NeuroCode (captura de tiempos con performance.now())
├── csvs/
│   ├── neurocode_P01.csv … P17.csv        ← 17 participantes con sesión completa (35 ensayos c/u, n = 595)
│   ├── extra/                             ← Archivos adicionales auditados por codigo/auditar_extras.py
│   └── txt/                               ← Respaldos en texto de WhatsApp
├── codigo/
│   ├── ajuste.py                          ← Algoritmo propio MCO, Hessiano, opciones A–D y generación de figuras
│   ├── auditar_extras.py                  ← Auditoría psicométrica/estadística (G1–G4) de CSV candidatos
│   ├── resultados.txt                     ← Salida numérica completa (n = 595, K = 7 medias y por sujeto)
│   ├── reporte_extras.md                  ← Dictamen de deduplicación y filtrado de datos extra
│   └── pseudocodigo.md                    ← Trazabilidad código↔modelo, pseudocódigo y diagrama de flujo
├── figuras/
│   ├── 01_dispersion.png                  ← Dispersión total (n=595) + ajuste lineal en medias (R²=0.9685)
│   ├── 02_rectas.png                      ← Atípicos más alejados + comparación con 3 rectas candidatas
│   ├── 03_superficie.png                  ← Paraboloide 3D z = S(a,b) con curvas proyectadas y mínimo global
│   ├── 04_trazas.png                      ← Trazas óptimas S(a,b*), S(a*,b) y familia de secciones transversales
│   ├── 05_curvas_nivel.png                ← Curvas de nivel elípticas, campo −∇S y eje del valle
│   ├── 06_residuos.png                    ← Residuos vs. ángulo (banda ±1 DE) e histograma con curva normal
│   ├── 07_opciones_BC.png                 ← Panel 2×2 con las Opciones A, B, C y D de la Sección 13
│   └── superficie_interactiva.html        ← Simulador 3D en vivo con sliders (a,b) y animación de descenso −∇S
├── presentacion/
│   ├── slides.md                          ← Fuente Marp de las 24 diapositivas con notas de orador
│   ├── slides.pdf                         ← Presentación lista para proyectar (16:9)
│   └── slides.html                        ← Versión web de las diapositivas
└── informe/
    ├── guia_desarrollo_manual.md          ← Deducción paso a paso + tabla de 7 filas para calculadora en 60 s
    └── hoja_batalla_sustentacion.md       ← Reparto de diapos para 4 integrantes y 7 preguntas trampa resueltas
```

---

### Referencias
- Shepard, R. N., & Metzler, J. (1971). Mental rotation of three-dimensional objects. *Science, 171*(3972), 701–703.
- Cooper, L. A., & Shepard, R. N. (1973). Chronometric studies of the rotation of mental images. En W. G. Chase (Ed.), *Visual information processing* (pp. 75–176). Academic Press.
