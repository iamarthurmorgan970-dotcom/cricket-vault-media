"""Thumbnail: Uttar Pradesh (amber) with the UK (cyan) laid on it at true size. Run from the episode folder."""
import sys, os
sys.path.insert(0, "../..")
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.collections import PolyCollection
import matplotlib.patheffects as pe
from engine.geo import load_world, merc, move
from engine.india import ST
from shapely.geometry import Polygon as SPoly
from shapely.ops import unary_union

C, _ = load_world()
cen = lambda rr: (lambda g: (g.centroid.x, g.centroid.y))(unary_union([SPoly(r).buffer(0) for r in rr]))
up = ST["Uttar Pradesh"]
uk = move(C["United Kingdom"], cen(C["United Kingdom"]), cen(up), 1.0)
B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_facecolor("#0b1a2b")
cx, cy = cen(up)
from engine.geo import mercy
w = 17.0
ax.set_xlim(cx - 0.27 * w, cx + 0.73 * w)
ax.set_ylim(mercy(cy) - w * 0.28, mercy(cy) + w * 0.28)
ax.add_collection(PolyCollection([merc(r) for rs in ST.values() for r in rs], facecolors="#24364d", edgecolors="#3b5476", lw=1))
ax.add_collection(PolyCollection([merc(r) for r in up], facecolors="#ffb703", edgecolors="white", lw=3, zorder=3))
ax.add_collection(PolyCollection([merc(r) for r in uk], facecolors="#4cc9f0", edgecolors="white", lw=3, alpha=0.82, zorder=4))
st = [pe.withStroke(linewidth=18, foreground="#07111d")]
fig.text(0.70, 0.66, "UP", fontproperties=B, size=150, color="#ffb703", ha="center", va="center", path_effects=st)
fig.text(0.70, 0.36, "= UK", fontproperties=B, size=130, color="#4cc9f0", ha="center", va="center", path_effects=st)
fig.text(0.70, 0.12, "+ 27 MORE", fontproperties=B, size=58, color="white", ha="center", va="center", path_effects=st)
fig.text(0.03, 0.05, "TRUE SCALE", fontproperties=B, size=34, color="#ffb703", ha="left", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
