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
    --good: #2b8a3e;
    --muted: #4b5563;
    --soft: #f1f3f7;
    --line: #d5dae3;
  }
  section {
    font-family: 'Inter','Segoe UI','Noto Sans','DejaVu Sans',sans-serif;
    background: #ffffff;
    color: var(--ink);
    font-size: 30px;
    line-height: 1.3;
    padding: 34px 56px 44px 56px;
    justify-content: flex-start;
  }
  section::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 10px;
    background: linear-gradient(90deg, var(--accent) 0 30%, var(--ink) 30% 100%);
  }
  section::after { color: var(--muted); font-size: 18px; }
  section h1 {
    font-size: 42px; line-height: 1.12; color: var(--ink);
    border-left: 10px solid var(--accent); padding-left: 16px;
    margin: 0 0 14px 0; font-weight: 800;
  }
  section h2 { font-size: 30px; margin: 0 0 6px 0; color: var(--ink); }
  section p, section li { font-size: 30px; margin: 5px 0; }
  section ul, section ol { margin: 6px 0 6px 26px; padding: 0; }
  section strong { color: var(--accent); }
  section em { color: var(--muted); font-style: normal; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 26px; align-items: start; }
  .cols.mid { align-items: center; }
  .cols3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
  .cols4 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px 22px; }
  .center { text-align: center; }
  .card { border: 2px solid var(--line); border-top: 9px solid var(--accent2); border-radius: 14px; padding: 12px 18px; background: #fbfcfd; }
  .card.hot { border-top-color: var(--accent); background: #fff6f0; }
  .card.good { border-top-color: var(--good); background: #f1faf3; }
  .card h2 { font-size: 27px; margin: 0 0 4px 0; }
  .card p, .card li { font-size: 27px; }
  .kpi { text-align: center; }
  .kpi .n { display: block; font-size: 76px; font-weight: 800; line-height: 1; color: var(--accent); }
  .kpi .n.blue { color: var(--accent2); }
  .kpi .n.green { color: var(--good); }
  .kpi .t { display: block; font-size: 25px; color: var(--muted); margin-top: 4px; }
  img { display: block; margin: 0 auto; }
  .cap { font-size: 27px; text-align: center; margin: 8px 0 0 0; }
  .tiny { font-size: 22px; color: var(--muted); }
  table { font-size: 27px; margin: 8px auto; border-collapse: collapse; }
  th { background: var(--ink); color: #fff; padding: 6px 14px; font-size: 25px; }
  td { padding: 6px 14px; border-bottom: 2px solid var(--soft); text-align: center; }
  td:first-child, th:first-child { text-align: left; }
  .flow { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 14px 8px; font-size: 25px; margin-top: 14px; }
  .box { border: 2px solid var(--ink); border-radius: 10px; padding: 8px 14px; background: var(--soft); text-align: center; }
  .box.key { border-color: var(--accent); background: #fff3ec; font-weight: 700; }
  .arr { color: var(--accent); font-size: 26px; font-weight: 800; }
  .pill { display: inline-block; font-size: 24px; font-weight: 700; color: #fff; background: var(--accent); border-radius: 999px; padding: 2px 16px; }
  .pill.blue { background: var(--accent2); }
  .pill.green { background: var(--good); }
  .names { border: 4px dashed var(--accent); border-radius: 16px; padding: 18px 26px; margin-top: 18px; background: #fff6f0; font-size: 31px; font-weight: 800; }
  section.lead { justify-content: center; background: linear-gradient(135deg, #14213d 0%, #1b2f5e 100%); color: #fff; }
  section.lead::before { background: var(--accent); height: 14px; }
  section.lead h1 { color: #fff; font-size: 62px; border-left-color: var(--accent); }
  section.lead p, section.lead li { color: #e5eaf3; font-size: 30px; }
  section.lead strong { color: #ffb37a; }
  section.lead .names { background: rgba(255,255,255,.1); color: #fff; border-color: #ffb37a; }
  section.lead::after { color: #cbd5e1; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# NeuroCode: ¿a qué velocidad gira tu cerebro?

Mejor recta del tiempo de **rotación mental** con **Cálculo Multivariable**

*Cálculo Multivariable · Ingeniería de Software · U. Cooperativa de Colombia (Pasto) · M.Sc. Alejandro Molina · 17 de noviembre de 2026*

<!--
Medimos cuánto tarda el cerebro en girar una letra R en la mente y buscamos la recta que mejor lo describe. La herramienta es cálculo de varias variables: parciales, gradiente y Hessiano. Todo con datos reales, inspirado en Shepard y Metzler, 1971.
-->

---

# Un experimento real, tres números

<div class="cols3">
<div class="kpi"><span class="n">17</span><span class="t">participantes con sesión completa</span></div>
<div class="kpi"><span class="n blue">7</span><span class="t">ángulos: 0°, 30° … 180°</span></div>
<div class="kpi"><span class="n green">595</span><span class="t">ensayos usados en el modelo<br>(5 aciertos × 7 × 17)</span></div>
</div>

<div class="cols" style="margin-top:22px">
<div class="card"><h2>x = ángulo de la R</h2>en grados</div>
<div class="card hot"><h2>y = tiempo de respuesta</h2>en milisegundos (solo aciertos)</div>
</div>

<!--
Cada participante vio una R girada 0, 30, 60, 90, 120, 150 o 180 grados y respondió si era normal o espejo. Solo aciertos: 5 por ángulo, 35 por persona, 17 personas, 595 ensayos. Diseño balanceado: 85 ensayos por ángulo.
-->

---

# El tiempo sube con el ángulo

![w:1160](../figuras/01_dispersion.png)

<p class="cap">Media: <strong>718.7 ms</strong> a 0° → <strong>1169.1 ms</strong> a 180°. ¿Cuál es la mejor recta?</p>

<!--
Izquierda: los 595 ensayos, con mucha dispersión entre personas. Derecha: las siete medias por ángulo, que sí siguen una recta casi perfecta. La pregunta es qué recta y = ax + b es la mejor.
-->

---

# Puente: un punto (a, b) = una recta

![w:1160](../figuras/08_puente.png)

<p class="cap">Cada punto del mapa es <strong>una recta</strong>; el valle de S marca la <strong>mejor</strong>.</p>

<!--
Esta es la idea central. A la izquierda el plano de parámetros: cada punto (a,b) es un candidato. A la derecha, ese mismo punto dibujado como recta sobre los datos. Los puntos cercanos al fondo del valle dan rectas que se pegan a las medias; los lejanos se despegan. La altura de S es el error de esa recta.
-->

---

# Medimos el error: S(a, b)

$$S(a,b)=\sum_{i=1}^{595}\big(y_i-\textcolor{#d9480f}{a}\,x_i-\textcolor{#d9480f}{b}\big)^2$$

![h:400](../figuras/02_rectas_B.png)

<p class="cap">Al cuadrado: sin cancelaciones, castiga lo grande y se puede derivar.</p>

<!--
Cada recta tiene un error total S. El cuadrado evita que errores positivos y negativos se cancelen, castiga los errores grandes y permite derivar. Las rectas punteadas tienen S mayor que la óptima, con el porcentaje en la leyenda.
-->

---

# Mínimo ⇒ gradiente cero

$$\frac{\partial S}{\partial a}=-2\sum x_i\,(y_i-a x_i-b)\qquad \frac{\partial S}{\partial b}=-2\sum (y_i-a x_i-b)$$

$$\nabla S=\mathbf{0}\;\Rightarrow\;\begin{cases}\textcolor{#d9480f}{a}\sum x_i^2+\textcolor{#d9480f}{b}\sum x_i=\sum x_iy_i\\\textcolor{#d9480f}{a}\sum x_i+\textcolor{#d9480f}{b}\,n=\sum y_i\end{cases}$$

<div class="card hot center">Plano tangente <strong>horizontal</strong>: no se puede bajar más</div>

<!--
Regla de la cadena tratando la otra variable como constante. Igualar el gradiente a cero da el sistema normal, dos ecuaciones y dos incógnitas. Geométricamente, el plano tangente a z = S(a,b) es horizontal.
-->

---

# Resultado: qué significan a* y b*

<div class="cols3">
<div class="kpi"><span class="n">2.75</span><span class="t">a* · ms por grado</span></div>
<div class="kpi"><span class="n blue">683</span><span class="t">b* · ms a 0° (tiempo basal)</span></div>
<div class="kpi"><span class="n green">364</span><span class="t">ω = 1000/a* · grados por segundo</span></div>
</div>

$$a^*=\frac{n\sum xy-\sum x\sum y}{n\sum x^2-(\sum x)^2}=\frac{3\,500\,688\,450}{1\,274\,490\,000}\approx 2.746737 \qquad b^*=\frac{\sum y-a^*\sum x}{n}\approx 683.1213$$

<p class="tiny center">n = 595 · Σx = 53 550 · Σy = 553 544.9 · Σx² = 6 961 500 · Σxy = 55 702 551 · S<sub>mín</sub> = 156 163 296.22 ms²</p>

<!--
a* es el costo de rotar un grado: 2.75 milisegundos. Su inverso es la velocidad angular: unos 364 grados por segundo. b* es el tiempo base sin rotación, 683 milisegundos: percibir, decidir y responder. Las sumatorias se verifican con calculadora o en un minuto con las 7 medias.
-->

---

# El Hessiano confirma: mínimo global

$$H=\begin{pmatrix}2\sum x^2 & 2\sum x\\ 2\sum x & 2n\end{pmatrix}=\begin{pmatrix}13\,923\,000 & 107\,100\\ 107\,100 & 1\,190\end{pmatrix}$$

<div class="cols3">
<div class="card good"><h2>det H &gt; 0</h2>5.098 × 10⁹</div>
<div class="card good"><h2>S<sub>aa</sub> &gt; 0</h2>1.3923 × 10⁷</div>
<div class="card good"><h2>autovalores &gt; 0</h2>λ₁ = 366.1 · λ₂ = 1.39 × 10⁷</div>
</div>

<div class="card hot center" style="margin-top:14px"><strong>H es constante</strong> ⇒ S es un paraboloide convexo: un único mínimo, global</div>

<!--
Verificamos el gradiente casi cero, del orden de 1e-9. El determinante y S_aa positivos, y los dos autovalores positivos, confirman mínimo. Como H no depende de a ni de b, el mínimo es global: no puede haber máximo ni silla. La curvatura es muy distinta en cada dirección: cociente 38 mil.
-->

---

# S es un valle con un solo fondo

<div class="cols mid">
<div>

![h:470](../figuras/03_superficie.png)

</div>
<div>

![h:470](../figuras/05_curvas_nivel.png)

</div>
</div>

<p class="cap">Derecha: <strong>−∇S</strong> siempre baja al mínimo, perpendicular a las curvas de nivel.</p>

<!--
Izquierda, la superficie con el mínimo marcado. Derecha, las curvas de nivel con el campo menos gradiente. Las flechas se dibujan en la escala de pantalla, por eso se ven perpendiculares a las elipses y apuntan al fondo.
-->

---

# ¿Por qué las elipses están inclinadas?

![w:1160](../figuras/11_elipses_centradas.png)

<p class="cap">Término cruzado <strong>S<sub>ab</sub> = 2Σx = 107 100 ≠ 0</strong> → inclinadas. Con <strong>x̃ = x − 90°</strong>: Σx̃ = 0 → ejes alineados.</p>

<!--
El término cruzado S_ab es 2 por la suma de x, y es positivo, por eso las elipses se inclinan: a y b están correlacionados, subir la pendiente obliga a bajar el intercepto. Si centramos x restando 90, que es el promedio de los ángulos, la suma de x tilde es cero, el término cruzado desaparece y las elipses quedan alineadas con los ejes. El mínimo no cambia: el nuevo intercepto es simplemente la media de y, 930 ms, el tiempo a 90 grados.
-->

---

# Cada corte por el óptimo es una parábola

![w:1160](../figuras/04_trazas.png)

<p class="cap">Fija b y mueve a (o al revés): parábola con vértice en el óptimo.</p>

<!--
Fijar b en b* y mover a da una parábola con vértice en a*; lo mismo con b. Las secciones con otro valor fijo son parábolas paralelas más altas. Visualmente, el fondo es único.
-->

---

# El código replica el cálculo a mano

<div class="flow">
<div class="box">Cargar 17 CSV</div><span class="arr">→</span>
<div class="box">n, Σx, Σy, Σx², Σxy</div><span class="arr">→</span>
<div class="box key">a*, b*</div><span class="arr">→</span>
<div class="box">S<sub>mín</sub></div><span class="arr">→</span>
<div class="box">H, det H</div><span class="arr">→</span>
<div class="box key">¿det H &gt; 0 y S<sub>aa</sub> &gt; 0?</div><span class="arr">→</span>
<div class="box">Residuos, RMSE, R²</div><span class="arr">→</span>
<div class="box">Comparar con NumPy / SciPy</div>
</div>

<div class="card" style="margin-top:20px"><strong>Algoritmo propio</strong> de mínimos cuadrados, <strong>sin regresión de librería</strong>. NumPy y SciPy solo <em>verifican</em>.</div>

<!--
Diagrama de codigo/ajuste.py: cada caja es un paso del desarrollo manual. Primero las sumatorias, luego a* y b*, el error mínimo, el Hessiano y el criterio de segunda derivada, los residuos y la comparación con numpy y scipy. El pseudocódigo está en codigo/pseudocodigo.md.
-->

---

# Nuestro código y las librerías coinciden

| Parámetro | Manual | Código propio | polyfit / linregress | Δ |
|---|---|---|---|---|
| a | 2.7467 | 2.746737 | 2.746737 | ≈ 1e-14 |
| b | 683.12 | 683.1213 | 683.1213 | ≈ 5e-13 |
| S mín | 156 163 296 | 156 163 296.22 | 156 163 296.22 | 0 |

<div class="card good center">Tres vías, mismo punto: la diferencia es solo ruido de punto flotante</div>

<!--
Manual, algoritmo propio y numpy/scipy coinciden hasta del orden de 1e-14. Esa diferencia es ruido de redondeo, el valor exacto varía algo según la versión de la librería. El cálculo analítico queda verificado.
-->

---

# Residuos centrados en 0, con un atípico claro

![w:1160](../figuras/06_residuos.png)

<p class="cap">Media ē ≈ 0 · mayor residuo: <strong>fila 262 (P09, 150°): +5015.7 ms</strong> · el abanico crece con el ángulo.</p>

<!--
Residuos centrados en cero, la mayoría entre menos mil y mil milisegundos, con cola derecha. La dispersión crece con el ángulo (heterocedasticidad). El extremo es la fila 262 de P09 a 150 grados, una distracción. No hay patrón curvo: lo lineal es aceptable.
-->

---

# Dos R² con la misma recta

![w:1020](../figuras/09_doble_r2.png)

<div class="cols" style="margin-top:6px">
<div class="card hot"><p><strong>R²<sub>raw</sub> = 0.0938</strong> — el 90.3 % del error está <em>dentro</em> de cada ángulo (personas distintas y ensayo a ensayo).</p></div>
<div class="card good"><p><strong>R²<sub>medias</sub> = 0.9685</strong> — al promediar se cancela ese ruido y aparece la tendencia.</p></div>
</div>

<!--
Es la misma recta, los mismos a y b, evaluada en dos escalas. El 90.3 por ciento de la variación total ocurre dentro de un mismo ángulo: unas personas son más rápidas, y cada persona varía de un ensayo a otro. Ningún modelo que solo conozca el ángulo puede explicar eso, por eso R² crudo es bajo aunque p es 2e-14. Con las medias el ruido se promedia y la recta explica 96.85 por ciento.
-->

---

# ¿Es un efecto real? 16 de 17 personas

![w:960](../figuras/10_pendientes.png)

<!--
Cada barra es la pendiente de una persona ajustada por separado. 16 de 17 son positivas; solo P01 no muestra efecto. Prueba de signos p = 2.7e-4. La pendiente global 2.75 queda en el centro. P09 es la más alta, 8.95; si la quitamos, a* baja a 2.36 y la conclusión no cambia.
-->

---

# El error se descompone en dos piezas ortogonales

$$S_{\min}=\underbrace{155\,637\,440}_{\text{dentro de cada ángulo}}\;+\;\underbrace{85\cdot S_{\text{medias}}(a^*,b^*)}_{525\,856\ \text{(ajuste de la recta)}}=156\,163\,296$$

<div class="cols">
<div class="card hot"><h2>Ruido irreducible</h2>99.7 % de S<sub>mín</sub>. Ninguna recta lo puede bajar.</div>
<div class="card good"><h2>Lo que sí controla la recta</h2>0.3 % de S<sub>mín</sub>. Por eso minimizar S ≡ minimizar el error sobre las 7 medias.</div>
</div>

<p class="tiny center">Con un tiempo base por persona (18 parámetros, ∇S = 0): misma a* = 2.7467 y R² sube a 0.38.</p>

<!--
Descomposición ortogonal: S mínimo es la variación dentro de cada ángulo más 85 veces el error de la recta sobre las medias. La primera pieza no depende de a ni de b. Por eso la recta de los 595 ensayos es exactamente la recta de las 7 medias. Si además damos a cada persona su propio tiempo base, la pendiente sale idéntica y R cuadrado sube a 0.38.
-->

---

# Análisis adicional: A, B, C y D

<div class="cols4">
<div class="card"><h2><span class="pill blue">A</span> Sensibilidad</h2>Ruido ±25 ms → σ<sub>a</sub> = 0.017<br><strong>solo 0.60 %</strong></div>
<div class="card"><h2><span class="pill blue">B</span> Atípicos</h2>Sin fila 262: a* = 2.61<br>Sin &gt; 3 s: a* = 2.41</div>
<div class="card"><h2><span class="pill blue">C</span> Cuadrático</h2>R² 0.0938 → 0.0941<br><strong>ΔR² = +0.0003</strong>: lineal basta</div>
<div class="card"><h2><span class="pill blue">D</span> Tamaño N</h2>a*(N) se estabiliza desde N ≥ 10 personas</div>
</div>

<!--
A: perturbamos cada tiempo con ruido de 25 ms, 500 veces: la pendiente casi no cambia. B: quitar el mayor atípico baja a* a 2.61; quitar todos los mayores a 3 segundos, 2.41. C: el cuadrático mejora R cuadrado en tres diezmilésimas, no aporta. D: con 10 personas o más la pendiente ya se estabiliza.
-->

---

# Robustez en dos imágenes

<div class="cols mid">
<div>

![h:430](../figuras/07_opciones_BC_A.png)

</div>
<div>

![h:440](../figuras/07_opciones_BC_C.png)

</div>
</div>

<p class="cap">Las rectas casi se superponen (izq.) y a* converge al sumar personas (der.).</p>

<!--
Izquierda: lineal con todos los datos, sin el atípico, sin los mayores a 3 segundos, y cuadrático: casi indistinguibles sobre las medias. Derecha: la pendiente acumulada a*(N) oscila con pocos participantes y se estabiliza cerca de 2.7.
-->

---

# Transparencia sobre la muestra

| Conjunto | Ensayos | a* (ms/°) |
|---|---|---|
| Los 15 primeros (protocolo original) | 525 | 2.65 |
| **Modelo oficial: 17 con sesión completa** | **595** | **2.75** |
| Todo lo recolectado, sin copias exactas | 875 | 2.41 |

<div class="card hot">2 de los 17 se sumaron después de ver su ajuste, por eso <strong>también reportamos con 15</strong>. Los 875 incluyen sesiones repetidas y con distracciones. En los tres casos: <strong>a* &gt; 0</strong>.</div>

<!--
Lo decimos de frente: los 15 primeros se recolectaron con el protocolo. Llegaron más archivos, quitamos copias exactas y sumamos dos personas nuevas. Con 15 personas la pendiente es 2.65, con las 17 es 2.75, y con todo lo recolectado, incluso sesiones repetidas y distraídas, 2.41. La conclusión cualitativa no cambia.
-->

---

# Cerebro vs. computador

![w:900](../figuras/12_cerebro_vs_cpu.png)

<div class="cols">
<div class="card hot"><h2>Cerebro</h2>analógico: el costo <strong>crece lineal con θ</strong> (≈ 364 °/s)</div>
<div class="card"><h2>Computador</h2>matriz de rotación R(θ) 2×2: <strong>O(1)</strong>, no depende de θ</div>
</div>

<!--
El cerebro tarda 2.75 milisegundos más por cada grado: gira la imagen mental paso a paso, como lo propusieron Shepard y Metzler. Un computador aplica la matriz de rotación y tarda lo mismo para 10 que para 180 grados. La línea azul es un esquema, no una medición. Mismo problema, dos estrategias.
-->

---

# Demo en vivo: el laboratorio 3D

<div class="cols3">
<div class="card"><h2>1 · Arrastra</h2>un punto en el mapa: la <strong>recta</strong> cambia al instante</div>
<div class="card hot"><h2>2 · Observa −∇S</h2>la flecha amarilla siempre apunta al fondo</div>
<div class="card good"><h2>3 · Compara</h2>gradiente puro (zigzag) · escalado (250 pasos) · centrado x̃ (39 pasos)</div>
</div>

<p style="margin-top:20px"><span class="pill">Abrir</span> <code>figuras/superficie_interactiva.html</code> — funciona sin internet</p>

<!--
Abrimos el simulador. Arrastramos el punto sobre el mapa y vemos cómo cambia la recta y los números: S, el gradiente, la velocidad omega y los dos R cuadrado. Pulsamos animar descenso. Con el gradiente puro casi no avanza, porque el cociente de curvaturas es 38 mil; con el gradiente escalado converge en unos 250 pasos; si marcamos centrar x tilde, las elipses se enderezan y converge en 39.
-->

---

# Conclusiones

<div class="cols4">
<div class="card hot"><h2>1 · La recta</h2>y = 2.75·x + 683: cada grado cuesta <strong>2.75 ms</strong> (≈ 364 °/s)</div>
<div class="card"><h2>2 · El cálculo</h2>∇S = 0 y H definida positiva ⇒ <strong>mínimo único y global</strong></div>
<div class="card good"><h2>3 · Doble R²</h2><strong>0.0938</strong> en ensayos, <strong>0.9685</strong> en medias: misma recta, ruido intra-ángulo</div>
<div class="card"><h2>4 · Límites</h2>17 personas, 16 con efecto positivo; el modelo mide la <strong>tendencia media</strong></div>
</div>

<!--
Resumen: la recta describe el costo de rotar; el cálculo garantiza el mínimo; el doble R cuadrado no es contradicción sino ruido entre personas; y somos transparentes con los límites: muestra pequeña, dos participantes añadidos, atípicos, heterocedasticidad.
-->

---

<!-- _class: lead -->

# Gracias: ¿preguntas?

Cada integrante puede deducir ∂S/∂a, ∂S/∂b y el Hessiano en el tablero.

<div class="names">Integrantes: [nombre 1] · [nombre 2] · [nombre 3] · [nombre 4]</div>

<!--
Agradecemos al profesor. Cada integrante puede derivar las parciales, el sistema normal y el Hessiano en el tablero y comprobarlo con la tabla de 7 medias. Quedamos atentos a preguntas.
-->
