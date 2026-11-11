"""012 Why Nobody Lives in Greenland. Each function takes the Scene S; S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.core import Scene
from engine.extras import dot
from engine.india import INDIA_POV
from engine.timeline import TL, setup as tl_setup
from shapely.geometry import Polygon as SPoly

GL = COUNTRIES["Greenland"]
NOT_INDIA = [n for n in COUNTRIES if n != "India"]
K = np.cos(np.radians(71))


def gl(a):
    """Simple local projection for Greenland close-ups (x squeezed by cos 71°), north up."""
    return np.column_stack([(a[:, 0] + 42) * K, a[:, 1]])


def inv_gl(p):
    return np.column_stack([p[:, 0] / K - 42, p[:, 1]])


GL_VIEW = (0.4, 71.6, 46)            # cx, cy, width in gl units

# Map pins (approximate coordinates)
TOWNS = {"Nuuk": (-51.72, 64.18), "Sisimiut": (-53.67, 66.94), "Ilulissat": (-51.10, 69.22),
         "Qaqortoq": (-46.04, 60.72), "Tasiilaq": (-37.64, 65.61), "Upernavik": (-56.15, 72.79),
         "Aasiaat": (-52.87, 68.71), "Ittoqqortoormiit": (-21.97, 70.49)}
PITUFFIK = (-68.70, 76.53)


def _ice_schematic():
    """Mainland Greenland shrunk inward until it covers ~80% of the mainland: a simplified ice sheet."""
    main = max(GL, key=lambda r: SPoly(gl(r)).area)
    P = SPoly(gl(main)).buffer(0)
    lo, hi = 0.0, 3.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if P.buffer(-mid).area > 0.8 * P.area:
            lo = mid
        else:
            hi = mid
    Q = P.buffer(-lo).simplify(0.05)
    polys = Q.geoms if hasattr(Q, "geoms") else [Q]
    return [np.asarray(p.exterior.coords) for p in polys if p.area > 0.05]


ICE = _ice_schematic()


def glmap(S, keys=None, ice_t=None, ice_alpha=0.9, dim=False):
    S.world(proj=gl, fc="#1d2d42" if dim else LAND)
    S.rings(GL, proj=gl, fc="#33506f" if not dim else "#24364d", ec="#6d8fb8", lw=1.2, z=3, alpha=1)
    if ice_t is not None:
        pc = PolyCollection(ICE, facecolors="#e8f4ff", edgecolors="#ffffff", linewidths=0.8, zorder=4, alpha=0)
        S.ax.add_collection(pc)

        def up(t):
            pc.set_alpha(ice_alpha * ease((t - ice_t) / 0.8))
        S.updaters.append(up)
    S.camera(keys or [(0, *GL_VIEW), (S.T, *GL_VIEW)])
    S.brand()


def town(S, name, t0, color=WHITE, size=24, dx=0, dy=0.35, ha="center", t1=None):
    lon, lat = TOWNS[name] if name in TOWNS else name
    return dot(S, lon, lat, name if name in TOWNS else "", t0, color=color, proj=gl, dx=dx, dy=dy, size=size,
               ha=ha, t1=t1)


def india_eq(S, t0, peak=0.9, proj=equal_earth):
    S.rings(INDIA_POV, proj=proj, fc=LAND, ec=EDGE, lw=0.5, z=1.5, alpha=1)
    S.highlight(INDIA_POV, PINK, t0, proj=proj, peak=peak, z=4.5)


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    S.graticule(proj=equal_earth, step=20)
    S.world(proj=equal_earth, names=NOT_INDIA)
    india_eq(S, S.c("India"))
    S.highlight(GL, CYAN, 0.4, proj=equal_earth, pulse=True, z=4.6)
    S.camera([(0, 10, 50, 270), (S.c("India") - 0.3, 24, 53, 178), (S.T, 24, 53, 172)])
    S.text(0.5, 0.5, "GREENLAND ≈ 2/3 THE SIZE OF INDIA", S.c("two thirds"), S.c("You could fit"), size=46,
           box=True, pop=True)
    S.text(0.5, 0.12, "POPULATION: 56,740", S.c("Fifty six"), S.c("You could fit"), size=54, color=CYAN, box=True,
           pop=True)
    S.bars([("Seats in Narendra Modi Stadium, Ahmedabad", 132000, AMBER, S.c("You could fit")),
            ("Everyone in Greenland (1 Jan 2026)", 56740, CYAN, S.c("You could fit") + 1.0)],
           S.c("You could fit") - 0.2, rect=(0.12, 0.3, 0.7, 0.32), xmax=165000, unit="", dec=0,
           t1=S.c("So why"))
    S.text(0.5, 0.5, "WHY IS IT SO EMPTY?", S.c("So why"), size=78, color=AMBER, box=True, pop=True)
    S.fade_in_out(0.6, 0)
    S.brand()


def s02_title(S):
    glmap(S, [(0, 0.4, 71.6, 52), (S.T, 0.4, 71.6, 46)], ice_t=0.0, ice_alpha=0.35, dim=True)
    S.text(0.5, 0.58, "WHY NOBODY LIVES", 0.3, size=96, pop=True)
    S.text(0.5, 0.45, "IN GREENLAND", 0.7, size=96, color=CYAN, pop=True)
    S.text(0.5, 0.33, "The world's biggest island, at its true scale", 1.2, size=30, color=MUTED, font=REG)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=AMBER)


def s03_news(S):
    S.graticule()
    S.world()
    S.camera([(0, -40, mercy(62), 150), (S.c("Pituffik"), -50, mercy(70), 110), (S.T, -48, mercy(69), 115)])
    S.highlight(GL, CYAN, 0.3, pulse=True)
    S.highlight(["United States of America"], AMBER, S.c("United States"), peak=0.7)
    S.highlight(["Denmark"], PINK, S.c("Denmark"), peak=0.95)
    S.headline("3 NOV 2026: GREENLAND APPROVES SECURITY DEAL", S.c("On the third"), size=40, y=0.08)
    S.text(0.5, 0.2, "16 FOR  ·  0 AGAINST  ·  7 ABSTAINED", S.c("Sixteen"), S.c("The deal lets"), size=40,
           color=GREEN, box=True, pop=True)
    dot(S, *PITUFFIK, "PITUFFIK SPACE BASE", S.c("Pituffik"), color=AMBER, dy=1.5, size=26)
    S.text(0.5, 0.2, "Next: Denmark's parliament debates it this month", S.c("Denmark's parliament"),
           S.c("To understand"), size=34, box=True)
    S.text(0.04, 0.2, "Source: Al Jazeera, 3 Nov 2026", S.c("To understand"), size=22, color=MUTED, ha="left", box=True)
    S.brand()


def s04_size(S):
    S.graticule()
    S.world(names=NOT_INDIA)
    S.rings(INDIA_POV, fc=LAND, ec=EDGE, lw=0.5, z=1.5, alpha=1)
    t_fair = S.c("On a fair map")
    S.camera([(0, 0, mercy(45), 330), (t_fair, 10, mercy(42), 300), (S.c("India is about"), 35, mercy(40), 190),
              (S.T, 35, mercy(38), 185)])
    S.highlight(GL, CYAN, 0.3, t_fair + 0.2, pulse=True)
    S.headline("ON A MERCATOR MAP, GREENLAND LOOKS GIANT", 0.4, t_fair, size=40)
    S.mover(GL, (-41, 72), (58, 14), t_fair, t_fair + 3.0, label="GREENLAND", ghost=True)
    S.highlight(INDIA_POV, PINK, S.c("India is about"), peak=0.9, z=4.5)
    S.bars([("India", 3.29, PINK, S.c("India is about")), ("Greenland", 2.17, CYAN, S.c("about two point"))],
           S.c("about two point") - 0.2, rect=(0.14, 0.64, 0.28, 0.17), xmax=4.6, dec=2, label_left=True)
    S.text(0.5, 0.1, "≈ 1 PERSON PER 38 km²", S.c("That works out"), size=50, color=AMBER, box=True, pop=True)
    S.brand()


def s05_ice(S):
    glmap(S, [(0, *GL_VIEW), (S.T, 4, 71.6, 52)], ice_t=S.c("buried"))
    S.headline("≈ 80% UNDER ONE SHEET OF ICE", S.c("About eighty"), size=44)
    S.bars([("Greenland's area", [(1.71, "#e8f4ff"), (0.46, GREEN)], None, S.c("covers roughly"))],
           S.c("covers roughly") - 0.2, rect=(0.58, 0.16, 0.36, 0.1), xmax=2.6, dec=2)
    S.text(0.76, 0.33, "ICE ≈ 1.71M km²", S.c("covers roughly"), size=30, color=WHITE, box=True)
    S.text(0.76, 0.06, "ICE-FREE ≈ 0.46M km²", S.c("Take that away"), size=30, color=GREEN, box=True)
    S.text(0.04, 0.06, "Ice outline simplified", 1.0, size=18, color=MUTED, font=REG, ha="left")
    S.brand()


def s06_thick(S):
    from engine.extras import peaks_chart
    peaks_chart(S, [("ICE SHEET", "at its thickest (3,000+ m)", 3.0, "#cfe8ff", "more than three"),
                    ("GUNNBJORN FJELD", "highest mountain", 3.694, AMBER, "Gunnbjorn")],
                "ICE ALMOST AS TALL AS THE HIGHEST PEAK", subtitle="Metres", ymax_km=5.5, width=12,
                captions=[])
    S.text(0.5, 0.76, "No towns, no soil, nothing to build on", S.c("There are no towns"), size=36, color=CYAN, box=True)
    S.brand()


def s07_volume(S):
    glmap(S, ice_t=0.0, dim=True)
    S.headline("≈ 2.9 MILLION km³ OF ICE", 0.4, size=46)
    S.bars([("Greenland ice sheet", 7.4, CYAN, S.c("seven point four")),
            ("Antarctic ice sheet", 58, VIOLET, S.c("fifty eight"))],
           S.c("If all of it") - 0.2, rect=(0.3, 0.2, 0.42, 0.26), xmax=75, unit="m", dec=1,
           title="Sea-level rise if it all melted (NSIDC)")
    S.brand()


def s08_cold(S):
    glmap(S, [(0, *GL_VIEW), (S.c("Nuuk"), -2.2, 65.5, 26), (S.T, -2.2, 65.3, 25)], ice_t=0.0)
    town(S, "Nuuk", S.c("Nuuk"), color=AMBER, size=30)
    S.headline("REASON 2: THE COLD", 0.3)
    S.text(0.7, 0.62, "NUUK, JULY AVERAGE ≈ 7 °C", S.c("averages only"), size=34, color=AMBER, box=True)
    S.text(0.7, 0.5, "JULY AVERAGE HIGH ≈ 10.5 °C", S.c("average high"), size=34, color=WHITE, box=True)
    S.text(0.7, 0.38, "FEBRUARY AVERAGE ≈ -8 °C", S.c("In February"), size=34, color=CYAN, box=True)
    S.caption("Nuuk averages, 1991–2020", S.c("And that's the mild"), color=MUTED, size=24)
    S.brand()


def s09_coast(S):
    glmap(S, [(0, *GL_VIEW), (S.c("Nuuk is the biggest"), -1.5, 66.5, 34), (S.T, -1, 67, 36)], ice_t=0.0)
    S.headline("PEOPLE LIVE WHERE THE ICE ENDS", 0.3, S.c("Nuuk is the biggest"), size=42)
    S.text(0.5, 0.1, "COASTLINE ≈ 44,087 km", S.c("coastline"), S.c("Nuuk is the biggest"), size=40, color=CYAN,
           box=True)
    t = S.c("almost every town")
    W_ = dict(ha="right", dx=-0.35, dy=-0.25)
    for i, (n, kw) in enumerate([("Qaqortoq", W_), ("Sisimiut", W_), ("Ilulissat", W_), ("Upernavik", W_),
                                 ("Tasiilaq", {}), ("Ittoqqortoormiit", {})]):
        town(S, n, t + 0.25 * i, size=20, **kw)
    town(S, "Nuuk", S.c("Nuuk is the biggest"), color=AMBER, size=30, ha="right", dx=-0.35, dy=-0.3)
    S.text(0.2, 0.5, "NUUK: 20,298 PEOPLE", S.c("about twenty"), size=36, color=AMBER, box=True, pop=True)
    S.text(0.2, 0.4, "= 36% OF GREENLAND", S.c("more than a third"), size=36, color=WHITE, box=True)
    S.text(0.2, 0.3, "89% LIVE IN TOWNS", S.c("Around eighty"), size=36, color=GREEN, box=True)
    S.brand()


def s10_roads(S):
    glmap(S, [(0, -2, 66.5, 34), (S.T, -2, 66.8, 33)], ice_t=0.0)
    S.headline("REASON 3: NO ROADS BETWEEN TOWNS", 0.3, size=42, y=0.08)
    names = ["Qaqortoq", "Nuuk", "Sisimiut", "Ilulissat", "Upernavik"]
    for n in names:
        town(S, n, 0.6, size=20, dx=-0.3, ha="right", dy=-0.1)
    t0 = S.c("you fly")
    pts = gl(np.array([TOWNS[n] for n in names]))
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        mid = (a + b) / 2 + np.array([0.9, 0])
        ts = np.linspace(0, 1, 40)
        curve = ((1 - ts) ** 2)[:, None] * a + (2 * (1 - ts) * ts)[:, None] * mid + (ts ** 2)[:, None] * b
        ln, = S.ax.plot([], [], color=AMBER, lw=2.5, ls=(0, (5, 3)), zorder=20)

        def up(t, ln=ln, curve=curve, ta=t0 + 0.5 * i):
            g = ease2((t - ta) / 0.8)
            k = max(int(g * len(curve)), 0)
            ln.set_data(curve[:k, 0], curve[:k, 1])
        S.updaters.append(up)
    S.text(0.74, 0.62, "PLANES: UP TO 37 PASSENGERS", S.c("thirty seven"), size=30, color=AMBER, box=True)
    S.text(0.74, 0.52, "NO RUNWAY? HELICOPTER", S.c("helicopter"), size=30, color=WHITE, box=True)
    S.text(0.74, 0.42, "COASTAL SHIP: APRIL TO DECEMBER", S.c("April to December"), size=30, color=CYAN, box=True)
    S.brand()


def s11_first(S):
    tl_setup(S)
    tl = TL(S)
    tl.camera([(0, -1300, 3800), (S.c("Then, around"), -300, 5400), (S.T, -300, 5500)])
    tl.marker(-2500, "INDEPENDENCE I", S.c("Independence One"), sub="c. 2500–1800 BC", color=CYAN, side=1, h=0.55,
              size=26)
    tl.marker(-2300, "SAQQAQ", S.c("Saqqaq"), sub="c. 2300–900 BC", color=GREEN, side=-1, h=0.35, size=26)
    tl.span(-600, 100, 0.25, VIOLET, "Dorset I", S.c("Dorset"), dur=1.0)
    tl.span(700, 1200, 0.25, VIOLET, "Dorset II", S.c("Dorset") + 0.6, dur=1.0)
    tl.marker(1100, "THULE (INUIT ANCESTORS)", S.c("Thule"), sub="arrive c. AD 1100", color=AMBER, side=-1, h=0.42,
              size=26)
    S.headline("PEOPLE HAVE LIVED HERE FOR ≈ 4,500 YEARS", 0.4, size=40, y=0.9)
    S.text(0.04, 0.06, "Dates: Encyclopaedia Britannica", S.c("They learned"), size=20, color=MUTED, ha="left")
    S.brand()


def s12_norse(S):
    tl_setup(S)
    tl = TL(S)
    tl.camera([(0, 1050, 600), (S.c("In seventeen"), 1350, 950), (S.T, 1360, 980)])
    tl.marker(982, "ERIK THE RED", S.c("Erik the Red"), sub="982–986", color=PINK, side=1, h=0.55, size=26)
    tl.span(986, 1450, 0.25, PINK, "Norse settlements: declined 1300s, abandoned 1400s", S.c("for more than"),
            dur=1.6)
    tl.span(1100, 2026, -0.55, AMBER, "Thule Inuit, from c. 1100: they stayed", S.c("The Inuit stayed"), dur=1.6)
    tl.marker(1721, "HANS EGEDE", S.c("In seventeen"), sub="1721: colonial era begins", color=CYAN, side=1, h=0.5,
              size=26)
    S.brand()


def s13_denmark(S):
    tl_setup(S)
    tl = TL(S, nice=[1, 2, 5])
    tl.camera([(0, 1987, 112), (S.T, 1989, 106)])
    tl.marker(1953, "PART OF DENMARK", S.c("Greenland became"), sub="1953", color=PINK, side=1, h=0.5, size=26)
    tl.marker(1979, "HOME RULE", S.c("home rule"), sub="1979", color=AMBER, side=-1, h=0.45, size=26)
    tl.marker(2009, "SELF-GOVERNMENT", S.c("wider self"), sub="2009", color=GREEN, side=1, h=0.5, size=26)
    tl.marker(2026, "SECURITY DEAL", 0.6, sub="Nov 2026", color=CYAN, side=-1, h=0.4, size=22)
    S.headline("DENMARK STILL HANDLES FOREIGN AFFAIRS + SECURITY", S.c("Today"), S.c("Nearly nine"), size=36,
               y=0.9)
    S.headline("88% OF RESIDENTS WERE BORN IN GREENLAND", S.c("Nearly nine"), size=38, y=0.9, color=AMBER)
    S.brand()


def s14_money(S):
    glmap(S, ice_t=0.0, dim=True)
    S.headline("REASON 4: THE ECONOMY", 0.3)
    S.bars([("Fishing's share of exports (approx.)", 90, CYAN, S.c("Fishing produces"))],
           S.c("Fishing produces") - 0.2, rect=(0.2, 0.62, 0.6, 0.1), xmax=115, unit="%", dec=0)
    S.text(0.5, 0.42, "DENMARK'S BLOCK GRANT: DKK 4.1 BILLION (2023)", S.c("block grant"), size=38, color=AMBER,
           box=True, pop=True)
    S.text(0.5, 0.32, "≈ HALF OF THE GOVERNMENT'S REVENUE", S.c("roughly half"), size=38, color=WHITE, box=True)
    S.caption("Huge area + few people + no roads = costly services", S.c("A small population"), color=GREEN)
    S.brand()


def s15_why_now(S):
    gpc = PolyCollection([], facecolors=LAND, edgecolors=EDGE, linewidths=0.6, zorder=2)
    gl_pc = PolyCollection([], facecolors=CYAN, edgecolors=WHITE, linewidths=1.0, zorder=3)
    S.ax.add_patch(Circle((0, 0), 1.0, fc="#0f2740", ec="#4a6a90", lw=2, zorder=1))
    S.ax.add_collection(gpc)
    S.ax.add_collection(gl_pc)
    S.ax.set_xlim(-1.35 * W / H, 1.35 * W / H)
    S.ax.set_ylim(-1.35, 1.35)
    others = [r for n in COUNTRIES if n != "Greenland" for r in COUNTRIES[n]]
    pit = np.array([PITUFFIK])
    sc = S.ax.scatter([], [], s=150, color=AMBER, edgecolors=WHITE, linewidths=2, zorder=5)
    lab = S.ax.text(0, 0, "PITUFFIK", fontproperties=BOLD, size=22, color=AMBER, zorder=6, alpha=0)
    tp = S.c("Pituffik")

    def up(t):
        lon0 = -55 + 0.8 * t
        vs = [ortho(r, lon0, 62)[0] for r in others if ortho(r, lon0, 62)[1] > 0]
        gpc.set_verts(vs)
        gl_pc.set_verts([ortho(r, lon0, 62)[0] for r in GL])
        p = ortho(pit, lon0, 62)[0][0]
        a = ease((t - tp) / 0.4)
        sc.set_offsets([p])
        sc.set_alpha(a)
        lab.set_position((p[0] - 0.36, p[1] + 0.03))
        lab.set_alpha(a)
    S.updaters.append(up)
    S.headline("WHY IT MATTERS: LOCATION", S.c("Location"), S.c("Greenland's natural"), size=44)
    S.caption("Resources include zinc, gold, uranium and rare earths", S.c("Greenland's natural"),
              S.c("And as the Arctic"), color=GREEN)
    S.caption("Empty island, global attention", S.c("An island that"), color=AMBER)
    S.brand()


def s16_recap(S):
    glmap(S, ice_t=0.0, dim=True)
    S.headline("WHY NOBODY LIVES IN GREENLAND", 0.3, size=44)
    rows = [("1. ICE: ≈ 80% COVERED, UP TO 3 KM THICK", "Four fifths", CYAN),
            ("2. COLD: NUUK'S JULY ≈ 7 °C", "Even the ice-free", WHITE),
            ("3. NO ROADS BETWEEN TOWNS", "There are no roads", AMBER),
            ("4. TINY POPULATION, HUGE AREA", "And a tiny", GREEN)]
    for i, (txt, ph, col) in enumerate(rows):
        S.text(0.5, 0.68 - 0.13 * i, txt, S.c(ph), size=40, color=col, box=True, pop=True)


def s17_outro(S):
    glmap(S, [(0, *GL_VIEW), (S.T, 0.4, 71.6, 50)], ice_t=0.0, ice_alpha=0.4, dim=True)
    S.text(0.5, 0.62, "WOULD YOU LIVE IN GREENLAND", 0.3, size=58, pop=True)
    S.text(0.5, 0.52, "FOR A YEAR?", 0.6, size=58, color=CYAN, pop=True)
    S.text(0.5, 0.38, "Tell me in the comments", S.c("Tell me"), size=34, color=MUTED, font=REG)
    S.text(0.5, 0.22, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=48, color=AMBER, box=True, pop=True)
    S.fade_in_out(0.3, 0.8)
