"""Scenes for 021 Meghalaya's living root bridges. S.c("phrase") is when the narrator says it.
Valleys, trees, roots and bridges are illustrations, not to scale. Pin positions are approximate."""
from engine.core import *
from engine.india import *
from matplotlib.patches import Polygon as MPoly, FancyBboxPatch, Rectangle, Ellipse, Circle as Circ

SHILLONG = (91.88, 25.57)
SOHRA = (91.73, 25.28)
MAWSYNRAM = (91.58, 25.30)
TYRNA = (91.69, 25.245)
PYNURSLA = (91.91, 25.30)
NE_VIEW = (91.5, mercy(25.6), 9.0)
MEG_VIEW = (91.3, mercy(25.5), 4.2)
SOHRA_VIEW = (91.72, mercy(25.42), 2.0)

LEAF, LEAF2, LEAF3 = "#2f6b3f", "#3f8a4f", "#1f4a2c"
ROOT, ROOT_E = "#a07850", "#5b4026"
WATER = "#3a8fc4"


# ------------------------------------------------------------------ helpers
def note(S, s, t0, x=0.88, y=0.035, size=18):
    S.text(x, y, s, t0, size=size, color=MUTED, ha="right", font=REG)


def card(S, text, t0, y=0.2, color=WHITE, t1=None, size=34, x=0.5, ha="center"):
    t0 = S.c(t0) if isinstance(t0, str) else t0
    t1 = S.c(t1) if isinstance(t1, str) else t1
    return S.text(x, y, text, t0, t1, size=size, color=color, box=True, ha=ha)


def fade(S, arts, t0, t1=None, peak=1.0, dur=0.4):
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / dur), ease((t1 - t) / dur)) * peak
        for x in arts:
            x.set_alpha(a)
    S.updaters.append(up)


def stage(S):
    S.ax.set_xlim(0, 16)
    S.ax.set_ylim(0, 9)
    S.brand()


def valley(S, dim=1.0, stream_y=2.2, gap=(5.2, 10.8)):
    """Illustrated forest gorge with a stream; banks at gap[0] and gap[1]. Not to scale."""
    stage(S)
    ax = S.ax
    for k in range(40):
        y = 9.0 * k / 40
        u = k / 40
        c = np.array([0.55, 0.68, 0.70]) * (1 - u) + np.array([0.05, 0.11, 0.17]) * u
        c = c * dim + (1 - dim) * np.array([0.03, 0.07, 0.11])
        ax.add_patch(Rectangle((0, y), 16, 9.0 / 40 + 0.01, fc=c, ec="none", zorder=0))
    rng = np.random.default_rng(3)
    # far misty hills
    xs = np.linspace(0, 16, 200)
    for i, (base, amp, col) in enumerate([(6.4, 0.7, "#4f7a6a"), (5.4, 0.9, "#3c6656")]):
        y = base + amp * np.sin(xs * (0.5 + 0.2 * i) + i * 2) + 0.25 * np.sin(xs * 2.1 + i)
        ax.fill_between(xs, 0, y, color=np.array(matplotlib.colors.to_rgb(col)) * dim, zorder=0.5 + i * 0.1)
    # left and right banks (steep forested slopes)
    l = [(0, 0), (0, 7.2), (2.5, 6.8), (4.2, 5.6), (gap[0], 4.3), (gap[0] + 0.5, stream_y), (gap[0] + 0.5, 0)]
    r = [(16, 0), (16, 7.4), (13.6, 7.0), (12.0, 5.8), (gap[1], 4.3), (gap[1] - 0.5, stream_y), (gap[1] - 0.5, 0)]
    for pts in (l, r):
        ax.add_patch(MPoly(pts, closed=True, fc=np.array(matplotlib.colors.to_rgb("#24442f")) * dim, ec="none",
                           zorder=1))
    # stream
    ax.add_patch(Rectangle((gap[0], 0), gap[1] - gap[0], stream_y, fc=np.array(matplotlib.colors.to_rgb(WATER)) * dim,
                           ec="none", zorder=0.9))
    for k in range(6):
        y = stream_y * (0.2 + 0.13 * k)
        ax.plot([gap[0] + 0.6 + rng.uniform(0, 1.5), gap[1] - 0.6 - rng.uniform(0, 1.5)], [y, y],
                color=np.array([0.75, 0.88, 0.95]) * dim, lw=1.5, alpha=0.5, zorder=0.95)
    # tree blobs on slopes
    for side in (0, 1):
        for k in range(16):
            if side == 0:
                x = rng.uniform(0.2, gap[0] - 0.3)
                ytop = np.interp(x, [0, 2.5, 4.2, gap[0]], [7.2, 6.8, 5.6, 4.3])
            else:
                x = rng.uniform(gap[1] + 0.3, 15.8)
                ytop = np.interp(x, [gap[1], 12.0, 13.6, 16], [4.3, 5.8, 7.0, 7.4])
            y = ytop - rng.uniform(0, 2.5)
            col = [LEAF, LEAF2, LEAF3][rng.integers(3)]
            ax.add_patch(Ellipse((x, y), rng.uniform(0.7, 1.3), rng.uniform(0.6, 1.0),
                                 fc=np.array(matplotlib.colors.to_rgb(col)) * dim, ec="none", zorder=1.2))


def fig_tree(S, x, y, t0=0.0, scale=1.0, dim=1.0):
    """Rubber fig on a bank: trunk, canopy, aerial roots hanging down. Illustration."""
    ax = S.ax
    arts = []
    arts.append(MPoly([(x - 0.25 * scale, y), (x + 0.25 * scale, y), (x + 0.15 * scale, y + 2.4 * scale),
                       (x - 0.15 * scale, y + 2.4 * scale)], closed=True, fc="#6e5236", ec=ROOT_E, lw=1.5, zorder=8))
    rng = np.random.default_rng(int(x * 10))
    for k in range(7):
        arts.append(Ellipse((x + rng.uniform(-1.3, 1.3) * scale, y + (2.6 + rng.uniform(0, 1.0)) * scale),
                            rng.uniform(1.1, 1.8) * scale, rng.uniform(0.8, 1.2) * scale,
                            fc=[LEAF, LEAF2, LEAF3][k % 3], ec="#1c3a24", lw=1, zorder=9))
    for p in arts:
        p.set_alpha(0)
        ax.add_patch(p)
    fade(S, arts, t0, peak=dim)
    lines = []
    for k in range(6):
        xx = x + (-1.0 + 0.4 * k) * scale
        ln, = ax.plot([xx, xx + rng.uniform(-0.05, 0.05)], [y + 2.4 * scale, y + 0.4 * scale], color=ROOT, lw=2,
                      zorder=7.5, alpha=0)
        lines.append(ln)
    fade(S, lines, t0 + 0.3, peak=dim)
    return arts


def roots_bridge(S, x0, x1, y, sag, t0, t1, n=14, seed=1, deck=True, color=ROOT, lw=3.0, z=10, fade_out=None):
    """A bundle of roots growing from x0 to x1 (left to right) with a sag; staggered between t0 and t1."""
    rng = np.random.default_rng(seed)
    u = np.linspace(0, 1, 80)
    lines = []
    for k in range(n):
        off = rng.uniform(-0.18, 0.18)
        wob = rng.uniform(0.02, 0.07)
        ph = rng.uniform(0, 6)
        xs = x0 + (x1 - x0) * u
        ys = y + off - sag * 4 * u * (1 - u) + wob * np.sin(u * 18 + ph)
        if k % 4 == 0:          # handrail roots, higher up
            ys = ys + 0.9 + rng.uniform(-0.05, 0.1)
        ln, = S.ax.plot([], [], color=color, lw=lw * rng.uniform(0.7, 1.3), zorder=z, solid_capstyle="round")
        ts = t0 + (t1 - t0) * 0.6 * k / max(n - 1, 1)
        lines.append((ln, xs, ys, ts))
    dur = (t1 - t0) * 0.4 + 0.01

    def up(t):
        a = 1.0 if fade_out is None else ease((fade_out - t) / 0.4)
        for ln, xs, ys, ts in lines:
            g = ease2((t - ts) / dur)
            m = int(g * len(xs))
            ln.set_data(xs[:m], ys[:m])
            ln.set_alpha(a)
    S.updaters.append(up)
    return lines


def bridge_scene(S, dim=1.0, t_grow=0.0, dur=0.01, decks=1):
    """Valley with a finished (or growing) root bridge."""
    valley(S, dim)
    fig_tree(S, 4.3, 4.6, 0.0, 0.9, dim)
    fig_tree(S, 11.7, 4.6, 0.0, 0.9, dim)
    roots_bridge(S, 4.6, 11.4, 4.5, 0.6, t_grow, t_grow + dur, n=16, seed=2, color=np.array([0.63, 0.47, 0.31]) * dim)
    if decks == 2:
        roots_bridge(S, 4.8, 11.2, 6.4, 0.45, t_grow, t_grow + dur, n=12, seed=5,
                     color=np.array([0.63, 0.47, 0.31]) * dim)


def rain_fx(S, t0, t1, n=70, color="#bfe3ff", seed=2):
    segs = LineCollection([], colors=color, linewidths=1.6, zorder=40, alpha=0)
    S.ax.add_collection(segs)
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0, 16, n)
    ph = rng.uniform(0, 1, n)
    sp = rng.uniform(0.8, 1.2, n)

    def up(t):
        a = min(ease((t - t0) / 0.5), ease((t1 - t) / 0.5))
        f = ((t - t0) * sp / 0.9 + ph) % 1.0
        ys = 9.5 - f * 10
        segs.set_segments([[(x - 0.08, y), (x, y - 0.45)] for x, y in zip(xs, ys)])
        segs.set_alpha(0.55 * a)
    S.updaters.append(up)


def meg_map(S, keys, t_hl=0.4, hl_peak=0.5):
    india(S, keys)
    S.highlight(ST["Meghalaya"], GREEN, t_hl, peak=hl_peak, lw=1.5)


def vbars(S, rows, t0, rect=(0.08, 0.14, 0.84, 0.6), ymax=None, unit="", dec=0, title=None, t1=None):
    """Vertical bars: rows of (label, value, color, t_appear)."""
    ax = S.fig.add_axes(rect)
    ax.set_axis_off()
    ymax = ymax or max(r[1] for r in rows) * 1.25
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylim(-ymax * 0.12, ymax)
    bg = FancyBboxPatch((-0.02, -0.04), 1.04, 1.08, transform=ax.transAxes, boxstyle="round,pad=0,rounding_size=0.03",
                        fc="#07111d", ec="none", alpha=0, clip_on=False, zorder=0)
    ax.add_patch(bg)
    tt = ax.text(0.5, 1.0, title or "", transform=ax.transAxes, fontproperties=BOLD, size=24, color=MUTED,
                 ha="center", va="top", alpha=0)
    arts = []
    for i, (lab, val, col, ta) in enumerate(rows):
        b = ax.bar(i, 0, width=0.62, color=col, zorder=2)[0]
        nm = ax.text(i, -ymax * 0.06, lab, fontproperties=BOLD, size=22, color=WHITE, ha="center", va="center",
                     alpha=0)
        num = ax.text(i, 0, "", fontproperties=BOLD, size=28, color=WHITE, ha="center", va="bottom", alpha=0)
        arts.append((b, val, nm, num, ta))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        fa = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        bg.set_alpha(0.85 * fa)
        tt.set_alpha(fa)
        for b, val, nm, num, ta in arts:
            g = ease2((t - ta) / 1.0)
            b.set_height(val * g)
            b.set_alpha(fa)
            nm.set_alpha(fa * ease((t - ta) / 0.3))
            num.set_text(f"{val * g:,.{dec}f}{unit}")
            num.set_position((num.get_position()[0], val * g + ymax * 0.01))
            num.set_alpha(fa * ease((t - ta) / 0.3))
    S.updaters.append(up)
    return ax


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    bridge_scene(S, dim=1.0, t_grow=0.2, dur=4.0)
    S.headline("THIS BRIDGE IS ALIVE", S.c("This bridge"), S.c("In the next"), size=56)
    card(S, "NO WOOD · NO STEEL · NO CONCRETE", "Nobody built", 0.76, WHITE, t1="In the next", size=36)
    card(S, "GROWN FROM A LIVING TREE", "It was grown", 0.66, GREEN, t1="In the next", size=40)
    card(S, "IT GETS STRONGER WITH AGE", "gets stronger", 0.56, AMBER, t1="In the next", size=40)
    card(S, "76 CATALOGUED IN ONE SURVEY", "seventy-six", 0.14, CYAN, t1="In the next", size=40)
    rows = [("How you grow a bridge", "how you grow"), ("Why anyone would bother", "why anyone"),
            ("The famous double-decker", "double-decker"), ("Why the world is watching", "whole world")]
    for i, (s, ph) in enumerate(rows):
        S.text(0.06, 0.8 - i * 0.1, f"{i + 1} · {s}", S.c(ph), size=36, ha="left", box=True)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    bridge_scene(S, dim=0.7)
    S.text(0.5, 0.72, "BRIDGES THAT GROW", 0.3, size=104, pop=True, box=True)
    S.text(0.5, 0.55, "MEGHALAYA'S LIVING ROOT BRIDGES", 0.8, size=46, color=GREEN, pop=True, box=True)
    S.text(0.5, 0.93, "TRUE SCALE", 0.0, size=28, color=CYAN)


def s03_where(S):
    t_z = S.c("Zoom in")
    meg_map(S, [(0, *INDIA_VIEW), (S.c("India's northeast"), *NE_VIEW), (t_z, *MEG_VIEW),
                (S.c("Sohra"), *SOHRA_VIEW), (S.T, 91.72, mercy(25.41), 1.9)])
    state_tag(S, "MEGHALAYA", S.c("Meghalaya"))
    S.highlight(["Bangladesh"], PINK, S.c("Bangladesh"), peak=0.35)
    pin(S, *SHILLONG, "SHILLONG (capital)", S.c("Shillong"), color=WHITE, dy=0.3, size=22)
    pin(S, *SOHRA, "SOHRA (Cherrapunji)", S.c("Sohra"), color=CYAN, dy=0.3, dx=4, size=22)
    pin(S, *MAWSYNRAM, "MAWSYNRAM", S.c("Mawsynram"), color=AMBER, dy=-2.0, dx=-3, size=22, ring=False)
    card(S, "SOHRA ≈ 55 km FROM SHILLONG", "fifty-five", 0.3, WHITE, t1="Mawsynram", size=32)
    card(S, "BANGLADESH", "Bangladesh", 0.2, PINK, t1="These two", size=36)
    S.caption("THE WETTEST PLACE ON EARTH?", S.c("These two"), color=AMBER, size=42)
    note(S, "Positions approximate · distance: Britannica", 0.5)


def s04_rain(S):
    valley(S, dim=0.45)
    rain_fx(S, 0.0, S.T + 1)
    S.headline("RAIN, MEASURED IN METRES", 0.3, size=44, color=CYAN)
    vbars(S, [("SOHRA\naverage year", 11.777, CYAN, S.c("Sohra averages")),
              ("MAWSYNRAM\naverage year", 11.873, AMBER, S.c("Mawsynram averages")),
              ("SOHRA\nAug 1860–Jul 1861", 26.461, PINK, S.c("Between August"))],
          0.6, rect=(0.12, 0.2, 0.5, 0.6), ymax=31, unit=" m", dec=1)
    card(S, "WORLD RECORD: 12 MONTHS", "Between August", 0.66, PINK, x=0.81, size=30)
    card(S, "JULY 1861: ≈ 9,300 mm", "July eighteen", 0.5, WHITE, x=0.81, size=32)
    card(S, "WORLD RECORD: ONE MONTH", "still the world", 0.41, AMBER, x=0.81, size=28)
    note(S, "Averages: Wikipedia (Cherrapunji); records: Guinness World Records, WMO. Britannica's average: ≈ 11.4 m",
         0.5, y=0.06, size=17)


def s05_problem(S):
    valley(S, dim=0.8)
    rain_fx(S, S.c("Every monsoon"), S.c("So the Khasi"))
    # a plank bridge that gets swept away
    t_rot = S.c("rot in the wet")
    planks = [Rectangle((5.6 + 0.5 * k, 4.2), 0.42, 0.18, fc="#8a6a45", ec="#4a3420", lw=1, zorder=10) for k in range(10)]
    for p in planks:
        S.ax.add_patch(p)
    base = [(p.get_x(), p.get_y()) for p in planks]

    def up(t):
        g = ease2((t - t_rot - 0.8) / 1.6)
        for k, p in enumerate(planks):
            x0, y0 = base[k]
            p.set_xy((x0 + g * (0.2 + 0.05 * k), y0 - g * (2.4 + 0.15 * (k % 3))))
            p.set_alpha(1 - g)
    S.updaters.append(up)
    S.headline("THE PROBLEM", 0.3, size=46, color=PINK)
    card(S, "MONSOON STREAMS BECOME TORRENTS", "torrents", 0.78, WHITE, size=34)
    card(S, "WOOD & BAMBOO: ROT, SWEPT AWAY", "rot in the wet", 0.68, PINK, size=34)
    card(S, "STEEL / CONCRETE: COSTLY · STEEL RUSTS", "Steel or concrete", 0.58, PINK, size=34)
    S.caption("THE KHASI AND JAINTIA SOLUTION: A MATERIAL THAT REPAIRS ITSELF", S.c("So the Khasi"), color=GREEN,
              size=32)
    note(S, "Source: Ludwig et al., Scientific Reports (2019)", 0.5, y=0.02)


def s06_tree(S):
    valley(S, dim=0.75, gap=(7.0, 15.5))
    fig_tree(S, 3.8, 3.8, 0.2, 1.3)
    S.headline("FICUS ELASTICA · THE RUBBER FIG", 0.3, size=44, color=GREEN)
    card(S, "AERIAL ROOTS GRIP SLOPES AND ROCK", "grip steep", 0.72, WHITE, x=0.68, size=32)
    # two roots fusing (inosculation) diagram, right side
    t_f = S.c("fuse into one")
    u = np.linspace(0, 1, 60)
    a, = S.ax.plot([], [], color=ROOT, lw=10, solid_capstyle="round", zorder=12)
    b, = S.ax.plot([], [], color=ROOT, lw=10, solid_capstyle="round", zorder=12)
    j = Circ((11.0, 2.2), 0.0, fc=AMBER, ec="none", zorder=13, alpha=0)
    S.ax.add_patch(j)

    def up(t):
        g = ease2((t - (t_f - 1.5)) / 1.5)
        xa = 8.6 + 2.4 * u * g
        ya = 1.2 + 1.0 * u * g
        xb = 13.4 - 2.4 * u * g
        yb = 1.2 + 1.0 * u * g
        a.set_data(xa, ya)
        b.set_data(xb, yb)
        h = ease((t - t_f) / 0.6)
        j.set_radius(0.35 * h)
        j.set_alpha(0.9 * h)
    S.updaters.append(up)
    card(S, "TWO ROOTS PRESS TOGETHER · FUSE INTO ONE", "fuse into one", 0.56, AMBER, x=0.68, size=30)
    card(S, "INOSCULATION", "inosculation", 0.47, CYAN, x=0.68, size=44)
    S.caption("ROOTS → A NETWORK → A NETWORK CAN CARRY WEIGHT".replace("→", ":"), S.c("Roots that fuse"),
              color=WHITE, size=34)
    note(S, "Sources: Wikipedia (Living root bridge); Ludwig et al. 2019", 0.5, y=0.02)


def s07_how(S):
    valley(S, dim=0.85)
    t_plant = S.c("Plant a fig")
    fig_tree(S, 4.3, 4.6, t_plant, 0.9)
    # areca trunk guide + bamboo frame
    t_g = S.c("guide them across")
    guide = Rectangle((4.7, 4.35), 6.5, 0.3, fc="#c9b48a", ec="#6b5a3a", lw=1.5, zorder=9, alpha=0)
    S.ax.add_patch(guide)
    frame = [S.ax.plot([5.0 + 0.8 * k, 5.0 + 0.8 * k], [4.3, 3.0], color="#d8c690", lw=3, zorder=8.5, alpha=0)[0]
             for k in range(8)]
    t_rot = S.c("scaffolding can rot")
    fade(S, [guide] + frame, S.c("hollowed trunks"), t_rot + 1.0)
    roots_bridge(S, 4.6, 11.4, 4.5, 0.6, t_g, S.c("Then do it again") + 3.0, n=16, seed=2)
    fig_tree(S, 11.7, 4.6, S.c("far bank"), 0.9)
    steps = [("1 · PLANT A FIG ON ONE BANK", "Plant a fig"), ("2 · GUIDE ITS ROOTS ACROSS", "guide them across"),
             ("   (hollow areca trunks or a bamboo frame)", "hollowed trunks"),
             ("3 · PLANT THEM IN THE FAR BANK", "far bank"), ("4 · REPEAT · TIE · TWIST · LET THEM FUSE", "Then do it again"),
             ("5 · SCAFFOLD GOES · ROOTS STAY", "scaffolding can rot")]
    for i, (s, ph) in enumerate(steps):
        S.text(0.04, 0.42 - i * 0.07, s, S.c(ph), size=28, ha="left", box=True)
    note(S, "Illustration, not to scale · Sources: Wikipedia; Ludwig et al. 2019", 0.5, y=0.02)


def s08_time(S):
    valley(S, dim=0.45)
    S.headline("HOW LONG TO GROW ONE?", 0.3, size=46, color=AMBER)
    S.bars([("Shortest estimate (Wikipedia, Cherrapunji)", 10, GREEN, S.c("about ten")),
            ("Longer estimate (UNDP)", 25, AMBER, S.c("twenty-five years")),
            ("Bridge #50: still not fully functional", 66, PINK, S.c("sixty-six"))],
           0.6, rect=(0.1, 0.3, 0.62, 0.42), xmax=80, unit="yrs", dec=0)
    card(S, "BUILT OVER DECADES, SOMETIMES GENERATIONS", "over generations", 0.16, WHITE, size=34)
    note(S, "Ludwig et al., Scientific Reports (2019) · estimates vary by source", 0.5, y=0.06)


def s09_stronger(S):
    bridge_scene(S, dim=0.65)
    S.headline("STRONGER WITH AGE", 0.3, size=48, color=GREEN)
    # thickening root cross-section
    t_th = S.c("thicken")
    c = Circ((14.4, 3.4), 0.2, fc=ROOT, ec=ROOT_E, lw=2, zorder=20, alpha=0)
    S.ax.add_patch(c)

    def up(t):
        g = ease2((t - t_th) / 2.5)
        c.set_radius(0.2 + 0.55 * g)
        c.set_alpha(ease((t - t_th + 0.3) / 0.4))
    S.updaters.append(up)
    card(S, "ROOTS UNDER LOAD THICKEN", "thicken", 0.55, WHITE, x=0.84, size=24)
    card(S, "JOINTS FUSE AND HARDEN", "Joints fuse", 0.78, WHITE, size=34)
    card(S, "≈ 50+ PEOPLE AT ONCE (reported)", "fifty or more", 0.14, AMBER, size=40, t1="The researchers")
    card(S, "'the only known example of repeated, predictable use of tree growth for structural purposes'",
         "The researchers", 0.14, CYAN, size=26, t1="Ages are rough")
    card(S, "AGES: ROUGH ESTIMATES · SOME SEVERAL HUNDRED YEARS", "Ages are rough", 0.14, WHITE, size=32)
    note(S, "Ludwig et al. 2019 · load figure: Wikipedia", 0.5, y=0.02)


def s10_count(S):
    t_z = S.c("Most are short")
    meg_map(S, [(0, *MEG_VIEW), (S.T, *MEG_VIEW)], hl_peak=0.45)
    S.headline("76 BRIDGES IN THE 2019 SURVEY", 0.3, size=44, color=GREEN)
    S.bars([("Under 20 m", 58, GREEN, S.c("fifty-eight")), ("20 m or longer", 15, AMBER, S.c("fifty-two point"))],
           t_z, rect=(0.08, 0.5, 0.4, 0.22), xmax=75, unit="", dec=0, title="73 measured lengths")
    card(S, "LENGTHS: ≈ 2 m TO 52.7 m", "fifty-two point", 0.38, WHITE, x=0.28, size=32)
    pin(S, *PYNURSLA, "LONGEST: > 50 m, near RANGTHYLLIANG", S.c("Rangthylliang"), color=AMBER, dy=0.15, size=20)
    card(S, "FOUND FROM ≈ 50 m TO ≈ 1,200 m ABOVE SEA LEVEL", "fifty metres above", 0.12, CYAN, size=32)
    note(S, "Ludwig et al. 2019 (58 of 73 measured lengths under 20 m) · longest bridge: Wikipedia · pin approximate",
         0.5, y=0.035, size=16)


def s11_double(S):
    bridge_scene(S, dim=0.9, t_grow=0.2, dur=3.0, decks=2)
    S.headline("THE DOUBLE-DECKER · NONGRIAT", 0.3, size=46, color=AMBER)
    card(S, "UPPER DECK ≈ 18 m", "eighteen metres", 0.8, WHITE, x=0.5, size=30)
    card(S, "LOWER DECK ≈ 24 m", "twenty-four", 0.3, WHITE, x=0.5, size=30)
    card(S, "UPPER LEVEL ADDED AFTER FLOODS", "after floods", 0.14, CYAN, size=34, t1="often said")
    card(S, "OFTEN SAID ≈ 200 YEARS OLD (estimate)", "often said", 0.14, AMBER, size=34)
    note(S, "Illustration · decks 80 ft and 60 ft per Smithsonian; age estimate: Wikipedia, Smithsonian", 0.5,
         y=0.02)


def s12_who(S):
    valley(S, dim=0.4)
    S.headline("WHO LOOKS AFTER THEM?", 0.3, size=46, color=WHITE)
    vbars(S, [("VILLAGE", 25, GREEN, S.c("Twenty-five")), ("FAMILY /\nPERSON", 12, CYAN, S.c("Twelve")),
              ("GROUP OF\nVILLAGES", 8, VIOLET, S.c("Eight")), ("UNKNOWN", 14, MUTED, S.c("Fourteen")),
              ("NOBODY", 16, PINK, S.c("sixteen"))],
          0.6, rect=(0.1, 0.2, 0.8, 0.58), ymax=30, dec=0, title="75 bridges by caretaker (2019 survey)")
    S.caption("A LIVING BRIDGE NEEDS LIVING PEOPLE", S.c("A living bridge"), color=AMBER, size=40)
    note(S, "Ludwig et al., Scientific Reports (2019)", 0.5, y=0.02)


def s13_threats(S):
    bridge_scene(S, dim=0.5)
    S.headline("THE DANGER", 0.3, size=48, color=PINK)
    card(S, "FLOODS · FIRES · LANDSLIDES", "Floods", 0.76, WHITE, size=38)
    card(S, "NEGLECT: DECAY, OR GROWN WILD", "Without care", 0.66, WHITE, size=36)
    card(S, "CONCRETE ROADS: LESS REASON TO TEND THEM", "concrete roads", 0.56, AMBER, size=34)
    card(S, "CONCRETE ADDED TO AT LEAST ONE BRIDGE", "concrete has even", 0.46, PINK, size=34)
    S.caption("DECADES TO GROW · A FEW SEASONS TO LOSE", S.c("A bridge that took"), color=CYAN, size=40)
    note(S, "Sources: Ludwig et al. 2019; Wikipedia; UNDP India", 0.5, y=0.02)


def s14_unesco(S):
    meg_map(S, [(0, *MEG_VIEW), (S.T, 91.6, mercy(25.45), 3.2)], hl_peak=0.6)
    S.headline("WHY IT MATTERS NOW", 0.3, size=46, color=AMBER)
    S.text(0.04, 0.76, "FEB 2022 · UNESCO tentative list", S.c("In February"), size=34, ha="left", box=True)
    S.text(0.04, 0.68, "'Jingkieng Jri: Living Root Bridge Cultural Landscapes'", S.c("Jingkieng"), size=26,
           ha="left", color=GREEN, box=True)
    S.text(0.04, 0.56, "JAN 2026 · full nomination submitted", S.c("In January"), size=34, ha="left", box=True,
           color=AMBER)
    S.text(0.04, 0.48, "for the 2026-27 evaluation cycle", S.c("evaluation cycle"), size=28, ha="left", box=True)
    S.text(0.04, 0.36, "MORE THAN 75 VILLAGES", S.c("more than seventy-five"), size=34, ha="left", box=True,
           color=CYAN)
    S.caption("IF APPROVED: WORLD HERITAGE", S.c("If it is approved"), color=GREEN, size=42)
    note(S, "Sources: UNESCO World Heritage Centre (tentative list ref. 6606); All India Radio News, 29 Jan 2026",
         0.5, y=0.02, size=16)


def s15_visit(S):
    meg_map(S, [(0, *MEG_VIEW), (S.c("From Sohra"), 91.72, mercy(25.33), 1.4), (S.T, 91.72, mercy(25.33), 1.3)],
            hl_peak=0.3)
    S.headline("HOW TO SEE ONE", 0.3, size=44, color=GREEN)
    card(S, "BEST: OCTOBER TO MARCH (dry season)", "October to March", 0.8, GREEN, size=34)
    pin(S, *SOHRA, "SOHRA", S.c("From Sohra"), color=CYAN, dy=0.8, size=22)
    pin(S, *TYRNA, "TYRNA ≈ 12-15 km from Sohra", S.c("Tyrna"), color=AMBER, dy=-0.5, dx=-7, size=22, ring=False)
    card(S, "≈ 3,000-3,500 STEPS DOWN (counts vary)", "thousands of stone", 0.3, WHITE, size=32)
    card(S, "≈ 2 HOURS EACH WAY", "two hours each", 0.21, WHITE, size=32)
    card(S, "+ RAINBOW FALLS · HOMESTAYS IN NONGRIAT", "Rainbow Falls", 0.12, CYAN, size=32)
    note(S, "Sources: Meghalaya Tourism; Lonely Planet; Smithsonian · positions approximate", 0.5, y=0.02, size=16)


def s16_caveat(S):
    bridge_scene(S, dim=0.55)
    S.headline("BEFORE YOU GO", 0.3, size=46, color=PINK)
    card(S, "A STEEP CLIMB BACK UP", "climb back up", 0.74, WHITE, size=36)
    card(S, "MONSOON: HEAVY RAIN + LANDSLIDES", "landslides", 0.64, AMBER, size=36)
    card(S, "STAY ON THE PATH · FOLLOW LOCAL RULES", "Stick to the path", 0.54, WHITE, size=36)
    card(S, "VILLAGE FEES HELP KEEP THEM ALIVE", "pay the small", 0.44, GREEN, size=36)


def s17_outro(S):
    bridge_scene(S, dim=0.75)
    S.headline("A ROOT BRIDGE AT TRUE SCALE", 0.3, size=44)
    card(S, "≈ 10-25 YEARS to grow", "Ten to twenty-five", 0.8, GREEN, size=34)
    card(S, "HUNDREDS OF YEARS of use", "Hundreds of years", 0.71, AMBER, size=34)
    card(S, "76 COUNTED · EVERY ONE NEEDS ITS PEOPLE", "Seventy-six bridges", 0.62, CYAN, size=34)
    S.text(0.5, 0.42, "WOULD YOU CROSS A LIVING BRIDGE?", S.c("Would you trust"), size=44, color=WHITE, box=True,
           pop=True)
    S.text(0.5, 0.28, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=44, color=AMBER, box=True, pop=True)
    S.fade_in_out(0, 1.0)


def hold(sid):
    return {"s01_hook": 0.8, "s02_title": 0.6, "s04_rain": 2.0, "s07_how": 2.5, "s09_stronger": 1.5,
            "s10_count": 1.5, "s11_double": 2.0, "s12_who": 2.0, "s14_unesco": 1.5, "s17_outro": 2.0}.get(sid, 1.0)
