import sys, numpy as np, matplotlib
matplotlib.use("Agg")
sys.path.insert(0, "../../engine")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as pe
import geo
from geo import merc, mercy
import json
from shapely.geometry import shape, MultiPolygon
C, _ = geo.load_world()
B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
d = json.load(open("/root/.cache/true-scale/admin1_10m.geojson"))
st = []
for f in d["features"]:
    if f["properties"].get("adm0_a3") == "IND":
        g = shape(f["geometry"]).simplify(0.03)
        for q in (g.geoms if isinstance(g, MultiPolygon) else [g]):
            st.append(merc(np.asarray(q.exterior.coords)))
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.add_collection(PolyCollection([merc(r) for n in C for r in C[n]], facecolors="#1d2d42", edgecolors="#2d4260", linewidths=0.5))
pov = json.load(open("/root/.cache/true-scale/admin0_10m_ind.geojson"))
gi = shape([f for f in pov["features"] if f["properties"].get("ADMIN") == "India"][0]["geometry"]).simplify(0.03)
ax.add_collection(PolyCollection([merc(np.asarray(q.exterior.coords)) for q in gi.geoms if q.area > 0.002],
                                 facecolors="#ffb703", edgecolors="#c98500", linewidths=0.8))
ax.add_collection(PolyCollection(st, facecolors="#ffb703", edgecolors="#c98500", linewidths=0.8))
cx, cy, w = 70, mercy(22), 62
h = w * 720 / 1280
ax.set_xlim(cx - w / 2, cx + w / 2); ax.set_ylim(cy - h / 2, cy + h / 2)
for lo, la, c in [(76.51, 19.98, "#4cc9f0"), (91.68, 25.25, "#7ae582"), (94.2, 26.95, "#ff4d8d"), (79.73, 30.26, "#ff4d8d"),
                  (78.28, 14.81, "#ffffff"), (70.21, 23.89, "#ffffff"), (76.9, 33.6, "#4cc9f0")]:
    p = merc(np.array([[lo, la]]))[0]
    ax.scatter([p[0]], [p[1]], s=520, color=c, edgecolors="#07111d", linewidths=4, zorder=5)
s = [pe.withStroke(linewidth=10, foreground="#07111d")]
fig.text(0.03, 0.80, "INDIA'S", fontproperties=B, size=80, color="white", path_effects=s)
fig.text(0.03, 0.58, "HIDDEN", fontproperties=B, size=96, color="#ffb703", path_effects=s)
fig.text(0.03, 0.36, "WONDERS", fontproperties=B, size=96, color="#ffb703", path_effects=s)
fig.text(0.03, 0.18, "you've never seen", fontproperties=B, size=44, color="white", path_effects=s)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
