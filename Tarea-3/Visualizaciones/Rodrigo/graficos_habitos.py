import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe

# ── DATA ──────────────────────────────────────────────────────────────────────
data = {
    "factor": {
        "Falta de tiempo\npara cocinar": 10,
        "Presupuesto\nlimitado": 8,
        "Poca oferta\nsaludable": 2,
        "Falta de\nmotivación": 1,
        "Falta de habilidades\npara cocinar": 1,
    },
    "dias_comida_rapida": {
        "0-1 días": 3,
        "2-3 días": 12,
        "4-5 días": 6,
        "6-7 días": 1,
    },
    "carrera_alimento": {
        "Ingeniería/Tecnología": {
            "Snacks dulces/galletas": 5,
            "Comida rápida/Chatarra": 4,
            "Snacks salados/papas": 2,
            "Fruta/Lácteos": 1,
        },
        "Administración\ny Negocios": {
            "Comida rápida/Chatarra": 2,
            "Snacks dulces/galletas": 1,
            "Snacks salados/papas": 1,
            "Prefiero no comer nada": 1,
        },
        "Salud": {
            "Fruta/Lácteos": 1,
            "Snacks dulces/galletas": 1,
            "frutos secos": 1,
            "Comida rápida/Chatarra": 1,
        },
        "Humanidades o\nCiencias sociales": {
            "Snacks salados/papas": 1,
        },
    },
}

# ── PALETA ────────────────────────────────────────────────────────────────────
BG      = "#0F0F1A"
ACCENT  = "#E8D5A3"
COLORS  = ["#F4845F", "#F2C078", "#86C5DA", "#A8E6CF", "#D4A5F5"]
GRAY    = "#2A2A3E"
WHITE   = "#F0EDE6"

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 1 — Radial Bar Chart
# "¿Cuántos días a la semana consumes comida rápida?"
# ══════════════════════════════════════════════════════════════════════════════
fig1, ax1 = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
fig1.patch.set_facecolor(BG)
ax1.set_facecolor(BG)

labels   = list(data["dias_comida_rapida"].keys())
values   = list(data["dias_comida_rapida"].values())
total    = sum(values)
n        = len(labels)

# Cada barra ocupa una "ranura" angular; dejamos un pequeño gap
bar_width   = 2 * np.pi / n * 0.72
angles      = [2 * np.pi / n * i + np.pi / 2 for i in range(n)]

# Radio máximo normalizado
max_val  = max(values)
radii    = [v / max_val for v in values]

# Fondo circular de cada ranura
for ang in angles:
    ax1.bar(ang, 1.0, width=bar_width, bottom=0.15,
            color=GRAY, alpha=0.35, zorder=1)

# Barras principales
bar_colors = [COLORS[i % len(COLORS)] for i in range(n)]
for ang, r, col in zip(angles, radii, bar_colors):
    ax1.bar(ang, r * 0.85, width=bar_width, bottom=0.15,
            color=col, alpha=0.92, zorder=2,
            linewidth=0)

# Etiquetas de valor en la punta de cada barra
for ang, r, v, col in zip(angles, radii, values, bar_colors):
    tip = r * 0.85 + 0.15 + 0.09
    ax1.text(ang, tip, str(v), ha="center", va="center",
             fontsize=13, fontweight="bold", color=col,
             fontfamily="monospace")

# Etiquetas de categoría en el exterior — padding dinámico por altura de barra
for ang, r, lbl, col in zip(angles, radii, labels, bar_colors):
    pad = 1.08 + r * 0.20   # barras altas empujan el label más afuera
    ax1.text(ang, pad, lbl, ha="center", va="center",
             fontsize=9.5, color=WHITE, fontfamily="monospace",
             linespacing=1.4,
             fontweight="semibold")

# Círculo central con estadística destacada
circle = plt.Circle((0, 0), 0.145, transform=ax1.transData._b,
                     color=BG, zorder=5)
ax1.text(0, 0, str(total), ha="center", va="center",
         fontsize=22, fontweight="bold", color=ACCENT,
         fontfamily="monospace", transform=ax1.transData)
ax1.text(0, -0.28, "respuestas", ha="center", va="center",
         fontsize=8, color=ACCENT, alpha=0.75,
         fontfamily="monospace", transform=ax1.transData)
ax1.set_xticks([])
ax1.set_yticks([])
ax1.spines["polar"].set_visible(False)
ax1.set_ylim(0, 1.58)

fig1.suptitle(
    "¿Cuántos días a la semana consumes\ncomida rápida o snacks?",
    fontsize=15, color=ACCENT, fontfamily="monospace",
    fontweight="bold", y=0.96
)
ax1.set_title(f"n = {total} estudiantes universitarios",
              fontsize=9, color=WHITE, alpha=0.55,
              fontfamily="monospace", pad=28)

plt.tight_layout()
fig1.savefig("grafico1_radial_bar.png",
             dpi=180, bbox_inches="tight", facecolor=BG)
print("Gráfico 1 guardado.")


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 2 — Sankey (manual con patches)
# Carrera → Alimento priorizado
# ══════════════════════════════════════════════════════════════════════════════

from matplotlib.path import Path

def sankey_bezier(ax, x0, y0_top, y0_bot, x1, y1_top, y1_bot, color, alpha=0.55):
    """Dibuja un flujo Sankey como banda Bézier cúbica."""
    cx = (x0 + x1) / 2
    verts = [
        (x0, y0_top), (cx, y0_top), (cx, y1_top), (x1, y1_top),
        (x1, y1_bot), (cx, y1_bot), (cx, y0_bot), (x0, y0_bot),
        (x0, y0_top),
    ]
    codes = [
        Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CLOSEPOLY,
    ]
    path  = Path(verts, codes)
    patch = mpatches.PathPatch(path, facecolor=color, edgecolor="none", alpha=alpha, zorder=2)
    ax.add_patch(patch)


fig2, ax2 = plt.subplots(figsize=(13, 9))
fig2.patch.set_facecolor(BG)
ax2.set_facecolor(BG)
ax2.set_xlim(0, 10)
ax2.set_ylim(-0.08, 1.04)
ax2.axis("off")

# ── Nodos izquierda: carreras ─────────────────────────────────────────────────
carreras_raw = {
    "Ingeniería /\nTecnología":      12,
    "Administración\ny Negocios":    5,
    "Salud":                         4,
    "Humanidades /\nCs. Sociales":   1,
}
TOTAL_S = sum(carreras_raw.values())

# ── Nodos derecha: alimentos ──────────────────────────────────────────────────
alimento_totals = {}
carrera_alimento_flat = {
    "Ingeniería /\nTecnología": {
        "Snacks\ndulces": 5, "Comida\nrápida": 4,
        "Snacks\nsalados": 2, "Fruta /\nLácteos": 1,
    },
    "Administración\ny Negocios": {
        "Comida\nrápida": 2, "Snacks\ndulces": 1,
        "Snacks\nsalados": 1, "No comer": 1,
    },
    "Salud": {
        "Fruta /\nLácteos": 1, "Snacks\ndulces": 1,
        "Frutos\nsecos": 1, "Comida\nrápida": 1,
    },
    "Humanidades /\nCs. Sociales": {
        "Snacks\nsalados": 1,
    },
}
for c_map in carrera_alimento_flat.values():
    for alim, cnt in c_map.items():
        alimento_totals[alim] = alimento_totals.get(alim, 0) + cnt

# Orden descendente
alimento_order  = sorted(alimento_totals, key=lambda x: -alimento_totals[x])
carrera_order   = list(carreras_raw.keys())

GAP  = 0.012   # espacio entre nodos
H    = 1 - GAP * (len(carrera_order) - 1)

# Posiciones Y de nodos izquierda
c_heights = {c: carreras_raw[c] / TOTAL_S * H for c in carrera_order}
c_y = {}
y = 1.0
for c in carrera_order:
    c_y[c] = (y, y - c_heights[c])
    y -= c_heights[c] + GAP

# Posiciones Y de nodos derecha
a_heights = {a: alimento_totals[a] / TOTAL_S * H for a in alimento_order}
a_y = {}
y = 1.0
for a in alimento_order:
    a_y[a] = (y, y - a_heights[a])
    y -= a_heights[a] + GAP

# Color por carrera
carrera_colors = {c: COLORS[i] for i, c in enumerate(carrera_order)}
# Color nodos derecha: gris con tinte
alim_colors = {a: COLORS[i % len(COLORS)] for i, a in enumerate(alimento_order)}

# ── Dibujar flujos ────────────────────────────────────────────────────────────
X_LEFT, X_RIGHT = 2.5, 7.5
NODE_W = 0.28

# Punteros de cursor para apilar flujos dentro de cada nodo
c_cursor = {c: c_y[c][0] for c in carrera_order}
a_cursor = {a: a_y[a][0] for a in alimento_order}

# Guardamos segmentos de destino para etiquetar después
# {alimento: [(carrera, y_top, y_bot, cnt), ...]}
a_segments = {a: [] for a in alimento_order}

for c in carrera_order:
    for a in alimento_order:
        cnt = carrera_alimento_flat.get(c, {}).get(a, 0)
        if cnt == 0:
            continue
        h = cnt / TOTAL_S * H
        y0_top = c_cursor[c]
        y0_bot = y0_top - h
        y1_top = a_cursor[a]
        y1_bot = y1_top - h
        c_cursor[c] = y0_bot
        a_cursor[a] = y1_bot
        a_segments[a].append((c, y1_top, y1_bot, cnt))
        sankey_bezier(ax2,
                      X_LEFT + NODE_W, y0_top, y0_bot,
                      X_RIGHT,         y1_top, y1_bot,
                      color=carrera_colors[c], alpha=0.48)

# ── Dibujar nodos izquierda ───────────────────────────────────────────────────
for c in carrera_order:
    top, bot = c_y[c]
    rect = mpatches.FancyBboxPatch(
        (X_LEFT, bot), NODE_W, top - bot,
        boxstyle="round,pad=0.003",
        facecolor=carrera_colors[c], edgecolor="none", zorder=3
    )
    ax2.add_patch(rect)
    mid = (top + bot) / 2
    ax2.text(X_LEFT - 0.1, mid, c,
             ha="right", va="center", fontsize=8.5,
             color=WHITE, fontfamily="monospace",
             fontweight="semibold", linespacing=1.35)
    ax2.text(X_LEFT + NODE_W / 2, mid, str(carreras_raw[c]),
             ha="center", va="center", fontsize=8,
             color=BG, fontfamily="monospace", fontweight="bold", zorder=4)

# ── Dibujar nodos derecha ─────────────────────────────────────────────────────
MIN_H_LABEL = 0.022   # altura mínima de segmento para mostrar etiqueta

for a in alimento_order:
    top, bot = a_y[a]
    # Barra de fondo (color neutro)
    rect = mpatches.FancyBboxPatch(
        (X_RIGHT, bot), NODE_W, top - bot,
        boxstyle="round,pad=0.003",
        facecolor=alim_colors[a], edgecolor="none", zorder=3, alpha=0.30
    )
    ax2.add_patch(rect)

    # Sub-segmentos coloreados por carrera + etiqueta de valor
    for (c, seg_top, seg_bot, cnt) in a_segments[a]:
        seg_h = seg_top - seg_bot
        sub = mpatches.FancyBboxPatch(
            (X_RIGHT, seg_bot), NODE_W, seg_h,
            boxstyle="round,pad=0.001",
            facecolor=carrera_colors[c], edgecolor=BG,
            linewidth=0.4, zorder=4, alpha=0.88
        )
        ax2.add_patch(sub)
        # Etiqueta de valor solo si el segmento tiene altura suficiente
        if seg_h >= MIN_H_LABEL:
            seg_mid = (seg_top + seg_bot) / 2
            ax2.text(X_RIGHT + NODE_W / 2, seg_mid, str(cnt),
                     ha="center", va="center", fontsize=7.5,
                     color=BG, fontfamily="monospace",
                     fontweight="bold", zorder=5)

    # Etiqueta exterior del alimento
    mid = (top + bot) / 2
    ax2.text(X_RIGHT + NODE_W + 0.1, mid, a,
             ha="left", va="center", fontsize=8.5,
             color=WHITE, fontfamily="monospace",
             fontweight="semibold", linespacing=1.35)
    # Total del alimento al final del label
    ax2.text(X_RIGHT + NODE_W + 0.1, mid - 0.032, f"total: {alimento_totals[a]}",
             ha="left", va="center", fontsize=7,
             color=WHITE, alpha=0.45, fontfamily="monospace")

# ── Título y leyenda ──────────────────────────────────────────────────────────
fig2.suptitle(
    "Carrera universitaria  →  Alimento priorizado en momentos de poco tiempo",
    fontsize=13, color=ACCENT, fontfamily="monospace",
    fontweight="bold", y=0.97
)
ax2.text(5, -0.055, f"n = {TOTAL_S} respuestas",
         ha="center", fontsize=8.5, color=WHITE,
         alpha=0.5, fontfamily="monospace")

plt.tight_layout(rect=[0, 0.03, 1, 0.96])
fig2.savefig("grafico2_sankey.png",
             dpi=180, bbox_inches="tight", facecolor=BG)
print("Gráfico 2 guardado.")
