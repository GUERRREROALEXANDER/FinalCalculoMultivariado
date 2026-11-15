---
marp: true
theme: default
size: 16:9
paginate: true
math: katex
title: NeuroCode - Rotación mental y mínimos cuadrados
lang: es
style: |
  :root {
    --ink: #14213d;
    --accent: #d9480f;
    --accent2: #1864ab;
    --muted: #5b6472;
    --soft: #f1f3f7;
    --line: #e2e6ec;
  }
  section {
    font-family: 'Inter','Noto Sans','DejaVu Sans',sans-serif;
    background: linear-gradient(to bottom, #ffffff 0%, #ffffff 88%, #f6f7f9 100%);
    color: var(--ink);
    font-size: 26px;
    line-height: 1.32;
    padding: 36px 56px 46px 56px;
    justify-content: flex-start;
  }
  section::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 8px;
    background: linear-gradient(90deg, var(--accent) 0 32%, var(--ink) 32% 100%);
  }
  section::after { color: var(--muted); font-size: 17px; }
  section h1 {
    font-size: 36px; line-height: 1.15; color: var(--ink);
    border-left: 9px solid var(--accent); padding-left: 16px;
    margin: 0 0 14px 0; font-weight: 800;
  }
  section h2 { font-size: 27px; margin: 0 0 6px 0; }
  section p, section li { font-size: 26px; margin: 4px 0; }
  section ul, section ol { margin: 6px 0 6px 24px; padding: 0; }
  section li { margin: 2px 0; }
  section strong { color: var(--accent); }
  section em { color: var(--muted); font-style: normal; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: start; }
  .cols.mid { align-items: center; }
  .cols.wide-left { grid-template-columns: 1.28fr 1fr; }
  .center { text-align: center; }
  .big { font-size: 64px; font-weight: 800; color: var(--accent); line-height: 1; }
  .big.blue { color: var(--accent2); }
  .kpi { font-size: 21px; color: var(--muted); }
  .badge { display: inline-block; font-size: 20px; font-weight: 700; color: #fff; background: var(--ink); border-radius: 999px; padding: 2px 14px; margin-right: 8px; }
  .badge.hot { background: var(--accent); }
  .badge.cool { background: var(--accent2); }
  .card { border: 2px solid var(--line); border-left: 8px solid var(--accent2); border-radius: 12px; padding: 10px 16px; background: #fbfcfd; }
  .card.hot { border-left-color: var(--accent); background: #fff6f0; }
  .card h2 { font-size: 24px; margin: 0 0 4px 0; color: var(--ink); }
  img { display: block; margin: 0 auto; }
  table { font-size: 21px; margin: 8px auto; border-collapse: collapse; line-height: 1.25; }
  th { background: var(--ink); color: #fff; padding: 5px 12px; font-size: 20px; }
  td { padding: 5px 12px; border-bottom: 2px solid var(--soft); text-align: center; }
  td:first-child, th:first-child { text-align: left; }
  .flow { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 14px 8px; font-size: 22px; margin-top: 14px; }
  .box { border: 2px solid var(--ink); border-radius: 10px; padding: 6px 12px; background: var(--soft); text-align: center; }
  .box.key { border-color: var(--accent); background: #fff3ec; font-weight: 700; }
  .arr { color: var(--accent); font-size: 22px; font-weight: 800; }
  .tiny { font-size: 20px; color: var(--muted); }
  .two { columns: 2; column-gap: 28px; }
  section.lead { justify-content: center; text-align: left; }
  section.lead h1 { font-size: 60px; border-left-width: 12px; }
  section.lead p { font-size: 28px; }
  section.demo p { font-size: 27px; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# NeuroCode: ¿a qué velocidad gira tu cerebro?

¿Cómo usa el Cálculo Multivariable la **mejor recta** del tiempo de rotación mental?

*Proyecto final de Cálculo Multivariable · Universidad Cooperativa de Colombia (Pasto) · 17 de noviembre de 2026*

<!--
Buenas. Medimos cuánto tarda el cerebro en girar una letra R en la mente y buscamos la recta que mejor lo describe. La herramienta es cálculo de varias variables: parciales, gradiente y Hessiano. Todo con datos reales, nada inventado.
-->

---

# Datos reales: ángulo contra tiempo

<div class="cols mid">
<div>

| Variable | Significado | Unidad |
|---|---|---|
| **x** | ángulo de la letra R | grados |
| **y** | tiempo de respuesta (aciertos) | ms |

<span class="badge hot">n = 525</span> 15 sujetos × 7 ángulos × 5 ensayos
<span class="badge">m = 75 / ángulo</span>

Diseño balanceado: cada ángulo pesa igual.

</div>
<div>

| $\theta$ | $\bar y$ (ms) |
|---|---|
| $0^\circ$ | **696.8** |
| $30^\circ$ | **727.1** |
| $60^\circ$ | **752.8** |
| $90^\circ$ | **904.9** |
| $120^\circ$ | **973.5** |
| $150^\circ$ | **1088.6** |
| $180^\circ$ | **1124.2** |

<p class="tiny center">Medias por ángulo · m = 75 ensayos c/u</p>

</div>
</div>

<!--
Cada participante vio una R girada 0, 30, 60, 90, 120, 150 o 180° y respondió si era normal o espejo. Solo aciertos: 5 datos por ángulo, 35 por persona, 525 total. La tabla muestra medias crecientes con el ángulo, indicio de tendencia lineal.
-->

---

# El tiempo sube con el ángulo: la recta sirve

![h:360](../figuras/01_dispersion.png)

Media **696.8 ms** a $0^\circ$ → **1124.2 ms** a $180^\circ$ · gran dispersión, tendencia creciente ⇒ modelo $y=ax+b$ razonable.

<!--
Cada punto es un ensayo. La media sube de 696.8 a 1124.2 ms. Hay mucha dispersión entre personas, pero la tendencia creciente es clara, así que probamos y = a·x + b.
-->

---

# Medimos qué tan mala es cada recta: S(a, b)

$$S(a,b)=\sum_{i=1}^{525}\big(y_i-\textcolor{#d9480f}{a}\,x_i-\textcolor{#d9480f}{b}\big)^2$$

![h:330](../figuras/02_rectas.png)

Al cuadrado: sin cancelaciones, castiga errores grandes y es derivable.

<!--
Cada pareja (a,b) es una recta distinta y S mide su error total. El cuadrado evita cancelaciones, castiga errores grandes y permite derivar. Las rectas punteadas tienen S mayor que la óptima.
-->

---

# En el mínimo, el gradiente es cero

$$\frac{\partial S}{\partial a}=-2\sum x_i\,(y_i-a x_i-b) \qquad \frac{\partial S}{\partial b}=-2\sum (y_i-a x_i-b)$$

$$\nabla S=\mathbf{0}\Rightarrow\begin{cases}\textcolor{#d9480f}{a}\sum x_i^2+\textcolor{#d9480f}{b}\sum x_i=\sum x_i y_i\\\textcolor{#d9480f}{a}\sum x_i+\textcolor{#d9480f}{b}\,n=\sum y_i\end{cases}$$

Plano tangente **horizontal**: no se puede bajar más.

<!--
Derivamos con regla de la cadena tratando la otra variable como constante. Igualar el gradiente a cero da las ecuaciones normales: 2 ecuaciones, 2 incógnitas. Geométricamente, el plano tangente a z=S(a,b) es horizontal.
-->

---

# Resultado: a\* = 2.65 ms/° y b\* = 656.91 ms

<p class="tiny center">n = 525 · Σx = 47 250 · Σy = 470 089.6 · Σx² = 6 142 500 · Σxy = 47 316 603</p>

$$a^*=\frac{n\sum xy-\sum x\sum y}{n\sum x^2-(\sum x)^2}=\frac{2\,629\,482\,975}{992\,250\,000}\approx\textcolor{#d9480f}{2.6500}$$

$$b^*=\frac{\sum y-a^*\sum x}{n}\approx\textcolor{#d9480f}{656.91}\qquad S_{\min}\approx 142\,057\,260$$

<!--
Sumatorias reales verificables con calculadora. Pendiente 2.65 ms por grado, intercepto 656.91 ms o tiempo base sin rotación. Error mínimo ≈ 142 millones de ms².
-->

---

# El Hessiano confirma: mínimo global

$$\nabla S(a^*,b^*)=[1.86\times 10^{-9},\,7.28\times 10^{-12}]\approx\mathbf{0}\qquad H=\begin{pmatrix}12\,285\,000 & 94\,500\\ 94\,500 & 1\,050\end{pmatrix}$$

$$D=\det H=3.969\times 10^9>0 \quad S_{aa}=1.2285\times 10^7>0 \quad \lambda_1=323.06>0,\;\lambda_2=1.2286\times 10^7>0$$

**H constante** ⇒ S es paraboloide convexo: mínimo único y global.

<!--
Verificación numérica del gradiente casi cero. D>0 y S_aa>0 más ambos valores propios positivos confirman mínimo. Como H no depende de a ni b, es global: imposible máximo o silla.
-->

---

# S es un valle con un solo fondo

<div class="cols mid">
<div>

![h:410](../figuras/03_superficie.png)

</div>
<div>

![h:410](../figuras/05_curvas_nivel.png)

</div>
</div>

Elipses **inclinadas** ($S_{ab}=2\Sigma x=94\,500>0$) y **alargadas** ($\lambda_2/\lambda_1\approx 38\,029$); $-\nabla S$ apunta al mínimo.

<!--
Izquierda: superficie z=S(a,b) con mínimo marcado. Derecha: curvas de nivel elípticas centradas en (a*,b*) con campo −gradiente apuntando al centro. Se inclinan por el término cruzado positivo y se alargan porque la superficie es ~38 mil veces más empinada en a que en b.
-->

---

# Cada corte por el óptimo es una parábola

![h:380](../figuras/04_trazas.png)

**Trazas óptimas** $S(a,b^*)$, $S(a^*,b)$ con vértice en el óptimo · **Secciones** $S(a,b_0)$, $S(a_0,b)$ paralelas desplazadas hacia arriba.

<!--
Fijar b en b* y mover a da parábola con vértice en a*, igual para a*. Las secciones con b0 o a0 fijos son parábolas paralelas más altas. Visualmente prueba que el fondo es único.
-->

---

# El código replica el cálculo a mano

<div class="flow">
<div class="box">Cargar CSV</div><span class="arr">→</span>
<div class="box">n, Σx, Σy, Σx², Σxy</div><span class="arr">→</span>
<div class="box key">a*, b*</div><span class="arr">→</span>
<div class="box">S<sub>mín</sub></div><span class="arr">→</span>
<div class="box">H, det H</div><span class="arr">→</span>
<div class="box key">¿det H > 0 y S<sub>aa</sub> > 0?</div><span class="arr">→</span>
<div class="box">Residuos, RMSE, R²</div><span class="arr">→</span>
<div class="box">vs. librerías</div>
</div>

Algoritmo propio **sin regresión de librería**; `polyfit` / `linregress` solo verifican.

<!--
Diagrama de codigo/ajuste.py: cada caja es un paso del desarrollo manual. Primero sumatorias, luego a* y b*, error mínimo, Hessiano y criterio de segunda derivada, residuos y comparación con numpy y scipy.
-->

---

# Nuestro código y las librerías coinciden

| Parámetro | Manual | Código propio | polyfit / linregress | Δ máx |
|---|---|---|---|---|
| a | 2.6500 | 2.650021 | 2.650021 | 3.55e-15 |
| b | 656.91 | 656.9069 | 656.9069 | 0.00e+00 |
| S mín | 142 057 260 | 142 057 259.72 | 142 057 259.72 | 0.00e+00 |

Tres vías, mismo punto: validación exacta a nivel de redondeo.

<!--
Manual, algoritmo propio y numpy/scipy coinciden hasta 1e-15. La diferencia máxima es ruido de punto flotante: el cálculo analítico queda verificado.
-->

---

# Residuos centrados en 0, más dispersos con el ángulo

![h:380](../figuras/06_residuos.png)

Media $e\approx -1.4\times 10^{-14}\approx 0$ · mayor residuo fila 262 ($x=150^\circ$, $e=\mathbf{5056.4}$ ms) · leve abanico: heterocedasticidad.

<!--
Residuos centrados en cero, mayoría entre −1000 y 1000 ms con cola alta. La dispersión crece con el ángulo y el extremo es la fila 262. No hay patrón curvo sistemático: el lineal es aceptable.
-->

---

# Calidad: dos caras de la misma recta

<div class="cols">
<div class="card hot">

## Ensayos crudos · n = 525

**RMSE = 520.2 ms**
**$R^2 = 0.0854$** ($p=8.4\times 10^{-12}$)

Pendiente real pero solo 8.5 %: heterogeneidad basal entre 15 sujetos.

</div>
<div class="card">

## Promedios · K = 7 (m = 75)

**Mismos** $a^*=2.6500$, $b^*=656.91$
**RMSE = 31.6 ms · $R^2 = 0.9619$** ($p=0.0001$)

96.2 % de la tendencia media: la recta describe el efecto rotación.

</div>
</div>

<!--
Misma recta en ambas escalas por diseño balanceado. En ensayos el ruido entre personas hunde R² aunque p es diminuta; en medias el ruido se promedia y R² llega a 96.2 %. Por eso el efecto es real y la recta es correcta para la tendencia.
-->

---

# Robustez: sensible, estable y lineal basta

<div class="cols wide-left">
<div>

![h:440](../figuras/07_opciones_BC.png)

</div>
<div>

**A Sensib.:** ±25 ms ⇒ $\sigma_a=0.019$ (0.72 %).
**B Atípicos:** sin f.262 $a^*=2.49$, RMSE 471; sin >3 s (n=519) $a^*=2.26$, $R^2=0.1024$.
**C Cuadr.:** $y=0.0041x^2+1.92x+675.2$, $R^2=0.0860$ ($\Delta=+0.0006$).
**D N:** $a^*(N)$ converge desde $N\ge 10$ ($n\ge 350$).

</div>
</div>

<!--
Las cuatro opciones confirman la recta: A muestra baja sensibilidad, B que un atípico mueve poco, C que el cuadrático no aporta y D que con 10+ participantes el ajuste se estabiliza.
-->

---

# Cerebro: paso a paso · Computador: de golpe

<div class="cols">
<div class="card hot">

## Cerebro

$$t=\textcolor{#d9480f}{656.91}+\textcolor{#d9480f}{2.65}\,\theta$$

≈ **377 °/s**: gira la imagen mental por etapas (Shepard–Metzler).

</div>
<div class="card">

## Computador

$$R(\theta)=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}$$

Tiempo **constante**: multiplica la matriz, sin costo por ángulo.

</div>
</div>

<!--
El cerebro tarda 2.65 ms más por grado, unos 377 °/s: rota paso a paso. Un computador aplica la matriz y tarda lo mismo siempre. Mismo problema, dos estrategias.
-->

---

# Limitaciones: pocas personas y mucha variación

- Solo **15** participantes: no generalizable.
- Pendiente por persona de **−0.08** (P01, sin efecto) a **8.95 ms/°** (P09).
- Atípicos por distracción (fila 262: 5056 ms).
- $R^2_{\text{raw}}=0.0854$: falta modelar el nivel basal por sujeto.

<!--
Con 15 personas y pendientes tan dispares el modelo global es promedio. Los atípicos y el R² bajo piden un modelo mixto por sujeto en trabajo futuro.
-->

---

<!-- _class: demo -->

# Demo en vivo

Abre la superficie interactiva: [`figuras/superficie_interactiva.html`](../figuras/superficie_interactiva.html)

O prueba la app de captura: [`app/index.html`](../app/index.html)

<!--
Giramos la superficie en el navegador hasta ver el fondo del valle en (a*,b*). Si el profesor quiere, hacemos la prueba en la app NeuroCode con doble clic.
-->

---

<!-- _class: lead -->

# Gracias: ¿preguntas?

Integrantes: **[nombre 1] · [nombre 2] · [nombre 3] · [nombre 4]**

<!--
Agradecemos al profesor. Cada integrante puede derivar las parciales y el Hessiano en el tablero. Quedamos atentos a preguntas.
-->
