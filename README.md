# 🧠 NeuroCode — ¿A qué velocidad gira tu cerebro?

**Proyecto final de Cálculo Multivariable · Ingeniería de Software · Universidad Cooperativa de Colombia (Pasto)**
**Entrega: martes 17 de noviembre de 2026**

> Regresión lineal y optimización con funciones de dos variables aplicada a un experimento real de neurociencia: la **rotación mental**.

---

## 0. Estado y pasos a seguir (actualizado 15 nov)

**Resultado con los 15 participantes (n = 525):** $a^* = 2.6500\text{ ms/}^\circ$ ($\approx 377.4\text{ }^\circ\text{/s}$), $b^* = 656.91\text{ ms}$, $S_{\min} \approx 1.421\times 10^8\text{ ms}^2$, Hessiano constante y definido positivo ($\det H = 3.969\times 10^9 > 0, S_{aa} = 1.2285\times 10^7 > 0 \Rightarrow$ mínimo global único).
- **En los 525 ensayos crudos:** $p = 8.40\times 10^{-12}$, $\text{RMSE} = 520.2\text{ ms}$, $R^2_{\text{raw}} = 0.0854$ (por la variación de velocidad base entre las 15 personas).
- **En los $K = 7$ promedios por ángulo (diseño balanceado, $75$ ensayos/ángulo):** por descomposición ortogonal de la suma de cuadrados, minimizar sobre las 7 medias da **exactamente el mismo $(a^*, b^*) = (2.6500\text{ ms/}^\circ, 656.91\text{ ms})$**, con **$\text{RMSE}_{\text{medias}} = 31.6\text{ ms}$ y $R^2_{\text{medias}} = 0.9619$ ($96.2\%$, $p = 0.0001$)**, replicando la ley lineal de Shepard y Metzler (1971).

| Paso | Estado | Dónde está |
|---|---|---|
| 1-2 App y datos | ✅ | `app/`, `csvs/` (15 archivos) |
| 3 Exploración | ✅ | `figuras/01_dispersion.png` (nube completa + ajuste en medias $R^2=0.962$) |
| 4 Desarrollo manual | ⏳ **cada integrante a mano** | `informe/guia_desarrollo_manual.md` (incluye tabla de 7 filas para calculadora en 60 s) |
| 5 Python | ✅ | `codigo/ajuste.py` → `codigo/resultados.txt` |
| 6 Gráficas | ✅ | `figuras/` (7 PNG + `superficie_interactiva.html` con trazas 3D) |
| 7 Residuos, RMSE, R² | ✅ | `figuras/06_residuos.png`, `resultados.txt` |
| 8 Análisis adicional (A, B, C y D) | ✅ | `figuras/07_opciones_BC.png` (panel 2×2 con las 4 opciones de la guía) |
| 9 Pseudocódigo y diagrama | ✅ | `codigo/pseudocodigo.md` |
| 10 Blender | ⏳ opcional | — |
| 11 Presentación | ✅ (el profe no pide informe) | `presentacion/slides.pdf` (fuente: `slides.md`) |
| 12 Defensa individual | ⏳ **ensayar** | Parte 3 de `informe/guia_desarrollo_manual.md` |

### Qué falta antes del martes 17

1. **Cada integrante hace el paso 4 a mano**, sin mirar la guía, y ensaya las 10 preguntas del paso 12 en voz alta (es el 40 % de la nota).
2. **Poner los nombres** en la última diapositiva (`presentacion/slides.md`, buscar `[nombre 1]`) y **repartir quién explica qué**.
3. **Probar el demo** en el computador de la exposición: `app/index.html` y `figuras/superficie_interactiva.html` (los enlaces del PDF son relativos; si el PDF se abre suelto, abrirlos aparte).
4. *(Opcional)* Exportar el diagrama de flujo a PNG, análisis de sensibilidad (opción A), Blender.

### Cómo regenerar todo

```bash
python3 codigo/ajuste.py > codigo/resultados.txt     # necesita numpy, scipy, pandas, matplotlib, plotly
cd presentacion && npx @marp-team/marp-cli slides.md --pdf --html --allow-local-files --no-stdin
```

Agregar más participantes = soltar el CSV en `csvs/` y volver a correr.

> ⚠️ **Códigos de participante:** en varios CSV el id tecleado en la app no coincide con el nombre del archivo (`neurocode_P05.csv` dice `36`, `P07` y `P11` dicen `P10`, `P12` dice `P11`, `P14` dice `P12`). El script usa **el nombre del archivo** como id. Los CSV no se editan.

---

## 1. ¿De qué trata el proyecto?

Cuando ves una letra girada, tu cerebro la "rota" mentalmente para reconocerla. El experimento clásico de Shepard y Metzler (1971) mostró que **el tiempo de respuesta crece en línea recta con el ángulo de rotación**: el cerebro gira la imagen a velocidad constante.

Medimos ese fenómeno con una app propia y encontramos la recta que mejor lo describe **minimizando una función de error de dos variables** con derivadas parciales, gradiente y Hessiano.

| Variable | Significado | Unidad |
|---|---|---|
| **x** | Ángulo de rotación de la letra R (0°, 30°, 60°, 90°, 120°, 150°, 180°) | grados |
| **y** | Tiempo que tarda la persona en responder correctamente | ms |
| **a\*** (pendiente) | Milisegundos que tarda el cerebro por cada grado de rotación → $1000/a^*$ = velocidad de rotación mental (°/s) | ms/grado |
| **b\*** (intercepto) | Tiempo base: ver la letra, decidir y presionar la tecla (sin rotación) | ms |

**Pregunta central:**
> ¿Cómo se puede utilizar el Cálculo Multivariable para determinar y analizar el modelo lineal que mejor describe el tiempo que tarda el cerebro en rotar mentalmente una imagen?

**Idea para la conclusión:** el cerebro rota la imagen *paso a paso* (el tiempo crece con el ángulo), mientras que un computador la rota de un solo golpe con una **matriz de rotación** (tiempo constante). Mismo problema, dos estrategias distintas.

---

## 2. Cómo se evalúa (y dónde ponemos el esfuerzo)

| Criterio | Peso | Qué necesitamos |
|---|---|---|
| Comprensión conceptual | 20 % | Entender el problema e interpretar a\*, b\*, ∇S y el Hessiano |
| Evaluación individual | 20 % | **Cada integrante** debe poder hacer el desarrollo manual y responder preguntas |
| Gráficos y análisis | 20 % | Superficie, trazas, curvas de nivel, residuos, bien interpretados |
| Presentación | 15 % | Claridad, diseño, comunicación oral |
| Conclusiones | 15 % | Reflexión crítica con RMSE, R² y análisis adicional |
| Programación y lógica | 10 % | Algoritmo propio, pseudocódigo / diagrama de flujo, relación código–modelo |

⚠️ **El 40 % depende de que TODOS dominemos el cálculo.** No sacrifiquemos estudio por efectos visuales.

---

## 3. Cronograma

| Día | Tareas | Estado |
|---|---|---|
| **Sáb 14 nov** | App de captura (`app/index.html`) · Recolección de datos | ✅ App lista · ⏳ Datos |
| **Dom 15 nov** | Desarrollo manual · Script de Python · Gráficas · Análisis adicional | ⏳ |
| **Lun 16 nov** | Diagrama de flujo · Presentación · Blender (opcional) · Informe · **Ensayo de la defensa** | ⏳ |
| **Mar 17 nov** | 🎤 Entrega y sustentación | ⏳ |

---

## 4. Plan paso a paso

### ✅ Paso 1 — App de captura de datos (LISTO)
- [x] `app/index.html`: un solo archivo, se abre con doble clic, no necesita instalación ni servidor.
- [x] Mide el tiempo con `performance.now()`, guarda solo aciertos y descarga un CSV.

### ⏳ Paso 2 — Recolección de datos (protocolo)
1. Abrir `app/index.html` en **el mismo computador** para todos (para que el teclado y la pantalla no cambien los tiempos).
2. Escribir un código de participante (`P01`, `P02`, …). **No usar nombres reales.**
3. Hacer los **5 ensayos de práctica** (no se guardan).
4. Medición: aparece una **+** y luego la letra **R** girada → presionar **F** si es normal o **J** si está en espejo.
   - Solo se guardan los **aciertos**. Los errores, las respuestas anticipadas (< 150 ms) y las de más de 7 s se repiten automáticamente.
   - Se obtienen **5 datos válidos por ángulo × 7 ángulos = 35 datos** por participante.
   - Los tiempos > 3 s se marcan como `posible_atipico` (útil para el análisis de la opción B).
5. Responder **concentrado, rápido y sin equivocarse**, en un lugar sin distracciones.
6. Al terminar, pulsar **"Descargar CSV (todos)"** y guardar el archivo en `datos/`.

> 🚫 **No inventar ni modificar datos.** Si alguien se distrajo de verdad, ese dato se deja y se analiza; no se provoca a propósito.

**Formato del CSV:**
```
participante,ensayo,angulo_grados,direccion,espejo,tiempo_ms,posible_atipico,fecha_hora
```

### ⏳ Paso 3 — Exploración de los datos
- [ ] Tabla de datos con unidades.
- [ ] Diagrama de dispersión (x = ángulo, y = tiempo).
- [ ] Discutir si un modelo $y = ax + b$ es razonable.

### ⏳ Paso 4 — Desarrollo analítico manual ✍️ (lo hace cada uno a mano)
Función de error cuadrático:

$$S(a,b) = \sum_{i=1}^{n} (y_i - a x_i - b)^2$$

**4.1 Derivadas parciales** (regla de la cadena):

$$\frac{\partial S}{\partial a} = -2\sum_{i=1}^{n} x_i\,(y_i - a x_i - b) \qquad \frac{\partial S}{\partial b} = -2\sum_{i=1}^{n} (y_i - a x_i - b)$$

**4.2 Punto crítico** $\nabla S(a,b) = \mathbf{0}$ → ecuaciones normales:

$$a\sum x_i^2 + b\sum x_i = \sum x_i y_i \qquad a\sum x_i + b\,n = \sum y_i$$

**4.3 Solución del sistema 2×2:**

$$a^* = \frac{n\sum x_i y_i - \sum x_i \sum y_i}{n\sum x_i^2 - \left(\sum x_i\right)^2} \qquad b^* = \frac{\sum y_i - a^*\sum x_i}{n}$$

**4.4 Hessiano:**

$$H = \begin{pmatrix} S_{aa} & S_{ab} \\ S_{ba} & S_{bb} \end{pmatrix} = \begin{pmatrix} 2\sum x_i^2 & 2\sum x_i \\ 2\sum x_i & 2n \end{pmatrix}$$

$$D = \det H = 4\left[n\sum x_i^2 - \left(\sum x_i\right)^2\right] > 0 \quad \text{y} \quad S_{aa} = 2\sum x_i^2 > 0 \;\Rightarrow\; \textbf{mínimo}$$

Como $H$ es **constante** (no depende de $a$ ni de $b$) y es definida positiva, $S$ es un **paraboloide convexo**: el mínimo es **global** y único.

- [ ] Calcular las sumatorias con nuestros datos: $n,\ \sum x_i,\ \sum y_i,\ \sum x_i^2,\ \sum x_i y_i$.
- [ ] Resolver a mano $a^*$, $b^*$ y $S(a^*, b^*)$.
- [ ] Calcular $H$ y $D$ con los números reales.

### ⏳ Paso 5 — Programa en Python (`codigo/`)
- [ ] Cargar el CSV.
- [ ] **Algoritmo propio** (sin librerías de regresión): sumatorias → $a^*$, $b^*$ → $S(a^*, b^*)$ → Hessiano.
- [ ] Verificación numérica del Hessiano (determinante y valores propios > 0).
- [ ] Comparación con librería (`numpy.polyfit` / `scipy.stats.linregress`).
- [ ] Tabla comparativa:

| Parámetro | Analítico (manual) | Código propio | Biblioteca Python | Diferencia máxima |
|---|---|---|---|---|
| a | | | | Δa |
| b | | | | Δb |
| S mín | | | | ΔS |

### ⏳ Paso 6 — Interpretación geométrica (gráficas)
- [ ] Datos + recta óptima + **3 rectas con otros (a, b)** para comparar.
- [ ] **Superficie** $z = S(a,b)$ con el mínimo marcado.
- [ ] **Trazas**: $S(a, b^*)$ y $S(a^*, b)$ (parábolas con vértice en el óptimo).
- [ ] **Secciones transversales** de la superficie.
- [ ] **Curvas de nivel** (elipses) con $(a^*, b^*)$ en el centro.
- [ ] Superficie 3D **interactiva** (HTML con Plotly) para la exposición.

### ⏳ Paso 7 — Calidad del ajuste
- [ ] Residuos $e_i = y_i - (a^* x_i + b^*)$: gráfico $e_i$ vs. $x_i$ + **histograma**.
- [ ] Analizar: ¿centrados en 0? ¿patrón o curva? ¿la dispersión crece con el ángulo? ¿atípicos?
- [ ] **RMSE** (en ms) y **R²**, interpretados para este experimento (no solo "es bueno/malo").

### ⏳ Paso 8 — Análisis adicional (hacemos varios)
- [ ] **Opción B:** influencia de un dato (quitar el atípico y recalcular).
- [ ] **Opción C:** comparar con un modelo cuadrático $y = ax^2 + bx + c$.
- [ ] *(Opcional)* **Opción A:** sensibilidad a pequeños cambios en los datos.

### ⏳ Paso 9 — Programación y lógica
- [ ] **Pseudocódigo** del algoritmo de ajuste.
- [ ] **Diagrama de flujo** (relación entre cada paso del código y cada paso del cálculo).

### ⏳ Paso 10 — Visuales (opcional, si sobra tiempo)
- [ ] Render en **Blender**: superficie de error como holograma + cerebro / letra R girando.

### ⏳ Paso 11 — Presentación e informe
- [ ] Diapositivas: problema → datos → cálculo manual → geometría → código → residuos → conclusiones.
- [ ] Demo en vivo: el profesor hace la prueba y ve su punto en la gráfica.
- [ ] Informe en Word (APA 7).

### ⏳ Paso 12 — Preparar la defensa individual 🎤
Cada integrante debe poder responder **sin leer**:
1. ¿Por qué se eleva el error al cuadrado y no se suma directamente?
2. Deriva $\partial S/\partial a$ y $\partial S/\partial b$ en el tablero.
3. ¿Qué significa geométricamente que $\nabla S = \mathbf{0}$? (plano tangente horizontal)
4. ¿Por qué el Hessiano es constante en este problema?
5. ¿Cómo sabes que es un mínimo y no un máximo o un punto de silla?
6. ¿Por qué las curvas de nivel son elipses y qué indica que sean alargadas?
7. ¿Qué significan $a^*$ y $b^*$ en el experimento?
8. ¿Qué te dicen los residuos sobre si el modelo lineal es adecuado?
9. ¿Qué significan el RMSE y el R² obtenidos?
10. ¿Qué limitaciones tiene el modelo?

---

## 5. Estructura del repositorio

```
FinalCalculoMultivariado/
├── README.md          ← este plan
├── app/
│   └── index.html     ← app de captura NeuroCode
├── csvs/              ← CSV recolectados
├── codigo/            ← scripts de Python (regresión, gráficas, análisis)
├── figuras/           ← gráficas exportadas
├── blender/           ← renders y escenas (opcional)
├── presentacion/      ← diapositivas
└── informe/           ← documento final
```

---

## 6. Reparto de tareas

| Tarea | Responsable |
|---|---|
| App de captura | ✅ Hecha |
| Recolección de datos | Todos |
| Desarrollo manual | **Todos** (cada uno lo debe saber hacer) |
| Python y gráficas | Por asignar |
| Diagrama de flujo y pseudocódigo | Por asignar |
| Blender | Por asignar |
| Presentación e informe | Por asignar |

---

### Referencias
- Shepard, R. N., & Metzler, J. (1971). Mental rotation of three-dimensional objects. *Science, 171*(3972), 701–703.
- Cooper, L. A., & Shepard, R. N. (1973). Chronometric studies of the rotation of mental images. En W. G. Chase (Ed.), *Visual information processing* (pp. 75–176). Academic Press.
