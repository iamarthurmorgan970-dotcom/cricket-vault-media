import sys, numpy as np, matplotlib
sys.path.insert(0, "../../engine")
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as pe
import geo
C, _ = geo.load_world()
B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
K = np.cos(np.radians(71))
gl = lambda a: np.column_stack([(a[:, 0] + 42) * K, a[:, 1]])
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_facecolor("#0b1a2b")
ax.add_collection(PolyCollection([gl(r) for n in C if n != "Greenland" for r in C[n]], facecolors="#1d2d42", edgecolors="#2d4260", linewidths=0.5))
ax.add_collection(PolyCollection([gl(r) for r in C["Greenland"]], facecolors="#e8f4ff", edgecolors="#4cc9f0", linewidths=3))
cx, cy, w = 9.0, 71.0, 46
h = w * 720 / 1280
ax.set_xlim(cx - w / 2, cx + w / 2); ax.set_ylim(cy - h / 2, cy + h / 2)
p = gl(np.array([[-51.72, 64.18]]))[0]
ax.scatter([p[0]], [p[1]], s=260, color="#ffb703", edgecolors="white", linewidths=3, zorder=5)
st = [pe.withStroke(linewidth=12, foreground="#07111d")]
fig.text(0.97, 0.66, "WHY SO", fontproperties=B, size=96, color="white", ha="right", path_effects=st)
fig.text(0.97, 0.42, "EMPTY?", fontproperties=B, size=120, color="#ffb703", ha="right", path_effects=st)
fig.text(0.97, 0.20, "56,740 PEOPLE", fontproperties=B, size=58, color="#4cc9f0", ha="right", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
