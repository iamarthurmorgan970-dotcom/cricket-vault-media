"""Timelines: a zoomable horizontal time axis with markers, spans and brackets (used in 'The True Scale of History')."""
import math
import numpy as np
from matplotlib.patches import Polygon as MPoly, Circle, FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D
from .core import (BOLD, REG, OCEAN, AMBER, CYAN, PINK, GREEN, VIOLET, WHITE, MUTED, ease, ease2)

AXIS = "#3b5476"
GOLD = "#ffd166"


def yr(y):
    """Year label: negative = BC."""
    y = int(round(y))
    if y == 0:
        return "BC | AD"
    if y < 0:
        return f"{-y:,} BC"
    if y < 1000:
        return f"AD {y}"
    return f"{y}"


class TL:
    """A horizontal timeline drawn in data coords: x = time, y in [-1, 1]."""

    def __init__(self, S, fmt=yr, y=-0.15, ticks=True, nice=None):
        self.S, self.ax, self.fmt, self.y = S, S.ax, fmt, y
        ax = self.ax
        ax.set_ylim(-1, 1)
        self.base = Line2D([0, 1], [y, y], transform=ax.get_yaxis_transform(), color=AXIS, lw=3, zorder=2)
        ax.add_line(self.base)
        self.ticks = []
        self.nice = nice
        if ticks:
            for _ in range(14):
                tl = Line2D([0, 0], [y - 0.03, y + 0.03], color=AXIS, lw=2, zorder=2)
                tx = ax.text(0, y - 0.08, "", fontproperties=REG, size=18, color=MUTED, ha="center", va="top",
                             zorder=2)
                ax.add_line(tl)
                self.ticks.append((tl, tx))
            S.updaters.append(self._ticks)

    def _ticks(self, t):
        x0, x1 = self.ax.get_xlim()
        span = x1 - x0
        steps = self.nice or [1, 2, 5]
        raw = span / 7
        e = math.floor(math.log10(raw))
        cands = [m * 10.0 ** k for k in (e - 1, e, e + 1) for m in steps]
        step = min(cands, key=lambda c: abs(math.log(c / raw)))
        first = math.ceil(x0 / step) * step
        vals = [first + i * step for i in range(len(self.ticks))]
        for (tl, tx), v in zip(self.ticks, vals):
            vis = v <= x1
            tl.set_visible(vis)
            tx.set_visible(vis)
            if vis:
                tl.set_xdata([v, v])
                tx.set_position((v, self.y - 0.08))
                tx.set_text(self.fmt(v))

    def camera(self, keys):
        """keys: (t, center, width); width interpolates in log space so zooms feel even."""
        ax = self.ax

        def up(t):
            if t <= keys[0][0]:
                c, w = keys[0][1:]
            elif t >= keys[-1][0]:
                c, w = keys[-1][1:]
            else:
                for (t0, c0, w0), (t1, c1, w1) in zip(keys, keys[1:]):
                    if t0 <= t <= t1:
                        u = ease2((t - t0) / max(t1 - t0, 1e-6))
                        w = math.exp(math.log(w0) + (math.log(w1) - math.log(w0)) * u)
                        # keep the right edge moving smoothly when zooming towards an end point
                        r0, r1 = c0 + w0 / 2, c1 + w1 / 2
                        c = (r0 + (r1 - r0) * u) - w / 2 if abs(r1 - r0) < 1e-9 else c0 + (c1 - c0) * u
                        break
            ax.set_xlim(c - w / 2, c + w / 2)
            if self.ticks:
                self._ticks(t)
        self.S.updaters.insert(0, up)

    def marker(self, x, label, t0, sub=None, color=AMBER, side=1, h=0.42, size=30, t1=None):
        ax, y = self.ax, self.y
        top = y + side * h
        stem = Line2D([x, x], [y, y], color=color, lw=3, zorder=4, alpha=0)
        ax.add_line(stem)
        dot = ax.scatter([x], [y], s=0, color=color, zorder=5, edgecolors=WHITE, linewidths=2)
        va = "bottom" if side > 0 else "top"
        gap = 0.03 * side
        if sub:
            sub_y, lab_y = (top + gap, top + gap + 0.10) if side > 0 else (top + gap - 0.11, top + gap)
        else:
            lab_y = top + gap
        lab = ax.text(x, lab_y, label, fontproperties=BOLD, size=size, color=WHITE, ha="center", va=va,
                      zorder=6, alpha=0)
        st = ax.text(x, sub_y, sub, fontproperties=BOLD, size=size * 0.7, color=color, ha="center", va=va,
                     zorder=6, alpha=0) if sub else None
        t1 = self.S.T + 1 if t1 is None else t1

        def up(t):
            a = min(ease((t - t0) / 0.4), ease((t1 - t) / 0.4))
            g = ease2((t - t0) / 0.5)
            stem.set_ydata([y, y + (top - y) * g])
            stem.set_alpha(a)
            dot.set_sizes([220 * a])
            xl, xr = ax.get_xlim()
            near = xl - (xr - xl) < x < xr + (xr - xl)       # Agg can't draw glyphs at absurd offsets
            lab.set_alpha(a)
            lab.set_visible(near)
            if st is not None:
                st.set_alpha(a)
                st.set_visible(near)
        self.S.updaters.append(up)
        return lab

    def span(self, x0, x1, row, color, label, t0, dur=1.2, t1=None, h=0.11, size=22, label_inside=False):
        ax = self.ax
        r = Rectangle((x0, row - h / 2), 0, h, color=color, zorder=3, alpha=0)
        ax.add_patch(r)
        lab = ax.text(x0, row + h / 2 + 0.03, label, fontproperties=BOLD, size=size, color=WHITE, ha="left",
                      va="bottom", zorder=6, alpha=0)
        t1 = self.S.T + 1 if t1 is None else t1

        def up(t):
            a = min(ease((t - t0) / 0.3), ease((t1 - t) / 0.4))
            g = ease2((t - t0) / dur)
            r.set_width((x1 - x0) * g)
            r.set_alpha(0.9 * a)
            lab.set_alpha(a)
            # keep the label on screen when the span starts off the left edge
            xl, xr = ax.get_xlim()
            lab.set_x(max(x0, xl + (xr - xl) * 0.01))
            lab.set_visible(x0 + (x1 - x0) * max(g, 0.02) > xl and x0 < xr)
        self.S.updaters.append(up)
        return r

    def bracket(self, x0, x1, row, label, t0, color=CYAN, t1=None, size=34, below=False):
        ax = self.ax
        d = -0.06 if below else 0.06
        ln, = ax.plot([], [], color=color, lw=4, zorder=7, solid_capstyle="round", alpha=0)
        lab = ax.text((x0 + x1) / 2, row + (d * 1.6 if not below else d * 1.6), label, fontproperties=BOLD,
                      size=size, color=color, ha="center", va="bottom" if not below else "top", zorder=8, alpha=0,
                      bbox=dict(boxstyle="round,pad=0.3", fc="#07111d", ec="none", alpha=0))
        t1 = self.S.T + 1 if t1 is None else t1
        m = (x0 + x1) / 2

        def up(t):
            a = min(ease((t - t0) / 0.3), ease((t1 - t) / 0.4))
            g = ease2((t - t0) / 0.9)
            l, r = m - (m - x0) * g, m + (x1 - m) * g
            ln.set_data([l, l, r, r], [row - d, row, row, row - d])
            ln.set_alpha(a)
            xl, xr = ax.get_xlim()
            lab.set_visible(xl - (xr - xl) < m < xr + (xr - xl))
            lab.set_alpha(a * ease((t - t0 - 0.5) / 0.4))
            lab.get_bbox_patch().set_alpha(0.75 * a * ease((t - t0 - 0.5) / 0.4))
        self.S.updaters.append(up)


def setup(S):
    S.ax.set_facecolor(OCEAN)
    S.brand()




def ma(x):
    return f"{-x:,.0f}M yrs ago" if x < -0.5 else "TODAY"


MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
CUM = np.cumsum([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])


def day_fmt(v):
    m = int(np.searchsorted(CUM, v, side="right") - 1)
    m = min(max(m, 0), 11)
    d = int(v - CUM[m]) + 1
    return f"{d} {MONTHS[m]}" if d != 1 else MONTHS[m]


def hms(v):
    """v = seconds before midnight (negative)."""
    s = 86400 + v
    h, m, sec = int(s // 3600), int(s % 3600 // 60), s % 60
    return f"{h:02d}:{m:02d}:{sec:02.0f}" if h < 24 else "MIDNIGHT"


