# Guía desde cero: desarrollo manual (paso 4)

Para quien nunca vio cálculo multivariable. Orden: ideas → ejemplo chico → nuestros datos → defensa.
Todo se puede hacer con calculadora y papel.

---

## Parte 0. Las 5 ideas que necesitas

**Idea 1: una función de dos variables.** Una función normal, f(x), recibe un número y da otro.
Una de dos variables, S(a, b), recibe **dos** números y da uno. Piénsala como un terreno: (a, b) es
el punto del mapa y S es la altura. Buscamos el punto más bajo (el valle).

**Idea 2: qué son `a` y `b` aquí.** La recta es y = a·x + b. Cada pareja (a, b) es una recta distinta.
S(a, b) mide qué tan mal pasa esa recta por nuestros datos. Menor S, mejor recta.

**Idea 3: por qué se eleva al cuadrado.** El error de un dato es e = y − (a·x + b). Si sumamos
errores sin cuadrar, los positivos y negativos se cancelan y una recta mala parece buena.
Al cuadrar, todo es positivo, los errores grandes pesan más y la función es suave (se puede derivar).

**Idea 4: derivada parcial.** Es derivar respecto de una variable **tratando la otra como un número
fijo**. ∂S/∂a: muevo solo `a` y miro cómo cambia la altura. ∂S/∂b: igual con `b`.
Regla práctica: derivas normal, y lo que no es la variable lo tratas como constante.

**Idea 5: gradiente y mínimo.** El gradiente ∇S = (∂S/∂a, ∂S/∂b) apunta hacia donde la altura sube
más rápido. En el fondo del valle no sube en ninguna dirección: **∇S = (0, 0)**.
Geométricamente, el plano tangente es horizontal. Eso nos da dos ecuaciones y dos incógnitas.
Pero (0,0) también ocurre en la cima o en un punto de silla, y el **Hessiano** confirma que es valle.

---

## Parte 1. Ejemplo chico (3 puntos) para entender el método

Datos: (x, y) = (0, 1), (1, 2), (2, 2). Buscamos y = a·x + b.

**Paso 1. La función de error.**
S(a, b) = (1 − b)² + (2 − a − b)² + (2 − 2a − b)²

**Paso 2. Derivadas parciales** (regla de la cadena: derivas el cuadrado y multiplicas por la
derivada de lo de adentro).
- ∂S/∂a = −2·[ 0·(1−b) + 1·(2−a−b) + 2·(2−2a−b) ]
- ∂S/∂b = −2·[ (1−b) + (2−a−b) + (2−2a−b) ]

En general: ∂S/∂a = −2 Σ xᵢ(yᵢ − a·xᵢ − b) y ∂S/∂b = −2 Σ (yᵢ − a·xᵢ − b).

**Paso 3. Igualar a cero** y ordenar. Salen las **ecuaciones normales**:
- a·Σx² + b·Σx = Σxy
- a·Σx  + b·n  = Σy

**Paso 4. Tabla de sumatorias.**

| x | y | x² | x·y |
|---|---|---|---|
| 0 | 1 | 0 | 0 |
| 1 | 2 | 1 | 2 |
| 2 | 2 | 4 | 4 |
| **Σx=3** | **Σy=5** | **Σx²=5** | **Σxy=6** |  (n = 3)

**Paso 5. Resolver el sistema 2×2.**
5a + 3b = 6 y 3a + 3b = 5. Con las fórmulas:
- a\* = (n·Σxy − Σx·Σy) / (n·Σx² − (Σx)²) = (3·6 − 3·5)/(3·5 − 9) = 3/6 = **0.5**
- b\* = (Σy − a\*·Σx)/n = (5 − 1.5)/3 = **7/6 ≈ 1.167**

**Paso 6. Error mínimo.** Predicciones: 1.167, 1.667, 2.167. Errores: −0.167, 0.333, −0.167.
S = 0.0278 + 0.1111 + 0.0278 = **0.1667**.

**Paso 7. Hessiano** (derivar otra vez las parciales):
- S_aa = 2Σx² = 10, S_bb = 2n = 6, S_ab = 2Σx = 6
- H = [[10, 6], [6, 6]], D = det H = 10·6 − 6·6 = **24 > 0** y S_aa = 10 > 0 → **mínimo**.

Regla: D > 0 y S_aa > 0 → mínimo. D > 0 y S_aa < 0 → máximo. D < 0 → punto de silla. D = 0 → no concluye.

Nota: H no depende de a ni de b, así que S es un paraboloide: **el mínimo es único y global**.

---

## Parte 2. Con nuestros datos (lo que entregan)

Datos: n = 525 ensayos (15 participantes × 7 ángulos × 5). x = ángulo en grados, y = tiempo en ms.

**Paso 1. Sumatorias** (del script, o con una hoja de cálculo para que cada uno lo verifique):

| n | Σx | Σy | Σx² | Σxy |
|---|---|---|---|---|
| 525 | 47 250 | 470 089.6 | 6 142 500 | 47 316 603 |

**Paso 2. Denominador común.**
D₀ = n·Σx² − (Σx)² = 525·6 142 500 − 47 250² = 3 224 812 500 − 2 232 562 500 = **992 250 000**

**Paso 3. Pendiente.**
Numerador = n·Σxy − Σx·Σy = 525·47 316 603 − 47 250·470 089.6 = 24 841 216 575 − 22 211 733 600 = 2 629 482 975
**a\* = 2 629 482 975 / 992 250 000 ≈ 2.6500 ms/°**

**Paso 4. Intercepto.**
b\* = (470 089.6 − 2.6500·47 250)/525 = (470 089.6 − 125 213.5)/525 ≈ **656.91 ms**

**Paso 5. Error mínimo.** Se puede calcular sin recorrer los 525 datos con
S_min = Σy² − a\*·Σxy − b\*·Σy, con Σy² = 576 252 338.14 → **S_min ≈ 142 057 260 ms²**

**Paso 6. Hessiano.**
H = [[2·6 142 500, 2·47 250], [2·47 250, 2·525]] = [[12 285 000, 94 500], [94 500, 1 050]]
D = 12 285 000·1 050 − 94 500² = 12 899 250 000 − 8 930 250 000 = **3 969 000 000 > 0** (= 4·D₀ ✔) y S_aa > 0 → **mínimo global**.

**Paso 7. Interpretar.**
- a\* ≈ 2.65 ms/°: el cerebro tarda ~2.65 ms más por cada grado de rotación → **1000/a\* ≈ 377 °/s** de velocidad de rotación mental.
- b\* ≈ 657 ms: tiempo base (ver, decidir, presionar) con la letra sin rotar.
- RMSE = √(S_min/n) ≈ 520 ms y R² = 1 − S_min/Σ(y−ȳ)² ≈ 0.085: el ángulo explica ~8.5 % de la variación. El efecto es real pero hay mucho ruido entre personas.

**Autoprueba:** con a\* y b\*, ∂S/∂a y ∂S/∂b deben dar ~0 (el script lo verifica: ≈ 1e-9).

---

## Parte 3. Respuestas cortas para la defensa

1. **¿Por qué al cuadrado?** Evita cancelaciones, castiga más los errores grandes y es derivable.
2. **Derivadas:** las de la Parte 1, paso 2.
3. **¿Qué significa ∇S = 0?** Plano tangente horizontal: no se puede bajar más en ninguna dirección.
4. **¿Por qué H es constante?** S es cuadrática en (a, b), así que sus segundas derivadas solo dependen de los x, no de a ni b.
5. **¿Cómo sabes que es mínimo?** D > 0 y S_aa > 0.
6. **¿Por qué elipses?** Cortar un paraboloide con planos horizontales da elipses; son alargadas porque a y b están correlacionados (Σx ≠ 0) y la superficie es mucho más empinada en `a` que en `b`.
7. **¿Qué son a\* y b\*?** Ms por grado y tiempo base.
8. **Residuos:** si no tienen patrón y están centrados en 0, el modelo lineal es razonable; aquí la dispersión crece con el ángulo.
9. **RMSE y R²:** error típico de ~520 ms; el ángulo explica ~8.5 %.
10. **Limitaciones:** 15 personas, no todos igual de rápidos, atípicos por distracción, la pendiente varía entre personas.
