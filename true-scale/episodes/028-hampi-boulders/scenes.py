"""Scenes for 028 Hampi: why it's covered in giant boulders. S.c("phrase") is when the narrator says it.
Boulder landscapes, the granite cross-section, the weathering blocks and the temple drawings are illustrations,
not to scale. The Tungabhadra line is schematic (Natural Earth has no Tungabhadra) and pin positions are approximate."""
from engine.core import *
from engine.india import *
from engine.timeline import TL, setup as tl_setup
from matplotlib.patches import Polygon as MPoly, FancyBboxPatch, Rectangle, Ellipse, Circle as Circ

HAMPI = (76.46, 15.335)
HOSAPETE = (76.39, 15.27)
BLR = (77.59, 12.97)
TALIKOTA = (76.32, 16.47)
BEIJING = (116.40, 39.90)
ROME = (12.50, 41.90)
LISBON = (-9.14, 38.72)
HERAT = (62.20, 34.35)
VENICE = (12.33, 45.44)
# Schematic course of the Tungabhadra (approximate; for orientation only)
TUNGA = [(75.70, 13.97), (75.80, 14.51), (76.05, 14.95), (76.33, 15.27), (76.47, 15.345), (76.60, 15.41),
         (76.90, 15.63), (77.42, 15.94), (78.05, 15.83), (78.27, 15.93)]
KA_VIEW = (76.4, mercy(14.6), 9.0)
HAMPI_VIEW = (76.45, mercy(15.32), 1.3)

GRANITE, GRANITE_E, GRANITE_D = "#c9a26b", "#6b4a2b", "#a77b4a"
GRUS, SOIL = "#7a5a3a", "#3b2f24"
BOULDER_COLS = ["#c9a26b", "#b88d58", "#d8b47e", "#a77b4a", "#bf9660"]


# ------------------------------------------------------------------ helpers
def note(S, s, t0, x=0.985, y=0.065, size=18):
    S.text(x, y, s, t0, size=size, color=MUTED, ha="right", font=REG)


def label(S, lon, lat, s, t0, color=WHITE, size=24, t1=None):
    pin(S, lon, lat, s, t0, color=color, ring=False, dy=0, size=size, t1=t1)


def fade(S, arts, t0, t1=None, peak=1.0, dur=0.4):
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / dur), ease((t1 - t) / dur)) * peak
        for x in arts:
            x.set_alpha(a)
    S.updaters.append(up)


def card(S, text, t0, y=0.2, color=WHITE, t1=None, size=34, x=0.5, ha="center"):
    t0 = S.c(t0) if isinstance(t0, str) else t0
    t1 = S.c(t1) if isinstance(t1, str) else t1
    return S.text(x, y, text, t0, t1, size=size, color=color, box=True, ha=ha)


def line_draw(S, xy, t0, color=AMBER, dur=1.4, lw=4, ls="-", z=26, t1=None):
    p = np.asarray(xy, float)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    ln, = S.ax.plot([], [], color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round")
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        g = ease2((t - t0) / dur) * seg[-1]
        if g <= 0:
            ln.set_data([], [])
            return
        k = min(max(np.searchsorted(seg, g), 1), len(p) - 1)
        f = (g - seg[k - 1]) / max(seg[k] - seg[k - 1], 1e-9)
        q = np.vstack([p[:k], p[k - 1] + (p[k] - p[k - 1]) * min(f, 1)])
        ln.set_data(q[:, 0], q[:, 1])
        ln.set_alpha(min(1, ease((t1 - t) / 0.4)))
    S.updaters.append(up)
    return ln


def tunga(S, t0, dur=1.6, lab=None):
    line_draw(S, merc(np.array(TUNGA)), t0, color="#3a8fc4", dur=dur, lw=4, z=20)
    if lab:
        label(S, *lab, "TUNGABHADRA (approx.)", t0 + dur * 0.6, color=CYAN, size=20)


def ka_hl(S, t0, t1=None, peak=0.38):
    S.highlight(ST["Karnataka"], AMBER, t0, t1, peak=peak, lw=1.5)


def stage(S):
    """Diagram mode: 16 x 9 units, equal aspect."""
    S.ax.set_xlim(0, 16)
    S.ax.set_ylim(0, 9)
    S.brand()


def landscape(S, t0=0.0, dim=1.0, seed=7, rise=1.6):
    """Illustrated Hampi skyline: warm sky, granite boulder heaps, a temple tower. Not to scale."""
    stage(S)
    ax = S.ax
    for k in range(40):
        y = 2.0 + 7.0 * k / 40
        u = k / 40
        c = np.array([0.95, 0.62, 0.28]) * (1 - u) ** 1.6 + np.array([0.043, 0.102, 0.169]) * (1 - (1 - u) ** 1.6)
        ax.add_patch(Rectangle((0, y), 16, 7.0 / 40 + 0.01, fc=c * dim + (1 - dim) * np.array([0.03, 0.07, 0.11]),
                               ec="none", zorder=0))
    ax.add_patch(Circ((12.2, 3.6), 0.6, fc="#ffd27a", ec="none", alpha=0.85 * dim, zorder=0.5))
    ax.add_patch(Rectangle((0, 0), 16, 2.1, fc=SOIL, ec="none", zorder=1))
    rng = np.random.default_rng(seed)
    piles = [(1.6, 2.6, 5), (4.6, 1.8, 4), (8.4, 3.0, 6), (12.6, 2.2, 5), (15.3, 1.6, 4)]
    arts = []
    for i, (cx, half, rows) in enumerate(piles):
        grp = []
        for r in range(rows):
            w = half * (1 - r / (rows + 0.6))
            n = max(1, int(round(w / 0.55)))
            for j in range(n):
                x = cx - w + (j + 0.5) * 2 * w / n + rng.uniform(-0.12, 0.12)
                y = 1.95 + r * 0.62 + rng.uniform(-0.05, 0.08)
                ew, eh = rng.uniform(0.75, 1.15), rng.uniform(0.62, 0.85)
                e = Ellipse((x, y + eh / 2), ew, eh, angle=rng.uniform(-18, 18),
                            fc=BOULDER_COLS[rng.integers(len(BOULDER_COLS))], ec=GRANITE_E, lw=1.4,
                            zorder=2 + r * 0.01 + i * 0.001, alpha=0)
                ax.add_patch(e)
                grp.append(e)
        if i == 2:        # a balanced boulder on top of the tallest heap
            e = Ellipse((cx + 0.15, 1.95 + rows * 0.62 + 0.42), 1.0, 0.78, angle=8, fc="#d8b47e", ec=GRANITE_E,
                        lw=1.4, zorder=3, alpha=0)
            ax.add_patch(e)
            grp.append(e)
        arts.append(grp)
    # small gopuram silhouette between heaps
    gx, gy = 10.6, 2.0
    gop = MPoly([(gx - 0.55, gy), (gx + 0.55, gy), (gx + 0.38, gy + 1.5), (gx + 0.2, gy + 1.75), (gx - 0.2, gy + 1.75),
                 (gx - 0.38, gy + 1.5)], closed=True, fc="#5a4330", ec="#2b2017", lw=1.2, zorder=1.9, alpha=0)
    ax.add_patch(gop)
    for i, grp in enumerate(arts):
        fade(S, grp, t0 + i * rise / len(arts), peak=dim)
    fade(S, [gop], t0 + rise, peak=dim)


def rain(S, xs, ytop, ybot, t0, t1, n=3, color=CYAN):
    """Falling raindrops along joint lines."""
    segs = LineCollection([], colors=color, linewidths=2.5, zorder=12, alpha=0)
    S.ax.add_collection(segs)
    rng = np.random.default_rng(1)
    phase = rng.uniform(0, 1, (len(xs), n))

    def up(t):
        a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        lines = []
        for i, x in enumerate(xs):
            for k in range(n):
                f = ((t - t0) / 1.6 + phase[i, k]) % 1.0
                y = ytop - f * (ytop - ybot)
                lines.append([(x, y), (x, y - 0.3)])
        segs.set_segments(lines)
        segs.set_alpha(0.85 * a)
    S.updaters.append(up)


# blocks for the weathering diagram: 6 columns x 3 rows
BX0, BY0, BW, BH, GAP, NC, NR = 2.6, 1.0, 1.75, 1.45, 0.08, 6, 3


def blocks(S, t_round0, t_round1, start_round=0.0, z=6):
    """Granite blocks cut by joints; corners round off between t_round0 and t_round1."""
    out = []
    for r in range(NR):
        for c in range(NC):
            x, y = BX0 + c * (BW + GAP), BY0 + r * (BH + GAP)
            p = FancyBboxPatch((x, y), BW, BH, boxstyle="round,pad=0,rounding_size=0.01", fc="#b9a48a",
                               ec="#5c4c3a", lw=1.6, zorder=z)
            S.ax.add_patch(p)
            out.append([p, x, y, r, c])

    def up(t):
        g = start_round + (1 - start_round) * ease2((t - t_round0) / max(t_round1 - t_round0, 1e-6))
        shrink = 0.16 * g
        for p, x, y, r, c in out:
            p.set_bounds(x + shrink, y + shrink, BW - 2 * shrink, BH - 2 * shrink)
            p.set_boxstyle("round", pad=0, rounding_size=0.02 + 0.6 * g)
    S.updaters.append(up)
    return out


def gopuram(ax, x, base, height, width, z=4):
    """Stepped temple gateway tower (schematic)."""
    pts = []
    tiers = 9
    for i in range(tiers):
        y0 = base + height * 0.12 + (height * 0.78) * i / tiers
        y1 = base + height * 0.12 + (height * 0.78) * (i + 1) / tiers
        w0 = width * (1 - 0.55 * i / tiers)
        w1 = width * (1 - 0.55 * (i + 1) / tiers)
        pts.append(MPoly([(x - w0 / 2, y0), (x + w0 / 2, y0), (x + w1 / 2, y1 - 0.02), (x - w1 / 2, y1 - 0.02)],
                         closed=True, fc=GRANITE if i % 2 == 0 else "#d8b47e", ec=GRANITE_E, lw=1.2, zorder=z))
    pts.append(Rectangle((x - width / 2, base), width, height * 0.12, fc=GRANITE_D, ec=GRANITE_E, lw=1.2, zorder=z))
    wt = width * 0.45
    pts.append(MPoly([(x - wt / 2, base + height * 0.9), (x + wt / 2, base + height * 0.9), (x + wt * 0.35, base + height),
                      (x - wt * 0.35, base + height)], closed=True, fc="#e7cf9f", ec=GRANITE_E, lw=1.2, zorder=z))
    pts.append(Rectangle((x - width * 0.12, base), width * 0.24, height * 0.1, fc="#2b2017", ec="none", zorder=z + 0.1))
    for p in pts:
        p.set_alpha(0)
        ax.add_patch(p)
    return pts


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    landscape(S, 0.0)
    S.headline("NOBODY DROPPED THESE BOULDERS", S.c("Nobody dropped"), S.c("And around"), size=48)
    card(S, "GRANITE ≈ 2.5 BILLION YEARS OLD", "two and a half billion", 0.76, AMBER, t1="And around", size=40)
    t_c = S.c("And around")
    S.headline("AROUND 1500, AN ESTIMATED...", t_c, S.c("This is Hampi"), size=44, color=WHITE)
    card(S, "1. BEIJING", "after Beijing", 0.72, MUTED, t1="This is Hampi", size=38)
    card(S, "2. THE CITY BUILT HERE", "second largest", 0.62, AMBER, t1="This is Hampi", size=44)
    S.text(0.5, 0.76, "HAMPI, KARNATAKA", S.c("This is Hampi"), S.c("In the next"), size=72, color=WHITE,
           box=True, pop=True)
    rows = [("How the boulders formed", "how the boulders"), ("An empire's capital", "how an empire"),
            ("Destroyed in 6 months", "how it fell"), ("Dug up this November", "what archaeologists")]
    for i, (s, ph) in enumerate(rows):
        S.text(0.06, 0.8 - i * 0.1, f"{i + 1} · {s}", S.c(ph), size=36, ha="left", box=True)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    landscape(S, 0.0, rise=0.01)
    S.text(0.5, 0.7, "HAMPI", 0.3, size=130, pop=True, box=True)
    S.text(0.5, 0.52, "WHY IT'S COVERED IN GIANT BOULDERS", 0.8, size=46, color=AMBER, pop=True, box=True)
    S.text(0.5, 0.93, "TRUE SCALE", 0.0, size=28, color=CYAN)


def s03_where(S):
    t_z = S.c("central Karnataka")
    india(S, [(0, *INDIA_VIEW), (t_z, *KA_VIEW), (S.c("Hosapete"), *HAMPI_VIEW),
              (S.c("Bengaluru"), *KA_VIEW), (S.c("From the air"), 76.45, mercy(15.32), 1.6),
              (S.T, 76.45, mercy(15.32), 1.5)])
    ka_hl(S, 0.6, S.c("From the air"))
    state_tag(S, "KARNATAKA", t_z)
    tunga(S, S.c("Tungabhadra"), lab=(76.95, 15.75))
    pin(S, *HAMPI, "HAMPI", S.c("Hampi sits"), dy=0.6)
    pin(S, *HOSAPETE, "HOSAPETE ≈ 13 km", S.c("Hosapete"), color=WHITE, dy=-1.6, ring=False, size=22)
    pin(S, *BLR, "BENGALURU ≈ 340 km", S.c("Bengaluru"), color=WHITE, dy=0.4, size=22, t1=S.c("From the air"))
    card(S, "RIDGE AFTER RIDGE OF GRANITE BOULDERS", "From the air", 0.14, AMBER, size=38)
    note(S, "River line approximate · distances per Karnataka Tourism", t_z, y=0.035, x=0.8)


def s04_legend(S):
    landscape(S, 0.0, dim=0.55, rise=0.01)
    S.headline("THE LEGEND", 0.3, size=48, color=AMBER)
    card(S, "KISHKINDHA · kingdom of the monkey brothers (Ramayana)", "Kishkindha", 0.78, WHITE, size=32)
    card(S, "VALI vs SUGREEVA: boulders hurled in their fight?", "hurled", 0.66, WHITE, size=32)
    card(S, "...or piled up for the bridge to Lanka?", "bridge to Lanka", 0.56, WHITE, size=32)
    card(S, "MATANGA HILL · tallest hill in Hampi · Sugreeva's refuge", "Matanga Hill", 0.44, CYAN, size=32)
    S.caption("NOW, THE GEOLOGY", S.c("The geology"), color=AMBER, size=42)


def s05_granite(S):
    stage(S)
    ax = S.ax
    # crust layers
    for i, c in enumerate(["#1b2a3d", "#1f3045", "#22354c", "#263a52"]):
        ax.add_patch(Rectangle((0, 7.2 - (i + 1) * 1.8), 16, 1.8, fc=c, ec="none", zorder=1))
    xs = np.linspace(0, 16, 120)
    ax.fill_between(xs, 7.2, 7.4 + 0.12 * np.sin(xs * 2.3), color="#3b4f68", zorder=2)
    surf = ax.text(0.4, 7.65, "SURFACE", fontproperties=BOLD, size=22, color=MUTED, va="bottom")
    t_m = S.c("molten magma")
    t_cool = S.c("It cooled very slowly")
    body = Ellipse((8.0, 3.1), 8.6, 3.8, fc="#ff7a2f", ec="#ffb36b", lw=3, zorder=3, alpha=0)
    ax.add_patch(body)
    hot, cold = np.array([1.0, 0.48, 0.18]), np.array([0.79, 0.64, 0.42])

    def up(t):
        body.set_alpha(0.95 * ease((t - t_m) / 1.0))
        g = ease2((t - t_cool) / 4.0)
        body.set_facecolor(hot * (1 - g) + cold * g)
        body.set_edgecolor(np.array([1.0, 0.7, 0.42]) * (1 - g) + np.array([0.42, 0.29, 0.17]) * g)
    S.updaters.append(up)
    # upward intrusion arrows as triangles
    tri = [MPoly([(x - 0.25, 0.2), (x + 0.25, 0.2), (x, 0.9)], closed=True, fc="#ff7a2f", ec="none", zorder=3,
                 alpha=0) for x in (5.5, 8.0, 10.5)]
    for p in tri:
        ax.add_patch(p)
    fade(S, tri, t_m, S.c("It cooled"))
    # joints, clipped to the granite body
    t_j = S.c("cracked into a grid")
    jl = []
    for x in np.arange(4.2, 12.2, 0.95):
        jl.append(ax.plot([x, x], [1.0, 5.2], color="#3a2a1a", lw=2.2, zorder=4, alpha=0)[0])
    for y in np.arange(1.6, 5.2, 0.75):
        jl.append(ax.plot([3.6, 12.4], [y, y], color="#3a2a1a", lw=2.2, zorder=4, alpha=0)[0])
    for ln in jl:
        ln.set_clip_path(body)
    fade(S, jl, t_j, dur=1.0)
    S.headline("STEP 1 · THE GRANITE", 0.3, size=44, color=AMBER)
    card(S, "DHARWAR CRATON · one of India's oldest, most stable pieces of crust", "Dharwar craton", 0.78, WHITE,
         size=28, t1="molten magma")
    card(S, "MAGMA, DEEP UNDERGROUND · Late Archaean, ≈ 2.5 billion years ago", "molten magma", 0.78, AMBER,
         size=28, t1=t_cool)
    card(S, "COOLED SLOWLY, MILES BELOW THE SURFACE", t_cool, 0.78, WHITE, size=30, t1=t_j)
    card(S, "IT SHRANK AND CRACKED: JOINTS", t_j, 0.78, AMBER, size=34)
    card(S, "the cracks set the shape of every boulder", "Those cracks", 0.66, CYAN, size=28)
    note(S, "Illustration, not to scale", 0.5, y=0.02, x=0.6)


def s06_weathering(S):
    stage(S)
    ax = S.ax
    ax.add_patch(Rectangle((0, 6.75), 16, 2.25, fc="#0f2236", ec="none", zorder=0))
    ax.add_patch(Rectangle((0, 5.6), 16, 1.15, fc=SOIL, ec="none", zorder=2))
    ax.text(0.4, 6.15, "SOIL", fontproperties=BOLD, size=20, color=MUTED, va="center", zorder=3)
    gr = Rectangle((BX0 - 0.15, BY0 - 0.1), NC * (BW + GAP) + 0.2, NR * (BH + GAP) + 0.12, fc=GRUS, ec="none",
                   zorder=5)
    ax.add_patch(gr)
    t_r = S.c("Rainwater seeps")
    t_f = S.c("feldspar")
    t_round = S.c("The corners")
    blocks(S, t_f, S.c("Geologists call these") + 0.5)
    xs = [BX0 + c * (BW + GAP) - GAP / 2 for c in range(1, NC)]
    rain(S, xs, 6.6, 1.2, t_r, S.T + 1)
    S.headline("STEP 2 · ROTTING UNDERGROUND", 0.3, size=44, color=AMBER)
    card(S, "RAINWATER SEEPS DOWN THE JOINTS", t_r, 0.8, CYAN, size=30, t1=t_f)
    card(S, "FELDSPAR TURNS TO CLAY + GRIT = GRUS", t_f, 0.8, AMBER, size=30, t1=t_round)
    card(S, "CORNERS ARE ATTACKED FROM 2-3 SIDES: THEY GO FIRST", t_round, 0.8, WHITE, size=30,
         t1="Geologists call these")
    card(S, "ROUNDED CORES OF FRESH ROCK = CORESTONES", "Geologists call these", 0.8, AMBER, size=34)
    note(S, "Illustration, not to scale", 0.5, y=0.02, x=0.6)


def s07_exposed(S):
    stage(S)
    ax = S.ax
    ax.add_patch(Rectangle((0, 0), 16, 9, fc="#0f2236", ec="none", zorder=0))
    for k in range(30):
        y = 1.0 + 8.0 * k / 30
        u = k / 30
        c = np.array([0.95, 0.62, 0.28]) * (1 - u) ** 2 + np.array([0.06, 0.13, 0.21]) * (1 - (1 - u) ** 2)
        sky = Rectangle((0, y), 16, 8.0 / 30 + 0.01, fc=c, ec="none", zorder=0.2, alpha=0)
        ax.add_patch(sky)
        fade(S, [sky], S.c("That's why"), dur=1.5)
    ground = Rectangle((0, 0), 16, 1.0, fc=SOIL, ec="none", zorder=8)
    ax.add_patch(ground)
    soil = Rectangle((0, 5.6), 16, 1.15, fc=SOIL, ec="none", zorder=7)
    ax.add_patch(soil)
    gr = Rectangle((BX0 - 0.15, BY0 - 0.1), NC * (BW + GAP) + 0.2, NR * (BH + GAP) + 0.12, fc=GRUS, ec="none",
                   zorder=5)
    ax.add_patch(gr)
    t_w = S.c("wears away")
    t_g = S.c("carry the loose grus")
    bl = blocks(S, 0, 1, start_round=1.0)
    rng = np.random.default_rng(4)
    drop = {}
    for p, x, y, r, c in bl:
        gone = (r == 2 and c in (0, 1, 4, 5)) or (r == 1 and c in (0, 5))
        dy = -r * 0.25 + rng.uniform(-0.08, 0.08)
        dx = rng.uniform(-0.35, 0.35) * r + (0.45 if c < 2 and r > 0 else -0.45 if c > 3 and r > 0 else 0)
        drop[id(p)] = (dx, dy, gone)
    t_settle = t_g + 2.0

    def up(t):
        k = ease2((t - t_w) / 3.0)
        soil.set_y(5.6 + 4.0 * k)
        soil.set_alpha(1 - k)
        gr.set_alpha(1 - ease2((t - t_g) / 2.5))
        s = ease2((t - t_settle) / 1.5)
        for p, x, y, r, c in bl:
            dx, dy, gone = drop[id(p)]
            b = p.get_bbox()
            p.set_x(x + 0.16 + dx * s)
            p.set_y(y + 0.16 + dy * s)
            p.set_alpha(1 - (ease((t - t_g) / 2.0) if gone else 0))
            p.set_facecolor(GRANITE if s > 0.5 else "#b9a48a")
    S.updaters.append(up)
    S.headline("STEP 3 · THE BOULDERS APPEAR", 0.3, size=44, color=AMBER)
    card(S, "THE LAND ABOVE WEARS AWAY", t_w, 0.8, WHITE, size=30, t1=t_g)
    card(S, "RAIN, GRAVITY, WIND CARRY THE GRUS OFF", t_g, 0.8, CYAN, size=30, t1="That's why")
    card(S, "CORESTONES LEFT STACKED WHERE THEY FORMED", "That's why", 0.8, AMBER, size=30, t1="Hills like these")
    card(S, "TORS · INSELBERGS (German: 'island mountain')", "Hills like these", 0.8, WHITE, size=30,
         t1="How long")
    card(S, "HOW LONG? STILL DEBATED, BUT VAST", "How long", 0.8, PINK, size=32)
    note(S, "Illustration, not to scale", 0.5, y=0.02, x=0.6)


def s08_scale(S):
    stage(S)
    ax = S.ax
    cx, cy, R = 8.0, 4.2, 2.7
    t_sq = S.c("Squeeze")
    face = Circ((cx, cy), R, fc="#0f2236", ec=WHITE, lw=4, zorder=3, alpha=0)
    ax.add_patch(face)
    ticks = []
    for h in range(24):
        a = np.pi / 2 - 2 * np.pi * h / 24
        r0 = R * (0.86 if h % 6 else 0.78)
        ticks.append(ax.plot([cx + r0 * np.cos(a), cx + R * 0.95 * np.cos(a)],
                             [cy + r0 * np.sin(a), cy + R * 0.95 * np.sin(a)], color=MUTED, lw=2, zorder=4,
                             alpha=0)[0])
    nums = [ax.text(cx + R * 0.62 * np.cos(np.pi / 2 - 2 * np.pi * h / 24), cy + R * 0.62 * np.sin(np.pi / 2 - 2 * np.pi * h / 24),
                    f"{h:02d}:00", fontproperties=BOLD, size=18, color=MUTED, ha="center", va="center", zorder=4,
                    alpha=0) for h in (0, 6, 12, 18)]
    fade(S, [face] + ticks + nums, t_sq)
    wedge = matplotlib.patches.Wedge((cx, cy), R * 0.94, 90, 90, fc=GRANITE, ec="none", zorder=3.5, alpha=0)
    ax.add_patch(wedge)
    hand, = ax.plot([cx, cx], [cy, cy + R * 0.9], color=AMBER, lw=5, zorder=5, alpha=0)

    def up(t):
        g = ease2((t - t_sq - 0.5) / 4.0)
        ang = 90 - 360 * g
        a = np.radians(ang)
        hand.set_data([cx, cx + R * 0.9 * np.cos(a)], [cy, cy + R * 0.9 * np.sin(a)])
        hand.set_alpha(ease((t - t_sq) / 0.4))
        wedge.set_theta1(ang)
        wedge.set_theta2(90)
        wedge.set_alpha(0.55 * ease((t - t_sq) / 0.4))
    S.updaters.append(up)
    S.headline("AT TRUE SCALE", 0.3, size=44, color=AMBER)
    card(S, "2.5 BILLION YEARS OF GRANITE = 24 HOURS", t_sq, 0.79, GRANITE, size=36)
    t_e = S.c("ruled from Hampi")
    card(S, "VIJAYANAGARA AT HAMPI: 1336-1565 = 229 YEARS", t_e, 0.14, WHITE, size=32, t1="less than one")
    card(S, "ITS WHOLE REIGN ON THIS CLOCK ≈ 0.008 SECONDS", "less than one", 0.14, PINK, size=36)
    note(S, "229 ÷ 2,500,000,000 × 86,400 s ≈ 0.0079 s", S.c("less than one"), y=0.035, x=0.8)


def s09_empire(S):
    tl_setup(S)
    tl = TL(S, nice=[1, 2, 5])
    tl.camera([(0, 1450, 420), (S.T, 1452, 400)])
    S.headline("THE VIJAYANAGARA EMPIRE", 0.3, size=44, color=AMBER)
    tl.marker(1336, "FOUNDED", S.c("In thirteen thirty six"), sub="1336", color=AMBER, side=1, h=0.36, size=28)
    tl.span(1336, 1565, -0.45, GRANITE, "HAMPI IS THE CAPITAL · 229 YEARS", S.c("Hampi became"), dur=1.6)
    tl.marker(1565, "FALL", S.c("For more than two"), sub="1565", color=PINK, side=1, h=0.36, size=28)
    card(S, "HARIHARA I + BUKKA I", "two brothers", 0.78, WHITE, size=34)
    card(S, "BY THE RIVER, AMONG GRANITE BOULDERS", "It sat beside", 0.68, WHITE, size=30, t1="The empire grew")
    card(S, "RICH ON THE COTTON AND SPICE TRADE", "The empire grew", 0.68, GREEN, size=30)
    note(S, "Source: Ministry of Culture; Wikipedia (Hampi)", 0.5)


def s10_bigcity(S):
    india(S, [(0, 52, mercy(30), 150), (S.T, 52, mercy(30), 145)])
    S.headline("ONE OF THE BIGGEST CITIES ON EARTH", 0.3, S.c("Visitors were stunned"), size=42)
    pin(S, *BEIJING, "1. BEIJING", S.c("after Beijing"), color=WHITE, dy=1.0, size=24)
    pin(S, *HAMPI, "2. VIJAYANAGARA (HAMPI)", S.c("second largest"), color=AMBER, dy=-1.0, size=26, ha="left", dx=3)
    card(S, "c. 1500 · estimate (Nicholas Gier and others)", "Historians", 0.14, WHITE, size=30, x=0.3,
         t1="Visitors were stunned")
    S.headline("VISITORS WERE STUNNED", S.c("Visitors were stunned"), size=42, color=AMBER)
    t_a = S.c("Abdur Razzaq")
    line_draw(S, merc(np.array([HERAT, HAMPI])), t_a, color=CYAN, dur=1.2, lw=3, ls="--")
    pin(S, *HERAT, "ABDUR RAZZAQ · Persian envoy", t_a, color=CYAN, dy=1.0, size=22)
    t_n = S.c("Niccolo")
    line_draw(S, merc(np.array([VENICE, HAMPI])), t_n, color=GREEN, dur=1.2, lw=3, ls="--")
    pin(S, *VENICE, "NICCOLÒ DE' CONTI · Italy", t_n, color=GREEN, dy=1.0, size=22)
    t_p = S.c("Domingo Paes")
    line_draw(S, merc(np.array([LISBON, HAMPI])), t_p, color=PINK, dur=1.2, lw=3, ls="--")
    pin(S, *LISBON, "DOMINGO PAES · Portugal, c. 1520", t_p, color=PINK, dy=-6.0, size=22, ha="left", dx=-2)
    pin(S, *ROME, "ROME", S.c("to Rome"), color=WHITE, dy=-4.5, size=22)
    card(S, "PAES COMPARED ITS SIZE TO ROME", "to Rome", 0.14, PINK, size=34, x=0.3)
    note(S, "Travel lines are schematic, not routes", t_a, y=0.82)


def s11_temples(S):
    stage(S)
    ax = S.ax
    ax.add_patch(Rectangle((0, 0), 16, 1.3, fc=SOIL, ec="none", zorder=1))
    t_v = S.c("The Virupaksha")
    g = gopuram(ax, 3.4, 1.3, 6.3, 3.0)
    fade(S, g, t_v)
    sb = [ax.plot([5.4, 5.4], [1.3, 7.6], color=AMBER, lw=3, zorder=5, alpha=0)[0],
          ax.text(5.6, 4.4, "≈ 50 m", fontproperties=BOLD, size=30, color=AMBER, va="center", zorder=5, alpha=0)]
    fade(S, sb, S.c("about fifty"))
    card(S, "VIRUPAKSHA · gateway ≈ 50 m", t_v, 0.9, WHITE, size=28, x=0.24)
    card(S, "parts by the 11th century", "eleventh century", 0.82, MUTED, size=24, x=0.24)
    card(S, "WORSHIP NEVER STOPPED", "Worship there", 0.16, GREEN, size=28, x=0.22)
    # stone chariot
    t_c = S.c("stone chariot")
    cx, cy = 10.6, 1.3
    ch = [Rectangle((cx - 1.1, cy + 0.9), 2.2, 1.6, fc=GRANITE, ec=GRANITE_E, lw=1.6, zorder=4),
          Rectangle((cx - 1.4, cy + 0.6), 2.8, 0.35, fc=GRANITE_D, ec=GRANITE_E, lw=1.6, zorder=4),
          MPoly([(cx - 0.9, cy + 2.5), (cx + 0.9, cy + 2.5), (cx + 0.5, cy + 3.3), (cx - 0.5, cy + 3.3)], closed=True,
                fc="#d8b47e", ec=GRANITE_E, lw=1.6, zorder=4),
          Rectangle((cx - 0.35, cy + 1.1), 0.7, 1.1, fc="#2b2017", ec="none", zorder=4.1)]
    for wx in (cx - 0.95, cx + 0.95):
        ch.append(Circ((wx, cy + 0.6), 0.6, fc="#d8b47e", ec=GRANITE_E, lw=2, zorder=4.2))
        ch.append(Circ((wx, cy + 0.6), 0.15, fc=GRANITE_E, ec="none", zorder=4.3))
    for p in ch:
        p.set_alpha(0)
        ax.add_patch(p)
    fade(S, ch, t_c)
    card(S, "VITTALA · stone chariot (Garuda shrine)", t_c, 0.9, WHITE, size=28, x=0.72)
    card(S, "on India's ₹50 note", "fifty rupee", 0.82, AMBER, size=26, x=0.72)
    # musical pillars
    t_m = S.c("musical sounds")
    pl = []
    for k in range(4):
        x = 13.2 + k * 0.6
        pl.append(Rectangle((x, 1.3), 0.3, 2.6, fc=GRANITE, ec=GRANITE_E, lw=1.4, zorder=4))
    for p in pl:
        p.set_alpha(0)
        ax.add_patch(p)
    fade(S, pl, S.c("Inside, a hall"))
    waves = []
    for r in (0.5, 0.9, 1.3):
        w = matplotlib.patches.Arc((14.1, 4.4), r * 2, r * 1.3, theta1=20, theta2=160, color=CYAN, lw=3, zorder=5,
                                   alpha=0)
        ax.add_patch(w)
        waves.append(w)

    def up(t):
        for i, w in enumerate(waves):
            ph = ((t - t_m) / 1.2 - i / 3) % 1.0
            w.set_alpha(ease((t - t_m) / 0.4) * (1 - ph))
    S.updaters.append(up)
    card(S, "PILLARS THAT RING WHEN STRUCK", "Inside, a hall", 0.16, CYAN, size=28, x=0.78)
    note(S, "Drawings are illustrations, not to scale", 0.5, y=0.035, x=0.8)


def s12_fall(S):
    t_m = S.c("In eighteen hundred")
    india(S, [(0, *KA_VIEW), (0.8, 76.9, mercy(15.95), 5.0), (t_m, 76.9, mercy(15.95), 4.8),
              (S.T, 76.9, mercy(15.95), 4.7)])
    ka_hl(S, 0.3, peak=0.3)
    pin(S, *HAMPI, "HAMPI", 0.4, dy=0.4)
    pin(S, *TALIKOTA, "TALIKOTA (battle area, approx.)", S.c("Battle of Talikota"), color=PINK, dy=0.3, size=24)
    S.headline("1565 · THE BATTLE OF TALIKOTA", 0.3, t_m, size=44, color=PINK)
    card(S, "DECCAN SULTANATES DEFEAT VIJAYANAGARA", "an alliance", 0.5, WHITE, size=28, x=0.7, t1="The capital was")
    card(S, "ALIYA RAMA RAYA captured and beheaded", "Aliya Rama Raya", 0.4, WHITE, size=28, x=0.7, t1="The capital was")
    card(S, "PILLAGED, LOOTED, BURNT FOR 6 MONTHS", "The capital was", 0.5, PINK, size=30, x=0.7, t1=t_m)
    card(S, "THEN ABANDONED", "then abandoned", 0.4, PINK, size=30, x=0.7, t1=t_m)
    S.headline("REDISCOVERED", t_m, size=44, color=AMBER)
    card(S, "1800 · Colin Mackenzie surveys the ruins", t_m, 0.5, WHITE, size=28, x=0.7)
    card(S, "1900 · Robert Sewell: 'A Forgotten Empire'", "Robert Sewell", 0.4, CYAN, size=28, x=0.7)


def s13_unesco(S):
    landscape(S, 0.0, dim=0.5, rise=0.01)
    S.headline("A WORLD HERITAGE SITE", 0.3, size=44, color=AMBER)
    stats = [("1986", "UNESCO World Heritage listing", "nineteen eighty six", AMBER),
             ("1999-2006", "on the list of sites in danger", "nineteen ninety nine", PINK),
             ("≈ 42 km²", "protected area (4,187 hectares)", "four thousand", CYAN),
             ("1,600+", "surviving remains", "sixteen hundred", GREEN)]
    for i, (big, small, ph, col) in enumerate(stats):
        x = 0.27 if i % 2 == 0 else 0.73
        y = 0.68 if i < 2 else 0.4
        S.text(x, y, big, S.c(ph), size=72, color=col, box=True, pop=True)
        S.text(x, y - 0.1, small, S.c(ph) + 0.3, size=28, color=WHITE)
    card(S, "temples · palaces · markets · water tanks · gateways", "Temples, palaces", 0.14, WHITE, size=30)


def s14_news(S):
    landscape(S, 0.0, dim=0.45, rise=0.01)
    S.headline("STILL BEING DUG UP", 0.3, size=46, color=AMBER)
    t_a = S.c("In May")
    S.text(0.5, 0.74, "MAY 2026 · near the HAZARA RAMA temple", t_a, size=36, color=WHITE, box=True)
    S.text(0.5, 0.64, "buried stone ceiling + rare elephant carvings · ≈ 4.3 × 4.2 m", S.c("stone ceiling"),
           size=30, color=MUTED)
    t_b = S.c("on the fourteenth")
    S.text(0.5, 0.46, "14 NOV 2026 · two more temples: VISHNU + SHIVA", t_b, size=36, color=AMBER, box=True,
           pop=True)
    S.text(0.5, 0.36, "near the Ganagitti temple, Hampi's oldest Jain shrine (1386)", S.c("Ganagitti"), size=30,
           color=MUTED)
    S.caption("ARCHAEOLOGICAL SURVEY OF INDIA EXCAVATIONS", t_a, color=CYAN, size=32)
    note(S, "Sources: Asianet Newsable (17 May 2026), IANS via ap7am (14 Nov 2026)", 0.6, y=0.02, x=0.75)


def s15_visit(S):
    t_t = S.c("Take the train")
    india(S, [(0, *KA_VIEW), (t_t, 76.85, mercy(15.32), 1.4), (S.T, 76.83, mercy(15.32), 1.35)])
    ka_hl(S, 0.3, t_t, peak=0.35)
    tunga(S, 0.2, dur=0.1)
    pin(S, *HAMPI, "HAMPI", 0.3, dy=0.6)
    S.headline("WHY GO NOW", 0.2, size=44, color=AMBER)
    card(S, "BEST TIME: OCTOBER TO FEBRUARY", "October to February", 0.14, GREEN, size=40, t1=t_t)
    card(S, "≈ 3 DAYS TO SEE IT PROPERLY", "three days", 0.24, WHITE, size=32, t1=t_t)
    pin(S, *HOSAPETE, "HOSAPETE JUNCTION ≈ 13 km", t_t, color=WHITE, dy=-1.6, ring=False, size=22)
    rs = [("MATANGA HILL at sunset", "Climb Matanga"), ("A CORACLE on the Tungabhadra", "Take a coracle"),
          ("THE HAMPI FESTIVAL, if your dates allow", "catch the Hampi festival")]
    for i, (s, ph) in enumerate(rs):
        S.text(0.45, 0.72 - i * 0.1, f"{i + 1} · {s}", S.c(ph), size=34, ha="left", box=True)
    note(S, "Source: Karnataka Tourism", 0.5, y=0.035, x=0.8)


def s16_caveat(S):
    landscape(S, 0.0, dim=0.55, rise=0.01)
    S.headline("BEFORE YOU GO", 0.3, size=46, color=PINK)
    card(S, "THE RUINS ARE FRAGILE", "These ruins are fragile", 0.74, WHITE, size=36)
    card(S, "DON'T CLIMB CARVED MONUMENTS", "Don't climb", 0.62, WHITE, size=36)
    card(S, "VIRUPAKSHA IS A LIVING TEMPLE", "living temple", 0.5, AMBER, size=36)
    S.caption("THE BOULDERS WILL LAST. THE CARVINGS MIGHT NOT.", S.c("The boulders will"), color=CYAN, size=38)


def s17_outro(S):
    landscape(S, 0.0, dim=0.7, rise=0.01)
    S.headline("HAMPI AT TRUE SCALE", 0.3, size=44)
    card(S, "≈ 2.5 BILLION YEARS to make the boulders", "two and a half", 0.8, GRANITE, size=34)
    card(S, "≈ 2 CENTURIES to build a great city", "two centuries", 0.71, AMBER, size=34)
    card(S, "6 MONTHS to destroy it", "six months", 0.62, PINK, size=34)
    S.text(0.5, 0.42, "LEGEND or GEOLOGY? Tell me below", S.c("Now tell me"), size=44, color=WHITE, box=True,
           pop=True)
    S.text(0.5, 0.28, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=44, color=AMBER, box=True, pop=True)
    S.fade_in_out(0, 1.0)


def hold(sid):
    return {"s01_hook": 0.6, "s07_exposed": 1.5, "s08_scale": 1.2, "s13_unesco": 0.8, "s17_outro": 1.5}.get(sid, 0.3)
