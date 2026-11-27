"""037 How Big Are the Oceans, Really? Each function takes the Scene S; S.c("phrase") is when the narrator says it.
World maps use Equal Earth (equal-area), so every area on screen is true. Ocean regions are a simplified 1-degree
classification (approximate IHO-style limits) used only for colour; every number comes from the sources in
out/upload-details.txt. India is always drawn with engine.india.INDIA_POV."""
import numpy as np
from engine.core import *
from engine.core import Scene
from engine.geo import move
from engine.india import INDIA_POV
from matplotlib.patches import Polygon as MPoly, FancyBboxPatch, Rectangle
from shapely.geometry import Polygon as SPoly, box
from shapely.ops import unary_union
from shapely import affinity

NOT_INDIA = [n for n in COUNTRIES if n != "India"]
BLUE = {"Pacific": CYAN, "Atlantic": "#4895ef", "Indian": VIOLET, "Southern": "#a9cbe6", "Arctic": GREEN}
DEEP = "#06101c"


# ------------------------------------------------------------------ geometry (lon/lat), built once
def _poly(r):
    p = SPoly(r).buffer(0)
    return p


LAND_G = unary_union([_poly(r) for n in NOT_INDIA for r in COUNTRIES[n]] + [_poly(r) for r in INDIA_POV]).buffer(0)


def _ocean_of(lon, lat):
    if lat < -60:
        return "Southern"
    if lat >= 66.5:
        return "Arctic"
    if 51 <= lat < 66.5 and -95 <= lon < -65:
        return "Arctic"                         # Hudson Bay
    if 36 <= lat < 47.5 and 46 <= lon < 56:
        return None                             # Caspian Sea (not an ocean)
    if 41 <= lat < 49.5 and -93 <= lon < -75:
        return None                             # Great Lakes
    # Indian Ocean
    if lat < 10 and 20 <= lon:
        lim = 147 if lat < -11 else 125 if lat < -8 else 99
        if lon < lim:
            return "Indian"
    if 10 <= lat < 30.5 and 32 <= lon < 99:
        return "Indian"
    # Atlantic
    if lat < -56:
        west = -67
    elif lat < 8:
        west = -70
    elif lat < 10.5:
        west = -81
    elif lat < 15:
        west = -85.5
    elif lat < 19:
        west = -92
    elif lat < 31:
        west = -98
    else:
        west = -100
    east = 20 if lat < 30 else 42
    if west <= lon < east:
        return "Atlantic"
    if 30 <= lat and 42 <= lon < 100:
        return None
    return "Pacific"


def _build_oceans():
    cells = {k: [] for k in BLUE}
    for lat in range(-90, 90):
        for lon in range(-180, 180):
            o = _ocean_of(lon + 0.5, lat + 0.5)
            if o:
                cells[o].append(box(lon, lat, lon + 1, lat + 1))
    out = {}
    for k, v in cells.items():
        g = unary_union(v).difference(LAND_G).simplify(0.15)
        out[k] = g
    return out


OCEANS = _build_oceans()


def _geoms(g):
    return list(g.geoms) if hasattr(g, "geoms") else [g]


def wrap(g, lon0):
    """Pieces of geometry g, shifted so they sit inside lon0-180 .. lon0+180, in shifted lon (x = lon - lon0)."""
    out = []
    win = box(lon0 - 180, -90, lon0 + 180, 90)
    for k in (-360, 0, 360):
        q = affinity.translate(g, k, 0).intersection(win)
        if q.is_empty:
            continue
        for p in _geoms(q):
            if p.geom_type != "Polygon" or p.area < 0.05:
                continue
            a = np.asarray(p.segmentize(1.0).exterior.coords).copy()
            a[:, 0] -= lon0
            out.append(a)
    return out


def EE(lon0):
    """Equal Earth centred on lon0 (for rings that are already shifted use EE0)."""
    def f(a):
        b = a.copy()
        b[:, 0] = b[:, 0] - lon0
        b[:, 0] -= 360 * np.round(b[:, 0].mean() / 360)
        return equal_earth(b)
    return f


_CACHE = {}


def layers(lon0):
    if lon0 not in _CACHE:
        lands = []
        for n in NOT_INDIA:
            for r in COUNTRIES[n]:
                lands += wrap(_poly(r), lon0)
        ind = []
        for r in INDIA_POV:
            ind += wrap(_poly(r), lon0)
        oc = {k: wrap(g, lon0) for k, g in OCEANS.items()}
        _CACHE[lon0] = (lands, ind, oc)
    return _CACHE[lon0]


def fade(S, arts, t0, t1=None, peak=1.0, dur=0.6):
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / dur), ease((t1 - t) / dur)) * peak
        for x in arts:
            x.set_alpha(a)
    S.updaters.append(up)


def basemap(S, lon0=0, keys=None, oceans=None, glow=None, grid=True):
    """World on Equal Earth centred at lon0. oceans: {name: (t0, t1)} to colour; glow: (t0, t1) colours all."""
    lands, ind, oc = layers(lon0)
    if grid:
        lines = []
        for lat in range(-80, 81, 20):
            lon = np.linspace(-180, 180, 181)
            lines.append(equal_earth(np.column_stack([lon, np.full_like(lon, lat)])))
        for lon in range(-180, 181, 30):
            lat = np.linspace(-90, 90, 91)
            lines.append(equal_earth(np.column_stack([np.full_like(lat, lon), lat])))
        S.ax.add_collection(LineCollection(lines, colors=GRID, linewidths=0.8, zorder=0.5))
    # globe outline
    lat = np.linspace(-90, 90, 181)
    edge = np.vstack([equal_earth(np.column_stack([np.full_like(lat, 180.0), lat])),
                      equal_earth(np.column_stack([np.full_like(lat, -180.0), lat[::-1]]))])
    S.ax.add_patch(MPoly(edge, closed=True, fc="none", ec=EDGE, lw=1.5, zorder=0.6))
    pcs = {}
    for k, rings in oc.items():
        pc = PolyCollection([equal_earth(r) for r in rings], facecolors=BLUE[k], edgecolors="none", zorder=0.8,
                            alpha=0)
        S.ax.add_collection(pc)
        pcs[k] = pc
        win = (oceans or {}).get(k) or glow
        if win:
            fade(S, [pc], win[0], win[1], peak=0.45)
    S.ax.add_collection(PolyCollection([equal_earth(r) for r in lands], facecolors=LAND, edgecolors=EDGE,
                                       linewidths=0.4, zorder=1))
    S.ax.add_collection(PolyCollection([equal_earth(r) for r in ind], facecolors=LAND, edgecolors=EDGE,
                                       linewidths=0.4, zorder=1.1))
    S.camera(keys or [(0, 0, 0, 380), (S.T, 0, 0, 372)])
    S.brand()
    return pcs


def mlabel(S, lon, lat, s, t0, lon0=0, t1=None, color=WHITE, size=30):
    x = ((lon - lon0 + 180) % 360) - 180
    p = equal_earth(np.array([[x, lat]]))[0]
    tx = S.ax.text(p[0], p[1], s, fontproperties=BOLD, size=size, color=color, ha="center", va="center",
                   zorder=40, alpha=0, bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        tx.set_alpha(a)
        tx.get_bbox_patch().set_alpha(0.75 * a)
    S.updaters.append(up)
    return tx


def panel(S, rect, t0, t1=None):
    ax = S.fig.add_axes(rect)
    ax.set_axis_off()
    bg = FancyBboxPatch((0, 0), 1, 1, transform=ax.transAxes, boxstyle="round,pad=0,rounding_size=0.03",
                        fc="#07111d", ec="none", alpha=0)
    ax.add_patch(bg)
    fade(S, [bg], t0, t1, peak=0.85)
    return ax


def stat(S, x, y, big, small, t0, color=AMBER, t1=None, bsize=84, ssize=26):
    S.text(x, y, big, t0, t1, size=bsize, color=color, pop=True)
    S.text(x, y - 0.075, small, t0 + 0.2, t1, size=ssize, color=WHITE, font=REG)


# ------------------------------------------------------------------ depth cross-section helpers
def section(S, depth_max=12000, top=10000, x0=0.0, x1=16.0):
    """A side view: sea surface at y=0, metres (negative down)."""
    ax = S.ax
    ax.set_xlim(x0, x1)
    ax.set_ylim(-depth_max * 1.08, top)
    sky = Rectangle((x0, 0), x1 - x0, top, fc=OCEAN, ec="none", zorder=0)
    sea = Rectangle((x0, -depth_max * 1.08), x1 - x0, depth_max * 1.08, fc="#0e2a47", ec="none", zorder=0.2)
    ax.add_patch(sky)
    ax.add_patch(sea)
    # darker with depth
    for i in range(12):
        d0 = -depth_max * 1.08 * i / 12
        ax.add_patch(Rectangle((x0, d0 - depth_max * 0.09), x1 - x0, depth_max * 0.09,
                               fc=DEEP, ec="none", alpha=0.08 * i, zorder=0.3))
    ax.plot([x0, x1], [0, 0], color=CYAN, lw=3, zorder=5)
    for k in range(2000, depth_max + 1, 2000):
        ax.plot([x0, x1], [-k, -k], color="#1d3a5c", lw=1, zorder=0.4, ls=(0, (4, 4)))
        ax.text(x0 + 0.12, -k + 120, f"{k:,} m", fontproperties=REG, size=17, color=MUTED, va="bottom", zorder=6)
    ax.text(x0 + 0.12, 150, "sea level", fontproperties=BOLD, size=18, color=CYAN, va="bottom", zorder=6)
    S.brand()


def depth_bar(S, cx, w, depth, color, t0, name, val=None, dur=1.2):
    ax = S.ax
    r = Rectangle((cx - w / 2, 0), w, 0, fc=color, ec="none", alpha=0.9, zorder=3)
    ax.add_patch(r)
    lab = ax.text(cx, 250, name, fontproperties=BOLD, size=22, color=color, ha="center", va="bottom", zorder=6,
                  alpha=0)
    num = ax.text(cx, 0, "", fontproperties=BOLD, size=22, color=WHITE, ha="center", va="top", zorder=6)

    def up(t):
        g = ease2((t - t0) / dur)
        d = depth * g
        r.set_y(-d)
        r.set_height(d)
        lab.set_alpha(ease((t - t0) / 0.3))
        num.set_position((cx, -d - 150))
        num.set_text(f"{(val or depth) * g:,.0f} m" if g > 0.02 else "")
    S.updaters.append(up)


def mountain(S, cx, base, height, color, t0, name, half=1.6, dur=1.6, label_side="right"):
    ax = S.ax
    tri = MPoly([[cx - half, base], [cx + half, base], [cx, base]], closed=True, fc=color, ec=WHITE, lw=1.5,
                zorder=4, alpha=0.95)
    ax.add_patch(tri)
    lab = ax.text(cx, base, "", fontproperties=BOLD, size=24, color=WHITE, ha="center", va="bottom", zorder=7,
                  bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0.0))

    def up(t):
        g = ease2((t - t0) / dur)
        tri.set_xy([[cx - half, base], [cx + half, base], [cx + half * 0.15, base + height * g * 0.82],
                    [cx, base + height * g], [cx - half * 0.2, base + height * g * 0.86]])
        lab.set_position((cx, base + height * g + 200))
        lab.set_text(f"{name} {height * g:,.0f} m" if g > 0.02 else "")
        lab.get_bbox_patch().set_alpha(0.75 if g > 0.02 else 0)
        tri.set_alpha(0.95 if g > 0 else 0)
    S.updaters.append(up)


def trench_floor(S, x0, x1, depth, t0, color="#13314f"):
    """Seafloor profile with a trench between x0 and x1 that opens down to `depth`."""
    ax = S.ax
    base = -3700
    pts = [[0, base - 300], [x0 - 1.5, base], [x0, base - 600], [(x0 + x1) / 2 - 0.4, -depth],
           [(x0 + x1) / 2 + 0.4, -depth], [x1, base - 800], [x1 + 1.5, base - 200], [16, base], [16, -13500],
           [0, -13500]]
    shp = MPoly(pts, closed=True, fc="#2a3f5a", ec=EDGE, lw=2, zorder=2.5, alpha=0)
    ax.add_patch(shp)
    fade(S, [shp], t0, peak=1.0, dur=0.8)


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    section(S)
    trench_floor(S, 6.0, 10.0, 11034, 0.2)
    mountain(S, 8.0, -11034, 8850, "#c9d6e3", S.c("drop it into"), "Everest", half=2.4, dur=2.4)
    S.headline("EVEREST FITS IN THE OCEAN", S.c("Take Mount"), S.c("That's how deep"))
    S.caption("Summit still about 2 km under water", S.c("Its summit"), S.c("And more than"), color=AMBER)
    S.text(0.5, 0.5, "Over 70% of the seafloor: unmapped", S.c("And more than"), S.c("Today,"), size=50,
           color=PINK, box=True, pop=True)
    S.headline("ALL 5 OCEANS AT TRUE SCALE", S.c("Today,"), y=0.9)
    S.caption("how big  ·  how deep  ·  how little we've seen", S.c("how big they are"))
    S.fade_in_out(0.4, 0.3)


def s02_title(S):
    basemap(S, lon0=-160, glow=(0.0, None))
    S.text(0.5, 0.56, "HOW BIG ARE THE OCEANS,", 0.2, size=70, pop=True)
    S.text(0.5, 0.44, "REALLY?", 0.5, size=96, color=AMBER, pop=True)
    S.fade_in_out(0.3, 0.4)


def s03_planet(S):
    t_h = S.c("The ocean covers")
    basemap(S, lon0=0, glow=(S.c("seventy point eight"), t_h + 0.2),
            keys=[(0, 0, 0, 400), (S.T, 0, 0, 380)])
    S.headline("EARTH'S SURFACE", S.c("Start with"), t_h)
    ax = panel(S, (0.25, 0.08, 0.5, 0.12), S.c("seventy point eight"), t_h)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    b1 = ax.barh(0.5, 0, height=0.5, left=0, color=CYAN, zorder=2)[0]
    b2 = ax.barh(0.5, 0, height=0.5, left=70.8, color=AMBER, zorder=2)[0]
    l1 = ax.text(35, 0.5, "70.8% below sea level", fontproperties=BOLD, size=24, color="#07111d", ha="center",
                 va="center", zorder=3, alpha=0)
    l2 = ax.text(85.4, 0.5, "29.2% land", fontproperties=BOLD, size=22, color="#07111d", ha="center",
                 va="center", zorder=3, alpha=0)
    ta, tb = S.c("seventy point eight"), S.c("Only twenty-nine")

    def up(t):
        fa = ease((t_h + 0.2 - t) / 0.4)
        b1.set_width(70.8 * ease2((t - ta) / 1.0))
        b1.set_alpha(fa)
        b2.set_width(29.2 * ease2((t - tb) / 0.8))
        b2.set_alpha(fa)
        l1.set_alpha(fa * ease((t - ta - 0.8) / 0.3))
        l2.set_alpha(fa * ease((t - tb - 0.6) / 0.3))
    S.updaters.append(up)
    # hemispheres
    tn, ts, tg = S.c("sixty-one percent"), S.c("eighty-one percent"), S.c("Turn the globe")
    S.text(0.5, 0.9, "HOW MUCH IS OCEAN?", t_h, tg, size=46, box=True, pop=True)
    stat(S, 0.3, 0.55, "61%", "of the Northern Hemisphere", tn, CYAN, tg)
    stat(S, 0.7, 0.55, "81%", "of the Southern Hemisphere", ts, CYAN, tg)
    sh = Rectangle((0, 0), 1, 1, transform=S.fig.transFigure, color="#07111d", zorder=30, alpha=0)
    S.fig.add_artist(sh)
    fade(S, [sh], tn - 0.3, tg, peak=0.6)
    # globe facing the Pacific
    gax = S.fig.add_axes([0, 0, 1, 1])
    gax.set_axis_off()
    gax.set_xlim(-1.12 * 16 / 9, 1.12 * 16 / 9)
    gax.set_ylim(-1.12, 1.12)
    bgr = Rectangle((-3, -3), 6, 6, fc=OCEAN, ec="none", alpha=0, zorder=0)
    gax.add_patch(bgr)
    fade(S, [bgr], tg - 0.2)
    th = np.linspace(0, 2 * np.pi, 200)
    disk = MPoly(np.column_stack([np.cos(th), np.sin(th)]), closed=True, fc="#1d6fa5", ec=CYAN, lw=2, alpha=0, zorder=1)
    gax.add_patch(disk)
    polys = []
    for n in NOT_INDIA:
        for r in COUNTRIES[n]:
            xy, vis = ortho(r, -165, -10)
            if vis > 0.98:
                polys.append(xy)
    lc = PolyCollection(polys, facecolors="#4a6a8f", edgecolors="#8fb0d6", linewidths=0.6, alpha=0, zorder=2)
    gax.add_collection(lc)
    fade(S, [disk, lc], tg)
    S.text(0.5, 0.05, "The Pacific side of Earth", tg + 0.4, size=32, box=True, zorder=80)
    S.fade_in_out(0.3, 0.3)


def s04_total(S):
    basemap(S, lon0=-160, glow=(0.2, None), keys=[(0, 0, 0, 380), (S.T, 0, 0, 370)])
    stat(S, 0.5, 0.72, "≈ 362 million km²", "the world ocean's area", S.c("three hundred"), AMBER, S.c("It holds"),
         bsize=76)
    stat(S, 0.5, 0.72, "≈ 1.3 billion km³", "of water", S.c("It holds"), CYAN, S.c("That's about"), bsize=76)
    S.headline("WHERE EARTH'S SURFACE WATER IS", S.c("That's about"))
    S.bars([("Oceans: Pacific 52 + Atlantic 25 + Indian 20", [(52, CYAN), (25, "#4895ef"), (20, VIOLET)], None,
             S.c("ninety-seven")),
            ("Ice", 2, "#e8f4ff", S.c("Ice holds")),
            ("Groundwater", 0.6, GREEN, S.c("Groundwater")),
            ("Lakes, rivers and air", 0.01, AMBER, S.c("rivers and the air"))],
           S.c("ninety-seven"), rect=(0.16, 0.2, 0.68, 0.5), xmax=118, unit="%", dec=2,
           title="Share of the water on Earth's surface (oceanography textbook, Webb)")
    S.fade_in_out(0.3, 0.3)


OCEAN_LBL = {"Pacific": (-140, 5), "Atlantic": (-35, 15), "Indian": (78, -22), "Southern": (-100, -68),
             "Arctic": (0, 80)}


def s05_five(S):
    cues = {"Pacific": "The Pacific", "Atlantic": "The Atlantic", "Indian": "The Indian Ocean",
            "Southern": "The Southern Ocean", "Arctic": "And the Arctic"}
    win = {k: (S.c(v), None) for k, v in cues.items()}
    basemap(S, lon0=-20, oceans=win, keys=[(0, 30, 0, 380), (S.T, 30, 0, 372)])
    S.headline("THE FIVE OCEANS", 0.3)
    for k, (lo, la) in OCEAN_LBL.items():
        mlabel(S, lo, la, k.upper(), S.c(cues[k]), lon0=-20, color=WHITE, size=28)
    S.bars([("Pacific", 168.7, CYAN, S.c(cues["Pacific"])), ("Atlantic", 85.1, "#4895ef", S.c(cues["Atlantic"])),
            ("Indian", 70.6, VIOLET, S.c(cues["Indian"])), ("Southern", 22.0, "#a9cbe6", S.c(cues["Southern"])),
            ("Arctic", 15.6, GREEN, S.c(cues["Arctic"]))],
           0.5, rect=(0.72, 0.08, 0.25, 0.46), xmax=240, unit="M km²", title="Area (Britannica / NOAA)")
    S.fade_in_out(0.3, 0.3)


def s06_pacific(S):
    basemap(S, lon0=-160, oceans={"Pacific": (0.2, None)}, keys=[(0, 0, 0, 380), (S.T, 0, 0, 366)])
    mlabel(S, -150, 0, "PACIFIC", 0.4, lon0=-160, size=34)
    stat(S, 0.5, 0.8, "≈ 47%", "of all the ocean on Earth", S.c("about forty-seven"), CYAN, S.c("Here is what"))
    S.bars([("Pacific Ocean", 168.7, CYAN, S.c("The Pacific is bigger")),
            ("All of Earth's land", 149.3, AMBER, S.c("adds up to"))],
           S.c("adds up to"), rect=(0.2, 0.12, 0.6, 0.2), xmax=210, unit="M km²",
           title="Area. Land from Britannica's 29.2% share of the surface")
    S.caption("about 20 million km² to spare", S.c("still have about"), color=GREEN)
    S.fade_in_out(0.3, 0.3)


def s07_drop(S):
    lon0 = -160
    basemap(S, lon0=lon0, oceans={"Pacific": (0.0, None)}, keys=[(0, 0, 0, 300), (S.T, 0, 0, 292)])
    proj = EE(lon0)
    S.headline("BIG COUNTRIES, DROPPED IN THE PACIFIC", 0.3, S.c("Four of"))
    drops = [(INDIA_POV, (79.0, 22.0), (-145.0, 8.0), PINK, "India", "Here is India"),
             (COUNTRIES["Australia"], (134.0, -25.0), (-140.0, -40.0), AMBER, "Australia", "Now add Australia"),
             (COUNTRIES["China"], (104.0, 35.0), (172.0, 24.0), GREEN, "China", "Then China"),
             (US48, (-98.0, 39.0), (-104.0, -12.0), VIOLET, "USA (48 states)", "Then the United States")]
    for rings, frm, to, col, name, ph in drops:
        t0 = S.c(ph)
        S.mover(rings, frm, to, t0 + 0.2, t0 + 2.4, color=col, label=name, proj=proj, ghost=True)
    S.caption("True shapes, true sizes (equal-area map)", S.c("Four of"), color=WHITE)
    S.fade_in_out(0.3, 0.3)


def s08_volume(S):
    basemap(S, lon0=-20, oceans={"Pacific": (0.2, None), "Atlantic": (S.c("The Atlantic holds"), None),
                                 "Indian": (S.c("Indian Ocean about"), None)},
            keys=[(0, 30, 0, 380), (S.T, 30, 0, 372)])
    S.headline("HOW MUCH WATER EACH HOLDS", 0.3)
    stat(S, 0.5, 0.68, "≈ 3,970 m", "Pacific average depth", S.c("three thousand nine"), CYAN,
         S.c("So it holds"))
    S.bars([("Pacific", 669.9, CYAN, S.c("six hundred")), ("Atlantic", 310.4, "#4895ef", S.c("The Atlantic holds")),
            ("Indian", 264.0, VIOLET, S.c("Indian Ocean about"))],
           S.c("six hundred"), rect=(0.2, 0.12, 0.6, 0.3), xmax=880, unit="M km³", dec=0,
           title="Volume (Britannica / NOAA)")
    S.caption("Pacific: more than 2× the Atlantic", S.c("more than twice"), color=AMBER)
    S.fade_in_out(0.3, 0.3)


def s09_poles(S):
    t_a = S.c("The Arctic is")
    basemap(S, lon0=0, oceans={"Southern": (S.c("The Southern Ocean"), None), "Arctic": (t_a, None)},
            keys=[(0, 0, -40, 340), (t_a - 0.5, 0, -60, 300), (t_a + 1.5, 0, 62, 300), (S.T, 0, 60, 290)])
    S.headline("THE POLAR OCEANS", 0.3)
    S.text(0.5, 0.78, "Southern: ≈ 22 million km²", S.c("covers about"), t_a, size=46, color="#a9cbe6", box=True)
    S.text(0.5, 0.22, "Arctic: ≈ 16 million km²", t_a + 0.3, S.c("It's also"), size=46, color=GREEN, box=True)
    S.bars([("Arctic", 1205, GREEN, S.c("only about")), ("World average", 3688, CYAN, S.c("world average"))],
           S.c("only about"), rect=(0.22, 0.08, 0.56, 0.2), xmax=4700, unit="m", dec=0,
           title="Average depth (Britannica / NOAA)")
    S.fade_in_out(0.3, 0.3)


def s10_depth(S):
    section(S, depth_max=10000, top=9800)
    S.headline("AVERAGE DEPTH", 0.3)
    rows = [("Pacific", 3970, CYAN), ("Indian", 3741, VIOLET), ("Atlantic", 3646, "#4895ef"),
            ("Southern", 3270, "#a9cbe6"), ("Arctic", 1205, GREEN)]
    t0 = S.c("About three thousand")
    depth_bar(S, 2.2, 1.6, 3688, AMBER, t0, "World ocean")
    for i, (n, d, c) in enumerate(rows):
        depth_bar(S, 4.6 + i * 1.9, 1.4, d, c, t0 + 0.6 + 0.35 * i, n)
    mountain(S, 14.6, 0, 8850, "#c9d6e3", S.c("two fifths"), "Everest", half=1.1)
    S.caption("Another textbook: ≈ 3,800 m. Figures depend on how basins are measured", S.c("Sources differ"),
              color=MUTED, size=28)
    S.fade_in_out(0.3, 0.3)


def s11_trench(S):
    t_s = S.c("Estimates of")
    q = equal_earth(np.array([[142.2 + 160 - 360, 11.35]]))[0]
    basemap(S, lon0=-160, keys=[(0, 0, 0, 380), (S.c("Challenger Deep") - 0.6, 0, 0, 380),
                                (S.c("Challenger Deep") + 1.4, q[0], q[1] - 6, 110), (S.T, q[0], q[1] - 6, 100)])
    S.headline("THE DEEPEST PLACE WE KNOW", 0.3)
    x = ((142.2 - (-160) + 180) % 360) - 180
    p = equal_earth(np.array([[x, 11.35]]))[0]
    sc = S.ax.scatter([p[0]], [p[1]], s=0, color=PINK, edgecolors=WHITE, linewidths=2.5, zorder=30)
    t_p = S.c("Challenger Deep")

    def up(t):
        a = ease((t - t_p) / 0.4)
        sc.set_sizes([420 * a * (0.85 + 0.15 * np.cos(2 * np.pi * max(t - t_p, 0) / 1.4))])
    S.updaters.append(up)
    mlabel(S, 142.2, 16.5, "Challenger Deep, Mariana Trench (approx.)", t_p + 0.4, lon0=-160, color=PINK, size=26)
    S.text(0.5, 0.2, "≈ 10,900 to 11,000+ m", t_s, S.c("Britannica gives"), size=60, color=AMBER, box=True, pop=True)
    S.text(0.5, 0.2, "Britannica: 11,034 m", S.c("Britannica gives"), size=60, color=AMBER, box=True, pop=True)
    S.fade_in_out(0.3, 0.3)


def s12_everest(S):
    section(S)
    trench_floor(S, 6.0, 10.0, 11034, 0.0)
    mountain(S, 8.0, -11034, 8850, "#c9d6e3", S.c("Now bring in"), "Everest", half=2.4, dur=2.0)
    S.headline("EVEREST IN THE TRENCH", 0.3)
    ax = S.ax
    arr, = ax.plot([10.7, 10.7], [-2184, 0], color=AMBER, lw=5, zorder=8, alpha=0)
    tx = ax.text(11.0, -1100, "≈ 2 km of water\nabove the summit", fontproperties=BOLD, size=30, color=AMBER,
                 va="center", zorder=8, alpha=0)
    fade(S, [arr, tx], S.c("its summit stops"))
    S.caption("Lowest trench estimate (≈ 10,920 m): still over 2,000 m above the peak", S.c("Even the lowest"),
              color=WHITE, size=30)
    S.fade_in_out(0.3, 0.3)


def s13_mapped(S):
    basemap(S, lon0=-20, glow=(0.2, None), keys=[(0, 30, 0, 380), (S.T, 30, 0, 370)])
    S.headline("HOW MUCH OF THE SEAFLOOR IS MAPPED?", 0.3)
    ax = panel(S, (0.15, 0.4, 0.7, 0.16), S.c("twenty-eight point"))
    ax.set_xlim(-2, 102)
    ax.set_ylim(0, 1)
    ax.barh(0.5, 100, height=0.42, color="#1b2f47", zorder=1)
    b = ax.barh(0.5, 0, height=0.42, color=GREEN, zorder=2)[0]
    lb = ax.text(1, 0.5, "", fontproperties=BOLD, size=30, color="#07111d", va="center", zorder=3)
    ax.text(99, 0.5, "not yet mapped", fontproperties=BOLD, size=26, color=MUTED, va="center", ha="right", zorder=3)
    t0 = S.c("twenty-eight point")

    def up(t):
        g = ease2((t - t0) / 1.4)
        b.set_width(28.7 * g)
        lb.set_text(f"{28.7 * g:.1f}% mapped" if g > 0.3 else "")
    S.updaters.append(up)
    S.text(0.5, 0.27, "≈ 104 million km²", S.c("one hundred and four"), size=48, color=GREEN, box=True)
    S.text(0.5, 0.27, "+ almost 5 million km² in a year", S.c("Almost five"), S.c("At that pace"), size=44,
           color=AMBER, box=True)
    S.caption("At that pace: roughly 50 more years", S.c("At that pace"), color=PINK)
    S.text(0.5, 0.78, "Seabed 2030 (Nippon Foundation-GEBCO), April 2026", 0.5, size=26, color=MUTED, font=REG)
    S.fade_in_out(0.3, 0.3)


def s14_seen(S):
    section(S, depth_max=6000, top=5000)
    ax = S.ax
    xs = np.linspace(0, 16, 300)
    floor = -4200 - 500 * np.sin(xs * 0.9) - 300 * np.sin(xs * 2.7 + 1)
    ax.fill_between(xs, floor, -7000, color="#2a3f5a", zorder=2.5)
    # sonar fan
    fan = MPoly([[5.5, -60], [3.2, -4500], [7.8, -4500]], closed=True, fc=GREEN, ec="none", alpha=0, zorder=2)
    ax.add_patch(fan)
    fade(S, [fan], S.c("sonar outlines"), peak=0.25)
    ship = MPoly([[4.9, 0], [6.1, 0], [6.3, 250], [4.7, 250]], closed=True, fc=WHITE, ec="none", zorder=6)
    ax.add_patch(ship)
    # tiny light
    light = ax.scatter([11.5], [-3900], s=0, color=AMBER, zorder=7)
    t_l = S.c("less than zero")

    def up(t):
        light.set_sizes([60 * ease((t - t_l) / 0.5)])
    S.updaters.append(up)
    S.headline("MAPPED IS NOT SEEN", 0.3)
    S.text(0.5, 0.72, "< 0.001%", t_l, size=110, color=AMBER, pop=True)
    S.text(0.5, 0.63, "of the seafloor directly seen by scientists", t_l + 0.3, size=30, font=REG)
    S.caption("Sonar outlines: more than a quarter. Eyes on: almost none", S.c("sonar outlines"), color=GREEN)
    S.fade_in_out(0.3, 0.3)


def s15_species(S):
    basemap(S, lon0=-20, glow=(0.2, None), keys=[(0, 30, 0, 380), (S.c("And in October") - 0.4, 30, 0, 380),
                                                (S.c("And in October") + 1.4, -45, -36, 110), (S.T, -48, -38, 100)])
    t_o = S.c("And in October")
    S.headline("STILL FINDING NEW LIFE", 0.3)
    stat(S, 0.5, 0.66, "1,121", "new species in one recent year (Ocean Census Alliance)", S.c("one thousand"), GREEN,
         S.c("Seven hundred"), bsize=110)
    stat(S, 0.5, 0.66, "728", "of them from specimens already in museums", S.c("Seven hundred"), AMBER,
         S.c("On average"), bsize=110)
    stat(S, 0.5, 0.66, "13+ years", "average wait from collection to description", S.c("On average"), PINK, t_o,
         bsize=96)
    sh = Rectangle((0, 0), 1, 1, transform=S.fig.transFigure, color="#07111d", zorder=30, alpha=0)
    S.fig.add_artist(sh)
    fade(S, [sh], S.c("one thousand") - 0.3, t_o, peak=0.6)
    x = ((-55.5 - (-20) + 180) % 360) - 180
    p = equal_earth(np.array([[x, -38.0]]))[0]
    sc = S.ax.scatter([p[0]], [p[1]], s=0, color=GREEN, edgecolors=WHITE, linewidths=2, zorder=30)

    def up(t):
        sc.set_sizes([300 * ease((t - t_o - 1.2) / 0.4)])
    S.updaters.append(up)
    mlabel(S, -55.5, -34.5, "Mar del Plata Canyon (approx.)", t_o + 1.4, lon0=-20, color=GREEN, size=26)
    S.caption("57 new species from one canyon, over 3,500 m deep (Oct 2026)", t_o + 1.6, color=GREEN, size=32)
    S.fade_in_out(0.3, 0.3)


def s16_highseas(S):
    basemap(S, lon0=-160, glow=(S.c("Roughly two"), None), keys=[(0, 0, 0, 380), (S.T, 0, 0, 368)])
    S.headline("WHO OWNS THE OCEAN?", 0.3)
    stat(S, 0.5, 0.7, "≈ 2/3", "of the ocean is outside any single country's jurisdiction", S.c("Roughly two"),
         CYAN, S.c("Less than one"))
    stat(S, 0.5, 0.7, "< 1%", "of the high seas is in marine protected areas", S.c("Less than one"), PINK,
         S.c("That's why"))
    S.text(0.5, 0.62, "HIGH SEAS TREATY", S.c("That's why"), size=70, color=AMBER, box=True, pop=True)
    S.text(0.5, 0.5, "In force: 17 January 2026", S.c("came into force"), size=44, color=WHITE, box=True)
    S.text(0.5, 0.4, "First conference of the parties: due within a year", S.c("first conference"), size=36,
           color=MUTED, box=True)
    S.fade_in_out(0.3, 0.3)


def s17_recap(S):
    basemap(S, lon0=-160, oceans={"Pacific": (0.2, None)}, keys=[(0, 0, 0, 380), (S.T, 0, 0, 360)])
    S.headline("THE OCEANS AT TRUE SCALE", 0.2)
    lines = [("Pacific > all the land on Earth", "one ocean", CYAN),
             ("Average depth ≈ 3.7 km", "An average depth", VIOLET),
             ("Everest + about 2 km of water", "A trench", AMBER),
             ("Mapped: under a third. Seen: almost none", "And a seafloor", PINK)]
    for i, (s, ph, c) in enumerate(lines):
        S.text(0.5, 0.7 - i * 0.13, s, S.c(ph), size=44, color=c, box=True, pop=True)
    S.fade_in_out(0.3, 0.3)


def s18_outro(S):
    basemap(S, lon0=-160, glow=(0.0, None), keys=[(0, 0, 0, 370), (S.T, 0, 0, 350)])
    opts = [("Pacific beats all the land", "the Pacific beating", CYAN),
            ("Everest vanishes in the trench", "Everest vanishing", AMBER),
            ("How little we've mapped", "how little", PINK)]
    S.headline("WHICH SURPRISED YOU MOST?", 0.3)
    for i, (s, ph, c) in enumerate(opts):
        S.text(0.5, 0.68 - i * 0.12, f"{i + 1}. {s}", S.c(ph), size=44, color=c, box=True, pop=True)
    S.text(0.5, 0.2, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=54, color=WHITE, box=True, pop=True)
    S.fade_in_out(0.3, 0.8)
