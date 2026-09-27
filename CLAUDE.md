# Proyecto: Análisis de datos con equipo de agentes (Titanic)

Proyecto de demostración para un vídeo de YouTube sobre cómo montar un equipo de agentes en Claude Code (un orquestador y tres sub-agentes). Dataset de prueba: `titanic.csv` (891 pasajeros, con nulos y variables mixtas). Usuario hispanohablante: responder siempre en español.

## Estado actual (leer primero)
El flujo completo **ya se ejecutó el 2026-09-20** sobre el Titanic: limpieza, análisis y gráficos están hechos y verificados. No hace falta repetirlos salvo que el usuario lo pida. Para reproducirlos: `python scripts/01_limpieza.py`, luego `02_analisis.py` y `03_graficos.py` (funcionan desde cualquier carpeta; usar `PYTHONIOENCODING=utf-8` en Windows). Se comprobó que regeneran los 19 CSV idénticos byte a byte.

## Estructura del proyecto
```
titanic.csv                        Dataset original (NO tocar)
CLAUDE.md                          Esta memoria del proyecto
.claude/agents/                    Los 4 agentes reutilizables (ver abajo)
scripts/
  01_limpieza.py                   Fase 1: titanic.csv -> outputs/titanic_clean.csv
  02_analisis.py                   Fase 2: -> outputs/tables/*.csv
  03_graficos.py                   Fase 3: -> outputs/figures/*.png
outputs/
  titanic_clean.csv                891 filas x 15 columnas
  cleaning_report.md               Informe de limpieza
  analysis_report.md               Informe de análisis (11 secciones; la 10 lista los gráficos)
  tables/                          18 CSV con tasas, correlaciones y odds ratios
  figures/                         11 PNG + README.md (índice de gráficos)
```

## Equipo de agentes (`.claude/agents/`)
| Archivo | Rol | Entrega |
|---|---|---|
| `orchestrator.md` | Dirige, coordina y cuestiona; no hace el trabajo. Solo puede lanzar los otros tres (`Agent(data-cleaner, data-analyst, visualizer)`). | Resumen final al usuario |
| `data-cleaner.md` | Nulos, tipos, duplicados; nunca toca el original. | `outputs/<nombre>_clean.csv` + `cleaning_report.md` |
| `data-analyst.md` | EDA con cifras, n y pruebas estadísticas; recomienda gráficos. | `outputs/analysis_report.md` |
| `visualizer.md` | Gráficos en español, con n en cada barra. | `outputs/figures/*.png` + `README.md` |

- **Son genéricos**: no dependen del Titanic; sirven para otro dataset copiando `.claude/agents/` (o a `~/.claude/agents/` para usarlos en todos los proyectos).
- **Orden fijo**: limpieza -> análisis -> visualización. Cada sub-agente empieza sin contexto, así que el orquestador le pasa rutas de archivo y las reglas relevantes.
- **Puntos de control**: tras cada fase el orquestador lee los archivos (no solo el resumen), recalcula al menos una cifra y devuelve la entrega con una crítica concreta si falla (máx. 2 rondas por fase).
- **Cómo lanzarlo de verdad**: un sub-agente no puede lanzar otros, por eso el orquestador debe ser el agente principal: `claude --agent orchestrator` en esta carpeta y pedir, por ejemplo, "Analiza titanic.csv". `/agents` lista los cuatro.

## Cómo se ejecutó (importante para no repetir errores)
- Los agentes se crearon **durante** la sesión y Claude Code solo los registra al arrancar, así que no eran invocables por nombre. Se ejecutó como alternativa: la sesión principal actuó de orquestador y lanzó agentes genéricos (`general-purpose`) con la orden de leer y seguir el `.md` de cada especialista. En una sesión nueva deberían cargarse por nombre; **no se ha probado** `claude --agent orchestrator` de verdad.
- A los sub-agentes se les rechaza la herramienta Write para informes `.md` (deben devolverlos como texto). Por eso el orquestador guardó `analysis_report.md`. Si se repite, pedirles que devuelvan el informe como texto y guardarlo desde la sesión principal.
- Los sub-agentes dejaron primero sus scripts (`clean.py`, `eda.py`) en el directorio temporal; se trasladaron a `scripts/` con rutas relativas a la ubicación del script. Al lanzar agentes, indicar explícitamente que el código se guarde en `scripts/`.

## Resultados del análisis (resumen)
Supervivencia global 38,4 % (342 de 891). Detalle y n en `outputs/analysis_report.md`.
1. **Sexo**: mujeres 74,2 % (n=314) frente a hombres 18,9 % (n=577); OR ajustado 15,7.
2. **Clase**: 63,0 % (1ª), 47,3 % (2ª), 24,2 % (3ª).
3. **Sexo x clase**: mujeres de 1ª 96,8 % y de 2ª 92,1 %; mujeres de 3ª 50,0 %; hombres de 3ª 13,5 % y de 2ª 15,7 %.
4. **Niños 0-12**: 58,0 % (n=69) frente a 36,7 % del resto; robusto a la imputación (todas edades reales). La edad continua es débil.
5. **Tamaño del grupo**: solo 30,4 %, 2 a 4 personas 57,9 %, 5 o más 16,1 %.
6. **Tarifa y cabina**: en gran parte reflejo de la clase.
7. **Embarque**: la ventaja de C se explica sobre todo por la clase.

## Decisiones de limpieza (para no reabrirlas sin motivo)
- `Age` (177 nulos): mediana por Pclass x Sex + indicador `Age_imputada`. La imputación comprime la varianza; hacer sensibilidad con `Age_imputada == 0`.
- `Cabin` (687 nulos, 77 %): no se imputa; se crean `tiene_Cabin` (0/1) y `Deck`. Están muy ligadas a la clase: no presentarlas como efectos independientes.
- `Embarked` (2 nulos, pasajeros 62 y 830): moda `S` (suposición; impacto irrelevante).
- Sin duplicados. 15 pasajeros con `Fare` = 0 se conservan (pueden ser datos faltantes o tripulación). `Fare` podría ser el total del ticket compartido (no verificado).
- `PassengerId` como texto. En memoria `Survived` es `category` y **no admite `.mean()`**: para tasas usar la versión numérica (leer el CSV).

## Limitaciones a mencionar siempre
Son asociaciones, no causalidad. Tickets compartidos (344 pasajeros en 134 tickets) hacen que los p-valores estén sobreestimados. No hay corrección por comparaciones múltiples. Grupos con n < 20 se marcan con † en los gráficos.

## Reglas de datos
- **Inmutabilidad de los datos originales:** nunca modificar ni sobrescribir `titanic.csv`. Guardar los datos limpios en un archivo nuevo.
- **Validar el shape tras cada merge o transformación** que cambie filas o columnas, y comprobar que coincide con lo esperado.
- No inventar columnas: usar solo las que existen en el dataset o las que se derivan explícitamente.
- Al limpiar, documentar qué se hizo con los nulos y con los duplicados.
- Toda afirmación del análisis lleva su cifra y su n.

## Salidas
- Gráficos en `outputs/figures/`; datos limpios, informes y tablas en `outputs/`, nunca sobre el original.
- El código va en `scripts/` (no dejar scripts en directorios temporales).

## Estilo y entorno
- Idioma: español para explicaciones, comentarios y títulos de gráficos.
- Python con pandas 2.2.2, matplotlib 3.8.0, seaborn 0.13.2, scipy 1.11.4 y statsmodels. Windows 11: usar `PYTHONIOENCODING=utf-8`. Los gráficos usan backend `Agg` (sin ventana).

## Pendiente / ideas
- Añadir a los tres `.md` de `.claude/agents/` la regla "guarda el código en `scripts/NN_fase.py`" (se propuso al usuario y aún no se ha aplicado).
- Probar el flujo real con `claude --agent orchestrator` en una sesión nueva.
- Próximo vídeo: el guion prevé preguntar a la audiencia qué dataset analizar; los agentes ya sirven para otro.
