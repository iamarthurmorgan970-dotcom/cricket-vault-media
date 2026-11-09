"""Scenes for this episode. Each function takes the Scene S; S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.india import *
from engine.extras import peaks_chart

# ------------------------------------------------------------------ scenes
def s01_hook(S):
    india(S, [(0, 82, mercy(23), 60), (S.T, 82, mercy(23), 50)])
    for (lo, la, lab, ph, col) in [(76.51, 19.98, "Meteorite crater lake", "a crater", CYAN),
                                    (78.28, 14.81, "A canyon", "A canyon", AMBER),
                                    (91.68, 25.25, "Living bridges", "Bridges", GREEN),
                                    (76.9, 33.6, "A frozen river", "frozen river", "#e8f4ff")]:
        pin(S, lo, la, lab, S.c(ph), color=col, size=24)
    S.headline("MOST INDIANS HAVE NEVER SEEN THEM", S.c("Most Indians"), y=0.08, size=40)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    S.world(fc="#1a2a3e", ec="#22364f")
    S.ax.add_collection(PolyCollection([merc(r) for r in INDIA_POV], facecolors="#22385a", edgecolors="#2f4a70",
                                       linewidths=0.8))
    S.ax.add_collection(PolyCollection([merc(r) for rs in ST.values() for r in rs], facecolors="#22385a",
                                       edgecolors="#2f4a70", linewidths=0.6))
    S.camera([(0, 82, mercy(22), 70), (S.T, 82, mercy(22), 62)])
    S.text(0.5, 0.58, "INDIA'S HIDDEN WONDERS", 0.3, size=82, pop=True)
    S.text(0.5, 0.45, "AT TRUE SCALE", 0.7, size=82, color=AMBER, pop=True)
    S.text(0.5, 0.33, "Craters, canyons, living bridges and high treks", 1.2, size=30, color=MUTED, font=REG)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=CYAN)


def p01_states(S):
    S.graticule()
    S.world()
    t_lift = S.c("Let's lift")
    t_goa = S.c("Now look at Goa")
    S.camera([(0, 75, mercy(26), 70), (t_lift, 45, mercy(36), 95), (t_lift + 4, 15, mercy(45), 55),
              (t_goa - 0.3, 15, mercy(45), 55), (t_goa + 1.2, 74.5, mercy(22), 30), (S.T, 74, mercy(20), 26)])
    raj = ST["Rajasthan"]
    S.highlight(raj, AMBER, 0.4, t_lift, peak=0.85)
    S.highlight(["Italy"], GREEN, t_lift + 3.5, t_goa, peak=0.6)
    S.highlight(["Poland"], CYAN, S.c("bigger than Poland"), t_goa, peak=0.6)
    S.mover(raj, (73.8, 26.6), (12.5, 43.0), t_lift, t_lift + 4.0, color=AMBER, label="RAJASTHAN", t_hide=t_goa)
    S.headline("BIGGER THAN ITALY", S.c("It's bigger than Italy"), S.c("bigger than Poland"), color=GREEN)
    S.headline("BIGGER THAN POLAND", S.c("bigger than Poland"), t_goa, color=CYAN)
    S.highlight(ST["Goa"], PINK, t_goa, peak=1.0, lw=2)
    S.highlight(raj, AMBER, t_goa + 0.5, peak=0.55)
    pin(S, 74.0, 15.35, "GOA", t_goa + 0.5, color=PINK, dy=0.5)
    S.bars([("Rajasthan", 342, AMBER, S.c("three hundred and forty") if False else t_goa + 0.8),
            ("Goa", 3.7, PINK, S.c("three thousand seven"))],
           t_goa + 0.5, rect=(0.62, 0.12, 0.30, 0.2), xmax=600, unit="thousand km²", dec=1)
    S.headline("GOA FITS INSIDE RAJASTHAN 90+ TIMES", S.c("You could fit"), y=0.08, color=PINK, size=38)
    S.brand()


def place(S, state, lon, lat, name, width, cards, extra=None, color=AMBER, zoom_phrase=None, center=None):
    t_z = S.c(zoom_phrase) if zoom_phrase else 1.2
    clon, clat = center or (lon, lat)
    india(S, [(0, *INDIA_VIEW), (t_z, clon, mercy(clat), width), (S.T, clon, mercy(clat), width * 0.9)],
          hl=[state] if state else None)
    state_tag(S, state.upper() if state else "")
    pin(S, lon, lat, name, t_z + 0.6, color=color, dy=2.2)
    for c in cards:
        card(S, *c)
    if extra:
        extra(S)


def p02_monolith(S):
    place(S, "Karnataka", 77.29, 12.92, "SAVANDURGA", 9, [
        ("One of Asia's largest monolith hills", "often described", 0.2, AMBER, S.c("A monolith is")),
        ("Monolith = a single, massive piece of rock", "A monolith is", 0.2, WHITE, S.c("Savandurga's twin")),
        ("≈ 1,226 m above sea level", "Savandurga's twin", 0.2, CYAN)], zoom_phrase="About sixty",
        extra=lambda S: pin(S, 77.59, 12.97, "Bengaluru", S.c("Bengaluru"), color=WHITE, ring=False, dy=-3.2, size=22))


def p03_lonar(S):
    place(S, "Maharashtra", 76.51, 19.98, "LONAR CRATER LAKE", 10, [
        ("Crater ≈ 1.8 km wide, ≈ 150 m deep", "inside a crater", 0.2, CYAN, S.c("It was created")),
        ("Made by a meteorite impact", "It was created", 0.2, AMBER, S.c("The water is")),
        ("Salty and strongly alkaline", "The water is", 0.2, WHITE, S.c("And in June")),
        ("June 2020: the lake turned pink", "And in June", 0.2, PINK)], zoom_phrase="In the middle")


def p04_gandikota(S):
    place(S, "Andhra Pradesh", 78.28, 14.81, "GANDIKOTA", 9, [
        ('"The Grand Canyon of India"', "earning it", 0.2, AMBER, S.c("Right on the edge")),
        ("Gorge carved by the Penna River", "the Penna", 0.32, WHITE, S.c("earning it")),
        ("Clifftop fort, ≈ 800 years of history", "Right on the edge", 0.2, CYAN)], zoom_phrase="At Gandikota")


def p05_kutch(S):
    place(S, "Gujarat", 70.21, 23.89, "DHOLAVIRA", 10, [
        ("Great Rann of Kutch: a white salt desert", "the Great Rann", 0.2, WHITE, S.c("And on an island")),
        ("Indus Valley city, 4,000+ years old", "Dholavira", 0.2, AMBER, S.c("In twenty twenty-one")),
        ("UNESCO World Heritage Site, 2021", "In twenty twenty-one", 0.2, GREEN)], zoom_phrase="Further west")


def p06_majuli(S):
    def ex(S):
        lc = LineCollection([merc(l) for l in river("Brahmaputra")], colors=CYAN, linewidths=5, zorder=20, alpha=0)
        S.ax.add_collection(lc)
        S.updaters.append(lambda t: lc.set_alpha(ease((t - 0.8) / 0.6)))
        S.bars([("1790s", 1300, AMBER, S.c("In the seventeen")), ("Today", 880, PINK, S.c("Today, it's"))],
               S.c("In the seventeen") - 0.3, rect=(0.62, 0.55, 0.32, 0.2), xmax=1600, unit="km²", dec=0)
    place(S, "Assam", 94.2, 26.95, "MAJULI", 9, [
        ("World's largest river island (Guinness)", "recognised by", 0.2, AMBER, S.c("It's home")),
        ("160,000+ people · Vaishnavite satras", "It's home", 0.2, WHITE, S.c("But the river")),
        ("The Brahmaputra is eroding it", "But the river", 0.2, PINK)], extra=ex, zoom_phrase="In the middle")


def p07_meghalaya(S):
    place(S, "Meghalaya", 91.68, 25.25, "LIVING ROOT BRIDGES", 6, [
        ("Rubber fig roots, guided across rivers", "They guide", 0.2, GREEN, S.c("There are about")),
        ("≈ 100 bridges in ≈ 70 villages", "There are about", 0.2, WHITE, S.c("They need")),
        ("Mawsynram: ≈ 11,900 mm of rain a year", "The village of Mawsynram", 0.2, CYAN)], color=GREEN,
        zoom_phrase="Next door",
        extra=lambda S: pin(S, 91.58, 25.30, "Mawsynram", S.c("The village of Mawsynram"), color=CYAN, dy=-3.5,
                            size=22))


def p08_ziro(S):
    place(S, "Arunachal Pradesh", 93.83, 27.55, "ZIRO VALLEY", 8, [
        ("Apatani people: rice and fish in the same fields", "They farm", 0.2, GREEN, S.c("a system so")),
        ("On UNESCO's World Heritage tentative list", "a system so", 0.2, AMBER, S.c("Pine-covered")),
        ("Pine hills, bamboo, almost no crowds", "Pine-covered", 0.2, WHITE)], zoom_phrase="And in Arunachal")


def p08b_flowers(S):
    place(S, "Uttarakhand", 79.6, 30.73, "VALLEY OF FLOWERS", 7, [
        ("Hundreds of species of wildflowers", "hundreds of species", 0.2, PINK, S.c("Together with")),
        ("UNESCO World Heritage, with Nanda Devi NP", "Together with", 0.2, GREEN, S.c("And yet")),
        ("Open a few months a year · on foot only", "And yet", 0.2, AMBER)], color=PINK, zoom_phrase="High in")


TREKS = [("KEDARKANTHA", "Uttarakhand", 3.81, GREEN, "Kedarkantha"),
         ("SANDAKPHU", "West Bengal", 3.636, CYAN, "Sandakphu, in"),
         ("CHADAR", "Ladakh", 3.4, "#e8f4ff", "The Chadar"),
         ("HAMPTA PASS", "Himachal", 4.27, AMBER, "Hampta Pass"),
         ("ROOPKUND", "Uttarakhand", 5.0, PINK, "And Roopkund")]


def p09_treks(S):
    ax = S.ax
    ax.set_xlim(0, 16)
    ax.set_ylim(-1.6, 6.6)
    S.text(0.5, 0.92, "INDIA'S FAMOUS TREKS, SIDE BY SIDE", 0.3, size=44, pop=True)
    S.text(0.5, 0.855, "Highest point, metres above sea level", 0.6, size=24, color=MUTED, font=REG)
    ax.plot([0, 16], [0, 0], color=MUTED, lw=2)
    for k in range(1, 6):
        ax.plot([0, 16], [k, k], color="#16283c", lw=1, zorder=0)
        ax.text(0.15, k + 0.05, f"{k},000 m", fontproperties=REG, size=16, color=MUTED, va="bottom")
    for i, (name, st, h, col, ph) in enumerate(TREKS):
        cx = 2.2 + i * 2.9
        tri = MPoly([[cx - 1.25, 0], [cx + 1.25, 0], [cx, 0]], closed=True, color=col, zorder=3, alpha=0.9)
        ax.add_patch(tri)
        lab = ax.text(cx, 0, "", fontproperties=BOLD, size=26, color=WHITE, ha="center", va="bottom", zorder=5)
        sub = ax.text(cx, -0.25, f"{name}\n{st}", fontproperties=BOLD, size=20, color=col, ha="center", va="top",
                      zorder=5, alpha=0)
        t0 = S.c(ph)

        def up(t, tri=tri, lab=lab, sub=sub, t0=t0, h=h, cx=cx):
            g = ease2((t - t0) / 1.2)
            tri.set_xy([[cx - 1.25, 0], [cx + 1.25, 0], [cx, h * g]])
            lab.set_position((cx, h * g + 0.08))
            lab.set_text(f"≈ {h * 1000 * g:,.0f} m" if g > 0.02 else "")
            sub.set_alpha(ease((t - t0) / 0.4))
        S.updaters.append(up)
    S.caption("Kedarkantha: a favourite first snow trek", S.c("it's a favourite"), S.c("Sandakphu, in"), color=GREEN)
    S.caption("Chadar: lower, but in deep winter", S.c("but in deep winter"), S.c("Hampta Pass"), color="#e8f4ff")
    S.brand()


def p10_sandakphu(S):
    peaks = [("Everest", 86.925, 27.988), ("Lhotse", 86.933, 27.962), ("Makalu", 87.089, 27.889),
             ("Kangchenjunga", 88.147, 27.703)]

    def ex(S):
        s = merc(np.array([[88.0, 27.1]]))[0]
        for i, (n, lo, la) in enumerate(peaks):
            p = merc(np.array([[lo, la]]))[0]
            ln, = S.ax.plot([s[0], p[0]], [s[1], p[1]], color=GOLD, lw=2.5, ls=(0, (5, 4)), zorder=25, alpha=0)
            sc = S.ax.scatter([p[0]], [p[1]], marker="^", s=0, color=WHITE, zorder=26)
            tx = S.ax.text(p[0], p[1] + (0.12 if i % 2 == 0 else -0.22), n.upper(), fontproperties=BOLD, size=20,
                           color=WHITE, ha="center", zorder=27, alpha=0)
            t0 = S.c("Everest, Kangchenjunga") + 0.5 * i

            def up(t, ln=ln, sc=sc, tx=tx, t0=t0):
                a = ease((t - t0) / 0.4)
                ln.set_alpha(a)
                sc.set_sizes([260 * a])
                tx.set_alpha(a)
            S.updaters.append(up)
    place(S, "West Bengal", 88.0, 27.1, "SANDAKPHU", 4.5, [
        ("Highest point in West Bengal · ≈ 3,636 m", "Sandakphu is the highest", 0.2, CYAN,
         S.c("Everest, Kangchenjunga")),
        ("4 of the 5 highest mountains on Earth, in one view", "Everest, Kangchenjunga", 0.2, GOLD)],
        extra=ex, color=CYAN, zoom_phrase="So why", center=(87.45, 27.42))


def p11_roopkund(S):
    place(S, "Uttarakhand", 79.73, 30.26, "ROOPKUND: SKELETON LAKE", 6, [
        ("Remains of 300+ people", "The remains", 0.2, WHITE, S.c("A twenty nineteen")),
        ("Died c. 800 CE  ·  others c. 1800 CE", "Some died", 0.2, PINK, S.c("Nobody knows")),
        ("Nobody knows exactly why", "Nobody knows", 0.2, AMBER)], color=PINK, zoom_phrase="It's a small")


def p12_chadar(S):
    place(S, "Ladakh", 76.9, 33.6, "CHADAR: THE FROZEN ZANSKAR", 7, [
        ("January–February: the river freezes", "In January", 0.2, CYAN, S.c("Trekkers walk")),
        ("Down to about −30°C", "Trekkers walk", 0.2, "#e8f4ff", S.c("In some recent")),
        ("Some winters, the ice doesn't form", "In some recent", 0.2, PINK)], color="#e8f4ff", zoom_phrase="In January")


def s99_outro(S):
    india(S, [(0, *INDIA_VIEW), (S.T, 82, mercy(22), 44)])
    for lo, la, col in [(76.51, 19.98, CYAN), (91.68, 25.25, GREEN), (94.2, 26.95, AMBER), (79.73, 30.26, PINK),
                        (78.28, 14.81, AMBER), (70.21, 23.89, WHITE), (76.9, 33.6, "#e8f4ff"), (93.83, 27.55, GREEN)]:
        pin(S, lo, la, "", 0.3, color=col, size=1)
    S.text(0.5, 0.9, "WHICH ONE WOULD YOU VISIT FIRST?", S.c("Which one"), size=48, box=True, pop=True)
    S.text(0.5, 0.1, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=52, box=True, pop=True)
    S.fade_in_out(0, 1.5)
