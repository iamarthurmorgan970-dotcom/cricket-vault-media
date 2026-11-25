"""022 Why Ships Don't Sail Around South America. Each function takes the Scene S; S.c("phrase") is when the narrator
says it. Routes, pins and the locks profile are schematic/approximate (labelled on screen)."""
from engine.core import *
from engine.core import Scene
from engine import geo
from engine.extras import dot, lat_line, RED
from engine.timeline import TL, setup as tl_setup
from matplotlib.patches import Rectangle as Rect, Polygon as MPoly

LOCAL = ["Chile", "Argentina", "Panama", "Colombia", "Costa Rica"]


def _load_10m():
    import json
    from shapely.geometry import shape
    d = json.load(open(f"{geo.DATA}/admin0_10m_ind.geojson"))
    out = {}
    for f in d["features"]:
        n = f["properties"]["ADMIN"]
        if n in LOCAL:
            out[n] = geo._rings(shape(f["geometry"]), 0.003)
    return out


_D = _load_10m()

# Approximate coordinates (lon, lat)
NY, SF = (-74.0, 40.7), (-122.4, 37.8)
COLON, PANAMA_CITY = (-79.90, 9.35), (-79.53, 8.97)
HORN = (-67.27, -55.98)
LIVINGSTON = (-60.5, -62.6)
PUNTA_ARENAS = (-70.91, -53.16)
FROWARD = (-71.30, -53.90)
SYDNEY = (151.2, -33.9)

ROUTE_HORN = [NY, (-68, 30), (-52, 12), (-34, -6), (-38, -24), (-54, -42), (-64, -54), (-67.3, -57.3), (-76, -56),
              (-80, -45), (-80, -25), (-90, -5), (-104, 10), (-117, 26), SF]
ROUTE_PANAMA = [NY, (-73, 30), (-76, 20), (-79.5, 12), COLON, PANAMA_CITY, (-80.5, 6), (-92, 10), (-108, 20),
                (-118, 30), SF]
ROUTE_MAG = [(-67.5, -52.3), (-69.4, -52.45), (-70.4, -52.85), (-70.85, -53.25), (-71.05, -53.7), (-71.35, -53.95),
             (-72.3, -53.65), (-73.3, -53.15), (-74.3, -52.75), (-75.3, -52.55)]

AMERICAS = (-84, -10, 225)
TIP = (-67.5, mercy(-54.5), 20)


def P(lon, lat):
    return merc(np.array([[lon, lat]]))[0]


def basemap(S, keys, dim=False, local=True):
    S.graticule(step=10)
    S.world(fc="#1d2d42" if dim else LAND, names=[n for n in COUNTRIES if not (local and n in LOCAL)])
    if local:
        for n in LOCAL:
            S.rings(_D[n], fc="#1d2d42" if dim else LAND, ec=EDGE, lw=0.8, z=2, alpha=1)
    S.camera(keys)
    S.brand()


def maplabel(S, lon, lat, s, t0, size=30, color=MUTED, t1=None):
    p = P(lon, lat)
    art = S.ax.text(p[0], p[1], s, fontproperties=BOLD, size=size, color=color, ha="center", va="center",
                    zorder=20, alpha=0)
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        art.set_alpha(min(ease((t - t0) / 0.5), ease((t1 - t) / 0.5)))
    S.updaters.append(up)
    return art


def route(S, pts, color, t0, dur=2.5, lw=5, t1=None, ls="-", z=24):
    xy = merc(np.array(pts, dtype=float))
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
    ln, = S.ax.plot([], [], color=color, lw=lw, zorder=z, ls=ls, solid_capstyle="round")
    head = S.ax.scatter([0], [0], s=0, color=color, edgecolors=WHITE, linewidths=1.5, zorder=z + 1)
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        g = ease2((t - t0) / dur)
        L = g * seg[-1]
        k = max(1, int(np.searchsorted(seg, L)))
        k = min(k, len(xy) - 1)
        f = (L - seg[k - 1]) / max(seg[k] - seg[k - 1], 1e-9)
        q = xy[k - 1] + (xy[k] - xy[k - 1]) * f
        d = np.vstack([xy[:k], q])
        a = min(ease((t - t0) / 0.3), ease((t1 - t) / 0.4))
        ln.set_data(d[:, 0], d[:, 1])
        ln.set_alpha(a)
        head.set_offsets([q])
        head.set_sizes([110 * a * (t >= t0)])
    S.updaters.append(up)


def gap_line(S, a, b, label, t0, color=AMBER, size=30, t1=None, off=(0, 0), lw=4):
    pa, pb = P(*a), P(*b)
    ln, = S.ax.plot([], [], color=color, lw=lw, zorder=25, solid_capstyle="round")
    m = (pa + pb) / 2
    lab = S.ax.text(m[0] + off[0], m[1] + off[1], label, fontproperties=BOLD, size=size, color=color, ha="center",
                    va="center", zorder=27, alpha=0, bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none",
                                                               alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a_ = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        g = ease2((t - t0) / 0.9)
        q = pa + (pb - pa) * g
        ln.set_data([pa[0], q[0]], [pa[1], q[1]])
        ln.set_alpha(a_)
        la = a_ * ease((t - t0 - 0.6) / 0.4)
        lab.set_alpha(la)
        lab.get_bbox_patch().set_alpha(0.8 * la)
    S.updaters.append(up)


def card(S, x, y, s, t0, t1=None, size=34, color=WHITE, ha="center"):
    return S.text(x, y, s, t0, t1, size=size, color=color, box=True, pop=True, ha=ha)


def src(S, s, t0, t1=None):
    S.text(0.015, 0.03, s, t0, t1, size=19, color=MUTED, ha="left", font=REG)


def flow(S, t0, lon0, lon1, lat0, lat1, n=45, speed=3.0, color=CYAN, size=60, marker=">", seed=4, t1=None):
    rng = np.random.default_rng(seed)
    pts = [(rng.uniform(lon0, lon1), rng.uniform(lat0, lat1)) for _ in range(n)]
    sc = S.ax.scatter([0], [0], s=0, color=color, zorder=22, marker=marker, alpha=0.85)
    span = lon1 - lon0
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.6), ease((t1 - t) / 0.5))
        sc.set_offsets([P(lon0 + ((x - lon0 + speed * t) % span), y) for x, y in pts])
        sc.set_sizes([size * a] * n)
    S.updaters.append(up)


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    basemap(S, [(0, *AMERICAS), (S.T, -84, -10, 215)])
    dot(S, *NY, "New York", 0.4, size=24, dx=6, dy=1.5, ha="left")
    dot(S, *SF, "San Francisco", 0.6, size=24, dx=-6, dy=1.5, ha="right")
    t_h, t_p = S.c("around the bottom"), S.c("Cut through")
    route(S, ROUTE_HORN, AMBER, t_h, dur=3.2)
    route(S, ROUTE_PANAMA, CYAN, t_p, dur=1.6)
    card(S, 0.78, 0.36, "AROUND SOUTH AMERICA\n≈ 13,000 MILES", S.c("thirteen thousand"), S.c("So why"), size=34,
         color=AMBER)
    card(S, 0.22, 0.62, "THROUGH PANAMA\n≈ 5,200 MILES", S.c("five thousand two"), S.c("So why"), size=34, color=CYAN)
    card(S, 0.78, 0.18, "THE LONG WAY: ≈ 2 MONTHS", S.c("two months"), S.c("So why"), size=30, color=WHITE)
    card(S, 0.5, 0.85, "TODAY: ALMOST NO CARGO SHIPS ROUND CAPE HORN", S.c("Today, almost"), S.c("So why"), size=36,
         color=WHITE)
    card(S, 0.5, 0.55, "WHY?", S.c("So why"), S.c("What makes"), size=110, color=AMBER)
    card(S, 0.5, 0.6, "THE CURRENT · THE WIND · THE WAVES", S.c("What makes"), size=38, color=PINK)
    card(S, 0.5, 0.45, "AND A SHORTCUT THAT RUNS ON RAIN", S.c("And what happens"), size=38, color=CYAN)
    src(S, "New York–San Francisco by sea: Britannica (approx.). Routes schematic.", S.c("thirteen thousand"))
    S.fade_in_out(0.6, 0)


def s02_title(S):
    basemap(S, [(0, -70, mercy(-30), 90), (S.T, -70, mercy(-35), 80)], dim=True)
    S.text(0.5, 0.6, "WHY SHIPS DON'T SAIL", 0.2, size=86, pop=True)
    S.text(0.5, 0.47, "AROUND SOUTH AMERICA", 0.5, size=80, color=AMBER, pop=True)
    S.text(0.5, 0.35, "Cape Horn, the Strait of Magellan and the Panama shortcut", 0.9, size=30, color=MUTED,
           font=REG)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=AMBER)


def s03_wall(S):
    t_z = S.c("only two")
    basemap(S, [(0, -85, mercy(15), 230), (S.c("Look at") + 1, -85, mercy(15), 230), (t_z, -85, mercy(5), 200),
                (t_z + 3.5, *TIP), (S.T, -67, mercy(-55), 19)])
    am = [n for n, c in CONT.items() if c in ("North America", "South America") and n not in LOCAL]
    S.highlight(am, AMBER, S.c("one long wall"), t_z + 1.5, peak=0.55)
    S.highlight([r for n in LOCAL for r in _D[n]], AMBER, S.c("one long wall"), t_z + 1.5, peak=0.55)
    card(S, 0.5, 0.88, "ONE WALL OF LAND, ARCTIC TO NEAR ANTARCTICA", S.c("one long wall"), t_z, size=38)
    card(S, 0.5, 0.88, "ONLY TWO NATURAL WAYS THROUGH", t_z, S.c("Strait of Magellan"), size=42, color=AMBER)
    card(S, 0.5, 0.12, "ONLY TWO NATURAL WAYS THROUGH", S.c("Strait of Magellan"), size=36, color=AMBER)
    route(S, ROUTE_MAG, GREEN, S.c("Strait of Magellan"), dur=1.4, lw=6)
    maplabel(S, -71.5, -52.2, "STRAIT OF MAGELLAN", S.c("Strait of Magellan"), size=26, color=GREEN)
    dot(S, *HORN, "Cape Horn", S.c("Cape Horn"), color=PINK, size=26, dy=-1.6)
    maplabel(S, -63, -59.3, "DRAKE PASSAGE", S.c("Drake Passage"), size=34, color=CYAN)
    maplabel(S, -61, -54.3, "ATLANTIC", t_z + 3.5, size=28, color=MUTED)
    maplabel(S, -75, -56.3, "PACIFIC", t_z + 3.5, size=28, color=MUTED)


def s04_horn(S):
    basemap(S, [(0, *TIP), (S.c("fifty six"), -67.3, mercy(-55.6), 7), (S.c("Two Dutch"), -67.3, mercy(-55.6), 7),
                (S.c("Atlantic meets"), -67.5, mercy(-55.5), 14), (S.T, -67.5, mercy(-55.5), 15)])
    dot(S, *HORN, "CAPE HORN", 0.4, color=PINK, size=30, dy=-0.55)
    lat_line(S, -56, S.c("fifty six"), MUTED, x0=-80, x1=-55, label="56° S", t1=S.c("Two Dutch"))
    card(S, 0.5, 0.87, "ON A SMALL ISLAND IN SOUTHERN CHILE", S.c("small island"), S.c("Surprisingly"), size=36)
    card(S, 0.5, 0.87, "NOT THE SOUTHERNMOST POINT OF SOUTH AMERICA", S.c("Surprisingly"), S.c("Two Dutch"), size=36,
         color=AMBER)
    card(S, 0.5, 0.87, "1616: SCHOUTEN AND LE MAIRE SAIL AROUND IT", S.c("Two Dutch"), S.c("Atlantic meets"),
         size=36, color=CYAN)
    card(S, 0.5, 0.2, "NAMED AFTER HOORN, THE NETHERLANDS", S.c("They named"), S.c("Atlantic meets"), size=34)
    maplabel(S, -63.2, -55.6, "ATLANTIC", S.c("Atlantic meets"), size=34, color=CYAN)
    maplabel(S, -72.5, -56.9, "PACIFIC", S.c("Pacific"), size=34, color=CYAN)
    card(S, 0.5, 0.87, "THE MOST FEARED CORNER OF THE SAILING WORLD", S.c("most feared"), size=38, color=PINK)
    src(S, "Wikipedia (Cape Horn)", 0.5)


def s05_drake(S):
    basemap(S, [(0, -65, mercy(-58), 34), (S.c("Antarctic Circumpolar"), -65, mercy(-58.5), 40), (S.T, -65,
                                                                                                     mercy(-58.5), 41)])
    maplabel(S, -57.5, -63.6, "ANTARCTICA", 0.5, size=30, color=WHITE)
    gap_line(S, HORN, LIVINGSTON, "≈ 800 KM", S.c("eight hundred"), color=AMBER, off=(4.5, 0), size=34)
    card(S, 0.5, 0.88, "DRAKE PASSAGE: AVG DEPTH ≈ 3,400 M", S.c("three thousand four"), S.c("Antarctic Circumpolar"),
         size=38, color=CYAN)
    flow(S, S.c("Antarctic Circumpolar"), -85, -45, -63.5, -56.8, n=60, speed=2.4)
    card(S, 0.5, 0.88, "THE ANTARCTIC CIRCUMPOLAR CURRENT", S.c("Antarctic Circumpolar"), S.c("Estimates put"),
         size=40, color=CYAN)
    S.bars([("Antarctic Circumpolar Current: low estimate", 100, CYAN, S.c("one hundred to")),
            ("Antarctic Circumpolar Current: high estimate", 150, CYAN, S.c("one hundred and fifty")),
            ("Gulf Stream, off Florida", 33, AMBER, S.c("Gulf Stream"))],
           S.c("Estimates put"), rect=(0.08, 0.56, 0.6, 0.3), xmax=190, unit="million m³/s", dec=0,
           title="WATER FLOW, MILLION CUBIC METRES PER SECOND")
    S.caption("WIDTH: ≈ 800 KM (WIKIPEDIA); BRITANNICA SAYS UP TO ≈ 1,000 KM", S.c("eight hundred") + 2.5,
              S.c("Antarctic Circumpolar"), size=28)
    src(S, "Britannica; Wikipedia (Drake Passage). Flow arrows schematic.", S.c("Estimates put"))


def s06_storms(S):
    basemap(S, [(0, *TIP), (S.c("In August"), -68, mercy(-48), 52), (S.T, -68, mercy(-48), 54)])
    flow(S, S.c("westerlies"), -90, -45, -60, -50, n=70, speed=6, color=WHITE, size=420, marker="_", seed=9)
    card(S, 0.5, 0.88, "THE WESTERLIES, SQUEEZED BETWEEN THE ANDES AND ANTARCTICA", S.c("westerlies"),
         S.c("In winter"), size=32)
    card(S, 0.5, 0.88, "WINTER: GALES UP TO 30% OF THE TIME", S.c("In winter"), S.c("In August"), size=40,
         color=AMBER)
    card(S, 0.27, 0.22, "DRAKE PASSAGE\nWAVES OFTEN > 12 M", S.c("twelve metres"), S.c("In August"), size=34,
         color=CYAN)
    card(S, 0.73, 0.22, "ROGUE WAVES\nUP TO 30 M", S.c("rogue waves"), S.c("In August"), size=34, color=PINK)
    card(S, 0.5, 0.62, "SHALLOWER SEA FLOOR = SHORTER, STEEPER WAVES", S.c("sea floor rises"), S.c("In August"),
         size=32)
    lat_line(S, -40, S.c("In August"), CYAN, x0=-110, x1=-20, label="40° S")
    card(S, 0.5, 0.68, "AUGUST: ICEBERGS CAN DRIFT NORTH OF 40° S", S.c("In August"), size=38, color=CYAN)
    src(S, "Wikipedia (Cape Horn; Drake Passage). Wind streaks schematic.", S.c("In winter"))


def s07_bounty(S):
    basemap(S, [(0, -68, mercy(-56), 22), (S.T, -68, mercy(-56), 20)], dim=True)
    dot(S, *HORN, "Cape Horn", 0.3, color=PINK, size=24, dy=-1.2)
    card(S, 0.5, 0.86, "1788: THE BRITISH SHIP BOUNTY HEADS WEST", S.c("seventeen eighty"), S.c("gave up"), size=40)
    route(S, [(-62, -57.2), (-66, -57.6), (-64.5, -57.8), (-67.5, -58.0), (-65.5, -57.9), (-66.8, -58.1)], AMBER,
          S.c("tried to sail"), dur=4.0, lw=4)
    S.bars([("Days spent trying", 31, AMBER, S.c("thirty one days")),
            ("Miles of headway made", 85, CYAN, S.c("eighty five"))],
           S.c("thirty one days"), rect=(0.06, 0.55, 0.36, 0.18), xmax=120, unit="", dec=0)
    card(S, 0.5, 0.86, "≈ 2.7 MILES OF PROGRESS A DAY · THEN IT TURNED BACK", S.c("gave up"), S.c("Many ships"), size=34, color=AMBER)
    card(S, 0.5, 0.86, "MANY SHIPS WRECKED, MANY SAILORS LOST", S.c("Many ships"), size=38, color=PINK)
    src(S, "Wikipedia (Cape Horn). Track schematic.", S.c("thirty one days"))


def s08_clippers(S):
    tl_setup(S)
    tl = TL(S, nice=[1, 2, 5])
    tl.camera([(0, 1850, 340), (S.c("The last"), 1880, 220), (S.T, 1885, 210)])
    tl.span(1700, 1914, 0.15, AMBER, "Clipper routes: Australia to Europe via Cape Horn", S.c("eighteenth"), dur=1.6)
    tl.marker(1914, "PANAMA CANAL OPENS", S.c("eighteenth") + 2.0, sub="Aug 1914", color=CYAN, side=-1, h=0.42,
              size=26)
    tl.marker(1949, "PAMIR: LAST CARGO SAILING SHIP", S.c("The last"), sub="grain, Australia to England",
              color=PINK, side=1, h=0.5, size=26)
    S.text(0.5, 0.88, "WOOL · GRAIN · GOLD", S.c("wool"), S.c("A sailor"), size=50, color=AMBER, box=True, pop=True)
    S.text(0.5, 0.88, "SURVIVE IT: A GOLD EARRING IN THE LEFT EAR", S.c("A sailor"), S.c("The last"), size=40,
           color=GREEN, box=True, pop=True)
    S.headline("FOR CENTURIES, NO OTHER CHOICE", 0.3, S.c("wool"), size=44)
    src(S, "Wikipedia (Cape Horn)", 0.5)


def s09_magellan(S):
    basemap(S, [(0, -71, mercy(-53.2), 14), (S.c("five hundred and seventy"), -71, mercy(-53.2), 11),
                (S.c("narrowest point"), -71.3, mercy(-53.9), 3.0), (S.c("It twists"), -71.3, mercy(-53.9), 3.2),
                (S.c("Today, ships"), -71, mercy(-53.2), 9), (S.T, -71, mercy(-53.2), 9)])
    route(S, ROUTE_MAG, GREEN, S.c("Ferdinand"), dur=3.0, lw=6)
    card(S, 0.5, 0.88, "1520: MAGELLAN · 38 DAYS TO GET THROUGH", S.c("Ferdinand"), S.c("five hundred and seventy"),
         size=40, color=GREEN)
    card(S, 0.5, 0.88, "≈ 570 KM LONG", S.c("five hundred and seventy"), S.c("narrowest point"), size=48)
    card(S, 0.5, 0.88, "≈ 2 KM WIDE AT ITS NARROWEST", S.c("narrowest point"), S.c("It twists"), size=46,
         color=AMBER)
    dot(S, *FROWARD, "near Cape Froward", S.c("narrowest point"), size=22, dy=-0.25, t1=S.c("Today, ships"))
    card(S, 0.5, 0.18, "NARROWS · SHIFTING WINDS · STRONG CURRENTS", S.c("It twists"), S.c("Today, ships"), size=34,
         color=PINK)
    card(S, 0.5, 0.88, "TODAY: A LOCAL PILOT IS COMPULSORY", S.c("Today, ships"), size=40, color=CYAN)
    dot(S, *PUNTA_ARENAS, "Punta Arenas (founded 1848)", S.c("Punta Arenas"), size=24, dy=0.35, color=WHITE)
    src(S, "Wikipedia; Britannica (Strait of Magellan). Line approximate.", S.c("five hundred and seventy"))


def s10_dig(S):
    basemap(S, [(0, -80, mercy(9), 40), (S.c("Panama is"), -79.7, mercy(9.1), 3.4), (S.T, -79.7, mercy(9.15), 3.0)])
    S.highlight(_D["Panama"], CYAN, S.c("Panama is"), peak=0.35)
    gap_line(S, COLON, PANAMA_CITY, "", S.c("thinnest"), color=AMBER, lw=7)
    dot(S, *COLON, "Colón (Atlantic)", S.c("thinnest"), size=22, dy=0.08, color=WHITE)
    dot(S, *PANAMA_CITY, "Panama City (Pacific)", S.c("thinnest"), size=22, dy=-0.2, color=WHITE)
    rows = [("1881: FRANCE STARTS DIGGING", S.c("eighteen eighty one"), WHITE),
            ("1904: THE UNITED STATES TAKES OVER", S.c("nineteen oh four"), WHITE),
            ("≈ 25,600 WORKERS DIED (BRITANNICA)", S.c("twenty five thousand"), PINK),
            ("15 AUG 1914: SS ANCON, FIRST CROSSING", S.c("fifteenth of August"), GREEN)]
    for i, (s, t, col) in enumerate(rows):
        S.text(0.965, 0.86 - i * 0.1, s, t, size=32, color=col, box=True, ha="right")
    S.text(0.965, 0.43, "malaria and yellow fever", S.c("malaria"), size=26, color=WHITE, ha="right", font=REG, box=True)
    src(S, "Britannica (Panama Canal timeline). Line approximate.", S.c("eighteen eighty one"))


def s11_locks(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(-14, 40)
    ax.add_patch(Rect((0, -14), 16, 14, color="#0e2a47", zorder=0))
    ax.plot([0, 16], [0, 0], color=CYAN, lw=2, zorder=1)
    prof = np.array([[0, 0], [2.0, 0], [2.0, 8.7], [2.6, 8.7], [2.6, 17.3], [3.2, 17.3], [3.2, 26], [11.6, 26],
                     [11.6, 16], [12.6, 16], [12.6, 8], [13.2, 8], [13.2, 0], [16, 0]])
    ground = np.vstack([[[0, -14]], prof + [0, -1.2], [[16, -14]]])
    ax.add_patch(MPoly(ground, closed=True, color="#3a2f25", zorder=1))
    water = MPoly(np.vstack([prof, [[16, -0.01], [0, -0.01]]]), closed=True, color="#1d5d8a", zorder=2)
    ax.add_patch(water)
    ax.text(0.3, 1.0, "ATLANTIC", fontproperties=BOLD, size=24, color=CYAN, va="bottom")
    ax.text(15.7, 1.0, "PACIFIC", fontproperties=BOLD, size=24, color=CYAN, va="bottom", ha="right")
    ax.text(7.4, 27.2, "GATUN LAKE (ARTIFICIAL, RAIN-FED)", fontproperties=BOLD, size=24, color=WHITE, ha="center",
            va="bottom")
    ax.text(2.6, -3.5, "GATUN\n3 steps", fontproperties=BOLD, size=22, color=AMBER, ha="center", va="top")
    ax.text(11.6, 12.5, "PEDRO\nMIGUEL", fontproperties=BOLD, size=20, color=AMBER, ha="center", va="top")
    ax.text(12.9, -3.5, "MIRAFLORES\n2 steps", fontproperties=BOLD, size=22, color=AMBER, ha="center", va="top")
    ship = Rect((0, 0), 0.55, 1.6, color=WHITE, zorder=5, alpha=0)
    ax.add_patch(ship)
    path = np.array([[0.3, 0], [1.6, 0], [2.05, 8.7], [2.65, 17.3], [3.3, 26], [11.1, 26], [11.7, 16], [12.7, 8],
                     [13.3, 0], [15.2, 0]])
    t0, t1 = S.c("Ships climb"), S.c("The water that")

    def up(t):
        g = ease2((t - t0) / max(t1 - t0, 1))
        k = g * (len(path) - 1)
        i = min(int(k), len(path) - 2)
        q = path[i] + (path[i + 1] - path[i]) * (k - i)
        ship.set_xy((q[0] - 0.27, q[1]))
        ship.set_alpha(ease((t - t0 + 0.5) / 0.5))
    S.updaters.append(up)
    S.headline("≈ 82 KM, DEEP WATER TO DEEP WATER", 0.3, S.c("But it does"), size=42)
    S.headline("SHIPS CLIMB OVER THE COUNTRY", S.c("But it does"), S.c("three steps"), size=46, color=AMBER)
    S.headline("GATUN LOCKS: UP 26 METRES", S.c("three steps"), S.c("The water that"), size=46, color=AMBER)
    S.headline("≈ 197 MILLION LITRES OF FRESH WATER PER SHIP", S.c("The older locks"), S.c("The crossing"),
               size=40, color=CYAN)
    S.headline("THE CROSSING: ≈ 8–10 HOURS", S.c("The crossing"), size=46, color=GREEN)
    src(S, "Britannica (Panama Canal; locks). Profile schematic, not to scale.", 0.5)
    S.brand()


def s12_distance(S):
    basemap(S, [(0, *AMERICAS), (S.T, -82, mercy(3), 186)], dim=True)
    route(S, ROUTE_HORN, AMBER, S.c("around South America"), dur=2.5, lw=4)
    route(S, ROUTE_PANAMA, CYAN, S.c("Through Panama"), dur=1.4, lw=4)
    S.bars([("Around South America", 13000, AMBER, S.c("about thirteen")),
            ("Through the Panama Canal", 5200, CYAN, S.c("about five thousand"))],
           S.c("about thirteen") - 0.2, rect=(0.38, 0.55, 0.5, 0.26), xmax=17000, unit="miles", dec=0,
           title="NEW YORK TO SAN FRANCISCO BY SEA (APPROX.)")
    card(S, 0.63, 0.42, "≈ 21,000 KM vs ≈ 8,400 KM: LESS THAN HALF", S.c("less than half"), size=32, color=WHITE)
    card(S, 0.63, 0.3, "SAILING SHIP AROUND THE HORN: ≈ 2 MONTHS", S.c("two months"), size=30, color=AMBER)
    card(S, 0.63, 0.19, "CROSSING PANAMA: ≈ 1 DAY WITH WAITING", S.c("about a day"), size=30, color=CYAN)
    src(S, "Britannica (miles; km converted). Routes schematic.", S.c("about thirteen"))


def s13_bigger(S):
    ax = S.ax
    ax.set_xlim(-30, 420)
    h = 450 * H / W
    ax.set_ylim(-h / 2, h / 2)
    box = Rect((0, -25.6), 370.3, 51.25, fc="none", ec=AMBER, lw=3, ls=(0, (6, 4)), zorder=3, alpha=0)
    ax.add_patch(box)
    hull = np.array([[1, -24.1], [330, -24.1], [366, 0], [330, 24.1], [1, 24.1]])
    ship = MPoly(hull, closed=True, fc=CYAN, ec=WHITE, lw=2, zorder=4, alpha=0)
    ax.add_patch(ship)
    tb, ts = S.c("three hundred and seventy"), S.c("A ship the size")

    def up(t):
        box.set_alpha(ease((t - tb) / 0.5))
        ship.set_alpha(0.85 * ease((t - ts) / 0.6))
    S.updaters.append(up)
    S.headline("2016: A THIRD, BIGGER SET OF LOCKS", 0.3, S.c("three hundred and seventy"), size=44)
    S.text(0.5, 0.78, "MAX SHIP: ≈ 370 M LONG · 51.25 M WIDE · 15.24 M DRAFT", tb, size=36, color=AMBER, box=True)
    S.text(0.5, 0.25, "2021: ≈ 97% OF THE WORLD'S CONTAINER SHIPS FIT", S.c("twenty twenty one"), ts, size=36,
           color=WHITE, box=True, pop=True)
    S.text(0.5, 0.25, "CMA CGM THEODORE ROOSEVELT: ≈ 366 M × 48 M · ≈ 14,855 TEU", ts, size=32, color=CYAN, box=True,
           pop=True)
    S.text(0.5, 0.67, "Top view, drawn to scale: ship vs the largest allowed", tb + 1, size=24, color=MUTED, font=REG)
    src(S, "Panama Canal Authority (2021); gCaptain (2018). Hull outline simplified.", tb)
    S.brand()


def s14_drought(S):
    basemap(S, [(0, -79.7, mercy(9.15), 3.0), (S.T, -79.7, mercy(9.15), 2.6)], dim=True)
    S.headline("THE WEAK SPOT: RAIN", 0.3, S.c("Normally"), size=50, color=CYAN)
    S.headline("2023: DROUGHT IN PANAMA", S.c("Normally"), S.c("Some ships"), size=44, color=AMBER)
    S.bars([("Normal (pre-drought)", 36, GREEN, S.c("thirty six")),
            ("Cut to (Dec 2023)", 22, AMBER, S.c("twenty two")),
            ("Planned low (Feb 2024)", 18, PINK, S.c("as low as"))],
           S.c("thirty six") - 0.2, rect=(0.12, 0.42, 0.5, 0.32), xmax=46, unit="ships a day", dec=0,
           title="DAILY CROSSINGS", t1=S.c("In October"))
    card(S, 0.82, 0.62, "WAITS UP TO\n3 WEEKS", S.c("Some ships"), S.c("In October"), size=34, color=WHITE)
    card(S, 0.82, 0.42, "$1 MILLION+\nFOR ONE SLOT", S.c("million dollars"), S.c("In October"), size=34, color=AMBER)
    S.bars([("US grain ships to Asia, Oct 2022", 34, GREEN, S.c("compared with")),
            ("US grain ships to Asia, Oct 2023", 5, PINK, S.c("only five"))],
           S.c("only five") - 0.2, rect=(0.12, 0.5, 0.5, 0.22), xmax=44, unit="ships", dec=0, t1=S.c("Analysts"))
    card(S, 0.5, 0.25, "THE LONG WAY: SUEZ, OR AROUND AFRICA", S.c("Others went"), S.c("Analysts"), size=36,
         color=CYAN)
    card(S, 0.5, 0.6, "MCKINSEY: ≈ 1,000 CROSSINGS A YEAR\nCOULD SWITCH TO MAGELLAN", S.c("Analysts"), size=38,
         color=GREEN)
    src(S, "MercoPress (13 Dec 2023); FreightWaves (Jan 2024); McKinsey (Jan 2024)", S.c("Normally"))


def s15_today(S):
    basemap(S, [(0, -79.7, mercy(9.15), 2.6), (S.T, -79.7, mercy(9.15), 3.2)], dim=True)
    S.headline("FISCAL YEAR 2026 (OCT 2025 – SEP 2026)", 0.3, S.c("And on the ninth"), size=40, color=GREEN)
    rows = [("13,951 TRANSITS · UP ≈ 4%", S.c("thirteen thousand"), WHITE),
            ("521 MILLION TONS: A NEW RECORD", S.c("five hundred and twenty one"), AMBER)]
    for i, (s, t, col) in enumerate(rows):
        S.text(0.5, 0.66 - i * 0.12, s, t, S.c("And on the ninth"), size=40, color=col, box=True, pop=True)
    S.headline("9 NOV 2026", S.c("And on the ninth"), size=46, color=CYAN)
    S.text(0.5, 0.66, "34 DAILY SLOTS · FULL 50-FOOT (15.24 M) DRAFT", S.c("thirty four"), size=38, color=WHITE,
           box=True, pop=True)
    S.text(0.5, 0.4, "SHARE OF WORLD SEA TRADE: ≈ 2.5–5%\n(estimates differ)", S.c("Estimates of"), size=36,
           color=AMBER, box=True, pop=True)
    src(S, "Seatrade; Maritime Executive (21 Oct 2026); Marine Insight (12 Nov 2026); McKinsey; MercoPress",
        S.c("thirteen thousand"))


def s16_who(S):
    basemap(S, [(0, *TIP), (S.T, -67.5, mercy(-55.5), 16)])
    dot(S, *HORN, "Cape Horn", 0.3, color=PINK, size=26, dy=-1.0)
    rows = [("NO REGULAR CARGO ROUTES", S.c("no regular"), WHITE),
            ("CRUISE SHIPS, ON PURPOSE", S.c("cruise ships"), CYAN),
            ("OCEAN RACERS: VENDÉE GLOBE", S.c("Ocean racers"), GREEN),
            ("THE BACKUP ROUTE", S.c("still the backup"), AMBER)]
    for i, (s, t, col) in enumerate(rows):
        S.text(0.04, 0.84 - i * 0.1, s, t, size=36, color=col, box=True, ha="left")
    S.text(0.96, 0.84, "for ships too big for Panama,\nor the next time the rain fails", S.c("ships too big"),
           size=28, color=WHITE, ha="right", font=REG, box=True)
    route(S, [(-60, -54.5), (-64, -56.6), (-67.3, -57.0), (-71, -56.8), (-75, -55.6)], WHITE, S.c("cruise ships"),
          dur=3, lw=3, ls=(0, (3, 2)))
    src(S, "Wikipedia (Cape Horn). Track schematic.", S.c("no regular"))


def s17_outro(S):
    basemap(S, [(0, -72, mercy(-20), 120), (S.T, -72, mercy(-20), 112)], dim=True)
    rows = [("THE CURRENT", S.c("the current"), CYAN), ("THE WIND", S.c("the wind"), WHITE),
            ("THE WAVES", S.c("the waves"), PINK), ("THE ICE", S.c("the ice"), CYAN),
            ("AN 82 KM SHORTCUT", S.c("eighty two"), AMBER)]
    q = S.c("Would you")
    for i, (s, t, col) in enumerate(rows):
        S.text(0.5, 0.82 - i * 0.1, s, t, q, size=40, color=col, box=True, pop=True)
    S.text(0.5, 0.62, "ROUND CAPE HORN FOR THE EARRING", q, size=52, color=AMBER, box=True, pop=True)
    S.text(0.5, 0.5, "OR TAKE THE PANAMA SHORTCUT?", q + 1.5, size=52, color=CYAN, box=True, pop=True)
    S.text(0.5, 0.32, "TELL ME IN THE COMMENTS", S.c("Tell me"), size=36, box=True)
    S.text(0.5, 0.17, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=44, color=AMBER, box=True, pop=True)
    S.fade_in_out(0, 1.0)
