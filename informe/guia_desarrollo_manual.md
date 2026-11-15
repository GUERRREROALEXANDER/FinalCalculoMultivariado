# Guía maestra de desarrollo manual y defensa individual (40 % de la nota)

Esta guía está diseñada para que cualquier integrante del grupo pueda:
1. **Hacer todo el desarrollo analítico en el tablero o en papel con calculadora** (Criterio 1: Comprensión conceptual 20 % + Criterio 2: Evaluación individual 20 %).
2. **Demostrar con una tabla de solo 7 filas** (los promedios por ángulo) que se obtiene **exactamente el mismo $(a^*, b^*) = (2.6500\text{ ms/}^\circ, 656.91\text{ ms})$** que con los $n = 525$ datos crudos.

---

## Parte 0. Las 5 ideas clave para el tablero

1. **Función de dos variables $S(a, b)$:** En $y = ax + b$, los datos $(x_i, y_i)$ ya están fijos; las incógnitas son la pendiente $a$ y el intercepto $b$. Cada par $(a, b)$ define una recta candidata y $S(a, b)$ mide su error cuadrático total (la "altura" en un paisaje 3D). Buscamos el fondo del valle.
2. **¿Por qué elevar los residuos al cuadrado?** El residuo es $e_i = y_i - (ax_i + b)$.
   - Si sumamos $\sum e_i$ sin cuadrar, los errores positivos y negativos se cancelan ($\sum e_i = 0$ para infinitas rectas malas).
   - Si usamos valor absoluto $\sum |e_i|$, la función tiene picos donde **no es derivable**.
   - Al elevar al cuadrado, $S(a,b) = \sum (y_i - ax_i - b)^2 \ge 0$ es suave ($C^\infty$), penaliza más las desviaciones grandes y tiene un único mínimo analítico.
3. **Derivadas parciales ($\partial S/\partial a$ y $\partial S/\partial b$):** Medimos la tasa de cambio del error al mover un parámetro dejando el otro fijo. Aplicamos la regla de la cadena a cada término $(y_i - ax_i - b)^2$:
   - La derivada interna respecto de $a$ es $-x_i$.
   - La derivada interna respecto de $b$ es $-1$.
4. **Condición necesaria de extremo ($\nabla S(a, b) = \mathbf{0}$):** El gradiente $\nabla S = \left(\frac{\partial S}{\partial a}, \frac{\partial S}{\partial b}\right)$ apunta en la dirección de máximo crecimiento de $S$. En un mínimo, no se puede bajar en ninguna dirección, por lo que el **plano tangente a la superficie $z = S(a,b)$ es horizontal** y $\nabla S(a^*, b^*) = (0, 0)$.
5. **Criterio del Hessiano (condición suficiente):** Como $\nabla S = \mathbf{0}$ también ocurre en máximos o puntos de silla, calculamos la matriz Hessiana de segundas derivadas:
   $$H = \begin{pmatrix} S_{aa} & S_{ab} \\ S_{ba} & S_{bb} \end{pmatrix}, \qquad D = \det(H) = S_{aa}S_{bb} - (S_{ab})^2$$
   Si $D > 0$ y $S_{aa} > 0$, la curvatura es cóncava hacia arriba en todas las direcciones $\Rightarrow$ **mínimo local**. Como $H$ es **constante** (no depende de $a$ ni de $b$), la superficie es un **paraboloide elíptico estrictamente convexo** y el mínimo es **único y global**.

---

## Parte 1. Deducción general paso a paso (lo que se escribe en el tablero)

### 7.1. Función objetivo y derivadas parciales
Dado el conjunto de datos $(x_1, y_1), \dots, (x_n, y_n)$:
$$S(a,b) = \sum_{i=1}^{n} (y_i - ax_i - b)^2$$

Derivando parcialmente respecto de $a$ ($b$ constante):
$$\frac{\partial S}{\partial a} = \sum_{i=1}^{n} 2(y_i - ax_i - b)\cdot(-x_i) = -2\sum_{i=1}^{n} x_i(y_i - ax_i - b)$$

Derivando parcialmente respecto de $b$ ($a$ constante):
$$\frac{\partial S}{\partial b} = \sum_{i=1}^{n} 2(y_i - ax_i - b)\cdot(-1) = -2\sum_{i=1}^{n} (y_i - ax_i - b)$$

### 7.2. Condición de punto crítico $\nabla S(a,b) = (0,0)$ (Ecuaciones Normales)
Igualamos ambas derivadas a cero, dividimos entre $-2$ y distribuimos la sumatoria (recordando que $\sum_{i=1}^n b = n\cdot b$):
$$\begin{cases}
\displaystyle\sum_{i=1}^{n} x_i y_i - a\sum_{i=1}^{n} x_i^2 - b\sum_{i=1}^{n} x_i = 0 \\[8pt]
\displaystyle\sum_{i=1}^{n} y_i - a\sum_{i=1}^{n} x_i - n\,b = 0
\end{cases}
\quad\Longrightarrow\quad
\begin{cases}
\left(\sum x_i^2\right)a + \left(\sum x_i\right)b = \sum x_i y_i & \text{(Ec. 1)} \\[6pt]
\left(\sum x_i\right)a + n\,b = \sum y_i & \text{(Ec. 2)}
\end{cases}$$

### 7.3. Solución algebraica manual del sistema $2\times 2$
De la **(Ec. 2)** despejamos $b$ en función de $a$:
$$b = \frac{\sum y_i - a\sum x_i}{n} = \bar{y} - a\bar{x}$$
*(Propiedad geométrica clave: la recta óptima siempre pasa por el centroide $(\bar{x}, \bar{y})$ de los datos).*

Sustituimos $b$ en la **(Ec. 1)**:
$$a\sum x_i^2 + \left(\frac{\sum y_i - a\sum x_i}{n}\right)\sum x_i = \sum x_i y_i$$
Multiplicamos toda la ecuación por $n$ y agrupamos los términos con $a$:
$$a\left[n\sum x_i^2 - \left(\sum x_i\right)^2\right] = n\sum x_i y_i - \left(\sum x_i\right)\left(\sum y_i\right)$$
De donde obtenemos las fórmulas cerradas de $(a^*, b^*)$:
$$\boxed{a^* = \frac{n\sum x_i y_i - \left(\sum x_i\right)\left(\sum y_i\right)}{n\sum x_i^2 - \left(\sum x_i\right)^2}} \qquad \boxed{b^* = \frac{\sum y_i - a^*\sum x_i}{n}}$$

### 7.4. Matriz Hessiana y demostración de mínimo global
Reescribiendo las primeras derivadas expandidas:
$$\frac{\partial S}{\partial a} = 2\left(\sum x_i^2\right)a + 2\left(\sum x_i\right)b - 2\sum x_i y_i, \qquad \frac{\partial S}{\partial b} = 2\left(\sum x_i\right)a + 2n\,b - 2\sum y_i$$
Calculamos las segundas derivadas parciales:
$$S_{aa} = \frac{\partial^2 S}{\partial a^2} = 2\sum_{i=1}^{n} x_i^2, \qquad S_{bb} = \frac{\partial^2 S}{\partial b^2} = 2n, \qquad S_{ab} = S_{ba} = \frac{\partial^2 S}{\partial a\partial b} = 2\sum_{i=1}^{n} x_i$$
Por tanto, la matriz Hessiana es:
$$H(a,b) = \begin{pmatrix} 2\sum x_i^2 & 2\sum x_i \\ 2\sum x_i & 2n \end{pmatrix}$$
Su determinante es:
$$D = \det(H) = 4n\sum x_i^2 - 4\left(\sum x_i\right)^2 = 4\left[n\sum x_i^2 - \left(\sum x_i\right)^2\right] = 4n\sum_{i=1}^{n}(x_i - \bar{x})^2$$
Como existen al menos dos ángulos distintos ($x_i \neq \bar{x}$), por la desigualdad de Cauchy-Schwarz se cumple estrictamente que:
$$S_{aa} = 2\sum x_i^2 > 0 \quad \text{y} \quad D = 4n\sum (x_i - \bar{x})^2 > 0 \quad\Longrightarrow\quad \textbf{Mínimo estricto global}.$$

---

## Parte 2. Cálculo numérico con nuestros datos reales

### 2A. Con los $n = 525$ ensayos completos (15 participantes $\times$ 35 ensayos)

| Cantidad | Valor exacto | Significado |
|---|---|---|
| $n$ | $525$ | Total de ensayos válidos ($75$ por cada uno de los $7$ ángulos) |
| $\sum x_i$ | $47\,250$ | Suma de ángulos ($\bar{x} = 90^\circ$) |
| $\sum y_i$ | $470\,089.6$ | Suma de tiempos en ms ($\bar{y} = 895.41\text{ ms}$) |
| $\sum x_i^2$ | $6\,142\,500$ | Suma de ángulos al cuadrado |
| $\sum x_i y_i$ | $47\,316\,603.0$ | Suma de productos ángulo $\times$ tiempo |
| $\sum y_i^2$ | $576\,252\,338.14$ | Suma de tiempos al cuadrado |

1. **Denominador común $D_0$:**
   $$D_0 = n\sum x_i^2 - \left(\sum x_i\right)^2 = 525(6\,142\,500) - (47\,250)^2 = 3\,224\,812\,500 - 2\,232\,562\,500 = 992\,250\,000$$
2. **Pendiente óptima $a^*$:**
   $$a^* = \frac{525(47\,316\,603.0) - (47\,250)(470\,089.6)}{992\,250\,000} = \frac{2\,629\,482\,975}{992\,250\,000} \approx \mathbf{2.650021\text{ ms/}^\circ}$$
3. **Intercepto óptimo $b^*$:**
   $$b^* = \frac{470\,089.6 - (2.650021)(47\,250)}{525} = \frac{344\,876.125}{525} \approx \mathbf{656.9069\text{ ms}}$$
4. **Error cuadrático mínimo $S(a^*, b^*)$:**
   $$S_{\min} = \sum y_i^2 - a^*\sum x_i y_i - b^*\sum y_i = 142\,057\,259.72\text{ ms}^2 \approx \mathbf{1.421\times 10^8\text{ ms}^2}$$
5. **Matriz Hessiana y criterio de segunda derivada:**
   $$H = \begin{pmatrix} 12\,285\,000 & 94\,500 \\ 94\,500 & 1\,050 \end{pmatrix}, \qquad D = \det(H) = 4 D_0 = \mathbf{3\,969\,000\,000 > 0}, \qquad S_{aa} = \mathbf{12\,285\,000 > 0}$$
   Valores propios de $H$: $\lambda_1 = 323.06 > 0$ y $\lambda_2 = 12\,285\,726.94 > 0$ ($H$ es definida positiva).

---

### 2B. Atajo de 60 segundos para la defensa: Tabla de $K = 7$ promedios por ángulo

> **Teorema de equivalencia (diseño balanceado):** Como cada uno de los $K = 7$ ángulos tiene exactamente $m = 75$ mediciones, la función de error se descompone ortogonalmente como:
> $$S(a,b) = \underbrace{\sum_{k=1}^{7}\sum_{j=1}^{75} (y_{kj} - \bar{y}_k)^2}_{\text{SS}_{\text{intra}} = 141\,531\,492.47\text{ (no depende de }a,b\text{)}} + 75\underbrace{\sum_{k=1}^{7} (\bar{y}_k - ax_k - b)^2}_{S_{\text{medias}}(a,b)}$$
> Al derivar respecto de $a$ y $b$, $\text{SS}_{\text{intra}}$ desaparece. Por tanto, **hacer el cálculo manual con las 7 medias por ángulo produce exactamente el mismo $(a^*, b^*)$ que con los 525 datos**, ¡y se puede sumar en 1 minuto con calculadora frente al profesor!

| $k$ | Ángulo $x_k$ (°) | Media $\bar{y}_k$ (ms) | $x_k^2$ | $x_k \bar{y}_k$ | Predicho $\hat{y}_k = a^*x_k + b^*$ | Residuo medio $e_k$ (ms) |
|---|---|---|---|---|---|---|
| 1 | $0$ | $696.78$ | $0$ | $0.00$ | $656.91$ | $+39.87$ |
| 2 | $30$ | $727.10$ | $900$ | $21\,813.00$ | $736.41$ | $-9.31$ |
| 3 | $60$ | $752.79$ | $3\,600$ | $45\,167.40$ | $815.91$ | $-63.12$ |
| 4 | $90$ | $904.89$ | $8\,100$ | $81\,440.10$ | $895.41$ | $+9.48$ |
| 5 | $120$ | $973.51$ | $14\,400$ | $116\,821.20$ | $974.91$ | $-1.40$ |
| 6 | $150$ | $1\,088.55$ | $22\,500$ | $163\,282.50$ | $1\,054.41$ | $+34.14$ |
| 7 | $180$ | $1\,124.24$ | $32\,400$ | $202\,363.20$ | $1\,133.91$ | $-9.67$ |
| **Suma ($K=7$)** | **$\sum x_k = 630$** | **$\sum \bar{y}_k = 6\,267.86$** | **$\sum x_k^2 = 81\,900$** | **$\sum x_k\bar{y}_k = 630\,888.04$** | **$\sum \hat{y}_k = 6\,267.86$** | **$\sum e_k = 0.00$** |

Verificación directa en calculadora con $K = 7$:
- $D_0 = 7(81\,900) - (630)^2 = 573\,300 - 396\,900 = 176\,400$
- $a^* = \frac{7(630\,888.04) - 630(6\,267.86)}{176\,400} = \frac{4\,416\,216.28 - 3\,948\,751.80}{176\,400} = \frac{467\,464.48}{176\,400} = \mathbf{2.650021\text{ ms/}^\circ}$
- $b^* = \frac{6\,267.86 - 2.650021(630)}{7} = \mathbf{656.9069\text{ ms}}$
- Sobre las 7 medias: $\text{RMSE}_{\text{medias}} = \sqrt{7010.23 / 7} = \mathbf{31.6\text{ ms}}$ y **$R^2_{\text{medias}} = 0.9619$ ($96.2\%$)**.

---

## Parte 3. Banco de preguntas de defensa oral (respuestas de 5.0)

1. **¿Por qué $R^2 = 0.0854$ en los 525 datos pero $R^2 = 0.9619$ en los promedios por ángulo?**
   Porque en los 525 ensayos crudos, el $99.6\%$ del error cuadrático ($\text{SS}_{\text{intra}} = 1.415\times 10^8\text{ ms}^2$) es **variabilidad humana dentro del mismo ángulo**: personas rápidas como P07 tienen tiempo base de $384\text{ ms}$ y personas pausadas como P10 tienen $1180\text{ ms}$. Ninguna función que dependa únicamente del ángulo $x$ puede predecir qué participante está sentado frente al teclado. Al promediar por ángulo (como hicieron Shepard y Metzler en 1971), el ruido entre sujetos se cancela y la ley lineal explica el **$96.2\%$** de la varianza ($p = 0.0001$).
2. **¿Por qué las curvas de nivel de $S(a,b)$ son elipses inclinadas y muy alargadas?**
   Son elipses porque la forma cuadrática asociada a $H$ es definida positiva ($\lambda_1, \lambda_2 > 0$). Están **inclinadas** porque el término cruzado fuera de la diagonal no es cero: $S_{ab} = 2\sum x_i = 94\,500 > 0$ (ya que los ángulos $x_i \in [0^\circ, 180^\circ]$ no están centrados en cero; si restáramos $\bar{x}=90^\circ$, $H$ sería diagonal y los ejes de las elipses serían paralelos a los ejes coordenados). Son **muy alargadas** porque el número de condición de $H$ es $\lambda_2 / \lambda_1 = 12\,285\,727 / 323.06 \approx 38\,029$: la función $S(a,b)$ es casi $195$ veces más sensible a cambios de 1 unidad en $a$ que a cambios de 1 unidad en $b$.
3. **¿Qué diferencia hay entre una traza y una sección transversal (Req. 7.7)?**
   En nuestro contexto, las **secciones transversales** son los cortes planos de la superficie $z = S(a,b)$ al fijar $b = b_0$ constante, dando la familia de parábolas $S(a, b_0) = (\sum x_i^2)a^2 + 2(b_0\sum x_i - \sum x_i y_i)a + C(b_0)$. La **traza óptima** es el corte particular que pasa por el mínimo ($b_0 = b^*$ o $a_0 = a^*$). Como $S_{ab} > 0$, al subir el corte $b_0$, el vértice de la sección transversal en $a$ se desplaza hacia la izquierda según $a_{\text{vértice}}(b_0) = a^* - \frac{\bar{x}}{\sum x_i^2 / n}(b_0 - b^*)$.
4. **¿Cómo se aplica Cálculo Multivariable al modelo cuadrático de la Opción C ($y = c_2 x^2 + c_1 x + c_0$)?**
   El error pasa a ser una función de **tres variables** $S(c_2, c_1, c_0) = \sum (y_i - c_2 x_i^2 - c_1 x_i - c_0)^2$. La condición $\nabla S = (0,0,0)$ en $\mathbb{R}^3$ genera un sistema lineal $3\times 3$ y una matriz Hessiana $3\times 3$ simétrica definida positiva. Al resolverlo se obtiene $y = 0.00406x^2 + 1.920x + 675.16$, cuyo $R^2_{\text{raw}} = 0.0860$ mejora apenas en $+0.0006$ respecto al lineal ($0.0854$), confirmando que no hay curvatura real que justifique agregar un tercer parámetro.
5. **¿Qué demuestra la comparación entre el cerebro humano y el computador?**
   El cerebro ejecuta una transformación analógica continua: su tiempo $t(\theta) = 656.91 + 2.65\theta$ crece linealmente con el ángulo a una velocidad angular mental de $\omega = 1000 / a^* \approx 377.4^\circ\text{/s}$. En cambio, un computador rota la imagen multiplicando coordenadas por la matriz ortogonal $R(\theta) = \begin{pmatrix}\cos\theta & -\sin\theta \\ \sin\theta & \cos\theta\end{pmatrix}$, realizando exactamente 4 multiplicaciones y 2 sumas en punto flotante ($\mathcal{O}(1)$ respecto a $\theta$), por lo que su pendiente es $a_{\text{CPU}} = 0\text{ ms/}^\circ$.
