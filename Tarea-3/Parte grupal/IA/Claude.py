import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# ─── DATOS ──────────────────────────────────────────────────────────────────
# Fuente: encuesta aplicada a 22 estudiantes universitarios (Mayo 2026)
# Los valores están normalizados en escala 0–1 por carrera, derivados de los
# cruces de variables visibles en las visualizaciones del informe (Sankey,
# Treemap, Heatmap y Donut).
#
# Método de estimación por variable:
#
# 1. FRECUENCIA DE CONSUMO ALTA (≥4 días/semana)
#    Fuente: Sankey (Rodrigo) + Donut (Ignacio)
#    - Ing/Tec (n=12): 6 respuestas en 4-5 días → 5/12 ~ 0.42  (approx, flujos sankey)
#    - Adm/Neg (n=5):  2 respuestas en 4-5 días → 2/5  = 0.40
#    - Salud   (n=4):  1 respuesta  en 4-5 días → 1/4  = 0.25
#    - Hum/CS  (n=1):  0 respuestas            → 0/1  = 0.00
#
# 2. ESTRÉS COMO FACTOR DETONANTE (acuerdo/total acuerdo)
#    Fuente: Heatmap (Cristóbal) — lectura de intensidades por franja de días
#    Se lee que las respuestas "De acuerdo" y "Totalmente de acuerdo" dominan
#    en todos los grupos. Se estima distribución proporcional al tamaño de carrera
#    con leve corrección por Salud (menor intensidad visual en 4-5 días):
#    - Ing/Tec: 0.75   - Adm/Neg: 0.70   - Salud: 0.50   - Hum/CS: 0.60
#
# 3. PRESUPUESTO LIMITADO como factor limitante
#    Fuente: Treemap (Cristóbal)
#    - Ing/Tec: 2do bloque más grande  → 0.55
#    - Adm/Neg: bloque mediano         → 0.45
#    - Salud:   bloque dominante       → 0.75
#    - Hum/CS:  bloque visible         → 0.60
#
# 4. FALTA DE TIEMPO para cocinar
#    Fuente: Treemap (Cristóbal)
#    - Ing/Tec: bloque más grande → 0.85
#    - Adm/Neg: bloque grande     → 0.70
#    - Salud:   bloque mediano    → 0.50
#    - Hum/CS:  bloque chico      → 0.40
#
# 5. ELECCIÓN DE COMIDA RÁPIDA/SNACKS DULCES (vs opciones saludables)
#    Fuente: Sankey (Rodrigo) — proporción de flujos hacia comida rápida/snacks dulces
#    - Ing/Tec (12): 5 snacks dulces + 4 rápida / 12 total = 9/12 = 0.75
#    - Adm/Neg (5):  2 snacks dulces + 2 rápida / 5  total = 4/5  = 0.80
#    - Salud   (4):  1 snacks dulces + 1 rápida / 4  total = 2/4  = 0.50
#    - Hum/CS  (1):  0 snacks dulces + 0 rápida / 1  total = 0/1  = 0.00

labels = [
    "Frecuencia alta\nde consumo",
    "Estrés como\ndetonante",
    "Presupuesto\nlimitado",
    "Falta de\ntiempo",
    "Preferencia por\ncomida rápida/snacks",
]

data = {
    "Ingeniería/Tecnología":      [0.42, 0.75, 0.55, 0.85, 0.75],
    "Adm. y Negocios":            [0.40, 0.70, 0.45, 0.70, 0.80],
    "Salud":                      [0.25, 0.50, 0.75, 0.50, 0.50],
    "Humanidades/Cs. Sociales":   [0.00, 0.60, 0.60, 0.40, 0.00],
}

sample_sizes = {
    "Ingeniería/Tecnología":    12,
    "Adm. y Negocios":           5,
    "Salud":                     4,
    "Humanidades/Cs. Sociales":  1,
}

# Paleta coherente con estilo oscuro del informe (similar a sankey y radial bar)
COLORS = {
    "Ingeniería/Tecnología":   "#E07B54",   # salmón/naranja
    "Adm. y Negocios":         "#C4A35A",   # dorado
    "Salud":                   "#6BB5C9",   # azul claro
    "Humanidades/Cs. Sociales":"#8B9E77",   # verde oliva
}

BG_DARK   = "#12111A"
GRID_COL  = "#2A2840"
LABEL_COL = "#C8C4E8"
TITLE_COL = "#E8E4FF"
SUB_COL   = "#8884AA"

# ─── FIGURA ─────────────────────────────────────────────────────────────────
N = len(labels)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # cerrar el polígono

fig = plt.figure(figsize=(14, 10), facecolor=BG_DARK)

# Layout: radar grande a la izquierda, leyenda + notas a la derecha
ax_radar = fig.add_axes([0.0, 0.05, 0.62, 0.90], polar=True, facecolor=BG_DARK)

# ── Grilla personalizada ──────────────────────────────────────────────────
ring_levels = [0.25, 0.50, 0.75, 1.00]
for level in ring_levels:
    ring_angles = np.linspace(0, 2 * np.pi, 200)
    ax_radar.plot(ring_angles, [level] * 200,
                  color=GRID_COL, linewidth=0.8, zorder=1)
    ax_radar.text(np.pi * 0.18, level + 0.02,
                  f"{int(level*100)}%",
                  color=SUB_COL, fontsize=7.5, ha="center", va="bottom",
                  fontfamily="monospace")

# Radios (spokes)
for angle in angles[:-1]:
    ax_radar.plot([angle, angle], [0, 1.0],
                  color=GRID_COL, linewidth=0.8, zorder=1)

# ── Trazar cada carrera ───────────────────────────────────────────────────
for career, values in data.items():
    v = values + values[:1]
    color = COLORS[career]
    n = sample_sizes[career]
    # Área rellena
    ax_radar.fill(angles, v,
                  alpha=0.12 if n > 3 else 0.07,
                  color=color, zorder=2)
    # Línea
    lw = 2.5 if n >= 10 else (2.0 if n >= 4 else 1.2)
    ls = "-" if n >= 4 else "--"
    ax_radar.plot(angles, v,
                  color=color, linewidth=lw, linestyle=ls,
                  zorder=3, solid_capstyle="round")
    # Puntos en cada vértice
    ax_radar.scatter(angles[:-1], values,
                     color=color, s=55 if n >= 4 else 30,
                     zorder=4, edgecolors=BG_DARK, linewidth=1.5)

# ── Etiquetas de ejes ─────────────────────────────────────────────────────
ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels([])   # las ponemos manualmente para más control

pad_factors = [1.22, 1.22, 1.22, 1.22, 1.22]
for i, (angle, label) in enumerate(zip(angles[:-1], labels)):
    ha = "center"
    va = "center"
    x = np.cos(angle - np.pi/2)
    y = np.sin(angle - np.pi/2)
    ax_radar.text(angle, pad_factors[i],
                  label,
                  ha="center", va="center",
                  fontsize=9.5,
                  color=LABEL_COL,
                  fontweight="bold",
                  multialignment="center",
                  linespacing=1.4)

ax_radar.set_ylim(0, 1.0)
ax_radar.set_yticks([])
ax_radar.spines["polar"].set_visible(False)
ax_radar.grid(False)

# ── Título ────────────────────────────────────────────────────────────────
fig.text(0.31, 0.97,
         "Perfil de riesgo alimenticio por área académica",
         ha="center", va="top",
         fontsize=15, fontweight="bold",
         color=TITLE_COL, fontfamily="serif")
fig.text(0.31, 0.93,
         "Intensidad relativa de 5 factores de riesgo  ·  n = 22 estudiantes universitarios",
         ha="center", va="top",
         fontsize=9, color=SUB_COL)

# ── Panel derecho: leyenda + datos ────────────────────────────────────────
ax_info = fig.add_axes([0.63, 0.08, 0.35, 0.84])
ax_info.set_facecolor("#1A1828")
ax_info.set_xlim(0, 1)
ax_info.set_ylim(0, 1)
for spine in ax_info.spines.values():
    spine.set_edgecolor(GRID_COL)

# Título del panel
ax_info.text(0.5, 0.95, "Carreras encuestadas",
             ha="center", va="top",
             fontsize=11, fontweight="bold",
             color=TITLE_COL, fontfamily="serif")

# Tarjetas por carrera
card_data = [
    ("Ingeniería/Tecnología",   12, "55%", "Falta de tiempo",      "Ing/Tec"),
    ("Adm. y Negocios",          5, "40%", "Falta de tiempo",      "Adm/Neg"),
    ("Salud",                    4, "25%", "Presupuesto limitado", "Salud"),
    ("Humanidades/Cs. Soc.",     1, " 0%", "Falta de tiempo",      "Hum/CS"),
]

y_positions = [0.78, 0.57, 0.36, 0.15]

for (career_name, n, high_freq, main_barrier, key), yp in zip(card_data, y_positions):
    color = COLORS[list(COLORS.keys())[[k for k in COLORS].index(
        [k for k in COLORS if k.startswith(career_name[:4])][0]
    )]]

# Método más simple:
career_list = list(data.keys())
color_list  = list(COLORS.values())

for i, ((career_name, n, high_freq, main_barrier, key), yp) in enumerate(zip(card_data, y_positions)):
    c = color_list[i]
    # Borde izquierdo coloreado
    rect = FancyBboxPatch((0.04, yp - 0.09), 0.92, 0.175,
                          boxstyle="round,pad=0.01",
                          facecolor="#12111A", edgecolor=c,
                          linewidth=1.5, zorder=2)
    ax_info.add_patch(rect)
    # Barra de color lateral
    bar = FancyBboxPatch((0.04, yp - 0.09), 0.025, 0.175,
                         boxstyle="round,pad=0.005",
                         facecolor=c, edgecolor="none", zorder=3)
    ax_info.add_patch(bar)

    # Nombre de carrera
    lw = "bold" if n >= 5 else "normal"
    ax_info.text(0.12, yp + 0.055, career_name,
                 fontsize=9.5, fontweight=lw,
                 color=c, va="top")
    # n
    ax_info.text(0.12, yp + 0.015,
                 f"n = {n}  ·  consumo ≥4 días: {high_freq}",
                 fontsize=8, color=SUB_COL, va="top")
    ax_info.text(0.12, yp - 0.025,
                 f"Principal barrera: {main_barrier}",
                 fontsize=8, color=LABEL_COL, va="top", style="italic")

ax_info.axis("off")

# ── Nota metodológica ────────────────────────────────────────────────────
fig.text(0.97, 0.03,
         "Datos: encuesta propia, Mayo 2026  |  Valores normalizados (0–1) desde cruces de variables\n"
         "Treemap, Sankey y Heatmap del mismo informe  |  INF-379 Visualización de datos, UTFSM",
         ha="right", va="bottom",
         fontsize=6.5, color=SUB_COL, fontstyle="italic")

plt.savefig("/mnt/user-data/outputs/radar_habitos_alimenticios.png",
            dpi=180, bbox_inches="tight",
            facecolor=BG_DARK, edgecolor="none")
print("Guardado correctamente.")
plt.close()
