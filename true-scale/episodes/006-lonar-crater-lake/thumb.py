import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle, Wedge
import matplotlib.patheffects as pe

B = FontProperties(fname="../../fonts/Poppins-Bold.ttf")
fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="#0b1a2b")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_facecolor("#1d2d42")
ax.set_xlim(0, 12.8); ax.set_ylim(0, 7.2)
ax.add_patch(plt.Rectangle((0, 0), 12.8, 7.2, fc="#1d2d42"))
cx, cy = 3.6, 3.6
ax.add_patch(Circle((cx, cy), 3.55, fc="#24364d", ec="none"))
ax.add_patch(Circle((cx, cy), 3.05, fc="#2f4a70", ec="white", lw=7))
ax.add_patch(Circle((cx, cy), 2.45, fc="#2a4262", ec="none"))
ax.add_patch(Wedge((cx, cy), 2.0, 90, 270, fc="#3f8f6b", ec="none"))
ax.add_patch(Wedge((cx, cy), 2.0, -90, 90, fc="#ff7aa8", ec="none"))
ax.add_patch(Circle((cx, cy), 2.0, fill=False, ec="#e8f4ff", lw=3))
# incoming rock streak
ax.plot([10.2, 6.4], [7.4, 5.9], color="#ffb703", lw=14, alpha=0.35, solid_capstyle="round")
ax.add_patch(Circle((6.4, 5.9), 0.28, fc="#ffb703", ec="white", lw=3))
st = [pe.withStroke(linewidth=12, foreground="#07111d")]
fig.text(0.97, 0.66, "INDIA'S", fontproperties=B, size=84, color="#4cc9f0", ha="right", path_effects=st)
fig.text(0.97, 0.40, "SPACE", fontproperties=B, size=130, color="white", ha="right", path_effects=st)
fig.text(0.97, 0.12, "CRATER", fontproperties=B, size=130, color="#ffb703", ha="right", path_effects=st)
fig.savefig("out/thumbnail.png", dpi=100, facecolor="#0b1a2b")
