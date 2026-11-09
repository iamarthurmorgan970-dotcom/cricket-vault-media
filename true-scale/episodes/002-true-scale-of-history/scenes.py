"""Scenes for this episode. Each function takes the Scene S; S.c("phrase") is when the narrator says it."""
from engine.core import *
from engine.timeline import *

# ------------------------------------------------------------------ scenes
PYR, CLEO, MOON = -2570, -69, 1969


def s01_hook(S):
    setup(S)
    tl = TL(S)
    tl.camera([(0, -300, 6300), (S.T, -300, 6100)])
    tl.marker(PYR, "GREAT PYRAMID", 0.5, sub="c. 2570 BC", color=GOLD)
    tl.marker(CLEO, "CLEOPATRA", 1.0, sub="born 69 BC", color=PINK, side=-1, h=0.3)
    tl.marker(MOON, "MOON LANDING", S.c("Moon landing"), sub="1969", color=CYAN)
    tl.bracket(PYR, CLEO, 0.62, "≈ 2,500 YEARS", S.c("Read that"), color=GOLD)
    tl.bracket(CLEO, MOON, 0.62, "≈ 2,000 YEARS", S.c("Read that") + 0.8, color=CYAN)
    S.headline("CLEOPATRA: CLOSER TO THE MOON LANDING", 0.4, S.c("Our brains"), size=40, y=0.08)
    S.headline("OUR BRAINS ARE TERRIBLE AT TIME", S.c("Our brains"), color=AMBER, y=0.08)
    S.fade_in_out(0.6, 0)


def s02_title(S):
    setup(S)
    S.text(0.5, 0.56, "THE TRUE SCALE", 0.3, size=96, pop=True)
    S.text(0.5, 0.43, "OF HISTORY", 0.7, size=96, color=AMBER, pop=True)
    S.text(0.5, 0.31, "Time is much stranger than you think", 1.2, size=30, color=MUTED, font=REG)
    S.text(0.5, 0.86, "TRUE SCALE", 0.0, size=28, color=CYAN)


def s02b_quiz(S):
    setup(S)
    S.text(0.5, 0.86, "QUICK QUIZ", 0.3, size=56, color=AMBER, pop=True)
    S.text(0.5, 0.62, "Closer to us today:", S.c("which is closer"), size=34, color=MUTED, font=REG)
    S.text(0.5, 0.53, "CLEOPATRA   or   THE GREAT PYRAMID ?", S.c("Cleopatra, or"), size=44)
    S.text(0.5, 0.36, "Closer in time to you:", S.c("And which"), size=34, color=MUTED, font=REG)
    S.text(0.5, 0.27, "T. REX   or   STEGOSAURUS ?", S.c("a T. rex"), size=44)
    S.caption("Hold on to your answers…", S.c("Hold on"), color=CYAN)


def s03_cleopatra(S):
    setup(S)
    tl = TL(S)
    t_moon = S.c("Now jump")
    S_cam = [(0, -1600, 2400), (S.c("Cleopatra was born"), -1350, 3200), (t_moon, -300, 5400),
             (S.c("By the time"), -1300, 3400), (S.c("And the Great"), -600, 6300)]
    tl.camera(S_cam)
    tl.marker(PYR, "GREAT PYRAMID", 0.4, sub="c. 2570 BC", color=GOLD)
    tl.marker(CLEO, "CLEOPATRA", S.c("Cleopatra was born"), sub="born 69 BC", color=PINK, side=-1, h=0.3)
    tl.bracket(PYR, CLEO, 0.62, "≈ 2,500 YEARS", S.c("That's a gap"), color=GOLD)
    tl.marker(MOON, "APOLLO 11", t_moon, sub="1969", color=CYAN, side=-1)
    tl.bracket(CLEO, MOON, 0.62, "≈ 2,000 YEARS", S.c("That's only"), color=CYAN)
    tl.marker(-430, "HERODOTUS", S.c("Herodotus"), sub="writing c. 430 BC", color=VIOLET, side=1, h=0.25, size=24)
    tl.span(PYR, 1240, -0.92, GOLD, "Great Pyramid: tallest structure on Earth for ≈ 3,800 years", S.c("And the Great"),
            dur=2.0)


def s04_mammoths(S):
    # part 1: the Arctic map; part 2: timeline
    def pac(a):
        b = a.copy()
        if b[:, 0].mean() < -20:
            b[:, 0] += 360
        return merc(b)
    S.graticule()
    S.world(proj=pac)
    S.camera([(0, 120, 95, 220), (S.c("Wrangel Island"), 178, 105, 120), (S.c("The last of them") - 0.4, 178, 105, 120)])
    wi = merc(np.array([[180.5, 71.3]]))[0]
    ring = Circle((wi[0], wi[1]), 4, fill=False, ec=AMBER, lw=4, zorder=20, alpha=0)
    S.ax.add_patch(ring)
    lab = S.ax.text(wi[0], wi[1] - 7, "WRANGEL ISLAND", fontproperties=BOLD, size=30, color=WHITE, ha="center",
                    va="top", zorder=21, alpha=0)
    tw = S.c("Wrangel Island")

    def up(t):
        a = ease((t - tw) / 0.5)
        ring.set_alpha(a)
        ring.set_radius(4 + 1.5 * math.sin(2 * math.pi * (t - tw) / 1.4))
        lab.set_alpha(a)
    S.updaters.append(up)
    S.headline("MAMMOTHS + PYRAMIDS?", 0.4, S.c("Most of them"))
    # timeline overlay on its own axes
    tax = S.fig.add_axes([0, 0, 1, 1])
    tax.set_axis_off()
    bg = Rectangle((0, 0), 1, 1, transform=tax.transAxes, color=OCEAN, zorder=0, alpha=0)
    tax.add_patch(bg)
    T2 = Scene.__new__(Scene)
    T2.__dict__.update(S.__dict__)
    T2.ax = tax
    tl = TL(T2)
    tax.set_xlim(-3300, -1300)
    t_tl = S.c("That's several")
    tl.marker(PYR, "GREAT PYRAMID", t_tl, sub="c. 2570 BC", color=GOLD)
    tl.span(-3300, -2000, -0.55, AMBER, "Last mammoths, Wrangel Island", t_tl + 0.6, dur=1.5)
    tl.marker(-2000, "LAST MAMMOTHS", t_tl + 1.8, sub="≈ 4,000 years ago", color=AMBER, side=-1, h=0.6)
    tl.bracket(PYR, -2000, 0.55, "SEVERAL CENTURIES", t_tl + 2.5, color=AMBER, size=30)

    def up2(t):
        a = ease((t - t_tl + 0.6) / 0.6)
        bg.set_alpha(a)
        tax.set_visible(a > 0)
    S.updaters.append(up2)
    S.brand()


def s05_oxford(S):
    setup(S)
    tl = TL(S)
    tl.camera([(0, 1300, 700), (S.c("And the Aztec Empire"), 1320, 560), (S.c("So Oxford"), 1550, 1050)])
    tl.span(1096, 2026, 0.35, CYAN, "University of Oxford: teaching by 1096", S.c("Teaching at"), dur=2.2)
    tl.marker(1325, "TENOCHTITLAN FOUNDED", S.c("The Aztec capital"), sub="1325", color=GREEN, side=-1, h=0.3)
    tl.bracket(1096, 1325, 0.62, "229 YEARS", S.c("That's more than"), color=AMBER, size=30, t1=S.c("So Oxford"))
    tl.span(1428, 1521, -0.88, PINK, "Aztec Empire 1428–1521", S.c("And the Aztec Empire"), dur=1.0)
    S.headline("OXFORD IS OLDER THAN THE AZTEC EMPIRE", S.c("So Oxford"), size=40)


def s05b_rome(S):
    setup(S)
    tl = TL(S)
    tl.camera([(0, 900, 1500), (S.c("By then"), 1440, 140), (S.T, 1450, 120)])
    tl.span(0, 476, 0.62, PINK, "Western Roman Empire, to 476", 0.6, dur=1.2, t1=S.c("By then") - 0.5)
    tl.span(476, 1453, 0.42, VIOLET, "Eastern Roman Empire to 1453", S.c("Its eastern half"), dur=2.0)
    tl.marker(1453, "CONSTANTINOPLE FALLS", S.c("until the city"), sub="1453", color=VIOLET, side=1, h=0.28, size=26)
    tl.marker(1450, "GUTENBERG PRINTING", S.c("Johannes Gutenberg"), sub="c. 1450", color=GOLD, side=-1, h=0.35, size=26)
    tl.marker(1492, "COLUMBUS SAILS", S.c("And just thirty-nine"), sub="1492", color=CYAN, side=-1, h=0.62, size=26)
    S.headline("ROME LASTED INTO THE AGE OF PRINTING", S.c("The Roman Empire lasted"), size=40)


def ma(x):
    return f"{-x:,.0f}M yrs ago" if x < -0.5 else "TODAY"


def s06_dinos(S):
    setup(S)
    tl = TL(S, fmt=ma, nice=[1, 2, 2.5, 5])
    tl.camera([(0, -100, 220), (S.T, -80, 190)])
    tl.span(-155, -145, 0.5, GREEN, "Stegosaurus", S.c("Stegosaurus lived"), dur=0.8, size=26)
    tl.span(-68, -66, 0.5, PINK, "T. rex", S.c("Tyrannosaurus"), dur=0.6, size=26)
    tl.marker(0, "YOU", S.c("from you"), color=CYAN, side=-1, h=0.3)
    tl.bracket(-150, -67, -0.62, "≈ 80 MILLION YEARS", S.c("That means"), color=GREEN, size=30, below=True)
    tl.bracket(-66, 0, -0.62, "66 MILLION YEARS", S.c("And only"), color=CYAN, size=30, below=True)
    S.headline("YOU'RE CLOSER TO T. REX THAN STEGOSAURUS WAS", S.c("You are closer"), size=36, color=PINK)
    S.headline("THE DINOSAURS DIDN'T ALL LIVE TOGETHER", 0.5, S.c("You are closer"), size=38)


def s07_sharks(S):
    setup(S)
    tl = TL(S, fmt=ma)
    tl.camera([(0, -180, 680), (S.T, -180, 660)])
    tl.span(-450, 0, 0.45, CYAN, "Shark-like fish (scales ≈ 450 million years old)", S.c("The earliest"), dur=2.0)
    tl.span(-385, 0, -0.6, GREEN, "Trees (from ≈ 385 million years ago)", S.c("The first trees"), dur=2.0)
    tl.bracket(-450, -385, 0.75, "60+ MILLION YEARS", S.c("So shark-like"), color=AMBER, size=28)
    S.caption("…of sharks swimming before the first tree", S.c("So shark-like") + 0.8, S.c("So shark-like") + 4.5, color=AMBER)
    S.headline("SHARKS ARE OLDER THAN TREES", S.c("So shark-like") + 4.6, size=44, y=0.08)


def s08_overlaps(S):
    setup(S)
    tl = TL(S)
    tl.camera([(0, 1850, 140), (S.c("The fax"), 1855, 110), (S.c("And Nintendo"), 1870, 100), (S.T, 1860, 120)])
    tl.span(1809, 1865, 0.62, AMBER, "Abraham Lincoln 1809–1865", S.c("Abraham Lincoln"), dur=1.2)
    tl.span(1809, 1882, 0.36, GREEN, "Charles Darwin 1809–1882", S.c("Charles Darwin"), dur=1.2)
    S.headline("BORN THE SAME DAY: 12 FEB 1809", S.c("the very same"), S.c("The fax"), size=40)
    tl.marker(1843, "FAX MACHINE", S.c("The fax"), sub="1843", color=CYAN, side=-1, h=0.3, size=26)
    tl.marker(1876, "TELEPHONE", S.c("more than thirty"), sub="1876", color=VIOLET, side=-1, h=0.3, size=26)
    tl.marker(1888, "JACK THE RIPPER", S.c("Jack the Ripper"), sub="1888", color=PINK, side=-1, h=0.62, size=24)
    tl.marker(1889, "NINTENDO FOUNDED", S.c("And Nintendo"), sub="1889", color="#ff4d4d", side=1, h=0.12, size=24)


def s09_modern(S):
    setup(S)
    tl = TL(S, fmt=lambda v: f"{v:.0f}" if abs(v - round(v)) < 1e-6 else "")
    t_wright = S.c("The Wright")
    tl.camera([(0, 1977.5, 1.6), (t_wright - 0.8, 1977.5, 1.6), (t_wright, 1940, 110), (S.T, 1940, 100)])
    tl.marker(1977 + 144 / 365, "STAR WARS", S.c("Star Wars"), sub="US release, May 1977", color=CYAN, side=-1, h=0.35, t1=t_wright)
    tl.marker(1977 + 252 / 365, "LAST GUILLOTINE", S.c("France carried"), sub="10 Sep 1977", color=PINK, side=1, h=0.3,
              t1=t_wright)
    tl.marker(1903.96, "FIRST FLIGHT", t_wright, sub="1903", color=GOLD, side=1, h=0.3)
    tl.marker(1969.55, "MOON LANDING", S.c("Just sixty-six"), sub="1969", color=CYAN, side=1, h=0.3)
    tl.bracket(1903.96, 1969.55, -0.55, "66 YEARS", S.c("Just sixty-six") + 0.5, color=AMBER, below=True)
    tl.span(1900, 1985, -0.85, VIOLET, "One lifetime", S.c("Someone could"), dur=1.5)
    S.headline("1977: STAR WARS AND THE GUILLOTINE", S.c("By then"), t_wright, size=40)


def s10_pension(S):
    setup(S)
    tl = TL(S)
    tl.camera([(0, 1880, 160), (S.c("It went to"), 1935, 210), (S.T, 1935, 200)])
    tl.span(1861, 1865, 0.62, PINK, "Civil War 1861–65", 0.5, dur=0.8, size=24)
    tl.span(1846, 1938, 0.32, AMBER, "Mose Triplett (fought in the war)", S.c("Her father"), dur=1.5, size=24)
    tl.span(1930, 2020, -0.55, CYAN, "Irene Triplett 1930–2020", S.c("was eighty-three"), dur=1.5, size=24)
    tl.span(1938, 2020, -0.85, GREEN, "Civil War pension paid: $73.13 / month", S.c("She received"), dur=1.5, size=24)
    tl.marker(2020.4, "LAST PAYMENT", S.c("until she died"), sub="2020", color=GREEN, side=1, h=0.25, size=26)
    S.headline("A CIVIL WAR PENSION, PAID UNTIL 2020", S.c("Yet the United"), S.c("It went to"), size=40)


def s11_numbers(S):
    setup(S)
    NOW = 2026.0

    def f(v):
        if v > NOW + 0.002:
            return ""
        if v > NOW - 0.2:
            d = (NOW - v) * 365
            return f"{d:.0f} days ago" if d > 0.5 else "NOW"
        return yr(v)
    tl = TL(S, fmt=f)
    t_b, t_t = S.c("A billion seconds"), S.c("And a trillion")
    tl.camera([(0, NOW - 0.035, 0.08), (t_b - 0.2, NOW - 0.035, 0.08), (t_b + 1.5, NOW - 20, 44),
               (t_t - 0.3, NOW - 20, 44), (t_t + 1.5, NOW - 15000, 46000), (S.T, NOW - 15000, 46000)])
    tl.marker(NOW - 11.57 / 365, "1 MILLION SECONDS", S.c("A million seconds"), sub="≈ 11.5 days", color=CYAN, t1=t_b + 0.2)
    tl.marker(NOW - 31.7, "1 BILLION SECONDS", t_b + 1.4, sub="≈ 31.7 years: the mid-1990s", color=AMBER, t1=t_t + 0.5)
    tl.marker(NOW - 31710, "1 TRILLION SECONDS", t_t + 1.6, sub="≈ 31,700 years: the Ice Age", color=PINK)
    S.headline("BIG NUMBERS, TURNED INTO TIME", 0.4, size=42)


MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
CUM = np.cumsum([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])


def day_fmt(v):
    m = int(np.searchsorted(CUM, v, side="right") - 1)
    m = min(max(m, 0), 11)
    d = int(v - CUM[m]) + 1
    return f"{d} {MONTHS[m]}" if d != 1 else MONTHS[m]


def s12_calendar(S):
    setup(S)
    tl = TL(S, fmt=day_fmt, nice=[1, 2, 5, 3])
    t_dino = S.c("The dinosaurs")
    tl.camera([(0, 178, 440), (t_dino - 0.6, 178, 440), (t_dino + 0.6, 350, 40), (S.T, 351, 34)])
    tl.marker(0.02, "BIG BANG", S.c("The Big Bang"), sub="1 Jan, 00:00", color=WHITE, side=1)
    tl.marker(244.9, "EARTH FORMS", S.c("The Earth"), sub="early September", color=CYAN, side=1)
    tl.marker(267.1, "FIRST LIFE", S.c("The first signs"), sub="late September", color=GREEN, side=-1)
    tl.marker(358.9, "DINOSAURS", t_dino + 0.5, sub="25 Dec", color=AMBER, side=1)
    tl.marker(363.25, "WIPED OUT", S.c("wiped out"), sub="30 Dec", color=PINK, side=-1)
    S.headline("13.8 BILLION YEARS IN ONE CALENDAR YEAR", S.c("Take the entire"), size=40)
    S.caption("1 day ≈ 38 million years", S.c("Each day"), color=AMBER)


def hms(v):
    """v = seconds before midnight (negative)."""
    s = 86400 + v
    h, m, sec = int(s // 3600), int(s % 3600 // 60), s % 60
    return f"{h:02d}:{m:02d}:{sec:02.0f}" if h < 24 else "MIDNIGHT"


def s13_lastday(S):
    setup(S)
    tl = TL(S, fmt=hms, nice=[1, 2, 5, 3, 6])
    t_h, t_p, t_c = S.c("Our own species"), S.c("The Great Pyramid"), S.c("And Columbus")
    tl.camera([(0, -43200, 86400), (t_h - 0.3, -600, 1300), (t_p - 0.5, -600, 1300), (t_p + 0.8, -6, 14),
               (S.T, -6, 13)])
    tl.marker(-685.6, "HOMO SAPIENS", t_h, sub="23:48:34", color=CYAN, side=1, t1=t_p)
    tl.marker(-10.5, "GREAT PYRAMID", t_p + 0.6, sub="10.5 s to midnight", color=GOLD, side=1)
    tl.marker(-4.6, "1 AD", S.c("Every empire") + 0.5, sub="4.6 s", color=VIOLET, side=-1, h=0.3, size=24)
    tl.marker(-1.22, "COLUMBUS", t_c, sub="1.2 s", color=PINK, side=-1, h=0.62)
    tl.marker(-0.001, "TODAY", t_c + 1.2, color=WHITE, side=1, h=0.25, size=26)
    tl.span(-10.5, 0, 0.0 - 0.15, AMBER, "", S.c("Every empire"), dur=1.0, h=0.06)
    S.headline("31 DECEMBER: THE LAST DAY", 0.3, t_h, size=42)
    S.headline("ALL OF RECORDED HISTORY: THE LAST ≈ 10 SECONDS", S.c("Every empire"), size=36, color=AMBER, y=0.08)


def s14_outro(S):
    setup(S)
    S.text(0.5, 0.80, "Cleopatra is closer to us than to the pyramids", S.c("Cleopatra is closer"), S.c("If this"),
           size=36, color=PINK, box=True)
    S.text(0.5, 0.66, "You're closer to T. rex than T. rex was to Stegosaurus", S.c("You are closer"), S.c("If this"),
           size=36, color=GREEN, box=True)
    S.text(0.5, 0.52, "All of human history: the last seconds of the cosmic year", S.c("And all of human"),
           S.c("If this"), size=36, color=AMBER, box=True)
    S.text(0.5, 0.5, "SUBSCRIBE TO TRUE SCALE", S.c("subscribe"), size=64, box=True, pop=True)
    S.text(0.5, 0.36, "Which fact surprised you most? Tell me in the comments", S.c("tell me"), size=30, color=WHITE,
           font=REG, box=True)
    S.fade_in_out(0, 1.5)


def s03b_greek(S):
    setup(S)
    tl = TL(S)
    tl.camera([(0, -185, 540), (S.T, -180, 520)])
    tl.marker(-332, "ALEXANDER CONQUERS EGYPT", S.c("Alexander the Great"), sub="332 BC", color=CYAN, side=1, size=28)
    tl.span(-305, -30, -0.6, VIOLET, "Ptolemaic dynasty (Greek-speaking Macedonians)", S.c("Her family, the"), dur=1.6)
    tl.marker(-51, "CLEOPATRA BECOMES QUEEN", S.c("in fifty-one"), sub="51 BC", color=PINK, side=1, h=0.25, size=26)
    tl.bracket(-332, -51, 0.75, "≈ 280 YEARS OF GREEK RULE", S.c("Greek rulers had"), color=AMBER, size=28)
    S.headline("CLEOPATRA WASN'T EGYPTIAN BY DESCENT", 0.5, S.c("They took over"), size=40, y=0.08)
    S.headline("EVEN EGYPT'S LAST DYNASTY WAS FOREIGN", S.c("Ancient Egypt was so"), size=40, color=AMBER, y=0.08)


def s08b_annefrank(S):
    setup(S)
    tl = TL(S)
    tl.camera([(0, 1945, 70), (S.T, 1950, 64)])
    tl.marker(1929.45, "ANNE FRANK", S.c("Anne Frank and"), sub="born 1929", color=AMBER, side=1, h=0.3)
    tl.marker(1929.04, "MARTIN LUTHER KING JR.", S.c("Martin Luther"), sub="born 1929", color=CYAN, side=-1, h=0.3)
    tl.span(1939.67, 1945.6, 0.52, PINK, "Second World War", S.c("Second World War"), dur=1.0, size=24)
    tl.span(1954, 1968, -0.78, GREEN, "Civil rights movement", S.c("civil rights"), dur=1.0, size=24)
    tl.marker(1963.66, "\"I HAVE A DREAM\"", S.c("I Have a Dream") - 1.2, sub="1963", color=GREEN, side=1, h=0.3, size=26)
    tl.bracket(1929.45, 1963.66, 0.8, "SHE'D HAVE BEEN 34", S.c("thirty-four"), color=AMBER, size=30)
    S.headline("SAME BIRTH YEAR: 1929", S.c("both born"), S.c("We remember"), size=44, y=0.08)
