"""Extras: myth cards with strike-through, city dots, latitude lines, rivers and lakes (used in '15 Geography Facts')."""
import json, math
import numpy as np
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle, Ellipse, FancyBboxPatch
from matplotlib.collections import PolyCollection, LineCollection
from shapely.geometry import shape
from .core import (W, BOLD, REG, OCEAN, LAND, EDGE, GRID, AMBER, CYAN, PINK, GREEN, VIOLET, WHITE, MUTED,
                   ease, ease2, merc, mercy, equal_earth, ortho, COUNTRIES, CONT)
from .geo import DATA

RED = "#ff5a5f"
GOLD = "#ffd166"

_rivers = json.load(open(f"{DATA}/ne_50m_rivers_lake_centerlines.geojson"))
_lakes = json.load(open(f"{DATA}/ne_50m_lakes.geojson"))


def river(names):
    out = []
    for f in _rivers["features"]:
        if f["properties"].get("name") in names:
            g = shape(f["geometry"])
            for l in (g.geoms if hasattr(g, "geoms") else [g]):
                out.append(np.asarray(l.coords))
    return out


def lake(name):
    out = []
    for f in _lakes["features"]:
        if f["properties"].get("name") == name:
            g = shape(f["geometry"])
            for p in (g.geoms if hasattr(g, "geoms") else [g]):
                out.append(np.asarray(p.exterior.coords))
    return out




def myth(S, n, text, truth=None, t_truth=None):
    """Top card: 'MYTH #n' + the myth, struck through when the truth arrives; truth headline at the bottom."""
    t_truth = t_truth if t_truth is not None else S.T * 0.3
    tag = S.fig.text(0.5, 0.925, f"MYTH #{n}", fontproperties=BOLD, size=26, color=RED, ha="center", va="center",
                     zorder=70, alpha=0)
    txt = S.fig.text(0.5, 0.86, text, fontproperties=BOLD, size=38, color=WHITE, ha="center", va="center", zorder=70,
                     alpha=0, bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.6", fc="#07111d", ec="none", alpha=0))
    S.fig.canvas.draw()
    bb = txt.get_window_extent(renderer=S.fig.canvas.get_renderer())
    x0, x1 = bb.x0 / W, bb.x1 / W
    strike = S.fig.add_artist(plt_line(x0, 0.86, x1))

    def up(t):
        a = ease((t - 0.2) / 0.4)
        tag.set_alpha(a)
        txt.set_alpha(a * (1 - 0.45 * ease((t - t_truth) / 0.4)))
        txt.get_bbox_patch().set_alpha(0.82 * a)
        g = ease2((t - t_truth + 0.2) / 0.5)
        strike.set_xdata([x0, x0 + (x1 - x0) * g])
        strike.set_alpha(1.0 if g > 0 else 0)
    S.updaters.append(up)
    if truth:
        S.text(0.5, 0.08, truth, t_truth + 0.3, size=40, color=GREEN, box=True, pop=True)


def plt_line(x0, y, x1):
    from matplotlib.lines import Line2D
    return Line2D([x0, x0], [y, y], color=RED, lw=6, alpha=0, zorder=75, solid_capstyle="round")


def dot(S, lon, lat, label, t0, color=WHITE, proj=merc, dx=0, dy=3, size=26, ha="center", t1=None, cross=False):
    p = proj(np.array([[lon, lat]]))[0]
    sc = S.ax.scatter([p[0]], [p[1]], s=0, color=color, edgecolors=WHITE, linewidths=2, zorder=30)
    tx = S.ax.text(p[0] + dx, p[1] + dy, label, fontproperties=BOLD, size=size, color=color, ha=ha, va="bottom",
                   zorder=31, alpha=0, bbox=dict(boxstyle="round,pad=0.25", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.35), ease((t1 - t) / 0.35))
        sc.set_sizes([160 * a])
        tx.set_alpha(a * (0.45 if cross and t > t0 + 0.01 and t > cross else 1))
        tx.get_bbox_patch().set_alpha(0.7 * a)
    S.updaters.append(up)
    return tx


def lat_line(S, lat, t0, color, x0=-180, x1=180, label=None, t1=None):
    y = mercy(lat)
    ln, = S.ax.plot([x0, x1], [y, y], color=color, lw=2.5, ls=(0, (6, 4)), zorder=25, alpha=0)
    lab = S.ax.text(x1, y + 1, label or "", fontproperties=BOLD, size=20, color=color, ha="right", va="bottom",
                    zorder=26, alpha=0) if label else None
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.5), ease((t1 - t) / 0.5))
        ln.set_alpha(a)
        if lab:
            lab.set_alpha(a)
    S.updaters.append(up)


def mapbase(S, proj=merc, grid=True):
    if grid:
        S.graticule(proj=proj)
    S.world(proj=proj)



def _strike_for(S, x, y, text, size, t0):
    from matplotlib.lines import Line2D
    tmp = S.fig.text(x, y, text, fontproperties=BOLD, size=size, ha="center", va="center", alpha=0)
    S.fig.canvas.draw()
    bb = tmp.get_window_extent(renderer=S.fig.canvas.get_renderer())
    tmp.remove()
    x0, x1 = bb.x0 / W, bb.x1 / W
    ln = Line2D([x0, x0], [y, y], color=RED, lw=7, zorder=80, alpha=0, solid_capstyle="round")

    def up(t):
        g = ease2((t - t0) / 0.45)
        ln.set_xdata([x0, x0 + (x1 - x0) * g])
        ln.set_alpha(1 if g > 0 else 0)
    S.updaters.append(up)
    return ln




def peaks_chart(S, rows, title, subtitle="Highest point, metres above sea level", ymax_km=None, width=16,
                captions=()):
    """Side-by-side mountains drawn to scale. rows: (NAME, sub-label, height_km, colour, cue phrase).
    captions: (text, start phrase, end phrase or None, colour)."""
    from matplotlib.patches import Polygon as P
    ax = S.ax
    top = ymax_km or max(r[2] for r in rows) * 1.25
    ax.set_xlim(0, width)
    ax.set_ylim(-0.32 * top, top * 1.32)
    S.text(0.5, 0.92, title, 0.3, size=44, pop=True)
    S.text(0.5, 0.855, subtitle, 0.6, size=24, color=MUTED, font=REG)
    ax.plot([0, width], [0, 0], color=MUTED, lw=2)
    step = 1 if top <= 7 else 2 if top <= 14 else 5
    for k in range(step, int(top) + 1, step):
        ax.plot([0, width], [k, k], color="#16283c", lw=1, zorder=0)
        ax.text(0.15, k + 0.05, f"{k},000 m", fontproperties=REG, size=16, color=MUTED, va="bottom")
    n = len(rows)
    gap = (width - 1.2) / n
    for i, (name, sub, h, col, ph) in enumerate(rows):
        cx = 1.2 + gap * (i + 0.5)
        half = gap * 0.43
        tri = P([[cx - half, 0], [cx + half, 0], [cx, 0]], closed=True, color=col, zorder=3, alpha=0.9)
        ax.add_patch(tri)
        lab = ax.text(cx, 0, "", fontproperties=BOLD, size=26, color=WHITE, ha="center", va="bottom", zorder=5)
        sb = ax.text(cx, -0.04 * top, f"{name}\n{sub}", fontproperties=BOLD, size=20, color=col, ha="center",
                     va="top", zorder=5, alpha=0)
        t0 = S.c(ph) if isinstance(ph, str) else ph

        def up(t, tri=tri, lab=lab, sb=sb, t0=t0, h=h, cx=cx, half=half):
            g = ease2((t - t0) / 1.2)
            tri.set_xy([[cx - half, 0], [cx + half, 0], [cx, h * g]])
            lab.set_position((cx, h * g + 0.02 * top))
            lab.set_text(f"≈ {h * 1000 * g:,.0f} m" if g > 0.02 else "")
            sb.set_alpha(ease((t - t0) / 0.4))
        S.updaters.append(up)
    for text, a, b, col in captions:
        S.caption(text, S.c(a), S.c(b) if b else None, color=col)
