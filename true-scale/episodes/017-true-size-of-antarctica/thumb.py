"""Thumbnail for 017 (run from the episode folder): Antarctica on an equal-area polar map with India placed
on it at true size, plus 2-3 huge words."""
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


def P(a):
    lon = np.radians(a[:, 0])
    c = np.radians(90 + np.clip(a[:, 1], -90, 90))
    rho = 2 * np.sin(c / 2)
    return np.column_stack([rho * np.sin(lon), rho * np.cos(lon)])


C = {f["properties"]["ADMIN"]: geo._rings(shape(f["geometry"]), 0.02)
     for f in json.load(open(f"{geo.DATA}/countries50.geojson"))["features"]}
IND = [geo._rings(shape(f["geometry"]), 0.02) for f in json.load(open(f"{geo.DATA}/admin0_10m_ind.geojson"))["features"]
       if f["properties"]["ADMIN"] == "India"][0]
IND = [r for r in IND if len(r) > 20]
SH = [r for f in json.load(open(f"{geo.DATA}/ne_50m_antarctic_ice_shelves_polys.geojson"))["features"]
      for r in geo._rings(shape(f["geometry"]), 0.02)]
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_facecolor("#0b1a2b")
ax.add_collection(PolyCollection([P(r) for r in SH], facecolors="#a9cbe6", edgecolors="#d9ecfa", linewidths=0.8))
ax.add_collection(PolyCollection([P(r) for r in C["Antarctica"]], facecolors="#e8f4ff", edgecolors="#e8f4ff",
                                 linewidths=0.8))
ax.add_collection(PolyCollection([P(r) for r in geo.move(IND, (79, 22), (40, -80), 1)],
                                 facecolors="#ff4d8d", edgecolors="white", linewidths=2, alpha=0.95))
cx, cy, w = -0.56, 0.0, 1.85
h = w * 720 / 1280
ax.set_xlim(cx - w / 2, cx + w / 2); ax.set_ylim(cy - h / 2, cy + h / 2)
st = [pe.withStroke(linewidth=14, foreground="#07111d")]
fig.text(0.04, 0.80, "ANTARCTICA", fontproperties=B, size=70, color="#4cc9f0", ha="left", path_effects=st)
fig.text(0.04, 0.47, "4×", fontproperties=B, size=170, color="white", ha="left", path_effects=st)
fig.text(0.04, 0.25, "INDIA", fontproperties=B, size=110, color="#ff4d8d", ha="left", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
