"""013 Every Indian State Compared to a Country. Each function takes the Scene S; S.c("phrase") is when it is said.
State areas: MoSPI (via StatisticsTimes). Country areas: Encyclopaedia Britannica (total area). Shapes: Natural Earth
(India's official boundary for India). Countries are moved on the sphere without stretching, so sizes on screen are true."""
from engine.core import *
from engine.india import *
from shapely.geometry import Polygon as SPoly
from shapely.ops import unary_union

# areas in km² exactly as listed by the sources
SA = {"Rajasthan": 342239, "Madhya Pradesh": 308252, "Maharashtra": 307713, "Uttar Pradesh": 240928,
      "Gujarat": 196244, "Karnataka": 191791, "Andhra Pradesh": 162970, "Odisha": 155707, "Chhattisgarh": 135192,
      "Tamil Nadu": 130060, "Telangana": 112077, "Bihar": 94163, "West Bengal": 88752, "Arunachal Pradesh": 83743,
      "Jharkhand": 79716, "Assam": 78438, "Himachal Pradesh": 55673, "Uttarakhand": 53483, "Punjab": 50362,
      "Haryana": 44212, "Kerala": 38852, "Meghalaya": 22429, "Manipur": 22327, "Mizoram": 21081, "Nagaland": 16579,
      "Tripura": 10486, "Sikkim": 7096, "Goa": 3702}
CA = {"Republic of the Congo": 342000, "Germany": 357596, "Finland": 338485, "Oman": 309500, "Italy": 302069,
      "United Kingdom": 242500, "Uganda": 241553, "Ghana": 238533, "Romania": 238397, "Senegal": 196712,
      "Uruguay": 193356, "Syria": 185180, "Tunisia": 163610, "Bangladesh": 147570, "Nepal": 147181,
      "Greece": 132049, "Nicaragua": 130373, "Honduras": 112492, "Bulgaria": 110372, "Cuba": 109884,
      "Hungary": 93023, "Portugal": 92225, "Jordan": 88794, "Austria": 83884, "Czechia": 78870,
      "Republic of Serbia": 77589, "Croatia": 56594, "Bosnia and Herzegovina": 51209, "Costa Rica": 51100,
      "Denmark": 42954, "Estonia": 45339, "Bhutan": 38394, "Netherlands": 36337, "Israel": 22072,
      "Slovenia": 20271, "Kuwait": 17818, "Lebanon": 10452, "Brunei": 5765, "Cyprus": 9251, "Luxembourg": 2586}
SHOW = {"Republic of the Congo": "REP. OF THE CONGO", "Republic of Serbia": "SERBIA",
        "Bosnia and Herzegovina": "BOSNIA & HERZ."}
CARD = {"Republic of the Congo": "Rep. of the Congo", "Republic of Serbia": "Serbia",
        "Bosnia and Herzegovina": "Bosnia & Herz."}
IND_FULL = (82.0, 23.4, 64.0)
NE_COUNTRY = {"Cyprus": ["Cyprus", "Northern Cyprus"]}       # Britannica's figure is the whole island


def crings(name):
    return [r for n in NE_COUNTRY.get(name, [name]) for r in COUNTRIES[n]]


def centroid(rings):
    g = unary_union([SPoly(r).buffer(0) for r in rings])
    return (g.centroid.x, g.centroid.y)


def view(state, k=2.6, wmin=6.0, dx=0.0, dy=0.0):
    a = np.vstack(ST[state])
    lon0, lon1 = a[:, 0].min(), a[:, 0].max()
    y0, y1 = mercy(a[:, 1].min()), mercy(a[:, 1].max())
    w = max(lon1 - lon0, (y1 - y0) * W / H, wmin / k) * k
    return ((lon0 + lon1) / 2 + dx * w, (y0 + y1) / 2 + dy * w * H / W, w)


def base(S, keys):
    india(S, keys)


def hl(S, state, t0, t1=None, color=AMBER, peak=0.75):
    S.highlight(ST[state], color, t0, t1, peak=peak, lw=1.5)


def twin(S, country, state, t0, color=CYAN, t_hide=None, dur=2.2, label=True, lab=None):
    rings = crings(country)
    S.mover(rings, centroid(rings), centroid(ST[state]), t0, t0 + dur, color=color, ghost=False,
            label=(lab or SHOW.get(country, country.upper())) if label else None, t_hide=t_hide, appear=t0 - 0.3)


def cmp(S, state, country, t0, t1=None, ccol=CYAN, y=0.155, diff=True):
    a, b = SA[state], CA[country]
    name = CARD.get(country, country)
    S.text(0.5, y, f"{state}  {a:,} km²      {name}  {b:,} km²", t0, t1, size=32, box=True)
    if diff:
        d = abs(a - b)
        pct = d / min(a, b) * 100
        S.text(0.5, y - 0.075, f"difference {d:,} km²  ({pct:.1f}%)", t0 + 0.6, t1, size=28, color=GREEN, box=True)


def title(S, s, t0=0.3, t1=None, color=AMBER):
    S.text(0.04, 0.92, s, t0, t1, size=34, color=color, ha="left", box=True)


def note(S, s, t0=0.5, t1=None):
    S.text(0.015, 0.025, s, t0, t1, size=17, color=MUTED, ha="left", font=REG)


def pan(S, va, vb, t_move, t_end=None):
    t_end = S.T if t_end is None else t_end
    return [(0, *va), (max(t_move - 1.0, 0.01), *va), (t_move + 0.6, *vb), (t_end, *vb)]


# ------------------------------------------------------------------ scenes
def s01_hook(S):
    v = view("Uttar Pradesh", k=2.4)
    base(S, [(0, *INDIA_VIEW), (1.2, *v), (S.T, v[0], v[1], v[2] * 0.95)])
    hl(S, "Uttar Pradesh", 0.6)
    title(S, "UTTAR PRADESH", 0.8)
    twin(S, "United Kingdom", "Uttar Pradesh", S.c("Slide Britain"))
    cmp(S, "Uttar Pradesh", "United Kingdom", S.c("about two hundred"))
    S.headline("LESS THAN 1% APART", S.c("The difference"), y=0.82, color=GREEN)
    note(S, "Areas: MoSPI (states), Britannica (countries). Shapes: Natural Earth.")
    S.fade_in_out(0.4, 0.4)


ORDER = sorted(SA, key=lambda s: -SA[s])
CYC = [AMBER, CYAN, PINK, GREEN, VIOLET]


def s02_promise(S):
    base(S, [(0, *IND_FULL), (S.T, IND_FULL[0], IND_FULL[1], IND_FULL[2] * 0.97)])
    t_a = S.c("twenty eight states")
    t_b = S.c("a nation of almost")
    for i, st in enumerate(ORDER):
        hl(S, st, t_a + (t_b - t_a + 1.5) * i / len(ORDER), color=CYC[i % 5], peak=0.7)
    S.text(0.14, 0.62, "28 STATES", t_a - 0.3, size=40, box=True, pop=True)
    S.text(0.14, 0.48, "28 COUNTRY\nTWINS", S.c("a nation of almost"), size=40, color=CYAN, box=True, pop=True)
    S.text(0.865, 0.5, "biggest to smallest\ntrue size\nclosest at the end", S.c("from the biggest"), size=28,
           box=True)


UTS = ["Jammu and Kashmir", "Ladakh", "Delhi", "Chandigarh", "Puducherry", "Andaman and Nicobar", "Lakshadweep",
       "Dadra and Nagar Haveli and Daman and Diu"]


def s03_rules(S):
    base(S, [(0, *IND_FULL), (S.T, IND_FULL[0], IND_FULL[1], IND_FULL[2] * 0.97)])
    S.text(0.14, 0.62, "INDIA", S.c("India covers"), size=40, color=MUTED, box=True)
    S.text(0.14, 0.53, "3,287,469 km²", S.c("India covers"), size=46, color=AMBER, box=True, pop=True)
    S.text(0.14, 0.40, "States: MoSPI (Govt of India)", S.c("State areas"), size=24, box=True)
    S.text(0.14, 0.33, "Countries: Britannica", S.c("country areas"), size=24, box=True)
    t_u = S.c("Union territories")
    for u in UTS:
        S.highlight(ST[u], MUTED, t_u, peak=0.85, lw=1.2)
    S.text(0.865, 0.62, "Union territories:\nnot included", t_u, size=28, color=MUTED, box=True)
    S.text(0.865, 0.3, "Countries moved\nwithout stretching:\ntrue size", S.c("Every country"), size=26,
           color=CYAN, box=True)


def s04_rajasthan(S):
    v = view("Rajasthan", k=2.3)
    base(S, [(0, *INDIA_VIEW), (1.0, *v), (S.T, v[0], v[1], v[2] * 0.97)])
    hl(S, "Rajasthan", 0.6)
    title(S, "#1  RAJASTHAN", 0.6)
    t1, t2, t3 = S.c("Republic of the Congo"), S.c("try Germany"), S.c("Finland")
    twin(S, "Republic of the Congo", "Rajasthan", t1, color=GREEN, t_hide=t2 - 0.3)
    cmp(S, "Rajasthan", "Republic of the Congo", t1 + 1.5, t2 - 0.3, ccol=GREEN)
    twin(S, "Germany", "Rajasthan", t2, color=CYAN, t_hide=t3 - 0.2)
    S.text(0.5, 0.155, f"Germany  {CA['Germany']:,} km²   ·   about 4.5% bigger", S.c("only about four"), t3 - 0.2,
           size=32, box=True)
    twin(S, "Finland", "Rajasthan", t3, color=PINK, dur=1.8)
    S.text(0.5, 0.155, f"Finland  {CA['Finland']:,} km²   ·   1.1% smaller", t3 + 1.0, size=32, box=True)


def s05_mp_maha(S):
    va, vb = view("Madhya Pradesh", k=2.2), view("Maharashtra", k=2.4)
    tb = S.c("Maharashtra is just")
    base(S, pan(S, va, vb, tb))
    hl(S, "Madhya Pradesh", 0.4, tb + 0.2)
    title(S, "#2  MADHYA PRADESH", 0.4, tb)
    twin(S, "Oman", "Madhya Pradesh", S.c("matches Oman"), color=CYAN, t_hide=tb + 0.2)
    cmp(S, "Madhya Pradesh", "Oman", S.c("matches Oman") + 1.6, tb)
    hl(S, "Maharashtra", tb)
    title(S, "#3  MAHARASHTRA", tb + 0.3)
    twin(S, "Italy", "Maharashtra", S.c("its twin is Italy"), color=PINK)
    cmp(S, "Maharashtra", "Italy", S.c("onto Maharashtra"))


def s06_up(S):
    v = view("Uttar Pradesh", k=2.6, dx=0.2)
    base(S, [(0, *v), (S.T, v[0], v[1], v[2] * 0.96)])
    hl(S, "Uttar Pradesh", 0.2)
    title(S, "#4  UTTAR PRADESH", 0.3)
    twin(S, "United Kingdom", "Uttar Pradesh", 0.6, dur=1.6)
    t = S.c("Uganda is listed")
    rows = [("Uttar Pradesh", SA["Uttar Pradesh"] / 1000, AMBER, 1.2),
            ("United Kingdom", CA["United Kingdom"] / 1000, CYAN, S.c("fifteen hundred")),
            ("Uganda", CA["Uganda"] / 1000, GREEN, t),
            ("Ghana", CA["Ghana"] / 1000, PINK, S.c("Ghana and Romania")),
            ("Romania", CA["Romania"] / 1000, VIOLET, S.c("Ghana and Romania") + 0.5)]
    S.bars(rows, 1.0, rect=(0.62, 0.07, 0.3, 0.56), xmax=300, unit="k km²", label_left=False, dec=1,
           title="Total area, thousand km²")
    S.headline("FOUR COUNTRIES WITHIN ABOUT 1%", S.c("Four countries"), y=0.82, color=GREEN)


def pair_scene(S, a, ca, b, cb, phrase_a, phrase_b, cue_b, na, nb, card_a=None, card_b=None, ka=2.4, kb=2.4,
               col_a=CYAN, col_b=PINK):
    va, vb = view(a, k=ka), view(b, k=kb)
    tb = S.c(cue_b)
    base(S, [(0, *INDIA_VIEW), (0.9, *va)] + pan(S, va, vb, tb)[1:])
    hl(S, a, 0.5, tb + 0.2)
    title(S, f"#{na}  {a.upper()}", 0.5, tb)
    ta = S.c(phrase_a)
    twin(S, ca, a, ta, color=col_a, t_hide=tb + 0.2)
    cmp(S, a, ca, card_a if card_a is not None else ta + 1.8, tb)
    hl(S, b, tb)
    title(S, f"#{nb}  {b.upper()}", tb + 0.3)
    t2 = S.c(phrase_b)
    twin(S, cb, b, t2, color=col_b)
    cmp(S, b, cb, card_b if card_b is not None else t2 + 1.8)


def s07_guj_kar(S):
    pair_scene(S, "Gujarat", "Senegal", "Karnataka", "Uruguay", "lines up with Senegal", "twin is Uruguay",
               "Just behind it", 5, 6)
    S.text(0.5, 0.78, f"Syria  {CA['Syria']:,} km²: a little smaller than both", S.c("Syria is"), size=28,
           color=MUTED, box=True)


def s08_ap_odisha(S):
    va, vb = view("Andhra Pradesh", k=2.3), view("Odisha", k=2.6)
    tb = S.c("Odisha, at about")
    base(S, [(0, *INDIA_VIEW), (0.9, *va)] + pan(S, va, vb, tb)[1:])
    hl(S, "Andhra Pradesh", 0.5, tb + 0.2)
    hl(S, "Telangana", S.c("Telangana was carved"), S.c("That makes it"), color=MUTED, peak=0.6)
    S.text(0.5, 0.78, "Telangana carved out", S.c("Telangana was carved"), S.c("That makes it"), size=28,
           color=MUTED, box=True)
    title(S, "#7  ANDHRA PRADESH", 0.5, tb)
    ta = S.c("twin of Tunisia")
    twin(S, "Tunisia", "Andhra Pradesh", ta, color=CYAN, t_hide=tb + 0.2)
    cmp(S, "Andhra Pradesh", "Tunisia", ta + 1.6, tb)
    hl(S, "Odisha", tb)
    title(S, "#8  ODISHA", tb + 0.3)
    t2 = S.c("larger than Bangladesh")
    twin(S, "Bangladesh", "Odisha", t2 - 0.8, color=GREEN, lab="BANGLADESH")
    cmp(S, "Odisha", "Bangladesh", t2 + 0.6)
    S.text(0.5, 0.78, f"Nepal  {CA['Nepal']:,} km²: also smaller", S.c("larger than Nepal"), size=28,
           color=MUTED, box=True)


def s09_chh_tn(S):
    pair_scene(S, "Chhattisgarh", "Greece", "Tamil Nadu", "Nicaragua", "match for Greece", "Nicaragua in Central",
               "And Tamil Nadu", 9, 10)


def s10_tel_bihar(S):
    pair_scene(S, "Telangana", "Honduras", "Bihar", "Hungary", "Its twin is Honduras", "matches Hungary",
               "Bihar, about", 11, 12, kb=2.6)
    S.text(0.5, 0.78, f"Bulgaria {CA['Bulgaria']:,}  ·  Cuba {CA['Cuba']:,} km²", S.c("Bulgaria and Cuba"),
           S.c("Bihar, about"), size=28, color=MUTED, box=True)
    S.text(0.5, 0.78, f"Portugal  {CA['Portugal']:,} km²", S.c("Portugal is close"), size=28, color=MUTED, box=True)


def s11_wb_arun(S):
    va, vb = view("West Bengal", k=2.2), view("Arunachal Pradesh", k=2.4)
    tb = S.c("And at the other end")
    base(S, [(0, *INDIA_VIEW), (0.9, *va)] + pan(S, va, vb, tb)[1:])
    hl(S, "West Bengal", 0.5, tb + 0.2)
    title(S, "#13  WEST BENGAL", 0.5, tb)
    ta = S.c("Jordan covers")
    twin(S, "Jordan", "West Bengal", ta - 1.2, color=CYAN, t_hide=tb + 0.2)
    S.text(0.5, 0.155, f"West Bengal  {SA['West Bengal']:,} km²", S.c("West Bengal covers"), tb, size=36, box=True,
           color=AMBER)
    S.text(0.5, 0.08, f"Jordan  {CA['Jordan']:,} km²", ta, tb, size=36, box=True, color=CYAN)
    S.headline("ONLY 42 km² APART", S.c("a difference of forty"), tb, y=0.82, color=GREEN)
    hl(S, "Arunachal Pradesh", tb)
    title(S, "#14  ARUNACHAL PRADESH", tb + 0.3)
    t2 = S.c("twin of Austria")
    twin(S, "Austria", "Arunachal Pradesh", t2, color=PINK)
    cmp(S, "Arunachal Pradesh", "Austria", t2 + 1.6)


def s12_jh_assam(S):
    pair_scene(S, "Jharkhand", "Czechia", "Assam", "Republic of Serbia", "pairs with Czechia", "pairs with Serbia",
               "Assam, on", 15, 16)


def s13_hills_punjab(S):
    v = view("Himachal Pradesh", k=3.4, dy=-0.05)
    base(S, [(0, *INDIA_VIEW), (1.0, *v), (S.T, v[0], v[1], v[2] * 0.97)])
    a, b, c = S.c("matches Croatia"), S.c("Uttarakhand, about"), S.c("And Punjab")
    hl(S, "Himachal Pradesh", 0.6, b)
    title(S, "#17  HIMACHAL PRADESH", 0.6, b)
    twin(S, "Croatia", "Himachal Pradesh", a, color=CYAN, t_hide=b)
    cmp(S, "Himachal Pradesh", "Croatia", a + 1.6, b)
    hl(S, "Uttarakhand", b, c)
    title(S, "#18  UTTARAKHAND", b + 0.2, c)
    twin(S, "Bosnia and Herzegovina", "Uttarakhand", b + 0.6, color=GREEN, t_hide=c)
    cmp(S, "Uttarakhand", "Bosnia and Herzegovina", b + 2.0, c)
    hl(S, "Punjab", c)
    title(S, "#19  PUNJAB", c + 0.2)
    twin(S, "Costa Rica", "Punjab", S.c("twin of Costa Rica"), color=PINK)
    cmp(S, "Punjab", "Costa Rica", S.c("twin of Costa Rica") + 1.6)


def s14_har_kerala(S):
    va, vb = view("Haryana", k=3.0), view("Kerala", k=2.8)
    tb = S.c("Then comes Kerala")
    base(S, [(0, *INDIA_VIEW), (0.9, *va)] + pan(S, va, vb, tb + 1.0)[1:])
    hl(S, "Haryana", 0.5, tb + 0.2)
    title(S, "#20  HARYANA", 0.5, tb)
    td = S.c("bigger than Denmark")
    twin(S, "Denmark", "Haryana", td - 0.8, color=CYAN, t_hide=tb + 0.2)
    S.text(0.5, 0.155, f"Denmark {CA['Denmark']:,}  <  Haryana {SA['Haryana']:,}  <  Estonia {CA['Estonia']:,} km²",
           td, tb, size=30, box=True)
    hl(S, "Kerala", tb)
    title(S, "#21  KERALA", tb + 0.3)
    t2 = S.c("Bhutan, only")
    twin(S, "Bhutan", "Kerala", t2 - 0.8, color=PINK, t_hide=S.c("Kerala is also"))
    cmp(S, "Kerala", "Bhutan", t2 + 0.6, S.c("Kerala is also"))
    twin(S, "Netherlands", "Kerala", S.c("Kerala is also"), color=VIOLET, dur=1.6)
    S.text(0.5, 0.155, f"Netherlands  {CA['Netherlands']:,} km²: smaller than Kerala", S.c("Kerala is also") + 1.2,
           size=30, box=True)


def s15_northeast(S):
    v = (91.5, mercy(24.6), 14.0)
    base(S, [(0, *INDIA_VIEW), (1.0, *v), (S.T, v[0], v[1], v[2] * 0.96)])
    title(S, "#22-26  THE NORTHEAST", 0.6)
    t_m = S.c("both are twins of Israel")
    t_z, t_n, t_t = S.c("Mizoram is"), S.c("Nagaland is"), S.c("And then there")
    hl(S, "Meghalaya", S.c("Meghalaya and Manipur"), t_z)
    hl(S, "Manipur", S.c("Meghalaya and Manipur"), t_z, color=PINK)
    twin(S, "Israel", "Meghalaya", t_m - 0.6, color=CYAN, t_hide=t_z, dur=1.8)
    twin(S, "Israel", "Manipur", t_m - 0.2, color=GREEN, t_hide=t_z, dur=1.8, lab="ISRAEL")
    S.text(0.22, 0.42, f"Meghalaya {SA['Meghalaya']:,}\nManipur {SA['Manipur']:,}\nIsrael {CA['Israel']:,} km²",
           t_m, t_z, size=28, box=True)
    hl(S, "Mizoram", t_z, t_n)
    twin(S, "Slovenia", "Mizoram", t_z + 0.2, color=PINK, t_hide=t_n, dur=1.6)
    S.text(0.22, 0.42, f"Mizoram {SA['Mizoram']:,}  >  Slovenia {CA['Slovenia']:,} km²", t_z + 1.2, t_n, size=28,
           box=True)
    hl(S, "Nagaland", t_n, t_t)
    twin(S, "Kuwait", "Nagaland", t_n + 0.2, color=GREEN, t_hide=t_t, dur=1.6)
    S.text(0.22, 0.42, f"Nagaland {SA['Nagaland']:,}  <  Kuwait {CA['Kuwait']:,} km²", t_n + 1.2, t_t, size=28,
           box=True)
    hl(S, "Tripura", t_t)
    twin(S, "Lebanon", "Tripura", S.c("Lebanon:") - 0.6, color=CYAN, dur=1.8)
    S.text(0.22, 0.42, f"Tripura  {SA['Tripura']:,} km²", S.c("Tripura:"), size=36, box=True, color=AMBER)
    S.text(0.22, 0.34, f"Lebanon  {CA['Lebanon']:,} km²", S.c("Lebanon:"), size=36, box=True, color=CYAN)
    S.headline("ONLY 34 km² APART: THE CLOSEST TWIN", S.c("A gap of just"), y=0.82, color=GREEN)


def s16_small(S):
    va, vb = view("Sikkim", k=3.2, wmin=6), view("Goa", k=3.2, wmin=5)
    tb = S.c("And Goa")
    base(S, [(0, *INDIA_VIEW), (0.9, *va)] + pan(S, va, vb, tb)[1:])
    hl(S, "Sikkim", 0.5, tb + 0.2)
    title(S, "#27  SIKKIM", 0.5, tb)
    t1, t2 = S.c("bigger than Brunei"), S.c("smaller than the island")
    twin(S, "Brunei", "Sikkim", t1 - 0.6, color=CYAN, t_hide=t2, dur=1.6)
    twin(S, "Cyprus", "Sikkim", t2, color=PINK, t_hide=tb + 0.2, dur=1.6, lab="CYPRUS (island)")
    S.text(0.5, 0.155, f"Brunei {CA['Brunei']:,}  <  Sikkim {SA['Sikkim']:,}  <  Cyprus {CA['Cyprus']:,} km²", t1, tb,
           size=30, box=True)
    hl(S, "Goa", tb)
    title(S, "#28  GOA", tb + 0.3)
    t3 = S.c("size of Luxembourg")
    twin(S, "Luxembourg", "Goa", t3 - 1.4, color=GREEN)
    S.text(0.5, 0.155, f"Goa {SA['Goa']:,} km²  =  about 1.4 × Luxembourg ({CA['Luxembourg']:,} km²)", t3 - 0.4,
           size=30, box=True)


def s17_closest(S):
    base(S, [(0, *IND_FULL), (S.T, *IND_FULL)])
    S.ax.add_patch(Rectangle((0, 0), 1, 1, transform=S.ax.transAxes, color=OCEAN, alpha=0.6, zorder=20))
    S.headline("THE CLOSEST TWINS", 0.3, y=0.9, color=AMBER)
    rows = [("Tamil Nadu · Nicaragua", 313, VIOLET, S.c("In sixth place")),
            ("Manipur · Israel", 255, PINK, S.c("Fifth")),
            ("Rajasthan · Rep. of the Congo", 239, GREEN, S.c("Fourth")),
            ("Arunachal Pradesh · Austria", 141, CYAN, S.c("Third")),
            ("West Bengal · Jordan", 42, AMBER, S.c("Second")),
            ("Tripura · Lebanon", 34, GREEN, S.c("And the winner"))]
    S.bars(rows, 0.5, rect=(0.40, 0.14, 0.46, 0.62), xmax=420, unit="km² apart", label_left=True, dec=0,
           title="Difference in area")


def s18_meaning(S):
    base(S, [(0, *INDIA_VIEW), (S.c("In reality") - 0.5, *INDIA_VIEW), (S.c("Rajasthan alone"), 48, mercy(32), 125),
             (S.T, 48, mercy(32), 120)])
    t = S.c("In reality")
    for i, st in enumerate(ORDER):
        hl(S, st, t + 0.05 * i, color=CYC[i % 5], peak=0.6)
    S.text(0.5, 0.85, "European-sized  ·  African-sized  ·  Central American-sized", S.c("the size of European"),
           S.c("Area is only"), size=30, box=True)
    S.highlight(["Germany"], CYAN, S.c("Rajasthan alone"), S.c("Area is only"), peak=0.8)
    S.highlight(ST["Rajasthan"], AMBER, S.c("Rajasthan alone"), S.c("Area is only"), peak=0.95, z=6)
    S.text(0.5, 0.15, f"Rajasthan {SA['Rajasthan']:,} km²   ·   Germany {CA['Germany']:,} km²", S.c("Rajasthan alone"),
           S.c("Area is only"), size=30, box=True)
    S.highlight(["United Kingdom"], CYAN, S.c("Area is only"), peak=0.8)
    S.highlight(ST["Uttar Pradesh"], AMBER, S.c("Area is only"), peak=0.95, z=6)
    S.text(0.5, 0.15, "Same size. Population? Another video.", S.c("how many people"), size=32, box=True,
           color=GREEN)


def s19_outro(S):
    base(S, [(0, *IND_FULL), (S.T, IND_FULL[0], IND_FULL[1], IND_FULL[2] * 0.97)])
    for i, st in enumerate(ORDER):
        hl(S, st, 0.2 + 0.04 * i, color=CYC[i % 5], peak=0.55)
    S.text(0.14, 0.6, "WHICH TWIN\nSURPRISED\nYOU?", 0.4, size=40, box=True, pop=True)
    S.text(0.865, 0.62, "Your state\n+ its country twin\nin the comments", S.c("Tell me your state"), size=28,
           box=True, color=CYAN)
    S.text(0.865, 0.25, "SUBSCRIBE\nTO TRUE SCALE", S.c("subscribe"), size=34, box=True, color=AMBER, pop=True)
    S.fade_in_out(0.3, 1.0)


def hold(sid):
    return {"s01_hook": 0.6, "s15_northeast": 0.8, "s17_closest": 1.5, "s19_outro": 1.0}.get(sid, 0.3)
