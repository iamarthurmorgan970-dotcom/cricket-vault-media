import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as pe
B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_xlim(0, 16); ax.set_ylim(0, 9)
for i, c in enumerate(np.linspace(0, 1, 40)):
    ax.axhspan(i * 9 / 40, (i + 1) * 9 / 40, color=plt.cm.colors.to_hex((0.04 + 0.12 * c, 0.10 + 0.08 * c, 0.17 + 0.12 * c)), zorder=0)
ax.add_patch(Circle((8, 5.2), 1.3, color="#ffb703", alpha=0.9, zorder=1))
def mtn(x0, x1, peak, h, col):
    ax.add_patch(Polygon([[x0, 0], [peak, h], [x1, 0]], fc=col, ec="#07111d", lw=3, zorder=2))
    s = 0.28
    ax.add_patch(Polygon([[peak - (peak - x0) * s, h * (1 - s)], [peak, h], [peak + (x1 - peak) * s, h * (1 - s)],
                          [peak + 0.3, h * (1 - s) + 0.35], [peak - 0.2, h * (1 - s) + 0.1], [peak - 0.6, h * (1 - s) + 0.4]],
                         fc="#f1f5f9", ec="none", zorder=3))
mtn(-1.5, 8.6, 3.6, 6.4, "#3a9d5d")
mtn(7.4, 17.5, 12.4, 6.3, "#2b8fb3")
st = [pe.withStroke(linewidth=12, foreground="#07111d")]
fig.text(0.255, 0.20, "KEDARKANTHA", fontproperties=B, size=52, color="#7ae582", ha="center", path_effects=st, zorder=10)
fig.text(0.755, 0.20, "BRAHMATAL", fontproperties=B, size=58, color="#4cc9f0", ha="center", path_effects=st, zorder=10)
fig.text(0.5, 0.40, "VS", fontproperties=B, size=120, color="white", ha="center", path_effects=st, zorder=10)
fig.text(0.5, 0.86, "FIRST SNOW TREK?", fontproperties=B, size=64, color="#ffb703", ha="center", va="center", path_effects=st, zorder=10)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
