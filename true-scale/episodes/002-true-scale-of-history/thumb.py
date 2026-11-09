import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Circle
import matplotlib.patheffects as pe
B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_xlim(0, 12.8); ax.set_ylim(0, 7.2)
st = [pe.withStroke(linewidth=9, foreground="#07111d")]
y = 1.9
ax.plot([0.4, 12.4], [y, y], color="#3b5476", lw=6)
# pyramid, Cleopatra, Moon
ax.add_patch(Polygon([[0.8, y + 0.15], [2.6, y + 0.15], [1.7, y + 1.75]], color="#ffd166"))
ax.add_patch(Circle((7.05, y), 0.28, color="#ff4d8d", ec="white", lw=3, zorder=5))
ax.add_patch(Circle((11.4, y + 0.95), 0.75, color="#d9dee7", zorder=4))
for cx, cy, r in [(11.15, 3.05, 0.13), (11.6, 2.65, 0.1), (11.55, 3.2, 0.08)]:
    ax.add_patch(Circle((cx, cy), r, color="#aeb6c4", zorder=5))
ax.text(1.7, y - 0.35, "PYRAMIDS", fontproperties=B, size=30, color="#ffd166", ha="center", va="top")
ax.text(7.05, y - 0.35, "CLEOPATRA", fontproperties=B, size=30, color="#ff4d8d", ha="center", va="top")
ax.text(11.4, y - 0.35, "MOON", fontproperties=B, size=30, color="#d9dee7", ha="center", va="top")
for x0, x1, lab, c in [(1.7, 7.05, "2,500 YRS", "#ffd166"), (7.05, 11.4, "2,000 YRS", "#4cc9f0")]:
    ax.plot([x0, x0, x1, x1], [y + 2.0, y + 2.2, y + 2.2, y + 2.0], color=c, lw=6)
    ax.text((x0 + x1) / 2, y + 2.35, lab, fontproperties=B, size=40, color=c, ha="center", path_effects=st)
fig.text(0.5, 0.86, "CLOSER TO THE MOON?!", fontproperties=B, size=78, color="white", ha="center", va="center", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
