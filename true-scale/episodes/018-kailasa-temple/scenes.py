"""018 Kailasa: the temple carved from one rock. Each function takes the Scene S; S.c("phrase") is when the
narrator says it. Temple drawings are schematic (overall courtyard 82 x 46 m and tower height 32.6 m are to scale;
internal layout simplified). Pin coordinates approximate."""
from engine.core import *
from engine.india import *
from engine.timeline import TL, setup as tl_setup
from matplotlib.patches import Polygon as MPoly, Rectangle as Rect, Circle as Circ, FancyBboxPatch as FBP

ROCK, ROCK2, STRATA = "#3a4659", "#2e394a", "#4b5a70"
STONE, STONE_E, STONE_D = "#b9ab92", "#efe6d2", "#8f826b"

ELLORA = (75.178, 20.025)
CSN = (75.343, 19.877)          # Chhatrapati Sambhajinagar
AJANTA = (75.700, 20.552)
MAHA_VIEW = (75.6, mercy(19.9), 7.5)

COURT_W, COURT_D, TOWER_H = 82.0, 46.0, 32.6
PAR_W, PAR_D, PAR_COL = 69.5, 30.9, 10.4


# ------------------------------------------------------------------ helpers
def note(S, s, t0, x=0.015, y=0.03, size=18, t1=None):
    S.text(0.015, 0.03, s, t0, t1, size=size, color=MUTED, ha="left", font=REG)


def fader(S, arts, t0, t1=None, peak=1.0, fade=0.4):
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / fade), ease((t1 - t) / fade)) * peak
        for x in arts:
            x.set_alpha(a)
    S.updaters.append(up)


def view(S, x0, x1, y0):
    """Diagram mode: data units in metres, 16:9 window starting at (x0, y0)."""
    S.ax.set_xlim(x0, x1)
    S.ax.set_ylim(y0, y0 + (x1 - x0) * H / W)


def tower_poly(x0, x1, base, top, steps=6):
    """Stepped Dravidian-style tower (vimana) outline, schematic."""
    pts = [(x0, base)]
    h = (top - base) * 0.86
    for i in range(steps):
        y = base + h * i / steps
        y1 = base + h * (i + 1) / steps
        inset = (x1 - x0) * 0.32 * (i + 1) / steps
        pts += [(x0 + inset - (x1 - x0) * 0.32 / steps, y1 - 0.4), (x0 + inset, y1 - 0.4)] if i else \
               [(x0, y1 - 0.4), (x0 + inset, y1 - 0.4)]
    xm = (x0 + x1) / 2
    w = (x1 - x0) * 0.36
    pts += [(xm - w / 2, base + h)]
    # dome cap
    for a in np.linspace(np.pi, 0, 14):
        pts.append((xm + w / 2 * np.cos(a), base + h + (top - base - h) * np.sin(a)))
    pts += [(xm + w / 2, base + h)]
    right = [(x1 - (px - x0), py) for px, py in pts[::-1]]
    return pts + right[1:]


def elevation(S, z=4, t0=0.0, alpha=1.0):
    """Side elevation of the Kailasa court, schematic. Ground y=0, courtyard x 0..82. Returns artists."""
    arts = []
    def add(p):
        S.ax.add_patch(p)
        arts.append(p)
        return p
    # gateway
    add(MPoly([(3, 0), (13, 0), (13, 9), (11.5, 11), (4.5, 11), (3, 9)], fc=STONE_D, ec=STONE_E, lw=1.2, zorder=z))
    # nandi mandapa
    add(MPoly([(20, 0), (29, 0), (29, 9), (28, 12.5), (21, 12.5), (20, 9)], fc=STONE, ec=STONE_E, lw=1.2, zorder=z))
    # bridge
    add(Rect((29, 7.5), 6, 1.6, fc=STONE_D, ec=STONE_E, lw=1.0, zorder=z))
    # two pillars
    for x in (16.0, 17.6):
        add(Rect((x, 0), 0.9, 14, fc=STONE_D, ec=STONE_E, lw=0.8, zorder=z - 0.1))
    # main body: plinth with elephant band, hall, tower
    add(Rect((35, 0), 33, 8, fc=STONE_D, ec=STONE_E, lw=1.2, zorder=z))
    for k in range(9):
        add(MPoly([(36 + k * 3.6, 0.6), (38.6 + k * 3.6, 0.6), (38.6 + k * 3.6, 3.6), (37.3 + k * 3.6, 4.6),
                   (36 + k * 3.6, 3.6)], fc="#a39377", ec=STONE_E, lw=0.6, zorder=z + 0.1))
    add(Rect((35, 8), 14, 8, fc=STONE, ec=STONE_E, lw=1.2, zorder=z))
    add(MPoly(tower_poly(48, 67, 8, TOWER_H), fc=STONE, ec=STONE_E, lw=1.2, zorder=z))
    # gallery at the back
    add(Rect((74, 0), 8, 12, fc=STONE_D, ec=STONE_E, lw=1.0, zorder=z))
    for k in range(3):
        add(Rect((74.8, 0.8 + k * 3.8), 6.4, 2.6, fc=ROCK2, ec="none", zorder=z + 0.1))
    for a in arts:
        a.set_alpha(0)
    fader(S, arts, t0, peak=alpha)
    return arts


def hillside(S, top=36.0, pit_level=None):
    """Basalt around the court. pit_level(t) = height of the rock still filling the pit (None: pit empty)."""
    S.ax.add_patch(Rect((-200, -60), 500, 60, fc=ROCK, ec="none", zorder=2))
    for xa, xb in ((-200, 0), (COURT_W, 300)):
        S.ax.add_patch(Rect((xa, 0), xb - xa, top, fc=ROCK, ec="none", zorder=2))
    for y in np.arange(-56, top, 5.5):            # lava-flow layers
        S.ax.plot([-200, 0], [y, y], color=STRATA, lw=1.2, zorder=2.1)
        S.ax.plot([COURT_W, 300], [y, y], color=STRATA, lw=1.2, zorder=2.1)
        if y < 0:
            S.ax.plot([0, COURT_W], [y, y], color=STRATA, lw=1.2, zorder=2.1)
    if pit_level is not None:
        r = Rect((-0.8, -0.8), COURT_W + 1.6, top, fc=ROCK, ec="none", zorder=6)
        S.ax.add_patch(r)
        lines = [S.ax.plot([0, COURT_W], [y, y], color=STRATA, lw=1.2, zorder=6.1)[0]
                 for y in np.arange(-56, top, 5.5) if y > 0]
        ys = [y for y in np.arange(-56, top, 5.5) if y > 0]
        cut = S.ax.plot([0, COURT_W], [top, top], color=AMBER, lw=4, zorder=6.2, alpha=0)[0]

        def up(t):
            lv = pit_level(t)
            r.set_height(lv + 0.8 if lv > 0.05 else 0)
            for ln, y in zip(lines, ys):
                ln.set_visible(y < lv)
            cut.set_ydata([lv, lv])
            cut.set_alpha(0.9 if 0.2 < lv < top - 0.2 else 0)
        S.updaters.append(up)


def sky(S):
    S.ax.set_facecolor(OCEAN)


def ground_label(S, s, x, y, t0, size=22, color=WHITE, t1=None, ha="center"):
    a = S.ax.text(x, y, s, fontproperties=BOLD, size=size, color=color, ha=ha, va="center", zorder=30, alpha=0,
                  bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        k = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        a.set_alpha(k)
        a.get_bbox_patch().set_alpha(0.8 * k)
    S.updaters.append(up)
    return a


def dim_h(S, x0, x1, y, lab, t0, color=AMBER, dy=1.2, size=28, t1=None):
    ln, = S.ax.plot([x0, x0], [y, y], color=color, lw=3, zorder=20, alpha=0)
    ends = [S.ax.plot([x, x], [y - 1, y + 1], color=color, lw=3, zorder=20, alpha=0)[0] for x in (x0, x1)]
    tx = S.ax.text((x0 + x1) / 2, y + dy, lab, fontproperties=BOLD, size=size, color=color, ha="center",
                   va="bottom", zorder=21, alpha=0)
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        k = min(ease((t - t0) / 0.3), ease((t1 - t) / 0.3))
        g = ease2((t - t0) / 0.9)
        ln.set_data([x0, x0 + (x1 - x0) * g], [y, y])
        ln.set_alpha(k)
        ends[0].set_alpha(k)
        ends[1].set_alpha(k * (g > 0.98))
        tx.set_alpha(k * ease((t - t0 - 0.5) / 0.4))
    S.updaters.append(up)


def dim_v(S, x, y0, y1, lab, t0, color=CYAN, size=28, dx=1.2, ha="left", t1=None):
    ln, = S.ax.plot([x, x], [y0, y0], color=color, lw=3, zorder=20, alpha=0)
    ends = [S.ax.plot([x - 0.8, x + 0.8], [y, y], color=color, lw=3, zorder=20, alpha=0)[0] for y in (y0, y1)]
    tx = S.ax.text(x + dx, (y0 + y1) / 2, lab, fontproperties=BOLD, size=size, color=color, ha=ha, va="center",
                   zorder=21, alpha=0, bbox=dict(boxstyle="round,pad=0.25", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        k = min(ease((t - t0) / 0.3), ease((t1 - t) / 0.3))
        g = ease2((t - t0) / 0.9)
        ln.set_data([x, x], [y0, y0 + (y1 - y0) * g])
        ln.set_alpha(k)
        ends[0].set_alpha(k)
        ends[1].set_alpha(k * (g > 0.98))
        tx.set_alpha(k * ease((t - t0 - 0.5) / 0.4))
        tx.get_bbox_patch().set_alpha(0.7 * k * ease((t - t0 - 0.5) / 0.4))
    S.updaters.append(up)


def court_scene(S, t_reveal=None, dur=6.0, xw=(-38, 120), y0=-22):
    """Elevation of the hill + temple; if t_reveal is given, the rock is removed top-down from t_reveal."""
    view(S, xw[0], xw[1], y0)
    if t_reveal is None:
        hillside(S)
    else:
        hillside(S, pit_level=lambda t: 36 * (1 - ease2((t - t_reveal) / dur)))
    elevation(S, t0=0.0)
    S.brand()


def plan_base(S, xw=(-39, 121), y0=-22):
    view(S, xw[0], xw[1], y0)
    S.ax.add_patch(Rect((-200, -100), 500, 300, fc=ROCK, ec="none", zorder=1))
    S.brand()


def court_plan(S, t0, z=3):
    """Plan of the cut-out court (light floor) with simplified layout. Front (gateway) on the left."""
    arts = []
    def add(p):
        S.ax.add_patch(p)
        arts.append(p)
        return p
    add(Rect((0, 0), COURT_W, COURT_D, fc="#56657b", ec=STONE_E, lw=2, zorder=z))
    # gallery along back and sides
    add(Rect((76, 0), 6, COURT_D, fc=STONE_D, ec=STONE_E, lw=1, zorder=z + 0.1))
    add(Rect((30, 0), 46, 4, fc=STONE_D, ec=STONE_E, lw=1, zorder=z + 0.1))
    add(Rect((30, 42), 46, 4, fc=STONE_D, ec=STONE_E, lw=1, zorder=z + 0.1))
    return arts


PLAN = {
    "gate": [(-2, 17), (6, 17), (6, 29), (-2, 29)],
    "nandi": [(15, 19), (24, 19), (24, 27), (15, 27)],
    "bridge": [(24, 21.6), (31, 21.6), (31, 24.4), (24, 24.4)],
    "hall": [(31, 12), (50, 12), (50, 34), (31, 34)],
    "tower": [(50, 14), (68, 14), (68, 32), (50, 32)],
}


def plan_temple(S, t0, which=None, z=4, color=STONE):
    arts = []
    for k, pts in PLAN.items():
        if which and k not in which:
            continue
        p = MPoly(pts, fc=color, ec=STONE_E, lw=1.4, zorder=z + (0.2 if k == "bridge" else 0))
        S.ax.add_patch(p)
        arts.append(p)
    for a in arts:
        a.set_alpha(0)
    fader(S, arts, t0)
    return arts


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    t_rev = S.c("Workers started")
    court_scene(S, t_reveal=t_rev, dur=S.c("This is Kailasa") - t_rev - 0.5)
    S.headline("≈ 200,000 TONNES OF ROCK REMOVED", 0.5, S.c("Nothing here"), size=50, color=AMBER)
    S.headline("NOTHING BUILT. NOTHING CARRIED IN.", S.c("Nothing here"), t_rev, size=46)
    S.headline("CARVED FROM THE TOP DOWN", t_rev, S.c("This is Kailasa"), size=50, color=CYAN)
    S.headline("KAILASA · ELLORA · 1,200+ YEARS OLD", S.c("This is Kailasa"), size=46, color=AMBER)
    note(S, "Schematic side view: court length and tower height to scale", 0.6, y=0.035, x=0.86)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    court_scene(S)
    S.text(0.5, 0.82, "KAILASA", 0.2, size=120, pop=True, box=True)
    S.text(0.5, 0.68, "THE TEMPLE CARVED FROM ONE ROCK", 0.6, size=48, color=AMBER, pop=True, box=True)


def s03_where(S):
    t_z = S.c("Ellora sits")
    india(S, [(0, *INDIA_VIEW), (t_z + 0.3, *MAHA_VIEW), (S.c("Ajanta") , *MAHA_VIEW),
              (S.T, 75.5, mercy(20.2), 4.6)], hl=["Maharashtra"], t_hl=t_z)
    state_tag(S, "MAHARASHTRA", t_z + 0.3)
    pin(S, *ELLORA, "ELLORA", t_z + 1.0, color=AMBER, dy=1.2)
    pin(S, *CSN, "CHHATRAPATI SAMBHAJINAGAR", S.c("Chhatrapati"), color=CYAN, dy=-2.2, size=22, ring=False)
    S.text(0.5, 0.2, "≈ 30 km northwest of Chhatrapati Sambhajinagar (formerly Aurangabad)", S.c("about thirty"),
           S.c("The famous"), size=32, box=True)
    pin(S, *AJANTA, "AJANTA", S.c("Ajanta"), color=PINK, dy=1.2, size=24)
    S.text(0.5, 0.2, "Ajanta's painted caves: ≈ 100 km away", S.c("about a hundred"), S.c("But Ellora"), size=34,
           box=True, color=PINK)
    S.text(0.5, 0.2, "Not one monument: a whole cliff of them", S.c("But Ellora"), size=36, box=True, color=AMBER)


def s04_ellora(S):
    view(S, 0, 160, 0)
    S.ax.add_patch(Rect((0, 0), 160, 50, fc=ROCK, ec="none", zorder=1))
    for y in np.arange(4, 50, 5.5):
        S.ax.plot([0, 160], [y, y], color=STRATA, lw=1.2, zorder=1.1)
    S.ax.add_patch(Rect((0, 0), 160, 14, fc="#25303f", ec="none", zorder=1.2))
    t_n = S.c("Twelve are Buddhist")
    groups = [(range(1, 13), CYAN, S.c("Twelve are Buddhist")), (range(13, 30), AMBER, S.c("seventeen are Hindu")),
              (range(30, 35), GREEN, S.c("five are Jain"))]
    x0, step = 8, 4.3
    t_first = S.c("Thirty-four caves")
    for rng_, col, tc in groups:
        for n in rng_:
            x = x0 + (n - 1) * step
            # door appears at the overall count, colour at group cue
            r = MPoly([(x, 14), (x + 3.2, 14), (x + 3.2, 19), (x + 1.6, 21), (x, 19)], fc="#07111d", ec=MUTED,
                      lw=1.2, zorder=3, alpha=0)
            S.ax.add_patch(r)
            lab = S.ax.text(x + 1.6, 11.5, str(n), fontproperties=BOLD, size=15, color=MUTED, ha="center",
                            va="center", zorder=4, alpha=0)
            ta = t_first + 0.04 * n
            cc = np.array(matplotlib.colors.to_rgb(col))

            def up(t, r=r, lab=lab, ta=ta, tc=tc, cc=cc, n=n):
                a = ease((t - ta) / 0.3)
                r.set_alpha(a)
                lab.set_alpha(a)
                g = ease((t - tc) / 0.5)
                base = np.array(matplotlib.colors.to_rgb("#07111d"))
                r.set_facecolor(tuple(base + (cc - base) * g))
                if n == 16:
                    k = ease((t - S.c("numbered Cave")) / 0.4)
                    r.set_linewidth(1.2 + 4 * k)
                    r.set_edgecolor(WHITE if k > 0.5 else MUTED)
                    lab.set_color(WHITE if k > 0.5 else MUTED)
                    lab.set_fontsize(15 + 9 * k)
            S.updaters.append(up)
    dim_h(S, x0, x0 + 33 * step + 3.2, 26, "MORE THAN 2 km OF CLIFF (not to scale)", S.c("stretches"), color=WHITE,
          size=24)
    S.headline("34 CAVES OPEN TO VISITORS", t_first, t_n, size=48)
    S.headline("12 BUDDHIST · 17 HINDU · 5 JAIN", t_n, S.c("carved between"), size=46)
    S.headline("CARVED c. AD 600 – 1000", S.c("carved between"), S.c("UNESCO"), size=48, color=AMBER)
    S.headline("UNESCO WORLD HERITAGE SITE · 1983", S.c("UNESCO"), S.c("And right"), size=46, color=CYAN)
    S.headline("CAVE 16: KAILASA", S.c("And right"), size=56, color=AMBER)
    for lab_, col, xx in (("BUDDHIST", CYAN, x0 + 5.5 * step), ("HINDU", AMBER, x0 + 20.5 * step),
                          ("JAIN", GREEN, x0 + 31.5 * step)):
        ground_label(S, lab_, xx + 1.6, 5, S.c({CYAN: "Twelve are Buddhist", AMBER: "seventeen are Hindu",
                                                GREEN: "five are Jain"}[col]), color=col, size=24)
    note(S, "Cave doors schematic, numbered as at the site", t_first, y=0.035)
    S.brand()


def s05_rock(S):
    view(S, 0, 160, 0)
    cols = ["#2b3546", "#334055", "#2a3343", "#3a4659", "#2e394a", "#36435a", "#2b3546", "#3c4a60"]
    ys = np.cumsum([0, 9, 12, 8, 13, 10, 11, 9, 18])
    t_l = S.c("layer upon layer")
    for i, (a, b) in enumerate(zip(ys, ys[1:])):
        r = Rect((0, a), 160, b - a, fc=cols[i % len(cols)], ec=STRATA, lw=1.4, zorder=1, alpha=0)
        S.ax.add_patch(r)
        ta = t_l + 0.25 * i

        def up(t, r=r, ta=ta):
            r.set_alpha(max(0.35, ease((t - ta) / 0.4)))
        S.updaters.append(up)
    S.headline("BASALT · DECCAN TRAPS", 0.4, S.c("Basalt is hard"), size=52, color=AMBER)
    S.text(0.5, 0.74, "Charanandri hills: old lava flows, layer on layer", S.c("Charanandri"), S.c("Basalt is hard"),
           size=34, box=True)
    S.headline("HARD. HEAVY. UNFORGIVING.", S.c("Basalt is hard"), S.c("Every cut"), size=50, color=WHITE)
    S.headline("NO SECOND CHANCES", S.c("Every cut"), size=58, color=PINK)
    # a chisel line
    t_c = S.c("Every cut")
    ln, = S.ax.plot([], [], color=AMBER, lw=5, zorder=5, solid_capstyle="round")

    def up(t):
        g = ease2((t - t_c) / 1.4)
        ln.set_data([30, 30 + 100 * g], [40, 40])
    S.updaters.append(up)
    S.brand()


def s06_method(S):
    plan_base(S)
    t_tr = S.c("First, three")
    t_dn = S.c("Then the carvers")
    t_left = S.c("What looks like")
    floor = Rect((0, 0), COURT_W, COURT_D, fc="#56657b", ec="none", zorder=2, alpha=0)
    S.ax.add_patch(floor)
    trenches = [((72, 0), 10, COURT_D), ((0, 0), 72, 6), ((0, 40), 72, 6)]
    tr_art = []
    for (xy, w, h) in trenches:
        r = Rect(xy, 0 if w > h else w, h if w > h else 0, fc="#07111d", ec=AMBER, lw=2, zorder=3, alpha=0)
        S.ax.add_patch(r)
        tr_art.append((r, w, h))
    outline = Rect((0, 0), COURT_W, COURT_D, fc="none", ec=WHITE, lw=2, ls=(0, (6, 4)), zorder=3.5, alpha=0)
    S.ax.add_patch(outline)
    fader(S, [outline], 0.5, t_tr + 2.5, peak=0.8)
    ground_label(S, "SOLID BASALT HILL (seen from above)", 41, 38, 0.5, color=WHITE, size=28, t1=t_tr)
    # the old way: a cave cut in from the front
    cave = Rect((0, 17), 0, 12, fc="#07111d", ec=MUTED, lw=2, zorder=3.4, alpha=0)
    S.ax.add_patch(cave)
    t_old = S.c("Most earlier")
    t_new = S.c("Kailasa was carved")

    def upc(t):
        cave.set_width(28 * ease2((t - t_old - 0.5) / 2.0))
        cave.set_alpha(min(ease((t - t_old) / 0.3), ease((t_new + 0.6 - t) / 0.4)))
    S.updaters.append(upc)
    block = Rect((0, 6), 72, 34, fc="#4f5e75", ec=STONE_E, lw=2, zorder=3, alpha=0)
    S.ax.add_patch(block)

    def up(t):
        for i, (r, w, h) in enumerate(tr_art):
            g = ease2((t - t_tr - 0.6 * i) / 1.4)
            a = ease((t - t_tr - 0.6 * i) / 0.3)
            if w > h:
                r.set_width(w * g)
            else:
                r.set_height(h * g)
            r.set_alpha(a)
        block.set_alpha(ease((t - t_tr - 2.0) / 0.5) * (1 - 0.7 * ease((t - t_dn - 1.5) / 1.5)))
    S.updaters.append(up)
    plan_temple(S, t_dn + 1.0)
    S.headline("EARLIER: DUG INWARDS FROM THE FRONT", S.c("Most earlier"), S.c("Kailasa was carved"), size=44)
    S.headline("KAILASA: FROM THE TOP DOWN", S.c("Kailasa was carved"), t_tr, size=48, color=AMBER)
    S.headline("1. THREE TRENCHES CUT INTO THE HILL", t_tr, t_dn, size=44, color=AMBER)
    S.headline("2. CARVE DOWN THROUGH THE BLOCK LEFT IN THE MIDDLE", t_dn, t_left, size=40, color=CYAN)
    S.headline("THE 'BUILDING' IS WHAT WAS LEFT BEHIND", t_left, size=44, color=WHITE)
    ground_label(S, "FRONT", -14, 23, 0.6, color=MUTED, size=24)
    ground_label(S, "BACK OF THE HILL", 100, 23, 0.6, color=MUTED, size=22)
    note(S, "Plan view, simplified", 0.6, y=0.035)


def s07_footprint(S):
    plan_base(S, xw=(-30, 130), y0=-20)
    arts = court_plan(S, 0)
    fader(S, arts, 0.3)
    plan_temple(S, 0.3)
    t_par = S.c("here is the Parthenon")
    dim_h(S, 0, COURT_W, 50, "≈ 82 m", S.c("eighty-two"), size=32)
    dim_v(S, -4, 0, COURT_D, "≈ 46 m", S.c("forty-six"), ha="right", dx=-1.5, size=32)
    S.headline("KAILASA'S COURTYARD", 0.4, t_par, size=50, color=AMBER, y=0.92)
    # Parthenon footprint slides in
    par = Rect((0, 0), PAR_W, PAR_D, fc=CYAN, ec=WHITE, lw=2, zorder=8, alpha=0)
    S.ax.add_patch(par)
    lab = S.ax.text(0, 0, "PARTHENON BASE ≈ 69.5 × 30.9 m", fontproperties=BOLD, size=26, color="#07111d",
                    ha="center", va="center", zorder=9, alpha=0)

    def up(t):
        g = ease2((t - t_par) / 1.4)
        x = 140 + (6.25 - 140) * g
        y = 7.5
        par.set_xy((x, y))
        a = 0.75 * ease((t - t_par) / 0.4)
        par.set_alpha(a)
        lab.set_position((x + PAR_W / 2, y + PAR_D / 2))
        lab.set_alpha(ease((t - t_par) / 0.4))
    S.updaters.append(up)
    S.headline("THE PARTHENON, ATHENS", t_par, S.c("Kailasa's courtyard covers"), size=50, color=CYAN, y=0.92)
    S.headline("≈ 3,770 m²  vs  ≈ 2,150 m²: ALMOST DOUBLE", S.c("Kailasa's courtyard covers"), size=44,
               color=WHITE, y=0.92)
    S.text(0.5, 0.075, "All of it cut out of solid rock", S.c("every square"), size=32, box=True, color=AMBER)
    note(S, "Outer sizes to scale; inner layout simplified", 0.4, y=0.03)


def s08_height(S):
    view(S, 0, 104, -9)
    S.ax.add_patch(Rect((-10, -20), 120, 20, fc=ROCK, ec="none", zorder=1))
    S.ax.plot([0, 104], [0, 0], color=STRATA, lw=2, zorder=1.1)
    for y in range(0, 41, 10):
        S.ax.plot([0, 104], [y, y], color=GRID, lw=1, zorder=0.5)
        S.ax.text(1, y + 0.4, f"{y} m", fontproperties=REG, size=18, color=MUTED, zorder=0.6)
    t_b = S.c("ten storey")
    t_c = S.c("Parthenon's columns")
    # Kailasa tower
    tw = MPoly(tower_poly(62, 86, 0, TOWER_H), fc=STONE, ec=STONE_E, lw=1.5, zorder=3, alpha=0)
    S.ax.add_patch(tw)
    fader(S, [tw], 0.3)
    dim_v(S, 89, 0, TOWER_H, "≈ 32.6 m", S.c("thirty-two and a half"), color=AMBER, size=32)
    ground_label(S, "KAILASA TOWER", 74, -4, 0.3, color=AMBER, size=24)
    # 10-storey building (approx 3.2 m a floor, for scale only)
    bl = []
    for k in range(10):
        r = Rect((36, k * 3.26), 14, 3.0, fc="#2c4262", ec=CYAN, lw=1.2, zorder=3, alpha=0)
        S.ax.add_patch(r)
        bl.append(r)
        for j in range(3):
            w = Rect((37.5 + j * 4.3, k * 3.26 + 0.8), 2.4, 1.4, fc=CYAN, ec="none", zorder=3.1, alpha=0)
            S.ax.add_patch(w)
            bl.append(w)
    fader(S, bl, t_b, peak=0.9)
    ground_label(S, "≈ 10-STOREY BUILDING", 43, -4, t_b, color=CYAN, size=22)
    # Parthenon column
    col = [Rect((21, 0), 2.0, PAR_COL, fc=WHITE, ec=MUTED, lw=1, zorder=3, alpha=0)]
    for j in range(4):
        col.append(Rect((21.25 + j * 0.45, 0.3), 0.15, PAR_COL - 0.6, fc=MUTED, ec="none", zorder=3.1, alpha=0))
    col.append(Rect((20.5, PAR_COL), 3.0, 0.8, fc=WHITE, ec=MUTED, lw=1, zorder=3, alpha=0))
    fader(S, col, t_c)
    dim_v(S, 25, 0, PAR_COL, "≈ 10.4 m", S.c("about ten metres"), color=WHITE, size=26)
    ground_label(S, "PARTHENON COLUMN", 23, -4, t_c, color=WHITE, size=20)
    # person for scale
    pp = [Circ((6, 1.55), 0.2, fc=PINK, ec="none", zorder=3, alpha=0),
          Rect((5.8, 0), 0.4, 1.35, fc=PINK, ec="none", zorder=3, alpha=0)]
    for p in pp:
        S.ax.add_patch(p)
    fader(S, pp, 0.3)
    ground_label(S, "PERSON", 6, -4, 0.3, color=PINK, size=20)
    S.headline("NOW LOOK UP", 0.4, S.c("thirty-two and a half"), size=50, y=0.92)
    S.headline("TOWER TOP ≈ 32.6 m ABOVE THE COURTYARD", S.c("thirty-two and a half"), S.c("Remember"), size=42,
               color=AMBER, y=0.92)
    S.headline("CARVED FROM ITS TIP DOWNWARDS", S.c("Remember"), size=46, color=CYAN, y=0.92)
    S.brand()


def s09_volume(S):
    view(S, 0, 160, 0)
    t_v = S.c("eighty-five thousand")
    t_pool = S.c("An Olympic")
    t_34 = S.c("thirty-four Olympic")
    S.headline("≈ 85,000 m³ OF ROCK", t_v - 0.3, S.c("weighing"), size=56, color=AMBER, y=0.88)
    S.headline("≈ 200,000 TONNES", S.c("weighing"), t_pool, size=56, color=AMBER, y=0.88)
    S.headline("OLYMPIC POOL: 50 × 25 × 2 m = 2,500 m³", t_pool, t_34, size=44, color=CYAN, y=0.88)
    S.headline("≈ 34 OLYMPIC POOLS OF STONE", t_34, size=54, color=WHITE, y=0.88)
    # 34 pools in a 7x5 grid (34 cells)
    pw, ph = 16, 8
    for i in range(34):
        r_, c_ = divmod(i, 7)
        x = 14 + c_ * (pw + 3)
        y = 60 - r_ * (ph + 3.2)
        rr = Rect((x, y), pw, ph, fc=CYAN, ec=WHITE, lw=1.2, zorder=3, alpha=0)
        S.ax.add_patch(rr)
        ta = (t_pool + 0.2) if i == 0 else (t_34 + 0.06 * i)

        def up(t, rr=rr, ta=ta, i=i):
            a = ease((t - ta) / 0.3)
            rr.set_alpha(0.85 * a)
            if i == 0 and t > t_pool:
                rr.set_facecolor(CYAN)
        S.updaters.append(up)
    S.text(0.5, 0.06, "Broken, carried and dumped by hand", S.c("All of it"), size=34, box=True, color=AMBER)
    note(S, "Volume and weight: estimates (Wikipedia, citing published studies)", t_v, y=0.025)
    S.brand()


def s10_time(S):
    view(S, 0, 160, 0)
    t_a = S.c("He assumed")
    t_250 = S.c("two hundred and fifty")
    t_cav = S.c("That is a calculation")
    S.headline("NO RECORD OF HOW LONG IT TOOK", 0.4, S.c("The archaeologist"), size=48, y=0.9)
    S.headline("ONE ESTIMATE: M. K. DHAVALIKAR", S.c("The archaeologist"), t_a, size=48, color=AMBER, y=0.9)
    S.headline("ASSUME: ≈ 4 CUBIC FEET OF ROCK / PERSON / DAY", t_a, t_250, size=40, color=CYAN, y=0.9)
    S.headline("250 LABOURERS · ≈ 5.5 YEARS", t_250, t_cav, size=52, color=AMBER, y=0.9)
    S.headline("AN ESTIMATE, NOT A RECORD", t_cav, S.c("Dhavalikar thought"), size=50, color=PINK, y=0.9)
    S.headline("SOME PANELS: 30–40 YEARS LATER", S.c("Dhavalikar thought"), size=48, color=WHITE, y=0.9)
    # 250 workers as dots (25 x 10)
    xs, ys = np.meshgrid(np.arange(25), np.arange(10))
    pts = np.column_stack([20 + xs.ravel() * 5, 22 + ys.ravel() * 4.2])
    sc = S.ax.scatter(pts[:, 0], pts[:, 1], s=0, color=AMBER, zorder=3)
    order = np.random.default_rng(2).permutation(250)

    def up(t):
        g = ease2((t - t_250) / 1.6)
        n = int(250 * g)
        sz = np.zeros(250)
        sz[order[:n]] = 70
        sc.set_sizes(sz * (1 - 0.6 * ease((t - t_cav) / 0.6)))
    S.updaters.append(up)
    # year bar
    ax = S.fig.add_axes([0.13, 0.08, 0.74, 0.07])
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    bar = Rect((0, 0.2), 0, 0.6, fc=AMBER, zorder=2)
    ax.add_patch(bar)
    ax.add_patch(Rect((0, 0.2), 6, 0.6, fc="none", ec=MUTED, lw=1.5, zorder=3))
    lab = ax.text(0.1, 0.5, "", fontproperties=BOLD, size=24, color="#07111d", va="center", zorder=4)

    def up2(t):
        g = ease2((t - t_250 - 1.0) / 2.5)
        bar.set_width(5.5 * g)
        lab.set_text(f"{5.5 * g:.1f} YEARS" if g > 0.15 else "")
    S.updaters.append(up2)
    note(S, "Each dot = 1 labourer (Dhavalikar's assumption)", t_250, y=0.025)
    S.brand()


def s11_who(S):
    tl_setup(S)
    tl = TL(S, y=-0.35)
    tl.camera([(0, 810, 520), (S.c("Krishna the First") - 0.5, 810, 520), (S.c("Krishna the First") + 1.5, 760, 150), (S.T, 760, 140)])
    tl.span(600, 1000, -0.8, MUTED, "ELLORA CAVES CARVED, c. AD 600–1000", 0.4, t1=None, size=24)
    tl.span(735, 756, -0.15, CYAN, "DANTIDURGA", S.c("Dantidurga"), size=24)
    tl.span(756, 773, 0.05, AMBER, "KRISHNA I", S.c("Krishna the First"), size=28)
    tl.marker(765, "KAILASA CARVED", S.c("in the middle of the eighth"), sub="mid-700s", color=AMBER, h=0.8, size=32)
    S.headline("WHO ORDERED IT?", 0.4, S.c("Krishna the First"), size=52, y=0.9)
    S.headline("KRISHNA I · RASHTRAKUTA DYNASTY · r. c. 756–773", S.c("Krishna the First"), S.c("His predecessor"),
               size=40, color=AMBER, y=0.9)
    S.headline("DANTIDURGA: INSCRIPTION IN CAVE 15 NEXT DOOR", S.c("His predecessor"), S.c("Either way"), size=38,
               color=CYAN, y=0.9)
    S.headline("CARVED IN THE MID-8th CENTURY", S.c("Either way"), size=46, color=WHITE, y=0.9)
    note(S, "Reign dates approximate (sources differ by a year or two)", 0.4, y=0.035)


def s12_words(S):
    view(S, 0, 160, 0)
    t_q = S.c("says the king")
    t_leg = S.c("Later, a Marathi")
    # copper plates
    plates = []
    for i in range(3):
        p = FBP((22 + i * 3, 36 - i * 3), 44, 26, boxstyle="round,pad=0,rounding_size=2", fc="#b87333",
                ec="#e0a370", lw=2, zorder=3 + i, alpha=0)
        S.ax.add_patch(p)
        plates.append(p)
        for k in range(6):
            ln, = S.ax.plot([26 + i * 3, 62 + i * 3], [56 - i * 3 - k * 3.6] * 2, color="#7a4a1f", lw=2,
                            ls=(0, (3, 2)), zorder=3.1 + i, alpha=0)
            plates.append(ln)
    fader(S, plates, 0.4, t_leg)
    S.headline("VADODARA COPPER-PLATE INSCRIPTION · c. AD 812", 0.4, t_leg, size=40, color=AMBER, y=0.9)
    S.text(0.71, 0.5, "The king built a temple\nso wondrous that even\nthe gods and the architect\nwere astonished", t_q, t_leg, size=46,
           color=WHITE, box=True)
    S.text(0.71, 0.25, "What the inscription says (paraphrased)", t_q, t_leg, size=22, color=MUTED, font=REG)
    S.headline("A LATER MARATHI LEGEND", t_leg, S.c("It's a legend"), size=48, color=CYAN, y=0.9)
    S.text(0.5, 0.62, "A queen's vow: no food until she sees the temple's top", S.c("A queen"), S.c("It's a legend"),
           size=36, box=True)
    S.text(0.5, 0.45, "Architect Kokasa: carve it from the top down", S.c("Kokasa"), S.c("It's a legend"), size=36,
           box=True, color=AMBER)
    S.headline("LEGEND, NOT HISTORY", S.c("It's a legend"), size=52, color=PINK, y=0.9)
    S.text(0.5, 0.55, "Katha-Kalpataru, c. 1470–1535: people were\nalready trying to explain it", S.c("It's a legend"),
           size=36, box=True)
    S.brand()


def s13_inside(S):
    plan_base(S, xw=(-30, 130), y0=-18)
    arts = court_plan(S, 0)
    fader(S, arts, 0.3)
    plan_temple(S, 0.3)
    hl = []

    def mark(key_pts, phrase, label, lx, ly, color=AMBER):
        t0 = S.c(phrase)
        p = MPoly(key_pts, fc=color, ec=WHITE, lw=2, zorder=9, alpha=0)
        S.ax.add_patch(p)
        fader(S, [p], t0, t0 + 3.5, peak=0.8)
        ground_label(S, label, lx, ly, t0, color=color, size=24, t1=t0 + 3.5)

    mark(PLAN["gate"], "through the gateway", "GATEWAY", 2, 33)
    # elephants: dots round the main body base
    t_e = S.c("Carved elephants")
    ex = list(np.linspace(32, 67, 10))
    pts = [(x, 11) for x in ex] + [(x, 35) for x in ex]
    el = S.ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=0, color=PINK, edgecolors=WHITE, zorder=10)
    S.updaters.append(lambda t: el.set_sizes([120 * min(ease((t - t_e) / 0.4), ease((t_e + 4 - t) / 0.4))] * len(pts)))
    ground_label(S, "ELEPHANTS AROUND THE BASE", 50, -6, t_e, color=PINK, size=24, t1=t_e + 4)
    mark(PLAN["bridge"], "A stone bridge", "ROCK BRIDGE", 27, 33, CYAN)
    mark(PLAN["nandi"], "Nandi hall", "NANDI HALL", 19, 13, AMBER)
    t_p = S.c("Two tall pillars")
    pil = [Circ((14, 8), 1.4, fc=GREEN, ec=WHITE, lw=2, zorder=10, alpha=0),
           Circ((14, 38), 1.4, fc=GREEN, ec=WHITE, lw=2, zorder=10, alpha=0)]
    for p in pil:
        S.ax.add_patch(p)
    fader(S, pil, t_p)
    ground_label(S, "TWO PILLARS", 14, 44, t_p, color=GREEN, size=22, t1=t_p + 3.5)
    t_h = S.c("sixteen pillars")
    cols_ = [(33.5 + 4.3 * i, 15.5 + 4.6 * j) for i in range(4) for j in range(4)]
    cs = S.ax.scatter([c[0] for c in cols_], [c[1] for c in cols_], s=0, color=AMBER, edgecolors=WHITE, zorder=10)
    S.updaters.append(lambda t: cs.set_sizes([90 * ease((t - t_h) / 0.4)] * 16))
    ground_label(S, "MAIN HALL: 16 PILLARS", 40, 50, t_h, color=AMBER, size=24, t1=S.c("A columned"))
    t_g = S.c("A columned")
    mark([(76, 0), (82, 0), (82, 46), (76, 46)], "A columned", "3-STOREY GALLERY", 100, 23, CYAN)
    t_s = S.c("five separate")
    sh = [(72, 36), (72, 10), (8, 3), (40, 39), (60, 7)]
    sh_art = [Rect((x - 1.8, y - 1.5), 3.6, 3.0, fc=VIOLET, ec=WHITE, lw=1.5, zorder=10, alpha=0) for x, y in sh]
    for r in sh_art:
        S.ax.add_patch(r)
    fader(S, sh_art, t_s)
    S.text(0.5, 0.075, "5 detached shrines · 3 for the river goddesses Ganga, Yamuna, Saraswati", t_s, size=30,
           box=True, color=VIOLET)
    S.headline("INSIDE THE COURT", 0.4, size=50, y=0.92)
    note(S, "Plan simplified: positions approximate", 0.4, y=0.03)


def s14_ravana(S):
    view(S, 0, 160, 0)
    t_hold = S.c("Shiva calmly")
    mtn = MPoly([(30, 10), (60, 52), (72, 44), (80, 60), (96, 42), (130, 10)], fc=ROCK, ec=STRATA, lw=2, zorder=2)
    cap = MPoly([(74, 52), (80, 60), (86, 52.5), (82, 54), (78, 51)], fc=WHITE, ec="none", zorder=2.1)
    S.ax.add_patch(mtn)
    S.ax.add_patch(cap)
    S.ax.add_patch(Rect((0, 0), 160, 10, fc="#25303f", ec="none", zorder=1))
    base_m = mtn.get_xy().copy()
    base_c = cap.get_xy().copy()
    t_r = S.c("Ravana trying")

    def up(t):
        amp = 1.6 * ease((t - t_r) / 0.4) * (1 - ease((t - t_hold) / 0.8))
        dx = amp * np.sin(2 * np.pi * t * 3.2)
        dy = amp * 0.5 * np.cos(2 * np.pi * t * 2.3)
        mtn.set_xy(base_m + [dx, dy])
        cap.set_xy(base_c + [dx, dy])
    S.updaters.append(up)
    S.headline("RAVANA SHAKES MOUNT KAILASA", t_r, t_hold, size=50, color=PINK, y=0.9)
    S.headline("...SHIVA HOLDS IT DOWN", t_hold, S.c("Some scholars"), size=50, color=AMBER, y=0.9)
    S.headline("THE TEMPLE'S NAME MAY COME FROM THIS SCENE", S.c("Some scholars"), S.c("Look closely"), size=40,
               color=WHITE, y=0.9)
    S.headline("ORIGINAL PAINTINGS: ONLY TRACES REMAIN", S.c("Look closely"), S.c("added in the eighteenth"),
               size=42, color=CYAN, y=0.9)
    S.headline("LATER COLOUR: 18th CENTURY, AHILYABAI HOLKAR ERA", S.c("added in the eighteenth"), size=38,
               color=AMBER, y=0.9)
    note(S, "Illustration, not the actual panel", 0.4, y=0.035)
    S.brand()


def s15_visit(S):
    india(S, [(0, *MAHA_VIEW), (S.T, 75.45, mercy(20.2), 3.8)], hl=["Maharashtra"], t_hl=0.0)
    state_tag(S, "PLAN YOUR VISIT", 0.3)
    pin(S, *ELLORA, "ELLORA", 0.5, color=AMBER, dy=1.0)
    pin(S, *AJANTA, "AJANTA", S.c("Ajanta, by"), color=PINK, dy=1.0, size=24)
    pin(S, *CSN, "CH. SAMBHAJINAGAR", S.c("nearest airport"), color=CYAN, dy=-1.9, size=22, ring=False)
    S.text(0.04, 0.78, "9 AM – 5 PM", S.c("open from nine"), size=34, ha="left", box=True)
    S.text(0.04, 0.67, "CLOSED TUESDAYS", S.c("closed on Tuesdays"), size=34, color=PINK, ha="left", box=True)
    S.text(0.04, 0.56, "Ajanta: closed Mondays", S.c("Ajanta, by"), size=30, color=WHITE, ha="left", box=True)
    S.text(0.04, 0.45, "Airport + railway: ≈ 30 km", S.c("nearest airport"), size=30, color=CYAN, ha="left", box=True)
    S.text(0.04, 0.34, "BEST: OCT – MAR", S.c("October to March"), size=34, color=GREEN, ha="left", box=True)
    S.text(0.5, 0.1, "Tip: arrive at opening, before the crowds and the afternoon sun", S.c("One honest"), size=32,
           box=True, color=AMBER)
    note(S, "Timings: MTDC. Check before you go.", 0.4, y=0.035)


def s16_scale(S):
    court_scene(S, xw=(-30, 128), y0=-30)
    S.headline("KAILASA AT TRUE SCALE", 0.3, size=54, y=0.92)
    S.text(0.22, 0.12, "COURT ≈ 82 × 46 m\nalmost 2× the Parthenon", S.c("A courtyard"), size=32, box=True, color=AMBER)
    S.text(0.5, 0.12, "TOWER ≈ 32.6 m\ncarved top-down", S.c("A tower"), size=32, box=True, color=CYAN)
    S.text(0.78, 0.12, "≈ 200,000 t of rock\nno machines", S.c("Around two hundred"), size=32, box=True, color=PINK)


def s17_outro(S):
    court_scene(S)
    S.text(0.5, 0.86, "A FEW HUNDRED PEOPLE IN < 6 YEARS...", 0.3, size=44, box=True, color=AMBER)
    S.text(0.5, 0.75, "...OR GENERATIONS?", S.c("or did it take"), size=50, box=True, color=CYAN)
    S.text(0.5, 0.1, "TELL ME IN THE COMMENTS  ·  SUBSCRIBE TO TRUE SCALE", S.c("Tell me"), size=34, box=True)
    S.fade_in_out(0, 1.0)


def hold(sid):
    return {"s02_title": 1.5, "s16_scale": 1.5, "s17_outro": 2.0}.get(sid, 1.0)
