# Hoja de Batalla para Sustentación (Meta: 5.0 / 5.0)

**Curso:** Cálculo Multivariable · **Docente:** M.Sc. Alejandro Molina · **Proyecto:** NeuroCode  
Esta hoja condensa todo lo que necesita cada integrante para dominar el **40 % de evaluación conceptual e individual** y el **15 % de conclusiones y presentación**.

---

## 1. Reparto estratégico de la exposición (24 diapositivas · 4 integrantes)

> **Regla de oro:** Todos deben saber derivar en el tablero, pero en la presentación oral cada uno lidera un bloque cerrado con transición limpia.

| Integrante | Diapositivas | Qué explica y qué demuestra |
|---|---|---|
| **Integrante 1** *(Problema, Datos y Modelo)* | **Diapos 1 a 5** | Plantea el fenómeno de Shepard y Metzler (rotación mental de la letra R), explica el diseño experimental balanceado ($17\times 7\times 5 = 595$ ensayos, $m=85$ por ángulo), muestra la tendencia en `01_dispersion.png` ($718.7 \to 1169.1\text{ ms}$), explica el puente "un punto $(a,b)$ = una recta" (`08_puente.png`) y formula la función de dos variables $S(a,b)=\sum (y_i-ax_i-b)^2$ (`02_rectas.png`). |
| **Integrante 2** *(Cálculo Multivariable: Gradiente y Hessiano)* | **Diapos 6 a 8** | Deduce $\frac{\partial S}{\partial a}$ y $\frac{\partial S}{\partial b}$ con regla de la cadena, plantea $\nabla S(a,b)=\mathbf{0}$ (plano tangente horizontal), resuelve el sistema $2\times 2$ con las sumatorias reales hasta $a^*=2.7467\text{ ms/}^\circ$ y $b^*=683.12\text{ ms}$, y demuestra con la matriz Hessiana $H$ ($D = 5.098\times 10^9 > 0$, $S_{aa} = 1.3923\times 10^7 > 0$, $\lambda_1,\lambda_2 > 0$) que es un **mínimo global único**. |
| **Integrante 3** *(Geometría 3D, Algoritmo, Validación y Residuos)* | **Diapos 9 a 14** | Interpreta geométricamente el paraboloide elíptico (`03_superficie.png`), las curvas de nivel inclinadas con el campo $-\nabla S$ (`05_curvas_nivel.png`) y por qué se enderezan al centrar $\tilde x = x-90^\circ$ (`11_elipses_centradas.png`), la diferencia entre **trazas óptimas** y **secciones transversales** (`04_trazas.png`), el flujo del algoritmo propio sin librerías y la tabla de validación ($\Delta a \approx 10^{-14}$) y los residuos (`06_residuos.png`: media $0$, sin sesgo curvo, heterocedasticidad y atípico fila 262). |
| **Integrante 4** *($R^2$ Dual, Robustez y Conclusiones)* | **Diapos 15 a 24** | Explica la **descomposición ortogonal del $R^2$** ($R^2_{\text{raw}}=9.38\%$ porque el 90.3 % de la variación está dentro de cada ángulo: 32 % diferencias entre personas y 68 % ensayo a ensayo, vs. $R^2_{\text{medias}}=96.85\%$ sobre las 7 medias con los **mismos** $a^*, b^*$; `09_doble_r2.png`), las 16 de 17 pendientes positivas (`10_pendientes.png`), la descomposición ortogonal de $S_{\min}$, presenta las 4 opciones adicionales A–D (`07_opciones_BC.png`), la transparencia de muestra ($a^*=2.65/2.75/2.41$ con 15, 17 y todo lo recolectado), la comparación Cerebro ($364.1^\circ\text{/s}$) vs. Computador (matriz de rotación $R(\theta)$ en $\mathcal{O}(1)$) y ejecuta la demo 3D interactiva con descenso por gradiente en vivo. |

---

## 2. Las 7 "Preguntas Trampa" de Cálculo Multivariable (para pasar de 4.5 a 5.0)

### Trampa 1: *"¿Qué pasa geométricamente y algebraicamente si todos los datos tuvieran el mismo ángulo $x_1 = x_2 = \dots = x_n = x_0$?"*
- **Respuesta algebraica:** El denominador $D_0 = n\sum x_i^2 - (\sum x_i)^2 = n\sum (x_i - \bar{x})^2$ se vuelve **cero**, y el determinante del Hessiano $D = 4D_0 = 0$. El criterio del Hessiano no concluye y el sistema $2\times 2$ tiene infinitas soluciones (las dos ecuaciones normales se vuelven la misma recta $a x_0 + b = \bar{y}$).
- **Respuesta geométrica:** La superficie $z = S(a,b)$ deja de ser un paraboloide elíptico (un tazón con un solo punto mínimo) y se degenera en un **cilindro parabólico** (una canaleta infinita cuyo fondo es toda la recta $a x_0 + b = \bar{y}$). Por eso se necesitan al menos dos ángulos distintos para ajustar una recta.

### Trampa 2: *"En sus curvas de nivel, ¿por qué las elipses están inclinadas (rotadas) y cómo harían para que quedaran derechas (paralelas a los ejes)?"*
- **Por qué están inclinadas:** Porque la derivada parcial mixta del Hessiano no es cero:
  $$S_{ab} = \frac{\partial^2 S}{\partial a\partial b} = 2\sum_{i=1}^n x_i = 107\,100 > 0$$
  Eso acopla los parámetros $a$ y $b$: si subes la pendiente $a$, debes bajar el intercepto $b$ según $b = \bar{y} - a\bar{x}$ para mantener la recta pasando por el centro de masa $(\bar{x}, \bar{y}) = (90^\circ, 930.33\text{ ms})$.
- **Cómo se enderezan (ortogonalización):** Si centramos la variable independiente definiendo $\tilde{x}_i = x_i - \bar{x} = x_i - 90^\circ$, entonces $\sum \tilde{x}_i = 0 \implies S_{ab} = 0$. El Hessiano queda **diagonal** $H = \begin{pmatrix} 2\sum \tilde{x}_i^2 & 0 \\ 0 & 2n \end{pmatrix}$ y los ejes de las elipses quedan exactamente paralelos a los ejes coordenados.

### Trampa 3: *"¿Cómo calcula la pendiente de la recta tangente a una sección transversal $S(a, b_0)$ en cualquier punto $a$?"*
- La sección transversal fijando $b = b_0$ es la parábola $g(a) = S(a, b_0)$. Su pendiente en cualquier $a$ es exactamente la derivada parcial:
  $$g'(a) = \frac{\partial S}{\partial a}(a, b_0) = 2\left(\sum x_i^2\right)a + 2\left(\sum x_i\right)b_0 - 2\sum x_i y_i$$
- Su vértice (donde $g'(a) = 0$) está en $a_{\text{vértice}}(b_0) = a^* - \frac{\sum x_i}{\sum x_i^2}(b_0 - b^*)$. Solo cuando $b_0 = b^*$, el vértice cae exactamente en $a = a^*$.

### Trampa 4: *"¿Por qué el vector gradiente $\nabla S(a,b)$ es siempre perpendicular a las curvas de nivel?"*
- Una curva de nivel cumple $S(a(t), b(t)) = k$ (constante). Derivando respecto a $t$ por la regla de la cadena multivariable:
  $$\frac{d}{dt}S(a(t), b(t)) = \frac{\partial S}{\partial a}\frac{da}{dt} + \frac{\partial S}{\partial b}\frac{db}{dt} = \nabla S(a,b) \cdot \mathbf{r}'(t) = 0$$
  Como el producto punto entre $\nabla S$ y el vector tangente $\mathbf{r}'(t)$ a la curva de nivel es cero, $\nabla S$ es ortogonal a la elipse de nivel, y $-\nabla S$ apunta hacia el interior del valle.

### Trampa 5: *"Si $R^2 = 0.0938$ en los 595 datos, ¿cómo justifican que el modelo lineal es bueno?"*
- Porque en un experimento con medidas repetidas ($17$ personas $\times 7$ ángulos $\times 5$ repeticiones), la suma de cuadrados se descompone como:
  $$S(a,b) = \text{SS}_{\text{intra-ángulo}} + 85\,S_{\text{medias}}(a,b)$$
- El término $\text{SS}_{\text{intra-ángulo}} = 1.556\times 10^8\text{ ms}^2$ ($90.3\%$ de la varianza total) mide cuánto varían los tiempos **dentro del mismo ángulo**. Ojo, no es todo "diferencia entre personas": solo un tercio ($32\%$) son personas rápidas ($\bar{y}_{\text{P07}} = 473\text{ ms}$) contra lentas ($\bar{y}_{\text{P09}} = 1483\text{ ms}$); dos tercios ($68\%$) son la misma persona variando de un ensayo a otro. Como **no depende de $a$ ni de $b$**, su gradiente es cero y ningún modelo $y = f(x)$ que dependa solo del ángulo puede explicarlo (ni siquiera el cuadrático, que da $R^2 = 0.0941$).
- En cambio, sobre la tendencia media por ángulo ($K = 7$), que tiene **exactamente el mismo mínimo $(a^*, b^*) = (2.7467, 683.12)$**, el modelo lineal explica **$R^2_{\text{medias}} = 0.9685$ ($96.85\%$)** con un error de apenas $\text{RMSE} = 29.7\text{ ms}$.
- **Remate (el argumento más fuerte):** **16 de 17 personas**, cada una por separado, tienen pendiente positiva (prueba de signos $p = 0.0003$). Y si a cada persona le damos su propio tiempo base, $S(a, b_1, \dots, b_{17})$ con 18 variables y el mismo método $\nabla S = \mathbf{0}$, la pendiente sale **idéntica** ($a^* = 2.7467$) y $R^2$ sube a $0.384$.

### Trampa 6: *"¿Por qué 17 participantes? ¿Cómo decidieron qué datos usar?"*
- **Responder con la verdad, sin rodeos:** los 15 primeros se recolectaron con el protocolo. Llegaron 13 archivos más; quitamos 3 copias exactas y sumamos 2 personas nuevas, elegidas mirando su ajuste. Como eso puede favorecer el resultado, **reportamos la pendiente con las tres reglas**: solo 15 → $a^* = 2.65$; 17 → $2.75$; todo lo recolectado ($n = 875$) → $2.41$. Y quitando a cualquier persona, $a^*$ queda entre $2.36$ y $2.92$. La conclusión (el tiempo sube unos 2.4–2.9 ms por grado) no depende de esa elección.
- **No decir** "los validamos estadísticamente": elegir datos por su $p$ o su $R^2$ no es validar, y el profesor lo sabe.

### Trampa 7: *"En su figura de curvas de nivel, ¿las flechas son de verdad $-\nabla S$? Los ejes tienen escalas muy distintas."*
- Sí, y por eso hubo que cuidarlas. En unidades crudas, $\partial S/\partial a$ es miles de veces mayor que $\partial S/\partial b$ (porque $S_{aa}/S_{bb} \approx 11\,700$), y una flecha dibujada así saldría casi horizontal, sin verse perpendicular a nada.
- La perpendicularidad (Trampa 4) solo se ve con los dos ejes a la misma escala. En la figura, 1 ms/° de $a$ ocupa en pantalla lo mismo que unos 160 ms de $b$. Por eso calculamos el gradiente en las variables del dibujo, $X = a\cdot p_a$ y $Y = b\cdot p_b$ (píxeles por unidad): por la regla de la cadena, $\partial S/\partial X = S_a/p_a$. Es la misma función con las variables reescaladas, así que sus flechas sí son perpendiculares a las elipses tal como se dibujan, y todas apuntan cuesta abajo.
- **Si preguntan por el demo 3D:** el botón baja por $-\nabla S$ con cada componente dividida por su curvatura, $a \leftarrow a - \alpha\,S_a/S_{aa}$ y $b \leftarrow b - \alpha\,S_b/S_{bb}$. Con $-\nabla S$ puro, como $\lambda_2/\lambda_1 \approx 38\,029$, el paso tendría que ser tan pequeño (para no salirse en la dirección empinada) que en la dirección plana tardaría miles de pasos en zigzag. Ese es el significado práctico del número de condición de $H$.

---

## 3. Fórmulas de bolsillo para escribir en el tablero sin dudar

1. **Función de error:** $S(a,b) = \sum_{i=1}^n (y_i - ax_i - b)^2$
2. **Parciales:** $\frac{\partial S}{\partial a} = -2\sum x_i(y_i - ax_i - b) = 0, \qquad \frac{\partial S}{\partial b} = -2\sum (y_i - ax_i - b) = 0$
3. **Ecuaciones normales:** $\left(\sum x_i^2\right)a + \left(\sum x_i\right)b = \sum x_i y_i, \qquad \left(\sum x_i\right)a + n\,b = \sum y_i$
4. **Solución cerrada:** $D_0 = n\sum x_i^2 - (\sum x_i)^2 > 0$, $\quad a^* = \frac{n\sum x_i y_i - \sum x_i\sum y_i}{D_0}$, $\quad b^* = \frac{\sum y_i - a^*\sum x_i}{n}$
5. **Hessiano:** $H = \begin{pmatrix} 2\sum x_i^2 & 2\sum x_i \\ 2\sum x_i & 2n \end{pmatrix}$, $\quad D = \det(H) = 4D_0 > 0$, $\quad S_{aa} = 2\sum x_i^2 > 0 \implies \text{Mínimo global}$.
