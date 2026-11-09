"""True Scale engine core: frame size, palette, fonts, the Scene class and the per-scene renderer.
An episode is a folder with script.json (narration per scene) and scenes.py (one function per scene id).
make.py sets EP (the episode being built) before scenes are rendered."""
import json, os, re, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import soundfile as sf
from . import geo
from .geo import merc, mercy, equal_earth, ortho, move, ease, ease2

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1920, 1080, 30
LEAD, TAIL = 0.5, 1.1
BOLD = FontProperties(fname=f"{HERE}/fonts/Poppins-Bold.ttf")
REG = FontProperties(fname=f"{HERE}/fonts/Poppins-Regular.ttf")
OCEAN, LAND, EDGE, GRID = "#0b1a2b", "#24364d", "#3b5476", "#132840"
AMBER, CYAN, PINK, GREEN, VIOLET = "#ffb703", "#4cc9f0", "#ff4d8d", "#7ae582", "#b388ff"
WHITE, MUTED = "#f1f5f9", "#9fb0c6"

COUNTRIES, CONT = geo.load_world()
ALASKA, US48, _ = geo.split_usa(COUNTRIES["United States of America"])
AFRICA = [n for n, c in CONT.items() if c == "Africa"]


class Episode:
    """The episode being built: its folder, narration script and audio clips."""

    def __init__(self, folder):
        self.dir = os.path.abspath(folder)
        self.script = {s["id"]: s for s in json.load(open(f"{self.dir}/script.json"))}
        self.order = [s["id"] for s in json.load(open(f"{self.dir}/script.json"))]
        self.scenes = {}           # id -> function(S), filled from scenes.py
        self.hold = None           # optional function(sid) -> extra seconds at the end of a scene
        self._len = {}


EP = None


def speech_len(sid):
    if sid not in EP._len:
        a, sr = sf.read(f"{EP.dir}/audio/{sid}.wav")
        EP._len[sid] = len(a) / sr
    return EP._len[sid]


def duration(sid):
    extra = EP.script[sid].get("hold", 0.0) + (EP.hold(sid) if EP.hold else 0.0)
    return LEAD + speech_len(sid) + TAIL + extra


def cue(sid, phrase, which=0):
    """Approximate time (s from scene start) when `phrase` is spoken: weight characters plus pauses at punctuation."""
    text = EP.script[sid]["text"]
    w = np.array([1.0 + (9 if ch in ".?!" else 4 if ch in ",:;" else 0) for ch in text])
    cum = np.concatenate([[0], np.cumsum(w)])
    hits = [m.start() for m in re.finditer(re.escape(phrase), text)]
    if not hits:
        raise KeyError(f"cue phrase not in narration of {sid}: {phrase!r}")
    return LEAD + speech_len(sid) * cum[hits[which]] / cum[-1]


# ------------------------------------------------------------------ scene scaffolding
class Scene:
    def __init__(self, sid):
        self.sid, self.T = sid, duration(sid)
        self.fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=OCEAN)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_facecolor(OCEAN)
        self.ax.set_axis_off()
        self.updaters, self.texts = [], []

    def c(self, phrase, which=0):
        return cue(self.sid, phrase, which)

    # camera: keyframes of (t, cx, cy, width)
    def camera(self, keys):
        def up(t):
            ks = keys
            if t <= ks[0][0]:
                k = ks[0][1:]
            elif t >= ks[-1][0]:
                k = ks[-1][1:]
            else:
                for (t0, *a), (t1, *b) in zip(ks, ks[1:]):
                    if t0 <= t <= t1:
                        u = ease2((t - t0) / max(t1 - t0, 1e-6))
                        k = [x + (y - x) * u for x, y in zip(a, b)]
                        break
            cx, cy, w = k
            h = w * H / W
            self.ax.set_xlim(cx - w / 2, cx + w / 2)
            self.ax.set_ylim(cy - h / 2, cy + h / 2)
        self.updaters.append(up)

    def text(self, x, y, s, t0, t1=None, size=40, color=WHITE, font=BOLD, ha="center", va="center",
             box=False, pop=False, fade=0.35, zorder=50):
        kw = dict(fontproperties=font, size=size, color=color, ha=ha, va=va, zorder=zorder, alpha=0)
        if box:
            kw["bbox"] = dict(boxstyle="round,pad=0.45,rounding_size=0.6", fc="#07111d", ec="none", alpha=0)
        art = self.fig.text(x, y, s, **kw)
        t1 = self.T + 1 if t1 is None else t1

        def up(t):
            a = min(ease((t - t0) / fade), ease((t1 - t) / fade))
            art.set_alpha(a)
            if box:
                art.get_bbox_patch().set_alpha(0.82 * a)
            if pop:
                art.set_fontsize(size * (0.85 + 0.15 * ease((t - t0) / 0.3)))
        self.updaters.append(up)
        return art

    def headline(self, s, t0, t1=None, y=0.9, size=46, color=WHITE):
        return self.text(0.5, y, s, t0, t1, size=size, color=color, box=True, pop=True)

    def caption(self, s, t0, t1=None, color=WHITE, size=34):
        return self.text(0.5, 0.09, s, t0, t1, size=size, color=color, font=BOLD, box=True)

    def world(self, proj=merc, names=None, fc=LAND, ec=EDGE, lw=0.5, z=1, alpha=1.0):
        names = names or list(COUNTRIES)
        verts = [proj(r) for n in names for r in COUNTRIES[n]]
        pc = PolyCollection(verts, facecolors=fc, edgecolors=ec, linewidths=lw, zorder=z, alpha=alpha)
        self.ax.add_collection(pc)
        return pc

    def rings(self, rings, proj=merc, fc=CYAN, ec=WHITE, lw=1.2, z=5, alpha=0.9):
        pc = PolyCollection([proj(r) for r in rings], facecolors=fc, edgecolors=ec, linewidths=lw,
                            zorder=z, alpha=alpha)
        self.ax.add_collection(pc)
        return pc

    def highlight(self, names_or_rings, color, t0, t1=None, proj=merc, peak=0.85, pulse=False, z=4, lw=1.0):
        rings = names_or_rings if names_or_rings and isinstance(names_or_rings[0], np.ndarray) else \
            [r for n in names_or_rings for r in COUNTRIES[n]]
        pc = self.rings(rings, proj, fc=color, ec=color, lw=lw, z=z, alpha=0)
        t1 = self.T + 1 if t1 is None else t1

        def up(t):
            a = min(ease((t - t0) / 0.5), ease((t1 - t) / 0.5)) * peak
            if pulse and t > t0:
                a *= 0.8 + 0.2 * np.cos(2 * np.pi * (t - t0) / 1.6)
            pc.set_alpha(a)
        self.updaters.append(up)
        return pc

    def mover(self, rings, frm, to, t0, t1, color=CYAN, label=None, label_dy=0, ghost=True, z=6,
              appear=None, proj=merc, ghost_color=None, t_hide=None):
        """A country sliding from frm to to (true shape), with an outline ghost left at home."""
        appear = t0 - 0.6 if appear is None else appear
        if ghost:
            gh = PolyCollection([proj(r) for r in rings], facecolors="none", edgecolors=ghost_color or color,
                                linewidths=1.6, linestyles=(0, (4, 3)), zorder=z - 1, alpha=0)
            self.ax.add_collection(gh)
        pc = self.rings(rings, proj, fc=color, ec=WHITE, lw=1.2, z=z, alpha=0)
        lab = None
        if label:
            lab = self.ax.text(0, 0, label, fontproperties=BOLD, size=26, color=WHITE, ha="center",
                               va="center", zorder=z + 1, alpha=0,
                               bbox=dict(boxstyle="round,pad=0.35", fc="#07111d", ec="none", alpha=0))
        state = {"rings": rings}

        def up(t):
            u = ease2((t - t0) / max(t1 - t0, 1e-6))
            rr = move(rings, frm, to, u)
            state["rings"] = rr
            pc.set_verts([proj(r) for r in rr])
            a = ease((t - appear) / 0.5)
            if t_hide is not None:
                a *= ease((t_hide - t) / 0.4)
            pc.set_alpha(0.88 * a)
            if ghost:
                gh.set_alpha(0.9 * ease((t - t0) / 0.6))
            if lab is not None:
                cx = frm[0] + (to[0] - frm[0]) * u
                cy = frm[1] + (to[1] - frm[1]) * u
                p = proj(np.array([[cx, cy]]))[0]
                lab.set_position((p[0], p[1] + label_dy))
                lab.set_alpha(a)
                lab.get_bbox_patch().set_alpha(0.75 * a)
        self.updaters.append(up)
        return pc

    def bars(self, rows, t0, rect=(0.06, 0.12, 0.36, 0.3), xmax=None, t1=None, unit="M km²", title=None,
             stack_last=False, label_left=False, dec=1):
        """rows: list of (label, value, color, t_appear). Horizontal bars that grow in."""
        ax = self.fig.add_axes(rect)
        ax.set_axis_off()
        xmax = xmax or max(r[1] for r in rows) * 1.25
        ax.set_xlim(0, xmax)
        ax.set_ylim(-0.6, len(rows) - 0.4)
        bg = FancyBboxPatch((-0.03, -0.06), 1.06, 1.12 + (0.12 if title else 0), transform=ax.transAxes,
                            boxstyle="round,pad=0,rounding_size=0.04", fc="#07111d", ec="none", alpha=0,
                            clip_on=False, zorder=0)
        ax.add_patch(bg)
        tt = ax.text(0, 1.06, title or "", transform=ax.transAxes, fontproperties=BOLD, size=22, color=MUTED,
                     va="bottom", alpha=0) if title else None
        arts = []
        for i, (lab, val, col, ta) in enumerate(rows):
            y = len(rows) - 1 - i
            if isinstance(val, (list, tuple)):          # stacked segments [(value, color), ...]
                segs, left = [], 0
                for v, cc in val:
                    segs.append((ax.barh(y, 0, left=left, height=0.62, color=cc, zorder=2)[0], left, v))
                    left += v
                total = left
            else:
                segs = [(ax.barh(y, 0, height=0.62, color=col, zorder=2)[0], 0, val)]
                total = val
            if label_left:
                name = ax.text(-xmax * 0.015, y, lab, fontproperties=BOLD, size=22, color=WHITE, va="center",
                               ha="right", alpha=0)
            else:
                name = ax.text(0, y + 0.43, lab, fontproperties=BOLD, size=20, color=WHITE, va="bottom", alpha=0)
            num = ax.text(0, y, "", fontproperties=BOLD, size=22, color=WHITE, va="center", ha="left", alpha=0)
            arts.append((segs, total, name, num, ta))
        t1 = self.T + 1 if t1 is None else t1
        t0 = max(t0, min(a[4] for a in arts) - 0.3)
        if label_left:
            bg.set_bounds(-0.32, -0.05, 1.35, 1.1)

        def up(t):
            fa = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
            bg.set_alpha(0.82 * fa)
            if tt:
                tt.set_alpha(fa)
            for segs, total, name, num, ta in arts:
                g = ease2((t - ta) / 1.0)
                shown = total * g
                for bar, left, v in segs:
                    w = np.clip(shown - left, 0, v)
                    bar.set_width(w)
                    bar.set_alpha(fa)
                name.set_alpha(fa * ease((t - ta) / 0.3))
                num.set_text(f"{shown:,.{dec}f} {unit}")
                num.set_position((shown + xmax * 0.015, num.get_position()[1]))
                num.set_alpha(fa * ease((t - ta) / 0.3))
        self.updaters.append(up)
        return ax

    def graticule(self, proj=merc, step=20, z=0.5, color=GRID, lw=0.8, lat_max=85):
        lines = []
        for lat in np.arange(-80, 81, step):
            lon = np.linspace(-180, 180, 181)
            lines.append(proj(np.column_stack([lon, np.full_like(lon, lat)])))
        for lon in np.arange(-180, 181, step):
            lat = np.linspace(-lat_max, lat_max, 171)
            lines.append(proj(np.column_stack([np.full_like(lat, lon), lat])))
        lc = LineCollection(lines, colors=color, linewidths=lw, zorder=z)
        self.ax.add_collection(lc)
        return lc

    def brand(self):
        self.fig.text(0.985, 0.03, "TRUE SCALE", fontproperties=BOLD, size=18, color=MUTED, ha="right",
                      alpha=0.7, zorder=60)

    def fade_in_out(self, fin=0.5, fout=0.5):
        r = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, color="black", zorder=100, alpha=1)
        self.fig.add_artist(r)

        def up(t):
            r.set_alpha(max(1 - t / fin if fin else 0, (t - (self.T - fout)) / fout if fout else 0, 0))
        self.updaters.append(up)

    def draw(self, t):
        for u in self.updaters:
            u(t)


def build(sid):
    S = Scene(sid)
    EP.scenes[sid](S)
    return S


def render(sid, stills=None):
    S = build(sid)
    os.makedirs(f"{EP.dir}/video", exist_ok=True)
    os.makedirs(f"{EP.dir}/stills", exist_ok=True)
    if stills:
        for t in stills:
            S.draw(t)
            S.fig.savefig(f"{EP.dir}/stills/{sid}_{t:05.1f}.png", dpi=100, facecolor=OCEAN)
        return
    out = f"{EP.dir}/video/{sid}.mp4"
    tmp = f"{EP.dir}/video/{sid}.partial.mp4"
    n = int(round(S.T * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-r", str(FPS), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        S.draw(i / FPS)
        S.fig.canvas.draw()
        p.stdin.write(bytes(S.fig.canvas.buffer_rgba()))
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(f"ffmpeg failed for {sid}")
    os.replace(tmp, out)
    print(f"{sid}: {n} frames, {S.T:.1f}s", flush=True)


