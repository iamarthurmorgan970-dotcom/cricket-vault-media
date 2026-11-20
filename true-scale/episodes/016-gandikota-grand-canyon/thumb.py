import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Rectangle, Circle
import matplotlib.patheffects as pe

B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.set_xlim(0, 12.8); ax.set_ylim(0, 7.2)
# sunset sky
for k in range(60):
    y = 7.2 * k / 60
    c = np.array([0.98, 0.62, 0.25]) * (1 - k / 60) + np.array([0.04, 0.10, 0.17]) * (k / 60)
    ax.add_patch(Rectangle((0, y), 12.8, 7.2 / 60 + 0.01, fc=c, ec="none"))
ax.add_patch(Circle((3.0, 3.9), 0.75, fc="#ffd27a", ec="none", alpha=0.9))
# canyon: two red cliffs with a deep gorge and river
rng = np.random.default_rng(3)
def cliff(xs, top, base=0):
    pts = [(xs[0], base)] + [(x, top + rng.uniform(-0.08, 0.08)) for x in np.linspace(xs[0], xs[1], 12)] + [(xs[1], base)]
    return pts
L = [(0, 0), (0, 3.6), (1.5, 3.55), (3.2, 3.5), (4.6, 3.4), (5.1, 3.0), (5.35, 1.2), (5.5, 0.6), (5.5, 0)]
R = [(7.0, 0), (7.0, 0.6), (7.2, 1.3), (7.45, 3.1), (8.0, 3.45), (12.8, 3.6), (12.8, 0)]
for P, c in ((L, "#b5513a"), (R, "#a4472f")):
    ax.add_patch(Polygon(P, closed=True, fc=c, ec="#5e2618", lw=3))
for y in np.linspace(0.6, 3.2, 8):
    ax.plot([0, 5.0], [y, y], color="#8e3b2a", lw=2)
    ax.plot([7.5, 12.8], [y, y], color="#7f3424", lw=2)
ax.add_patch(Polygon([(5.45, 0), (5.5, 0.6), (7.0, 0.6), (7.05, 0)], closed=True, fc="#3a8fc4", ec="none"))
# fort on the right rim
fx = 9.0
ax.add_patch(Rectangle((fx, 3.55), 2.6, 0.55, fc="#e6d6b4", ec="#6b5a3a", lw=2.5))
for k in range(8):
    ax.add_patch(Rectangle((fx + 0.05 + k * 0.33, 4.1), 0.18, 0.18, fc="#e6d6b4", ec="#6b5a3a", lw=2))
for x in (fx - 0.25, fx + 2.45):
    ax.add_patch(Rectangle((x, 3.55), 0.42, 0.95, fc="#f0e3c4", ec="#6b5a3a", lw=2.5))
st = [pe.withStroke(linewidth=16, foreground="#07111d")]
fig.text(0.5, 0.84, "INDIA'S", fontproperties=B, size=80, color="#4cc9f0", ha="center", path_effects=st)
fig.text(0.5, 0.655, "GRAND CANYON?", fontproperties=B, size=96, color="white", ha="center", path_effects=st)
fig.text(0.04, 0.06, "TRUE SCALE", fontproperties=B, size=40, color="#ffb703", ha="left", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
