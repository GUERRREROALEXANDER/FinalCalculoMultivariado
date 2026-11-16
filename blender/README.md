# Visuales 3D en Blender (opcional, para las slides)

Todo se calculó con los datos reales de `codigo/resultados.txt` (n = 595):
Σx = 53 550 · Σy = 553 544.9 · Σx² = 6 961 500 · Σxy = 55 702 551 · Σy² = 687 301 826.87
→ a* = 2.746737 ms/° · b* = 683.1213 ms · S_mín = 156 163 296.22 ms² (verificado).

## Archivos

| Archivo | Qué es | Dónde usarlo |
|---|---|---|
| `renders/R/R_normal_000.png` … `R_normal_180.png` | R 3D a 0°, 30°, …, 180° (giro horario) | Slide 2 (experimento) |
| `renders/R/R_espejo_000.png` … `R_espejo_180.png` | La misma R en espejo | Slide 2 |
| `renders/R_lamina_7x2.png` | Las 14 en una lámina con rótulos (Normal → F, Espejo → J) | Slide 2, lista para pegar |
| `renders/paraboloide/S_superficie_minimo.png` | Superficie S(a,b), mínimo, plano tangente horizontal (∇S = 0), curvas de nivel y trazas | Slides "S es un valle" / "Mínimo ⇒ gradiente cero" |
| `renders/paraboloide/S_descenso_gradiente_0001-0240.mp4` | Video 10 s: bolita bajando por −∇S hasta el mínimo | Slide del gradiente / Hessiano |
| `renders/paraboloide/S_descenso_final.png` | Último cuadro del video (imagen fija) | Respaldo si no corre el video |
| `renders/elipses/elipses_inclinadas_x_grados.png` | Curvas de nivel con x en grados (∂²S/∂a∂b = 2Σx ≠ 0) | Slide "¿Por qué las elipses están inclinadas?" |
| `renders/elipses/elipses_alineadas_x_centrado.png` | Las mismas con x − 90° (∂²S/∂a∂b = 0) | Misma slide |
| `renders/elipses/elipses_centrado_0001-0144.mp4` | Video 6 s del paso de inclinadas a alineadas | Misma slide |
| `r_rotacion.blend`, `paraboloide.blend`, `paraboloide_descenso.blend`, `elipses_centradas.blend` | Escenas fuente | Para re-renderizar |

## Qué es exacto (por si preguntan en la sustentación)

- **R:** misma fuente que la app (Arial Bold) y mismo orden de transformaciones que `app/index.html`: `rotate(θ) scaleX(-1)` → primero espejo, luego giro horario.
- **Superficie:** z = 0.7·S(a,b)/10⁸ con el piso en S = 0 (el eje vertical no está recortado). Escala de pantalla: X = a − 3, Y = (b − 700)/100.
- **Curvas de nivel:** elipses exactas a partir de los valores propios de H/2 (error relativo ~10⁻¹⁵), niveles S = S_mín·(1 + 0.04k²).
- **Plano tangente:** horizontal en (a*, b*, S_mín). Como S es convexa queda debajo de la superficie salvo en el mínimo; por eso la superficie es semitransparente.
- **Bolita:** sigue la curva de máximo descenso −∇S integrada con RK4 desde (a, b) = (−0.6, 360). Igual que la figura 05, el gradiente se toma en las variables de pantalla, así el camino es perpendicular a las elipses dibujadas. La flecha mide |∇S| (proporcional) y llega a 0 en el mínimo. El camino gira ~90°: primero baja rápido por la dirección del valor propio grande y luego avanza lento por el valle alargado (Hessiano mal condicionado). La velocidad de la animación es suavizada; la que es real es la forma del camino.
- **Centrado x − 90°:** es un cizallamiento β = b + 90·t·a. Cada cuadro intermedio es el problema real con x − 90t, no una mezcla visual. En t = 1 la superficie coincide con el problema centrado (error 10⁻¹⁵), el término cruzado es 0, a* no cambia y β* = ȳ = 930.33 ms. La superficie se ve más plana al final porque, en el mismo rango de pantalla, la dirección de β es la de curvatura chica (2n frente a 2Σx̃²).

Volver a renderizar: `blender -b <archivo>.blend -a` (videos) o abrir el `.blend` y pulsar F12.
