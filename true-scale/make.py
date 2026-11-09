"""Build a True Scale episode end to end.

    python3 true-scale/make.py setup                        # download map data + voice model (once per machine)
    python3 true-scale/make.py tts     episodes/<slug>      # narration clips for every scene (skips existing)
    python3 true-scale/make.py stills  episodes/<slug> <scene_id> <t> [<t> ...]   # PNG frames to check layout
    python3 true-scale/make.py render  episodes/<slug> [scene_id ...]             # scene videos (2 in parallel)
    python3 true-scale/make.py assemble episodes/<slug>     # join scenes + narration + music -> out/<slug>.mp4
    python3 true-scale/make.py all     episodes/<slug>      # tts + render + assemble + contact sheet

An episode folder holds script.json ([{"id", "text", optional "hold"}...]) and scenes.py, which defines one
function per scene id taking the Scene `S`, and may define hold(sid) for extra seconds at the end of scenes.
Paths for episodes are relative to true-scale/.
"""
import importlib.util, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.environ.get("TS_DATA", os.path.expanduser("~/.cache/true-scale"))
os.environ["TS_DATA"] = DATA
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
FILES = {"countries50.geojson": NE + "ne_50m_admin_0_countries.geojson",
         "admin1_10m.geojson": NE + "ne_10m_admin_1_states_provinces.geojson",
         "admin0_10m_ind.geojson": NE + "ne_10m_admin_0_countries_ind.geojson",
         "ne_50m_rivers_lake_centerlines.geojson": NE + "ne_50m_rivers_lake_centerlines.geojson",
         "ne_50m_lakes.geojson": NE + "ne_50m_lakes.geojson",
         "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
         "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"}
VOICE = os.environ.get("TS_VOICE", "am_michael")
SPEED = 0.94


def setup():
    os.makedirs(DATA, exist_ok=True)
    for name, url in FILES.items():
        path = os.path.join(DATA, name)
        if not os.path.exists(path):
            print("downloading", name, flush=True)
            subprocess.run(["curl", "-sSfL", "-o", path + ".part", url], check=True)
            os.replace(path + ".part", path)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "kokoro-onnx",
                    "soundfile", "shapely", "pyproj", "matplotlib"], check=False)


def ep_dir(arg):
    d = arg if os.path.isabs(arg) else os.path.join(HERE, arg)
    if not os.path.exists(os.path.join(d, "script.json")):
        sys.exit(f"no script.json in {d}")
    return d


def tts(d):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(DATA, "kokoro-v1.0.onnx"), os.path.join(DATA, "voices-v1.0.bin"))
    os.makedirs(os.path.join(d, "audio"), exist_ok=True)
    for s in json.load(open(os.path.join(d, "script.json"))):
        out = os.path.join(d, "audio", s["id"] + ".wav")
        if os.path.exists(out):
            continue
        a, sr = k.create(s["text"], voice=VOICE, speed=SPEED, lang="en-us")
        sf.write(out + ".tmp.wav", a, sr)
        os.replace(out + ".tmp.wav", out)
        print(s["id"], round(len(a) / sr, 1), "s", flush=True)


def load(d):
    from engine import core
    core.EP = core.Episode(d)
    spec = importlib.util.spec_from_file_location("scenes", os.path.join(d, "scenes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for sid in core.EP.order:
        fn = getattr(mod, sid, None)
        if fn is None:
            sys.exit(f"scenes.py has no function for scene {sid}")
        core.EP.scenes[sid] = fn
    core.EP.hold = getattr(mod, "hold", None)
    return core


def total_minutes(d):
    core = load(d)
    return sum(core.duration(s) for s in core.EP.order) / 60


def render(d, ids=None):
    order = [s["id"] for s in json.load(open(os.path.join(d, "script.json")))]
    ids = ids or order
    procs = []
    for sid in ids:
        procs.append(subprocess.Popen([sys.executable, __file__, "_one", d, sid]))
        if len(procs) == 2:
            procs.pop(0).wait()
    for p in procs:
        p.wait()
    missing = [s for s in ids if not os.path.exists(os.path.join(d, "video", s + ".mp4"))]
    if missing:
        sys.exit(f"render failed for: {missing}")


def assemble(d):
    import numpy as np, soundfile as sf
    FPS, SR, LEAD = 30, 44100, 0.5
    order = [s["id"] for s in json.load(open(os.path.join(d, "script.json")))]
    slug = os.path.basename(os.path.normpath(d))

    def frames(path):
        out = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                              "stream=nb_read_packets", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
        return int(out.strip())
    parts, starts, t = [], [], 0.0
    for sid in order:
        n = frames(os.path.join(d, "video", sid + ".mp4"))
        L = int(round(n / FPS * SR))
        a, sr = sf.read(os.path.join(d, "audio", sid + ".wav"))
        a = a.mean(axis=1) if a.ndim > 1 else a
        if sr != SR:
            a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * SR / sr)), np.arange(len(a)), a)
        seg = np.zeros(L)
        i0 = int(LEAD * SR)
        seg[i0:i0 + len(a)] = a[:max(0, L - i0)]
        parts.append(seg)
        starts.append(t)
        t += L / SR
    voice = np.concatenate(parts)
    voice *= 0.89 / (np.abs(voice).max() + 1e-9)
    N = len(voice)
    tt = np.arange(N) / SR
    seed = sum(map(ord, slug))
    rng = np.random.default_rng(seed)
    progs = [[[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]],
             [[146.83, 174.61, 220.0], [116.54, 146.83, 174.61], [174.61, 220.0, 261.63], [130.81, 164.81, 196.0]],
             [[164.81, 196.0, 246.94], [130.81, 164.81, 196.0], [196.0, 246.94, 293.66], [146.83, 185.0, 220.0]]]
    chords = progs[seed % len(progs)]
    bar = 8.0
    music = np.zeros(N)
    for k in range(int(np.ceil(N / SR / bar)) + 1):
        t0 = k * bar
        i0, i1 = int(t0 * SR), min(N, int((t0 + bar + 2) * SR))
        if i0 >= N:
            break
        x = tt[i0:i1] - t0
        env = np.minimum(1, x / 2.0) * np.minimum(1, np.maximum(0, (bar + 2 - x) / 2.5))
        for f in chords[k % 4]:
            for det in (-0.6, 0.6):
                music[i0:i1] += env * np.sin(2 * np.pi * (f / 2 + det) * x + rng.uniform(0, 6)) * 0.12
            music[i0:i1] += env * np.sin(2 * np.pi * f * x) * 0.05
        music[i0:i1] += env * np.sin(2 * np.pi * chords[k % 4][0] / 4 * x) * 0.18
    for b in np.arange(0, N / SR, 0.6):
        i = int(b * SR)
        L = min(int(0.25 * SR), N - i)
        if L <= 0:
            break
        music[i:i + L] += 0.10 * np.exp(-np.arange(L) / SR * 18) * np.sin(2 * np.pi * 55 * np.arange(L) / SR)
    music = np.convolve(music, np.ones(40) / 40, mode="same")
    music /= np.abs(music).max() + 1e-9
    env = np.convolve(np.abs(voice), np.ones(int(0.3 * SR)) / int(0.3 * SR), mode="same")
    duck = np.convolve(np.where(env > 0.01, 0.10, 0.22), np.ones(int(0.4 * SR)) / int(0.4 * SR), mode="same")
    fade = np.minimum(1, tt / 2.0) * np.minimum(1, (tt[-1] - tt) / 3.0)
    mix = np.tanh(1.1 * (voice + music * duck * fade)) / np.tanh(1.1)
    sf.write(os.path.join(d, "mix.wav"), np.stack([mix, mix], axis=1), SR)
    with open(os.path.join(d, "concat.txt"), "w") as fh:
        for sid in order:
            fh.write(f"file '{os.path.join(d, 'video', sid + '.mp4')}'\n")
    os.makedirs(os.path.join(d, "out"), exist_ok=True)
    joined = os.path.join(d, "joined.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(d, "concat.txt"), "-c", "copy", joined], check=True)
    out = os.path.join(d, "out", slug + ".mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-i", os.path.join(d, "mix.wav"), "-map",
                    "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags",
                    "+faststart", out + ".partial.mp4"], check=True)
    os.replace(out + ".partial.mp4", out)
    with open(os.path.join(d, "out", "chapters.txt"), "w") as fh:
        for sid, s in zip(order, starts):
            fh.write(f"{int(s // 60)}:{int(s % 60):02d} {sid}\n")
    print(open(os.path.join(d, "out", "chapters.txt")).read())
    print(f"total {N / SR / 60:.2f} min -> {out}")
    # contact sheet: 20 frames across the video, to eyeball before sending
    sheet_dir = os.path.join(d, "check")
    os.makedirs(sheet_dir, exist_ok=True)
    total = N / SR
    for i in range(20):
        ts = total * (i + 0.5) / 20
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ts:.2f}", "-i", out, "-frames:v", "1", "-vf",
                        "scale=480:-1", os.path.join(sheet_dir, f"{i:02d}.png")], check=False)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", os.path.join(sheet_dir, "*.png"),
                    "-vf", "tile=4x5", os.path.join(d, "out", "contact-sheet.png")], check=False)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "setup":
        setup()
    elif cmd == "tts":
        tts(ep_dir(sys.argv[2]))
    elif cmd == "minutes":
        print(f"{total_minutes(ep_dir(sys.argv[2])):.2f} min")
    elif cmd == "stills":
        core = load(ep_dir(sys.argv[2]))
        core.render(sys.argv[3], [float(x) for x in sys.argv[4:]])
        print("stills in", os.path.join(core.EP.dir, "stills"))
    elif cmd == "_one":
        core = load(sys.argv[2])
        core.render(sys.argv[3])
    elif cmd == "render":
        render(ep_dir(sys.argv[2]), sys.argv[3:] or None)
    elif cmd == "assemble":
        assemble(ep_dir(sys.argv[2]))
    elif cmd == "all":
        d = ep_dir(sys.argv[2])
        tts(d)
        print(f"length: {total_minutes(d):.2f} min", flush=True)
        render(d)
        assemble(d)
    else:
        sys.exit(__doc__)
