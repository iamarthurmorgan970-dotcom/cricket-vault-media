"""Scenes for 036 Rann of Kutch and Dholavira. S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.india import *
from engine.timeline import TL, setup as tl_setup
from matplotlib.patches import Polygon as MPoly, Ellipse

SALT, MUD, WET = "#e9f1f7", "#8a7a63", "#2f7fb0"
BHUJ = (69.67, 23.25)
DHORDO = (69.66, 23.86)
KALO = (69.80, 23.88)
DHOLAVIRA = (70.214, 23.889)
KHAVDA = (69.72, 23.85)

# Approximate (schematic) outlines, lon/lat. Not survey boundaries.
GREAT_RANN = [(68.75, 23.95), (68.95, 24.25), (69.4, 24.35), (69.9, 24.4), (70.4, 24.5), (70.9, 24.4),
              (71.25, 24.15), (71.1, 23.92), (70.75, 23.72), (70.35, 23.62), (70.05, 23.68), (69.95, 23.92),
              (69.8, 23.92), (69.66, 23.885), (69.45, 23.9), (69.1, 23.9)]
LITTLE_RANN = [(70.55, 23.55), (70.9, 23.62), (71.35, 23.55), (71.65, 23.3), (71.55, 23.05), (71.15, 22.95),
               (70.8, 23.05), (70.6, 23.3)]
KHADIR = ((70.25, 23.875), 0.42, 0.13)       # centre, width (lon), height (lat)

KUTCH_VIEW = (70.1, mercy(23.6), 5.2)


def mpoly(pts):
    return merc(np.array(pts))


def _clip_to_india(pts):
    """Keep the schematic Rann inside India's official boundary (no spill into Pakistan)."""
    from shapely.geometry import Polygon as SP
    from shapely.ops import unary_union
    ind = unary_union([SP(r).buffer(0) for r in INDIA_POV if len(r) > 3])
    g = SP(pts).buffer(0).intersection(ind)
    if g.geom_type == "MultiPolygon":
        g = max(g.geoms, key=lambda q: q.area)
    return [tuple(c) for c in np.array(g.exterior.coords)]


GREAT_RANN = _clip_to_india(GREAT_RANN)


def rann_layer(S, t_in=0.0, wet_until=None, dry_by=None, little=True, start=SALT, alpha=0.92):
    """Draws the Rann (approximate). Colour can go from wet blue to white salt between wet_until and dry_by."""
    polys = [MPoly(mpoly(GREAT_RANN), closed=True, fc=start, ec="none", zorder=5, alpha=0)]
    if little:
        polys.append(MPoly(mpoly(LITTLE_RANN), closed=True, fc=start, ec="none", zorder=5, alpha=0))
    for p in polys:
        S.ax.add_patch(p)
    (cx, cy), w, h = KHADIR
    c = merc(np.array([[cx, cy]]))[0]
    isl = Ellipse(c, w, h * 1.1, fc="#2c4262", ec="#4f6d94", lw=1.2, zorder=5.5, alpha=0)
    S.ax.add_patch(isl)
    a_rgb = np.array(matplotlib.colors.to_rgb(WET))
    b_rgb = np.array(matplotlib.colors.to_rgb(SALT))

    def up(t):
        a = ease((t - t_in) / 0.6) * alpha
        for p in polys:
            p.set_alpha(a)
            if wet_until is not None:
                u = ease2((t - wet_until) / max(dry_by - wet_until, 0.5))
                p.set_facecolor(tuple(a_rgb + (b_rgb - a_rgb) * u))
        isl.set_alpha(ease((t - t_in) / 0.6))
    S.updaters.append(up)
    return polys


def kutch(S, keys=None, hl=False, **kw):
    india(S, keys or [(0, *KUTCH_VIEW), (S.T, *KUTCH_VIEW)], hl=["Gujarat"] if hl else None)
    return rann_layer(S, **kw)


def label(S, lon, lat, s, t0, color=WHITE, size=24, t1=None):
    pin(S, lon, lat, s, t0, color=color, ring=False, dy=0, size=size, t1=t1)


def note(S, s, t0, x=0.985, y=0.08, size=18):
    S.text(x, y, s, t0, size=size, color=MUTED, ha="right", font=REG)


def hdim(S, x0, x1, y, lab, t0, color=AMBER, dy=10, size=30):
    ln, = S.ax.plot([x0, x0], [y, y], color=color, lw=3, zorder=20, alpha=0)
    tx = S.ax.text((x0 + x1) / 2, y + dy, lab, fontproperties=BOLD, size=size, color=color, ha="center",
                   va="bottom", zorder=21, alpha=0)

    def up(t):
        g = ease2((t - t0) / 0.9)
        ln.set_data([x0, x0 + (x1 - x0) * g], [y, y])
        ln.set_alpha(ease((t - t0) / 0.3))
        tx.set_alpha(ease((t - t0 - 0.5) / 0.4))
    S.updaters.append(up)


def vdim(S, x, y0, y1, lab, t0, color=CYAN, size=30, dx=8, ha="left"):
    ln, = S.ax.plot([x, x], [y0, y0], color=color, lw=3, zorder=20, alpha=0)
    tx = S.ax.text(x + dx, (y0 + y1) / 2, lab, fontproperties=BOLD, size=size, color=color, ha=ha,
                   va="center", zorder=21, alpha=0)

    def up(t):
        g = ease2((t - t0) / 0.9)
        ln.set_data([x, x], [y0, y0 + (y1 - y0) * g])
        ln.set_alpha(ease((t - t0) / 0.3))
        tx.set_alpha(ease((t - t0 - 0.5) / 0.4))
    S.updaters.append(up)


def route(S, pts, t0, color=AMBER, dur=1.4, lw=4, ls=(0, (6, 4)), t1=None):
    p = merc(np.array(pts))
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    ln, = S.ax.plot([], [], color=color, lw=lw, ls=ls, zorder=26, solid_capstyle="round")
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        g = ease2((t - t0) / dur) * seg[-1]
        k = np.searchsorted(seg, g)
        if g <= 0:
            ln.set_data([], [])
            return
        k = min(max(k, 1), len(p) - 1)
        f = (g - seg[k - 1]) / max(seg[k] - seg[k - 1], 1e-9)
        q = np.vstack([p[:k], p[k - 1] + (p[k] - p[k - 1]) * min(f, 1)])
        ln.set_data(q[:, 0], q[:, 1])
        ln.set_alpha(min(1, ease((t1 - t) / 0.4)))
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
        t1_ = S.T + 1 if t1 is None else t1
        S.updaters.append(lambda t: r.set_alpha(0.85 * min(ease((t - t0) / 0.4), ease((t1_ - t) / 0.4))))
    return ax


def fader(S, arts, t0, t1=None, peak=1.0):
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4)) * peak
        for x in arts:
            x.set_alpha(a)
    S.updaters.append(up)


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    t_z = S.c("huge stretch")
    t_dry = S.c("Then the water")
    kutch(S, [(0, *INDIA_VIEW), (t_z + 0.3, *KUTCH_VIEW), (S.T, 70.1, mercy(23.7), 4.6)],
          t_in=t_z + 0.6, wet_until=t_dry, dry_by=t_dry + 2.5)
    S.headline("A SHALLOW WETLAND IN THE MONSOON...", S.c("shallow wetland"), t_dry + 0.5, size=40, color=CYAN)
    S.headline("...THEN THOUSANDS OF km² OF WHITE SALT", S.c("a flat, white"), S.c("And on an island"), size=40)
    pin(S, *DHOLAVIRA, "DHOLAVIRA", S.c("on an island"), color=AMBER, dy=1.6)
    S.headline("A CITY PLANNED ≈ 5,000 YEARS AGO", S.c("on an island"), S.c("This is the Rann"), size=40,
               color=AMBER)
    S.headline("THE RANN OF KUTCH · SEASON NOW OPEN", S.c("This is the Rann"), size=40, color=WHITE)
    note(S, "Rann outline approximate", t_z + 0.8)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    kutch(S, [(0, 70.1, mercy(23.7), 4.6), (S.T, 70.1, mercy(23.75), 4.2)])
    S.text(0.5, 0.74, "THE RANN OF KUTCH", 0.3, size=96, pop=True, box=True)
    S.text(0.5, 0.6, "INDIA'S WHITE DESERT + A 5,000-YEAR-OLD CITY", 0.8, size=48, color=AMBER, pop=True,
           box=True)
    S.text(0.5, 0.93, "TRUE SCALE", 0.0, size=28, color=CYAN)


def s03_where(S):
    t_z = S.c("Kutch district")
    kutch(S, [(0, *INDIA_VIEW), (t_z + 0.2, 69.9, mercy(24.0), 9.5), (S.T, 69.9, mercy(24.0), 8.8)], t_in=t_z,
          hl=True)
    state_tag(S, "GUJARAT · KUTCH DISTRICT", t_z)
    label(S, 68.6, 25.4, "SINDH (PAKISTAN)", S.c("Sindh"), color=WHITE)
    label(S, 71.2, 26.0, "THAR DESERT", S.c("Thar"), color=WHITE)
    label(S, 69.3, 22.65, "GULF OF KUTCH", S.c("Gulf of Kutch"), color=CYAN, size=22)
    label(S, 67.4, 22.3, "ARABIAN SEA", S.c("Arabian Sea"), color=CYAN, size=22)
    label(S, 69.9, 24.15, "GREAT RANN", S.c("The Great Rann"), color=AMBER, size=26)
    label(S, 71.1, 23.3, "LITTLE RANN", S.c("Little Rann"), color=AMBER, size=22)
    note(S, "Rann outlines approximate", t_z + 0.5)


def s04_size(S):
    kutch(S, [(0, 70.4, mercy(23.75), 5.6), (S.T, 70.4, mercy(23.75), 5.2)])
    S.headline("HOW BIG? DEPENDS WHERE YOU DRAW THE EDGE", 0.4, size=38, y=0.9)
    S.bars([("Great Rann · Wikipedia", 7500, SALT, S.c("seven thousand five")),
            ("Great Rann · Britannica", 18000, AMBER, S.c("eighteen thousand")),
            ("Little Rann · Britannica", 5100, CYAN, S.c("five thousand more"))],
           S.c("seven thousand five") - 0.3, rect=(0.06, 0.1, 0.42, 0.36), xmax=24000, unit="km²", dec=0)
    card(S, "Average height: only ≈ 15 m above sea level", "astonishingly flat", 0.12, GREEN, x=0.745, size=28)


def s05_sea(S):
    t_cut = S.c("connection to the sea")
    kutch(S, [(0, 69.9, mercy(23.6), 6.5), (S.T, 69.9, mercy(23.6), 6.0)], start=WET, alpha=0.85)
    # sea link that closes: a channel from the Gulf of Kutch into the basin
    ch = MPoly(mpoly([(68.6, 23.2), (68.75, 23.95), (69.1, 23.9), (69.0, 23.3)]), closed=True, fc=WET, ec="none",
               zorder=4.9, alpha=0)
    S.ax.add_patch(ch)
    polys = [p for p in S.ax.patches if isinstance(p, MPoly) and p is not ch][:2]
    a_rgb, m_rgb = np.array(matplotlib.colors.to_rgb(WET)), np.array(matplotlib.colors.to_rgb(MUD))

    def up(t):
        ch.set_alpha(0.85 * (1 - ease2((t - t_cut) / 1.5)))
        u = ease2((t - S.c("What the sea")) / 1.5)
        for p in polys:
            p.set_facecolor(tuple(a_rgb + (m_rgb - a_rgb) * u))
    S.updaters.append(up)
    S.headline("ONCE A SHALLOW ARM OF THE ARABIAN SEA", S.c("This whole area"), t_cut, size=38, color=CYAN)
    S.headline("THE LAND ROSE, THE SEA WAS CUT OFF", t_cut, S.c("Accounts say"), size=38, color=WHITE)
    S.headline("STILL NAVIGABLE IN ALEXANDER'S TIME (ACCOUNTS SAY)", S.c("Accounts say"), S.c("What the sea"),
               size=34, color=AMBER)
    S.headline("LEFT BEHIND: SALTY CLAY + MUDFLATS", S.c("What the sea"), size=38, color=AMBER)
    note(S, "Illustration: outlines and old sea link approximate", 0.5)


def s06_salt(S):
    t_mon = S.c("In the monsoon")
    t_evap = S.c("the water evaporates")
    kutch(S, [(0, 70.4, mercy(23.4), 6.2), (S.c("In very wet") - 0.3, 70.4, mercy(23.4), 6.2),
              (S.c("In very wet") + 1.2, 70.6, mercy(22.9), 8.0), (S.c("Then the rains") , 70.6, mercy(22.9), 8.0),
              (S.c("Then the rains") + 1.2, 70.4, mercy(23.6), 6.0)],
          start=WET, wet_until=t_evap, dry_by=t_evap + 2.5)
    t_w = S.c("In very wet")
    route(S, [(69.0, 22.75), (69.8, 23.4), (70.8, 23.3), (71.8, 22.6), (72.4, 22.1)], t_w + 0.6, color=CYAN,
          t1=S.c("Then the rains") + 0.5)
    label(S, 68.9, 22.5, "GULF OF KUTCH", t_w + 0.6, color=CYAN, size=20, t1=S.c("Then the rains") + 0.5)
    label(S, 72.5, 21.8, "GULF OF KHAMBHAT", t_w + 1.4, color=CYAN, size=20, t1=S.c("Then the rains") + 0.5)
    # month strip
    ax2 = sub_axes(S, [0.08, 0.06, 0.84, 0.13], (0, 12), (0, 1.6), t0=t_mon)
    MON = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    cols = [SALT, SALT, SALT, PINK, PINK, WET, WET, WET, WET, MUTED, SALT, SALT]
    arts = []
    for i, (m, c) in enumerate(zip(MON, cols)):
        r = Rectangle((i + 0.06, 0.55), 0.88, 0.8, fc=c, alpha=0)
        ax2.add_patch(r)
        arts += [r, ax2.text(i + 0.5, 0.95, m, fontproperties=BOLD, size=22, color="#07111d", ha="center",
                             va="center", alpha=0)]
    lab = ax2.text(6, 0.2, "MONSOON: WETLAND  ·  WINTER: WHITE SALT  ·  SUMMER: SCORCHING", fontproperties=BOLD,
                   size=20, color=WHITE, ha="center", va="center", alpha=0)
    fader(S, arts + [lab], t_mon)
    S.headline("WATER IN...", t_mon, t_evap, size=44, color=CYAN, y=0.9)
    S.headline("...WATER EVAPORATES, SALT STAYS", t_evap, S.c("Just don't"), size=44, color=WHITE, y=0.9)
    S.headline("SUMMER: CLOSE TO 50°C", S.c("Just don't"), size=44, color=PINK, y=0.9)
    note(S, "Seasons simplified; flooding varies year to year", t_mon, y=0.97)


def s07_flamingo(S):
    kutch(S, [(0, 70.1, mercy(23.8), 4.6), (S.T, 69.95, mercy(23.95), 3.6)], little=False)
    S.highlight([np.array(GREAT_RANN)], GREEN, S.c("Kutch Desert"), peak=0.35, lw=2, z=6)
    S.text(0.5, 0.9, "KUTCH DESERT WILDLIFE SANCTUARY · 1986", S.c("Kutch Desert"), size=38, box=True, pop=True,
           color=GREEN)
    card(S, "≈ 7,506 km²: the largest sanctuary in Gujarat", "seven thousand five", 0.8, WHITE, size=32)
    fc = (69.88, 24.05)
    pin(S, *fc, "FLAMINGO CITY (approx.)", S.c("Flamingo City"), color=PINK, dy=1.6, size=24)
    rng = np.random.default_rng(3)
    p0 = merc(np.array([fc]))[0]
    pts = p0 + rng.normal(0, 0.06, (120, 2))
    sc = S.ax.scatter(pts[:, 0], pts[:, 1], s=14, color=PINK, zorder=27, alpha=0)
    fader(S, [sc], S.c("breed regularly"), peak=0.9)
    card(S, "The only area in India where greater flamingos breed regularly", "only area", 0.2, PINK,
         S.c("Nesting here"), size=32)
    card(S, "Nesting first reported: 1883", "Nesting here", 0.2, WHITE, S.c("in nineteen forty-five"), size=36)
    card(S, "1945: Salim Ali estimated ≈ 500,000 birds", "in nineteen forty-five", 0.2, AMBER, size=36)
    note(S, "Source: Gujarat Forest Department", S.c("According"), y=0.06)


def s08_border(S):
    kutch(S, [(0, 69.6, mercy(24.0), 6.5), (S.T, 69.4, mercy(24.0), 6.0)], hl=False)
    S.highlight(["Pakistan"], MUTED, 0.4, peak=0.35)
    label(S, 68.2, 24.7, "PAKISTAN", 0.4, color=WHITE)
    label(S, 71.4, 22.9, "INDIA", 0.4, color=WHITE)
    S.headline("1965: FIGHTING OVER THE WESTERN RANN", S.c("In nineteen sixty-five"), S.c("An international"),
               size=40, color=PINK)
    S.headline("1968: INTERNATIONAL TRIBUNAL", S.c("An international"), size=40, color=AMBER)
    S.bars([("India", 90, AMBER, S.c("ninety percent")), ("Pakistan", 10, MUTED, S.c("about ten"))],
           S.c("ninety percent") - 0.3, rect=(0.3, 0.1, 0.4, 0.22), xmax=120, unit="%",
           dec=0, title="SHARE OF THE DISPUTED AREA (APPROX.)")


def s09_utsav(S):
    kutch(S, [(0, 70.1, mercy(23.7), 4.6), (S.c("tent city"), 69.75, mercy(23.8), 2.6), (S.T, 69.75, mercy(23.8), 2.3)],
          little=False)
    pin(S, *DHORDO, "DHORDO · TENT CITY", S.c("tent city"), color=AMBER, dy=-4.5)
    S.text(0.5, 0.9, "RANN UTSAV 2026-27", S.c("Rann Utsav"), size=48, box=True, pop=True, color=AMBER)
    card(S, "1 NOV 2026 – 7 MAR 2027", "first of November", 0.8, WHITE, size=40)
    card(S, "Dhordo: UN Tourism 'Best Tourism Village', 2023", "Best Tourism", 0.2, CYAN, S.c("At the craft"),
         size=32)
    card(S, "Crafts: Ajrakh · Bandhani · mirror work · Lippan art", "At the craft", 0.2, PINK, size=32)
    note(S, "Source: Outlook Traveller", S.c("This season"), y=0.06)


def s10_moon(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.add_patch(Rectangle((0, 0), 16, 3.0, fc="#cdd9e3", zorder=1))
    rng = np.random.default_rng(8)
    for _ in range(60):     # salt crust cracks
        x, y = rng.uniform(0, 16), rng.uniform(0, 2.9)
        ax.plot([x, x + rng.uniform(-0.8, 0.8)], [y, min(2.95, y + rng.uniform(-0.3, 0.3))], color="#aebfcd",
                lw=1.5, zorder=1.5)
    moon = Circle((12.6, 6.9), 1.1, fc="#f6f3e6", ec="none", zorder=2, alpha=0)
    glow = Circle((12.6, 6.9), 1.6, fc="#f6f3e6", ec="none", zorder=1.8, alpha=0)
    ax.add_patch(glow)
    ax.add_patch(moon)
    S.updaters.append(lambda t: (moon.set_alpha(ease((t - 0.3) / 0.8)), glow.set_alpha(0.15 * ease((t - 0.3) / 0.8))))
    S.text(0.06, 0.88, "FULL-MOON PERIODS, 2026-27", S.c("This season"), size=40, color=AMBER, ha="left", box=True)
    rows = [("23-25 NOV", "twenty third to the twenty fifth"), ("22-24 DEC", "twenty second"),
            ("21-23 JAN", "twenty first to the twenty third"), ("19-21 FEB", "nineteenth")]
    for i, (s, ph) in enumerate(rows):
        S.text(0.06, 0.76 - i * 0.095, s, S.c(ph), size=40, color=WHITE, ha="left", box=True)
    S.headline("SALT UNDER A FULL MOON", 0.4, S.c("This season"), size=48, color=WHITE, y=0.9)
    card(S, "Stargazing? Pick a dark-moon night", "If you love", 0.16, CYAN, size=36)
    note(S, "Dates: Outlook Traveller", S.c("This season"), y=0.065)
    S.brand()


def s11_kaladungar(S):
    kutch(S, [(0, 70.1, mercy(23.7), 4.6), (S.c("Kalo Dungar"), 69.85, mercy(23.85), 1.8),
              (S.T, 69.85, mercy(23.85), 1.6)], little=False)
    pin(S, *KALO, "KALO DUNGAR", S.c("Kalo Dungar"), color=AMBER, dy=-4.5)
    S.bars([("Kalo Dungar", 462, AMBER, S.c("four hundred and sixty")),
            ("Great Rann (average)", 15, SALT, S.c("highest point"))],
           S.c("four hundred and sixty") - 0.3, rect=(0.58, 0.62, 0.36, 0.22), xmax=600, unit="m", dec=0,
           title="HEIGHT ABOVE SEA LEVEL")
    card(S, "Highest point in Kutch", "highest point", 0.2, WHITE, S.c("Up here"), size=36)
    card(S, "Dattatreya temple, said to be ≈ 400 years old", "Up here", 0.2, AMBER, S.c("Legend says"), size=34)
    card(S, "Legend: jackals are still fed rice after evening prayers", "Legend says", 0.2, PINK, size=32)


def s12_dholavira(S):
    t_tl = S.c("UNESCO says")
    tl_setup(S)
    tl = TL(S, nice=[1, 2, 5])
    tl.camera([(0, -500, 7000), (S.T, -500, 6800)])
    tl.span(-3000, -1500, 0.2, AMBER, "LIVED IN ≈ 3000-1500 BC (UNESCO)", t_tl, dur=1.4)
    tl.span(-3500, -3000, 0.42, MUTED, "recent research: maybe earlier", S.c("Some recent"), dur=1.0)
    tl.marker(2021, "UNESCO WORLD HERITAGE", S.c("In July"), sub="27 July 2021", color=CYAN, side=-1, h=0.35,
              size=26)
    S.headline("DHOLAVIRA · KHADIR BET ISLAND", 0.3, size=44, y=0.9, color=AMBER)
    card(S, "6th largest of 1,000+ known Harappan sites (UNESCO)", "Out of more", 0.78, WHITE, S.c("In July"),
         size=34)


def s13_plan(S):
    ax = S.ax
    w = 1700
    h = w * H / W
    ax.set_xlim(-750, w - 750)
    ax.set_ylim(-200, h - 200)
    S.ax.add_patch(Rectangle((-2000, -2000), 5000, 5000, fc="#1d2d42", zorder=0.5))
    L, Wd = 771, 617
    wall = Rectangle((0, 0), L, Wd, fill=False, ec=WHITE, lw=5, zorder=5, alpha=0)
    ax.add_patch(wall)
    t_p = S.c("carefully planned")
    parts = [  # schematic positions inside the wall
        (Rectangle((310, 400), 170, 150, fc=AMBER, ec="none"), "CASTLE", "fortified castle"),
        (Rectangle((90, 210), 600, 160, fc=CYAN, ec="none"), "MIDDLE TOWN", "A middle town"),
        (Rectangle((40, 30), 690, 150, fc=GREEN, ec="none"), "LOWER TOWN", "A lower town"),
        (Rectangle((90, 380), 200, 190, fc=PINK, ec="none"), "CEREMONIAL\nGROUND", "ceremonial ground"),
        (Rectangle((-420, 120), 260, 330, fc=MUTED, ec="none"), "CEMETERY", "a cemetery"),
    ]
    for r, name, ph in parts:
        r.set_alpha(0)
        r.set_zorder(4)
        ax.add_patch(r)
        x, y = r.get_x() + r.get_width() / 2, r.get_y() + r.get_height() / 2
        tx = ax.text(x, y, name, fontproperties=BOLD, size=20, color="#07111d", ha="center", va="center", zorder=6,
                     alpha=0)
        t0 = S.c(ph)
        S.updaters.append(lambda t, r=r, tx=tx, t0=t0: (r.set_alpha(0.85 * ease((t - t0) / 0.4)),
                                                        tx.set_alpha(ease((t - t0) / 0.4))))
    S.updaters.append(lambda t: wall.set_alpha(ease((t - t_p) / 0.5)))
    t_d = S.c("seven hundred and seventy")
    hdim(S, 0, L, Wd + 25, "≈ 771 m", t_d)
    vdim(S, L + 25, 0, Wd, "≈ 617 m", S.c("six hundred and twenty"))
    S.text(0.04, 0.92, "A PLANNED CITY", t_p, size=44, color=WHITE, ha="left", box=True, pop=True)
    card(S, "Found by Shambhudan Gadhvi, early 1960s · recorded 1967-68", "A local man", 0.08, WHITE,
         S.c("What they uncovered"), size=28)
    card(S, "13 excavation seasons, up to 2005", "thirteen seasons", 0.08, AMBER, S.c("What they uncovered"),
         size=30)
    note(S, "Schematic layout; outer wall to scale", t_p, y=0.065)
    S.brand()


def s14_water(S):
    ax = S.ax
    ax.set_xlim(-10, 150)
    h = 160 * H / W
    ax.set_ylim(-45, h - 45)
    ax.add_patch(Rectangle((-50, -100), 300, 100, fc="#3a3226", zorder=1))
    t_r = S.c("Some of the big")
    res = Rectangle((0, -7), 79, 7, fc=WET, ec=WHITE, lw=3, zorder=3, alpha=0)
    ax.add_patch(res)
    t_s = S.c("A huge stepwell")
    sw = Rectangle((0, -32), 73.4, 10, fc="#5aa7d6", ec=WHITE, lw=3, zorder=3, alpha=0)
    ax.add_patch(sw)
    for k in range(10):   # steps
        ax.plot([k * 3, k * 3 + 3, k * 3 + 3], [-22 - k, -22 - k, -23 - k], color=WHITE, lw=1.5, alpha=0,
                zorder=3.5)
    steps = ax.lines[-10:]
    person = Rectangle((84, 0), 0.6, 1.7, fc=AMBER, zorder=4, alpha=0)
    ax.add_patch(person)
    ptx = ax.text(86, 3, "person ≈ 1.7 m", fontproperties=BOLD, size=20, color=AMBER, alpha=0, zorder=4)
    fader(S, [res], t_r)
    fader(S, [person, ptx], t_r)
    fader(S, [sw] + steps, t_s)
    hdim(S, 0, 79, 2, "RESERVOIR ≈ 79 m LONG", t_r, dy=1.5, size=26)
    vdim(S, 81, 0, -7, "≈ 7 m DEEP", t_r + 0.6, size=24, dx=1.5)
    hdim(S, 0, 73.4, -20, "STEPWELL ≈ 73 m LONG", t_s, color=CYAN, dy=1.5, size=26)
    vdim(S, 75.5, -22, -32, "≈ 10 m DEEP", t_s + 0.6, color=CYAN, size=24, dx=1.5)
    S.headline("ONE OF THE DRIEST PLACES IN INDIA", 0.3, S.c("Two seasonal"), size=40, y=0.9, color=WHITE)
    S.headline("16+ STONE RESERVOIRS", S.c("Sixteen or more"), t_s, size=44, y=0.9, color=CYAN)
    S.headline("OFTEN CALLED ONE OF THE EARLIEST WATER SYSTEMS", S.c("It is often"), size=36, y=0.9, color=AMBER)
    note(S, "Side views drawn to scale", t_r, y=0.065)
    S.brand()


def s15_signboard(S):
    ax = S.ax
    ax.set_xlim(-0.4, 3.6)
    h = 4.0 * H / W
    ax.set_ylim(-1.0, h - 1.0)
    board = Rectangle((0, 0), 3.0, 0.55, fc="#6b4f33", ec="none", zorder=2, alpha=0)
    ax.add_patch(board)
    t_b = S.c("ten large")
    arts = []
    rng = np.random.default_rng(11)
    for i in range(10):     # abstract placeholders, NOT the real signs
        x = 0.08 + i * 0.29
        kind = rng.integers(0, 3)
        if kind == 0:
            p = Rectangle((x + 0.04, 0.09), 0.14, 0.37, fill=False, ec=SALT, lw=6, zorder=3)
        elif kind == 1:
            p = Circle((x + 0.11, 0.275), 0.12, fill=False, ec=SALT, lw=6, zorder=3)
        else:
            p = Rectangle((x + 0.09, 0.09), 0.04, 0.37, fc=SALT, ec="none", zorder=3)
        p.set_alpha(0)
        ax.add_patch(p)
        arts.append((p, t_b + 0.15 * i))
    for p, t0 in arts:
        S.updaters.append(lambda t, p=p, t0=t0: p.set_alpha(ease((t - t0) / 0.3)))
    fader(S, [board], S.c("wooden board"))
    hdim(S, 0, 3.0, 0.62, "BOARD ≈ 3 m LONG", S.c("three metres"), dy=0.04, size=30)
    vdim(S, -0.08, 0.09, 0.46, "≈ 37 cm", S.c("thirty seven"), size=26, dx=-0.04, ha="right")
    S.headline("OUTSIDE THE NORTH GATE OF THE CITADEL", 0.3, S.c("In July"), size=38, y=0.9)
    S.headline("'WORLD'S OLDEST KNOWN SIGNBOARD'", S.c("In July"), S.c("Nobody can"), size=44, y=0.9,
               color=AMBER)
    S.headline("STILL UNREADABLE: INDUS SCRIPT UNDECIPHERED", S.c("Nobody can"), size=38, y=0.9, color=PINK)
    card(S, "India's Ministry of Culture, July 2026", "In July", 0.17, WHITE, S.c("Nobody can"), size=30)
    note(S, "Illustration only: shapes are not the real signs", 0.5, y=0.04)


def s16_trade(S):
    S.graticule(step=10)
    S.world()
    S.ax.add_collection(PolyCollection([merc(r) for r in INDIA_POV], facecolors="#2c4262", edgecolors="#4f6d94",
                                       linewidths=1.0, zorder=1.8))
    S.camera([(0, 58, mercy(26), 34), (S.T, 58, mercy(26), 31)])
    pin(S, *DHOLAVIRA, "DHOLAVIRA", 0.4, color=AMBER, dy=1.2)
    t_m = S.c("with Mesopotamia")
    t_o = S.c("with Magan")
    pin(S, 46.1, 30.96, "MESOPOTAMIA", t_m, color=CYAN, dy=1.2)
    pin(S, 57.5, 22.5, "MAGAN (OMAN PENINSULA)", t_o, color=PINK, dy=-2.6)
    route(S, [DHOLAVIRA, (64, 24.5), (57, 25.5), (50.5, 28.5), (46.1, 30.96)], t_m, color=CYAN, dur=2.0)
    route(S, [DHOLAVIRA, (63, 23.5), (57.5, 22.5)], t_o, color=PINK, dur=1.6)
    card(S, "Bead and jewellery workshops: shell, agate, carnelian, copper, gold", "Workshops here", 0.12, WHITE,
         S.c("And UNESCO"), size=30)
    card(S, "Trade with Harappan cities, Mesopotamia and Magan (UNESCO)", "And UNESCO", 0.12, AMBER, size=32)
    note(S, "Routes illustrative", t_m, y=0.065)
    S.brand()


def s17_reach(S):
    kutch(S, [(0, 70.1, mercy(23.6), 4.6), (S.T, 70.1, mercy(23.6), 4.3)], little=False)
    pin(S, *BHUJ, "BHUJ · airport + rail", S.c("Bhuj is"), color=WHITE, dy=-4.5, size=22)
    pin(S, *DHORDO, "DHORDO", S.c("Dhordo and"), color=AMBER, dy=2.0, size=22)
    route(S, [BHUJ, (69.7, 23.55), DHORDO], S.c("Dhordo and"), color=AMBER)
    label(S, 69.2, 23.5, "≈ 85 km · ≈ 1.5 h", S.c("eighty five") + 0.5, color=AMBER, size=22)
    pin(S, *DHOLAVIRA, "DHOLAVIRA", S.c("Dholavira is"), color=CYAN, dy=-4.5, size=22)
    route(S, [BHUJ, (70.13, 23.28), (70.34, 23.29), (70.64, 23.57), (70.45, 23.75), DHOLAVIRA],
          S.c("Dholavira is"), color=CYAN, dur=2.0)
    label(S, 70.75, 23.25, "≈ 250 km via Bhachau, Rapar", S.c("two hundred and fifty") + 0.5, color=CYAN, size=22)
    route(S, [(69.93, 23.9), (70.05, 23.9), (70.14, 23.89)], S.c("Road to Heaven"), color=PINK, ls="-", lw=6)
    label(S, 70.2, 24.3, "ROAD TO HEAVEN ≈ 30 km", S.c("Road to Heaven") + 0.6, color=PINK, size=22)
    card(S, "Plan 2-3 nights · more for Kalo Dungar + Dholavira", "Two to three", 0.1, WHITE, size=32)
    note(S, "Routes schematic; times vary", S.c("Bhuj is"), y=0.065)


def s18_caveat(S):
    kutch(S, [(0, 70.1, mercy(23.7), 4.6), (S.T, 70.1, mercy(23.7), 4.3)], little=False)
    S.text(0.5, 0.88, "BEFORE YOU GO", 0.3, size=48, box=True, pop=True, color=PINK)
    rows = [("White Rann entry needs a permit: check current rules", "need an entry permit", WHITE),
            ("Cold after sunset: pack warm layers", "It gets cold", CYAN),
            ("Diwali, Christmas, New Year: book well ahead", "And Diwali", AMBER)]
    for i, (s, ph, col) in enumerate(rows):
        S.text(0.5, 0.7 - i * 0.12, s, S.c(ph), size=38, color=col, box=True)


def s99_outro(S):
    kutch(S, [(0, 70.1, mercy(23.7), 4.6), (S.T, 70.1, mercy(23.75), 4.0)], little=False)
    pin(S, *DHORDO, "WHITE DESERT", 0.3, color=WHITE, dy=-4.5)
    pin(S, *DHOLAVIRA, "5,000-YEAR-OLD CITY", 0.3, color=AMBER, dy=2.0)
    S.text(0.5, 0.86, "WHITE DESERT UNDER A FULL MOON,", S.c("The white"), size=42, box=True, pop=True)
    S.text(0.5, 0.76, "OR A 5,000-YEAR-OLD CITY?", S.c("or a five"), size=42, box=True, pop=True, color=AMBER)
    S.text(0.5, 0.12, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=52, box=True, pop=True, color=CYAN)
    S.fade_in_out(0, 1.5)
