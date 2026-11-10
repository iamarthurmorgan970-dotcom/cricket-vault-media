"""Kedarkantha vs Brahmatal. Each function takes the Scene S; S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.india import *
from engine.extras import peaks_chart
from matplotlib.patches import Polygon as MPoly

KK, BT = GREEN, CYAN
# approximate locations (lon, lat)
SANKRI = (78.18, 31.08)
KK_TOP = (78.24, 31.02)
LOHAJUNG = (79.62, 30.10)
BT_TOP = (79.67, 30.14)
DEHRADUN = (78.03, 30.32)
KATHGODAM = (79.52, 29.27)
RISHIKESH = (78.27, 30.09)
TRISHUL = (79.78, 30.31)
NANDA_GHUNTI = (79.72, 30.47)
UK_VIEW = (79.0, mercy(30.2), 6.2)


def P(lonlat):
    return merc(np.array([lonlat]))[0]


def dashed(S, a, b, t0, color=GOLD, lw=3, t1=None, dur=1.0):
    pa, pb = P(a), P(b)
    ln, = S.ax.plot([pa[0], pa[0]], [pa[1], pa[1]], color=color, lw=lw, ls=(0, (5, 4)), zorder=25, alpha=0)
    t1 = S.T + 1 if t1 is None else t1

    def up(t):
        g = ease2((t - t0) / dur)
        ln.set_data([pa[0], pa[0] + (pb[0] - pa[0]) * g], [pa[1], pa[1] + (pb[1] - pa[1]) * g])
        ln.set_alpha(min(1.0 if g > 0 else 0, ease((t1 - t) / 0.4)))
    S.updaters.append(up)


def board(S, rows, title=None, y0=0.66, dy=0.115, t_head=0.3, kk_x=0.42, bt_x=0.76, label_x=0.06):
    """Versus board: header KEDARKANTHA | BRAHMATAL, then rows (label, kk_text, bt_text, phrase)."""
    bg = FancyBboxPatch((0.03, y0 - dy * (len(rows) - 0.4)), 0.94, 0.22 + dy * (len(rows) - 0.4),
                        transform=S.fig.transFigure, boxstyle="round,pad=0,rounding_size=0.02", fc="#07111d",
                        ec="none", alpha=0, zorder=40)
    S.fig.add_artist(bg)
    S.updaters.append(lambda t: bg.set_alpha(0.75 * ease((t - t_head) / 0.4)))
    if title:
        S.text(0.5, 0.91, title, t_head, size=46, pop=True)
    S.text(kk_x, y0 + 0.12, "KEDARKANTHA", t_head, size=34, color=KK)
    S.text(bt_x, y0 + 0.12, "BRAHMATAL", t_head, size=34, color=BT)
    for i, (lab, a, b, ph) in enumerate(rows):
        t0 = S.c(ph) if isinstance(ph, str) else ph
        y = y0 - i * dy
        S.text(label_x, y, lab, t0, size=26, color=MUTED, ha="left", font=BOLD)
        S.text(kk_x, y, a, t0 + 0.2, size=30, color=WHITE)
        S.text(bt_x, y, b, t0 + 0.5, size=30, color=WHITE)


def uk_map(S, keys=None):
    india(S, keys or [(0, *UK_VIEW), (S.T, UK_VIEW[0], UK_VIEW[1], UK_VIEW[2] * 0.92)])
    S.highlight(ST["Uttarakhand"], "#3a5a85", 0.0, peak=0.6, lw=1.5)


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    uk_map(S, [(0, 79.0, mercy(30.4), 9), (S.T, 79.0, mercy(30.5), 6.5)])
    pin(S, *KK_TOP, "KEDARKANTHA", S.c("Two of India"), color=KK, dy=2.4)
    pin(S, *BT_TOP, "BRAHMATAL", S.c("Two of India") + 0.5, color=BT, dy=2.4)
    S.headline("SAME HEIGHT: ≈ 3,800 M", S.c("about three thousand"), S.c("But on one"), y=0.88, color=AMBER)
    S.headline("ONE: ≈ 400 M MORE CLIMBING", S.c("But on one"), S.c("And from the top"), y=0.88, color=KK)
    S.headline("ONE: A PEAK ALMOST 2× HIGHER", S.c("And from the top"), S.c("Kedarkantha or"), y=0.88, color=BT)
    S.headline("WHICH ONE IS YOURS?", S.c("Kedarkantha or"), y=0.1, size=52)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    S.world(fc="#1a2a3e", ec="#22364f")
    S.ax.add_collection(PolyCollection([merc(r) for r in INDIA_POV], facecolors="#22385a", edgecolors="#2f4a70",
                                       linewidths=0.8))
    S.ax.add_collection(PolyCollection([merc(r) for rs in ST.values() for r in rs], facecolors="#22385a",
                                       edgecolors="#2f4a70", linewidths=0.6))
    S.camera([(0, 79, mercy(30), 16), (S.T, 79, mercy(30), 13)])
    S.text(0.5, 0.62, "KEDARKANTHA", 0.3, size=86, color=KK, pop=True)
    S.text(0.5, 0.5, "vs", 0.6, size=50, color=WHITE)
    S.text(0.5, 0.38, "BRAHMATAL", 0.9, size=86, color=BT, pop=True)
    S.text(0.5, 0.25, "Which is the best first snow trek?", 1.3, size=32, color=MUTED, font=REG)
    S.text(0.5, 0.88, "TRUE SCALE  ·  TREK vs TREK", 0.0, size=28, color=AMBER)


def p01_where(S):
    t_z = S.c("but in different")
    india(S, [(0, *INDIA_VIEW), (t_z, *UK_VIEW), (S.T, UK_VIEW[0], UK_VIEW[1], 5.8)], hl=["Uttarakhand"],
          hl_color=AMBER, t_hl=0.6)
    state_tag(S, "UTTARAKHAND", 0.5)
    pin(S, *SANKRI, "Sankri", S.c("Its base village is Sankri"), color=KK, dy=2.0)
    pin(S, *KK_TOP, "", S.c("Kedarkantha is in"), color=KK, ring=False)
    pin(S, *DEHRADUN, "Dehradun", S.c("from Dehradun"), color=WHITE, ring=False, dy=-2.6, size=22)
    pin(S, *LOHAJUNG, "Lohajung", S.c("Its base village is Lohajung"), color=BT, dy=2.0)
    S.text(0.5, 0.2, "Kedarkantha: Uttarkashi district", S.c("Kedarkantha is in"), S.c("Brahmatal is further"),
           size=32, color=KK, box=True)
    S.text(0.5, 0.2, "Brahmatal: Chamoli district (Roopkund's base too)", S.c("Brahmatal is further"),
           S.c("Two treks"), size=32, color=BT, box=True)
    dashed(S, SANKRI, LOHAJUNG, S.c("Two treks"))
    S.text(0.5, 0.2, "≈ 175 km apart, as the crow flies", S.c("Two treks") + 0.6, size=34, color=GOLD, box=True)


def peak_mark(S, lonlat, label, t0, color=WHITE, dy=0.06):
    p = P(lonlat)
    sc = S.ax.scatter([p[0]], [p[1]], marker="^", s=0, color=color, edgecolors="#07111d", linewidths=1.5, zorder=26)
    tx = S.ax.text(p[0], p[1] + dy, label, fontproperties=BOLD, size=20, color=color, ha="center", va="bottom",
                   zorder=27, alpha=0)

    def up(t):
        a = ease((t - t0) / 0.4)
        sc.set_sizes([300 * a])
        tx.set_alpha(a)
    S.updaters.append(up)


def zoom(S, top, center, width, zoom_phrase, name, color, base, base_name, cards, head, top_dy=2.2, base_kw=None):
    t_z = S.c(zoom_phrase)
    uk_map(S, [(0, *UK_VIEW), (t_z + 0.5, center[0], mercy(center[1]), width),
               (S.T, center[0], mercy(center[1]), width * 0.9)])
    state_tag(S, "UTTARAKHAND", 0.3)
    S.headline(head, 0.6, y=0.88, color=color)
    pin(S, *top, name, t_z + 0.8, color=color, dy=top_dy)
    pin(S, *base, base_name, t_z + 1.2, color=WHITE, ring=False, size=22, **(base_kw or {}))
    for c in cards:
        card(S, *c)


def p02_kk(S):
    zoom(S, KK_TOP, (78.36, 31.04), 1.6, "Kedarkantha is a summit", "KEDARKANTHA", KK, SANKRI, "Sankri", [
        ("Forest of pine, oak and maple", "You walk up", 0.2, KK, S.c("camp beside")),
        ("Camp at Juda ka Talab, a small lake", "camp beside", 0.2, CYAN, S.c("The summit is")),
        ("Summit ≈ 3,800 m", "The summit is", 0.2, AMBER, S.c("including Swargarohini")),
        ("Views: Swargarohini · Bandarpunch · Black Peak", "including Swargarohini", 0.2, WHITE,
         S.c("It's often")),
        ("Often called one of India's most popular winter treks", "It's often", 0.2, KK)], "A SUMMIT TREK",
        top_dy=-3.8, base_kw=dict(dy=1.4))
    peak_mark(S, (78.52, 31.09), "SWARGAROHINI", S.c("including Swargarohini") + 0.3)
    peak_mark(S, (78.55, 31.00), "BANDARPUNCH", S.c("Bandarpunch"), dy=-0.075)


def p03_bt(S):
    zoom(S, BT_TOP, (79.70, 30.31), 1.9, "Brahmatal is a ridge", "BRAHMATAL", BT, LOHAJUNG, "Lohajung", [
        ("Oak and rhododendron forest", "You walk through", 0.1, BT, S.c("then climb")),
        ("Bekaltal, the first lake  ·  then a long open ridge", "then climb", 0.1, WHITE,
         S.c("The highest point")),
        ("Brahmatal Top ≈ 3,700–3,800 m (sources differ)", "The highest point", 0.1, AMBER, S.c("The lake below")),
        ("Named after Lord Brahma", "The lake below", 0.1, WHITE, S.c("In winter")),
        ("In winter, both lakes can freeze", "In winter", 0.1, CYAN)], "A RIDGE AND LAKE TREK",
        base_kw=dict(dy=-1.0, dx=-3, ha="right"))
    peak_mark(S, TRISHUL, "TRISHUL", 2.0, color=AMBER)
    peak_mark(S, NANDA_GHUNTI, "NANDA GHUNTI", 2.4, color=VIOLET)


def p04_height(S):
    peaks_chart(S, [("KEDARKANTHA", "summit", 3.8, KK, "Kedarkantha summit"),
                    ("BRAHMATAL TOP", "highest point", 3.75, BT, "Brahmatal Top")],
                "HIGHEST POINT", ymax_km=4.6, width=12,
                captions=[("ON HEIGHT ALONE: A TIE", "this is a tie", None, AMBER)])
    S.brand()


def p05_climb(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(-2.0, 5.0)
    S.text(0.5, 0.92, "HOW MUCH YOU ACTUALLY CLIMB", 0.3, size=44, pop=True)
    S.text(0.5, 0.855, "Base village to highest point, metres above sea level", 0.6, size=24, color=MUTED, font=REG)
    ax.plot([0, 16], [0, 0], color=MUTED, lw=2)
    for k in range(1, 5):
        ax.plot([0, 16], [k, k], color="#16283c", lw=1, zorder=0)
        ax.text(0.15, k + 0.05, f"{k},000 m", fontproperties=REG, size=16, color=MUTED, va="bottom")
    cols = [("KEDARKANTHA", "from Sankri", 1.95, 3.80, KK, "Sankri sits", "So on Kedarkantha", 4.6),
            ("BRAHMATAL", "from Lohajung", 2.32, 3.73, BT, "Lohajung sits", "On Brahmatal", 10.6)]
    for name, sub, base, top, col, ph_b, ph_g, cx in cols:
        tb, tg = S.c(ph_b), S.c(ph_g)
        bb = Rectangle((cx - 1.4, 0), 2.8, 0, color="#3b5476", zorder=3)
        gb = Rectangle((cx - 1.4, base), 2.8, 0, color=col, zorder=3, alpha=0.9)
        ax.add_patch(bb)
        ax.add_patch(gb)
        lb = ax.text(cx, 0, "", fontproperties=BOLD, size=24, color=WHITE, ha="center", va="center", zorder=5)
        lg = ax.text(cx, 0, "", fontproperties=BOLD, size=30, color="#07111d", ha="center", va="center", zorder=5)
        nm = ax.text(cx, -0.15, f"{name}\n{sub}", fontproperties=BOLD, size=22, color=col, ha="center", va="top",
                     zorder=5, alpha=0)

        def up(t, bb=bb, gb=gb, lb=lb, lg=lg, nm=nm, tb=tb, tg=tg, base=base, top=top, cx=cx):
            g1 = ease2((t - tb) / 1.0)
            bb.set_height(base * g1)
            lb.set_position((cx, base * g1 / 2))
            lb.set_text(f"start ≈ {base * 1000 * g1:,.0f} m" if g1 > 0.05 else "")
            nm.set_alpha(ease((t - tb) / 0.4))
            g2 = ease2((t - tg) / 1.0)
            gb.set_height((top - base) * g2)
            gain = round((top - base) * 1000 / 50) * 50
            lg.set_position((cx, base + (top - base) * g2 / 2))
            lg.set_text(f"+ {gain * g2:,.0f} m" if g2 > 0.05 else "")
        S.updaters.append(up)
    S.caption("≈ 400 m MORE CLIMBING ON KEDARKANTHA  (taller than the Eiffel Tower)", S.c("That's about"),
              color=KK, size=32)
    S.brand()


def p06_days(S):
    S.graticule(step=5)
    board(S, [("Typical trip", "6 days", "6 days", "usually sold"),
              ("Walking days", "≈ 4", "≈ 4", "with about four"),
              ("On foot", "≈ 20–23 km", "≈ 22–28 km", "Kedarkantha covers"),
              ("Varies by", "operator & route", "operator & route", "Trek lengths vary")],
          title="DISTANCE AND DAYS", y0=0.62, dy=0.13)
    S.caption("Always check the exact itinerary you book", S.c("so always check"), color=AMBER)
    S.brand()


def p07_access(S):
    uk_map(S, [(0, 79.0, mercy(30.05), 7.6), (S.T, 79.0, mercy(30.05), 7.2)])
    t1 = S.c("For Kedarkantha")
    t2 = S.c("For Brahmatal")
    pin(S, *DEHRADUN, "Dehradun", t1, color=WHITE, ring=False, dy=-4.2, size=22)
    pin(S, *SANKRI, "Sankri", t1 + 0.4, color=KK, dy=2.2)
    dashed(S, DEHRADUN, SANKRI, t1 + 0.6, color=KK, dur=1.5)
    pin(S, *KATHGODAM, "Kathgodam (rail)", S.c("Kathgodam"), color=WHITE, ring=False, dy=-4.2, size=22)
    pin(S, *RISHIKESH, "Rishikesh", S.c("or from Rishikesh"), color=WHITE, ring=False, dy=-4.2, size=22)
    pin(S, *LOHAJUNG, "Lohajung", t2, color=BT, dy=2.2)
    dashed(S, KATHGODAM, LOHAJUNG, S.c("Kathgodam") + 0.3, color=BT, dur=1.5)
    dashed(S, RISHIKESH, LOHAJUNG, S.c("or from Rishikesh") + 0.3, color=BT, dur=1.5)
    S.text(0.5, 0.9, "Dehradun to Sankri: ≈ 200 km, 7–11 hours", t1 + 0.8, t2, size=32, color=KK, box=True)
    S.text(0.5, 0.9, "Kathgodam ≈ 200 km · Rishikesh ≈ 270 km: 10–12 hours", S.c("Kathgodam"),
           S.c("Lohajung is the more"), size=30, color=BT, box=True)
    S.text(0.5, 0.9, "Lohajung is the more remote base", S.c("Lohajung is the more"), size=34, color=AMBER,
           box=True)


def p08_summit(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ts = S.c("Many groups")
    # sky brightening towards sunrise
    sky = Rectangle((0, 0), 16, 9, color="#3a2a4a", zorder=0, alpha=0)
    ax.add_patch(sky)
    sun = Circle((11.5, 3.0), 1.0, color=AMBER, zorder=1, alpha=0)
    ax.add_patch(sun)
    mt = MPoly([[1, 0.6], [8, 7.2], [15, 0.6]], closed=True, fc="#2c4262", ec="#4f6d94", lw=2, zorder=2)
    ax.add_patch(mt)
    snow = MPoly([[6.2, 5.5], [8, 7.2], [9.8, 5.5], [9.0, 5.8], [8.3, 5.3], [7.4, 5.8]], closed=True, fc="#e8f4ff",
                 ec="none", zorder=3)
    ax.add_patch(snow)
    path = np.array([[3.0, 0.9], [5.0, 1.6], [4.2, 2.3], [6.3, 3.1], [5.6, 3.9], [7.2, 4.8], [6.8, 5.6], [7.7, 6.4],
                     [8.0, 7.2]])
    seg = np.cumsum(np.r_[0, np.hypot(*np.diff(path, axis=0).T)])
    ln, = ax.plot([], [], color=KK, lw=4, ls=(0, (2, 2)), zorder=5)
    dot = ax.scatter([path[0, 0]], [path[0, 1]], s=0, color=KK, edgecolors=WHITE, linewidths=2, zorder=6)
    t_go, t_end = ts, S.c("The whole day") + 1.0

    def up(t):
        g = ease2((t - t_go) / (t_end - t_go))
        L = seg[-1] * g
        k = np.searchsorted(seg, L)
        pts = path[:max(k, 1)]
        if k < len(path) and k > 0:
            u = (L - seg[k - 1]) / (seg[k] - seg[k - 1])
            pts = np.vstack([path[:k], path[k - 1] + (path[k] - path[k - 1]) * u])
        ln.set_data(pts[:, 0], pts[:, 1])
        dot.set_offsets([pts[-1]])
        dot.set_sizes([220 * ease((t - t_go) / 0.4)])
        s = ease((t - t_go) / (t_end - t_go))
        sky.set_alpha(0.9 * s)
        sun.set_alpha(s)
        sun.center = (11.5, 3.0 + 3.5 * s)
    S.updaters.append(up)
    S.headline("KEDARKANTHA: SUMMIT DAY", 0.3, y=0.92, color=KK)
    S.text(0.04, 0.78, "Start ≈ 4 AM, in the dark", S.c("around four"), size=30, color=WHITE, ha="left", box=True)
    S.text(0.04, 0.68, "Steep zigzag, often in snow", S.c("The final climb"), size=30, color=WHITE, ha="left",
           box=True)
    S.text(0.04, 0.58, "≈ 7–8 hours up and down", S.c("The whole day"), size=30, color=AMBER, ha="left", box=True)
    S.caption("A real summit, mountains on every side", S.c("It's tough"), color=KK)
    S.brand()


def p09_views(S):
    peaks_chart(S, [("BRAHMATAL TOP", "where you stand", 3.75, BT, "From the ridge"),
                    ("NANDA GHUNTI", "≈ 6,309 m", 6.309, VIOLET, "And Nanda Ghunti"),
                    ("TRISHUL", "≈ 7,120 m", 7.12, AMBER, "Trishul, about")],
                "THE VIEW FROM BRAHMATAL, TO SCALE", ymax_km=8.2, width=15,
                captions=[("Trishul: often called the first 7,000 m peak climbed (1907)", "often described",
                           "And Nanda Ghunti", AMBER),
                          ("Trishul ≈ 1.9× the height of Brahmatal Top", "Trishul is almost", None, AMBER)])
    S.brand()


def p10_ridge(S):
    uk_map(S, [(0, 79.70, mercy(30.29), 1.4), (S.T, 79.70, mercy(30.29), 1.3)])
    S.headline("BRAHMATAL: A DAY OF BIG VIEWS", 0.3, y=0.9, color=BT)
    L = dict(ha="right", dx=-2.5, dy=-1.0)
    Rt = dict(ha="left", dx=2.5, dy=-1.0)
    pin(S, *LOHAJUNG, "Lohajung", 0.6, color=WHITE, ring=False, size=22, **L)
    pin(S, *BT_TOP, "Brahmatal Top", S.c("on to Brahmatal Top"), color=BT, size=24, **Rt)
    pin(S, 79.70, 30.21, "Ali & Bedni Bugyal (Roopkund route)", S.c("You also look"), color=GREEN, size=22, **L)
    pin(S, *TRISHUL, "TRISHUL", 1.2, color=AMBER, ring=False, size=24, **Rt)
    pin(S, *NANDA_GHUNTI, "NANDA GHUNTI", 1.6, color=VIOLET, ring=False, size=24, **Rt)
    S.text(0.5, 0.12, "Ridge: Tilandi  ·  Jhandi Top  ·  Brahmatal Top", S.c("The Brahmatal ridge"),
           S.c("You also look"), size=32, color=WHITE, box=True)
    S.text(0.5, 0.12, "Meadows of the Roopkund trek, across the valley", S.c("You also look"),
           S.c("Instead of one"), size=32, color=GREEN, box=True)
    S.text(0.5, 0.12, "Many call it the more scenic of the two", S.c("Instead of one"), size=34, color=BT, box=True)


MONTHS = "J F M A M J J A S O N D".split()


def p11_snow(S):
    S.graticule(step=5)
    S.text(0.5, 0.92, "WHEN TO GO", 0.3, size=46, pop=True)
    x0, wbox, y_kk, y_bt = 0.2, 0.062, 0.62, 0.38
    for i, m in enumerate(MONTHS):
        S.text(x0 + (i + 0.5) * wbox, 0.78, m, 0.4, size=26, color=MUTED)
    S.text(0.04, y_kk, "KEDAR-\nKANTHA", 0.4, size=24, color=KK, ha="left")
    S.text(0.04, y_bt, "BRAHMA-\nTAL", 0.4, size=24, color=BT, ha="left")

    def cell(i, y, color, t0, alpha=0.9):
        r = FancyBboxPatch((x0 + i * wbox + 0.004, y - 0.06), wbox - 0.008, 0.12, transform=S.fig.transFigure,
                           boxstyle="round,pad=0,rounding_size=0.008", fc=color, ec="none", alpha=0, zorder=40)
        S.fig.add_artist(r)
        S.updaters.append(lambda t: r.set_alpha(alpha * ease((t - t0) / 0.4)))

    t_open = S.c("Kedarkantha is open")
    for i in range(12):
        cell(i, y_kk, "#2c4262", 0.5)
        cell(i, y_bt, "#2c4262", 0.5)
        if i not in (6, 7):
            cell(i, y_kk, KK, t_open + 0.05 * i, 0.45)
    t_snow = S.c("both usually have snow")
    for i in (11, 0, 1):
        cell(i, y_kk, "#e8f4ff", t_snow, 0.95)
        cell(i, y_bt, "#e8f4ff", t_snow + 0.3, 0.95)
    for i in (9, 10):
        cell(i, y_bt, BT, S.c("lovely in autumn"), 0.7)
    cell(2, y_bt, PINK, S.c("rhododendrons"), 0.8)
    S.text(0.5, 0.2, "White = usual snow months (Dec–Feb)", t_snow, S.c("Kedarkantha is open"), size=28,
           color=WHITE, box=True)
    S.text(0.5, 0.2, "Kedarkantha: open ≈ 10 months, closed in the monsoon", t_open, S.c("Brahmatal is lovely"),
           size=28, color=KK, box=True)
    S.text(0.5, 0.2, "Brahmatal: autumn = clear views · March = rhododendrons", S.c("Brahmatal is lovely"),
           S.c("If snow is"), size=28, color=BT, box=True)
    S.text(0.5, 0.2, "Best bet for snow: late December to February", S.c("If snow is"), size=32, color=AMBER,
           box=True)
    S.brand()


def p12_crowds(S):
    S.graticule(step=5)
    board(S, [("Busiest", "mid-Dec to mid-Jan", "busy in winter", "gets extremely"),
              ("Crowd level", "very high (Sankri side)", "lower", "but it sees fewer"),
              ("Quieter option", "other base villages", "autumn, after Diwali", "Some operators")],
          title="CROWDS", y0=0.6, dy=0.14)
    S.caption("Kedarkantha's fame is also its problem", S.c("Kedarkantha's fame"), S.c("One major"), color=PINK)
    S.caption("Source: Indiahikes trek guide", S.c("One major"), color=MUTED, size=26)
    S.brand()


def p13_fitness(S):
    S.graticule(step=5)
    board(S, [("Rating", "Easy–Moderate", "Easy–Moderate", "Both are usually rated"),
              ("Fitness target", "5 km in < 40 min", "5 km in < 40 min", "A common fitness"),
              ("Hardest part", "one long summit day", "spread over days", "The difference is")],
          title="HOW HARD IS IT?", y0=0.6, dy=0.14)
    S.caption("Suitable for fit beginners", S.c("suitable for fit"), S.c("A common fitness"), color=GREEN)
    S.brand()


def p14_rules(S):
    S.graticule(step=5)
    S.text(0.5, 0.86, "BEFORE YOU BOOK", 0.3, size=54, color=AMBER, pop=True)
    rows = [("Jan 2026: Uttarakhand drafts new trekking rules", "In January"),
            ("Operators registered  ·  certified guides", "including registration"),
            ("Trekkers: insurance + medical certificate (draft)", "The draft also"),
            ("Rules can change: check with your operator", "Draft rules can")]
    for i, (txt, ph) in enumerate(rows):
        S.text(0.5, 0.66 - i * 0.14, txt, S.c(ph), size=34, color=WHITE if i < 3 else AMBER, box=True)
    S.brand()


def p15_verdict(S):
    S.graticule(step=5)
    S.text(0.5, 0.92, "THE VERDICT", 0.3, size=50, pop=True)
    for x, name, col, ph, items in [
            (0.27, "PICK KEDARKANTHA IF...", KK, "Pick Kedarkantha",
             [("you want a real summit", "standing on a real"), ("you don't mind crowds", "if you don't mind"),
              ("you can push hard for one day", "push hard")]),
            (0.73, "PICK BRAHMATAL IF...", BT, "Pick Brahmatal",
             [("you want bigger mountain views", "bigger mountain"), ("frozen lakes + a ridge walk", "frozen lakes"),
              ("a little less climbing & crowd", "a little less")])]:
        S.text(x, 0.76, name, S.c(ph), size=38, color=col, box=True, pop=True)
        for i, (txt, p) in enumerate(items):
            S.text(x, 0.6 - i * 0.12, txt, S.c(p), size=30, color=WHITE)
    S.caption("Either way: a superb first taste of Himalayan snow", S.c("Either way"), color=AMBER)
    S.brand()


def s99_outro(S):
    uk_map(S, [(0, *UK_VIEW), (S.T, UK_VIEW[0], UK_VIEW[1], 5.6)])
    pin(S, *KK_TOP, "KEDARKANTHA", 0.3, color=KK, dy=-3.8)
    pin(S, *BT_TOP, "BRAHMATAL", 0.5, color=BT, dy=-3.8)
    S.text(0.5, 0.9, "WHICH ONE WOULD YOU PICK?", S.c("Which one"), size=50, box=True, pop=True)
    S.text(0.5, 0.1, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=52, box=True, pop=True)
    S.fade_in_out(0, 1.5)


def hold(sid):
    return 1.5 if sid.startswith("p") else 0.0
