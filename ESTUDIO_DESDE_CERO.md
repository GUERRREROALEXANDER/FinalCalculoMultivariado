# ESTUDIO DESDE CERO — Mastery Insana (Meta 5.0)

> Lee esto de principio a fin. Al terminar debes poder: derivar todo a mano en el tablero, explicar cada número del proyecto, y responder cualquier pregunta trampa sin dudar.

---

## FASE 0. El mapa mental (5 min)

Todo el proyecto es UNA sola historia:

1. **Fenómeno:** girar mentalmente una letra toma más tiempo si está más rotada.
2. **Datos:** medimos (ángulo x, tiempo y) con nuestra app. n = 595 ensayos.
3. **Modelo:** proponemos recta y = ax + b.
4. **Pregunta matemática:** ¿qué (a, b) minimiza el error total S(a,b)?
5. **Herramienta:** Cálculo Multivariable (derivadas parciales → gradiente → Hessiano).
6. **Verificación:** código propio + librerías + geometría 3D + residuos + R².

Si te pierdes, vuelve a esta lista.

---

## FASE 1. El experimento (qué significan x, y, a, b)

| Símbolo | Qué es | Valor en nuestro proyecto |
|---|---|---|
| x | ángulo de la letra R | 0°, 30°, 60°, 90°, 120°, 150°, 180° |
| y | tiempo de respuesta (solo aciertos) | media 930.33 ms |
| a* | ms extra por cada grado | **2.7467 ms/°** |
| b* | tiempo base a 0° (ver + decidir + pulsar) | **683.12 ms** |
| ω | velocidad de rotación mental = 1000/a* | **364.1 °/s** |

Ecuación final: **t(θ) = 683.12 + 2.75·θ** (ms).

Contraste Cerebro vs CPU (pregunta fija de conclusiones):
- Cerebro: analógico, tiempo crece con θ (pendiente 2.75).
- Computador: matriz R(θ), tiempo O(1), pendiente 0.

---

## FASE 2. Por qué el error es S(a,b) = Σ(yᵢ − axᵢ − b)²

- Residuo: eᵢ = yᵢ − (axᵢ + b) (observado menos predicho).
- ¿Por qué NO Σeᵢ? Se cancelan + y − (infinitas rectas malas dan 0).
- ¿Por qué NO Σ|eᵢ|? Tiene picos, no es derivable en 0.
- ¿Por qué SÍ Σeᵢ²? Es suave, penaliza errores grandes, tiene mínimo único analítico. S ≥ 0 siempre.

**Idea clave:** los datos (xᵢ, yᵢ) están FIJOS. Las variables son (a, b). Cada punto (a,b) = una recta candidata. S(a,b) = altura del paisaje 3D. Buscamos el fondo del valle.

---

## FASE 3. Derivación completa a mano (la escribes en el tablero)

### Paso 1 — Parciales (regla de la cadena)

S(a,b) = Σ (yᵢ − axᵢ − b)²

Respecto a a (b constante, derivada interna = −xᵢ):
> ∂S/∂a = Σ 2(yᵢ − axᵢ − b)·(−xᵢ) = **−2 Σ xᵢ(yᵢ − axᵢ − b)**

Respecto a b (a constante, derivada interna = −1):
> ∂S/∂b = Σ 2(yᵢ − axᵢ − b)·(−1) = **−2 Σ (yᵢ − axᵢ − b)**

### Paso 2 — Gradiente = 0 (ecuaciones normales)

∇S = (∂S/∂a, ∂S/∂b) = (0, 0). Divides entre −2 y distribuyes (recuerda Σb = n·b):

> (Σxᵢ²)a + (Σxᵢ)b = Σxᵢyᵢ ... (Ec.1)
> (Σxᵢ)a + n·b = Σyᵢ ... (Ec.2)

Significado geométrico: en el mínimo el **plano tangente a z = S(a,b) es horizontal**.

### Paso 3 — Resolver el sistema 2×2

De Ec.2: **b = ȳ − a·x̄** → la recta óptima SIEMPRE pasa por el centroide (x̄, ȳ).

Sustituyes en Ec.1, multiplicas por n, agrupas a:

> **a* = [n·Σxᵢyᵢ − Σxᵢ·Σyᵢ] / [n·Σxᵢ² − (Σxᵢ)²]**
> **b* = (Σyᵢ − a*·Σxᵢ) / n**

Denominador D₀ = n·Σxᵢ² − (Σxᵢ)² = n·Σ(xᵢ − x̄)² > 0 (Cauchy-Schwarz, si hay ≥2 x distintos).

### Paso 4 — Hessiano (demostrar que es mínimo global)

Segundas derivadas:
> S_aa = 2Σxᵢ², S_bb = 2n, S_ab = S_ba = 2Σxᵢ

> H = [[2Σxᵢ², 2Σxᵢ],[2Σxᵢ, 2n]], D = det(H) = 4·D₀

Criterio: si **D > 0 y S_aa > 0 → mínimo local**. Como H es CONSTANTE (no depende de a,b), la superficie es paraboloide elíptico convexo → **mínimo único y global**.

Con nuestros datos: H = [[13 923 000, 107 100],[107 100, 1190]], D = 5 097 960 000 > 0, S_aa > 0. λ₁ = 366.13, λ₂ = 1.39×10⁷ (ambos > 0, definida positiva). ∇S(a*,b*) ≈ (0,0) con error 10⁻⁹.

---

## FASE 4. Los números (memoriza estos 6)

- n = 595 (17 personas × 35 ensayos; 85 por ángulo)
- Σx = 53 550, Σy = 553 544.9, Σx² = 6 961 500, Σxy = 55 702 551.0
- D₀ = 1 274 490 000
- a* = 2.746737 ms/°, b* = 683.1213 ms
- S_min = 156 163 296.22 ms²
- RMSE crudo = 512.3 ms, R² crudo = 0.0938 | RMSE medias = 29.7 ms, R² medias = 0.9685

### Atajo de 60 segundos (tabla K=7, MISMO resultado)

Como el diseño es balanceado (m=85 por ángulo), S(a,b) = SS_intra + 85·S_medias(a,b). SS_intra no depende de (a,b), su gradiente es 0. Por eso con solo 7 filas sale idéntico:

Σx=630, Σȳ=6512.30, Σx²=81 900, Σxȳ=655 324.13
D₀ = 7(81900) − 630² = 176 400
a* = [7(655324.13) − 630(6512.30)]/176400 = **2.746737** ✓

---

## FASE 5. Geometría 3D (qué decir de cada figura)

- **03_superficie:** paraboloide elíptico z = S(a,b), fondo en (a*, b*).
- **04_trazas:** sección transversal = corte con b = b₀ fijo (parábola). Traza óptima = la que pasa por el mínimo (b₀ = b*). Vértice: a_vértice(b₀) = a* − (Σx/Σx²)(b₀ − b*).
- **05_curvas_nivel:** elipses **inclinadas** porque S_ab = 107 100 ≠ 0 (x no centrada). **Alargadas** porque λ₂/λ₁ ≈ 38 029 → elipse ~195 veces más larga que ancha (√38 029). No confundir con S_aa/S_bb ≈ 11 700 (sensibilidad por unidad de a vs. de b). Centrar x̃ = x − 90° → H diagonal → elipses derechas.
- **−∇S:** perpendicular a las curvas de nivel (prueba: S(a(t),b(t)) = k → d/dt = ∇S·r′ = 0), apunta al valle. Eso anima la demo HTML.

---

## FASE 6. Residuos y R² dual (la pregunta que más tumba)

- eᵢ = yᵢ − (a*xᵢ + b*). Media ≈ 0 (10⁻¹³). Sin patrón curvo → lineal OK. Dispersión crece con x (heterocedasticidad: a 150° hay más varianza). Atípico fila 262 (P09, e = +5015 ms).
- **¿Por qué R² crudo = 9.38% y en medias = 96.85%?** El 99.66% del error mínimo (SS_intra = 1.556×10⁸, = 90.3% de la varianza total) es variación DENTRO del mismo ángulo. OJO, no todo es "entre personas": solo 1/3 (32%) son personas rápidas vs lentas (P07 base 384 ms vs P10 base 1180 ms); 2/3 (68%) es la misma persona variando de ensayo a ensayo. Ningún modelo f(x) puede predecir eso.
- **El argumento más fuerte:** 16 de 17 personas, cada una por separado, tienen pendiente > 0 (prueba de signos p = 0.0003). Con un tiempo base por persona (S(a, b₁…b₁₇), 18 variables, ∇S = 0): MISMO a* = 2.7467 y R² sube a 0.38. Al promediar por ángulo el ruido se cancela y la ley lineal explica el 96.85% (p = 0.00006).
- RMSE: 512.3 ms (crudo) vs 29.7 ms (medias).

---

## FASE 7. Opciones A–D (una frase cada una)

- **A (sensibilidad):** ruido ±25 ms × 500 sims → σ_a = 0.60%, σ_b = 0.26%. Modelo robusto.
- **B (atípicos):** sin fila 262 → a* = 2.606, RMSE 469.5. Sin 6 ensayos >3000 ms → a* = 2.409, RMSE 409.3, R² = 0.1103. Conclusión: atípicos inflan pero no rompen la ley.
- **C (cuadrático):** y = 0.00304x² + 2.199x + 696.81, R² = 0.0941 (+0.0003). Nada. Parsimonia → lineal gana.
- **D (tamaño N):** a* se estabiliza en 2.65–2.75 desde N ≥ 10 (n ≥ 350).

---

## FASE 8. Preguntas trampa (respóndelas en voz alta)

1. **¿Mismo x en todos los datos?** D₀ = 0, D = 0, infinitas soluciones (recta ax₀+b = ȳ). Superficie = canaleta infinita (cilindro parabólico), no tazón.
2. **¿Por qué elipses inclinadas / cómo enderezarlas?** Por S_ab ≠ 0. Centrar x̃ = x − 90° → H diagonal.
3. **¿Pendiente de la tangente a S(a, b₀)?** g′(a) = ∂S/∂a(a, b₀). Vértice donde = 0.
4. **¿Por qué ∇S ⊥ curvas de nivel?** Regla de la cadena: ∇S·r′ = dS/dt = 0.
5. **¿R² bajo = modelo malo?** No: SS_intra domina; en medias R² = 96.85% con los mismos (a*, b*), y 16/17 personas tienen pendiente > 0.
6. **¿Por qué 17 personas? ¿Cómo eligieron los datos?** Base de 15 con el protocolo; se sumaron 2 personas nuevas, y lo admitimos: se eligieron mirando su ajuste. Por eso reportamos con las tres reglas: 15 → a* = 2.65, 17 → 2.75, todo (n = 875) → 2.41. Quitando a cualquier persona, a* entre 2.36 y 2.92. La conclusión no cambia.
7. **¿Las flechas de 05_curvas_nivel son de verdad −∇S, con escalas tan distintas?** Sí: se calculan en las variables del dibujo (X = a·p_a, Y = b·p_b; regla de la cadena: ∂S/∂X = S_a/p_a). Es la misma función reescalada, por eso se ven ⊥ a las elipses. En unidades crudas S_a ≫ S_b y la flecha saldría casi horizontal.

---

## FASE 9. Checklist final antes del martes

- [ ] Escribo la derivación completa sin mirar (Fase 3).
- [ ] Recito los 6 números de memoria (Fase 4).
- [ ] Hago la tabla K=7 en calculadora en <60 s.
- [ ] Explico cada figura en 30 s (Fase 5).
- [ ] Respondo las 7 trampas en voz alta (Fase 8).
- [ ] Pruebo la demo HTML en el PC de exposición.
- [ ] Nombres reales en slides + PDF recompilado.

**Fórmulas de bolsillo:** S = Σ(y−ax−b)² · ∂S/∂a = −2Σx(y−ax−b) · ∂S/∂b = −2Σ(y−ax−b) · a* = [nΣxy−ΣxΣy]/D₀ · b* = ȳ − a*x̄ · H = [[2Σx²,2Σx],[2Σx,2n]] · D = 4D₀ > 0.
