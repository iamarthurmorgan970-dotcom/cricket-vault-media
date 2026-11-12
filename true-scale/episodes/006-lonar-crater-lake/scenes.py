"""Scenes for 006 Lonar crater lake. S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.india import *
from engine.timeline import TL, setup as tl_setup
from matplotlib.patches import Polygon as MPoly

LON, LAT = 76.5075, 19.975
LAKE_G, LAKE_P = "#3f8f6b", "#ff7aa8"
ROCK, ROCK2 = "#2c4262", "#22364f"
MUMBAI = (72.88, 19.08)

# ------------------------------------------------------------------ crater cross-section (km, drawn to scale)
RIM_X, RIM_H, FLOOR_X, FLOOR_Y = 0.9, 0.02, 0.55, -0.13


def prof(x):
    """Ground height (km) along a line through the centre. Plain = 0, rim +20 m, floor 150 m below rim."""
    ax_ = np.abs(x)
    y = np.zeros_like(x, dtype=float)
    out = ax_ >= RIM_X
    y[out] = RIM_H * np.exp(-(ax_[out] - RIM_X) / 0.35)
    wall = (ax_ >= FLOOR_X) & (ax_ < RIM_X)
    u = (ax_[wall] - FLOOR_X) / (RIM_X - FLOOR_X)
    y[wall] = FLOOR_Y + (RIM_H - FLOOR_Y) * u ** 1.3
    y[ax_ < FLOOR_X] = FLOOR_Y
    return y


def water_y(half_width):
    return float(prof(np.array([half_width]))[0])


WATER = water_y(0.6)       # lake about 1.2 km wide


def xsec(S, w=3.4, cy=-0.04, keys=None, layers=True, draw_t=None, water_t=0.0, water_col=LAKE_G):
    """Draw the crater cross-section. Returns dict of artists."""
    ax = S.ax
    if keys:
        S.camera(keys)
    else:
        h = w * H / W
        ax.set_xlim(-w / 2, w / 2)
        ax.set_ylim(cy - h / 2, cy + h / 2)
    xs = np.linspace(-3, 3, 900)
    ys = prof(xs)
    bottom = -1.2
    ground = MPoly(np.vstack([np.column_stack([xs, ys]), [[3, bottom], [-3, bottom]]]), closed=True, fc=ROCK,
                   ec="none", zorder=3)
    ax.add_patch(ground)
    if layers:
        for k, yy in enumerate(np.arange(-0.03, -1.2, -0.045)):
            ax.plot([-3, 3], [yy, yy], color="#3b5476" if k % 2 else "#33496a", lw=1.2, zorder=3.2, alpha=0.6)
        # layers cut by the crater: mask with sky colour above the profile
        sky = MPoly(np.vstack([np.column_stack([xs, ys]), [[3, 2], [-3, 2]]]), closed=True, fc=OCEAN, ec="none",
                    zorder=3.3)
        ax.add_patch(sky)
    line, = ax.plot(xs, ys, color=WHITE, lw=3, zorder=4)
    wx = np.linspace(-0.6, 0.6, 200)
    wpoly = MPoly(np.vstack([np.column_stack([wx, prof(wx)]), [[0.6, WATER], [-0.6, WATER]]]), closed=True,
                  fc=water_col, ec="none", zorder=3.6, alpha=0)
    ax.add_patch(wpoly)
    wl, = ax.plot([-0.6, 0.6], [WATER, WATER], color=water_col, lw=9, solid_capstyle="round", zorder=3.7, alpha=0)
    t_draw = draw_t

    def up(t):
        if t_draw is not None:
            g = ease2((t - t_draw) / 1.6)
            n = max(2, int(len(xs) * g))
            line.set_data(xs[:n], ys[:n])
        wpoly.set_alpha(0.9 * ease((t - water_t) / 0.6))
        wl.set_alpha(ease((t - water_t) / 0.6))
    S.updaters.append(up)
    return dict(line=line, water=wpoly, wl=wl)


def topview(S, w=3.2, cy=-0.12, lake_col=LAKE_G):
    """Crater seen from above, to scale (km): rim 1.8 km, lake about 1.2 km."""
    ax = S.ax
    h = w * H / W
    ax.set_xlim(-w / 2, w / 2)
    ax.set_ylim(cy - h / 2, cy + h / 2)
    ax.add_patch(Rectangle((-5, -5), 10, 10, fc="#1d2d42", zorder=0.5))
    ax.add_patch(Circle((0, 0), 1.05, fc="#24364d", ec="none", zorder=1))
    ax.add_patch(Circle((0, 0), RIM_X, fc="#2f4a70", ec=WHITE, lw=4, zorder=2))
    ax.add_patch(Circle((0, 0), 0.72, fc="#2a4262", ec="none", zorder=2.5))
    lake = Circle((0, 0), 0.6, fc=lake_col, ec="#9fe3c0", lw=2, zorder=3)
    ax.add_patch(lake)
    return lake


def hdim(S, x0, x1, y, label, t0, color=AMBER, dy=0.012, size=30):
    ln, = S.ax.plot([x0, x0], [y, y], color=color, lw=3, zorder=20, alpha=0)
    e0, = S.ax.plot([x0, x0], [y - 0.008, y + 0.008], color=color, lw=3, zorder=20, alpha=0)
    e1, = S.ax.plot([x1, x1], [y - 0.008, y + 0.008], color=color, lw=3, zorder=20, alpha=0)
    tx = S.ax.text((x0 + x1) / 2, y + dy, label, fontproperties=BOLD, size=size, color=color, ha="center",
                   va="bottom", zorder=21, alpha=0)

    def up(t):
        g = ease2((t - t0) / 0.9)
        a = ease((t - t0) / 0.3)
        ln.set_data([x0, x0 + (x1 - x0) * g], [y, y])
        for z in (ln, e0, e1):
            z.set_alpha(a)
        tx.set_alpha(ease((t - t0 - 0.5) / 0.4))
    S.updaters.append(up)


def vdim(S, x, y0, y1, label, t0, color=CYAN, size=30, side=1):
    ln, = S.ax.plot([x, x], [y0, y0], color=color, lw=3, zorder=20, alpha=0)
    caps = [S.ax.plot([x - 0.025, x + 0.025], [yy, yy], color=color, lw=3, zorder=20, alpha=0)[0] for yy in (y0, y1)]
    tx = S.ax.text(x + 0.04 * side, (y0 + y1) / 2, label, fontproperties=BOLD, size=size, color=color,
                   ha="left" if side > 0 else "right", va="center", zorder=21, alpha=0)

    def up(t):
        g = ease2((t - t0) / 0.9)
        a = ease((t - t0) / 0.3)
        ln.set_data([x, x], [y0, y0 + (y1 - y0) * g])
        ln.set_alpha(a)
        for c in caps:
            c.set_alpha(a)
        tx.set_alpha(ease((t - t0 - 0.5) / 0.4))
    S.updaters.append(up)


def label(S, x, y, s, t0, color=WHITE, size=26, t1=None, ha="center"):
    tx = S.ax.text(x, y, s, fontproperties=BOLD, size=size, color=color, ha=ha, va="center", zorder=22, alpha=0,
                   bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0))
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        tx.set_alpha(a)
        tx.get_bbox_patch().set_alpha(0.75 * a)
    S.updaters.append(up)
    return tx


def lonar_map(S, keys, hl=True):
    india(S, keys, hl=["Maharashtra"] if hl else None)


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    t_z = S.c("there's a hole")
    lonar_map(S, [(0, *INDIA_VIEW), (t_z, 75.0, mercy(19.6), 14), (S.T, 75.0, mercy(19.6), 12.5)])
    pin(S, *MUMBAI, "MUMBAI", 0.8, color=WHITE, dy=-1.4, size=24)
    pin(S, LON, LAT, "LONAR", t_z, color=AMBER, dy=0.9)
    a, b = merc(np.array([MUMBAI]))[0], merc(np.array([[LON, LAT]]))[0]
    ln, = S.ax.plot([a[0], a[0]], [a[1], a[1]], color=AMBER, lw=3, ls=(0, (6, 4)), zorder=25)
    t_l = S.c("About five")

    def up(t):
        g = ease2((t - t_l) / 1.4)
        ln.set_data([a[0], a[0] + (b[0] - a[0]) * g], [a[1], a[1] + (b[1] - a[1]) * g])
    S.updaters.append(up)
    label(S, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.55, "≈ 500 km", t_l + 1.0, color=AMBER, size=26)
    S.headline("≈ 1.8 km WIDE, MADE BY A ROCK FROM SPACE", S.c("almost two"), S.c("And right now"), size=40)
    S.headline("NOW ITS TEMPLES ARE GOING UNDER WATER", S.c("And right now"), size=40, color=CYAN)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    xsec(S, w=3.4, cy=-0.02, water_t=0.0)
    S.camera([(0, 0, -0.02, 3.6), (S.T, 0, -0.03, 3.3)])
    S.text(0.5, 0.74, "LONAR", 0.3, size=110, pop=True)
    S.text(0.5, 0.61, "INDIA'S METEORITE CRATER LAKE", 0.7, size=56, color=AMBER, pop=True)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=CYAN)
    S.brand()


def s03_where(S):
    t_z = S.c("Lonar sits")
    lonar_map(S, [(0, *INDIA_VIEW), (t_z + 0.2, 76.6, mercy(19.4), 12), (S.T, LON, mercy(19.9), 9)])
    state_tag(S, "MAHARASHTRA")
    pin(S, LON, LAT, "LONAR", t_z + 0.6, color=AMBER, dy=0.9)
    pin(S, 76.18, 20.53, "Buldhana", S.c("Buldhana"), color=WHITE, ring=False, dy=0.5, size=20)
    card(S, "Buldhana district · Vidarbha region", "Buldhana district", 0.2, WHITE, S.c("on the flat"))
    card(S, "Deccan Plateau: a flat tableland of old lava", "on the flat", 0.2, AMBER, S.c("Then the ground"))
    card(S, "Then the ground drops away", "Then the ground", 0.2, CYAN)


def s04_size(S):
    xsec(S, w=2.5, cy=-0.04, draw_t=0.2, water_t=S.c("The lake inside"))
    S.headline("DRAWN TO TRUE SCALE", 0.4, S.c("To picture"), size=36, y=0.9, color=MUTED)
    hdim(S, -RIM_X, RIM_X, 0.06, "≈ 1.8 km ACROSS", S.c("one point eight"), color=AMBER)
    vdim(S, -0.3, RIM_H, FLOOR_Y, "≈ 150 m DEEP", S.c("one hundred and fifty"), color=CYAN)
    label(S, 0.95, -0.07, "RIM ≈ 20 m above the plain", S.c("Its rim"), color=WHITE, size=22)
    label(S, 0, WATER - 0.08, "LAKE ≈ 1.2 km WIDE", S.c("The lake inside"), color=GREEN, size=24)
    # 40-storey tower (≈ 130 m) on the crater floor
    tw = Rectangle((0.27, FLOOR_Y), 0.06, 0, fc=PINK, ec=WHITE, lw=1.5, zorder=6, alpha=0)
    S.ax.add_patch(tw)
    t_t = S.c("a forty-storey")

    def up(t):
        g = ease2((t - t_t) / 1.4)
        tw.set_height(0.13 * g)
        tw.set_alpha(0.95 * ease((t - t_t) / 0.3))
    S.updaters.append(up)
    S.headline("A 40-STOREY TOWER WOULD BARELY REACH THE RIM", S.c("a forty-storey"), size=36, y=0.9, color=PINK)
    S.brand()


def s05_impact(S):
    xsec(S, w=3.4, cy=0.25)
    S.camera([(0, 0, 0.25, 3.4), (S.T, 0, 0.2, 3.2)])
    t_hit = S.c("A meteorite") + 0.2
    # incoming rock
    rock = Circle((-1.6, 1.0), 0.035, fc=AMBER, ec=WHITE, lw=2, zorder=30, alpha=0)
    S.ax.add_patch(rock)
    trail, = S.ax.plot([], [], color=AMBER, lw=6, alpha=0.5, zorder=29, solid_capstyle="round")
    flash = Circle((0, 0), 0.01, fc="#fff3c4", ec="none", zorder=31, alpha=0)
    S.ax.add_patch(flash)
    rng = np.random.default_rng(6)
    deb = [(rng.uniform(-1, 1), rng.uniform(0.2, 1.0)) for _ in range(40)]
    sc = S.ax.scatter([0] * 40, [0] * 40, s=18, color="#c9b38a", zorder=28, alpha=0)

    def up(t):
        u = (t - (t_hit - 1.0)) / 1.0
        if 0 <= u <= 1:
            x, y = -1.6 + 1.6 * u, 1.0 - 1.0 * u
            rock.center = (x, y)
            rock.set_alpha(1)
            trail.set_data([-1.6 + 1.6 * max(u - 0.35, 0), x], [1.0 - 1.0 * max(u - 0.35, 0), y])
        else:
            rock.set_alpha(0)
            trail.set_data([], [])
        f = t - t_hit
        if f >= 0:
            flash.set_radius(0.05 + 0.9 * ease(f / 0.5))
            flash.set_alpha(max(0, 0.9 - f / 0.9))
            g = ease2(min(f / 2.5, 1))
            pts = [(dx * 2.0 * g, dy * 0.5 * np.sin(np.pi * g) * 1.0 + 0.0) for dx, dy in deb]
            sc.set_offsets(pts)
            sc.set_alpha(max(0, 1 - f / 6))
    S.updaters.append(up)
    card(S, "≈ 2 million tonnes (estimate)", "two million", 0.83, AMBER, S.c("When it hit"), size=38)
    card(S, "≈ 90,000 km/h", "ninety thousand", 0.74, CYAN, S.c("When it hit"), size=38)
    card(S, "Energy often compared to a 6-megaton blast", "When it hit", 0.83, PINK, S.c("Scientists later"),
         size=36)
    card(S, "Debris thrown up to ≈ 2 km from the centre", "throwing debris", 0.6, WHITE, S.c("Scientists later"),
         size=32)
    card(S, "Shatter cones + shock-melted glass = proof of impact", "Scientists later", 0.83, GREEN, size=34)
    S.brand()


def s06_basalt(S):
    xsec(S, w=3.4, cy=0.4)
    S.camera([(0, 0, 0.4, 3.4), (S.T, 0, 0.38, 3.2)])
    card(S, "DECCAN BASALT: lava layers ≈ 66 million years old", "made of basalt", 0.9, AMBER,
         S.c("Lonar is often"), size=36)
    card(S, "Often described as the only known impact crater formed entirely in basalt", "Lonar is often", 0.9,
         WHITE, S.c("That matters"), size=32)
    # Moon and Mars discs
    ax2 = S.fig.add_axes([0.1, 0.42, 0.8, 0.36])
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 3.6)
    ax2.set_aspect("equal", adjustable="datalim")
    ax2.set_axis_off()
    discs = [(2.2, "#3f8f6b", "LONAR (EARTH)", None), (5.0, "#b8b8b8", "MOON", "the Moon"),
             (7.8, "#c1440e", "MARS", "Mars are")]
    arts = []
    for x, col, name, ph in discs:
        c = Circle((x, 2.0), 1.0, fc=col, ec=WHITE, lw=2, alpha=0)
        ax2.add_patch(c)
        tx = ax2.text(x, 0.55, name, fontproperties=BOLD, size=26, color=WHITE, ha="center", alpha=0)
        arts.append((c, tx, S.c(ph) if ph else S.c("That matters")))
    t_end = S.c("In twenty nineteen")

    def up(t):
        for c, tx, t0 in arts:
            a = min(ease((t - t0) / 0.4), ease((t_end - t) / 0.4))
            c.set_alpha(0.9 * a)
            tx.set_alpha(a)
    S.updaters.append(up)
    S.headline("ALL LARGELY BASALT", S.c("largely basalt"), t_end, y=0.82, size=40, color=CYAN)
    card(S, "2019, IIT Bombay: minerals similar to Apollo Moon rocks", "In twenty nineteen", 0.62, CYAN, size=36)
    card(S, "A natural lab for impacts on other worlds", "So scientists", 0.52, GREEN, size=34)
    S.brand()


def kya(x):
    if x > 1000:
        return ""
    return "TODAY" if x > -1000 else f"{-x / 1000:,.0f}k yrs ago"


def s07_age(S):
    tl_setup(S)
    tl = TL(S, fmt=kya, nice=[1, 2, 5])
    tl.camera([(0, -55000, 150000), (S.c("Then, in") - 0.5, -55000, 150000), (S.c("Then, in") + 1.5, -330000, 800000), (S.T, -330000, 820000)])
    tl.marker(0, "TODAY", 0.4, color=WHITE, side=1, h=0.3, size=24)
    tl.marker(-52000, "≈ 52,000 YEARS", S.c("fifty-two thousand"), sub="thermoluminescence", color=GREEN,
              side=1, h=0.5, size=26)
    tl.span(-617000, -523000, 0.25, AMBER, "570,000 ± 47,000", S.c("about five hundred"), dur=1.0)
    tl.marker(-570000, "≈ 570,000 YEARS", S.c("argon dating"), sub="argon-argon, 2011", color=AMBER, side=-1,
              h=0.28, size=26)
    S.headline("HOW OLD IS LONAR? STILL DEBATED", 0.4, size=40, y=0.9)
    S.caption("Older figure may be inflated by trapped argon", S.c("Some researchers"), S.c("So the honest"),
              color=PINK)
    S.caption("Somewhere between ≈ 50,000 and ≈ 570,000 years", S.c("So the honest"), color=CYAN)
    S.brand()


def yrs(x):
    return f"{int(round(x))}"


def s08_discovery(S):
    tl_setup(S)
    tl = TL(S, fmt=yrs, nice=[1, 2, 5])
    tl.camera([(0, 1880, 240), (S.T, 1905, 250)])
    tl.marker(1823, "C. J. E. ALEXANDER", S.c("A British officer"), sub="records the crater, 1823", color=AMBER,
              side=1, h=0.5, size=26)
    tl.span(1823, 1965, 0.08, MUTED, "Often thought to be a volcano", S.c("For a long time"), dur=1.4)
    tl.marker(1979, "NATIONAL GEOLOGICAL MONUMENT", S.c("In nineteen"), sub="Geological Survey of India, 1979",
              color=GREEN, side=-1, h=0.42, size=26)
    S.headline("FROM 'OLD VOLCANO' TO PROVEN IMPACT CRATER", S.c("Only later"), size=38, y=0.9)
    S.brand()


def s09_water(S):
    xsec(S, w=3.4, cy=-0.02)
    S.camera([(0, 0, -0.02, 3.4), (S.T, 0, -0.05, 2.6)])
    t_in = S.c("Water comes in")
    for i, x in enumerate([-0.82, -0.7, 0.7, 0.82]):
        y0 = water_y(abs(x)) + 0.0
        S.ax.annotate("", xy=(np.sign(x) * 0.6, WATER + 0.004), xytext=(x, water_y(abs(x)) + 0.03),
                      arrowprops=dict(arrowstyle="-|>", color=CYAN, lw=3), zorder=25).set_alpha(0)
    arrows = [a for a in S.ax.texts if hasattr(a, "arrow_patch")]
    evap = []
    for x in (-0.3, 0, 0.3):
        a = S.ax.annotate("", xy=(x, WATER + 0.1), xytext=(x, WATER + 0.01),
                          arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=3, ls="--"), zorder=25)
        evap.append(a)
    t_ev = S.c("evaporating")

    def up(t):
        for a in arrows:
            a.arrow_patch.set_alpha(ease((t - t_in) / 0.4))
        for a in evap:
            a.arrow_patch.set_alpha(ease((t - t_ev) / 0.4))
    S.updaters.append(up)
    S.headline("NO OUTLET", S.c("has no outlet"), size=46, y=0.9, color=PINK)
    label(S, -0.95, -0.03, "rain + springs in", t_in, color=CYAN, size=24)
    label(S, 0, WATER + 0.125, "only way out: evaporation", t_ev, color=AMBER, size=24)
    card(S, "SALTY + STRONGLY ALKALINE", "salty and strongly", 0.16, WHITE, S.c("with a pH"), size=40)
    card(S, "pH ≈ 9 to 10.5", "with a pH", 0.16, AMBER, S.c("Ordinary fish"), size=44)
    card(S, "Microbes thrive: e.g. Cecembia lonarensis", "Several bacteria", 0.16, GREEN, size=38)
    S.brand()


def s10_pink(S):
    wpoly = topview(S, w=5.2, cy=-0.1)
    S.camera([(0, 0, -0.1, 5.4), (S.T, 0, -0.1, 5.0)])
    S.brand()
    t0, t1 = S.c("it turned from green"), S.c("to pink") + 0.8
    g_rgb, p_rgb = np.array(matplotlib.colors.to_rgb(LAKE_G)), np.array(matplotlib.colors.to_rgb(LAKE_P))

    def up(t):
        u = ease2((t - t0) / max(t1 - t0, 0.5))
        wpoly.set_facecolor(tuple(g_rgb + (p_rgb - g_rgb) * u))
    S.updaters.append(up)
    S.headline("JUNE 2020", S.c("And in June"), size=56, y=0.88, color=PINK)
    card(S, "Green to pink in 2-3 days", "two to three days", 0.16, WHITE, S.c("Studies linked"), size=42)
    card(S, "Low water + higher salinity favoured salt-loving microbes", "Studies linked", 0.16, AMBER,
         S.c("Photos went"), size=34)
    card(S, "The photos went viral across India", "Photos went", 0.16, CYAN, size=38)
    S.brand()


def s11_temples(S):
    place(S, "Maharashtra", LON, LAT, "LONAR", 8.0, [
        ("Stone temples, mostly ≈ 11th-12th century", "most dating", 0.2, AMBER, S.c("The finest")),
        ("DAITYA SUDAN TEMPLE · Hemadpanti style", "The finest", 0.2, WHITE, S.c("Local legend")),
        ("Legend: Vishnu slew the demon Lonasura", "Local legend", 0.2, PINK, S.c("At the Gomukh")),
        ("GOMUKH: spring water from a stone cow's mouth", "At the Gomukh", 0.2, CYAN)],
        zoom_phrase="People have", center=(LON, LAT - 0.6))


def s12_wildlife(S):
    xsec(S, w=3.4, cy=-0.02)
    S.text(0.5, 0.88, "LONAR WILDLIFE SANCTUARY", S.c("Lonar Wildlife"), size=44, box=True, pop=True, color=GREEN)
    S.text(0.5, 0.77, "RAMSAR WETLAND · 2020", S.c("Ramsar"), size=40, box=True, color=CYAN)
    S.bars([("Bird species", 160, AMBER, S.c("one hundred and sixty")),
            ("Reptile species", 46, GREEN, S.c("forty-six")),
            ("Mammal species", 12, CYAN, S.c("twelve mammals"))],
           S.c("one hundred and sixty") - 0.3, rect=(0.25, 0.05, 0.5, 0.36), xmax=210, unit="", dec=0)
    S.brand()


def shore(S):
    """Close-up of the shore, in metres: a slope, a temple, a ruler in feet."""
    ax = S.ax
    ax.set_xlim(-2, 42)
    h = 44 * H / W
    ax.set_ylim(-4, -4 + h)
    xs = np.linspace(-2, 42, 200)
    ys = np.clip((xs - 8) * 0.45, -4, 40)
    ax.add_patch(MPoly(np.vstack([np.column_stack([xs, ys]), [[42, -10], [-2, -10]]]), closed=True, fc=ROCK,
                       ec=WHITE, lw=2.5, zorder=3))
    # temple: base + spire, standing at x 14..20
    bx, by = 14.0, (14.0 - 8) * 0.45
    ax.add_patch(Rectangle((bx, by - 1.5), 5, 3.8, fc="#c9b38a", ec=WHITE, lw=1.5, zorder=4))
    ax.add_patch(MPoly([[bx - 0.3, by + 2.3], [bx + 5.3, by + 2.3], [bx + 2.5, by + 6.5]], closed=True,
                       fc="#d9c49a", ec=WHITE, lw=1.5, zorder=4))
    ax.add_patch(Rectangle((bx + 1.8, by - 1.5), 1.4, 2.2, fc="#5a4a33", zorder=4.5))
    return by - 1.5


def s13_rising(S):
    base = shore(S)
    lvl0 = base - 1.0
    FT = 0.3048
    water = Rectangle((-2, -10), 44, 0, fc=LAKE_P, ec="none", alpha=0.55, zorder=5)
    S.ax.add_patch(water)
    t_r = S.c("Over the last")
    rise = 25 * FT

    def up(t):
        g = ease2((t - t_r) / 6.0)
        water.set_height(lvl0 + 10 + rise * g)
    S.updaters.append(up)
    # ruler in feet
    for f in range(0, 26, 5):
        y = lvl0 + f * FT
        S.ax.plot([36, 37.2], [y, y], color=WHITE, lw=2, zorder=6)
        S.ax.text(37.6, y, f"+{f} ft", fontproperties=BOLD, size=20, color=WHITE, va="center", zorder=6)
    S.ax.plot([36.6, 36.6], [lvl0, lvl0 + rise], color=WHITE, lw=2, zorder=6)
    S.headline("THE LAKE IS RISING", 0.4, S.c("In March"), size=44, y=0.9, color=CYAN)
    S.headline("MINISTER, MARCH 2026: UP 20-25 FEET", S.c("In March"), S.c("Other reports"), size=38, y=0.9,
               color=AMBER)
    S.headline("OTHER REPORTS: 15-20 FEET", S.c("Other reports"), S.c("At least six"), size=38, y=0.9, color=WHITE)
    S.headline("AT LEAST 6 TEMPLES SUBMERGED", S.c("At least six"), size=40, y=0.9, color=PINK)
    card(S, "incl. Kamalja Devi: water inside the sanctum", "Kamalja Devi", 0.12, WHITE, size=34)
    S.text(0.02, 0.03, "Schematic: water rise to scale, slope and temple illustrative", 0.5, size=16, color=MUTED,
           font=REG, ha="left")
    S.brand()


def s14_why(S):
    xsec(S, w=3.4, cy=-0.25)
    t_s = S.c("four springs")
    S.text(0.5, 0.9, "WHY IS IT RISING?", 0.3, size=44, box=True, pop=True)
    for i, x in enumerate([-0.85, -0.72, 0.72, 0.85]):
        a = S.ax.annotate("", xy=(np.sign(x) * 0.6, WATER + 0.004), xytext=(x, water_y(abs(x)) + 0.03),
                          arrowprops=dict(arrowstyle="-|>", color=CYAN, lw=3), zorder=25)
        a.arrow_patch.set_alpha(0)
        S.updaters.append(lambda t, a=a: a.arrow_patch.set_alpha(ease((t - t_s) / 0.4)))
    label(S, 0, 0.14, "heavy rain", S.c("heavy rain"), color=WHITE, size=26)
    label(S, -1.1, 0.06, "4 springs flowing in", t_s, color=CYAN, size=24)
    label(S, 0, WATER - 0.05, "no outlet", S.c("no outlet"), color=PINK, size=26)
    rows = [("JAN 2026  Bombay HC (Nagpur bench) orders a PIL", "In January", AMBER),
            ("IIT Bombay experts sampling the lake", "IIT Bombay", GREEN),
            ("MAR 2026  State to seek wildlife nod to pump water out", "seek wildlife", CYAN)]
    for i, (s, ph, col) in enumerate(rows):
        S.text(0.08, 0.42 - i * 0.085, s, S.c(ph), size=32, color=col, ha="left", box=True)
    S.caption("Is pumping safe for such a unique lake? Still debated", S.c("Whether pumping"), color=PINK)
    S.brand()


def s15_reasons(S):
    xsec(S, w=3.4, cy=0.35)
    S.text(0.5, 0.9, "4 REASONS TO GO", 0.3, size=48, box=True, pop=True, color=AMBER)
    items = [("1  Walk into a space-rock crater", "First", AMBER, 0.27, 0.7),
             ("2  A salty, alkaline lake", "Second", GREEN, 0.73, 0.7),
             ("3  Centuries-old temples", "Third", PINK, 0.27, 0.56),
             ("4  Birds, forest, wide skies", "And fourth", CYAN, 0.73, 0.56)]
    for s, ph, col, x, y in items:
        S.text(x, y, s, S.c(ph), size=36, color=col, box=True, pop=True)
    S.brand()


def s16_visit(S):
    t_z = S.c("Getting there")
    lonar_map(S, [(0, *INDIA_VIEW), (t_z + 0.3, 76.0, mercy(20.0), 5.2), (S.T, 76.0, mercy(20.05), 5.0)])
    pin(S, LON, LAT, "LONAR", 0.8, color=AMBER, dy=0.35)
    routes = [((75.34, 19.88), "CH. SAMBHAJINAGAR (airport)", "≈ 135-140 km", "Chhatrapati", 0.3, PINK),
              ((75.88, 19.84), "JALNA (rail)", "≈ 90 km", "Jalna or", -0.6, CYAN),
              ((76.20, 20.88), "MALKAPUR (rail)", "≈ 90 km", "Malkapur", 0.15, GREEN)]
    for (lo, la), name, dist, ph, dy, col in routes:
        t0 = S.c(ph)
        pin(S, lo, la, name, t0, color=col, dy=dy, size=20, ring=False)
        a, b = merc(np.array([[lo, la]]))[0], merc(np.array([[LON, LAT]]))[0]
        ln, = S.ax.plot([a[0], a[0]], [a[1], a[1]], color=col, lw=3, ls=(0, (5, 4)), zorder=25)

        def up(t, ln=ln, a=a, b=b, t0=t0):
            g = ease2((t - t0) / 1.0)
            ln.set_data([a[0], a[0] + (b[0] - a[0]) * g], [a[1], a[1] + (b[1] - a[1]) * g])
        S.updaters.append(up)
    card(S, "Airport ≈ 135-140 km · Jalna / Malkapur stations ≈ 90 km", "Chhatrapati", 0.2, WHITE,
         S.c("From any"), size=32)
    card(S, "Then ≈ 2-3 hours by taxi or state bus", "From any", 0.2, WHITE, S.c("The best time"), size=34)
    # months strip
    ax2 = S.fig.add_axes([0.1, 0.08, 0.8, 0.12])
    ax2.set_xlim(0, 12)
    ax2.set_ylim(0, 1.6)
    ax2.set_axis_off()
    bgm = FancyBboxPatch((-0.2, -0.25), 12.4, 1.65, boxstyle="round,pad=0,rounding_size=0.2", fc="#07111d",
                         ec="none", alpha=0, clip_on=False)
    ax2.add_patch(bgm)
    MON = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    cols = [GREEN, GREEN, GREEN, MUTED, MUTED, PINK, PINK, PINK, PINK, GREEN, GREEN, GREEN]
    boxes = []
    for i, (m, c) in enumerate(zip(MON, cols)):
        r = Rectangle((i + 0.06, 0.4), 0.88, 0.8, fc=c, alpha=0)
        ax2.add_patch(r)
        tx = ax2.text(i + 0.5, 0.8, m, fontproperties=BOLD, size=24, color="#07111d", ha="center", va="center",
                      alpha=0)
        boxes.append((r, tx))
    lab = ax2.text(6, 0.1, "BEST: OCTOBER TO MARCH  ·  JUNE-SEPTEMBER: SLIPPERY TRAILS", fontproperties=BOLD,
                   size=22, color=WHITE, ha="center", va="center", alpha=0)
    t_m = S.c("The best time")

    def up2(t):
        for i, (r, tx) in enumerate(boxes):
            a = ease((t - t_m - 0.05 * i) / 0.3)
            r.set_alpha(0.9 * a)
            tx.set_alpha(a)
        lab.set_alpha(ease((t - t_m - 0.6) / 0.4))
        bgm.set_alpha(0.82 * ease((t - t_m) / 0.3))
    S.updaters.append(up2)


def s17_caveat(S):
    xsec(S, w=3.4, cy=0.35)
    S.text(0.5, 0.9, "BEFORE YOU GO", 0.3, size=46, box=True, pop=True, color=PINK)
    rows = [("Steep, uneven path down: carry water, go early", "The path down", WHITE),
            ("Some shore temples may be closed or underwater", "Some temples", CYAN),
            ("Protected, fragile lake: no litter, take nothing", "And remember", AMBER)]
    for i, (s, ph, col) in enumerate(rows):
        S.text(0.5, 0.74 - i * 0.1, s, S.c(ph), size=36, color=col, box=True)
    S.brand()


def s99_outro(S):
    w = xsec(S, w=3.4, cy=-0.02, water_col=LAKE_P)
    S.camera([(0, 0, -0.02, 3.4), (S.T, 0, -0.04, 3.0)])
    S.text(0.5, 0.86, "PUMP THE WATER OUT TO SAVE THE TEMPLES,", S.c("Should"), size=40, box=True, pop=True)
    S.text(0.5, 0.76, "OR LEAVE THE LAKE TO NATURE?", S.c("or leave"), size=40, box=True, pop=True, color=AMBER)
    S.text(0.5, 0.12, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=52, box=True, pop=True, color=CYAN)
    S.fade_in_out(0, 1.5)
