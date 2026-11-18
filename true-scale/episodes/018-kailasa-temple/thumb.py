"""Thumbnail for 018 Kailasa. Run from the episode folder: python3 thumb.py"""
import sys, os
sys.path.insert(0, "../..")
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Rectangle
import matplotlib.patheffects as pe
import importlib.util

B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
spec = importlib.util.spec_from_file_location("tp", "scenes.py")
src = open("scenes.py").read()
ns = {}
# reuse the tower outline helper without loading the whole engine
exec(src[src.index("def tower_poly"):src.index("def elevation")], {"np": np}, ns)
tower_poly = ns["tower_poly"]

STONE, STONE_E, STONE_D, ROCK, STRATA = "#c7b896", "#f3ead6", "#9a8c70", "#2e394a", "#46556b"
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.set_xlim(-4, 150); ax.set_ylim(-26, 60.6)
# rock walls and floor
ax.add_patch(Rectangle((-20, -40), 220, 40, fc=ROCK))
ax.add_patch(Rectangle((-20, 0), 30, 40, fc=ROCK))
ax.add_patch(Rectangle((62, 0), 140, 40, fc=ROCK))
for y in np.arange(-38, 40, 5):
    ax.plot([-20, 10], [y, y], color=STRATA, lw=1.5)
    ax.plot([62, 200], [y, y], color=STRATA, lw=1.5)
    if y < 0:
        ax.plot([10, 62], [y, y], color=STRATA, lw=1.5)
# glow in the pit
for k in range(12):
    ax.add_patch(Rectangle((10, 0), 52, 40 - k * 2.5, fc="#ffb703", alpha=0.025, ec="none"))
# temple (scaled side view)
ax.add_patch(Rectangle((14, 0), 36, 9, fc=STONE_D, ec=STONE_E, lw=2))
for k in range(9):
    x = 15 + k * 3.9
    ax.add_patch(Polygon([(x, 0.8), (x + 2.8, 0.8), (x + 2.8, 4.2), (x + 1.4, 5.4), (x, 4.2)], fc="#b3a283",
                         ec=STONE_E, lw=1))
ax.add_patch(Rectangle((14, 9), 14, 9, fc=STONE, ec=STONE_E, lw=2))
ax.add_patch(Polygon(tower_poly(27, 50, 9, 37), fc=STONE, ec=STONE_E, lw=2))
ax.add_patch(Rectangle((52, 0), 9, 13, fc=STONE_D, ec=STONE_E, lw=2))
# chisel marks: top-down arrow

st = [pe.withStroke(linewidth=14, foreground="#07111d")]
fig.text(0.97, 0.73, "CARVED", fontproperties=B, size=104, color="white", ha="right", path_effects=st)
fig.text(0.97, 0.47, "FROM ONE", fontproperties=B, size=86, color="#4cc9f0", ha="right", path_effects=st)
fig.text(0.97, 0.20, "ROCK", fontproperties=B, size=140, color="#ffb703", ha="right", path_effects=st)
os.makedirs("out", exist_ok=True)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
