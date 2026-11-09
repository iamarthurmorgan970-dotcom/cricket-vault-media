import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as pe
import geo
from geo import merc, move
C, CONT = geo.load_world()
BOLD = FontProperties(fname="fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_facecolor("#0b1a2b")
ax.add_collection(PolyCollection([merc(r) for n in C for r in C[n]], facecolors="#24364d", edgecolors="#3b5476", linewidths=0.5))
af = [r for n, c in CONT.items() if c == "Africa" for r in C[n]]
ax.add_collection(PolyCollection([merc(r) for r in af], facecolors="#ffb703", edgecolors="#ffb703", linewidths=0.6))
g = C["Greenland"]
ax.add_collection(PolyCollection([merc(r) for r in g], facecolors="#4cc9f0", edgecolors="white", linewidths=1.5))
ax.add_collection(PolyCollection([merc(r) for r in move(g, (-41, 72), (22, 2), 1)], facecolors="#4cc9f0", edgecolors="white", linewidths=2))
cx, cy, w = 40, 62, 370
h = w * 720 / 1280
ax.set_xlim(cx - w / 2, cx + w / 2); ax.set_ylim(cy - h / 2, cy + h / 2)
ax.annotate("", xy=(16, 14), xytext=(-30, 82), arrowprops=dict(arrowstyle="-|>,head_width=0.8,head_length=1.2", lw=6, color="white", connectionstyle="arc3,rad=0.3"))
st = [pe.withStroke(linewidth=10, foreground="#07111d")]
fig.text(0.97, 0.80, "THE MAP", fontproperties=BOLD, size=78, color="white", ha="right", path_effects=st)
fig.text(0.97, 0.63, "LIED", fontproperties=BOLD, size=110, color="#ffb703", ha="right", path_effects=st)
fig.text(0.56, 0.18, "REAL SIZE", fontproperties=BOLD, size=44, color="#4cc9f0", ha="left", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
