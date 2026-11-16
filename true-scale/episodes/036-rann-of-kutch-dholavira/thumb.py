import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle, Polygon
import matplotlib.patheffects as pe
from scipy.spatial import Voronoi

B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.set_xlim(0, 12.8); ax.set_ylim(0, 7.2)
# night sky
ax.add_patch(plt.Rectangle((0, 0), 12.8, 7.2, fc="#0b1a2b"))
for k in range(30):
    r = 1.0 + 0.04 * k
    ax.add_patch(Circle((2.3, 5.6), r, fc="#f6f3e6", ec="none", alpha=0.035))
ax.add_patch(Circle((2.3, 5.6), 1.0, fc="#f6f3e6", ec="none"))
rng = np.random.default_rng(4)
u = rng.uniform(0, 1, 420)
pts = np.column_stack([rng.uniform(-1, 13.8, 420), 3.6 * (1 - u ** 0.6)])
pts[:, 1] = 3.6 - (3.6 - pts[:, 1])  # keep
vor = Voronoi(pts)
ax.add_patch(plt.Rectangle((0, 0), 12.8, 3.6, fc="#e4edf3"))
for (i, j) in vor.ridge_vertices:
    if i < 0 or j < 0:
        continue
    A, Bp = vor.vertices[i], vor.vertices[j]
    if max(A[1], Bp[1]) > 3.55 or min(A[1], Bp[1]) < -0.5:
        continue
    ax.plot([A[0], Bp[0]], [A[1], Bp[1]], color="#a9bccb", lw=1 + 2.5 * (1 - A[1] / 3.6), solid_capstyle="round")
ax.add_patch(plt.Rectangle((0, 3.55), 12.8, 0.1, fc="#c9d6e0"))
st = [pe.withStroke(linewidth=14, foreground="#07111d")]
fig.text(0.97, 0.80, "INDIA'S", fontproperties=B, size=80, color="#4cc9f0", ha="right", path_effects=st)
fig.text(0.97, 0.53, "WHITE", fontproperties=B, size=140, color="white", ha="right", path_effects=st)
fig.text(0.97, 0.24, "DESERT", fontproperties=B, size=140, color="#ffb703", ha="right", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
