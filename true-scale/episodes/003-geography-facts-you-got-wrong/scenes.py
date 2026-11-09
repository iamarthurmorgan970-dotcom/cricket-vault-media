"""Scenes for this episode. Each function takes the Scene S; S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.extras import *

# ------------------------------------------------------------------ scenes
def s01_hook(S):
    mapbase(S)
    S.camera([(0, 20, 40, 380), (S.T, 30, 35, 340)])
    myths = [("Mount Everest is the tallest mountain", S.c("Mount Everest")),
             ("You can see the Great Wall from space", S.c("You can see")),
             ("The Sahara is the biggest desert", S.c("The Sahara"))]
    t_wrong = S.c("And every single")
    for i, (m, t) in enumerate(myths):
        y = 0.70 - i * 0.16
        S.text(0.5, y, m, t, size=44, box=True, pop=True)
        S.fig.add_artist(_strike_for(S, 0.5, y, m, 44, t_wrong + 0.25 * i))
    S.text(0.5, 0.16, "ALL WRONG (OR NOT THE WHOLE TRUTH)", t_wrong + 0.8, size=48, color=RED, box=True, pop=True)
    S.fade_in_out(0.6, 0)
    S.brand()


def _strike_for(S, x, y, text, size, t0):
    from matplotlib.lines import Line2D
    tmp = S.fig.text(x, y, text, fontproperties=BOLD, size=size, ha="center", va="center", alpha=0)
    S.fig.canvas.draw()
    bb = tmp.get_window_extent(renderer=S.fig.canvas.get_renderer())
    tmp.remove()
    x0, x1 = bb.x0 / W, bb.x1 / W
    ln = Line2D([x0, x0], [y, y], color=RED, lw=7, zorder=80, alpha=0, solid_capstyle="round")

    def up(t):
        g = ease2((t - t0) / 0.45)
        ln.set_xdata([x0, x0 + (x1 - x0) * g])
        ln.set_alpha(1 if g > 0 else 0)
    S.updaters.append(up)
    return ln


def s02_title(S):
    S.world(proj=equal_earth, fc="#1a2a3e", ec="#22364f")
    S.camera([(0, 0, 10, 380), (S.T, 0, 10, 360)])
    S.text(0.5, 0.58, "15 GEOGRAPHY FACTS", 0.3, size=90, pop=True)
    S.text(0.5, 0.45, "YOU GOT WRONG", 0.7, size=90, color=RED, pop=True)
    S.text(0.5, 0.33, "Keep count of how many you believed", 1.3, size=30, color=MUTED, font=REG)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=CYAN)


def m01_everest(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(-7, 2)
    t_truth = S.c("But tallest")
    myth(S, 1, "Mount Everest is the tallest mountain", "TALLEST: MAUNA KEA (10,210 m base to peak)", t_truth)
    sea = Rectangle((0, -7), 16, 7, color="#0f2f52", zorder=1, alpha=0)
    ax.add_patch(sea)
    ax.plot([0, 16], [0, 0], color=CYAN, lw=2, zorder=3)
    ax.text(15.8, 0.1, "sea level", fontproperties=REG, size=20, color=CYAN, ha="right", va="bottom")
    # scale: 1 unit = 1 km (y), mountains drawn as triangles
    ev = MPoly([[1.5, 0], [4.5, 8.849 * 0.0 + 0], [3.0, 0]], color=AMBER, zorder=4)
    ev_tri = MPoly([[1.2, 0], [4.8, 0], [3.0, 0]], closed=True, color=AMBER, zorder=4)
    mk_tri = MPoly([[8.0, -6.0], [14.0, -6.0], [11.0, -6.0]], closed=True, color=GREEN, zorder=2)
    ax.add_patch(ev_tri)
    ax.add_patch(mk_tri)
    lab_e = ax.text(3.0, 0, "EVEREST\n8,849 m above sea level", fontproperties=BOLD, size=24, color=AMBER, ha="center",
                    va="bottom", zorder=6, alpha=0)
    lab_m = ax.text(11.0, 0, "MAUNA KEA\n10,210+ m from its base", fontproperties=BOLD, size=24, color=GREEN,
                    ha="center", va="bottom", zorder=6, alpha=0)
    ax.text(11.0, -6.6, "Pacific Ocean floor", fontproperties=REG, size=20, color=MUTED, ha="center", va="center")
    t_e, t_m = S.c("Everest is the highest"), S.c("Mauna Kea")
    ax.set_ylim(-10, 16)

    def up(t):
        ge = ease2((t - t_e) / 1.2)
        ev_tri.set_xy([[1.2, 0], [4.8, 0], [3.0, 8.849 * ge]])
        lab_e.set_position((3.0, 8.849 * ge + 0.2))
        lab_e.set_alpha(ease((t - t_e - 0.8) / 0.4))
        gm = ease2((t - t_m) / 1.8)
        top = -6.0 + 10.21 * gm
        mk_tri.set_xy([[7.6, -6.0], [14.4, -6.0], [11.0, top]])
        lab_m.set_position((11.0, top + 0.2))
        lab_m.set_alpha(ease((t - t_m - 1.4) / 0.4))
        sea.set_alpha(0.85 * ease((t - t_m + 0.5) / 0.6))
    S.updaters.append(up)
    S.text(0.5, 0.42, "Most of Mauna Kea is underwater", S.c("Most of it"), S.T, size=30, color=CYAN, box=True)
    S.brand()


def m02_chimborazo(S):
    ax = S.ax
    ax.set_xlim(-1.6 * 16 / 9, 1.6 * 16 / 9)
    ax.set_ylim(-1.6, 1.6)
    t_truth = S.c("It isn't")
    myth(S, 2, "Everest's peak is the closest point to space", "CHIMBORAZO'S PEAK IS FURTHER FROM EARTH'S CENTRE", t_truth)
    circ = Circle((0, -0.1), 1.05, fill=False, ec=MUTED, lw=2, ls=(0, (6, 4)), zorder=2)
    ell = Ellipse((0, -0.1), 2.1, 2.1, fc="#1d3b5c", ec=CYAN, lw=3, zorder=1)
    ax.add_patch(ell)
    ax.add_patch(circ)
    eq, = ax.plot([], [], color=AMBER, lw=2, zorder=3)
    lab = ax.text(1.3, -0.8, "", fontproperties=BOLD, size=22, color=WHITE, ha="left", zorder=5, linespacing=1.3)
    t_b = S.c("It bulges")
    pts = {}
    for name, ang, col in [("CHIMBORAZO", 1.5, GREEN), ("EVEREST", 28, AMBER)]:
        pts[name] = (ax.scatter([], [], s=140, color=col, edgecolors=WHITE, zorder=6),
                     ax.text(0, 0, name, fontproperties=BOLD, size=24, color=col, zorder=6, alpha=0), ang)
    t_c = S.c("So Mount Chimborazo")

    def up(t):
        g = ease2((t - t_b) / 1.5)
        w = 2.1 * (1 + 0.12 * g)          # bulge hugely exaggerated so it's visible
        h = 2.1 * (1 - 0.04 * g)
        ell.set_width(w)
        ell.set_height(h)
        eq.set_data([-w / 2, w / 2], [-0.1, -0.1])
        lab.set_text("Equator: ≈ 21 km further\nfrom the centre\n(bulge exaggerated)" if g > 0.3 else "")
        for name, (sc, tx, ang) in pts.items():
            a = ease((t - t_c) / 0.5)
            th = math.radians(ang)
            x, y = (w / 2) * math.cos(th) * 1.0, (h / 2) * math.sin(th) - 0.1
            sc.set_offsets([[x, y]])
            sc.set_alpha(a)
            tx.set_position((x + 0.1, y + (0.12 if name == "EVEREST" else -0.2)))
            tx.set_alpha(a)
    S.updaters.append(up)
    S.brand()


def m03_wall(S):
    mapbase(S)
    t_truth = S.c("China's first")
    S.camera([(0, 100, 50, 120), (S.T, 108, 48, 90)])
    myth(S, 3, "You can see the Great Wall from space", "NOT WITH THE NAKED EYE, EVEN FROM LOW ORBIT", t_truth)
    S.highlight(["China"], PINK, 0.5, peak=0.55)
    S.text(0.5, 0.42, "Very long. Very narrow. Same colour as the land.", S.c("The wall is very"), size=34, box=True)
    S.text(0.75, 0.62, '"I couldn\'t see it" - Yang Liwei', S.c("Yang Liwei"), S.c("The wall is very") - 0.2, size=30,
           color=AMBER, box=True)
    S.brand()


def m04_desert(S):
    mapbase(S, proj=equal_earth, grid=False)
    t_truth = S.c("By that measure")
    S.camera([(0, 0, -8, 380), (S.T, 0, -12, 370)])
    myth(S, 4, "The Sahara is the largest desert", "LARGEST DESERT: ANTARCTICA", t_truth)
    S.highlight(["Antarctica"], "#e8f4ff", t_truth + 0.3, proj=equal_earth, peak=0.95)
    sahara = [n for n in ("Algeria", "Libya", "Egypt", "Mali", "Niger", "Chad", "Mauritania", "Sudan")]
    S.highlight(sahara, AMBER, S.c("The Sahara, at"), proj=equal_earth, peak=0.6)
    S.text(0.5, 0.62, "Desert = very little rain or snow, not heat", S.c("It's defined"), t_truth, size=34, box=True)
    S.bars([("Antarctica", 14.2, "#e8f4ff", S.c("fourteen million")), ("Sahara (largest hot desert)", 9.2, AMBER,
                                                                         S.c("nine point two"))],
           S.c("fourteen million") - 0.3, rect=(0.62, 0.55, 0.32, 0.2), xmax=17)
    S.brand()


def m05_nile(S):
    mapbase(S, proj=equal_earth, grid=False)
    t_truth = S.c("But measuring")
    S.camera([(0, -10, 5, 300), (S.T, -10, 5, 280)])
    myth(S, 5, "The Nile is definitely the longest river", "NILE OR AMAZON? STILL DISPUTED", t_truth)
    for names, col, t0 in [(["Nile", "Kagera", "Victoria Nile", "Albert Nile", "Bahr el Jebel", "El Bahr el Abyad", "Rosetta Branch"], CYAN, 0.6), (["Amazonas", "Ucayali"], GREEN, S.c("One Brazilian"))]:
        ls = [equal_earth(l) for l in river(names)]
        lc = LineCollection(ls, colors=col, linewidths=5, zorder=20, alpha=0)
        S.ax.add_collection(lc)
        S.updaters.append(lambda t, lc=lc, t0=t0: lc.set_alpha(ease((t - t0) / 0.6)))
    S.bars([("Nile (usual figure)", 6.65, CYAN, S.c("six thousand six")),
            ("Amazon (2007 Brazilian study)", 6.99, GREEN, S.c("almost seven"))],
           S.c("six thousand six") - 0.3, rect=(0.06, 0.12, 0.34, 0.2), xmax=8.5, unit="thousand km", dec=2)
    S.text(0.75, 0.25, "Where does it start? Which mouth counts?", S.c("Where exactly"), size=30, box=True)
    S.brand()


def m06_timezones(S):
    mapbase(S, proj=equal_earth, grid=False)
    t_truth = S.c("But the winner")
    S.camera([(0, 0, 5, 380), (S.T, 0, 5, 370)])
    myth(S, 6, "Russia has the most time zones", "FRANCE: 12 TIME ZONES", t_truth)
    S.highlight(["Russia"], PINK, S.c("Russia has eleven"), t_truth, peak=0.7, proj=equal_earth)
    S.highlight(["United States of America"], CYAN, S.c("So does"), t_truth, peak=0.7, proj=equal_earth)
    fr = ["France", "Saint Pierre and Miquelon", "Wallis and Futuna", "Saint Martin", "Saint Barthelemy",
          "French Polynesia", "New Caledonia", "French Southern and Antarctic Lands"]
    S.highlight(fr, AMBER, t_truth, proj=equal_earth, peak=0.95, lw=2)
    spots = [(2.5, 46.5), (-53, 4), (-61, 15.5), (55.5, -21), (45.2, -12.8), (-149.5, -17.6), (-140, -9), (165.5, -21.3),
             (-176.2, -13.3), (-56.3, 46.9), (69.5, -49.3), (140, -66.7)]
    for i, (lo, la) in enumerate(spots):
        p = equal_earth(np.array([[lo, la]]))[0]
        ring = Circle(p, 4.5, fill=False, ec=AMBER, lw=3, zorder=25, alpha=0)
        S.ax.add_patch(ring)
        t0 = S.c("France isn't just") + 0.25 * i
        S.updaters.append(lambda t, r=ring, t0=t0: r.set_alpha(ease((t - t0) / 0.3)))
    S.text(0.5, 0.2, "RUSSIA 11  ·  USA 11  ·  FRANCE 12", S.c("Russia has eleven"), t_truth + 0.2, size=36, box=True)
    S.brand()


def m07_northpole(S):
    gpc = PolyCollection([], facecolors=LAND, edgecolors=EDGE, linewidths=0.6, zorder=2)
    disc = Circle((0, 0), 1.0, fc="#0f2740", ec="#4a6a90", lw=2, zorder=1)
    S.ax.add_patch(disc)
    S.ax.add_collection(gpc)
    ice = Circle((0, 0), 0.28, fc="#e8f4ff", ec="none", alpha=0, zorder=3)
    S.ax.add_patch(ice)
    S.ax.set_xlim(-1.5 * 16 / 9, 1.5 * 16 / 9)
    S.ax.set_ylim(-1.5, 1.4)
    allr = [r for n in COUNTRIES for r in COUNTRIES[n]]
    t_truth = S.c("But there's no land")
    t_s = S.c("The South Pole")
    myth(S, 7, "The North Pole is on land", "THE NORTH POLE IS IN THE MIDDLE OF AN OCEAN", t_truth)
    pole = S.ax.scatter([0], [0], s=0, color=RED, edgecolors=WHITE, linewidths=2, zorder=6)
    lab = S.ax.text(0.33, 0.05, "", fontproperties=BOLD, size=26, color=WHITE, zorder=7)

    def up(t):
        u = ease2((t - t_s) / 1.5) - ease2((t - t_truth + 0.6) / 1.5)    # visit the south pole, then come back north
        lat0 = 90 - 180 * u
        vs = [p for r in allr for p, v in [ortho(r, 0, lat0)] if v > 0]
        gpc.set_verts(vs)
        north = lat0 > 60
        ice.set_alpha(0.85 * ease((t - t_truth) / 0.6) if north else 0)
        pole.set_sizes([180 if (north and t > t_truth) or (not north and lat0 < -60) else 0])
        lab.set_text("NORTH POLE: SEA ICE" if north and t > t_truth else ("SOUTH POLE: ANTARCTICA" if lat0 < -60 else ""))
    S.updaters.append(up)
    S.brand()


def m08_capitals(S):
    mapbase(S, proj=equal_earth, grid=False)
    S.camera([(0, 0, 10, 380), (S.T, 0, 10, 370)])
    t_truth = S.c("Very often")
    myth(S, 8, "The biggest city is the capital", "OFTEN IT ISN'T", t_truth)
    pairs = [("Sydney", 151.21, -33.87, "Canberra", 149.13, -35.28, "Australia's"),
             ("Istanbul", 28.98, 41.01, "Ankara", 32.85, 39.93, "Turkey's"),
             ("Rio", -43.17, -22.91, "Brasília", -47.88, -15.79, "Brazil's"),
             ("Lagos", 3.38, 6.52, "Abuja", 7.49, 9.07, "Nigeria's"),
             ("Toronto", -79.38, 43.65, "Ottawa", -75.70, 45.42, "Canada's")]
    for wrong, wl, wa, right, rl, ra, ph in pairs:
        t0 = S.c(ph)
        dot(S, wl, wa, wrong, t0, color=RED, proj=equal_earth, dy=-9, size=22, cross=t0 + 1.2)
        dot(S, rl, ra, right + " ✓" if False else right, t0 + 1.2, color=GREEN, proj=equal_earth, dy=3, size=24)
    S.brand()


def m09_latitude(S):
    mapbase(S)
    t_truth = S.c("It's actually")
    S.camera([(0, -50, 52, 190), (S.T, -50, 55, 180)])
    myth(S, 9, "Europe is level with the United States", "EUROPE IS MUCH FURTHER NORTH", t_truth)
    dot(S, 12.50, 41.90, "Rome 41.9°N", S.c("Rome is"), color=AMBER, size=22)
    dot(S, -74.01, 40.71, "New York 40.7°N", S.c("New York"), color=CYAN, dy=-7, size=22)
    lat_line(S, 41.9, S.c("Rome is"), AMBER, -130, 30)
    dot(S, -0.13, 51.51, "London 51.5°N", S.c("And London"), color=AMBER, size=22)
    dot(S, -114.07, 51.05, "Calgary 51.0°N", S.c("Calgary"), color=CYAN, dy=-7, size=22)
    lat_line(S, 51.51, S.c("And London"), AMBER, -130, 30)
    S.brand()


def m10_reno(S):
    mapbase(S)
    t_truth = S.c("Not quite")
    t_p = S.c("At the Panama")
    S.camera([(0, -115, 40, 40), (t_p - 0.5, -117, 39.5, 26), (t_p + 0.8, -79.6, 9.0, 3.2), (S.T, -79.7, 9.1, 3.0)])
    myth(S, 10, "Everything in California is west of Nevada", "RENO IS WEST OF LOS ANGELES", t_truth)
    for name, lo, la, col, dy in [("Reno", -119.81, 39.53, AMBER, 0.5), ("Los Angeles", -118.24, 34.05, CYAN, 0.5)]:
        dot(S, lo, la, name, S.c("Reno, Nevada") if name == "Reno" else S.c("Los Angeles"), color=col, dy=dy, size=24,
            t1=t_p)
        p = merc(np.array([[lo, la]]))[0]
        ln, = S.ax.plot([p[0], p[0]], [mercy(30), mercy(45)], color=col, lw=2, ls=(0, (5, 4)), alpha=0, zorder=20)
        t0 = S.c("Reno, Nevada")
        S.updaters.append(lambda t, ln=ln, t0=t0: ln.set_alpha(min(ease((t - t0) / 0.5), ease((t_p - t) / 0.4))))
    dot(S, -79.92, 9.35, "Atlantic entrance", t_p + 0.8, color=CYAN, dy=0.06, size=24)
    dot(S, -79.57, 8.95, "Pacific entrance", t_p + 1.6, color=GREEN, dy=-0.25, size=24)
    S.headline("PACIFIC END IS EAST OF THE ATLANTIC END", t_p + 2.4, color=GREEN, y=0.08, size=38)
    S.brand()


def m11_greenland(S):
    mapbase(S)
    t_truth = S.c("It's almost")
    S.camera([(0, -30, 112, 175), (S.T, -30, 110, 165)])
    myth(S, 11, "Iceland is icy and Greenland is green", "IT'S ALMOST THE OTHER WAY AROUND", t_truth)
    S.highlight(["Iceland"], GREEN, S.c("Glaciers cover only"), peak=0.85)
    S.highlight(["Greenland"], "#e8f4ff", S.c("Meanwhile"), peak=0.95)
    S.bars([("Iceland: glaciers", 10, GREEN, S.c("one tenth")), ("Greenland: ice sheet", 80, "#e8f4ff", S.c("eighty percent"))],
           S.c("one tenth") - 0.3, rect=(0.62, 0.14, 0.32, 0.2), xmax=100, unit="% of land", dec=0)
    S.brand()


def m12_deadsea(S):
    mapbase(S)
    t_truth = S.c("It's actually")
    t_c = S.c("And the same")
    S.camera([(0, 36, 32, 30), (t_c - 0.3, 36, 32, 30), (t_c + 1.0, 46, 46, 70), (S.T, 46, 46, 66)])
    myth(S, 12, "The Dead Sea and the Caspian Sea are seas", "BOTH ARE LAKES", t_truth)
    S.highlight(lake("Dead Sea"), CYAN, 0.6, peak=1.0)
    dot(S, 35.5, 31.5, "Dead Sea: a salt lake", t_truth, color=CYAN, dx=1, ha="left", size=24, t1=t_c)
    dot(S, 50.5, 41.5, "Caspian Sea: largest lake on Earth", t_c + 1.0, color=AMBER, dx=4, ha="left", size=24)
    S.bars([("Caspian Sea", 371, AMBER, S.c("three hundred")), ("Germany", 358, MUTED, S.c("Bigger than"))],
           S.c("three hundred") - 0.3, rect=(0.06, 0.12, 0.32, 0.2), xmax=470, unit="thousand km²", dec=0)
    S.brand()


def m13_baikal(S):
    mapbase(S)
    t_truth = S.c("Not by area")
    S.camera([(0, 106, 66, 60), (S.T, 108, 65, 50)])
    myth(S, 13, "The biggest lakes hold the most fresh water", "LAKE BAIKAL: ~20% OF UNFROZEN SURFACE FRESH WATER",
         t_truth)
    S.highlight(lake("Lake Baikal"), CYAN, 0.6, peak=1.0)
    dot(S, 108.5, 53.6, "Lake Baikal", S.c("Lake Baikal"), color=CYAN, dx=2, ha="left", size=26)
    S.text(0.5, 0.25, "Deepest lake on Earth: 1,600+ m", S.c("deepest lake"), size=36, color=AMBER, box=True)
    S.brand()


def m14_continents(S):
    allr = [(n, r) for n in COUNTRIES for r in COUNTRIES[n]]
    col = {"Africa": AMBER, "Europe": CYAN, "Asia": PINK, "North America": GREEN, "South America": VIOLET,
           "Oceania": "#ff9e00", "Antarctica": "#e8f4ff", "Seven seas (open ocean)": LAND}
    pc = PolyCollection([equal_earth(r) for _, r in allr], edgecolors=EDGE, linewidths=0.4, zorder=2)
    S.ax.add_collection(pc)
    S.camera([(0, 0, 5, 380), (S.T, 0, 5, 370)])
    t_truth = S.c("But in many")
    myth(S, 14, "Everyone agrees there are seven continents", "IT DEPENDS WHERE YOU WENT TO SCHOOL", t_truth)
    t6, t6b, t5 = S.c("joining North"), S.c("Others join"), S.c("And the five")
    import matplotlib.colors as mc

    def colour(n, mode):
        c = CONT.get(n, "")
        if mode >= 1 and c == "South America":
            c = "North America"
        if mode == 2:
            c = CONT.get(n, "")
            if c == "Europe":
                c = "Asia"
        if mode == 3:
            c = CONT.get(n, "")
            if c == "South America":
                c = "North America"
            if c == "Antarctica":
                return LAND
        return col.get(c, LAND)

    def up(t):
        mode = 0 if t < t6 else 1 if t < t6b else 2 if t < t5 else 3
        pc.set_facecolors([colour(n, mode) for n, _ in allr])
    S.updaters.append(up)
    for txt, t0, t1 in [("7 CONTINENTS", S.c("kids learn seven"), t6), ("6: THE AMERICAS AS ONE", t6, t6b),
                        ("6: EURASIA", t6b, t5), ("5 OLYMPIC RINGS: INHABITED CONTINENTS", t5, S.T + 1)]:
        S.text(0.5, 0.2, txt, t0, t1, size=40, box=True)
    S.brand()


def m15_hemispheres(S):
    mapbase(S, proj=equal_earth, grid=False)
    S.camera([(0, 0, 5, 380), (S.T, 0, 5, 370)])
    t_truth = S.c("Roughly ninety")
    myth(S, 15, "People are spread evenly around the globe", "~90% LIVE IN THE NORTHERN HEMISPHERE", t_truth)
    y0 = equal_earth(np.array([[0, 0.0]]))[0][1]
    north = Rectangle((-200, y0), 400, 120, color=AMBER, alpha=0, zorder=1)
    south = Rectangle((-200, y0 - 120), 400, 120, color=CYAN, alpha=0, zorder=1)
    S.ax.add_patch(north)
    S.ax.add_patch(south)
    eq, = S.ax.plot([-200, 200], [y0, y0], color=WHITE, lw=2.5, ls=(0, (6, 4)), zorder=5, alpha=0)

    def up(t):
        a = ease((t - t_truth) / 0.6)
        north.set_alpha(0.11 * a)
        south.set_alpha(0.08 * a)
        eq.set_alpha(a)
    S.updaters.append(up)
    S.highlight(["China", "India", "United States of America"], AMBER, S.c("the giants"), peak=0.85, proj=equal_earth)
    S.text(0.12, 0.6, "≈ 90%", t_truth + 0.4, size=64, color=AMBER, box=True, pop=True)
    S.text(0.12, 0.3, "≈ 10%", t_truth + 0.9, size=64, color=CYAN, box=True, pop=True)
    S.brand()


def s99_outro(S):
    S.world(proj=equal_earth, fc="#1a2a3e", ec="#22364f")
    S.camera([(0, 0, 10, 380), (S.T, 0, 10, 360)])
    S.text(0.5, 0.62, "HOW MANY DID YOU BELIEVE?", 0.3, size=64, pop=True)
    S.text(0.5, 0.50, "Tell me your score in the comments", S.c("Tell me"), size=34, color=MUTED, font=REG)
    S.text(0.5, 0.30, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=60, box=True, pop=True)
    S.fade_in_out(0, 1.5)
    S.brand()
