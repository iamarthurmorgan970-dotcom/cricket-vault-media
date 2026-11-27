import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Rectangle
import matplotlib.patheffects as pe
B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.set_xlim(0, 16); ax.set_ylim(-11800, 1500)
ax.add_patch(Rectangle((0, 0), 16, 1500, fc="#0b1a2b"))
for i in range(40):
    d0 = -11800 * i / 40
    c = np.array([0x16, 0x4e, 0x80]) * (1 - i / 40) + np.array([0x04, 0x0c, 0x16]) * (i / 40)
    ax.add_patch(Rectangle((0, d0 - 300), 16, 300, fc="#%02x%02x%02x" % tuple(c.astype(int)), ec="none"))
ax.plot([0, 16], [0, 0], color="#4cc9f0", lw=6)
ax.add_patch(Polygon([[0, -4200], [2.2, -4000], [3.6, -5200], [5.1, -11034], [5.9, -11034], [7.4, -5000],
                      [9.0, -3900], [9.0, -12000], [0, -12000]], fc="#2a3f5a", ec="#3b5476", lw=3))
ax.add_patch(Polygon([[3.0, -11034], [8.0, -11034], [5.5, -11034 + 8850]], fc="#e8f1f8", ec="white", lw=3))
ax.annotate("", xy=(5.5, -150), xytext=(5.5, -2080),
            arrowprops=dict(arrowstyle="<->", color="#ffb703", lw=5))
st = [pe.withStroke(linewidth=14, foreground="#07111d")]
fig.text(0.97, 0.66, "EVEREST", fontproperties=B, size=104, color="white", ha="right", path_effects=st)
fig.text(0.97, 0.45, "SINKS HERE", fontproperties=B, size=88, color="#ffb703", ha="right", path_effects=st)
fig.text(0.97, 0.27, "2 KM TO SPARE", fontproperties=B, size=54, color="#ff4d8d", ha="right", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
