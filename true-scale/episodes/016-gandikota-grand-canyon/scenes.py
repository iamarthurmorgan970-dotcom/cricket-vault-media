"""Scenes for 016 Gandikota: India's Grand Canyon at true scale. S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.india import *
from engine.timeline import TL, setup as tl_setup
from matplotlib.patches import Polygon as MPoly, FancyBboxPatch, Rectangle

GANDI = (78.287, 14.815)
JMD = (78.39, 14.85)
KADAPA = (78.82, 14.47)
MUDDANURU = (78.40, 14.67)
YERRA = (78.54, 14.64)
BLR = (77.59, 12.97)
HYD = (78.49, 17.39)
BELUM = (78.11, 15.10)
ROCK, ROCK2, RIVER = "#b5513a", "#8e3b2a", "#3a8fc4"
# Schematic course of the Penna in this region (Natural Earth has no Penna line): approximate only.
PENNA = [(77.55, 14.45), (77.85, 14.6), (78.1, 14.74), (78.287, 14.80), (78.45, 14.76), (78.7, 14.62),
         (79.0, 14.52), (79.4, 14.48), (79.75, 14.45), (79.99, 14.44), (80.15, 14.6)]
AP_VIEW = (79.2, mercy(15.6), 9.5)
GANDI_VIEW = (78.45, mercy(14.75), 3.2)
KM_PER_DEG = 111.32 * np.cos(np.radians(GANDI[1]))


def ap_hl(S, t0, t1=None, peak=0.38):
    S.highlight(ST["Andhra Pradesh"], AMBER, t0, t1, peak=peak, lw=1.5)


def note(S, s, t0, x=0.985, y=0.065, size=18):
    S.text(x, y, s, t0, size=size, color=MUTED, ha="right", font=REG)


def label(S, lon, lat, s, t0, color=WHITE, size=24, t1=None):
    pin(S, lon, lat, s, t0, color=color, ring=False, dy=0, size=size, t1=t1)


def line_draw(S, xy, t0, color=AMBER, dur=1.4, lw=4, ls="-", z=26, t1=None, ax=None):
    ax = ax or S.ax
    p = np.asarray(xy, float)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    ln, = ax.plot([], [], color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round")
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


def penna(S, t0, dur=1.6, label_at=None):
    line_draw(S, merc(np.array(PENNA)), t0, color=RIVER, dur=dur, lw=4, z=20)
    if label_at:
        label(S, *label_at, "PENNA RIVER (approx.)", t0 + dur * 0.6, color=CYAN, size=20)


def fade(S, arts, t0, t1=None, peak=1.0):
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4)) * peak
        for x in arts:
            x.set_alpha(a)
    S.updaters.append(up)


def sub_axes(S, rect, xlim, ylim, t0=0.0, t1=None, bg=True):
    ax = S.fig.add_axes(rect)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_axis_off()
    if bg:
        r = FancyBboxPatch((-0.02, -0.04), 1.04, 1.08, transform=ax.transAxes,
                           boxstyle="round,pad=0,rounding_size=0.03", fc="#07111d", ec="none", alpha=0,
                           clip_on=False, zorder=0)
        ax.add_patch(r)
        fade(S, [r], t0, t1, 0.85)
    return ax


def hbar(S, ax, y, val, color, name, valtext, t0, h=0.45, t1=None, size=24, grow=1.0):
    r = Rectangle((0, y - h / 2), 0, h, color=color, zorder=3, alpha=0)
    ax.add_patch(r)
    nm = ax.text(0, y + h / 2 + 0.05, name, fontproperties=BOLD, size=size * 0.85, color=WHITE, va="bottom",
                 alpha=0, zorder=4)
    xr = ax.get_xlim()[1]
    vt = ax.text(0, y, valtext, fontproperties=BOLD, size=size, color=color, va="center", alpha=0, zorder=4)
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
        g = ease2((t - t0) / grow)
        r.set_width(val * g)
        r.set_alpha(a)
        nm.set_alpha(a)
        vt.set_position((val * g + xr * 0.012, y))
        vt.set_alpha(a * ease((t - t0 - grow * 0.7) / 0.3))
    S.updaters.append(up)


def gorge_section(S, ax, t0, w=150, d=90, hill=100, t1=None, fort=True):
    """Schematic cross-section of the gorge in metres: river channel w wide, cliffs d high, fort on right hill."""
    L = MPoly([(-420, -30), (-420, d + 8), (-160, d + 4), (-40, d), (-8, d - 20), (0, 0), (0, -30)], closed=True,
              fc=ROCK, ec=ROCK2, lw=2, zorder=3, alpha=0)
    R = MPoly([(w, -30), (w, 0), (w + 10, d - 25), (w + 30, d), (w + 140, hill), (w + 330, hill + 6),
               (w + 520, d + 2), (w + 520, -30)], closed=True, fc=ROCK, ec=ROCK2, lw=2, zorder=3, alpha=0)
    water = Rectangle((0, -30), w, 34, fc=RIVER, ec="none", zorder=2, alpha=0)
    arts = [L, R, water]
    for k in range(1, 5):            # rock layers
        yy = d * k / 5
        a1, = ax.plot([-420, -12], [yy, yy], color=ROCK2, lw=1.4, zorder=3.5, alpha=0)
        a2, = ax.plot([w + 6 + 10 * k / 5, w + 520], [yy, yy], color=ROCK2, lw=1.4, zorder=3.5, alpha=0)
        arts += [a1, a2]
    for p in (L, R, water):
        ax.add_patch(p)
    if fort:
        x0 = w + 170
        walls = [Rectangle((x0, hill + 6), 160, 26, fc="#d9c7a3", ec="#8a7a5a", lw=2, zorder=4, alpha=0)]
        for k in range(6):
            walls.append(Rectangle((x0 + k * 30, hill + 32), 14, 10, fc="#d9c7a3", ec="#8a7a5a", lw=1.5, zorder=4,
                                   alpha=0))
        walls.append(Rectangle((x0 - 14, hill + 6), 26, 46, fc="#e6d6b4", ec="#8a7a5a", lw=2, zorder=4.5, alpha=0))
        walls.append(Rectangle((x0 + 148, hill + 6), 26, 46, fc="#e6d6b4", ec="#8a7a5a", lw=2, zorder=4.5, alpha=0))
        for p in walls:
            ax.add_patch(p)
        arts += walls
    fade(S, arts, t0, t1)
    return arts


def card(S, text, t0, y=0.2, color=WHITE, t1=None, size=34, x=0.5, ha="center"):
    t0 = S.c(t0) if isinstance(t0, str) else t0
    return S.text(x, y, text, t0, t1, size=size, color=color, box=True, ha=ha)


def plain(S):
    S.ax.set_xlim(0, 1)
    S.ax.set_ylim(0, 1)
    S.brand()


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    t_z = S.c("In a quiet corner")
    india(S, [(0, *INDIA_VIEW), (t_z + 2.5, *GANDI_VIEW), (S.T, 78.45, mercy(14.75), 2.8)])
    ap_hl(S, 0.8, t_z + 2.6, peak=0.8)
    label(S, *KADAPA, "KADAPA", t_z + 3.2, size=20)
    penna(S, t_z + 2.8)
    pin(S, *GANDI, "GANDIKOTA", t_z + 3.2, dy=1.3)
    S.headline("\"INDIA'S GRAND CANYON\"", S.c("India's Grand Canyon"), S.c("But the real"), size=50, color=AMBER)
    t_b = S.c("But the real")
    ax = sub_axes(S, [0.08, 0.08, 0.84, 0.26], (0, 560), (-0.2, 2.2), t0=t_b, t1=S.c("So is the nickname"))
    hbar(S, ax, 1.35, 446, AMBER, "GRAND CANYON, ARIZONA (USA)", "≈ 446 km", t_b + 0.4, t1=S.c("So is the nickname"))
    hbar(S, ax, 0.25, 7, CYAN, "GANDIKOTA GORGE, ANDHRA PRADESH", "≈ 7 km", S.c("is about seven"),
         t1=S.c("So is the nickname"))
    S.headline("SO IS THE NICKNAME FAIR?", S.c("So is the nickname"), S.c("In this video"), size=50)
    S.headline("BOTH, SIDE BY SIDE, AT TRUE SCALE", S.c("In this video"), size=46, color=CYAN)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    india(S, [(0, 78.45, mercy(14.75), 2.8), (S.T, 78.45, mercy(14.75), 2.6)])
    penna(S, 0.0, dur=0.1)
    S.text(0.5, 0.66, "GANDIKOTA", 0.3, size=110, pop=True, box=True)
    S.text(0.5, 0.45, "INDIA'S GRAND CANYON, AT TRUE SCALE", 0.8, size=48, color=AMBER, pop=True, box=True)
    S.text(0.5, 0.93, "TRUE SCALE", 0.0, size=28, color=CYAN)


def s03_where(S):
    t_z = S.c("Kadapa district")
    india(S, [(0, *INDIA_VIEW), (t_z, *AP_VIEW), (S.c("about fifteen"), 78.45, mercy(14.8), 2.6),
              (S.T, 78.4, mercy(14.8), 2.4)])
    ap_hl(S, 0.6, S.c("about fifteen"))
    state_tag(S, "ANDHRA PRADESH · KADAPA DISTRICT", t_z)
    pin(S, *GANDI, "GANDIKOTA", t_z + 0.6, dy=0.9)
    penna(S, S.c("Penna river"), label_at=(79.25, 14.3))
    pin(S, *KADAPA, "KADAPA", t_z + 1.0, color=WHITE, ring=False, dy=0.6, size=20)
    pin(S, *JMD, "JAMMALAMADUGU", S.c("Jammalamadugu"), color=WHITE, dy=-3.5, ring=False, size=20, dx=2,
        ha="left")
    card(S, "≈ 15 km from Jammalamadugu", "about fifteen", 0.14, WHITE, t1=S.c("it has carved"))
    pin(S, 78.1, 14.92, "ERRAMALA HILLS", S.c("Erramala"), color=PINK, ring=False, dy=0.5, size=24, dx=-3,
        ha="right")
    card(S, "River + red hills = a gorge", S.c("it has carved"), 0.14, AMBER)


def s04_name(S):
    plain(S)
    ax = S.ax
    S.text(0.5, 0.88, "IN TELUGU", 0.2, size=34, color=MUTED)
    S.text(0.3, 0.64, "GANDI", S.c("gandi"), size=110, color=ROCK, pop=True)
    S.text(0.3, 0.5, "= gorge", S.c("means gorge"), size=48)
    S.text(0.7, 0.64, "KOTA", S.c("kota"), size=110, color=AMBER, pop=True)
    S.text(0.7, 0.5, "= fort", S.c("means fort"), size=48)
    S.text(0.5, 0.3, "GORGE FORT", S.c("A gorge fort"), size=80, color=WHITE, box=True, pop=True)
    S.text(0.5, 0.13, "≈ 900 years of building walls on top of the canyon walls", S.c("For about"), size=32,
           color=CYAN)


def s05_gorge(S):
    ax = S.ax
    ax.set_xlim(-700, 1000)
    ax.set_ylim(-110, 230)
    S.brand()
    gorge_section(S, ax, 0.3, fort=False)
    fort = gorge_section(S, ax, S.c("And on the right bank"), fort=True)
    S.headline("THE GORGE IN CROSS-SECTION", 0.3, size=44, color=WHITE)
    t_w = S.c("one hundred to two hundred")
    ln, = ax.plot([0, 150], [-42, -42], color=CYAN, lw=3, alpha=0)
    tx = ax.text(75, -50, "RIVER CHANNEL ≈ 100–200 m wide", fontproperties=BOLD, size=28, color=CYAN, ha="center",
                 va="top", alpha=0)
    fade(S, [ln, tx], t_w, S.c("The gorge was the moat"))
    t_c = S.c("three hundred feet")
    v, = ax.plot([-440, -440], [0, 90], color=AMBER, lw=3, alpha=0)
    vt = ax.text(-455, 45, "CLIFFS\n≈ 90 m\n(≈ 300 ft)", fontproperties=BOLD, size=26, color=AMBER, ha="right",
                 va="center", alpha=0)
    fade(S, [v, vt], t_c)
    t_f = S.c("about one hundred metres")
    v2, = ax.plot([690, 690], [0, 106], color=GREEN, lw=3, alpha=0)
    vt2 = ax.text(702, 55, "FORT ≈ 100 m\nabove the river", fontproperties=BOLD, size=26, color=GREEN, ha="left",
                  va="center", alpha=0)
    fade(S, [v2, vt2], t_f)
    S.caption("THE GORGE WAS THE MOAT", S.c("The gorge was the moat"), color=AMBER, size=40)
    note(S, "Schematic: widths and heights as quoted by sources, vertical scale exaggerated", 0.6, y=0.82)


def s06_length(S):
    t_lay = S.c("lay the Grand Canyon")
    end_lon = GANDI[0] + 446 / KM_PER_DEG
    india(S, [(0, 78.4, mercy(14.8), 2.2), (S.c("about seven kilometres"), 78.35, mercy(14.8), 0.9),
              (t_lay, 80.6, mercy(15.0), 9.0), (S.T, 80.6, mercy(15.0), 8.6)])
    ap_hl(S, t_lay, peak=0.45)
    pin(S, *GANDI, "GANDIKOTA", 0.3, dy=0.6, ring=False, size=20)
    S.headline("GRAND CANYON ≈ 277 river miles ≈ 446 km", 0.4, S.c("At Gandikota"), size=42, color=AMBER)
    gp = merc(np.array([[78.25, 14.815], [78.315, 14.80]]))
    line_draw(S, gp, S.c("about seven kilometres"), color=CYAN, lw=8, dur=0.8)
    S.headline("GANDIKOTA GORGE ≈ 7 km", S.c("At Gandikota"), t_lay, size=42, color=CYAN)
    xs = np.linspace(GANDI[0], end_lon, 50)
    line_draw(S, merc(np.column_stack([xs, np.full_like(xs, GANDI[1])])), t_lay + 0.4, color=AMBER, lw=7,
              dur=S.c("keeps going") - t_lay + 1.5)
    S.headline("THE GRAND CANYON, LAID FROM GANDIKOTA", t_lay, S.c("That's more than"), size=42, color=AMBER)
    label(S, 80.1, 14.1, "COAST", S.c("reaches the coast"), color=WHITE, size=20)
    label(S, 81.3, 15.6, "≈ 250 km OUT TO SEA", S.c("out to sea"), color=AMBER, size=26)
    label(S, 83.8, 15.6, "BAY OF BENGAL", S.c("Bay of Bengal"), color=CYAN, size=24)
    S.caption("446 km ÷ 7 km ≈ MORE THAN 60 GANDIKOTAS", S.c("That's more than"), color=WHITE, size=40)
    note(S, "Straight line for scale; the real canyon winds", t_lay, y=0.82)


def s07_depth(S):
    ax = S.ax
    ax.set_xlim(0, 3200)
    ax.set_ylim(-2550, 900)
    S.brand()
    S.headline("HOW DEEP? RIM TO RIVER", 0.3, size=44)
    ax.plot([0, 3200], [0, 0], color=MUTED, lw=2)
    for d in (500, 1000, 1500):
        ax.plot([0, 3200], [-d, -d], color="#16283c", lw=1, zorder=0)
        ax.text(20, -d + 15, f"{d:,} m", fontproperties=REG, size=16, color=MUTED, va="bottom")
    cols = [("GRAND CANYON\naverage", 1600, AMBER, "one point six", 650, "≈ 1.6 km"),
            ("GRAND CANYON\ndeepest", 1829, PINK, "deepest", 1500, "≈ 1,829 m"),
            ("GANDIKOTA\ncliffs", 90, CYAN, "about ninety metres", 2550, "≈ 90 m")]
    for name, d, col, ph, cx, lab in cols:
        t0 = S.c(ph)
        r = Rectangle((cx - 230, 0), 460, 0, color=col, alpha=0, zorder=3)
        ax.add_patch(r)
        nm = ax.text(cx, 40, name, fontproperties=BOLD, size=24, color=col, ha="center", va="bottom", alpha=0)
        vt = ax.text(cx, 0, lab, fontproperties=BOLD, size=28, color=WHITE, ha="center", va="top", alpha=0, zorder=6)

        def up(t, r=r, d=d, t0=t0, nm=nm, vt=vt, cx=cx):
            g = ease2((t - t0) / 1.2)
            r.set_height(-d * g)
            a = ease((t - t0) / 0.4)
            r.set_alpha(0.85 * a)
            nm.set_alpha(a)
            vt.set_position((cx, -d * g - 25))
            vt.set_alpha(a)
        S.updaters.append(up)
    t_b = S.c("two Burj Khalifas")
    for k in range(2):
        y0 = -1829 + k * 828
        tower = MPoly([(1430, y0), (1570, y0), (1520, y0 + 500), (1505, y0 + 700), (1500, y0 + 828),
                       (1495, y0 + 700), (1480, y0 + 500)], closed=True, fc=WHITE, ec="#07111d", lw=2, zorder=5,
                      alpha=0)
        ax.add_patch(tower)
        fade(S, [tower], t_b + 0.5 * k)
    card(S, "2 × Burj Khalifa (828 m)\n= 1,656 m: still fits inside", t_b, 0.5, WHITE, size=28, x=0.79)
    S.caption("ROUGHLY 20× SHALLOWER", S.c("Roughly twenty"), color=CYAN, size=40)


def s08_width(S):
    plain(S)
    S.headline("HOW WIDE? RIM TO RIM", 0.3, size=44)
    ax = sub_axes(S, [0.08, 0.42, 0.84, 0.36], (0, 36), (-0.3, 2.6), t0=0.6)
    hbar(S, ax, 1.9, 29, PINK, "GRAND CANYON · widest", "up to ≈ 29 km", S.c("twenty nine"))
    hbar(S, ax, 1.0, 16, AMBER, "GRAND CANYON · near the main viewpoints", "≈ 16 km", S.c("sixteen"))
    hbar(S, ax, 0.1, 0.2, CYAN, "GANDIKOTA", "≈ 0.1–0.2 km (100–200 m)", S.c("Gandikota is one"))
    t_tw = S.c("But here's the twist")
    ax2 = sub_axes(S, [0.08, 0.08, 0.84, 0.22], (0, 260), (-0.3, 1.9), t0=t_tw)
    hbar(S, ax2, 1.2, 180, PINK, "GRAND CANYON · narrowest (Marble Canyon)", "≈ 180 m", S.c("Marble Canyon"))
    hbar(S, ax2, 0.2, 200, CYAN, "GANDIKOTA · up to", "≈ 100–200 m", S.c("So at its tightest"))
    S.text(0.5, 0.345, "ZOOMED IN: metres", t_tw, size=24, color=MUTED, font=REG)


def s09_rock(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    S.brand()
    t0 = 0.4
    bands = [ROCK, "#c9714f", ROCK2, "#d4896a", ROCK, "#a8492f", "#c9714f"]
    arts = []
    for i, c in enumerate(bands):
        y0 = 0.6 + i * 0.55
        xx = np.linspace(0.5, 7.5, 80)
        top = y0 + 0.55 + 0.05 * np.sin(xx * 9 + i)
        p = MPoly(np.vstack([np.column_stack([xx, np.full_like(xx, y0)]), np.column_stack([xx, top])[::-1]]),
                  closed=True, fc=c, ec="none", zorder=2, alpha=0)
        ax.add_patch(p)
        arts.append(p)
    fade(S, arts, t0)
    t_r = S.c("ripple marks")
    for i in range(3):
        xx = np.linspace(1 + i * 2.1, 2.8 + i * 2.1, 60)
        ln, = ax.plot(xx, 3.0 + 0.09 * np.sin(xx * 14), color=WHITE, lw=2.5, zorder=3, alpha=0)
        fade(S, [ln], t_r + 0.2 * i)
    S.text(0.25, 0.86, "GANDIKOTA QUARTZITE", 0.3, size=40, color=AMBER, box=True)
    card(S, "part of the CUDDAPAH SUPERGROUP", S.c("Cuddapah"), 0.78, WHITE, size=28, x=0.25)
    card(S, "ripple marks · cross-bedding", t_r, 0.62, WHITE, size=26, x=0.25)
    steps = [("SAND", "It began as sand"), ("BURIED", "buried"), ("PRESSED + CEMENTED", "pressed"),
             ("QUARTZITE", "red quartzite")]
    for i, (s, ph) in enumerate(steps):
        S.text(0.74, 0.82 - i * 0.1, s, S.c(ph), size=36, color=[MUTED, WHITE, WHITE, AMBER][i], pop=True)
    t_p = S.c("Proterozoic")
    card(S, "PROTEROZOIC EON (2,500–539 million years ago)\nexact age still debated", t_p, 0.36, CYAN, size=28,
         x=0.74)
    t_g = S.c("The Grand Canyon's oldest")
    card(S, "GRAND CANYON: oldest rocks ≈ 2 billion years\ncanyon carved in the last 5–6 million", t_g, 0.16, PINK,
         size=28, x=0.74)
    note(S, "Rock layers illustrative", 0.5)


def s10_fort(S):
    tl_setup(S)
    tl = TL(S, nice=[1, 2, 5])
    tl.camera([(0, 1400, 900), (S.T, 1410, 880)])
    S.headline("A GORGE FORT, 900 YEARS OLD", 0.3, size=44, color=AMBER)
    tl.marker(1123, "SAND FORT", S.c("eleven twenty three"), sub="1123 · Gandikota Kaifiyat", color=AMBER, side=1,
              h=0.38, size=26)
    tl.span(1239, 1304, -0.45, CYAN, "KAKATIYAS (1239–1304)", S.c("Under the Kakatiyas"), dur=1.0)
    card(S, "PEMMASANI NAYAKS · Vijayanagara commanders · held it ≈ 300 years", S.c("Pemmasani"), 0.2, GREEN,
         size=30)
    card(S, "≈ 40 bastions · the gorge guards the west and north", S.c("forty bastions"), 0.1, WHITE, size=30)


def s11_rulers(S):
    plain(S)
    S.headline("WHO HELD GANDIKOTA", 0.3, size=44)
    rows = [("Kalyani Chalukyas (1123)", 0.15, MUTED), ("Kakatiyas", 0.15, MUTED),
            ("Vijayanagara · Pemmasani Nayaks", 0.15, MUTED),
            ("Qutb Shahis of Golconda · Mir Jumla, 1650", "Qutb Shahi", AMBER), ("Mughals", "the Mughals", WHITE),
            ("Nawabs of Kadapa", "Nawabs", WHITE), ("Kingdom of Mysore", "Kingdom of Mysore", WHITE),
            ("British (from 1791)", "the British", CYAN)]
    for i, (s, ph, col) in enumerate(rows):
        t0 = S.c(ph) if isinstance(ph, str) else 0.4 + 0.25 * i
        S.text(0.5, 0.78 - i * 0.075, f"{i + 1}. {s}", t0, size=34, color=col)
    S.caption("8 POWERS IN ≈ 700 YEARS", S.c("Eight different"), color=AMBER, size=40)


def s12_mirjumla(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    S.brand()
    t_m = S.c("Jama Masjid")
    # mosque with two minarets (illustration)
    parts = [Rectangle((2.2, 1.2), 3.6, 2.2, fc="#d9c7a3", ec="#8a7a5a", lw=2),
             MPoly([(2.6, 3.4), (5.4, 3.4), (5.0, 3.9), (3.0, 3.9)], closed=True, fc="#d9c7a3", ec="#8a7a5a", lw=2)]
    for x in (1.7, 5.9):
        parts += [Rectangle((x, 1.2), 0.45, 3.7, fc="#e6d6b4", ec="#8a7a5a", lw=2),
                  matplotlib.patches.Ellipse((x + 0.225, 5.05), 0.6, 0.55, fc="#e6d6b4", ec="#8a7a5a", lw=2)]
    for k in range(3):
        parts.append(matplotlib.patches.Ellipse((3.0 + k * 1.0, 1.9), 0.55, 1.2, fc="#5b4a35", ec="none"))
    for p in parts:
        p.set_zorder(3)
        ax.add_patch(p)
    fade(S, parts, t_m)
    S.headline("MIR JUMLA'S MARK", 0.3, size=44, color=AMBER)
    card(S, "JAMA MASJID · two minarets", t_m, 0.74, WHITE, size=30, x=0.25)
    card(S, "CANNON FOUNDRIES", S.c("cannon foundries"), 0.66, WHITE, size=30, x=0.68)
    card(S, "TAVERNIER · French gem merchant, came to meet him", S.c("Tavernier"), 0.55, CYAN, size=26, x=0.70)
    t_d = S.c("diamonds")
    gem = MPoly([(11.0, 3.6), (11.7, 4.3), (12.9, 4.3), (13.6, 3.6), (12.3, 1.8)], closed=True, fc="#bfe9ff",
                ec=WHITE, lw=2.5, zorder=4, alpha=0)
    ax.add_patch(gem)
    fade(S, [gem], t_d)
    card(S, "DIAMONDS were mined in this region", t_d, 0.12, AMBER, size=32, x=0.76)
    note(S, "Illustration, not the real mosque", t_m)


def s13_inside(S):
    ax = S.ax
    ax.set_xlim(-700, 1000)
    ax.set_ylim(-110, 460)
    S.brand()
    gorge_section(S, ax, 0.2)
    S.headline("INSIDE THE WALLS", 0.3, size=44, color=AMBER)
    items = [("MADHAVARAYA TEMPLE · 36-pillar hall", "Madhavaraya"),
             ("RAGHUNATHA TEMPLE · built by the Pemmasani chiefs", "Raghunatha"),
             ("GRANARY · 2 rows of 12 pillars", "granary"),
             ("JAMA MASJID · mini CHARMINAR · KATHULA KONERU", "The mosque")]
    for i, (s, ph) in enumerate(items):
        card(S, s, ph, 0.78 - i * 0.09, WHITE, size=30, t1=S.c("Then you step") + 0.2)
    S.caption("...THEN THE CANYON DROPS AWAY", S.c("Then you step"), color=AMBER, size=40)
    note(S, "Schematic", 0.5)


def s14_news(S):
    plain(S)
    S.headline("GANDIKOTA IS CHANGING FAST", 0.3, size=44, color=AMBER)
    card(S, "AUG 2025 · foundation stone for a ≈ ₹78 crore tourism project", "In August", 0.74, WHITE, size=32)
    card(S, "DEC 2025 · plans reported: tent city, ropeway, glass walkway", "By December", 0.6, CYAN, size=32)
    card(S, "JAN 2026 · 3-day Gandikota festival, helicopter rides over the gorge", "In January", 0.46, GREEN,
         size=32)
    S.text(0.5, 0.24, "SEVERAL ARE STILL PLANS: CHECK WHAT'S OPEN", S.c("Several of these"), size=40, color=PINK,
           box=True, pop=True)
    note(S, "Sources: New Indian Express (Aug 2025), Deccan Chronicle (Dec 2025, Jan 2026)", 0.6)


def s15_reasons(S):
    india(S, [(0, 77.4, mercy(14.75), 3.2), (S.T, 77.45, mercy(14.75), 3.0)])
    penna(S, 0.0, dur=0.1)
    pin(S, *GANDI, "GANDIKOTA", 0.3, dy=0.6, size=22)
    S.headline("WHY GO?", 0.2, size=48, color=AMBER)
    rs = [("1 · Red quartzite at sunrise and sunset", "One."), ("2 · A canyon + a 900-year-old fort", "Two."),
          ("3 · Quiet, for now", "Three."), ("4 · Add the Belum Caves nearby", "Four.")]
    for i, (s, ph) in enumerate(rs):
        S.text(0.06, 0.74 - i * 0.1, s, S.c(ph), size=36, ha="left", box=True)
    card(S, "Grand Canyon NP: ≈ 4.4 million visitors in 2025", "four point four", 0.16, PINK, size=30, x=0.06,
         ha="left", t1=S.c("Four."))
    pin(S, *BELUM, "BELUM CAVES", S.c("Belum Caves"), color=CYAN, dy=0.6, size=22)


def s16_getthere(S):
    t_b = S.c("Bengaluru")
    india(S, [(0, 78.55, mercy(14.75), 2.0), (S.c("Kadapa is"), 78.6, mercy(14.7), 2.0),
              (t_b, 78.6, mercy(15.2), 13.5), (S.T, 78.6, mercy(15.2), 13.0)])
    ap_hl(S, t_b, peak=0.4)
    S.headline("GETTING THERE", 0.2, t_b, size=44, color=AMBER)
    pin(S, *GANDI, "GANDIKOTA", 0.3, dy=0.6, size=22)
    seq = [(JMD, "JAMMALAMADUGU ≈ 15 km", "Jammalamadugu", WHITE),
           (KADAPA, "KADAPA ≈ 80 km · nearest airport", "Kadapa is", WHITE),
           (MUDDANURU, "MUDDANURU station ≈ 26 km", "Muddanuru", CYAN),
           (YERRA, "YERRAGUNTLA station ≈ 47 km", "Yerraguntla", CYAN)]
    for i, (ll, txt, ph, col) in enumerate(seq):
        t1 = S.c(seq[i + 1][2]) if i + 1 < len(seq) else t_b
        pin(S, *ll, txt, S.c(ph), color=col, dy=-1.2, size=24, t1=t1)
    pin(S, *BLR, "BENGALURU ≈ 300 km", t_b, color=WHITE, dy=0.3, size=22)
    pin(S, *HYD, "HYDERABAD ≈ 400 km", S.c("Hyderabad"), color=WHITE, dy=0.3, size=22)
    card(S, "BEST TIME: OCTOBER TO FEBRUARY", "The best time", 0.1, GREEN, size=40, x=0.7)
    note(S, "Distances approximate", t_b, y=0.82)


def s17_caveat(S):
    ax = S.ax
    ax.set_xlim(-700, 1000)
    ax.set_ylim(-110, 460)
    S.brand()
    gorge_section(S, ax, 0.2)
    S.headline("BEFORE YOU GO", 0.3, size=44, color=PINK)
    card(S, "SHEER DROPS: stay back from the edge", "sheer drops", 0.78, WHITE, size=32)
    card(S, "SUMMER: very hot, river can run low", "The summer", 0.69, WHITE, size=32)
    card(S, "FRAGILE RUINS: don't climb, carry your rubbish out", "the ruins are fragile", 0.6, WHITE, size=32)


def s18_outro(S):
    india(S, [(0, 78.45, mercy(14.6), 3.2), (S.T, 78.45, mercy(14.6), 2.9)])
    penna(S, 0.0, dur=0.1)
    pin(S, *GANDI, "GANDIKOTA", 0.3, dy=-3, size=22)
    S.headline("AT TRUE SCALE", 0.3, size=44)
    card(S, "THE REAL ONE: 60× longer · ≈ 20× deeper", "more than sixty", 0.8, AMBER, size=38)
    card(S, "GANDIKOTA: a 900-year-old fort on the rim", "But Gandikota has", 0.71, CYAN, size=38)
    S.text(0.5, 0.3, "REAL GRAND CANYON or INDIA'S? Tell me below", S.c("Which would you"), size=40, color=WHITE,
           box=True, pop=True)
    S.text(0.5, 0.15, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=44, color=AMBER, box=True, pop=True)
    S.fade_in_out(0, 1.0)


def hold(sid):
    return {"s01_hook": 0.6, "s06_length": 1.5, "s07_depth": 1.0, "s08_width": 1.0, "s18_outro": 1.5}.get(sid, 0.3)
