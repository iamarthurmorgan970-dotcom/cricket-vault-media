import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Rectangle, Circle, Ellipse
import matplotlib.patheffects as pe

B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.set_xlim(0, 12.8); ax.set_ylim(0, 7.2)
for k in range(60):
    y = 7.2 * k / 60
    u = k / 60
    c = np.array([0.98, 0.62, 0.25]) * (1 - u) ** 1.3 + np.array([0.04, 0.10, 0.17]) * (1 - (1 - u) ** 1.3)
    ax.add_patch(Rectangle((0, y), 12.8, 7.2 / 60 + 0.01, fc=c, ec="none"))
ax.add_patch(Circle((2.2, 2.6), 0.7, fc="#ffd27a", ec="none", alpha=0.9))
ax.add_patch(Rectangle((0, 0), 12.8, 0.9, fc="#3b2f24", ec="none"))
cols = ["#c9a26b", "#b88d58", "#d8b47e", "#a77b4a", "#bf9660"]
rng = np.random.default_rng(11)
# big heap on the right with a balanced boulder on top
heap = [(9.6, 3.2, 4)]
for cx, half, rows in heap:
    for r in range(rows):
        w = half * (1 - r / (rows + 0.4))
        n = max(1, int(round(w / 0.9)))
        for j in range(n):
            x = cx - w + (j + 0.5) * 2 * w / n + rng.uniform(-0.1, 0.1)
            ew, eh = rng.uniform(1.3, 1.7), rng.uniform(1.0, 1.25)
            y = 0.85 + r * 0.95
            ax.add_patch(Ellipse((x, y + eh / 2), ew, eh, angle=rng.uniform(-15, 15), fc=cols[rng.integers(5)],
                                 ec="#5a3d22", lw=3))
ax.add_patch(Ellipse((9.75, 5.55), 2.0, 1.5, angle=10, fc="#d8b47e", ec="#5a3d22", lw=3.5))
# small heaps left
for cx in (1.0, 4.4):
    for j in range(3):
        ax.add_patch(Ellipse((cx + j * 0.6 - 0.6, 1.2), 0.75, 0.6, fc=cols[rng.integers(5)], ec="#5a3d22", lw=2))
    ax.add_patch(Ellipse((cx, 1.7), 0.7, 0.55, fc=cols[rng.integers(5)], ec="#5a3d22", lw=2))
# temple tower silhouette for scale
gx = 5.7
ax.add_patch(Polygon([(gx - 0.45, 0.9), (gx + 0.45, 0.9), (gx + 0.3, 2.3), (gx + 0.15, 2.55), (gx - 0.15, 2.55),
                      (gx - 0.3, 2.3)], closed=True, fc="#4a3626", ec="#2b2017", lw=2))
st = [pe.withStroke(linewidth=16, foreground="#07111d")]
fig.text(0.04, 0.77, "WHO PILED", fontproperties=B, size=96, color="white", ha="left", path_effects=st)
fig.text(0.04, 0.58, "THESE?", fontproperties=B, size=110, color="#ffb703", ha="left", path_effects=st)
fig.text(0.04, 0.42, "HAMPI", fontproperties=B, size=60, color="#4cc9f0", ha="left", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
