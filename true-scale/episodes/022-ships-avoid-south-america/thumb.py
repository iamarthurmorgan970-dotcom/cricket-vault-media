import sys, json, numpy as np, matplotlib
sys.path.insert(0, "../../engine")
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as pe
from shapely.geometry import shape
import geo
B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
d = json.load(open(f"{geo.DATA}/countries50.geojson"))
rings = []
for f in d["features"]:
    rings += [geo.merc(r) for r in geo._rings(shape(f["geometry"]), 0.02)]
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_facecolor("#0b1a2b")
ax.add_collection(PolyCollection(rings, facecolors="#2a3f5a", edgecolors="#3b5476", linewidths=0.8))
horn = [(-34, -6), (-38, -24), (-54, -42), (-64, -54), (-67.3, -57.3), (-76, -56), (-80, -45), (-80, -25), (-86, -12)]
xy = geo.merc(np.array(horn, float))
ax.plot(xy[:, 0], xy[:, 1], color="white", lw=16, solid_capstyle="round", zorder=4)
ax.plot(xy[:, 0], xy[:, 1], color="#ffb703", lw=10, solid_capstyle="round", zorder=5)
p = geo.merc(np.array([[-67.27, -55.98]]))[0]
ax.scatter([p[0]], [p[1]], s=1100, color="#ff4d8d", edgecolors="white", linewidths=4, zorder=6)
cx, cy, w = -32, geo.mercy(-40), 104
h = w * 720 / 1280
ax.set_xlim(cx - w / 2, cx + w / 2); ax.set_ylim(cy - h / 2, cy + h / 2)
st = [pe.withStroke(linewidth=14, foreground="#07111d")]
fig.text(0.97, 0.64, "WHY SHIPS", fontproperties=B, size=96, color="white", ha="right", path_effects=st)
fig.text(0.97, 0.43, "AVOID THIS", fontproperties=B, size=96, color="#ffb703", ha="right", path_effects=st)
fig.text(0.97, 0.25, "CAPE HORN", fontproperties=B, size=62, color="#ff4d8d", ha="right", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
