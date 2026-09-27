# -*- coding: utf-8 -*-
"""Genera los 12 graficos de la seccion 10 de outputs/analysis_report.md.

Solo LEE outputs/titanic_clean.csv y outputs/tables/*.csv; no modifica ningun dataset.
Salida: PNG (dpi 150) en outputs/figures/.
Uso:  PYTHONIOENCODING=utf-8 python scripts/03_graficos.py
"""
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import FuncFormatter

OUT = Path(__file__).resolve().parents[1] / "outputs"
FIG = OUT / "figures"
TAB = OUT / "tables"
FIG.mkdir(parents=True, exist_ok=True)

SMALL = 20                      # umbral de n pequeno
INK, MUTED, GRID = "#222222", "#6b6b6b", "#dddddd"
EDGE = "#2b2b2b"
WARN = "#A6261D"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#888888",
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "hatch.linewidth": 0.8, "savefig.dpi": 150, "figure.dpi": 100,
})

# Paleta coherente (Okabe-Ito, apta para daltonismo) + textura como 2o canal
SEX = {"female": dict(color="#0072B2", hatch="", label="Mujer"),
       "male": dict(color="#E69F00", hatch="//", label="Hombre")}
NEUTRAL = dict(color="#4C6A92", hatch="")
CABIN = {1: dict(color="#009E73", hatch="", label="Con cabina"),
         0: dict(color="#B5B5B5", hatch="..", label="Sin cabina")}
PORT = {"C": dict(color="#CC79A7", hatch="", label="Cherburgo (C)"),
        "Q": dict(color="#56B4E9", hatch="xx", label="Queenstown (Q)"),
        "S": dict(color="#8C8C8C", hatch="..", label="Southampton (S)")}
CLASE = {1: "1ª clase", 2: "2ª clase", 3: "3ª clase"}

# ----------------------------------------------------------------- datos
df = pd.read_csv(OUT / "titanic_clean.csv")
GLOBAL = df["Survived"].mean() * 100
df["Familia"] = df["SibSp"] + df["Parch"] + 1
AGE_LABELS = ["0-12", "13-18", "19-35", "36-50", "51+"]
df["Edad_grupo"] = pd.cut(df["Age"], [-np.inf, 12, 18, 35, 50, np.inf], labels=AGE_LABELS)
N_IMPUT = int(df["Age_imputada"].sum())            # 177
N_FARE0 = int((df["Fare"] == 0).sum())             # 15
real = df[df["Age_imputada"] == 0]


def rate(sub):
    return sub["Survived"].mean() * 100, len(sub)


def pct(x, d=1):
    return f"{x:.{d}f}".replace(".", ",") + " %"


def num(x, d=1):
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(str(round(float(x), 6))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    return f"{q}".replace(".", ",")


# ------------------------------------------------------------- utilidades
def style_axes(ax, ymax=118):
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, ymax)                           # eje desde 0; techo solo para etiquetas
    ax.set_yticks(range(0, 101, 20))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f} %"))
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def hline_global(ax, x_right=None, fs=8):
    ax.axhline(GLOBAL, color=MUTED, ls=":", lw=1.2, zorder=1)
    ax.annotate(f"Global\n{pct(GLOBAL)}", xy=(1.0, GLOBAL), xycoords=("axes fraction", "data"),
                xytext=(4, 0), textcoords="offset points", ha="left", va="center",
                fontsize=fs, color=MUTED, annotation_clip=False)


def draw_bars(ax, xs, rates, ns, width, style, fs=8.5):
    """Barras de tasa con % y n; n<SMALL -> relleno tenue + borde discontinuo + dagger."""
    for x, r, n in zip(xs, rates, ns):
        small = n < SMALL
        fc = to_rgba(style["color"], 0.30 if small else 1.0)
        ax.bar(x, r, width, facecolor=fc, edgecolor=EDGE, lw=0.9,
               ls="--" if small else "-", hatch=style["hatch"], zorder=2)
        ax.annotate(pct(r), (x, r), xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=fs, color=INK, fontweight="bold")
        ax.annotate(f"†n={n}" if small else f"n={n}", (x, r), xytext=(0, 3 + fs * 1.45),
                    textcoords="offset points", ha="center", va="bottom", fontsize=fs - 0.5,
                    color=WARN if small else MUTED, fontweight="bold" if small else "normal")


def legend_below(ax, handles, ncol=None, y=-0.16):
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, y),
              ncol=ncol or len(handles), frameon=False, fontsize=9)


def sex_handles():
    return [Patch(facecolor=v["color"], edgecolor=EDGE, hatch=v["hatch"], label=v["label"])
            for v in SEX.values()]


def finish(fig, name, title, subtitle=None, notes=(), small_note=True, top_pad=0.0):
    """Titulo (mensaje), subtitulo y nota al pie con cautelas; guarda el PNG."""
    W, H = fig.get_size_inches()
    notes = list(notes)
    if small_note:
        notes.append(f"† n < {SMALL}: grupo muy pequeño, estimación imprecisa (barra tenue con borde discontinuo). "
                     "n = tamaño del grupo. Asociaciones observadas, no causalidad.")
    width = int((W - 0.6) / 0.068)
    lines = []
    for n_ in notes:
        lines += textwrap.wrap(n_, width=width, subsequent_indent="   ") or [""]
    bottom_in = 0.22 + 0.165 * len(lines)
    tl = textwrap.wrap(title, width=int((W - 0.4) / 0.128))
    sub_y = 0.14 + 0.27 * len(tl) + 0.05
    top_in = sub_y + (0.25 if subtitle else 0) + 0.32 + top_pad
    fig.tight_layout(rect=[0, bottom_in / H, 1, 1 - top_in / H])
    fig.text(0.012, 1 - 0.14 / H, "\n".join(tl), fontsize=13.5, fontweight="bold", color=INK,
             ha="left", va="top", linespacing=1.15)
    if subtitle:
        fig.text(0.012, 1 - sub_y / H, subtitle, fontsize=9.5, color=MUTED, ha="left", va="top")
    fig.text(0.012, 0.10 / H, "\n".join(lines), fontsize=7.8, color=MUTED, ha="left", va="bottom",
             linespacing=1.35)
    fig.savefig(FIG / name, dpi=150, facecolor="white")
    plt.close(fig)
    print("OK", name)


# =============================================================== 1. sexo
def g01():
    fig, ax = plt.subplots(figsize=(7.5, 5.6))
    xs, r, n = [], [], []
    for i, s in enumerate(["female", "male"]):
        rr, nn = rate(df[df.Sex == s])
        draw_bars(ax, [i], [rr], [nn], 0.5, SEX[s])
        r.append(rr); n.append(nn)
    ax.set_xticks([0, 1], ["Mujeres", "Hombres"])
    ax.set_ylabel("Supervivencia (% de pasajeros del grupo)")
    style_axes(ax)
    hline_global(ax)
    finish(fig, "supervivencia_por_sexo.png",
           "Sobrevivió el 74,2 % de las mujeres frente al 18,9 % de los hombres",
           "Tasa de supervivencia por sexo (891 pasajeros); la línea punteada marca la tasa global",
           small_note=False,
           notes=["n = tamaño del grupo (ningún grupo con n < 20). Asociación observada, no causalidad; "
                  "el sexo es el factor más asociado con la supervivencia (V de Cramér = 0,54)."])


# ============================================================ 2+3. clase
def g02_03():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw=dict(width_ratios=[1, 1.35]))
    # panel izquierdo: por clase
    for i, c in enumerate([1, 2, 3]):
        rr, nn = rate(df[df.Pclass == c])
        draw_bars(a1, [i], [rr], [nn], 0.55, NEUTRAL)
    a1.set_xticks(range(3), [CLASE[c] for c in (1, 2, 3)])
    a1.set_title("Por clase", loc="left", fontsize=11, color=INK)
    a1.set_ylabel("Supervivencia (% de pasajeros del grupo)")
    style_axes(a1); hline_global(a1)
    # panel derecho: clase x sexo
    w = 0.36
    for j, s in enumerate(["female", "male"]):
        rs, ns_ = [], []
        for c in (1, 2, 3):
            rr, nn = rate(df[(df.Pclass == c) & (df.Sex == s)])
            rs.append(rr); ns_.append(nn)
        draw_bars(a2, np.arange(3) + (j - 0.5) * (w + 0.02), rs, ns_, w, SEX[s], fs=8)
    a2.set_xticks(range(3), [CLASE[c] for c in (1, 2, 3)])
    a2.set_title("Por clase y sexo", loc="left", fontsize=11, color=INK)
    style_axes(a2); hline_global(a2)
    legend_below(a2, sex_handles(), y=-0.09)
    finish(fig, "supervivencia_por_clase_y_sexo.png",
           "El sexo domina en las tres clases; las mujeres de 3ª pierden casi toda su ventaja (50,0 %)",
           "Tasa de supervivencia por clase (izquierda) y por clase y sexo (derecha)",
           small_note=False,
           notes=["n = tamaño del grupo (ningún grupo con n < 20). Los gráficos cruzan dos variables, pero "
                  "sexo y clase se distribuyen de forma desigual (491 de 891 pasajeros viajan en 3ª). "
                  "Asociaciones observadas, no causalidad."])


# ================================================== 4. edad completo/reales
def g04():
    fig, ax = plt.subplots(figsize=(10, 5.8))
    w = 0.38
    series = [("Todos los pasajeros (edades imputadas incluidas)", df,
               dict(color="#9CC3E0", hatch="..")),
              (f"Solo edades reales (excluye {N_IMPUT} imputadas)", real,
               dict(color="#0072B2", hatch=""))]
    for j, (lab, sub, st) in enumerate(series):
        rs, ns_ = zip(*[rate(sub[sub.Edad_grupo == g]) for g in AGE_LABELS])
        draw_bars(ax, np.arange(5) + (j - 0.5) * (w + 0.02), rs, ns_, w, st, fs=8)
    ax.set_xticks(range(5), AGE_LABELS)
    ax.set_xlabel("Grupo de edad (años)")
    ax.set_ylabel("Supervivencia (% de pasajeros del grupo)")
    style_axes(ax); hline_global(ax)
    legend_below(ax, [Patch(facecolor=s[2]["color"], edgecolor=EDGE, hatch=s[2]["hatch"], label=s[0])
                      for s in series], y=-0.17)
    finish(fig, "supervivencia_por_grupo_edad.png",
           "Los niños (0-12) sobreviven más (58,0 %) y excluir las edades imputadas apenas cambia el resultado",
           "Tasa de supervivencia por grupo de edad: análisis completo frente a solo edades reales",
           notes=[f"Los {N_IMPUT} pasajeros con edad imputada (mediana por clase y sexo) están en 19-35 y 36-50; "
                  "todos los de 0-12, 13-18 y 51+ tienen edad real, por lo que sus barras son idénticas. "
                  "La imputación comprime la variabilidad de la edad."])


# ======================================================= 5. edad x sexo
def g05():
    fig, ax = plt.subplots(figsize=(10, 5.8))
    w = 0.38
    for j, s in enumerate(["female", "male"]):
        rs, ns_ = zip(*[rate(real[(real.Sex == s) & (real.Edad_grupo == g)]) for g in AGE_LABELS])
        draw_bars(ax, np.arange(5) + (j - 0.5) * (w + 0.02), rs, ns_, w, SEX[s], fs=8)
    ax.set_xticks(range(5), AGE_LABELS)
    ax.set_xlabel("Grupo de edad (años)")
    ax.set_ylabel("Supervivencia (% de pasajeros del grupo)")
    style_axes(ax); hline_global(ax)
    legend_below(ax, sex_handles(), y=-0.17)
    finish(fig, "supervivencia_edad_x_sexo.png",
           "Los niños de ambos sexos sobreviven por igual (~58 %); los varones de 13-18 años solo un 8,8 %",
           f"Supervivencia por edad y sexo, solo edades reales (se excluyen las {N_IMPUT} edades imputadas; n = 714)",
           notes=[f"Solo edades reales (Age_imputada = 0): se excluyen las {N_IMPUT} imputadas. "
                  "Con n = 17, el 94,1 % de las mujeres de 51+ es muy impreciso."])


# ====================================================== 6. densidad edad
def g06():
    fig, ax = plt.subplots(figsize=(9, 5.4))
    bins = np.arange(0, 85, 5)
    spec = {1: ("Sobrevivieron", "#009E73", "-"), 0: ("No sobrevivieron", "#7A7A7A", "--")}
    for k, (lab, col, ls) in spec.items():
        a = real.loc[real.Survived == k, "Age"]
        w_ = np.full(len(a), 100 / len(a))
        ax.hist(a, bins=bins, weights=w_, histtype="stepfilled", color=to_rgba(col, 0.28),
                edgecolor=col, lw=0, zorder=2)
        ax.hist(a, bins=bins, weights=w_, histtype="step", color=col, lw=2, ls=ls, zorder=3,
                label=f"{lab} (n={len(a)}; mediana {num(a.median())} años)")
        ax.axvline(a.median(), color=col, lw=1.2, ls=ls, alpha=0.8, zorder=1)
    ax.set_xlim(0, 80)
    ax.set_xlabel("Edad (años; tramos de 5 años)")
    ax.set_ylabel("% de los pasajeros de cada grupo")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g} %"))
    ax.set_yticks(range(0, 19, 3))
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    finish(fig, "distribucion_edad_por_supervivencia.png",
           "La edad por sí sola casi no separa a supervivientes y no supervivientes",
           f"Distribución de la edad según supervivencia, solo edades reales (n = 714; se excluyen las {N_IMPUT} imputadas)",
           small_note=False,
           notes=[f"Solo Age_imputada = 0: se excluyen las {N_IMPUT} edades imputadas. Cada grupo suma 100 %, por lo que "
                  "las alturas son comparables aunque haya más no supervivientes. Las líneas verticales son las medianas "
                  "(28,0 años en ambos grupos; Mann-Whitney p = 0,16). Solo destaca un poco más de niños (0-5) entre "
                  "los supervivientes. Asociación observada, no causalidad."])


# ============================================================ 7. familia
def g07():
    fig, ax = plt.subplots(figsize=(9, 5.8))
    fam = df["Familia"].clip(upper=7)
    labels = ["1\n(solo)", "2", "3", "4", "5", "6", "7 o más"]
    rs, ns_ = zip(*[rate(df[fam == k]) for k in range(1, 8)])
    draw_bars(ax, range(7), rs, ns_, 0.6, NEUTRAL)
    ax.set_xticks(range(7), labels)
    ax.set_xlabel("Personas en el grupo familiar (pasajero + SibSp + Parch)")
    ax.set_ylabel("Supervivencia (% de pasajeros del grupo)")
    style_axes(ax); hline_global(ax)
    sub7 = df[df.Familia >= 7]
    finish(fig, "supervivencia_por_tamano_familia.png",
           "Máxima supervivencia con 4 personas (72,4 %); cae desde las 5 personas",
           "Tasa de supervivencia según el tamaño del grupo familiar a bordo",
           notes=["Tamaño = SibSp + Parch + 1. \"7 o más\" agrupa tamaños 7 (n=12), 8 (n=6) y 11 (n=7); "
                  f"en total {int(sub7.Survived.sum())} de {len(sub7)} sobreviven. "
                  "Los grupos de 5 o más son casi todos de 3ª clase (44 de 49 en tickets de 5+), así que el efecto "
                  "se mezcla con la clase."])


# ============================================================= 8. Fare
def g08():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 5.8), gridspec_kw=dict(width_ratios=[1.1, 1]))
    q = pd.read_csv(TAB / "tasa_por_cuartil_tarifa.csv")
    ranges = {"Q1": "0 – 7,90", "Q2": "7,93 – 14,45", "Q3": "14,46 – 31,00", "Q4": "31,28 – 512,33"}
    draw_bars(a1, range(4), q["tasa_pct"], q["n"], 0.6, NEUTRAL)
    a1.set_xticks(range(4), [f"{k}\n{ranges[k]}" for k in q["Fare_cuartil"]])
    a1.set_xlabel("Cuartil de tarifa (rango de Fare en £)")
    a1.set_ylabel("Supervivencia (% de pasajeros del grupo)")
    a1.set_title("Supervivencia por cuartil de tarifa", loc="left", fontsize=11)
    style_axes(a1); hline_global(a1)
    # boxplot Fare por clase, escala log simetrica (incluye Fare=0)
    data = [df.loc[df.Pclass == c, "Fare"] for c in (1, 2, 3)]
    bp = a2.boxplot(data, positions=range(3), widths=0.5, patch_artist=True,
                    medianprops=dict(color=INK, lw=1.8),
                    flierprops=dict(marker="o", ms=3, mfc="none", mec=MUTED, alpha=0.7))
    for b in bp["boxes"]:
        b.set(facecolor=to_rgba(NEUTRAL["color"], 0.55), edgecolor=EDGE)
    a2.set_yscale("symlog", linthresh=1)
    a2.set_ylim(0, 800)
    a2.set_yticks([0, 1, 5, 10, 50, 100, 500])
    a2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    a2.minorticks_off()
    a2.set_xticks(range(3), [f"{CLASE[c]}\nn={len(d)}\nmediana {num(d.median())} £" for c, d in zip((1, 2, 3), data)])
    a2.set_ylabel("Fare (£, escala logarítmica)")
    a2.set_title("Tarifa por clase: la tarifa refleja la clase", loc="left", fontsize=11)
    a2.spines[["top", "right"]].set_visible(False)
    a2.grid(axis="y", color=GRID, lw=0.8); a2.set_axisbelow(True)
    z = df[df.Fare == 0].Pclass.value_counts().sort_index()
    a2.annotate(f"{N_FARE0} pasajeros con Fare = 0\n({z[1]} en 1ª, {z[2]} en 2ª, {z[3]} en 3ª)",
                xy=(1, 0), xytext=(0.62, 0.115), textcoords="axes fraction", fontsize=8, color=WARN,
                ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=WARN, lw=0.8, relpos=(0.3, 0)))
    finish(fig, "tarifa_cuartiles_y_boxplot_por_clase.png",
           "Pagar más se asocia a sobrevivir más, pero la tarifa refleja sobre todo la clase",
           "Supervivencia por cuartil de tarifa (izquierda) y distribución de la tarifa por clase (derecha)",
           notes=["Fare puede ser el total del ticket compartido por varios pasajeros (344 pasajeros comparten 134 tickets); "
                  "no está verificado. Dentro de cada clase la relación con la supervivencia se atenúa (en 3ª no hay "
                  "diferencia, p = 0,20).",
                  f"Hay {N_FARE0} pasajeros con Fare = 0 (todos hombres; 1 sobrevive), posibles datos faltantes; se "
                  "mantienen. Por eso el boxplot usa escala logarítmica simétrica (el 0 se dibuja en la base)."])


# ============================================================ 9. cabina
def g09():
    fig, ax = plt.subplots(figsize=(9, 5.9))
    w = 0.36
    for j, cab in enumerate([0, 1]):
        rs, ns_ = zip(*[rate(df[(df.Pclass == c) & (df.tiene_Cabin == cab)]) for c in (1, 2, 3)])
        draw_bars(ax, np.arange(3) + (j - 0.5) * (w + 0.02), rs, ns_, w, CABIN[cab])
    share = [df.loc[df.Pclass == c, "tiene_Cabin"].mean() * 100 for c in (1, 2, 3)]
    ax.set_xticks(range(3), [f"{CLASE[c]}\n({pct(s)} tiene cabina)" for c, s in zip((1, 2, 3), share)])
    ax.set_ylabel("Supervivencia (% de pasajeros del grupo)")
    style_axes(ax); hline_global(ax)
    legend_below(ax, [Patch(facecolor=v["color"], edgecolor=EDGE, hatch=v["hatch"], label=v["label"])
                      for k, v in CABIN.items()][::-1], y=-0.17)
    n2 = len(df[(df.Pclass == 2) & (df.tiene_Cabin == 1)]); n3 = len(df[(df.Pclass == 3) & (df.tiene_Cabin == 1)])
    finish(fig, "supervivencia_clase_x_cabina.png",
           "La cabina no es independiente de la clase: casi solo la tiene 1ª clase, y en 2ª y 3ª son muy pocos",
           "Supervivencia según tenga o no cabina registrada, dentro de cada clase",
           notes=[f"En 2ª y 3ª clase solo hay {n2} y {n3} pasajeros con cabina (n muy pequeño): esas barras son "
                  "orientativas. Cabina y clase están relacionadas (81,5 % de 1ª frente a 8,7 % de 2ª y 2,4 % de 3ª) y "
                  "la ausencia de cabina puede ser un problema de registro, no de alojamiento.",
                  "Dentro de 1ª la diferencia por cabina es moderada (p ≈ 0,04); solo entre hombres de 1ª no es "
                  "significativa (p = 0,11)."])


# ========================================================== 10. embarque
def g10():
    fig, ax = plt.subplots(figsize=(10, 5.9))
    w = 0.26
    for j, p in enumerate(["C", "Q", "S"]):
        rs, ns_ = zip(*[rate(df[(df.Pclass == c) & (df.Embarked == p)]) for c in (1, 2, 3)])
        draw_bars(ax, np.arange(3) + (j - 1) * (w + 0.02), rs, ns_, w, PORT[p], fs=8)
    ax.set_xticks(range(3), [CLASE[c] for c in (1, 2, 3)])
    ax.set_ylabel("Supervivencia (% de pasajeros del grupo)")
    style_axes(ax); hline_global(ax)
    legend_below(ax, [Patch(facecolor=v["color"], edgecolor=EDGE, hatch=v["hatch"], label=v["label"])
                      for v in PORT.values()], y=-0.11)
    finish(fig, "supervivencia_clase_x_embarque.png",
           "La ventaja de Cherburgo se explica sobre todo por la clase: la diferencia por puerto solo se mantiene en 3ª",
           "Tasa de supervivencia por puerto de embarque dentro de cada clase",
           notes=["En 1ª y 2ª clase el puerto no marca diferencias claras (p = 0,28 y 0,69); en 3ª, Cherburgo (37,9 %) y "
                  "Queenstown (37,5 %) superan a Southampton (19,0 %). Q en 1ª (n=2) y en 2ª (n=3) no es interpretable. "
                  "Los 2 pasajeros sin puerto se imputaron como S."])


# ===================================================== 11. forest OR
def g11():
    t = pd.read_csv(TAB / "regresion_logistica_OR.csv")
    t = t[(t.modelo == "completo") & (t.variable != "Intercept")].set_index("variable")
    rows = [("Mujer (frente a hombre)", "fem", 1),
            ("2ª clase (frente a 1ª)", "C(Pclass)[T.2]", 1),
            ("3ª clase (frente a 1ª)", "C(Pclass)[T.3]", 1),
            ("Edad (por cada 10 años más)", "Age", 10),
            ("Tamaño del grupo familiar\n(por cada persona más)", "Familia", 1)]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for i, (lab, key, p) in enumerate(rows):
        y = len(rows) - 1 - i
        r = t.loc[key]
        o, lo, hi = r.OR ** p, r.IC95_inf ** p, r.IC95_sup ** p
        col = SEX["female"]["color"] if o > 1 else SEX["male"]["color"]
        ax.plot([lo, hi], [y, y], color=EDGE, lw=1.8, zorder=2)
        ax.plot(o, y, "D" if o > 1 else "o", ms=9, mfc=col, mec=EDGE, zorder=3)
        ax.annotate(f"OR {num(o, 2)}  (IC 95 %: {num(lo, 2)} a {num(hi, 2)})", xy=(1.02, y),
                    xycoords=("axes fraction", "data"), va="center", fontsize=9, color=INK)
    ax.axvline(1, color=MUTED, lw=1.2, ls="--", zorder=1)
    ax.set_xscale("log")
    ticks = [0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 25]
    ax.set_xticks(ticks, [num(v, 2).rstrip("0").rstrip(",") if v < 1 else f"{v:g}" for v in ticks])
    ax.minorticks_off()
    ax.set_xlim(0.04, 30)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
    ax.set_xlabel("Odds ratio (escala logarítmica); 1 = sin asociación")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.annotate("← menos probabilidad de sobrevivir", xy=(0.0, 1.03), xycoords="axes fraction", fontsize=8.5, color=MUTED)
    ax.annotate("más probabilidad de sobrevivir →", xy=(1.0, 1.03), xycoords="axes fraction", fontsize=8.5,
                color=MUTED, ha="right")
    # el ancho del margen derecho lo reserva finish() con un rect ajustado
    fig.subplots_adjust(right=0.66)
    W, H = fig.get_size_inches()
    notes = [f"Regresión logística con n = 891 (incluye las {N_IMPUT} edades imputadas): Supervivencia ~ clase + sexo + edad + "
             "tamaño familiar. Los OR de edad son por 10 años (OR anual 0,957). Con solo edades reales (n = 714) los resultados "
             "son casi idénticos. Cada OR está ajustado por las otras variables; son asociaciones, no causalidad, y los "
             "tickets compartidos hacen que las observaciones no sean independientes (los IC pueden ser algo optimistas).",
             "Rombo azul: OR > 1 (asociado a mayor supervivencia); círculo naranja: OR < 1."]
    lines = []
    for n_ in notes:
        lines += textwrap.wrap(n_, width=int((W - 0.6) / 0.068), subsequent_indent="   ")
    bottom_in = 0.22 + 0.165 * len(lines)
    fig.subplots_adjust(left=0.24, right=0.70, top=1 - 1.1 / H, bottom=(bottom_in + 0.75) / H)
    fig.text(0.012, 1 - 0.14 / H, "Sexo y clase pesan mucho más que la edad y el tamaño familiar",
             fontsize=13.5, fontweight="bold", ha="left", va="top")
    fig.text(0.012, 1 - 0.50 / H, "Odds ratio ajustados (modelo completo, n = 891) con intervalo de confianza del 95 %",
             fontsize=9.5, color=MUTED, ha="left", va="top")
    fig.text(0.012, 0.10 / H, "\n".join(lines), fontsize=7.8, color=MUTED, ha="left", va="bottom", linespacing=1.35)
    fig.savefig(FIG / "forest_plot_odds_ratios.png", dpi=150, facecolor="white")
    plt.close(fig)
    print("OK forest_plot_odds_ratios.png")


# ==================================================== 12. Spearman
def g12():
    c = pd.read_csv(TAB / "correlaciones_spearman.csv", index_col=0)
    order = ["Survived", "Sex_female", "Pclass", "Fare", "tiene_Cabin", "Familia", "Age", "SibSp", "Parch",
             "Age_imputada"]
    names = {"Survived": "Supervivencia", "Sex_female": "Mujer (sí = 1)", "Pclass": "Clase (1ª=1, 3ª=3)",
             "Fare": "Fare (tarifa)", "tiene_Cabin": "Tiene cabina", "Familia": "Tamaño del grupo familiar",
             "Age": "Edad", "SibSp": "Hermanos/cónyuge (SibSp)", "Parch": "Padres/hijos (Parch)",
             "Age_imputada": "Edad imputada"}
    m = c.loc[order, order]
    mask = np.triu(np.ones_like(m, dtype=bool), k=1)
    fig, ax = plt.subplots(figsize=(10.5, 8))
    cmap = LinearSegmentedColormap.from_list("div", ["#D55E00", "#F7F7F7", "#0072B2"])
    sns.heatmap(m, mask=mask, cmap=cmap, vmin=-1, vmax=1, center=0, annot=True, fmt=".2f",
                annot_kws=dict(fontsize=9), linewidths=1, linecolor="white", square=True,
                cbar_kws=dict(shrink=0.7, label="Correlación de Spearman"), ax=ax)
    for t in ax.texts:                                    # coma decimal
        t.set_text(t.get_text().replace(".", ","))
    lab = [names[k] for k in order]
    ax.set_xticks(np.arange(len(order)) + 0.5, lab, rotation=40, ha="right")
    ax.set_yticks(np.arange(len(order)) + 0.5, lab, rotation=0)
    ax.add_patch(Rectangle((0, 0), 1, len(order), fill=False, ec=INK, lw=2.2, clip_on=False))
    finish(fig, "correlacion_spearman.png",
           "Sexo y clase son las variables más ligadas a la supervivencia; Fare, cabina y clase están entrelazadas",
           "Correlación de Spearman entre variables (n = 891); recuadro = correlaciones con la supervivencia",
           small_note=False,
           notes=["Clase: 1 = 1ª, 3 = 3ª, por eso su correlación es negativa con la supervivencia, con Fare y con la cabina "
                  "(a peor clase, menos tarifa, menos cabina y menos supervivencia). Fare-Clase = -0,69 y Cabina-Clase = "
                  "-0,68: no son factores independientes.",
                  f"Fare puede ser el total de un ticket compartido (no verificado) y hay {N_FARE0} pasajeros con Fare = 0. "
                  f"La cabina tiene un 77 % de nulos (no aleatorios); la edad incluye {N_IMPUT} valores imputados. "
                  "Correlaciones = asociaciones, no causalidad."])


if __name__ == "__main__":
    # comprobaciones cruzadas con las tablas del analista
    t = pd.read_csv(TAB / "tasa_clase_x_sexo.csv")
    for _, r in t.iterrows():
        rr, nn = rate(df[(df.Pclass == r.Pclass) & (df.Sex == r.Sex)])
        assert nn == r.n and abs(rr - r.tasa_pct) < 0.06, r
    for f, sub in (("tasa_por_edad_completo", df), ("tasa_por_edad_solo_reales", real)):
        for _, r in pd.read_csv(TAB / f"{f}.csv").iterrows():
            rr, nn = rate(sub[sub.Edad_grupo == r.Edad_grupo])
            assert nn == r.n and abs(rr - r.tasa_pct) < 0.06, (f, r)
    for _, r in pd.read_csv(TAB / "tasa_clase_x_cabina.csv").iterrows():
        rr, nn = rate(df[(df.Pclass == r.Pclass) & (df.tiene_Cabin == r.tiene_Cabin)])
        assert nn == r.n and abs(rr - r.tasa_pct) < 0.06, r
    for _, r in pd.read_csv(TAB / "tasa_clase_x_embarque.csv").iterrows():
        rr, nn = rate(df[(df.Pclass == r.Pclass) & (df.Embarked == r.Embarked)])
        assert nn == r.n and abs(rr - r.tasa_pct) < 0.06, r
    assert len(df) == 891 and N_IMPUT == 177 and N_FARE0 == 15
    print("Comprobaciones con tablas OK")
    for f in (g01, g02_03, g04, g05, g06, g07, g08, g09, g10, g11, g12):
        f()
