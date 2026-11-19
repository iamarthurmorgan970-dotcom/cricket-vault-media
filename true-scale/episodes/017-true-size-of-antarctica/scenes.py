"""017 How Big Is Antarctica Really? Each function takes the Scene S; S.c("phrase") is when the narrator says it.
Polar maps use a Lambert azimuthal equal-area projection centred on the South Pole, so every area shown is true.
Antarctica = Natural Earth land + ice shelves (together about 13.8M km², close to the usual 14.2M figure)."""
import json
from engine.core import *
from engine.core import Scene
from engine.geo import DATA, _rings
from engine.india import INDIA_POV
from matplotlib.patches import Ellipse, Wedge, Polygon as MPoly
from shapely.geometry import Polygon as SPoly, shape
from shapely.ops import unary_union

ICE, SHELF, ICE_E = "#e8f4ff", "#a9cbe6", "#ffffff"
SEA_ICE = "#7fb3d9"
R_KM = 6371.0


def P(a):
    """Lambert azimuthal equal-area, south polar aspect (lon 0 up, 90E right). Units: Earth radius = 1."""
    lon = np.radians(a[:, 0])
    c = np.radians(90 + np.clip(a[:, 1], -90, 90))
    rho = 2 * np.sin(c / 2)
    return np.column_stack([rho * np.sin(lon), rho * np.cos(lon)])


ANT = COUNTRIES["Antarctica"]
SHELVES = [r for f in json.load(open(f"{DATA}/ne_50m_antarctic_ice_shelves_polys.geojson"))["features"]
           for r in _rings(shape(f["geometry"]), 0.04)]
SOUTH = [n for n in COUNTRIES if n != "Antarctica" and min(r[:, 1].min() for r in COUNTRIES[n]) < -20]
AUS = COUNTRIES["Australia"]
IND_HOME, AUS_HOME = (79.0, 22.0), (134.0, -25.0)
IND_T, AUS_T = (-60.0, -81.0), (90.0, -76.0)       # where they land on the ice (set from a placement search)

_full = unary_union([SPoly(P(r)).buffer(0) for r in ANT + SHELVES])


def _sea_ice_rings():
    """A simplified sea-ice belt: Antarctica grown outward until the belt itself covers 17.59M km² (true area)."""
    target = 17.59e6 / R_KM ** 2
    lo, hi = 0.0, 0.5
    for _ in range(30):
        mid = (lo + hi) / 2
        if _full.buffer(mid).area - _full.area < target:
            lo = mid
        else:
            hi = mid
    g = _full.buffer(lo).simplify(0.004)
    return [np.asarray(p.exterior.coords) for p in (g.geoms if hasattr(g, "geoms") else [g])]


SEA = _sea_ice_rings()


def _sector(l0, l1):
    pts = [(l, -60.0) for l in np.linspace(l0, l1, 60)] + [(l1, -90.0), (l0, -90.0)]
    g = SPoly(P(np.array(pts))).intersection(_full)
    return [np.asarray(p.exterior.coords) for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.area > 1e-5]


AAT = _sector(45, 136) + _sector(142, 160)          # Australian Antarctic Territory (antarctica.gov.au)
ADELIE = _sector(136, 142)                          # French Adélie Land

VIEW = (0.0, 0.02, 2.0)


def polygons(S, rings, fc, ec, lw=1.0, z=3, alpha=1.0, proj=True):
    pc = PolyCollection([P(r) if proj else r for r in rings], facecolors=fc, edgecolors=ec, linewidths=lw,
                        zorder=z, alpha=alpha)
    S.ax.add_collection(pc)
    return pc


def fade(S, arts, t0, t1=None, peak=1.0, dur=0.6):
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / dur), ease((t1 - t) / dur)) * peak
        for x in arts:
            x.set_alpha(a)
    S.updaters.append(up)


def polar(S, keys=None, dim=False, sea=None):
    """South-polar base map. sea=(t0, t1) shows the simplified sea-ice belt."""
    lines = []
    for lat in (-80, -70, -60, -50, -40):
        lon = np.linspace(-180, 180, 361)
        lines.append(P(np.column_stack([lon, np.full_like(lon, lat)])))
    for lon in range(-180, 180, 30):
        lat = np.linspace(-90, -35, 60)
        lines.append(P(np.column_stack([np.full_like(lat, lon), lat])))
    S.ax.add_collection(LineCollection(lines, colors=GRID, linewidths=0.9, zorder=0.5))
    S.ax.add_collection(PolyCollection([P(r) for n in SOUTH for r in COUNTRIES[n]], facecolors=LAND,
                                       edgecolors=EDGE, linewidths=0.5, zorder=1))
    if sea:
        pc = polygons(S, SEA, SEA_ICE, "#cfe6f7", lw=0.8, z=1.5, proj=False, alpha=0)
        fade(S, [pc], sea[0], sea[1], peak=0.55)
    a = 0.55 if dim else 1.0
    polygons(S, SHELVES, SHELF, "#d9ecfa", lw=0.5, z=2, alpha=a)
    polygons(S, ANT, ICE, ICE, lw=0.6, z=2.5, alpha=a)
    S.camera(keys or [(0, *VIEW), (S.T, *VIEW)])
    S.brand()


def label(S, lon, lat, s, t0, t1=None, color=WHITE, size=26, dy=0.0, dx=0.0):
    p = P(np.array([[lon, lat]]))[0]
    tx = S.ax.text(p[0] + dx, p[1] + dy, s, fontproperties=BOLD, size=size, color=color, ha="center", va="center",
                   zorder=40, alpha=0, bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        tx.set_alpha(a)
        tx.get_bbox_patch().set_alpha(0.75 * a)
    S.updaters.append(up)
    return tx


def pin(S, lon, lat, s, t0, color=AMBER, dy=0.035, size=24, t1=None, dx=0.0):
    p = P(np.array([[lon, lat]]))[0]
    sc = S.ax.scatter([p[0]], [p[1]], s=0, color=color, edgecolors=WHITE, linewidths=2, zorder=45)
    tx = S.ax.text(p[0] + dx, p[1] + dy, s, fontproperties=BOLD, size=size, color=color, ha="center", va="bottom",
                   zorder=46, alpha=0, bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.35), ease((t1 - t) / 0.35))
        sc.set_sizes([170 * a])
        tx.set_alpha(a)
        tx.get_bbox_patch().set_alpha(0.75 * a)
    S.updaters.append(up)


def drop(S, rings, home, target, t0, dur=3.0, color=PINK, name=None, label_dy=0.0):
    """Slide a country in from the open ocean (true shape and area) onto its target on the ice."""
    start = (target[0], -38.0)
    r0 = move(rings, home, start, 1.0)
    return S.mover(r0, start, target, t0, t0 + dur, color=color, label=name, label_dy=label_dy, ghost=False, proj=P,
                   z=8)


def placed(S, rings, home, target, t0, color=PINK, name=None, t1=None, peak=0.85):
    rr = move(rings, home, target, 1.0)
    pc = polygons(S, rr, color, WHITE, lw=1.2, z=8, alpha=0)
    fade(S, [pc], t0, t1, peak=peak)
    if name:
        label(S, target[0], target[1], name, t0 + 0.2, t1, size=24)
    return pc


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    t_real = S.c("In reality")
    S.graticule()
    S.world()
    S.highlight(["Antarctica"], ICE, 0.2, t_real, peak=0.95)
    S.camera([(0, 0, mercy(-30), 380), (t_real - 0.3, 0, mercy(-55), 380)])
    S.headline("ON MOST MAPS: A WHITE SMEAR", S.c("thin white"), t_real - 0.2, y=0.88)
    # the real thing, on an equal-area polar map, drawn over the Mercator view
    ov = S.fig.add_axes([0, 0, 1, 1])
    ov.set_axis_off()
    ov.set_xlim(-1.0 * W / H, 1.0 * W / H)
    ov.set_ylim(-1.0, 1.0)
    bg = Rectangle((0, 0), 1, 1, transform=ov.transAxes, color=OCEAN, zorder=0, alpha=0)
    ov.add_patch(bg)
    k = 1.55                                          # fit the continent to the overlay
    land = PolyCollection([P(r) * k for n in SOUTH for r in COUNTRIES[n]], facecolors=LAND, edgecolors=EDGE,
                          linewidths=0.5, zorder=1, alpha=0)
    sh = PolyCollection([P(r) * k for r in SHELVES], facecolors=SHELF, edgecolors="#d9ecfa", linewidths=0.5,
                        zorder=2, alpha=0)
    an = PolyCollection([P(r) * k for r in ANT], facecolors=ICE, edgecolors=ICE, linewidths=0.6, zorder=2.5,
                        alpha=0)
    ind = PolyCollection([P(r) * k for r in move(INDIA_POV, IND_HOME, IND_T, 1)], facecolors=PINK,
                         edgecolors=WHITE, linewidths=1.2, zorder=3, alpha=0)
    au = PolyCollection([P(r) * k for r in move(AUS, AUS_HOME, AUS_T, 1)], facecolors=AMBER, edgecolors=WHITE,
                        linewidths=1.2, zorder=3, alpha=0)
    for c in (land, sh, an, ind, au):
        ov.add_collection(c)
    t_ind, t_fw = S.c("bigger than India"), S.c("Its ice holds")

    def up(t):
        a = ease((t - t_real) / 0.6)
        ov.set_visible(a > 0)
        for x in (bg, land, sh, an):
            x.set_alpha(a)
        ind.set_alpha(0.85 * min(ease((t - t_ind) / 0.4), ease((t_fw - t) / 0.4)))
        au.set_alpha(0.85 * min(ease((t - t_ind - 0.8) / 0.4), ease((t_fw - t) / 0.4)))
    S.updaters.append(up)
    S.text(0.5, 0.9, "BIGGER THAN INDIA + AUSTRALIA", t_ind, t_fw, size=46, box=True, pop=True, zorder=80)
    S.text(0.5, 0.1, "...with room for almost another India", S.c("with room"), t_fw, size=32, color=MUTED,
           font=REG, box=True, zorder=80)
    S.text(0.5, 0.9, "≈ 70% OF EARTH'S FRESH WATER", t_fw, S.c("And this year"), size=46, color=CYAN, box=True,
           pop=True, zorder=80)
    S.text(0.5, 0.9, "2026: ONE OF THE SMALLEST SEA-ICE PEAKS EVER", S.c("And this year"), S.c("So how big"),
           size=40, color=AMBER, box=True, pop=True, zorder=80)
    S.text(0.5, 0.5, "HOW BIG IS IT REALLY?", S.c("So how big"), size=80, color=WHITE, box=True, pop=True, zorder=80)
    S.fade_in_out(0.5, 0)
    S.brand()


def s02_title(S):
    polar(S, [(0, 0, 0.02, 2.4), (S.T, 0, 0.02, 2.1)], dim=True)
    S.text(0.5, 0.58, "HOW BIG IS", 0.3, size=96, pop=True)
    S.text(0.5, 0.45, "ANTARCTICA REALLY?", 0.7, size=96, color=CYAN, pop=True)
    S.text(0.5, 0.33, "The frozen continent at its true scale", 1.2, size=30, color=MUTED, font=REG)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=AMBER)


def s03_mercator(S):
    t_globe = S.c("Now look at the same")
    S.graticule()
    S.world()
    S.highlight(["Antarctica"], ICE, 0.3, t_globe, peak=0.95, pulse=True)
    S.camera([(0, 0, mercy(20), 380), (S.c("stretches everything"), 0, mercy(0), 380),
              (S.c("Near the poles"), 0, mercy(-50), 380), (t_globe, 0, mercy(-62), 380)])
    S.headline("1569: GERARDUS MERCATOR'S MAP FOR SAILORS", S.c("In fifteen"), S.c("stretches everything"), size=40)
    S.headline("STRETCHING GROWS AWAY FROM THE EQUATOR", S.c("stretches everything"), S.c("Near the poles"), size=40)
    S.headline("AT THE POLES: STRETCHED WITHOUT LIMIT", S.c("Near the poles"), S.c("So on a Mercator"), size=40)
    S.headline("ANTARCTICA BECOMES A WHITE BAND", S.c("So on a Mercator"), t_globe, size=40, color=CYAN)
    # equal-area polar view fades in on top
    ov = S.fig.add_axes([0, 0, 1, 1])
    ov.set_axis_off()
    ov.set_xlim(-1.0 * W / H, 1.0 * W / H)
    ov.set_ylim(-1.0, 1.0)
    bg = Rectangle((0, 0), 1, 1, transform=ov.transAxes, color=OCEAN, zorder=0, alpha=0)
    ov.add_patch(bg)
    k = 1.55
    lines = []
    for lat in (-80, -70, -60, -50, -40):
        lon = np.linspace(-180, 180, 361)
        lines.append(P(np.column_stack([lon, np.full_like(lon, lat)])) * k)
    for lon in range(-180, 180, 30):
        lat = np.linspace(-90, -35, 60)
        lines.append(P(np.column_stack([np.full_like(lat, lon), lat])) * k)
    grid = LineCollection(lines, colors=GRID, linewidths=0.9, zorder=0.5, alpha=0)
    land = PolyCollection([P(r) * k for n in SOUTH for r in COUNTRIES[n]], facecolors=LAND, edgecolors=EDGE,
                          linewidths=0.5, zorder=1, alpha=0)
    sh = PolyCollection([P(r) * k for r in SHELVES], facecolors=SHELF, edgecolors="#d9ecfa", linewidths=0.5,
                        zorder=2, alpha=0)
    an = PolyCollection([P(r) * k for r in ANT], facecolors=ICE, edgecolors=ICE, linewidths=0.6, zorder=2.5,
                        alpha=0)
    for c in (grid, land, sh, an):
        ov.add_collection(c)
    pole = ov.scatter([0], [0], s=0, color=PINK, edgecolors=WHITE, linewidths=2, zorder=5)
    pt = ov.text(0.0, -0.07, "SOUTH POLE", fontproperties=BOLD, size=22, color=PINK, ha="center", va="top",
                 zorder=6, alpha=0)
    t_pole = S.c("South Pole")

    def up(t):
        a = ease((t - t_globe) / 0.8)
        ov.set_visible(a > 0)
        for x in (bg, grid, land, sh, an):
            x.set_alpha(a)
        b = ease((t - t_pole) / 0.4)
        pole.set_sizes([150 * b])
        pt.set_alpha(b)
    S.updaters.append(up)
    S.text(0.5, 0.92, "SEEN FROM BELOW: THE REAL SHAPE", t_globe + 0.4, size=44, box=True, pop=True, zorder=80)
    S.text(0.04, 0.05, "Equal-area polar map", t_globe + 0.8, size=22, color=MUTED, font=REG, ha="left", zorder=80)
    S.brand()


def s04_area(S):
    polar(S, [(0, *VIEW), (S.T, 0.25, 0.02, 2.2)])
    S.headline("≈ 14.2 MILLION KM²", S.c("Its real area"), y=0.92, size=50)
    S.text(0.5, 0.82, "5th LARGEST OF 7 CONTINENTS", S.c("fifth largest"), S.c("For Indian"), size=34,
           color=CYAN, box=True)
    S.text(0.5, 0.82, "≈ 40% BIGGER THAN EUROPE  ·  ALMOST 2 × AUSTRALIA", S.c("forty percent"), S.c("For Indian"),
           size=30, color=WHITE, box=True, zorder=55)
    S.bars([("Antarctica", 14.2, ICE, S.c("Its real area")),
            ("Australia", 7.69, AMBER, S.c("double the size")),
            ("India", 3.29, PINK, S.c("India covers"))],
           S.c("Its real area") - 0.3, rect=(0.72, 0.16, 0.2, 0.3), xmax=22, unit="M km²", dec=2, label_left=True)
    S.text(0.5, 0.82, "MORE THAN 4 × INDIA", S.c("more than four"), size=50, color=PINK, box=True, pop=True,
           zorder=60)
    S.text(0.04, 0.05, "Equal-area polar map", 0.5, size=22, color=MUTED, font=REG, ha="left")


def s05_fit(S):
    polar(S)
    t_i, t_a = S.c("place it on the ice"), S.c("Now add Australia")
    drop(S, INDIA_POV, IND_HOME, IND_T, t_i - 1.5, 2.8, color=PINK, name="INDIA")
    drop(S, AUS, AUS_HOME, AUS_T, t_a, 3.0, color=AMBER, name="AUSTRALIA")
    S.headline("INDIA AT TRUE SIZE AND SHAPE", S.c("Take India"), t_a, y=0.92)
    S.headline("+ AUSTRALIA", t_a, S.c("Together"), y=0.92, color=AMBER)
    S.headline("MOST OF IT... BUT NOT ALL", S.c("Together"), S.c("Add up"), y=0.92)
    S.bars([("Antarctica", 14.2, ICE, S.c("Add up")),
            ("India + Aus. + rest",
             [(3.29, PINK), (7.69, AMBER), (3.22, CYAN)], None, S.c("Add up") + 0.8)],
           S.c("Add up") - 0.3, rect=(0.2, 0.14, 0.24, 0.16), xmax=21, unit="M km²", dec=1, label_left=True)
    S.text(0.5, 0.92, "LEFT OVER ≈ 3.2M KM²: ALMOST ONE MORE INDIA", S.c("three point two"), size=40, color=CYAN,
           box=True, pop=True, zorder=60)
    S.text(0.96, 0.075, "Equal-area map; outline includes ice shelves", 0.5, size=20, color=MUTED, font=REG,
           ha="right")


def tall_chart(S, ymax):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(-0.2 * ymax, ymax * 1.25)
    ax.plot([0, 16], [0, 0], color=MUTED, lw=2, zorder=3)
    for k in range(1000, int(ymax) + 1, 1000):
        ax.plot([0, 16], [k, k], color="#16283c", lw=1, zorder=0)
        ax.text(0.15, k + 40, f"{k:,} m", fontproperties=REG, size=16, color=MUTED, va="bottom")


def burj(S, x, base, t0, w=0.9, color=AMBER, alpha=1.0):
    h = 828
    pts = [(x - w / 2, base), (x + w / 2, base), (x + w * 0.28, base + h * 0.45), (x + w * 0.14, base + h * 0.75),
           (x + w * 0.04, base + h), (x - w * 0.04, base + h), (x - w * 0.14, base + h * 0.75),
           (x - w * 0.28, base + h * 0.45)]
    p = MPoly(pts, closed=True, fc=color, ec=WHITE, lw=1.0, zorder=6, alpha=0)
    S.ax.add_patch(p)
    fade(S, [p], t0, peak=alpha, dur=0.35)
    return p


def column(S, x, h, t0, color, text, sub, w=2.4, dur=1.4):
    r = Rectangle((x - w / 2, 0), w, 0, fc=color, ec=WHITE, lw=1.2, zorder=4, alpha=0.92)
    S.ax.add_patch(r)
    lab = S.ax.text(x, 0, "", fontproperties=BOLD, size=26, color=WHITE, ha="center", va="bottom", zorder=8)
    sb = S.ax.text(x, -90, sub, fontproperties=BOLD, size=20, color=color, ha="center", va="top", zorder=8, alpha=0)

    def up(t):
        g = ease2((t - t0) / dur)
        r.set_height(h * g)
        r.set_alpha(0.92 if g > 0 else 0)
        lab.set_position((x, h * g + 60))
        lab.set_text(text if g > 0.97 else (f"{h * g:,.0f} m" if g > 0.02 else ""))
        sb.set_alpha(ease((t - t0) / 0.4))
    S.updaters.append(up)


def s06_ice(S):
    tall_chart(S, 5000)
    S.text(0.5, 0.93, "HOW THICK IS THE ICE?", 0.3, size=46, pop=True)
    S.text(0.5, 0.87, "Ice thickness, metres (Bedmap3 survey, 2025)", 0.6, size=24, color=MUTED, font=REG)
    t_b = S.c("The tallest building")
    burj(S, 2.6, 0, t_b)
    S.ax.text(2.6, -90, "BURJ KHALIFA\n828 m", fontproperties=BOLD, size=20, color=AMBER, ha="center", va="top",
              zorder=8, alpha=0)
    fade(S, [S.ax.texts[-1]], t_b)
    column(S, 6.0, 1948, S.c("about one point nine"), CYAN, "≈ 1.9 km", "AVERAGE ICE")
    t_2 = S.c("more than two Burj")
    for k in range(2):
        burj(S, 7.8, k * 828, t_2 + 0.3 * k, w=0.7)
    column(S, 11.2, 4757, S.c("At its thickest"), ICE, "≈ 4,757 m", "THICKEST\n(East Antarctica)")
    t_5 = S.c("Stack five")
    for k in range(5):
        burj(S, 13.6, k * 828, t_5 + 0.35 * k, w=0.8)
    S.ax.text(13.6, -90, "5 × BURJ\n= 4,140 m", fontproperties=BOLD, size=20, color=AMBER, ha="center", va="top",
              zorder=8, alpha=0)
    fade(S, [S.ax.texts[-1]], t_5)
    S.text(0.3, 0.62, "STILL SHORT OF THE BOTTOM", t_5 + 2.0, size=36, color=AMBER, box=True, pop=True)
    S.brand()


def s07_water(S):
    S.ax.set_xlim(0, 16)
    S.ax.set_ylim(0, 9)
    S.text(0.5, 0.92, "≈ 27 MILLION KM³ OF ICE", S.c("Add it all"), size=50, box=True, pop=True)
    # donut: 70% of fresh water
    t70 = S.c("seventy percent")
    ax2 = S.fig.add_axes([0.06, 0.16, 0.38, 0.6])
    ax2.set_axis_off()
    ax2.set_xlim(-1.3, 1.3)
    ax2.set_ylim(-1.3, 1.3)
    ax2.set_aspect("equal")
    ring_bg = Wedge((0, 0), 1.0, 0, 360, width=0.32, fc="#1d2d42", ec="none", alpha=0)
    ring = Wedge((0, 0), 1.0, 90, 90, width=0.32, fc=CYAN, ec="none", alpha=0)
    ax2.add_patch(ring_bg)
    ax2.add_patch(ring)
    num = ax2.text(0, 0.05, "", fontproperties=BOLD, size=60, color=WHITE, ha="center", va="center", alpha=0)
    sub = ax2.text(0, -0.32, "of Earth's\nfresh water", fontproperties=REG, size=22, color=MUTED, ha="center",
                   va="center", alpha=0)

    def up(t):
        a = ease((t - t70 + 0.3) / 0.4)
        g = ease2((t - t70) / 1.4)
        for x in (ring_bg, ring, num, sub):
            x.set_alpha(a)
        ring.set_theta1(90 - 360 * 0.70 * g)
        num.set_text(f"{70 * g:.0f}%")
    S.updaters.append(up)
    # sea level: +58 m against a 15-storey building (schematic)
    t58 = S.c("fifty eight metres")
    ax3 = S.fig.add_axes([0.56, 0.22, 0.38, 0.58])
    ax3.set_axis_off()
    ax3.set_xlim(0, 10)
    ax3.set_ylim(-4, 70)
    floors = []
    for k in range(15):
        f = Rectangle((3.6, k * 3.5), 2.8, 3.2, fc="#3b5476", ec="#6d8fb8", lw=1, zorder=2, alpha=0)
        ax3.add_patch(f)
        floors.append(f)
    blab = ax3.text(5.0, -1.5, "15-storey building", fontproperties=BOLD, size=20, color=MUTED, ha="center",
                    va="top", alpha=0)
    water = Rectangle((0, 0), 10, 0, fc="#1f6fb2", ec="none", zorder=3, alpha=0)
    ax3.add_patch(water)
    wl, = ax3.plot([0, 10], [0, 0], color=CYAN, lw=3, zorder=4, alpha=0)
    wt = ax3.text(9.8, 0, "", fontproperties=BOLD, size=30, color=CYAN, ha="right", va="bottom", zorder=5, alpha=0)
    t_bld = S.c("If every bit")

    def up2(t):
        a = ease((t - t_bld) / 0.5)
        for f in floors:
            f.set_alpha(a)
        blab.set_alpha(a)
        g = ease2((t - t58) / 2.2)
        lv = 58 * g
        water.set_height(lv)
        water.set_alpha(0.55 * ease((t - t58) / 0.3))
        wl.set_ydata([lv, lv])
        wl.set_alpha(ease((t - t58) / 0.3))
        wt.set_position((9.8, lv + 0.8))
        wt.set_text(f"+{lv:.0f} m" if g > 0 else "")
        wt.set_alpha(ease((t - t58) / 0.3))
    S.updaters.append(up2)
    S.text(0.5, 0.14, "A MEASURE OF STORED WATER, NOT A FORECAST", S.c("It isn't a forecast"), size=34, color=AMBER, box=True)
    S.text(0.96, 0.075, "Sources: Bedmap3 (2025); Wikipedia. Building schematic.", 0.5, size=18, color=MUTED,
           font=REG, ha="right")
    S.brand()


LAKE_VOSTOK, VOSTOK_STN = (106.0, -77.5), (106.8, -78.47)


def s08_vostok(S):
    p = P(np.array([LAKE_VOSTOK]))[0]
    t_z = S.c("The biggest is")
    polar(S, [(0, *VIEW), (t_z, *VIEW), (t_z + 3.0, p[0] - 0.03, p[1], 0.16), (S.T, p[0] - 0.03, p[1], 0.15)])
    # schematic lake, true length/width (250 x 50 km), long axis roughly along the meridian
    ang = np.degrees(np.arctan2(p[1], p[0]))
    e = Ellipse((p[0], p[1]), 250 / R_KM, 50 / R_KM, angle=ang + 12, fc="#1f6fb2", ec=CYAN, lw=2, zorder=6, alpha=0)
    S.ax.add_patch(e)
    fade(S, [e], t_z + 2.0, peak=0.95)
    label(S, LAKE_VOSTOK[0], LAKE_VOSTOK[1], "LAKE VOSTOK", t_z + 2.4, size=26, dy=0.014, color=CYAN)
    S.headline("LAKES UNDER THE ICE", S.c("there are lakes"), t_z + 2.4, y=0.92)
    S.text(0.04, 0.82, "≈ 250 km LONG", S.c("two hundred and fifty"), size=36, color=CYAN, ha="left", box=True)
    S.text(0.04, 0.72, "UP TO ≈ 50 km WIDE", S.c("up to fifty"), size=36, color=CYAN, ha="left", box=True)
    S.text(0.04, 0.62, "≈ 4 km OF ICE ON TOP", S.c("four kilometres"), size=36, color=WHITE, ha="left", box=True)
    S.text(0.04, 0.52, "CONFIRMED FROM SPACE: 1993", S.c("confirmed from space"), size=32, color=WHITE, ha="left",
           box=True)
    S.text(0.04, 0.42, "SEALED OFF ≈ 15 MILLION YEARS?", S.c("fifteen million"), size=32, color=AMBER, ha="left",
           box=True)
    S.text(0.04, 0.32, "FEB 2012: DRILL REACHES IT", S.c("In February"), size=32, color=PINK, ha="left", box=True)
    S.text(0.96, 0.075, "Lake outline simplified; true length and width", t_z + 2.4, size=20, color=MUTED, font=REG,
           ha="right")


def s09_cold(S):
    p = P(np.array([VOSTOK_STN]))[0]
    polar(S, [(0, *VIEW), (S.c("at Russia's"), p[0] * 0.6, p[1] * 0.6, 1.3), (S.T, p[0] * 0.6, p[1] * 0.6, 1.25)])
    S.headline("THE COLDEST PLACE ON EARTH", S.c("coldest place"), y=0.92)
    pin(S, *VOSTOK_STN, "VOSTOK STATION", S.c("at Russia's"), color=CYAN)
    S.text(0.04, 0.71, "−89.2 °C", S.c("minus eighty"), size=84, color=CYAN, ha="left", box=True, pop=True)
    S.text(0.04, 0.62, "Thermometer record · 21 July 1983", S.c("the twenty first"), size=28, color=WHITE,
           font=REG, ha="left", box=True)
    S.text(0.04, 0.46, "≈ −98 °C", S.c("minus ninety eight"), size=84, color=VIOLET, ha="left", box=True, pop=True)
    S.text(0.04, 0.35, "Satellite readings, snow hollows on the\nEast Antarctic Plateau (above 3,500 m)",
           S.c("On the high"), size=26, color=WHITE, font=REG, ha="left", box=True)
    S.text(0.96, 0.075, "Sources: Wikipedia; AGU / Geophysical Research Letters (2018)", 0.5, size=20, color=MUTED,
           font=REG, ha="right")


def s10_desert(S):
    polar(S, [(0, *VIEW), (S.T, -0.45, 0.02, 2.1)], dim=True)
    S.headline("A FROZEN DESERT", S.c("All that ice"), y=0.92, size=56)
    S.text(0.5, 0.82, "DESERT = LITTLE PRECIPITATION, NOT HEAT", S.c("A desert is defined"), S.c("Averaged"),
           size=34, color=AMBER, box=True)
    S.bars([("Continent average", 150, CYAN, S.c("one hundred and fifty")),
            ("Inland: under", 50, VIOLET, S.c("less than fifty"))],
           S.c("Averaged") - 0.3, rect=(0.26, 0.42, 0.22, 0.16), xmax=260, unit="mm / year", dec=0, label_left=True,
           title="Precipitation, water equivalent")
    S.text(0.5, 0.16, "COLDEST · DRIEST · WINDIEST", S.c("coldest, driest"), size=56, color=WHITE, box=True,
           pop=True)


def s11_sea_ice(S):
    t_sea = S.c("Every winter")
    polar(S, [(0, *VIEW), (t_sea, 0, 0.02, 2.7), (S.T, 0, 0.02, 2.6)], sea=(t_sea + 0.5, S.T + 1))
    S.headline("THE OCEAN FREEZES TOO", S.c("Every winter"), S.c("This year"), y=0.92)
    S.headline("14 SEP 2026: WINTER PEAK", S.c("This year"), S.c("That sounds"), y=0.92, color=CYAN)
    S.bars([("Sea ice, 2026 peak", 17.59, SEA_ICE, S.c("seventeen point")),
            ("Antarctica", 14.2, ICE, S.c("seventeen point") + 0.8)],
           S.c("seventeen point") - 0.3, rect=(0.16, 0.14, 0.18, 0.15), xmax=26, unit="M km²", dec=2, label_left=True)
    S.headline("3rd LOWEST PEAK SINCE SATELLITES (1978)", S.c("third lowest"), S.c("The record low"), y=0.92,
               color=AMBER, size=40)
    S.headline("RECORD LOW PEAK: 2023", S.c("The record low"), S.c("And in early"), y=0.92, color=AMBER)
    S.headline("OCT 2026: RECORD DAILY LOWS (NSIDC)", S.c("And in early"), y=0.92, color=PINK, size=42)
    S.text(0.96, 0.075, "Sea-ice belt simplified; true total area", t_sea + 0.8, size=20, color=MUTED, font=REG,
           ha="right")
    S.text(0.96, 0.115, "Sources: NASA Earth Observatory; NSIDC", S.c("This year"), size=20, color=MUTED, font=REG,
           ha="right")


def s12_people(S):
    polar(S, [(0, *VIEW), (S.T, 0.3, 0.02, 2.1)], dim=True)
    S.headline("WHO LIVES THERE?", S.c("So who"), S.c("Nobody"), y=0.92)
    S.headline("NOBODY, PERMANENTLY", S.c("Nobody"), y=0.92, color=AMBER)
    S.bars([("Summer", 5000, AMBER, S.c("In summer")), ("Winter", 1000, CYAN, S.c("In winter"))],
           S.c("In summer") - 0.3, rect=(0.72, 0.56, 0.2, 0.14), xmax=8500, unit="people", dec=0, label_left=True,
           title="People living on the continent")
    S.text(0.785, 0.44, "70+ research stations", S.c("seventy research"), size=30, color=WHITE, box=True)
    S.text(0.785, 0.3, "≈ 118,000", S.c("one hundred and eighteen"), size=64, color=GREEN, box=True, pop=True)
    S.text(0.785, 0.2, "tourists, 2024-25 season (IAATO)", S.c("one hundred and eighteen"), size=24, color=WHITE,
           font=REG, box=True)


DG, MAITRI, BHARATI = (12.0, -70.08), (11.73, -70.77), (76.19, -69.41)


def s13_india(S):
    mid = P(np.array([(44.0, -70.0)]))[0]
    polar(S, [(0, *VIEW), (S.c("Two years"), *VIEW), (S.c("Today India"), 0.05, 0.2, 1.15),
              (S.T, 0.05, 0.2, 1.1)])
    S.headline("INDIA IN ANTARCTICA", 0.3, y=0.92, color=PINK)
    S.text(0.04, 0.8, "1981  First expedition", S.c("first Indian"), size=32, ha="left", box=True)
    S.text(0.04, 0.71, "1983  Dakshin Gangotri", S.c("Two years"), size=32, ha="left", box=True, color=MUTED)
    S.text(0.04, 0.62, "1990  Retired (half buried by ice)", S.c("retired"), size=28, ha="left", box=True,
           color=MUTED, font=REG)
    S.text(0.04, 0.53, "1989  Maitri", S.c("Maitri"), size=32, ha="left", box=True, color=AMBER)
    S.text(0.04, 0.44, "2012  Bharati", S.c("and Bharati"), size=32, ha="left", box=True, color=CYAN)
    pin(S, *DG, "DAKSHIN GANGOTRI", S.c("Dakshin"), color=MUTED, dy=0.03, size=20)
    pin(S, *MAITRI, "MAITRI", S.c("Maitri"), color=AMBER, dy=-0.07, size=24)
    pin(S, *BHARATI, "BHARATI", S.c("and Bharati"), color=CYAN, dy=0.03, size=24)
    S.text(0.96, 0.075, "Station positions approximate", 0.5, size=20, color=MUTED, font=REG, ha="right")


CLAIMANTS = ["Argentina", "Australia", "Chile", "France", "New Zealand", "Norway", "United Kingdom"]


def s14_owner(S):
    polar(S, [(0, *VIEW), (S.T, 0.3, 0.02, 2.1)])
    S.headline("WHO OWNS ANTARCTICA?", 0.3, S.c("Seven countries"), y=0.92)
    S.headline("7 COUNTRIES CLAIM SLICES", S.c("Seven countries"), S.c("But under"), y=0.92, color=AMBER)
    for i, n in enumerate(CLAIMANTS):
        S.text(0.04, 0.8 - i * 0.075, n.upper(), S.c(n.split()[0] if n != "United Kingdom" else "United Kingdom"),
               S.c("But under"), size=28, ha="left", box=True, color=AMBER if n == "Australia" else WHITE)
    aat = polygons(S, AAT, AMBER, WHITE, lw=1.0, z=5, proj=False, alpha=0)
    fade(S, [aat], S.c("Australia's claim"), S.c("But under"), peak=0.75)
    label(S, 95, -75, "AUSTRALIA'S CLAIM ≈ 42%", S.c("Australia's claim") + 0.3, S.c("But under"), color=AMBER,
          size=24)
    S.text(0.5, 0.08, "Argentina, Chile and UK claims overlap", S.c("overlap"), S.c("But under"), size=30,
           box=True)
    S.headline("ANTARCTIC TREATY, 1959", S.c("But under"), S.c("Fifty eight"), y=0.92, color=GREEN)
    S.text(0.04, 0.72, "Peace and science only", S.c("set aside"), S.c("Fifty eight"), size=32, ha="left", box=True)
    S.text(0.04, 0.63, "No military activity", S.c("No military"), S.c("Fifty eight"), size=32, ha="left", box=True)
    S.text(0.04, 0.54, "No new claims", S.c("no new claims"), S.c("Fifty eight"), size=32, ha="left", box=True)
    S.headline("58 PARTIES (2024)  ·  INDIA JOINED 1983", S.c("Fifty eight"), y=0.92, color=GREEN, size=40)
    S.text(0.96, 0.075, "Claim area: Australian Antarctic Division", S.c("Australia's claim"), size=20, color=MUTED,
           font=REG, ha="right")


def s15_recap(S):
    polar(S, [(0, -0.5, 0.02, 2.7), (S.T, -0.55, 0.02, 2.6)], sea=(S.c("And around it"), S.T + 1))
    placed(S, INDIA_POV, IND_HOME, IND_T, S.c("More than four"), color=PINK)
    placed(S, AUS, AUS_HOME, AUS_T, S.c("More than four") + 0.3, color=AMBER)
    rows = [("> 4 × INDIA OF LAND", "More than four", PINK), ("≈ 1.9 km OF ICE ON AVERAGE", "Ice almost", CYAN),
            ("≈ 70% OF EARTH'S FRESH WATER", "Seventy percent", WHITE),
            ("LAKE VOSTOK: ≈ 250 km LONG", "A hidden lake", CYAN), ("2026: 3rd LOWEST SEA-ICE PEAK", "And around it", AMBER)]
    for i, (s, ph, col) in enumerate(rows):
        S.text(0.04, 0.84 - i * 0.09, s, S.c(ph), size=30, color=col, ha="left", box=True)


def s16_outro(S):
    polar(S, [(0, 0.25, 0.02, 2.6), (S.T, 0.25, 0.02, 2.3)], dim=True)
    S.text(0.5, 0.75, "SIZE, ICE OR COLD?", S.c("Which fact"), size=72, color=CYAN, box=True, pop=True)
    S.text(0.5, 0.63, "Which surprised you most? Tell me in the comments", S.c("Tell me"), size=32, font=REG,
           box=True)
    S.text(0.5, 0.25, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=60, box=True, pop=True)
    S.fade_in_out(0, 1.5)
