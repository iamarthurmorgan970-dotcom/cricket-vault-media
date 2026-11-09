"""India maps: state outlines (Natural Earth admin-1), India's official boundary (Natural Earth, India point of
view), pins, place zooms and fact cards (used in 'India's Hidden Wonders')."""
import json, math
import numpy as np
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle
from matplotlib.collections import PolyCollection, LineCollection
from shapely.geometry import shape, MultiPolygon
from .core import (BOLD, REG, OCEAN, LAND, EDGE, AMBER, CYAN, PINK, GREEN, VIOLET, WHITE, MUTED, ease, ease2,
                   merc, mercy, move, COUNTRIES)
from .geo import DATA

GOLD, RED = "#ffd166", "#ff5a5f"


def _load_states():
    d = json.load(open(f"{DATA}/admin1_10m.geojson"))
    out = {}
    for f in d["features"]:
        p = f["properties"]
        if p.get("adm0_a3") != "IND":
            continue
        g = shape(f["geometry"]).simplify(0.02, preserve_topology=True)
        rings = []
        for q in (g.geoms if isinstance(g, MultiPolygon) else [g]):
            a = np.asarray(q.exterior.coords)
            if len(a) >= 4:
                rings.append(a)
        out[p["name"]] = rings
    return out


ST = _load_states()


def _load_india_pov():
    d = json.load(open(f"{DATA}/admin0_10m_ind.geojson"))
    f = [f for f in d["features"] if f["properties"].get("ADMIN") == "India"][0]
    g = shape(f["geometry"]).simplify(0.02, preserve_topology=True)
    return [np.asarray(q.exterior.coords) for q in (g.geoms if isinstance(g, MultiPolygon) else [g])
            if q.area > 0.002]


INDIA_POV = _load_india_pov()     # India's official boundary (Natural Earth, India point of view)
_rivers = json.load(open(f"{DATA}/ne_50m_rivers_lake_centerlines.geojson"))


def river(name):
    out = []
    for f in _rivers["features"]:
        if f["properties"].get("name") == name:
            g = shape(f["geometry"])
            for l in (g.geoms if hasattr(g, "geoms") else [g]):
                out.append(np.asarray(l.coords))
    return out


INDIA_VIEW = (82, mercy(22), 48)


def india(S, keys=None, hl=None, hl_color=AMBER, t_hl=0.4):
    S.graticule(step=5)
    S.world()
    S.ax.add_collection(PolyCollection([merc(r) for r in INDIA_POV], facecolors="#2c4262", edgecolors="#4f6d94",
                                       linewidths=1.0, zorder=1.8))
    pc = PolyCollection([merc(r) for rs in ST.values() for r in rs], facecolors="#2c4262", edgecolors="#4f6d94",
                        linewidths=0.8, zorder=2)
    S.ax.add_collection(pc)
    if hl:
        S.highlight([r for s in hl for r in ST[s]], hl_color, t_hl, peak=0.8, lw=1.5)
    S.camera(keys or [(0, *INDIA_VIEW), (S.T, *INDIA_VIEW)])
    S.brand()


def pin(S, lon, lat, label, t0, color=AMBER, dy=0.6, size=26, ring=True, t1=None, ha="center", dx=0):
    p = merc(np.array([[lon, lat]]))[0]
    sc = S.ax.scatter([p[0]], [p[1]], s=0, color=color, edgecolors=WHITE, linewidths=2, zorder=30)
    rg = Circle(p, 0.6, fill=False, ec=color, lw=3, zorder=29, alpha=0) if ring else None
    if rg:
        S.ax.add_patch(rg)
    tx = S.ax.text(p[0] + dx, p[1] + dy, label, fontproperties=BOLD, size=size, color=WHITE, ha=ha, va="bottom",
                   zorder=31, alpha=0, bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        sc.set_sizes([170 * a])
        wv = S.ax.get_xlim()[1] - S.ax.get_xlim()[0]
        tx.set_position((p[0] + dx * wv / 48, p[1] + dy * wv / 48))
        tx.set_alpha(a)
        tx.get_bbox_patch().set_alpha(0.75 * a)
        if rg:
            w = S.ax.get_xlim()[1] - S.ax.get_xlim()[0]
            rg.set_radius(w * (0.018 + 0.006 * math.sin(2 * math.pi * (t - t0) / 1.4)))
            rg.set_alpha(a)
    S.updaters.append(up)


def card(S, text, phrase, y=0.2, color=WHITE, t1=None, size=34, x=0.5):
    t0 = S.c(phrase) if isinstance(phrase, str) else phrase
    S.text(x, y, text, t0, t1, size=size, color=color, box=True)


def state_tag(S, text, t0=0.3):
    S.text(0.04, 0.92, text, t0, size=30, color=AMBER, ha="left", box=True)




def place(S, state, lon, lat, name, width, cards, extra=None, color=AMBER, zoom_phrase=None, center=None):
    t_z = S.c(zoom_phrase) if zoom_phrase else 1.2
    clon, clat = center or (lon, lat)
    india(S, [(0, *INDIA_VIEW), (t_z, clon, mercy(clat), width), (S.T, clon, mercy(clat), width * 0.9)],
          hl=[state] if state else None)
    state_tag(S, state.upper() if state else "")
    pin(S, lon, lat, name, t_z + 0.6, color=color, dy=2.2)
    for c in cards:
        card(S, *c)
    if extra:
        extra(S)
