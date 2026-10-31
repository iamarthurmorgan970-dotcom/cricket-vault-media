#!/usr/bin/env python3
"""
cricket_videos.py - turn free Cricsheet ball-by-ball data into cricket stat videos
for YouTube. Shorts (9:16, 1080x1920) by default; add --format long for 16:9.

WHAT IT MAKES
  worm     Animated match "worm" for one match: live score, wickets, "need X off Y".
  race     Bar-chart race of all-time leaders: runs, wickets, sixes or fours.
  player   One player's career, innings by innings, with live stat counters.
  compare  Two players head to head after the same number of innings ("Kohli vs Babar
           after 137 ODI innings") - the format breaking out on cricket Shorts right now.
  helpers: matches = list match IDs, find = look up a player's exact Cricsheet name.

SETUP (once)
  1. Install Python 3.9+ from python.org (on Windows tick "Add python.exe to PATH").
  2. In a terminal:   pip install matplotlib imageio-ffmpeg
  3. Download data in JSON format from https://cricsheet.org/downloads/
     (e.g. the IPL zip, T20 internationals, ODIs, or "recently played").
     Point this script at the .zip itself - no need to unzip.

EXAMPLES (replace ipl_json.zip with your file's actual name)
  python cricket_videos.py matches ipl_json.zip --last 10
  python cricket_videos.py worm    ipl_json.zip --match 1426312 --handle @YourChannel
  python cricket_videos.py race    ipl_json.zip --metric sixes --handle @YourChannel
  python cricket_videos.py find    ipl_json.zip kohli
  python cricket_videos.py player  ipl_json.zip --name "V Kohli" --handle @YourChannel
  python cricket_videos.py compare all_json.zip --match-type ODI --a "V Kohli" --b "Babar Azam"
  python cricket_videos.py compare all_json.zip --match-type Test --metric wickets --per match \
                                   --a "JJ Bumrah" --b "MA Starc"

USEFUL OPTIONS (any video command)
  --format long        16:9 for normal videos (default: short, for Shorts)
  --still              save only the final frame as a PNG (quick check / thumbnail)
  --seconds 30         length of the animated part (plus a short hold at each end)
  --title "..."        your own headline instead of the automatic one
  --no-sound           skip the built-in original music and sound effects
  --event "Premier"    keep only matches whose event name contains this text
  --match-type T20     T20, IT20, ODI, ODM, Test or MDM
  --since 2020 --until 2024-05-31     date range (year or full date)
  --team "India"       keep only matches involving this team
  --gender male|female
  --team-type international      only internationals (club = leagues such as the IPL)

Cricsheet data is free to use with credit; every video carries "Data: cricsheet.org".
"""
import argparse
import glob
import json
import math
import os
import shutil
import subprocess
import sys
import textwrap
import zipfile
import zlib
from collections import Counter, defaultdict
from datetime import datetime

try:
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import MaxNLocator, MultipleLocator
    from matplotlib.transforms import blended_transform_factory
except ImportError:
    sys.exit("Missing libraries. Run:  pip install matplotlib imageio-ffmpeg")

# --------------------------------------------------------------------------- look
BG = "#0d0d0d"        # frame background
INK = "#f0efec"       # primary text
INK2 = "#c3c2b7"      # secondary text
MUTED = "#898781"     # axis labels, credits
GRID = "#2c2c2a"      # gridlines
AXIS = "#383835"      # baseline
BLUE = "#3987e5"      # series 1 (colour-blind-safe pair with ORANGE on dark)
ORANGE = "#d95926"    # series 2 / highlight

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Helvetica Neue", "Arial", "Liberation Sans", "DejaVu Sans"],
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": INK, "axes.edgecolor": AXIS, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED,
})

FPS = 30
FORMATS = {"short": (1080, 1920), "long": (1920, 1080)}

# Short names for scoreboards. Anything not listed and longer than 12 letters
# becomes its initials. Add your own with --abbr "Team Name=ABC".
ABBR = {
    "Chennai Super Kings": "CSK", "Mumbai Indians": "MI", "Kolkata Knight Riders": "KKR",
    "Royal Challengers Bangalore": "RCB", "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad": "SRH", "Delhi Capitals": "DC", "Delhi Daredevils": "DD",
    "Punjab Kings": "PBKS", "Kings XI Punjab": "KXIP", "Rajasthan Royals": "RR",
    "Gujarat Titans": "GT", "Lucknow Super Giants": "LSG", "Deccan Chargers": "DCH",
    "Gujarat Lions": "GL", "Pune Warriors": "PWI", "Kochi Tuskers Kerala": "KTK",
    "Rising Pune Supergiant": "RPS", "Rising Pune Supergiants": "RPS",
}

BOWLER_WICKETS = {"bowled", "caught", "lbw", "stumped", "caught and bowled", "hit wicket"}
NOT_OUT_KINDS = {"retired hurt", "retired not out"}


# --------------------------------------------------------------------------- data
def iter_matches(source, quiet=False):
    """Yield (match_id, match_dict) from a Cricsheet .zip, a folder of .json files, or one .json."""
    def load(fh, name):
        try:
            return json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"  skipping unreadable file {name}", file=sys.stderr)
            return None

    def stem(name):
        return os.path.splitext(os.path.basename(name))[0]

    if not os.path.exists(source):
        sys.exit(f"Can't find '{source}'. Check the file name and folder.")
    if os.path.isdir(source):
        names = sorted(glob.glob(os.path.join(source, "*.json")))
        opener = lambda n: open(n, encoding="utf-8")
        z = None
    elif source.lower().endswith(".zip"):
        z = zipfile.ZipFile(source)
        names = sorted(n for n in z.namelist() if n.lower().endswith(".json"))
        opener = z.open
    elif source.lower().endswith(".json"):
        names, z = [source], None
        opener = lambda n: open(n, encoding="utf-8")
    else:
        sys.exit("Give a Cricsheet .zip, a folder of .json files, or a single match .json file.")
    if not names:
        sys.exit(f"No .json match files found in '{source}'. Download the JSON version from cricsheet.org.")
    for i, n in enumerate(names, 1):
        if not quiet and len(names) > 500 and i % 2000 == 0:
            print(f"  read {i:,} of {len(names):,} matches...", file=sys.stderr)
        with opener(n) as fh:
            m = load(fh, n)
        if isinstance(m, dict) and "info" in m:
            yield stem(n), m
    if z:
        z.close()


def load_one_match(args):
    src = args.data
    if src.lower().endswith(".json") and os.path.isfile(src):
        return next(iter_matches(src, quiet=True))
    if not args.match:
        sys.exit("Add --match ID (find IDs with the 'matches' command), or pass one match .json file.")
    want = f"{args.match}.json"
    if os.path.isdir(src):
        path = os.path.join(src, want)
        if not os.path.isfile(path):
            sys.exit(f"No match {args.match} in that folder.")
        return next(iter_matches(path, quiet=True))
    with zipfile.ZipFile(src) as z:
        hits = [n for n in z.namelist() if os.path.basename(n) == want]
        if not hits:
            sys.exit(f"No match {args.match} in that zip. Run the 'matches' command to see IDs.")
        with z.open(hits[0]) as fh:
            return str(args.match), json.load(fh)


def deliveries(inn):
    for ov in inn.get("overs", []):
        for d in ov.get("deliveries", []):
            yield d


def batter_of(d):
    return d.get("batter") or d.get("batsman")


def is_legal(d):
    ex = d.get("extras", {})
    return "wides" not in ex and "noballs" not in ex


def match_date(info):
    ds = info.get("dates") or ["0000-00-00"]
    return str(ds[0])


def event_name(info):
    ev = info.get("event")
    return (ev.get("name", "") if isinstance(ev, dict) else str(ev or "")).strip()


def match_ok(info, a):
    if a.event and a.event.lower() not in event_name(info).lower():
        return False
    if a.match_type and str(info.get("match_type", "")).lower() != a.match_type.lower():
        return False
    if a.gender and info.get("gender", "") != a.gender:
        return False
    if getattr(a, "team_type", None) and info.get("team_type", "") != a.team_type:
        return False
    if a.team and a.team.lower() not in [t.lower() for t in info.get("teams", [])]:
        return False
    d = match_date(info)
    if a.since and d[:len(a.since)] < a.since:
        return False
    if a.until and d[:len(a.until)] > a.until:
        return False
    return True


def result_text(info):
    o = info.get("outcome", {})
    elim = o.get("eliminator")
    if "winner" in o:
        by, w = o.get("by", {}), o["winner"]
        if "innings" in by:
            s = f"{w} won by an innings and {by.get('runs', 0)} runs"
        elif "runs" in by:
            s = f"{w} won by {by['runs']} run{'s' if by['runs'] != 1 else ''}"
        elif "wickets" in by:
            s = f"{w} won by {by['wickets']} wicket{'s' if by['wickets'] != 1 else ''}"
        else:
            s = f"{w} won"
        if o.get("method"):
            s += f" ({o['method']})"
        return s
    r = o.get("result", "")
    if r == "tie":
        return f"Match tied - {elim} won the Super Over" if elim else "Match tied"
    if r == "draw":
        return "Match drawn"
    if r == "no result":
        return "No result"
    return ""


def pretty_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d %b %Y").lstrip("0")
    except ValueError:
        return d


def month_year(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%b %Y")
    except ValueError:
        return d[:4]


def parse_abbr(pairs):
    out = {}
    for p in pairs or []:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def short_team(team, extra):
    if team in extra:
        return extra[team]
    if team in ABBR:
        return ABBR[team]
    if len(team) <= 12:
        return team
    return "".join(w[0] for w in team.split() if w[:1].isalpha()).upper()


# --------------------------------------------------------------------------- canvas
class Layout:
    def __init__(self, fmt):
        self.fmt = fmt
        self.W, self.H = FORMATS[fmt]
        short = fmt == "short"
        self.mx = 0.075 if short else 0.05          # side margin (fraction of width)
        self.top = 0.935 if short else 0.92
        self.wrap = 22 if short else 40             # title characters per line
        self.title_size = 50 if short else 46
        self.sub_size = 24 if short else 22
        # Shorts: keep the bottom ~22% and the right edge clear of YouTube's own buttons/caption
        self.plot_bottom = 0.315 if short else 0.11
        self.plot_right = 0.86 if short else 0.95
        self.footer_y = 0.245 if short else 0.925

    def px(self, n):      # vertical pixels -> figure fraction
        return n / self.H

    def pxx(self, n):     # horizontal pixels -> figure fraction
        return n / self.W

    def pt(self, size):   # font points -> figure-height fraction
        return size * 100 / 72 / self.H


def new_figure(L):
    return plt.figure(figsize=(L.W / 100, L.H / 100), dpi=100)


def wrap_parts(text, width, sep=" · "):
    """Wrap a 'a · b · c' line, breaking between parts where possible."""
    lines, cur = [], ""
    for part in text.split(sep):
        cand = f"{cur}{sep}{part}" if cur else part
        if len(cand) <= width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = part
    lines.append(cur)
    return "\n".join(textwrap.fill(l, width) for l in lines)


def draw_header(fig, L, title, subtitle, width=None):
    """Draw title + subtitle from the top; return the y (figure fraction) just below them."""
    t = textwrap.fill(title, width or L.wrap)
    lines = t.count("\n") + 1
    fig.text(L.mx, L.top, t, size=L.title_size, weight="bold", color=INK, va="top", linespacing=1.12)
    y = L.top - L.pt(L.title_size) * (1.22 * lines) - L.px(10)
    if subtitle:
        s = wrap_parts(subtitle, int((width or L.wrap) * L.title_size / L.sub_size * 0.95))
        n = s.count("\n") + 1
        fig.text(L.mx, y, s, size=L.sub_size, color=INK2, va="top", linespacing=1.3)
        y -= L.pt(L.sub_size) * 1.3 * n
    return y


def draw_footer(fig, L, handle):
    """Shorts: bottom-left, above YouTube's caption overlay. Long-form: top-right corner."""
    y = L.footer_y
    x, ha = (L.mx, "left") if L.fmt == "short" else (1 - L.mx, "right")
    if handle:
        fig.text(x, y, handle, size=26, weight="bold", color=INK2, va="bottom", ha=ha)
        y -= L.px(8)
    fig.text(x, y, "Data: cricsheet.org", size=17, color=MUTED, va="top", ha=ha)


def style_axes(ax, size=20):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["bottom"].set_linewidth(1.5)
    ax.tick_params(axis="both", labelsize=size, length=0, pad=10)
    ax.grid(axis="y", color=GRID, linewidth=1.2)
    ax.set_axisbelow(True)


# --------------------------------------------------------------------------- video output
def find_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        exe = shutil.which("ffmpeg")
        if exe:
            return exe
    sys.exit("ffmpeg not found. Run:  pip install imageio-ffmpeg")


class Video:
    """Streams raw frames from the matplotlib canvas into ffmpeg (H.264 MP4)."""

    def __init__(self, path, fig):
        self.path, self.fig = path, fig
        w, h = fig.canvas.get_width_height()
        root, _ = os.path.splitext(path)
        self.tmp = root + ".partial.mp4"
        cmd = [find_ffmpeg(), "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", self.tmp]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def frame(self, repeat=1):
        self.fig.canvas.draw()
        data = bytes(self.fig.canvas.buffer_rgba())
        try:
            for _ in range(max(1, repeat)):
                self.proc.stdin.write(data)
        except BrokenPipeError:
            sys.exit("ffmpeg stopped unexpectedly - the video was not written.")

    def close(self):
        self.proc.stdin.close()
        if self.proc.wait() != 0:
            sys.exit("ffmpeg failed - the video was not written.")
        os.replace(self.tmp, self.path)


# --------------------------------------------------------------------------- sound
# An original backing track and sound effects, synthesised here so every video is
# royalty-free. The seed (from the file name) varies key and tempo between videos.
SR = 44100
PROGRESSIONS = [  # (bass roots, pad chords) in Hz
    ([110.0, 87.31, 130.81, 98.0],    # Am F C G
     [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]]),
    ([146.83, 116.54, 87.31, 130.81],  # Dm Bb F C
     [[293.66, 349.23, 440.0], [233.08, 293.66, 349.23], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0]]),
    ([82.41, 130.81, 98.0, 146.83],    # Em C G D
     [[329.63, 392.0, 493.88], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66], [293.66, 369.99, 440.0]]),
]


def _secs(sec):
    return np.arange(int(sec * SR)) / SR


def _filt(x, lo=None, hi=None):
    """Gentle high-pass (lo) and/or low-pass (hi), done in the frequency domain."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9
    if hi:
        X *= 1 / (1 + (f / hi) ** 4)
    if lo:
        X *= (f / lo) ** 4 / (1 + (f / lo) ** 4)
    return np.fft.irfft(X, len(x))


def _saw(freq, t, detune=0.0):
    return 2 * ((freq * (1 + detune) * t) % 1.0) - 1


def _sweep(t, f_end, f_extra, tau):
    f = f_end + f_extra * np.exp(-t / tau)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def _kick(rng):
    t = _secs(0.45)
    click = _filt(rng.standard_normal(len(t)), lo=1500) * np.exp(-t / 0.004) * 0.25
    return _sweep(t, 48, 90, 0.035) * np.exp(-t / 0.2) + click


def _snare(rng):
    t = _secs(0.3)
    noise = _filt(rng.standard_normal(len(t)), lo=1200, hi=9000) * np.exp(-t / 0.09) * 0.55
    return noise + np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.06) * 0.45


def _hat(rng):
    t = _secs(0.08)
    return _filt(rng.standard_normal(len(t)), lo=7000) * np.exp(-t / 0.018) * 0.22


def _bass(freq, dur):
    t = _secs(dur)
    x = _saw(freq, t) * 0.6 + np.sin(2 * np.pi * freq * t) * 0.6
    env = np.minimum(1, t / 0.005) * (0.35 + 0.65 * np.exp(-t / 0.12)) * np.clip((dur - t) / 0.02, 0, 1)
    return _filt(x, hi=900) * env


def _pad(freqs, dur):
    t = _secs(dur)
    x = sum(_saw(f, t, d) for f in freqs for d in (-0.004, 0.0, 0.004)) / (3 * len(freqs))
    env = np.minimum(1, t / 0.25) * np.clip((dur - t) / 0.3, 0, 1)
    return _filt(x, hi=1800) * env


def _pluck(freq, dur):
    t = _secs(dur)
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) + 0.15 * _saw(freq, t)
    return x * np.minimum(1, t / 0.003) * np.exp(-t / 0.13)


def _whoosh(rng, dur=0.7):
    t = _secs(dur)
    n = rng.standard_normal(len(t))
    rise = t / dur
    x = _filt(n, lo=300, hi=1500) * (1 - rise) + _filt(n, lo=2500, hi=8000) * rise
    return x * np.sin(np.pi * t / dur) ** 2


def _impact(rng):
    t = _secs(1.8)
    boom = _sweep(t, 55, 70, 0.05) * np.exp(-t / 0.35)
    ding = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1318.5, 0.5), (1975.5, 0.25), (2637.0, 0.2)))
    noise = _filt(rng.standard_normal(len(t)), lo=800) * np.exp(-t / 0.05) * 0.5
    return boom + ding * np.exp(-t / 0.6) * 0.5 + noise


def _wicket(rng):
    t = _secs(0.35)
    crack = _filt(rng.standard_normal(len(t)), lo=2000) * np.exp(-t / 0.01) * 0.6
    return _sweep(t, 140, 160, 0.02) * np.exp(-t / 0.12) * 0.8 + crack


def make_soundtrack(total, intro, anim_end, hits, seed):
    """Stereo float array: groove while the chart animates, impact on the final reveal."""
    rng = np.random.default_rng(seed)
    roots, chords = PROGRESSIONS[seed % len(PROGRESSIONS)]
    beat = 60 / (112, 118, 124)[(seed // 3) % 3]
    bar = 4 * beat
    n = int((total + 2) * SR)
    music, sfx = np.zeros(n), np.zeros(n)

    def put(buf, x, at, gain=1.0):
        i = int(at * SR)
        if 0 <= i < len(buf):
            j = min(len(buf), i + len(x))
            buf[i:j] += x[:j - i] * gain

    kick, snare, hat = _kick(rng), _snare(rng), _hat(rng)
    pads = [_pad(c, bar + 0.3) for c in chords]
    cache = {}
    for b in range(int(np.ceil(total / bar)) + 1):
        t0, k = b * bar, b % 4
        put(music, pads[k], t0, 0.5)
        for s in range(8):                                   # eighth notes
            ts = t0 + s * beat / 2
            if ts < intro - 0.05 or ts >= anim_end:          # groove only while the chart moves
                continue
            mult = 2 if s in (3, 6) else 1
            key = ("b", k, mult)
            if key not in cache:
                cache[key] = _bass(roots[k] * mult, beat / 2 * 0.9)
            put(music, cache[key], ts, 0.5)
            put(music, hat, ts, 0.5 if s % 2 else 0.8)
            if s in (0, 4) or (s == 7 and b % 2):
                put(music, kick, ts, 0.9)
            if s in (2, 6):
                put(music, snare, ts, 0.7)
            tone = chords[k][(0, 1, 2, 1)[s % 4]] * 2
            if ("p", tone) not in cache:
                cache[("p", tone)] = _pluck(tone, beat / 2)
            put(music, cache[("p", tone)], ts, 0.18)
    t = np.arange(n) / SR
    music *= np.clip(t / 0.3, 0, 1) * np.clip((total - t) / 1.5, 0, 1)
    music *= 0.12 / (np.sqrt(np.mean(music[:int(total * SR)] ** 2)) + 1e-9)
    put(sfx, _whoosh(rng), max(0.0, intro - 0.55), 0.35)
    put(sfx, _impact(rng), anim_end, 0.45)
    for h in hits:
        put(sfx, _wicket(rng), h, 0.3)
    mix = np.tanh(1.4 * (music + sfx)) / np.tanh(1.4)       # soft limiter
    return np.stack([mix, mix], axis=1)


def add_soundtrack(path, total, intro, anim_end, hits, seed):
    import wave
    audio = make_soundtrack(total, intro, anim_end, hits, seed)
    root = os.path.splitext(path)[0]
    wav, tmp = root + ".audio.wav", root + ".sound.mp4"
    with wave.open(wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(audio, -1, 1) * 32000).astype("<i2").tobytes())
    cmd = [find_ffmpeg(), "-y", "-loglevel", "error", "-i", path, "-i", wav, "-map", "0:v", "-map", "1:a",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", tmp]
    ok = subprocess.run(cmd).returncode == 0
    os.remove(wav)
    if not ok:
        sys.exit("Adding sound failed - the silent video is still there.")
    os.replace(tmp, path)


def render(fig, update, args, default_name, intro=1.0, outro=4.0, events=()):
    """events: animation progress points (0-1) that get a hit sound, e.g. wickets."""
    out = args.out or default_name
    if args.still:
        update(1.0)
        png = os.path.splitext(out)[0] + ".png"
        fig.savefig(png, dpi=100)
        print(f"Saved {png}")
        return
    n = max(2, round(args.seconds * FPS))
    v = Video(out, fig)
    update(0.0)
    v.frame(repeat=round(intro * FPS))
    step = max(1, n // 10)
    for i in range(1, n + 1):
        update(i / n)
        v.frame()
        if i % step == 0:
            print(f"  rendering... {100 * i // n}%", file=sys.stderr)
    v.frame(repeat=round(outro * FPS))
    v.close()
    total = (n + round(intro * FPS) + round(outro * FPS)) / FPS
    if not getattr(args, "no_sound", False):
        start = round(intro * FPS) / FPS
        add_soundtrack(out, total, start, start + n / FPS, [start + p * n / FPS for p in events],
                       zlib.crc32(os.path.basename(out).encode()))
    print(f"Saved {out}  ({total:.0f} s, {FORMATS[args.format][0]}x{FORMATS[args.format][1]})")


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in s).strip("_").lower()[:40]


# --------------------------------------------------------------------------- worm
def fmt_overs(legal, bpo):
    o, b = divmod(legal, bpo)
    return f"{o}" if b == 0 else f"{o}.{b}"


def ordinal(n):
    n = int(n)
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def write_facts(a, facts):
    """--facts FILE: save the numbers behind a video, so captions can be written from them."""
    if getattr(a, "facts", None):
        with open(a.facts, "w", encoding="utf-8") as fh:
            json.dump(facts, fh, indent=2, ensure_ascii=False)


def innings_card(inn, bpo):
    bat, bowl = {}, {}
    runs = wk = legal = 0
    for d in deliveries(inn):
        r, ex = d.get("runs", {}), d.get("extras", {})
        b, bw = batter_of(d), d.get("bowler")
        bat.setdefault(b, [0, 0])
        bat[b][0] += r.get("batter", 0)
        if "wides" not in ex:
            bat[b][1] += 1
        bowl.setdefault(bw, [0, 0])
        bowl[bw][1] += r.get("total", 0) - ex.get("byes", 0) - ex.get("legbyes", 0) - ex.get("penalty", 0)
        runs += r.get("total", 0)
        if is_legal(d):
            legal += 1
        for w in d.get("wickets", []):
            if w.get("kind") not in NOT_OUT_KINDS:
                wk += 1
            if w.get("kind") in BOWLER_WICKETS:
                bowl[bw][0] += 1
    top_bat = sorted(bat.items(), key=lambda kv: (-kv[1][0], kv[1][1]))[:2]
    top_bowl = sorted(bowl.items(), key=lambda kv: (-kv[1][0], kv[1][1]))[:2]
    return dict(team=inn.get("team", ""), runs=runs, wickets=wk, legal_balls=legal, overs=fmt_overs(legal, bpo),
                declared=bool(inn.get("declared")),
                top_batters=[dict(name=n, runs=v[0], balls=v[1]) for n, v in top_bat],
                top_bowlers=[dict(name=n, wickets=v[0], conceded=v[1]) for n, v in top_bowl])


def match_facts(m):
    """Plain facts about one match: scores, best performers, how the chase went."""
    info = m.get("info", {})
    bpo = info.get("balls_per_over", 6)
    inns = [i for i in m.get("innings", []) if not i.get("super_over") and i.get("overs")]
    cards = [innings_card(i, bpo) for i in inns]
    ev = info.get("event") if isinstance(info.get("event"), dict) else {}
    mt = info.get("match_type", "")
    intl = info.get("team_type") == "international"
    facts = dict(kind="worm", date=match_date(info), event=event_name(info), match_number=ev.get("match_number"),
                 format={"T20": "T20I" if intl else "T20"}.get(mt, mt), match_type=mt,
                 team_type=info.get("team_type", ""), gender=info.get("gender", ""), venue=info.get("venue", ""),
                 city=info.get("city", ""), teams=info.get("teams", []), result=result_text(info),
                 outcome=info.get("outcome", {}), player_of_match=info.get("player_of_match", []),
                 super_over=any(i.get("super_over") for i in m.get("innings", [])), innings=cards)
    if info.get("overs") and len(inns) >= 2:
        tg = inns[1].get("target", {})
        target = tg.get("runs") or cards[0]["runs"] + 1
        tov = float(tg.get("overs") or info["overs"])
        whole = int(tov)
        target_balls = whole * bpo + round((tov - whole) * 10)
        last = inns[1]["overs"][-1]
        before_last = cards[1]["runs"] - sum(d.get("runs", {}).get("total", 0) for d in last.get("deliveries", []))
        chased = cards[1]["runs"] >= target
        facts["chase"] = dict(target=target, target_balls=target_balls,
                              final_over_reached=last.get("over") == math.ceil(target_balls / bpo) - 1,
                              needed_in_final_over=target - before_last,
                              chased=chased,
                              balls_to_spare=target_balls - cards[1]["legal_balls"] if chased else None)
    return facts


def cmd_worm(a):
    mid, m = load_one_match(a)
    info = m.get("info", {})
    bpo = info.get("balls_per_over", 6)
    inns = [i for i in m.get("innings", []) if not i.get("super_over") and i.get("overs")]
    if not inns:
        sys.exit("This match has no ball-by-ball innings to draw (abandoned?).")
    extra = parse_abbr(a.abbr)

    order = []
    for i in inns:
        if i["team"] not in order:
            order.append(i["team"])
    for t in info.get("teams", []):
        if t not in order:
            order.append(t)
    colour = {t: (BLUE, ORANGE)[k % 2] for k, t in enumerate(order[:2])}

    series = []
    for inn in inns:
        legal = runs = wk = 0
        xs, ys, st, wk_idx = [0.0], [0], [(0, 0, 0)], []
        for d in deliveries(inn):
            runs += d.get("runs", {}).get("total", 0)
            if is_legal(d):
                legal += 1
            out = sum(1 for w in d.get("wickets", []) if w.get("kind") not in NOT_OUT_KINDS)
            wk += out
            xs.append(legal / bpo)
            ys.append(runs)
            st.append((legal, runs, wk))
            if out:
                wk_idx.append(len(xs) - 1)
        series.append(dict(team=inn["team"], xs=np.array(xs), ys=np.array(ys), st=st, wk=wk_idx,
                           declared=bool(inn.get("declared")),
                           repeat=any(s["team"] == inn["team"] for s in series)))

    limited = bool(info.get("overs"))
    target = target_balls = None
    if limited and len(series) >= 2:
        tg = inns[1].get("target", {})
        target = tg.get("runs") or int(series[0]["ys"][-1]) + 1
        tov = tg.get("overs") or info["overs"]
        whole = int(tov)
        target_balls = whole * bpo + round((float(tov) - whole) * 10)

    # ---- figure
    L = Layout(a.format)
    fig = new_figure(L)
    t1 = short_team(order[0], extra)
    t2 = short_team(order[1], extra) if len(order) > 1 else ""
    title = a.title or (f"{t1} vs {t2}" if t2 else t1)
    bits = [event_name(info)]
    mn = info.get("event", {}).get("match_number") if isinstance(info.get("event"), dict) else None
    if mn:
        bits[0] += f", Match {mn}"
    bits += [pretty_date(match_date(info)), info.get("venue", "")]
    sub = a.subtitle or " · ".join(b for b in bits if b)
    y = draw_header(fig, L, title, sub)
    draw_footer(fig, L, a.handle)

    # scoreboard rows (they double as the legend: colour chip = team)
    y -= L.px(34)
    row_h = L.px(66)
    board = {}
    for k, team in enumerate(order[:2]):
        yy = y - k * row_h
        fig.add_artist(Rectangle((L.mx, yy - L.px(13)), L.pxx(26), L.px(26),
                                 transform=fig.transFigure, color=colour[team], lw=0))
        name = team if len(team) <= (18 if a.format == "short" else 30) else short_team(team, extra)
        fig.text(L.mx + L.pxx(44), yy, name, size=34, weight="bold", color=INK, va="center")
        sc = fig.text(1 - L.mx - L.pxx(150), yy, "", size=34, weight="bold", color=INK,
                      va="center", ha="right")
        ov = fig.text(1 - L.mx - L.pxx(132), yy, "", size=24, color=MUTED, va="center")
        board[team] = (sc, ov)
    y -= (len(board) - 1) * row_h + L.px(64)
    situation = fig.text(L.mx, y, "", size=30, color=INK2, va="center")

    top = y - L.px(120)
    left = L.mx + (L.pxx(70) if a.format == "short" else L.pxx(60))
    ax = fig.add_axes([left, L.plot_bottom, L.plot_right - left, top - L.plot_bottom])
    style_axes(ax)
    xmax = float(info["overs"]) if limited else max(float(s["xs"][-1]) for s in series)
    ymax = max(float(s["ys"].max()) for s in series)
    if target:
        ymax = max(ymax, target)
    ax.set_xlim(0, xmax * 1.02)
    ax.set_ylim(0, ymax * 1.1)
    ax.xaxis.set_major_locator(MultipleLocator(5 if xmax <= 20 else 10 if xmax <= 50 else 20))
    ax.yaxis.set_major_locator(MaxNLocator(5, integer=True))
    ax.set_xlabel("Overs", size=20, labelpad=12)
    ax.text(0, 1.03, "Runs", transform=ax.transAxes, size=20, color=MUTED, va="bottom")
    ax.text(1, 1.03, "●  wicket", transform=ax.transAxes, size=20, color=MUTED, va="bottom", ha="right")

    tline = tlabel = None
    if target:
        tline = ax.axhline(target, color=MUTED, lw=1.6, ls=(0, (6, 4)), visible=False)
        tlabel = ax.text(0.01, target, f" Target {target}", transform=blended_transform_factory(ax.transAxes, ax.transData),
                         size=20, color=MUTED, va="bottom", visible=False)

    for s in series:
        c = colour.get(s["team"], INK2)
        ls = (0, (5, 3)) if s["repeat"] else "-"
        s["line"], = ax.plot([], [], color=c, lw=3.6, ls=ls, solid_capstyle="round", zorder=3)
        s["wk_dots"], = ax.plot([], [], "o", ms=11, mfc=c, mec=BG, mew=2.5, zorder=4)
        s["head"], = ax.plot([], [], "o", ms=17, mfc=INK, mec=c, mew=3.5, zorder=5)

    lens = [len(s["xs"]) - 1 for s in series]
    starts = np.cumsum([0] + lens[:-1])
    total = sum(lens)
    result = result_text(info)

    def team_score(team, shown):
        parts, last_legal = [], None
        for s, n in zip(series, shown):
            if s["team"] != team or n < 0:
                continue
            legal, runs, wk = s["st"][n]
            txt = f"{runs}" if wk >= 10 else f"{runs}/{wk}"
            if s["declared"] and n == len(s["st"]) - 1:
                txt += "d"
            parts.append(txt)
            last_legal = legal
        if not parts:
            return "", ""
        return " & ".join(parts), f"({fmt_overs(last_legal, bpo)} ov)"

    def update(t):
        done = t * total
        shown, cur = [], 0
        for i, s in enumerate(series):
            if done <= starts[i] and i > 0:
                shown.append(-1)
                n = -1
            else:
                n = int(min(lens[i], max(0, done - starts[i])))
                shown.append(n)
                cur = i
            if n < 0:
                s["line"].set_data([], [])
                s["wk_dots"].set_data([], [])
                s["head"].set_data([], [])
                continue
            s["line"].set_data(s["xs"][:n + 1], s["ys"][:n + 1])
            w = [j for j in s["wk"] if j <= n]
            s["wk_dots"].set_data(s["xs"][w], s["ys"][w])
            s["head"].set_data([], [])
        hs = series[cur]
        n = shown[cur]
        hs["head"].set_data([hs["xs"][n]], [hs["ys"][n]])
        for team, (sc, ov) in board.items():
            a_, b_ = team_score(team, shown)
            sc.set_text(a_ or "Yet to bat")
            sc.set_color(INK if a_ else MUTED)
            sc.set_size(34 if a_ else 26)
            ov.set_text(b_)
        if tline is not None:
            vis = cur >= 1
            tline.set_visible(vis)
            tlabel.set_visible(vis)
        legal, runs, wk = hs["st"][n]
        if t >= 1 and result:
            situation.set_text(result)
            situation.set_color(INK)
            situation.set_weight("bold")
        elif limited and cur == 1 and target:
            need, left_b = target - runs, target_balls - legal
            situation.set_text("Target reached" if need <= 0 else
                               f"Need {need} off {left_b} ball{'s' if left_b != 1 else ''}")
        elif cur == 0:
            rr = runs / (legal / bpo) if legal else 0.0
            situation.set_text(f"Run rate {rr:.2f}")
        else:
            situation.set_text(f"{ordinal(cur + 1)} innings")

    hits = [(starts[i] + j) / total for i, s in enumerate(series) for j in s["wk"]]
    write_facts(a, dict(match_facts(m), match_id=mid, on_screen_title=title))
    render(fig, update, a, f"worm_{mid}_{a.format}.mp4", events=hits)


# --------------------------------------------------------------------------- race
METRIC_WORD = {"runs": "runs", "wickets": "wickets", "sixes": "sixes", "fours": "fours"}


def match_values(m, metric):
    vals = Counter()
    for inn in m.get("innings", []):
        if inn.get("super_over"):
            continue
        for d in deliveries(inn):
            if metric == "wickets":
                for w in d.get("wickets", []):
                    if w.get("kind") in BOWLER_WICKETS and d.get("bowler"):
                        vals[d["bowler"]] += 1
                continue
            b = batter_of(d)
            if not b:
                continue
            r = d.get("runs", {})
            rb = r.get("batter", 0)
            if metric == "runs":
                vals[b] += rb
            elif metric == "sixes" and rb == 6 and not r.get("non_boundary"):
                vals[b] += 1
            elif metric == "fours" and rb == 4 and not r.get("non_boundary"):
                vals[b] += 1
    return vals


def cmd_race(a):
    rows, events, types = [], Counter(), Counter()
    for mid, m in iter_matches(a.data):
        info = m["info"]
        if not match_ok(info, a):
            continue
        rows.append((match_date(info), mid, match_values(m, a.metric)))
        events[event_name(info)] += 1
        types[info.get("match_type", "")] += 1
    if len(rows) < 2:
        sys.exit("Fewer than 2 matches left after your filters - loosen them.")
    rows.sort(key=lambda r: (r[0], r[1]))
    n = len(rows)
    top = a.top

    K = int(min(n, max(4, round(a.seconds * 2))))          # ~2 steps per second
    edges = np.linspace(0, n, K + 1).round().astype(int)
    names = sorted({p for _, _, v in rows for p in v})
    col = {p: i for i, p in enumerate(names)}
    inc = np.zeros((K + 1, len(names)))
    for k in range(K):
        for _, _, v in rows[edges[k]:edges[k + 1]]:
            for p, x in v.items():
                inc[k + 1, col[p]] += x
    cum = np.cumsum(inc, axis=0)

    rank = np.full(cum.shape, top + 1.0)
    idx = np.arange(len(names))
    for k in range(K + 1):
        order = np.lexsort((idx, -cum[k]))[:top + 1]
        for r, p in enumerate(order):
            if cum[k, p] > 0:
                rank[k, p] = r + 1
    cand = np.where((rank <= top).any(axis=0))[0]
    if len(cand) == 0:
        sys.exit(f"No {a.metric} found in these matches.")
    cum, rank = cum[:, cand], rank[:, cand]
    cnames = [names[i] for i in cand]
    dates = [rows[0][0]] + [rows[e - 1][0] for e in edges[1:]]

    ev, evn = events.most_common(1)[0]
    ev = ev if ev and evn >= 0.8 * n else ""
    word = METRIC_WORD[a.metric]
    title = a.title or (f"Most {word} in the {ev}" if ev else f"Most {word}")
    mt = types.most_common(1)[0][0] if len(types) == 1 else ""
    sub = a.subtitle or " · ".join(x for x in [
        "All-time leaders", f"{rows[0][0][:4]}–{rows[-1][0][:4]}", mt, f"{n:,} matches"] if x)

    L = Layout(a.format)
    fig = new_figure(L)
    y = draw_header(fig, L, title, sub)
    draw_footer(fig, L, a.handle)
    y -= L.px(26)
    when = fig.text(L.mx, y, "", size=56 if a.format == "short" else 50, weight="bold",
                    color=INK2, va="top")
    y -= L.pt(56 if a.format == "short" else 50) * 1.2
    count = fig.text(L.mx, y, "", size=22, color=MUTED, va="top")
    y -= L.px(70)
    name_w = L.pxx(330 if a.format == "short" else 380)
    left = L.mx + name_w
    ax = fig.add_axes([left, L.plot_bottom, L.plot_right - left, y - L.plot_bottom])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim(top + 0.5, 0.5)

    hl = (a.highlight or "").lower()
    colours = [ORANGE if hl and nm.lower() == hl else BLUE for nm in cnames]
    is_hl = np.array([c == ORANGE for c in colours])
    bars = ax.barh(np.full(len(cand), top + 2.0), np.zeros(len(cand)), height=0.76, color=colours, lw=0)
    blend = blended_transform_factory(ax.transAxes, ax.transData)
    nsize = 26 if a.format == "short" else 24
    label_name = [ax.text(-0.025, 0, nm, transform=blend, ha="right", va="center", size=nsize,
                          color=INK, weight="bold" if colours[i] == ORANGE else "normal", clip_on=False)
                  for i, nm in enumerate(cnames)]
    label_val = [ax.text(0, 0, "", ha="left", va="center", size=nsize, color=INK2, clip_on=False)
                 for _ in cnames]

    def update(t):
        pos = t * K
        k = min(int(pos), K - 1)
        f = pos - k
        e = f * f * f * (f * (6 * f - 15) + 10)       # smootherstep: swaps pass quickly
        vals = cum[k] + (cum[k + 1] - cum[k]) * f
        rks = rank[k] + (rank[k + 1] - rank[k]) * e
        alpha = np.clip((top + 1 - rks) / 0.6, 0, 1)
        shown = alpha > 0
        vmax = vals[shown].max() if shown.any() else 1
        xmax = max(vmax, 1) * 1.2
        ax.set_xlim(0, xmax)
        # When two bars cross, fade the labels of the one dropping so names never overprint;
        # the rising bar is drawn on top.
        falling = (rank[k + 1] > rank[k]) & ~is_hl
        text_alpha = alpha.copy()
        vis_idx = np.where(shown)[0]
        by_pos = vis_idx[np.argsort(rks[vis_idx], kind="stable")]
        for upper, lower in zip(by_pos[:-1], by_pos[1:]):
            d = rks[lower] - rks[upper]
            if d < 0.85:
                loser = upper if falling[upper] and not falling[lower] else lower
                if is_hl[loser]:
                    loser = upper if loser == lower else lower
                text_alpha[loser] *= (d / 0.85) ** 2
        for i in range(len(cand)):
            vis = bool(shown[i])
            bars[i].set_visible(vis)
            label_name[i].set_visible(vis)
            label_val[i].set_visible(vis)
            if not vis:
                continue
            bars[i].set_y(rks[i] - 0.38)
            bars[i].set_width(vals[i])
            bars[i].set_alpha(alpha[i])
            bars[i].set_zorder(4 if is_hl[i] else 2 if falling[i] else 3)
            label_name[i].set_y(rks[i])
            label_name[i].set_alpha(text_alpha[i])
            label_val[i].set_position((vals[i] + xmax * 0.012, rks[i]))
            label_val[i].set_text(f"{int(round(vals[i])):,}")
            label_val[i].set_alpha(text_alpha[i])
            label_val[i].set_zorder(4 if falling[i] else 5)
        j = int(round(pos))
        when.set_text(month_year(dates[j]))
        done = int(round(edges[k] + (edges[k + 1] - edges[k]) * f))
        count.set_text(f"Match {done:,} of {n:,}")

    render(fig, update, a, f"race_{a.metric}_{a.format}.mp4")


# --------------------------------------------------------------------------- player
def cmd_player(a):
    target = a.name
    inns, events, types = [], Counter(), Counter()
    for mid, m in iter_matches(a.data):
        info = m["info"]
        if not match_ok(info, a):
            continue
        ps = info.get("players")
        if ps and not any(target in v for v in ps.values()):
            continue
        teams = info.get("teams", [])
        for ii, inn in enumerate(m.get("innings", [])):
            if inn.get("super_over"):
                continue
            runs = balls = 0
            batted = out = False
            for d in deliveries(inn):
                if batter_of(d) == target:
                    batted = True
                    runs += d.get("runs", {}).get("batter", 0)
                    if "wides" not in d.get("extras", {}):
                        balls += 1
                elif d.get("non_striker") == target:
                    batted = True
                for w in d.get("wickets", []):
                    if w.get("player_out") == target and w.get("kind") not in NOT_OUT_KINDS:
                        out = batted = True
            if batted:
                opp = next((t for t in teams if t != inn.get("team")), "")
                inns.append(dict(date=match_date(info), mid=mid, ii=ii, runs=runs, balls=balls,
                                 out=out, team=inn.get("team", ""), opp=opp))
        if any(i["mid"] == mid for i in inns[-2:]):
            events[event_name(info)] += 1
            types[info.get("match_type", "")] += 1
    if not inns:
        sys.exit(f"No innings found for '{target}'. Names are as Cricsheet writes them "
                 f"(e.g. 'V Kohli') - use the 'find' command to look it up.")
    inns.sort(key=lambda r: (r["date"], r["mid"], r["ii"]))
    N = len(inns)
    runs = np.array([i["runs"] for i in inns], float)
    outs = np.array([i["out"] for i in inns], float)
    balls = np.array([i["balls"] for i in inns], float)
    c_runs, c_outs, c_balls = np.cumsum(runs), np.cumsum(outs), np.cumsum(balls)
    avg = np.where(c_outs > 0, c_runs / np.maximum(c_outs, 1), np.nan)

    team = Counter(i["team"] for i in inns).most_common(1)[0][0]
    ev, evn = events.most_common(1)[0]
    scope = ev if ev and evn >= 0.8 * sum(events.values()) else (types.most_common(1)[0][0] if len(types) == 1 else "")
    title = a.title or target
    sub = a.subtitle or " · ".join(x for x in [team, scope, f"{inns[0]['date'][:4]}–{inns[-1]['date'][:4]}"] if x)

    L = Layout(a.format)
    fig = new_figure(L)
    y = draw_header(fig, L, title, sub)
    draw_footer(fig, L, a.handle)

    # stat tiles: 3x2 on Shorts, one row of 6 on long-form
    labels = ["Runs", "Average", "Strike rate", "100s", "50s", "Best"]
    cols = 3 if a.format == "short" else 6
    tile_w = (1 - 2 * L.mx) / cols
    y -= L.px(36)
    tiles = []
    for i, lab in enumerate(labels):
        r, c = divmod(i, cols)
        tx = L.mx + c * tile_w
        ty = y - r * L.px(150)
        v = fig.text(tx, ty, "0", size=50, weight="bold", color=INK, va="top")
        fig.text(tx, ty - L.px(80), lab, size=21, color=MUTED, va="top")
        tiles.append(v)
    rows_n = (len(labels) + cols - 1) // cols
    y -= rows_n * L.px(150) + L.px(10)
    now = fig.text(L.mx, y, "", size=22, color=INK2, va="top")

    left = L.mx + L.pxx(80)
    ax = fig.add_axes([left, L.plot_bottom, L.plot_right - left, y - L.px(120) - L.plot_bottom])
    style_axes(ax)
    x = np.arange(1, N + 1)
    ymax = max(runs.max(), np.nanmax(avg) if np.isfinite(avg).any() else 0, 10)
    ax.set_xlim(0.4, N + 0.6)
    ax.set_ylim(0, ymax * 1.15)
    ax.xaxis.set_major_locator(MaxNLocator(6, integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(5, integer=True))
    ax.set_xlabel("Innings", size=20, labelpad=12)
    bars = ax.bar(x, np.zeros(N), width=0.8 if N < 60 else 0.9, color=BLUE, lw=0)
    avg_line, = ax.plot([], [], color=ORANGE, lw=3.6, solid_capstyle="round", zorder=3)
    ax.legend(handles=[Rectangle((0, 0), 1, 1, color=BLUE), Line2D([], [], color=ORANGE, lw=3.6)],
              labels=["Runs in the innings", "Career average"], loc="lower left",
              bbox_to_anchor=(0, 1.02), ncol=2, frameon=False, fontsize=19, labelcolor=INK2,
              handlelength=1.4, borderaxespad=0, handletextpad=0.6, columnspacing=1.6)
    best5, gap = [], max(2, N // 18)                    # label only the top scores, spaced out
    for i in np.argsort(-runs, kind="stable"):
        if len(best5) == 5:
            break
        if all(abs(i - j) > gap for j in best5):
            best5.append(i)
    peak = {i: ax.text(x[i], runs[i] + ymax * 0.015, "", ha="center", va="bottom", size=17, color=INK2)
            for i in best5}

    def stats(c):
        if c == 0:
            return ["0", "–", "–", "0", "0", "–"]
        r = runs[:c]
        hi = int(np.argmax(r))
        best = f"{int(r[hi])}{'' if outs[hi] else '*'}"
        return [f"{int(c_runs[c - 1]):,}",
                f"{avg[c - 1]:.1f}" if np.isfinite(avg[c - 1]) else "–",
                f"{100 * c_runs[c - 1] / c_balls[c - 1]:.1f}" if c_balls[c - 1] else "–",
                str(int((r >= 100).sum())), str(int(((r >= 50) & (r < 100)).sum())), best]

    def update(t):
        shown = t * N
        c = int(shown)
        grow = shown - c
        for i, b in enumerate(bars):
            if i < c:
                b.set_height(runs[i])
            elif i == c and c < N:
                b.set_height(runs[i] * grow)
            else:
                b.set_height(0)
        avg_line.set_data(x[:c], avg[:c])
        for i, txt in peak.items():
            txt.set_text(str(int(runs[i])) if i < c else "")
        for tile, val in zip(tiles, stats(c)):
            tile.set_text(val)
        if c > 0:
            last = inns[c - 1]
            now.set_text(f"Innings {c}  ·  {month_year(last['date'])}  ·  vs {last['opp']}")
        else:
            now.set_text("")

    render(fig, update, a, f"player_{slug(target)}_{a.format}.mp4")


# --------------------------------------------------------------------------- compare
def collect_careers(a, names):
    """One pass over the data: a batting/bowling line per innings for each named player."""
    out = {n: [] for n in names}
    for mid, m in iter_matches(a.data):
        info = m["info"]
        if not match_ok(info, a):
            continue
        ps = info.get("players") or {}
        present = [n for n in names if not ps or any(n in v for v in ps.values())]
        if not present:
            continue
        teams = info.get("teams", [])
        for ii, inn in enumerate(m.get("innings", [])):
            if inn.get("super_over"):
                continue
            rec = {n: dict(bat=False, runs=0, balls=0, outs=0, bowl=False, wkts=0, conceded=0, legal=0)
                   for n in present}
            for d in deliveries(inn):
                b, ns, bw = batter_of(d), d.get("non_striker"), d.get("bowler")
                r, ex = d.get("runs", {}), d.get("extras", {})
                if b in rec:
                    rec[b]["bat"] = True
                    rec[b]["runs"] += r.get("batter", 0)
                    if "wides" not in ex:
                        rec[b]["balls"] += 1
                if ns in rec:
                    rec[ns]["bat"] = True
                if bw in rec:
                    e = rec[bw]
                    e["bowl"] = True
                    e["conceded"] += r.get("total", 0) - ex.get("byes", 0) - ex.get("legbyes", 0) - ex.get("penalty", 0)
                    if "wides" not in ex and "noballs" not in ex:
                        e["legal"] += 1
                for w in d.get("wickets", []):
                    po = w.get("player_out")
                    if po in rec and w.get("kind") not in NOT_OUT_KINDS:
                        rec[po]["outs"] = 1
                        rec[po]["bat"] = True
                    if bw in rec and w.get("kind") in BOWLER_WICKETS:
                        rec[bw]["wkts"] += 1
            for n, e in rec.items():
                if e["bat"] or e["bowl"]:
                    other = next((t for t in teams if t != inn.get("team")), "")
                    e.update(date=match_date(info), mid=mid, ii=ii, five=int(e["wkts"] >= 5),
                             team=inn.get("team", "") if e["bat"] else other)
                    out[n].append(e)
    for n in names:
        out[n].sort(key=lambda e: (e["date"], e["mid"], e["ii"]))
    return out


def per_match(entries):
    """Merge a player's innings into one row per match (for bowlers: 'after N Tests')."""
    rows = {}
    for e in entries:
        r = rows.setdefault(e["mid"], dict(e, wkts=0, conceded=0, legal=0, five=0))
        for k in ("wkts", "conceded", "legal", "five"):
            r[k] += e[k]
    return sorted(rows.values(), key=lambda e: (e["date"], e["mid"]))


def career_stats(rows, role):
    """Cumulative stat rows: list (one per count 0..N) of [(label, text, value, higher_is_better)]."""
    stats = [None]
    if role == "bat":
        R = B = O = H = F = 0
        for e in rows:
            R += e["runs"]
            B += e["balls"]
            O += e["outs"]
            H += e["runs"] >= 100
            F += 50 <= e["runs"] < 100
            stats.append(dict(total=R, rows=[
                ("Runs", f"{R:,}", R, True),
                ("Average", f"{R / O:.1f}" if O else "–", R / O if O else None, True),
                ("Strike rate", f"{100 * R / B:.1f}" if B else "–", 100 * R / B if B else None, True),
                ("100s / 50s", f"{H} / {F}", H * 1000 + F, True)]))
    else:
        W = C = L = V = 0
        for e in rows:
            W += e["wkts"]
            C += e["conceded"]
            L += e["legal"]
            V += e["five"]
            stats.append(dict(total=W, rows=[
                ("Wickets", f"{W:,}", W, True),
                ("Average", f"{C / W:.1f}" if W else "–", C / W if W else None, False),
                ("Economy", f"{6 * C / L:.2f}" if L else "–", 6 * C / L if L else None, False),
                ("5-wkt hauls", str(V), V, True)]))
    return stats


FORMAT_WORD = {"odi": "ODI", "test": "Test", "t20": "T20", "it20": "T20I", "odm": "one-day", "mdm": "first-class"}


def cmd_compare(a):
    names = [a.a, a.b]
    if a.a == a.b:
        sys.exit("Pick two different players.")
    careers = collect_careers(a, names)
    role = "bowl" if a.metric == "wickets" else "bat"
    seqs = []
    for n in names:
        rows = [e for e in careers[n] if e[role]]
        if role == "bowl" and a.per == "match":
            rows = per_match(rows)
        if not rows:
            sys.exit(f"No {'bowling' if role == 'bowl' else 'batting'} found for '{n}' with these filters. "
                     f"Check the exact name with the 'find' command.")
        seqs.append(rows)
    N = min(len(s) for s in seqs)
    if a.innings:
        N = min(N, a.innings)
    seqs = [s[:N] for s in seqs]
    stats = [career_stats(s, role) for s in seqs]
    totals = [np.cumsum([e["runs"] if role == "bat" else e["wkts"] for e in s]) for s in seqs]
    labels = [a.label_a or a.a, a.label_b or a.b]

    unit = "Tests" if (role == "bowl" and a.per == "match" and (a.match_type or "").lower() == "test") else \
        "matches" if (role == "bowl" and a.per == "match") else "innings"
    fw = FORMAT_WORD.get((a.match_type or "").lower(), "")
    if a.team_type == "international" and fw == "T20":
        fw = "T20I"
    span = lambda s: f"{s[0]['date'][:4]}–{s[-1]['date'][:4]}" if s[0]["date"][:4] != s[-1]["date"][:4] else s[0]["date"][:4]
    title = (a.title or f"{labels[0]} vs {labels[1]}").replace("{N}", str(N))
    lead_word = "" if unit == "Tests" or not fw else fw + " "
    sub = a.subtitle or f"First {N} {lead_word}{unit} each · {span(seqs[0])} vs {span(seqs[1])}"

    L = Layout(a.format)
    short = a.format == "short"
    fig = new_figure(L)
    y = draw_header(fig, L, title, sub)
    draw_footer(fig, L, a.handle)
    colours = [BLUE, ORANGE]

    # stat table: label column + one column per player (Shorts: stacked above the chart;
    # long-form: table on the left, chart on the right)
    tbl_right = 1 - L.mx if short else 0.42
    col_x = [L.mx + (tbl_right - L.mx) * f for f in (0.42, 0.74)]
    y -= L.px(40)
    for k in range(2):
        cx = col_x[k]
        fig.add_artist(Rectangle((cx - L.pxx(13), y - L.px(13)), L.pxx(26), L.px(26),
                                 transform=fig.transFigure, color=colours[k], lw=0))
        nm = labels[k].split()[-1] if len(labels[k]) > 12 else labels[k]
        fig.text(cx, y - L.px(30), nm, size=26 if short else 24, weight="bold", color=INK, ha="center", va="top")
    y -= L.px(110)
    row_h = L.px(84 if short else 92)
    cells = []
    for r in range(4):
        yy = y - r * row_h
        lab = fig.text(L.mx, yy, "", size=24 if short else 22, color=MUTED, va="center")
        vals = [fig.text(cx, yy, "", size=42 if short else 38, weight="bold", color=INK, ha="center", va="center")
                for cx in col_x]
        cells.append((lab, vals))
    y -= 3 * row_h + L.px(70)
    counter = fig.text(L.mx, y, "", size=24, color=INK2, va="center")
    verdict = fig.text(L.mx, y - L.px(56), "", size=32 if short else 30, weight="bold", color=INK, va="center")

    if short:
        top = y - L.px(130)
        left = L.mx + L.pxx(90)
        ax = fig.add_axes([left, L.plot_bottom, L.plot_right - left, top - L.plot_bottom])
    else:
        left = 0.52
        ax = fig.add_axes([left, L.plot_bottom, L.plot_right - left, 0.70 - L.plot_bottom])
    style_axes(ax)
    x = np.arange(0, N + 1)
    ys = [np.concatenate([[0], t]) for t in totals]
    ymax = max(float(t.max()) for t in ys)
    ax.set_xlim(0, N * 1.02)
    ax.set_ylim(0, ymax * 1.12)
    ax.xaxis.set_major_locator(MaxNLocator(5, integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(5, integer=True))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_xlabel(unit.capitalize() if unit != "innings" else "Innings", size=20, labelpad=12)
    ax.text(0, 1.03, "Runs" if role == "bat" else "Wickets", transform=ax.transAxes, size=20, color=MUTED, va="bottom")
    lines, heads = [], []
    for k in range(2):
        ln, = ax.plot([], [], color=colours[k], lw=3.6, solid_capstyle="round", zorder=3)
        hd, = ax.plot([], [], "o", ms=14, mfc=INK, mec=colours[k], mew=3, zorder=4)
        lines.append(ln)
        heads.append(hd)

    def update(t):
        pos = t * N
        c = int(pos)
        frac = pos - c
        for k in range(2):
            yk = ys[k]
            if c < N:
                xs = np.append(x[:c + 1], c + frac)
                yv = np.append(yk[:c + 1], yk[c] + (yk[c + 1] - yk[c]) * frac)
            else:
                xs, yv = x, yk
            lines[k].set_data(xs, yv)
            heads[k].set_data([xs[-1]], [yv[-1]])
        cnt = c
        for r in range(4):
            lab, vals = cells[r]
            if cnt == 0:
                lab.set_text(stats[0][1]["rows"][r][0])
                for v in vals:
                    v.set_text("0" if r == 0 else "–")
                    v.set_color(INK)
                continue
            ra, rb = stats[0][cnt]["rows"][r], stats[1][cnt]["rows"][r]
            lab.set_text(ra[0])
            vals[0].set_text(ra[1])
            vals[1].set_text(rb[1])
            va_, vb_, hib = ra[2], rb[2], ra[3]
            if va_ is None or vb_ is None or va_ == vb_:
                vals[0].set_color(INK)
                vals[1].set_color(INK)
            else:
                a_wins = (va_ > vb_) == hib
                vals[0].set_color(INK if a_wins else MUTED)
                vals[1].set_color(MUTED if a_wins else INK)
        counter.set_text(f"After {max(cnt, 0)} {unit}" if cnt else "")
        if t >= 1:
            ta, tb = int(totals[0][-1]), int(totals[1][-1])
            word = "runs" if role == "bat" else "wickets"
            if ta == tb:
                verdict.set_text(f"Dead level on {ta:,} {word}")
            else:
                lead = labels[0] if ta > tb else labels[1]
                verdict.set_text(f"{lead} leads by {abs(ta - tb):,} {word}")
        else:
            verdict.set_text("")

    ta, tb = int(totals[0][-1]), int(totals[1][-1])
    word = "runs" if role == "bat" else "wickets"
    write_facts(a, dict(
        kind="compare", on_screen_title=title, subtitle=sub, format=fw, unit=unit, count=N, metric=word,
        data_through=max(seqs[0][-1]["date"], seqs[1][-1]["date"]),
        players=[dict(cricsheet_name=names[k], label=labels[k],
                      first=seqs[k][0]["date"], last=seqs[k][-1]["date"],
                      stats={r[0]: r[1] for r in stats[k][N]["rows"]}) for k in range(2)],
        leader=None if ta == tb else (labels[0] if ta > tb else labels[1]), margin=abs(ta - tb)))
    render(fig, update, a, f"compare_{slug(a.a)}_vs_{slug(a.b)}_{a.format}.mp4", intro=1.0, outro=4.0)


# --------------------------------------------------------------------------- helpers
def cmd_matches(a):
    rows = []
    for mid, m in iter_matches(a.data):
        info = m["info"]
        if match_ok(info, a):
            rows.append((match_date(info), mid, " vs ".join(info.get("teams", [])),
                         event_name(info), result_text(info)))
    rows.sort(reverse=True)
    if not rows:
        sys.exit("No matches found with those filters.")
    for d, mid, teams, ev, res in rows[:a.last]:
        print(f"{mid:>9}  {d}  {teams}\n{'':>11}{ev}{'  |  ' if ev and res else ''}{res}")
    print(f"\n{len(rows):,} matches in total. Use the number on the left with:  worm <data> --match <number>")


def cmd_find(a):
    q = a.query.lower()
    seen = defaultdict(Counter)
    for _, m in iter_matches(a.data):
        info = m["info"]
        if not match_ok(info, a):
            continue
        for team, ps in (info.get("players") or {}).items():
            for p in ps:
                if q in p.lower():
                    seen[p][team] += 1
    if not seen:
        sys.exit(f"Nobody matching '{a.query}'. Cricsheet uses initials + surname, e.g. 'V Kohli'.")
    for p, teams in sorted(seen.items(), key=lambda kv: -sum(kv[1].values()))[:25]:
        print(f"{p:<28} {sum(teams.values()):>4} matches   ({', '.join(t for t, _ in teams.most_common(3))})")


# --------------------------------------------------------------------------- CLI
def main():
    filt = argparse.ArgumentParser(add_help=False)
    filt.add_argument("data", help="Cricsheet .zip, folder of .json files, or one match .json")
    filt.add_argument("--event", help="keep matches whose event name contains this text")
    filt.add_argument("--match-type", help="T20, IT20, ODI, ODM, Test or MDM")
    filt.add_argument("--gender", choices=["male", "female"])
    filt.add_argument("--team-type", choices=["international", "club"],
                      help="international = Tests/ODIs/T20Is only; club = leagues like the IPL")
    filt.add_argument("--team", help="keep matches involving this team (exact name)")
    filt.add_argument("--since", help="start date, e.g. 2020 or 2020-04-01")
    filt.add_argument("--until", help="end date, e.g. 2024 or 2024-05-31")

    vid = argparse.ArgumentParser(add_help=False)
    vid.add_argument("--format", choices=["short", "long"], default="short",
                     help="short = 9:16 for Shorts (default), long = 16:9")
    vid.add_argument("--handle", default="", help="your channel handle, shown on the video")
    vid.add_argument("--title", help="headline (default: automatic)")
    vid.add_argument("--subtitle", help="line under the headline (default: automatic)")
    vid.add_argument("--out", help="output file name (.mp4)")
    vid.add_argument("--still", action="store_true", help="save only the final frame as a PNG")
    vid.add_argument("--facts", help="also save the video's numbers to this JSON file (for captions)")
    vid.add_argument("--no-sound", action="store_true",
                     help="leave the video silent (default: original music and sound effects)")

    p = argparse.ArgumentParser(description="Make cricket stat videos from Cricsheet data.",
                                epilog="Run any command with -h for its options.")
    sp = p.add_subparsers(dest="cmd", required=True)

    w = sp.add_parser("worm", parents=[filt, vid], help="animated worm for one match")
    w.add_argument("--match", help="match ID (see the 'matches' command)")
    w.add_argument("--seconds", type=float, default=20)
    w.add_argument("--abbr", action="append", help='short team name, e.g. --abbr "Sunrisers Hyderabad=SRH"')
    w.set_defaults(fn=cmd_worm)

    r = sp.add_parser("race", parents=[filt, vid], help="bar-chart race of all-time leaders")
    r.add_argument("--metric", choices=list(METRIC_WORD), default="runs")
    r.add_argument("--top", type=int, default=10)
    r.add_argument("--highlight", help="player to colour orange, e.g. 'V Kohli'")
    r.add_argument("--seconds", type=float, default=40)
    r.set_defaults(fn=cmd_race)

    pl = sp.add_parser("player", parents=[filt, vid], help="one player's career innings by innings")
    pl.add_argument("--name", required=True, help="exact Cricsheet name, e.g. 'V Kohli' (see 'find')")
    pl.add_argument("--seconds", type=float, default=30)
    pl.set_defaults(fn=cmd_player)

    c = sp.add_parser("compare", parents=[filt, vid], help="two players head to head after the same number of innings")
    c.add_argument("--a", required=True, help="first player, exact Cricsheet name, e.g. 'V Kohli'")
    c.add_argument("--b", required=True, help="second player, e.g. 'Babar Azam'")
    c.add_argument("--label-a", help="name to show on screen, e.g. 'Virat Kohli'")
    c.add_argument("--label-b", help="name to show on screen")
    c.add_argument("--metric", choices=["runs", "wickets"], default="runs")
    c.add_argument("--per", choices=["innings", "match"], default="innings",
                   help="for wickets: count by innings bowled or by match ('after 50 Tests')")
    c.add_argument("--innings", type=int, help="cap the comparison at this many innings/matches")
    c.add_argument("--seconds", type=float, default=15)
    c.set_defaults(fn=cmd_compare)

    mt = sp.add_parser("matches", parents=[filt], help="list matches and their IDs, newest first")
    mt.add_argument("--last", type=int, default=20)
    mt.set_defaults(fn=cmd_matches)

    f = sp.add_parser("find", parents=[filt], help="find a player's exact Cricsheet name")
    f.add_argument("query")
    f.set_defaults(fn=cmd_find)

    a = p.parse_args()
    if hasattr(a, "top") and not 3 <= a.top <= 15:
        sys.exit("--top must be between 3 and 15.")
    a.fn(a)


if __name__ == "__main__":
    main()
