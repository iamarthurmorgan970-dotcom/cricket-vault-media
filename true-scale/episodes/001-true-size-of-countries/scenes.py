"""Scenes for this episode. Each function takes the Scene S; S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.core import Scene

# ------------------------------------------------------------------ scenes
WORLD_VIEW = (0, 25, 380)          # cx, cy(merc), width


def s01_hook(S):
    S.graticule()
    S.world()
    S.camera([(0, 0, 50, 400), (S.c("Now look"), -10, 62, 380), (S.c("Africa is fourteen") - 0.5, -10, 62, 380),
              (S.T, 0, 58, 395)])
    S.highlight(["Greenland"], CYAN, S.c("Greenland"), pulse=True)
    S.highlight(AFRICA, AMBER, S.c("whole of Africa"), pulse=True)
    S.text(0.5, 0.1, "GREENLAND  ≈  AFRICA ?", S.c("looks about"), S.c("Here's the thing"), size=50, box=True, pop=True)
    S.text(0.5, 0.1, "AFRICA IS 14× BIGGER", S.c("Africa is fourteen"), size=58, color=AMBER, box=True, pop=True)
    S.fade_in_out(0.6, 0)
    S.brand()


def s02_title(S):
    S.world(fc="#1a2a3e", ec="#22364f", alpha=1)
    S.camera([(0, 0, 30, 380), (S.T, 0, 30, 350)])
    S.text(0.5, 0.56, "THE TRUE SIZE", 0.3, size=96, pop=True)
    S.text(0.5, 0.43, "OF COUNTRIES", 0.7, size=96, color=AMBER, pop=True)
    S.text(0.5, 0.31, "Why the map on your wall is lying to you", 1.2, size=30, color=MUTED, font=REG)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=CYAN)


def s02b_quiz(S):
    S.graticule()
    S.world()
    S.camera([(0, 20, 72, 265), (S.T, 25, 70, 255)])
    S.highlight(["Greenland"], CYAN, 0.6)
    S.highlight(["India"], PINK, 1.2)
    S.headline("QUICK QUIZ: WHICH IS BIGGER?", 0.3)
    p = merc(np.array([[-41.0, 70.0], [79.0, 22.0]]))
    S.ax.text(p[0, 0], p[0, 1], "GREENLAND", fontproperties=BOLD, size=30, color=WHITE, ha="center", zorder=20)
    S.ax.text(p[1, 0], p[1, 1] - 14, "INDIA", fontproperties=BOLD, size=30, color=WHITE, ha="center", zorder=20)
    S.caption("On this map, Greenland looks about 3× bigger", S.c("On the map"))
    S.text(0.5, 0.5, "?", S.c("Keep your answer"), size=220, color=WHITE)
    S.brand()


def s03_greenland(S):
    S.graticule()
    S.world()
    t_move = S.c("slide it south")
    t_shr = S.c("It shrinks")
    t_drc = S.c("Democratic Republic")
    t_end = S.c("Same shape")
    S.camera([(0, -20, 45, 230), (t_move, -15, 35, 240), (t_drc, 0, 20, 220), (t_end, 0, 20, 220),
              (S.c("remember our quiz"), 25, 30, 250)])
    S.highlight(AFRICA, AMBER, 0.3, peak=0.55)
    S.highlight(["Democratic Republic of the Congo"], "#ff9e00", t_drc - 0.3, S.c("And remember"), peak=0.95)
    g = COUNTRIES["Greenland"]
    S.mover(g, (-41, 72), (-25, 2), t_move, t_drc - 0.6, label="GREENLAND", label_dy=0, t_hide=t_drc + 0.2)
    # second step: lay Greenland over DR Congo for the comparison
    S.mover(move(g, (-41, 72), (-25, 2), 1.0), (-25, 2), (23, -3), t_drc, t_drc + 2.2, color=CYAN,
            ghost=False, appear=t_drc, z=7)
    S.headline("WATCH IT SHRINK", t_shr - 0.3, t_drc - 0.5)
    S.headline("SMALLER THAN DR CONGO", t_drc + 1.5, S.c("Greenland covers"), color=CYAN)
    S.bars([("Greenland", 2.2, CYAN, S.c("Greenland covers")), ("Africa", 30.4, AMBER, S.c("Africa covers"))],
           S.c("Greenland covers") - 0.3, rect=(0.06, 0.62, 0.34, 0.2), xmax=38, t1=S.c("And remember"))
    S.highlight(["India"], PINK, S.c("And remember"), peak=0.95)
    S.bars([("India", 3.3, PINK, S.c("India covers")), ("Greenland", 2.2, CYAN, S.c("India covers") + 0.4)],
           S.c("And remember"), rect=(0.06, 0.62, 0.34, 0.2), xmax=4.6)
    S.headline("INDIA IS 1.5× GREENLAND", S.c("one and a half"), color=PINK)
    S.brand()


def s04_why(S):
    # spinning globe
    gpc = PolyCollection([], facecolors=LAND, edgecolors=EDGE, linewidths=0.6, zorder=2)
    S.ax.add_patch(Circle((0, 0), 1.0, fc="#0f2740", ec="#4a6a90", lw=2, zorder=1))
    S.ax.add_collection(gpc)
    grid = LineCollection([], colors="#1d3b5c", linewidths=0.8, zorder=1.5)
    S.ax.add_collection(grid)
    S.ax.set_xlim(-1.6 * W / H, 1.6 * W / H)
    S.ax.set_ylim(-1.6, 1.6)
    allr = [r for n in COUNTRIES for r in COUNTRIES[n]]
    glines = [np.column_stack([np.linspace(-180, 180, 181), np.full(181, la)]) for la in range(-60, 61, 30)] + \
             [np.column_stack([np.full(121, lo), np.linspace(-90, 90, 121)]) for lo in range(-180, 180, 30)]

    def up(t):
        lon0 = 40 - 18 * t
        vs = []
        for r in allr:
            p, vis = ortho(r, lon0, 20)
            if vis > 0:
                vs.append(p)
        gpc.set_verts(vs)
        gl = []
        for l in glines:
            p, vis = ortho(l, lon0, 20)
            lam, phi = np.radians(l[:, 0] - lon0), np.radians(l[:, 1])
            cosc = np.sin(np.radians(20)) * np.sin(phi) + np.cos(np.radians(20)) * np.cos(phi) * np.cos(lam)
            p = p.copy()
            p[cosc < 0] = np.nan
            gl.append(p)
        grid.set_segments(gl)
    S.updaters.append(up)
    S.headline("A SPHERE CAN'T BE FLATTENED", S.c("The Earth is"), S.c("In fifteen"))
    S.caption("…without tearing or stretching it", S.c("without tearing"), S.c("In fifteen"))
    S.text(0.5, 0.88, "1569", S.c("fifteen sixty"), size=80, color=AMBER, pop=True)
    S.text(0.5, 0.78, "Gerardus Mercator", S.c("Gerardus"), size=40)
    S.caption("A map for sailors", S.c("making a map"), color=CYAN)
    S.brand()


def s05_rhumb(S):
    S.graticule(step=10)
    S.world()
    S.camera([(0, -40, 40, 110), (S.c("But to keep") - 0.5, -40, 40, 110), (S.T, -10, 40, 330)])
    a = np.array([-9.14, 38.72])     # Lisbon
    b = np.array([-82.38, 23.13])    # Havana
    pa, pb = merc(a[None])[0], merc(b[None])[0]
    line, = S.ax.plot([], [], color=AMBER, lw=4, zorder=10)
    ship = S.ax.scatter([pa[0]], [pa[1]], s=160, color=WHITE, zorder=11, alpha=0)
    for p, n in [(pa, "Lisbon"), (pb, "Havana")]:
        S.ax.scatter([p[0]], [p[1]], s=70, color=WHITE, zorder=11)
        S.ax.text(p[0] + 2, p[1] + 2, n, fontproperties=BOLD, size=24, color=WHITE, zorder=12)
    t0, t1 = S.c("Draw a line"), S.c("For ships") + 0.5

    def up(t):
        u = ease2((t - t0) / (t1 - t0))
        q = pa + (pb - pa) * u
        line.set_data([pa[0], q[0]], [pa[1], q[1]])
        ship.set_offsets([q])
        ship.set_alpha(1.0 if t0 < t < t1 + 1 else 0)
    S.updaters.append(up)
    S.headline("STRAIGHT LINE = CONSTANT COMPASS BEARING", S.c("a straight line"), S.c("But to keep"), size=38)
    S.headline("…SO EVERYTHING GETS STRETCHED TOWARDS THE POLES", S.c("But to keep"), size=36, color=CYAN)
    # latitude labels showing the growing gaps
    S.brand()


def s06_tissot(S):
    from pyproj import Geod
    gd = Geod(ellps="WGS84")
    S.graticule(step=20)
    S.world(fc="#1d2d42", ec="#2d4260")
    S.camera([(0, 0, 66, 425), (S.T, 0, 66, 425)])
    circles = {}
    az = np.linspace(0, 360, 73)
    for lat in (0, 20, 40, 60, 80):
        ring = []
        for lon in range(-150, 181, 60):
            lo, la, _ = gd.fwd(np.full(73, lon), np.full(73, lat), az, np.full(73, 500e3))
            ring.append(merc(np.column_stack([lo, la])))
        circles[lat] = ring
    order = {0: S.c("at the equator"), 20: S.c("at the equator") + 1.2, 40: S.c("At sixty") - 1.2,
             60: S.c("At sixty"), 80: S.c("At eighty")}
    for lat, rings in circles.items():
        col = {0: GREEN, 20: GREEN, 40: AMBER, 60: AMBER, 80: PINK}[lat]
        pc = PolyCollection(rings, facecolors=col, edgecolors=WHITE, linewidths=1.2, zorder=5, alpha=0)
        S.ax.add_collection(pc)
        t0 = order[lat]
        S.updaters.append(lambda t, pc=pc, t0=t0: pc.set_alpha(0.75 * ease((t - t0) / 0.6)))
    S.headline("SAME AREA, EVERY CIRCLE", S.c("Imagine identical"), S.c("At sixty"), y=0.07)
    for lat, lab, t in [(0, "×1", S.c("at the equator")), (60, "×4", S.c("four times")), (80, "×33", S.c("thirty-three"))]:
        y = mercy(lat)
        S.ax.text(-178, y, lab, fontproperties=BOLD, size=34, color=WHITE, ha="left", va="center", zorder=20,
                  alpha=0)
        art = S.ax.texts[-1]
        S.updaters.append(lambda tt, art=art, t=t: art.set_alpha(ease((tt - t) / 0.4)))
    S.headline("AT THE POLES: INFINITE STRETCH", S.c("And at the poles"), color=PINK, y=0.07)
    S.brand()


def compare_move(S, name, rings, frm, to, color, headline_looks, t_move_phrase, final_head, bars, extra=None):
    S.graticule()
    S.world()
    t_move = S.c(t_move_phrase)
    S.camera([(0, 20, 60, 380), (t_move, 30, 45, 300), (t_move + 4, 20, 30, 260), (S.T, 20, 25, 250)])
    S.highlight(AFRICA, AMBER, 0.3, peak=0.8)
    S.highlight(rings, color, 0.6, t_move, peak=0.8)
    S.headline(headline_looks, S.c("On this map") if "On this map" in SCRIPT[S.sid]["text"] else 0.6, t_move)
    S.mover(rings, frm, to, t_move, t_move + 4.0, color=color, label=name.upper())
    S.headline(final_head, t_move + 4.2, color=color)
    S.bars(bars, t_move + 4.5, rect=(0.62, 0.62, 0.32, 0.2), xmax=36)
    if extra:
        extra(S)
    S.brand()


def s07_russia(S):
    compare_move(S, "Russia", COUNTRIES["Russia"], (100, 62), (21, 0), PINK, "LOOKS 2.5× BIGGER THAN AFRICA",
                 "drag it down", "AFRICA IS ALMOST 2× RUSSIA",
                 [("Russia", 17.1, PINK, S.c("seventeen million")), ("Africa", 30.4, AMBER, S.c("But Africa"))])


def s08_canada(S):
    def extra(S):
        S.bars([("Russia + Canada", [(17.1, PINK), (9.98, VIOLET)], None, S.c("Canada and Russia")),
                ("Africa", 30.4, AMBER, S.c("Canada and Russia") + 0.6)],
               S.c("Canada and Russia") - 0.3, rect=(0.62, 0.30, 0.32, 0.2), xmax=36, title="TOGETHER")
    compare_move(S, "Canada", COUNTRIES["Canada"], (-100, 60), (21, 2), VIOLET, "LOOKS 1.5× AFRICA",
                 "Its real size", "ABOUT 1/3 OF AFRICA",
                 [("Canada", 9.98, VIOLET, S.c("Its real size") + 4.5), ("Africa", 30.4, AMBER, S.c("That's about"))],
                 extra)


def s09_africa(S):
    S.graticule()
    S.world()
    S.camera([(0, 15, 30, 300), (S.c("Watch this"), -2, 12, 175), (S.T, -2, 12, 175)])
    S.highlight(AFRICA, AMBER, 0.3, peak=0.85)
    S.headline("THE MAP SHRINKS AFRICA'S IMPORTANCE", S.c("That makes Africa") - 0.5, S.c("Watch this"), size=38)
    usa = COUNTRIES["United States of America"]
    for rings, frm, to, col, lab, ph in [
            (US48 + ALASKA, (-98, 40), (10, 14), CYAN, "USA", "the United States"),
            (COUNTRIES["China"], (103, 35), (27, -3), PINK, "CHINA", "China"),
            (COUNTRIES["India"], (79, 22), (25, -22), GREEN, "INDIA", "India")]:
        t = S.c(ph)
        S.mover(rings, frm, to, t - 0.2, t + 2.2, color=col, label=lab, ghost=False, appear=t - 0.4)
    S.bars([("USA + China + India", [(9.5, CYAN), (9.6, PINK), (3.3, GREEN)], None, S.c("Together")),
            ("Africa", 30.4, AMBER, S.c("Africa still"))],
           S.c("Together") - 0.3, rect=(0.04, 0.40, 0.30, 0.2), xmax=36)
    S.headline("8 MILLION KM² TO SPARE", S.c("Africa still") + 0.8, color=AMBER, y=0.08)
    S.brand()


def s10_india(S):
    S.graticule(step=10)
    S.world()
    t_move = S.c("So let's slide")
    S.camera([(0, 45, 40, 140), (t_move, 45, 45, 140), (S.T, 20, 55, 120)])
    eu = {"Germany": CYAN, "France": VIOLET, "Spain": GREEN, "Italy": AMBER, "United Kingdom": "#ff8fab"}
    for n, c in eu.items():
        S.highlight([n], c, S.c("Europe"), peak=0.9)
    S.highlight(["India"], PINK, 0.4, t_move, peak=0.85)
    S.headline("NOT A FAIR FIGHT: EUROPE IS STRETCHED", S.c("But that's not"), t_move, size=38)
    S.mover(COUNTRIES["India"], (79, 22), (8, 47), t_move, t_move + 4.5, color=PINK, label="INDIA")
    S.headline("BIGGER THAN ALL FIVE COMBINED", S.c("India is bigger"), color=PINK)
    S.bars([("India", 3.3, PINK, S.c("India is bigger") + 0.3),
            ("DE + FR + ES + IT + UK", [(0.36, CYAN), (0.64, VIOLET), (0.51, GREEN), (0.30, AMBER), (0.24, "#ff8fab")],
             None, S.c("India is bigger") + 0.8)],
           S.c("India is bigger"), rect=(0.06, 0.12, 0.34, 0.2), xmax=4.2)
    S.brand()


def us_overlay(S, name, rings, frm, color, look_head, t_phrase, final_head, bar_rows, cam=None, to=(-98, 39),
               extra=None):
    S.graticule()
    S.world()
    t = S.c(t_phrase)
    S.camera(cam or [(0, -10, 30, 330), (t, -60, 40, 200), (S.T, -95, 50, 115)])
    S.highlight(US48, "#e9edf2", 0.3, peak=0.35)
    S.highlight(rings, color, 0.5, t, peak=0.85)
    if look_head:
        S.headline(look_head, 0.6, t)
    S.mover(rings, frm, to, t, t + 4.5, color=color, label=name.upper())
    S.headline(final_head, t + 4.6, color=color)
    if bar_rows:
        S.bars(bar_rows, t + 4.8, rect=(0.06, 0.12, 0.32, 0.2), xmax=max(r[1] for r in bar_rows) * 1.3)
    if extra:
        extra(S, t)
    S.brand()


def s11_australia(S):
    us_overlay(S, "Australia", COUNTRIES["Australia"], (134, -25), GREEN, "LOOKS FAR SMALLER THAN THE USA",
               "So let's move", "ALMOST EXACTLY THE MAINLAND US",
               [("Australia", 7.7, GREEN, S.c("Around seven")), ("US mainland", 8.1, "#e9edf2", S.c("against about"))])


def s11b_brazil(S):
    us_overlay(S, "Brazil", COUNTRIES["Brazil"], (-53, -10), GREEN, None, "Let's lift",
               "BIGGER THAN THE MAINLAND US",
               [("Brazil", 8.5, GREEN, S.c("Eight and a half")), ("US mainland", 8.1, "#e9edf2", S.c("Eight and a half") + 0.6)],
               cam=[(0, -75, 10, 200), (S.c("Let's lift"), -75, 15, 200), (S.T, -95, 50, 115)])


def s11c_indonesia(S):
    def extra(S, t):
        y = mercy(30)
        for x0, x1, yy, lab, col, ta in [(-124.4, -67, mercy(27.5), "Mainland US ≈ 4,500 km", "#e9edf2", t + 4.8),
                                         (-96 - 22.9, -96 + 22.9, mercy(48), "Indonesia ≈ 5,100 km", PINK, t + 5.6)]:
            ln, = S.ax.plot([x0, x1], [yy, yy], color=col, lw=4, zorder=15, alpha=0)
            tx = S.ax.text((x0 + x1) / 2, yy + 1.8, lab, fontproperties=BOLD, size=24, color=col, ha="center",
                           zorder=16, alpha=0)
            S.updaters.append(lambda tt, ln=ln, tx=tx, ta=ta: (ln.set_alpha(ease((tt - ta) / 0.5)),
                                                                tx.set_alpha(ease((tt - ta) / 0.5))))
    us_overlay(S, "Indonesia", COUNTRIES["Indonesia"], (118, -2.5), PINK, "A SCATTER OF ISLANDS…", "But lay it",
               "WIDER THAN THE USA, COAST TO COAST", None,
               cam=[(0, 60, 0, 260), (S.c("But lay it"), 0, 20, 280), (S.T, -95, 46, 115)], to=(-96, 37.5), extra=extra)


def s12_alaska(S):
    S.graticule()
    S.world()
    t = S.c("Let's slide")
    S.camera([(0, -120, 50, 120), (t, -118, 40, 120), (S.T, -112, 30, 100)])
    S.highlight(ALASKA, CYAN, 0.4, t, peak=0.85)
    S.highlight(["Mexico"], GREEN, 0.8, peak=0.8)
    S.headline("ALASKA LOOKS ENORMOUS", 0.5, t)
    S.mover(ALASKA, (-152, 64), (-131, 22), t, t + 4, color=CYAN, label="ALASKA")
    S.headline("SMALLER THAN MEXICO", S.c("Alaska is actually"), color=CYAN)
    S.bars([("Alaska", 1.7, CYAN, S.c("One point seven")), ("Mexico", 1.96, GREEN, S.c("against nearly"))],
           S.c("One point seven") - 0.3, rect=(0.06, 0.62, 0.30, 0.2), xmax=2.5)
    S.brand()


def s13_antarctica(S):
    t_real = S.c("In reality")
    # part 1: Mercator strip
    S.graticule(lat_max=85)
    wpc = S.world()
    S.camera([(0, 0, -20, 400), (t_real - 0.6, 0, -40, 400)])
    hl = S.highlight(["Antarctica"], "#e8f4ff", 0.5, t_real, peak=0.95)
    S.headline("ON MERCATOR: A GIANT WHITE STRIP", S.c("smeared"), t_real - 0.3)
    # part 2: globe from below
    globe_ax = S.fig.add_axes([0, 0, 1, 1])
    globe_ax.set_axis_off()
    globe_ax.set_xlim(-1.5 * W / H, 1.5 * W / H)
    globe_ax.set_ylim(-1.5, 1.5)
    bgr = Rectangle((0, 0), 1, 1, transform=globe_ax.transAxes, color=OCEAN, zorder=0)
    globe_ax.add_patch(bgr)
    disc = Circle((0, 0), 1.0, fc="#0f2740", ec="#4a6a90", lw=2, zorder=1)
    globe_ax.add_patch(disc)
    land = PolyCollection([], facecolors=LAND, edgecolors=EDGE, linewidths=0.6, zorder=2)
    ant = PolyCollection([], facecolors="#e8f4ff", edgecolors=WHITE, linewidths=1, zorder=3)
    rus = PolyCollection([], facecolors=PINK, edgecolors=WHITE, linewidths=1.2, zorder=4, alpha=0.85)
    for c in (land, ant, rus):
        globe_ax.add_collection(c)
    others = [r for n in COUNTRIES if n != "Antarctica" for r in COUNTRIES[n]]
    t_rus = S.c("smaller than Russia")

    def up(t):
        a = ease((t - t_real) / 0.7)
        globe_ax.set_visible(a > 0)
        for art in (bgr, disc):
            art.set_alpha(a)
        if a <= 0:
            return
        vs = [p for r in others for p, v in [ortho(r, 0, -90)] if v > 0]
        land.set_verts(vs)
        ant.set_verts([ortho(r, 0, -90)[0] for r in COUNTRIES["Antarctica"]])
        land.set_alpha(a)
        ant.set_alpha(a)
        u = ease2((t - t_rus) / 3.0)
        rr = move(COUNTRIES["Russia"], (100, 62), (100, -62), u)
        rus.set_verts([ortho(r, 0, -90)[0] for r in rr])
        rus.set_alpha(0.85 * ease((t - t_rus + 0.3) / 0.5))
    S.updaters.append(up)
    S.text(0.5, 0.9, "REALITY: 14 MILLION KM²", t_real + 0.3, S.c("smaller than Russia"), size=46, box=True, pop=True)
    S.text(0.5, 0.9, "SMALLER THAN RUSSIA (17.1M)", S.c("smaller than Russia") + 0.3, size=46, color=PINK, box=True,
           pop=True, zorder=80)
    S.brand()


def s14_ranking(S):
    S.ax.set_xlim(0, 1)
    S.ax.set_ylim(0, 1)
    rows = [("Russia", 17.1, PINK, "Russia"), ("Antarctica", 14.2, "#e8f4ff", "Antarctica"),
            ("Canada", 9.98, VIOLET, "Canada"), ("China", 9.6, PINK, "China"),
            ("United States", 9.5, CYAN, "United States"), ("Brazil", 8.5, GREEN, "Brazil"),
            ("Australia", 7.7, GREEN, "Australia"), ("India", 3.3, PINK, "India"),
            ("Greenland", 2.2, CYAN, "Greenland")]
    bar_rows = [(lab, v, c, S.c(ph)) for lab, v, c, ph in rows]
    bar_rows.insert(0, ("AFRICA (continent)", 30.4, AMBER, S.c("Now put Africa") + 0.8))
    S.text(0.5, 0.93, "THE WORLD AT TRUE SCALE", 0.3, size=46, pop=True)
    S.text(0.5, 0.87, "Total area, million km²", 0.6, size=24, color=MUTED, font=REG)
    S.bars(bar_rows, 0.2, rect=(0.27, 0.07, 0.62, 0.74), xmax=36, label_left=True)
    S.brand()


def s15_better(S):
    allr = [(n, r) for n in COUNTRIES for r in COUNTRIES[n]]
    pc = PolyCollection([merc(r) for _, r in allr], facecolors=LAND, edgecolors=EDGE, linewidths=0.5, zorder=2)
    S.ax.add_collection(pc)
    hl_names = set(AFRICA) | {"Greenland"}
    cols = [AMBER if n in AFRICA else CYAN if n == "Greenland" else LAND for n, _ in allr]
    t_m = S.c("Watch the world")
    S.camera([(0, 0, 20, 400), (t_m, 0, 10, 400), (t_m + 3, 0, 8, 370)])

    def up(t):
        u = ease2((t - t_m) / 3.0)
        pc.set_verts([(1 - u) * merc(r) + u * equal_earth(r) for _, r in allr])
        a = ease((t - t_m + 0.5) / 0.8)
        fc = [matplotlib.colors.to_rgba(c) if c == LAND else
              tuple(np.array(matplotlib.colors.to_rgba(LAND)) * (1 - a) + np.array(matplotlib.colors.to_rgba(c)) * a)
              for c in cols]
        pc.set_facecolors(fc)
    S.updaters.append(up)
    S.headline("MERCATOR: GREAT FOR STREETS", S.c("Web maps"), S.c("But for showing"))
    S.headline("2017: BOSTON SCHOOLS SWITCH TO GALL-PETERS", S.c("In twenty seventeen"), S.c("And in twenty eighteen"), size=40)
    S.headline("2018: EQUAL EARTH PROJECTION", S.c("And in twenty eighteen"), t_m)
    S.headline("EQUAL EARTH: EVERY AREA TRUE", t_m + 0.4, color=AMBER, y=0.08)
    S.brand()


def s16_outro(S):
    S.world(proj=equal_earth)
    S.highlight(AFRICA, AMBER, 0.3, proj=equal_earth, peak=0.85)
    S.highlight(["Greenland"], CYAN, 0.3, proj=equal_earth, peak=0.85)
    S.highlight(["Russia"], PINK, S.c("Russia is not"), proj=equal_earth, peak=0.8)
    S.camera([(0, 0, -12, 400), (S.T, 0, -12, 380)])
    S.headline("A MAP IS A CHOICE, NOT A PHOTOGRAPH", S.c("It isn't a"), S.c("Greenland is not"), size=40)
    S.text(0.5, 0.9, "Greenland ≠ Africa", S.c("Greenland is not"), S.c("subscribe"), size=40, color=CYAN, box=True)
    S.text(0.5, 0.82, "Russia < Africa", S.c("Russia is not"), S.c("subscribe"), size=40, color=PINK, box=True)
    S.text(0.5, 0.74, "Africa is HUGE", S.c("And Africa is far"), S.c("subscribe"), size=40, color=AMBER, box=True)
    S.text(0.5, 0.17, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=60, color=WHITE, box=True, pop=True)
    S.text(0.5, 0.07, "Which country surprised you most? Tell me in the comments", S.c("tell me"), size=30,
           color=WHITE, font=REG, box=True)
    S.fade_in_out(0, 1.5)
    S.brand()


def s03b_saudi(S):
    S.graticule()
    S.world()
    t = S.c("But slide it")
    S.camera([(0, 5, 55, 200), (t, 10, 50, 190), (S.T, 40, 30, 110)])
    S.highlight(["Saudi Arabia"], GREEN, 0.5, peak=0.85)
    S.highlight(["Greenland"], CYAN, 0.3, t, peak=0.85)
    S.headline("GREENLAND vs THE ARABIAN PENINSULA", 0.4, t, size=40)
    S.mover(COUNTRIES["Greenland"], (-41, 72), (45, 24), t, t + 4.5, color=CYAN, label="GREENLAND")
    S.headline("A NEAR PERFECT MATCH", S.c("A near perfect"), color=GREEN)
    S.bars([("Saudi Arabia", 2.15, GREEN, S.c("Saudi Arabia covers")), ("Greenland", 2.17, CYAN, S.c("Greenland, about"))],
           S.c("Saudi Arabia covers") - 0.3, rect=(0.06, 0.12, 0.32, 0.2), xmax=2.8, dec=2)
    S.brand()


def s10b_japan(S):
    S.graticule(step=10)
    S.world()
    t = S.c("Put it at")
    S.camera([(0, 75, 50, 190), (t, 75, 52, 190), (S.T, 14, 58, 70)])
    S.highlight(["Germany"], CYAN, 0.4, peak=0.85)
    S.highlight(["Japan"], PINK, 0.4, t, peak=0.9)
    S.headline("JAPAN LOOKS SMALLER THAN GERMANY", 0.5, t, size=40)
    S.mover(COUNTRIES["Japan"], (138, 37), (15, 51), t, t + 4.5, color=PINK, label="JAPAN", label_dy=-4)
    S.headline("JAPAN IS BIGGER", t + 4.7, color=PINK)
    S.bars([("Japan", 378, PINK, S.c("Japan covers")), ("Germany", 358, CYAN, S.c("Germany, about"))],
           S.c("Japan covers") - 0.3, rect=(0.06, 0.12, 0.32, 0.2), xmax=500, unit="thousand km²", dec=0)
    S.brand()
s03_greenland_v2 = s03_greenland
s16_outro_v2 = s16_outro
