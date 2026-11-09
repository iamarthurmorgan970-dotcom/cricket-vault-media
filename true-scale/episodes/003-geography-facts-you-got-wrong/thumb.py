import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Rectangle
import matplotlib.patheffects as pe
B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_xlim(0, 12.8); ax.set_ylim(0, 7.2)
st = [pe.withStroke(linewidth=9, foreground="#07111d")]
sea = 3.0
ax.add_patch(Rectangle((6.0, 0), 6.8, sea, color="#0f2f52"))
ax.plot([6.0, 12.8], [sea, sea], color="#4cc9f0", lw=3)
s = 0.36  # units per km
ax.add_patch(Polygon([[6.4, sea], [8.6, sea], [7.5, sea + 8.849 * s]], color="#ffb703"))
ax.add_patch(Polygon([[8.8, sea - 6.0 * s], [12.6, sea - 6.0 * s], [10.7, sea + 4.21 * s]], color="#7ae582"))
ax.text(7.5, sea + 8.849 * s + 0.12, "EVEREST", fontproperties=B, size=28, color="#ffb703", ha="center", path_effects=st)
ax.text(10.7, sea + 4.21 * s + 0.12, "MAUNA KEA", fontproperties=B, size=28, color="#7ae582", ha="center", path_effects=st)
ax.text(10.7, 1.6, "TALLER!", fontproperties=B, size=40, color="white", ha="center", path_effects=st)
fig.text(0.04, 0.70, "YOU GOT", fontproperties=B, size=84, color="white", ha="left", path_effects=st)
fig.text(0.04, 0.48, "THESE", fontproperties=B, size=84, color="white", ha="left", path_effects=st)
fig.text(0.04, 0.26, "WRONG", fontproperties=B, size=100, color="#ff5a5f", ha="left", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
