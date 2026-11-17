"""007 Why There's No Bridge Between Europe and Africa. Each function takes the Scene S; S.c("phrase") is when the
narrator says it. Pin coordinates are approximate; cross-sections are schematic (not to scale unless stated)."""
from engine.core import *
from engine.core import Scene
from engine import geo
from engine.extras import dot, RED
from engine.timeline import TL, setup as tl_setup, ma
from matplotlib.patches import FancyArrow, Rectangle as Rect, Polygon as MPoly
from matplotlib.lines import Line2D

# Detailed coastlines for the strait close-ups (default world map is simplified for global views)
LOCAL = ["Spain", "Morocco", "Portugal", "Algeria", "France", "Gibraltar"]


def _load_10m():
    import json
    from shapely.geometry import shape
    d = json.load(open(f"{geo.DATA}/admin0_10m_ind.geojson"))
    out = {}
    for f in d["features"]:
        n = f["properties"]["ADMIN"]
        if n in LOCAL:
            out[n] = geo._rings(shape(f["geometry"]), 0.002)
    return out


_D = _load_10m()

# Approximate coordinates (lon, lat)
MARROQUI = (-5.61, 36.00)      # Point Marroquí, Tarifa (Spain)
CIRES = (-5.48, 35.91)         # Point Cires (Morocco)
TRAFALGAR = (-6.03, 36.18)
SPARTEL = (-5.92, 35.79)
PALOMA = (-5.72, 36.06)        # Punta Paloma (Spain)
MALABATA = (-5.75, 35.81)      # Punta Malabata (Morocco), near Tangier
TANGIER = (-5.81, 35.77)
TARIFA = (-5.60, 36.01)

STRAIT = (-5.65, mercy(35.95), 1.6)      # cx, cy, width in merc units


def P(lon, lat):
    return merc(np.array([[lon, lat]]))[0]


def local_map(S, keys=None, dim=False):
    S.world(fc="#1d2d42" if dim else LAND, names=[n for n in COUNTRIES if n not in LOCAL])
    for n in LOCAL:
        S.rings(_D[n], fc="#1d2d42" if dim else LAND, ec=EDGE, lw=1.0, z=2, alpha=1)
    S.camera(keys or [(0, *STRAIT), (S.T, *STRAIT)])
    S.brand()


def maplabel(S, lon, lat, s, t0, size=30, color=MUTED, t1=None, italic=False):
    p = P(lon, lat)
    art = S.ax.text(p[0], p[1], s, fontproperties=REG if italic else BOLD, size=size, color=color, ha="center",
                    va="center", zorder=20, alpha=0)
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        art.set_alpha(min(ease((t - t0) / 0.5), ease((t1 - t) / 0.5)))
    S.updaters.append(up)
    return art


def gap_line(S, a, b, label, t0, color=AMBER, size=30, t1=None, off=(0, 0), lw=4):
    pa, pb = P(*a), P(*b)
    ln, = S.ax.plot([], [], color=color, lw=lw, zorder=25, solid_capstyle="round")
    ends = S.ax.scatter([pa[0], pb[0]], [pa[1], pb[1]], s=0, color=color, edgecolors=WHITE, zorder=26)
    m = (pa + pb) / 2
    lab = S.ax.text(m[0] + off[0], m[1] + off[1], label, fontproperties=BOLD, size=size, color=color, ha="center",
                    va="center", zorder=27, alpha=0,
                    bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a_ = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        g = ease2((t - t0) / 0.9)
        q = pa + (pb - pa) * g
        ln.set_data([pa[0], q[0]], [pa[1], q[1]])
        ln.set_alpha(a_)
        ends.set_sizes([90 * a_, 90 * a_ * (g > 0.98)])
        la = a_ * ease((t - t0 - 0.6) / 0.4)
        lab.set_alpha(la)
        lab.get_bbox_patch().set_alpha(0.8 * la)
    S.updaters.append(up)


def card(S, x, y, s, t0, t1=None, size=34, color=WHITE, ha="center"):
    return S.text(x, y, s, t0, t1, size=size, color=color, box=True, pop=True, ha=ha)


def src(S, s, t0, t1=None):
    S.text(0.015, 0.03, s, t0, t1, size=19, color=MUTED, ha="left", font=REG)


def depth_chart(S, rows, title, t_title=0.3, maxd=1000, unit_note="Metres below sea level (to scale)"):
    """Columns hanging down from a sea surface, drawn to scale. rows: (NAME, sub, depth_m, colour, t0, label)."""
    ax = S.ax
    ax.set_xlim(0, 16)
    top, bot = 1.25 * maxd * 0.18, -maxd * 1.2
    ax.set_ylim(bot, top + maxd * 0.32)
    S.text(0.5, 0.92, title, t_title, size=44, pop=True)
    S.text(0.5, 0.855, unit_note, t_title + 0.3, size=24, color=MUTED, font=REG)
    sea = Rect((0, bot), 16, -bot, color="#0e2a47", zorder=0)
    ax.add_patch(sea)
    ax.plot([0, 16], [0, 0], color=CYAN, lw=3, zorder=2)
    ax.text(0.2, 15, "SEA LEVEL", fontproperties=BOLD, size=18, color=CYAN, va="bottom")
    step = 100 if maxd <= 500 else 200
    for k in range(step, int(maxd) + 1, step):
        ax.plot([0, 16], [-k, -k], color="#16334f", lw=1, zorder=1)
        ax.text(0.15, -k + 8, f"{k} m", fontproperties=REG, size=16, color=MUTED, va="bottom")
    n = len(rows)
    gap = (16 - 1.6) / n
    for i, (name, sub, d, col, t0, lab) in enumerate(rows):
        cx = 1.6 + gap * (i + 0.5)
        half = gap * 0.28
        r = Rect((cx - half, 0), 2 * half, 0, color=col, zorder=3, alpha=0.92)
        ax.add_patch(r)
        num = ax.text(cx, 0, "", fontproperties=BOLD, size=28, color=WHITE, ha="center", va="top", zorder=5)
        nm = ax.text(cx, maxd * 0.05, f"{name}\n{sub}", fontproperties=BOLD, size=21, color=col, ha="center",
                     va="bottom", zorder=5, alpha=0, linespacing=1.1)

        def up(t, r=r, num=num, nm=nm, t0=t0, d=d, cx=cx, lab=lab):
            g = ease2((t - t0) / 1.2)
            r.set_y(-d * g)
            r.set_height(d * g)
            num.set_position((cx, -d * g - maxd * 0.015))
            num.set_text(lab if g > 0.98 else (f"{d * g:,.0f} m" if g > 0.02 else ""))
            nm.set_alpha(ease((t - t0) / 0.4))
        S.updaters.append(up)
    S.brand()


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    S.graticule(step=10)
    local_map(S, [(0, -3, mercy(38), 30), (S.c("thirteen") + 0.2, *STRAIT), (S.c("That is shorter") - 0.3, *STRAIT),
                  (S.c("Yet there is"), -5.65, mercy(35.95), 2.2), (S.T, -5.65, mercy(35.95), 2.4)])
    maplabel(S, -4.3, 37.4, "EUROPE", 0.4, size=40, color=WHITE, t1=S.c("thirteen"))
    maplabel(S, -5.0, 33.5, "AFRICA", 0.6, size=40, color=WHITE, t1=S.c("thirteen"))
    gap_line(S, MARROQUI, CIRES, "13–14 KM", S.c("thirteen"), off=(0.33, 0.06), t1=S.c("That is shorter"), size=40)
    S.bars([("Atal Setu, Mumbai: sea section", 16.5, PINK, S.c("Atal Setu")),
            ("Europe to Africa at the narrowest point", 14.2, AMBER, S.c("Atal Setu") + 1.4)],
           S.c("That is shorter") - 0.2, rect=(0.14, 0.32, 0.68, 0.3), xmax=21, unit="km", t1=S.c("Yet there is"),
           title="LENGTH IN KM (strait: 13–14 km depending on source)")
    S.text(0.5, 0.62, "NO BRIDGE. NO TUNNEL. NO ROAD.", S.c("Yet there is"), S.c("So why"), size=60, color=WHITE,
           box=True, pop=True)
    S.text(0.5, 0.5, "WHY?", S.c("So why"), size=110, color=AMBER, box=True, pop=True)
    S.text(0.5, 0.2, "2026: SPAIN AND MOROCCO STILL FUNDING STUDIES", S.c("And why"), size=38, color=CYAN,
           box=True, pop=True)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    local_map(S, [(0, -5.65, mercy(35.95), 3.0), (S.T, *STRAIT)], dim=True)
    S.text(0.5, 0.6, "WHY THERE'S NO BRIDGE", 0.3, size=86, pop=True)
    S.text(0.5, 0.47, "BETWEEN EUROPE AND AFRICA", 0.7, size=74, color=AMBER, pop=True)
    S.text(0.5, 0.35, "The Strait of Gibraltar, at its true scale", 1.1, size=30, color=MUTED, font=REG)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=AMBER)


def s03_where(S):
    local_map(S, [(0, -5.0, mercy(36.0), 7.0), (S.c("fifty eight"), -5.65, mercy(35.97), 2.3),
                  (S.c("narrowest"), *STRAIT), (S.T, *STRAIT)])
    maplabel(S, -7.3, 35.3, "ATLANTIC\nOCEAN", S.c("Atlantic"), size=30, color=CYAN, t1=S.c("fifty eight"))
    maplabel(S, -3.2, 36.2, "MEDITERRANEAN\nSEA", S.c("Mediterranean"), size=30, color=CYAN, t1=S.c("fifty eight"))
    maplabel(S, -5.2, 36.9, "SPAIN", S.c("Spain"), size=36, color=WHITE)
    maplabel(S, -5.5, 35.2, "MOROCCO", S.c("Morocco"), size=36, color=WHITE)
    S.headline("STRAIT OF GIBRALTAR: ABOUT 58 KM LONG", S.c("fifty eight"), S.c("Ferries"), size=40)
    gap_line(S, TRAFALGAR, SPARTEL, "≈ 43 KM", S.c("forty three"), color=CYAN, off=(-0.3, 0.0))
    gap_line(S, MARROQUI, CIRES, "13–14 KM", S.c("narrowest"), off=(0.3, 0.07), size=34)
    dot(S, *MARROQUI, "Point Marroquí", S.c("Point Marroquí"), dy=0.03, size=22, t1=S.c("Ferries"))
    dot(S, *CIRES, "Point Cires", S.c("Point Cires"), dy=-0.09, size=22, t1=S.c("Ferries"))
    S.caption("FERRIES CROSS DAILY: FROM ABOUT 35 MINUTES", S.c("Ferries"), color=GREEN)
    src(S, "Width and length: Britannica (13 km), Wikipedia (14.2 km)", S.c("depending"), S.c("Ferries"))


def s04_ships(S):
    local_map(S, [(0, -5.6, mercy(35.95), 2.8), (S.T, -5.6, mercy(35.95), 2.5)])
    rng = np.random.default_rng(7)
    ships = []
    for i in range(26):
        lane = rng.uniform(35.93, 36.03)
        speed = rng.uniform(0.18, 0.3) * (1 if i % 2 else -1)
        x0 = rng.uniform(-6.6, -4.9)
        sc = S.ax.scatter([0], [0], s=0, color=AMBER if speed > 0 else CYAN, edgecolors=WHITE, linewidths=0.8,
                          zorder=22, marker="o")
        ships.append((sc, lane, speed, x0))
    t0 = S.c("More than")

    def up(t):
        a = ease((t - t0 + 0.5) / 0.6)
        for sc, lane, sp, x0 in ships:
            x = -6.6 + ((x0 + 6.6 + sp * t) % 1.7)
            sc.set_offsets([P(x, lane)])
            sc.set_sizes([70 * a])
    S.updaters.append(up)
    S.text(0.5, 0.82, "100,000+ VESSELS A YEAR", t0, size=64, color=AMBER, box=True, pop=True)
    S.text(0.5, 0.18, "THE MEDITERRANEAN'S ONLY NATURAL OPENING TO THE OCEAN", S.c("because"), S.c("Whatever"),
           size=34, box=True)
    S.text(0.5, 0.18, "HOW DEEP IS THE WATER?", S.c("So the first"), size=48, color=CYAN, box=True, pop=True)
    src(S, "Morocco World News, 10 Apr 2026", t0)


def s05_deep(S):
    depth_chart(S, [("CHANNEL TUNNEL", "deepest point", 115, GREEN, S.c("Channel Tunnel"), "≈ 115 m"),
                    ("SEIKAN TUNNEL", "Japan, track level", 240, VIOLET, S.c("Seikan"), "≈ 240 m"),
                    ("CAMARINAL SILL", "shallowest crossing", 290, CYAN, S.c("Camarinal Sill"), "≈ 280–300 m"),
                    ("THE NARROWS", "Gibraltar, deepest", 900, AMBER, S.c("nine hundred"), "≈ 900 m")],
                "PROBLEM 1: THE DEPTH", maxd=950)
    S.text(0.3, 0.45, "Shallower, but a much\nlonger crossing", S.c("That is the shallowest"), S.c("For comparison"),
           size=26, color=CYAN, box=True)
    src(S, "Wikipedia (Strait of Gibraltar, Channel Tunnel, Seikan Tunnel)", S.c("For comparison"))


def s06_bridge(S):
    local_map(S, [(0, *STRAIT), (S.T, *STRAIT)], dim=True)
    S.headline("THE BRIDGE IDEA: T. Y. LIN'S PROPOSAL", 0.3, size=42)
    S.bars([("1915 Çanakkale Bridge, Turkey (world record, 2022)", 2023, GREEN, S.c("nineteen fifteen")),
            ("Lin's proposed Gibraltar bridge", 5000, AMBER, S.c("five thousand"))],
           S.c("five thousand") - 0.3, rect=(0.1, 0.5, 0.62, 0.24), xmax=6200, unit="m", dec=0,
           title="MAIN SPAN (METRES)")
    S.bars([("Çanakkale towers", 334, GREEN, S.c("three hundred and thirty four")),
            ("Lin's proposed towers", 910, AMBER, S.c("nine hundred and ten"))],
           S.c("nine hundred and ten") - 0.3, rect=(0.1, 0.13, 0.62, 0.24), xmax=1130, unit="m", dec=0,
           title="TOWER HEIGHT (METRES)")
    S.text(0.86, 0.62, "≈ 2.5×\nTHE RECORD", S.c("two and a half"), size=46, color=AMBER, box=True, pop=True)
    S.text(0.86, 0.25, "ALMOST 3×\nAS TALL", S.c("almost three"), size=46, color=AMBER, box=True, pop=True)
    src(S, "Wikipedia (Strait of Gibraltar crossing; 1915 Çanakkale Bridge)", S.c("Today"))


def s07_currents(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(-9, 2)
    ax.add_patch(Rect((0, -4), 16, 4, color="#123a5e", zorder=1))
    ax.add_patch(Rect((0, -7.6), 16, 3.6, color="#0b2640", zorder=1))
    sea = np.array([[0, -9], [0, -8.2], [4, -7.4], [6.5, -7.0], [9, -7.3], [12, -7.8], [16, -8.4], [16, -9]])
    ax.add_patch(MPoly(sea, closed=True, color="#3a2f25", zorder=2))
    ax.plot([0, 16], [0, 0], color=CYAN, lw=3, zorder=3)
    S.text(0.08, 0.84, "WEST: ATLANTIC", 0.3, size=30, color=MUTED, ha="left")
    S.text(0.92, 0.84, "EAST: MEDITERRANEAN", 0.3, size=30, color=MUTED, ha="right")
    S.headline("TWO CURRENTS, STACKED", 0.2, size=44, y=0.93)
    t_top, t_bot = S.c("Fresher"), S.c("Underneath")
    rng = np.random.default_rng(3)
    top = [(rng.uniform(0, 16), rng.uniform(-3.5, -0.5)) for _ in range(40)]
    bot = [(rng.uniform(0, 16), rng.uniform(-7.0, -4.5)) for _ in range(40)]
    sc1 = ax.scatter([0], [0], s=0, color=CYAN, zorder=5, marker=">")
    sc2 = ax.scatter([0], [0], s=0, color=AMBER, zorder=5, marker="<")

    def up(t):
        a1, a2 = ease((t - t_top) / 0.6), ease((t - t_bot) / 0.6)
        sc1.set_offsets([((x + 1.2 * t) % 16, y) for x, y in top])
        sc1.set_sizes([110 * a1] * len(top))
        sc2.set_offsets([((x - 0.7 * t) % 16, y) for x, y in bot])
        sc2.set_sizes([110 * a2] * len(bot))
    S.updaters.append(up)
    S.text(0.5, 0.68, "SURFACE: FRESHER ATLANTIC WATER FLOWS EAST, IN", t_top, size=32, color=CYAN, box=True)
    S.text(0.5, 0.36, "DEEP: SALTIER MED WATER FLOWS WEST, OUT", t_bot, size=32, color=AMBER, box=True)
    S.caption("WHY: EVAPORATION > RIVERS + RAIN", S.c("This happens"), color=WHITE)
    src(S, "Schematic, not to scale. Wikipedia; Britannica", 0.5)
    S.brand()


def s08_quake(S):
    S.graticule(step=10)
    S.world()
    S.camera([(0, -12, mercy(37), 34), (S.T, -12, mercy(37), 32)])
    S.highlight(["Spain", "Portugal", "France"], CYAN, S.c("Eurasian"), peak=0.55)
    S.highlight(["Morocco", "Algeria"], AMBER, S.c("African Plate"), peak=0.55)
    S.text(0.3, 0.66, "EURASIAN PLATE", S.c("Eurasian"), size=32, color=CYAN, box=True)
    S.text(0.42, 0.24, "AFRICAN PLATE", S.c("African Plate"), size=32, color=AMBER, box=True)
    t_ar = S.c("slowly moving north")
    arr = FancyArrow(0, 0, 0, 0, width=0.6, color=AMBER, zorder=30, alpha=0)
    S.ax.add_patch(arr)
    a0 = P(-6.3, 32.8)

    def up(t):
        g = ease2((t - t_ar) / 1.0)
        arr.set_data(x=a0[0], y=a0[1], dx=0, dy=2.0 * g + 0.01, width=0.6, head_width=1.6, head_length=1.0)
        arr.set_alpha(ease((t - t_ar) / 0.3))
    S.updaters.append(up)
    fz = merc(np.array([[-27, 38.6], [-20, 37.6], [-14, 36.9], [-9.5, 36.3], [-5.6, 35.95]]))
    ln, = S.ax.plot([], [], color=RED, lw=4, ls=(0, (6, 4)), zorder=28)
    t_f = S.c("Azores")

    def up2(t):
        g = ease2((t - t_f) / 1.4)
        k = max(2, int(2 + g * (len(fz) - 2) + 0.999))
        d = fz[:k].copy()
        if g < 1:
            seg = g * (len(fz) - 1)
            i = min(int(seg), len(fz) - 2)
            d = np.vstack([fz[:i + 1], fz[i] + (fz[i + 1] - fz[i]) * (seg - i)])
        ln.set_data(d[:, 0], d[:, 1])
        ln.set_alpha(1 if t >= t_f else 0)
    S.updaters.append(up2)
    S.text(0.24, 0.47, "AZORES–GIBRALTAR FAULT ZONE\n(approximate line)", t_f, S.c("That is why"), size=24,
           color=RED, box=True)
    S.text(0.5, 0.1, "DEC 2025: SPAIN + MOROCCO AGREE A 3-YEAR STUDY:\nEARTHQUAKES, TSUNAMIS, SEABED MOVEMENT",
           S.c("That is why"), size=32, color=WHITE, box=True, pop=True)
    S.headline("PROBLEM 2: THE GROUND", 0.3, size=44)
    src(S, "Wikipedia; Morocco World News, 10 Apr 2026", S.c("That is why"))
    S.brand()


def s09_rock(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(-9, 2)
    ax.add_patch(Rect((0, -3), 16, 3, color="#123a5e", zorder=1))
    ax.plot([0, 16], [0, 0], color=CYAN, lw=3, zorder=3)
    floor = np.array([[0, -2.4], [3, -2.8], [6, -3.2], [10, -3.0], [13, -2.7], [16, -2.3]])
    ax.add_patch(MPoly(np.vstack([floor, [[16, -9], [0, -9]]]), closed=True, color="#5a4a3a", zorder=2))
    ax.add_patch(MPoly(np.vstack([floor, floor[::-1] + [0, -0.5]]), closed=True, color="#8a7a5a", zorder=3))
    for cx in (5.0, 10.2):
        ch = np.array([[cx - 1.3, -3.1], [cx - 0.8, -5.6], [cx, -6.3], [cx + 0.8, -5.6], [cx + 1.3, -3.1]])
        pc = MPoly(ch, closed=True, color="#b58a5a", zorder=4, alpha=0)
        ax.add_patch(pc)

        def up(t, pc=pc):
            pc.set_alpha(0.95 * ease((t - S.c("two deep")) / 0.6))
        S.updaters.append(up)
    tbm = Circle((0, -5.0), 0.45, color=AMBER, zorder=6, alpha=0)
    ax.add_patch(tbm)
    trail, = ax.plot([], [], color=AMBER, lw=10, alpha=0.5, zorder=5, solid_capstyle="butt")
    t_m = S.c("A tunnel boring")

    def upm(t):
        g = ease2((t - t_m) / 5.0)
        x = 0.4 + 15.0 * g
        tbm.center = (x, -5.0)
        tbm.set_alpha(ease((t - t_m) / 0.4))
        trail.set_data([0, x], [-5.0, -5.0])
        trail.set_alpha(0.5 * ease((t - t_m) / 0.4))
    S.updaters.append(upm)
    S.text(0.5, 0.88, "THE SEABED: CLAY-RICH FLYSCH UNDER YOUNGER SEDIMENTS", S.c("flysch"), S.c("Herrenknecht"),
           size=32, box=True)
    S.text(0.5, 0.2, "TWO DEEP ANCIENT CHANNELS FILLED WITH CLAY", S.c("two deep"), S.c("Herrenknecht"), size=34,
           color=AMBER, box=True, pop=True)
    S.text(0.5, 0.88, "JUNE 2025, HERRENKNECHT: TECHNICALLY POSSIBLE", S.c("Herrenknecht"), size=36, color=GREEN,
           box=True, pop=True)
    S.text(0.5, 0.2, "...BUT EXTREMELY COMPLEX", S.c("extremely complex"), size=44, color=AMBER, box=True, pop=True)
    src(S, "Schematic, not to scale. Wikipedia; Morocco World News (Nov 2025, Apr 2026)", 0.5)
    S.brand()


def s10_flood(S):
    tl_setup(S)
    tl = TL(S, fmt=lambda v: f"{-v:.1f}M yrs ago" if v < -0.05 else ("TODAY" if v < 0.05 else ""), nice=[1, 2, 5])
    tl.camera([(0, -5.6, 1.6), (S.c("Then, about"), -5.5, 1.4), (S.c("That flood"), -2.4, 9.0), (S.T, -2.4, 9.1)])
    tl.marker(-5.97, "ATLANTIC LINK CLOSES", S.c("About six"), sub="≈ 5.97M years ago", color=PINK, side=1, h=0.5,
              size=26)
    tl.span(-5.97, -5.33, 0.15, PINK, "The Mediterranean mostly dries up", S.c("The Mediterranean was"), dur=1.6)
    tl.marker(-5.33, "THE ZANCLEAN FLOOD", S.c("Then, about"), sub="≈ 5.33M years ago", color=CYAN, side=-1,
              h=0.42, size=26)
    S.text(0.5, 0.88, "≈ 90% REFILLED IN A FEW MONTHS TO 2 YEARS", S.c("ninety percent"), S.c("That flood"),
           size=38, color=CYAN, box=True, pop=True)
    S.text(0.5, 0.78, "FLOW ≈ 3× THE AMAZON RIVER", S.c("three times"), S.c("That flood"), size=38, color=AMBER,
           box=True, pop=True)
    S.text(0.5, 0.85, "THE FLOOD HELPED CARVE TODAY'S DEEP STRAIT", S.c("That flood"), size=40, color=WHITE,
           box=True, pop=True)
    src(S, "Garcia-Castellanos et al., Nature 2009 (via Phys.org); Wikipedia", S.c("Then, about"))


def s11_history(S):
    tl_setup(S)
    tl = TL(S, nice=[1, 2, 5])
    tl.camera([(0, 1962, 90), (S.c("Then, in"), 1980, 126), (S.T, 1980, 127)])
    tl.marker(1930, "TUNNEL PROPOSED", S.c("nineteen thirty"), sub="1930 (Spain)", color=CYAN, side=1, h=0.5,
              size=26)
    tl.marker(1979, "DECLARATION OF FEZ", S.c("nineteen seventy nine"), sub="1979: kings of Spain + Morocco",
              color=AMBER, side=-1, h=0.42, size=26)
    tl.marker(1981, "SECEGSA FOUNDED", S.c("SECEGSA"), sub="1981 (Spain); partner: SNED (Morocco)", color=GREEN,
              side=1, h=0.25, size=24)
    tl.span(1985, 2022, 0.42, VIOLET, "Studies come and go", S.c("Studies came"), dur=1.4)
    tl.marker(2023, "PLAN RELAUNCHED", S.c("Then, in"), sub="2023", color=PINK, side=-1, h=0.42, size=26)
    S.headline("A 100-YEAR-OLD DREAM", 0.3, size=44)
    src(S, "Wikipedia (Strait of Gibraltar crossing)", 0.6)


def s12_plan(S):
    local_map(S, [(0, *STRAIT), (S.c("The full rail"), -5.85, mercy(35.95), 1.1), (S.T, -5.85, mercy(35.95), 1.05)])
    S.headline("THE PLAN: A RAILWAY TUNNEL (NO CARS)", 0.3, S.c("The full rail"), size=42)
    dot(S, *PALOMA, "Punta Paloma", S.c("Punta Paloma"), dy=0.03, size=22, color=WHITE)
    dot(S, *MALABATA, "Punta Malabata (near Tangier)", S.c("Punta Malabata"), dy=-0.06, size=22, color=WHITE)
    a, b = P(*PALOMA), P(*MALABATA)
    ln, = S.ax.plot([], [], color=AMBER, lw=6, ls=(0, (3, 2)), zorder=24)
    t0 = S.c("Punta Malabata") + 0.3

    def up(t):
        g = ease2((t - t0) / 1.4)
        q = a + (b - a) * g
        ln.set_data([a[0], q[0]], [a[1], q[1]])
    S.updaters.append(up)
    rows = [("65 KM RAIL LINK", S.c("sixty five")), ("≈ 28 KM UNDER THE SEA", S.c("twenty eight")),
            ("2 TUBES + A SERVICE TUNNEL", S.c("two single")), ("CROSS PASSAGES EVERY 340 M", S.c("cross passages")),
            ("DEEPEST ≈ 475 M BELOW SEA LEVEL", S.c("four hundred and seventy five"))]
    for i, (s, t) in enumerate(rows):
        S.text(0.035, 0.8 - i * 0.1, s, t, size=32, color=AMBER if i == 4 else WHITE, box=True, ha="left")
    S.text(0.97, 0.1, "Route line approximate", S.c("Punta Malabata"), size=20, color=MUTED, ha="right", font=REG)
    src(S, "Morocco World News (22 Nov 2025; 10 Apr 2026)", S.c("sixty five"))


def s13_compare(S):
    depth_chart(S, [("CHANNEL TUNNEL", "50 km · 38 km undersea", 115, GREEN, S.c("The Channel Tunnel"), "≈ 115 m"),
                    ("SEIKAN TUNNEL", "54 km · 23 km undersea", 240, VIOLET, S.c("The Seikan"), "≈ 240 m"),
                    ("GIBRALTAR (PLAN)", "65 km · ≈ 28 km undersea", 475, AMBER, S.c("The Gibraltar link"),
                     "≈ 475 m")],
                "DEEPEST POINT BELOW SEA LEVEL", maxd=520)
    S.caption("ROUGHLY TWICE AS DEEP AS SEIKAN", S.c("roughly twice"), color=AMBER)
    src(S, "Wikipedia; Morocco World News", S.c("The Gibraltar link"))


def s14_cost(S):
    local_map(S, [(0, *STRAIT), (S.T, *STRAIT)], dim=True)
    S.headline("THE COST", 0.3, S.c("In March"), size=48)
    S.text(0.5, 0.66, "SPAIN'S SECTION ALONE: > €8.5 BILLION", S.c("eight and a half"), S.c("In March"), size=44,
           color=AMBER, box=True, pop=True)
    S.text(0.5, 0.48, "WHOLE PROJECT: €15–30 BILLION (ESTIMATES)", S.c("fifteen to thirty"), S.c("In March"),
           size=44, color=WHITE, box=True, pop=True)
    S.headline("THE STUDIES", S.c("In March"), size=48)
    S.text(0.5, 0.7, "MAR 2026: SPAIN APPROVES €1.73M FOR STUDIES", S.c("In March"), size=36, color=CYAN, box=True)
    S.text(0.5, 0.58, "NOV 2026: MOROCCO SETS ASIDE ≈ €11M FOR 2027 STUDIES", S.c("In November"), size=36,
           color=GREEN, box=True)
    S.text(0.5, 0.4, "NEXT: A TEST TUNNEL (EXPLORATORY GALLERY)", S.c("The next big"), size=38, color=WHITE,
           box=True, pop=True)
    S.text(0.5, 0.28, "DECISION ≈ 2027 · 6–9 YEARS TO BUILD", S.c("A decision"), size=38, color=AMBER, box=True,
           pop=True)
    src(S, "Morocco World News (Nov 2025, Apr 2026); Euro Weekly News (5 Nov 2026)", 0.5)


def s15_when(S):
    tl_setup(S)
    tl = TL(S, nice=[1, 2, 5])
    tl.camera([(0, 2031, 16), (S.T, 2032, 18)])
    tl.marker(2026, "TODAY", 0.3, sub="Nov 2026", color=WHITE, side=1, h=0.3, size=26)
    tl.marker(2030, "WORLD CUP: SPAIN, MOROCCO, PORTUGAL", S.c("World Cup"), sub="tunnel won't be ready", color=PINK,
              side=-1, h=0.42, size=24)
    tl.span(2035, 2040, 0.3, AMBER, "Earliest estimates: 2035–2040", S.c("twenty thirty five"), dur=1.2)
    S.text(0.5, 0.88, "NO FINAL DECISION TO BUILD YET", S.c("no final decision"), S.c("Politics"), size=44,
           color=AMBER, box=True, pop=True)
    S.text(0.5, 0.88, "A RAIL LINK FROM THE EU'S OUTER BORDER TO NORTH AFRICA", S.c("Politics"), size=34,
           color=CYAN, box=True, pop=True)
    src(S, "Morocco World News (Jan, Apr 2026); Euro Weekly News (5 Nov 2026)", S.c("World Cup"))


def s16_payoff(S):
    S.graticule(step=5)
    local_map(S, [(0, -5.0, mercy(35.6), 9.0), (S.T, -5.3, mercy(35.4), 10.5)])
    S.highlight(_D["Spain"], CYAN, 0.3, peak=0.35)
    S.highlight(_D["Morocco"], AMBER, 0.3, peak=0.35)
    route_es = [(-5.98, 37.39), (-6.29, 36.53), (-5.97, 36.27), PALOMA]          # Seville, Cádiz, Vejer area
    route_ma = [MALABATA, TANGIER, (-6.58, 34.26), (-6.84, 34.02), (-7.59, 33.57)]  # Tangier, Kenitra, Rabat, Casablanca
    t1, t2 = S.c("Spain's high"), S.c("Al Boraq")
    for pts, col, t0 in ((route_es, CYAN, t1), (route_ma, AMBER, t2)):
        xy = merc(np.array(pts))
        ln, = S.ax.plot([], [], color=col, lw=5, zorder=24)

        def up(t, xy=xy, ln=ln, t0=t0):
            g = ease2((t - t0) / 1.4)
            k = g * (len(xy) - 1)
            i = min(int(k), len(xy) - 2)
            d = np.vstack([xy[:i + 1], xy[i] + (xy[i + 1] - xy[i]) * (k - i)])
            ln.set_data(d[:, 0], d[:, 1])
        S.updaters.append(up)
    a, b = P(*PALOMA), P(*MALABATA)
    S.ax.plot([a[0], b[0]], [a[1], b[1]], color=WHITE, lw=5, ls=(0, (2, 1.5)), zorder=25)
    dot(S, -5.98, 37.39, "Seville", t1, size=22, dx=-0.75, dy=-0.12)
    dot(S, -7.59, 33.57, "Casablanca", t2 + 1.0, size=22, dy=0.12)
    dot(S, *TANGIER, "Tangier", t2, size=22, dx=-0.6, dy=-0.1)
    S.text(0.7, 0.6, "≈ 30 MINUTES\nBETWEEN CONTINENTS", S.c("about thirty"), size=44, color=GREEN, box=True,
           pop=True)
    S.text(0.75, 0.2, "AL BORAQ: AFRICA'S FIRST\nHIGH-SPEED RAILWAY", t2, size=28, color=AMBER, box=True)
    S.text(0.04, 0.06, "Lines schematic, cities approximate", t1, size=20, color=MUTED, ha="left", font=REG)


def s17_outro(S):
    local_map(S, [(0, *STRAIT), (S.T, -5.65, mercy(35.95), 1.9)], dim=True)
    rows = [("DEEP WATER", S.c("Deep water"), AMBER), ("A BUSY SHIPPING LANE", S.c("a busy"), WHITE),
            ("TWO CURRENTS", S.c("two currents"), CYAN), ("MOVING PLATES", S.c("moving plates"), PINK),
            ("BURIED CLAY CHANNELS", S.c("buried clay"), GREEN)]
    q = S.c("Would you")
    for i, (s, t, col) in enumerate(rows):
        S.text(0.5, 0.8 - i * 0.1, s, t, q, size=40, color=col, box=True, pop=True)
    S.text(0.5, 0.6, "TRAIN UNDER THE SEA", q, size=58, color=AMBER, box=True, pop=True)
    S.text(0.5, 0.48, "OR THE FERRY?", q + 1.2, size=58, color=CYAN, box=True, pop=True)
    S.text(0.5, 0.3, "TELL ME IN THE COMMENTS", S.c("Tell me"), size=36, box=True)
    S.text(0.5, 0.15, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=44, color=AMBER, box=True, pop=True)
    S.fade_in_out(0, 1.0)
