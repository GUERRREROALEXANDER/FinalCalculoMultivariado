# Guía para agentes

## 1) Qué es el proyecto
NeuroCode es el proyecto final de Cálculo Multivariable de Ingeniería de Software,
UCC Pasto. Mide tiempos de rotación mental y ajusta y = ax + b minimizando S(a,b)
mediante derivadas parciales, gradiente y Hessiano.

## 2) Estructura de carpetas
- `app/`: aplicación HTML de captura de tiempos y exportación CSV.
- `csvs/`: datos oficiales; `extra/` y `txt/` contienen candidatos y respaldos.
- `codigo/`: ajuste, auditoría, resultados y plantilla del simulador.
- `codigo/lab/`: módulos JavaScript y pruebas en `tests/`.
- `codigo/studio/` y `codigo/vendor/`: vista 3D y dependencias locales.
- `figuras/`: gráficos generados y `superficie_interactiva.html`.
- `presentacion/`: diapositivas, fuentes y recursos locales.
- `informe/`: desarrollo manual y guía de sustentación.
- `blender/`: escenas `.blend`, renders y videos opcionales.
No existe `docs/`; consultar también `README.md`, `requisitos.md`, `rubrica.md`
y `ESTUDIO_DESDE_CERO.md`.

## 3) Requisitos e instalación
- Python **3.10+**, según el README. Instalación documentada completa:
  `pip install numpy matplotlib scipy pandas plotly`.
- Node.js y `npx` para Marp; las pruebas usan `node:test`.
  El repositorio no fija versión de Node ni de los paquetes Python/Marp.
- Navegador para la captura y el laboratorio; Blender opcional, sin versión fijada.
- Java y Terraform no se usan ni tienen versiones declaradas en el repositorio.
- No hay `package.json`, archivo de requisitos Python ni lockfile de instalación.

## 4) Cómo ejecutarlo y cómo probarlo
Desde la raíz, abrir `app/index.html` en el navegador para capturar datos.
Abrir `figuras/superficie_interactiva.html` para usar el laboratorio sin internet.

Regeneración documentada (sobrescribe informes, figuras y simulador):
```bash
python3 codigo/auditar_extras.py > codigo/reporte_extras.md
python3 codigo/ajuste.py > codigo/resultados.txt
```
Pruebas existentes del laboratorio, con el ejecutor integrado de Node:
```bash
node --test codigo/lab/tests/*.test.mjs
```
Recompilar las diapositivas, según el README (sintaxis Bash o PowerShell 7):
```bash
cd presentacion && npx @marp-team/marp-cli slides.md --pdf --allow-local-files --no-stdin && npx @marp-team/marp-cli slides.md --html --allow-local-files --no-stdin
```
Comprobar visualmente captura, controles y descenso del laboratorio.
El ajuste compara el algoritmo propio con `numpy.polyfit` y `scipy.stats.linregress`.
La auditoría devuelve 0 si supera sus umbrales y 1 si no los supera.

## 5) Reglas para agentes
- Commits solo a nombre del autor; sin `Co-Authored-By` ni atribución de IA.
- No subir `.env`, credenciales, claves ni otros secretos; revisar el diff.
- Ejecutar pruebas pertinentes antes de afirmar que algo está listo;
  informar resultados, fallos y verificaciones pendientes.
- Conservar CSV crudos y respaldos; no corregir sus IDs ni eliminar atípicos.
- No sobrescribir escenas Blender, PDFs del docente ni trabajo ajeno sin encargo.
- Editar `codigo/simulador_template.html` y módulos fuente para cambiar el laboratorio;
  el HTML de `figuras/` se regenera. Conservar dependencias locales y sus licencias.
- Respetar `requisitos.md` y `rubrica.md`; no inventar fuentes, datos ni resultados.

## 6) Notas y trampas conocidas
- Base oficial documentada: 17 participantes, 595 ensayos; cada ángulo tiene 85.
  El reporte de extras guardado describe una base anterior de 15 participantes.
- El ajuste identifica participantes por nombre de archivo: hay IDs internos repetidos.
- R² crudo = 0.0938 y R² de las siete medias = 0.9685: no intercambiarlos.
- La incorporación de dos participantes tuvo sesgo de selección reconocido en el README;
  mantener esa aclaración y la comparación de robustez.
- Sin Plotly, el ajuste omite el HTML interactivo y avisa por stderr.
- Centrar x − 90° conserva la pendiente, pero cambia el intercepto a β = b + 90a.
- En Blender, el descenso usa variables de pantalla y velocidad visual suavizada;
  no interpretar la velocidad de animación como tiempo físico.
