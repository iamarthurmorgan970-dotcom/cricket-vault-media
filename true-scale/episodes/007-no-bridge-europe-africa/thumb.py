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
d = json.load(open(f"{geo.DATA}/admin0_10m_ind.geojson"))
R = {}
for f in d["features"]:
    n = f["properties"]["ADMIN"]
    if n in ("Spain", "Morocco", "Portugal", "Gibraltar", "Algeria"):
        R[n] = [geo.merc(r) for r in geo._rings(shape(f["geometry"]), 0.002)]
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_facecolor("#0b1a2b")
ax.add_collection(PolyCollection([r for n in ("Spain", "Portugal", "Gibraltar") for r in R[n]], facecolors="#2f6f9a",
                                 edgecolors="#4cc9f0", linewidths=2))
ax.add_collection(PolyCollection([r for n in ("Morocco", "Algeria") for r in R[n]], facecolors="#8a6a2a",
                                 edgecolors="#ffb703", linewidths=2))
a = geo.merc(np.array([[-5.61, 36.00], [-5.48, 35.91]]))
ax.plot(a[:, 0], a[:, 1], color="#ffffff", lw=14, solid_capstyle="round", zorder=5)
ax.plot(a[:, 0], a[:, 1], color="#ff4d8d", lw=9, solid_capstyle="round", zorder=6)
cx, cy, w = -4.85, geo.mercy(35.95), 2.8
h = w * 720 / 1280
ax.set_xlim(cx - w / 2, cx + w / 2); ax.set_ylim(cy - h / 2, cy + h / 2)
st = [pe.withStroke(linewidth=12, foreground="#07111d")]
fig.text(0.97, 0.80, "EUROPE", fontproperties=B, size=58, color="#4cc9f0", ha="right", path_effects=st)
fig.text(0.97, 0.13, "AFRICA", fontproperties=B, size=58, color="#ffb703", ha="right", path_effects=st)
fig.text(0.97, 0.52, "ONLY 14 KM", fontproperties=B, size=96, color="white", ha="right", path_effects=st)
fig.text(0.97, 0.34, "NO BRIDGE?", fontproperties=B, size=96, color="#ff4d8d", ha="right", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
