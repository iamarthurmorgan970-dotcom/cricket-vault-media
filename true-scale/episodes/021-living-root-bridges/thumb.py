"""Thumbnail for 021 (run from the episode folder): 'THIS BRIDGE IS ALIVE' over an illustrated root bridge."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Rectangle, Ellipse
import matplotlib.patheffects as pe

B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.set_xlim(0, 12.8); ax.set_ylim(0, 7.2)
for k in range(60):
    u = k / 60
    c = np.array([0.62, 0.78, 0.74]) * (1 - u) + np.array([0.05, 0.12, 0.17]) * u
    ax.add_patch(Rectangle((0, 7.2 * u), 12.8, 7.2 / 60 + 0.01, fc=c, ec="none"))
xs = np.linspace(0, 12.8, 200)
ax.fill_between(xs, 0, 4.6 + 0.5 * np.sin(xs * 0.7), color="#3c6656")
# banks + stream
ax.add_patch(Polygon([(0, 0), (0, 5.6), (3.0, 4.4), (4.2, 2.6), (4.4, 0)], fc="#1f3d29", ec="none"))
ax.add_patch(Polygon([(12.8, 0), (12.8, 5.8), (10.0, 4.5), (8.8, 2.6), (8.6, 0)], fc="#1f3d29", ec="none"))
ax.add_patch(Rectangle((4.4, 0), 4.2, 0.9, fc="#3a8fc4", ec="none"))
rng = np.random.default_rng(4)
for k in range(26):
    side = k % 2
    x = rng.uniform(0.2, 3.6) if side == 0 else rng.uniform(9.2, 12.6)
    ax.add_patch(Ellipse((x, rng.uniform(3.0, 5.6)), rng.uniform(0.9, 1.6), rng.uniform(0.7, 1.1),
                         fc=["#2f6b3f", "#3f8a4f", "#24502f"][k % 3], ec="none"))
# trunks
for x in (3.2, 9.6):
    ax.add_patch(Polygon([(x - 0.3, 2.6), (x + 0.3, 2.6), (x + 0.18, 5.6), (x - 0.18, 5.6)], fc="#6e5236",
                         ec="#3b2a18", lw=2))
    for k in range(5):
        ax.add_patch(Ellipse((x + rng.uniform(-1.1, 1.1), 5.9 + rng.uniform(-0.2, 0.6)), 1.6, 1.0,
                             fc=["#2f6b3f", "#3f8a4f", "#24502f"][k % 3], ec="#1c3a24", lw=1))
# the bridge: thick bundle of roots
u = np.linspace(0, 1, 120)
for k in range(26):
    off = rng.uniform(-0.25, 0.25)
    y = 2.7 + off - 1.0 * 4 * u * (1 - u) + 0.06 * np.sin(u * 20 + k)
    if k % 5 == 0:
        y = y + 1.1
    ax.plot(3.3 + 6.2 * u, y, color=["#a07850", "#8a6440", "#b88d5e"][k % 3], lw=rng.uniform(3, 7),
            solid_capstyle="round")
st = [pe.withStroke(linewidth=18, foreground="#07111d")]
fig.text(0.5, 0.80, "THIS BRIDGE", fontproperties=B, size=104, color="white", ha="center", va="center",
         path_effects=st)
fig.text(0.5, 0.12, "IS ALIVE", fontproperties=B, size=120, color="#7ae582", ha="center", va="center",
         path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
