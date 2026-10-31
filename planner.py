#!/usr/bin/env python3
"""
planner.py - runs every day on GitHub Actions for The Cricket Vault.

1. Looks at matches from the last few days and picks the ones worth a Short
   (India games, the IPL, close finishes between the big teams).
2. Renders queued ideas from queue.json (comparisons, races, career videos).
3. Records every finished video, with the facts behind it, in manifest.json.
   Claude reads that file each day, writes the title and description, and
   schedules the best video through Metricool.

Data comes from Cricsheet (cricsheet.org): free ball-by-ball records, credited
in every video.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import cricket_videos as cv  # noqa: E402

READY = os.path.join(ROOT, "shorts", "ready")
MANIFEST = os.path.join(ROOT, "manifest.json")
QUEUE = os.path.join(ROOT, "queue.json")
PLAYERS = os.path.join(ROOT, "data", "players_index.json")
HANDLE = "@thecricketvault"
BIG = {"India", "Australia", "England", "Pakistan", "South Africa", "New Zealand",
       "Sri Lanka", "Afghanistan", "West Indies", "Bangladesh"}
LEAGUE_TAGS = {"Indian Premier League": "IPL"}
WORM_SHELF_LIFE_DAYS = 4          # a match Short is stale after this
MIN_WORM_SCORE = 50


def load(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return default


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- choosing matches
def worm_score(f):
    """How likely a match is to interest Indian and global fans. 0 = skip."""
    if f["gender"] != "male" or f["match_type"] not in ("T20", "ODI") or len(f["innings"]) < 2:
        return 0
    teams = set(f["teams"])
    league = LEAGUE_TAGS.get(f["event"])
    if f["team_type"] != "international" and not league:
        return 0
    score = 0
    if "India" in teams:
        score += 50
    if teams <= BIG:
        score += 20
    if league:
        score += 35
    o, ch = f["outcome"], f.get("chase") or {}
    by = o.get("by", {})
    close = (o.get("result") == "tie"
             or (ch.get("chased") and ch.get("final_over_reached"))
             or by.get("runs", 99) <= 10 or by.get("wickets", 99) <= 2)
    if close:
        score += 40
    if f.get("super_over"):
        score += 20
    if not o:
        return 0                                       # no result
    return score


def hooks(f):
    """(on-screen headline without emoji, suggested YouTube title)."""
    A, B = (cv.short_team(t, {}) for t in f["teams"])
    league = LEAGUE_TAGS.get(f["event"])
    n = f.get("match_number")
    if league:
        tag = f"{A} vs {B} {league} {f['date'][:4]}"
    else:
        tag = f"{A} vs {B}" + (f" {cv.ordinal(n)} {f['format']}" if n else f" {f['format']}")
    o, ch = f["outcome"], f.get("chase") or {}
    w, by = o.get("winner"), o.get("by", {})
    loser = next((t for t in f["teams"] if t != w), "")
    if o.get("result") == "tie":
        return f"{A} vs {B} ended in a TIE", f"It's a TIE 😱 {tag}"
    if ch.get("chased") and ch.get("final_over_reached") and w == f["innings"][1]["team"]:
        need = ch["needed_in_final_over"]
        return (f"{w} needed {need} off the final over",
                f"{w} needed {need} off the LAST over 😳 {tag}")
    if "runs" in by and by["runs"] <= 10:
        s = "s" if by["runs"] != 1 else ""
        return (f"{w} defended {ch.get('target', 0) - 1} by just {by['runs']} run{s}",
                f"{w} won by just {by['runs']} run{s} 😳 {tag}")
    if "wickets" in by and by["wickets"] <= 2:
        s = "s" if by["wickets"] != 1 else ""
        return (f"{w} got home by {by['wickets']} wicket{s}",
                f"{w} scrape home by {by['wickets']} wicket{s} 😳 {tag}")
    margin = f"{by['runs']} runs" if "runs" in by else f"{by.get('wickets', 0)} wickets"
    return f"{w} beat {loser} by {margin}", f"{w} beat {loser} by {margin} 🔥 {tag}"


def render(kind, source, extra, item_id):
    os.makedirs(READY, exist_ok=True)
    out = os.path.join(READY, f"{item_id}.mp4")
    facts = os.path.join(READY, f"{item_id}.json")
    cmd = [sys.executable, os.path.join(ROOT, "cricket_videos.py"), kind, source, *extra,
           "--handle", HANDLE, "--out", out, "--facts", facts]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        return None, (r.stderr or r.stdout).strip()[-600:]
    return (os.path.relpath(out, ROOT), os.path.relpath(facts, ROOT)), ""


def plan_worms(source, manifest, today, window, max_new):
    seen = {it["id"] for it in manifest["items"]}
    since = (today - dt.timedelta(days=window)).isoformat()
    picks = []
    for mid, m in cv.iter_matches(source, quiet=True):
        if cv.match_date(m["info"]) < since or f"worm-{mid}" in seen:
            continue
        try:
            f = cv.match_facts(m)
        except (KeyError, IndexError, TypeError, ValueError) as e:
            log(f"  skip {mid}: {e}")
            continue
        s = worm_score(f)
        if s >= MIN_WORM_SCORE:
            picks.append((s, f["date"], mid, f))
    picks.sort(key=lambda p: (-p[0], p[1]))
    log(f"Worm candidates since {since}: {len(picks)}")
    for s, date, mid, f in picks[:max_new]:
        screen, yt = hooks(f)
        item_id = f"worm-{mid}"
        files, err = render("worm", source, ["--match", mid, "--title", screen], item_id)
        entry = dict(id=item_id, kind="worm", created=today.isoformat(), match_date=date, priority=s,
                     expires=(dt.date.fromisoformat(date) + dt.timedelta(days=WORM_SHELF_LIFE_DAYS)).isoformat(),
                     suggested_title=yt)
        if files:
            entry.update(status="ready", file=files[0], facts_file=files[1])
            log(f"  rendered {item_id} ({s}): {yt}")
        else:
            entry.update(status="failed", error=err)
            log(f"  FAILED {item_id}: {err}")
        manifest["items"].append(entry)


def plan_queue(source, queue, manifest, today, max_new):
    done = 0
    for q in queue["items"]:
        if q.get("status") != "queued" or done >= max_new:
            continue
        files, err = render(q["kind"], source, q["args"], q["id"])
        done += 1
        entry = dict(id=q["id"], kind=q["kind"], created=today.isoformat(), priority=q.get("priority", 60),
                     expires=None, suggested_title=q.get("suggested_title", ""), notes=q.get("notes", ""))
        if files:
            entry.update(status="ready", file=files[0], facts_file=files[1])
            facts = load(os.path.join(ROOT, files[1]), {})
            if facts.get("on_screen_title"):
                entry["suggested_title"] = entry["suggested_title"].replace("{N}", str(facts.get("count", "")))
            q["status"] = "rendered"
            log(f"  rendered queued {q['id']}")
        else:
            entry.update(status="failed", error=err)
            q["status"] = "failed"
            q["error"] = err
            log(f"  FAILED queued {q['id']}: {err}")
        manifest["items"] = [it for it in manifest["items"] if it["id"] != q["id"]] + [entry]


def build_players_index(source, today):
    """Exact Cricsheet names of international men's players, so ideas can be checked."""
    counts = {}
    for _, m in cv.iter_matches(source, quiet=True):
        i = m["info"]
        if i.get("team_type") != "international" or i.get("gender") != "male":
            continue
        fmt = {"T20": "T20I"}.get(i.get("match_type"), i.get("match_type"))
        for team, ps in (i.get("players") or {}).items():
            for p in ps:
                e = counts.setdefault(p, {"teams": {}, "formats": {}, "last": ""})
                e["teams"][team] = e["teams"].get(team, 0) + 1
                e["formats"][fmt] = e["formats"].get(fmt, 0) + 1
                e["last"] = max(e["last"], cv.match_date(i))
    keep = {p: dict(team=max(e["teams"], key=e["teams"].get), formats=e["formats"], last=e["last"])
            for p, e in counts.items() if sum(e["formats"].values()) >= 10}
    save(PLAYERS, {"built": today.isoformat(), "players": dict(sorted(keep.items()))})
    log(f"Players index: {len(keep)} players")


def expire(manifest, today):
    for it in manifest["items"]:
        if it.get("status") == "ready" and it.get("expires") and it["expires"] < today.isoformat():
            it["status"] = "expired"
            for k in ("file", "facts_file"):
                path = os.path.join(ROOT, it.get(k, "") or "")
                if it.get(k) and os.path.exists(path):
                    os.remove(path)
            log(f"  expired {it['id']}")


def needs_full_data(recent, today):
    if not recent or not os.path.exists(recent):
        return True
    if any(q.get("status") == "queued" for q in load(QUEUE, {"items": []})["items"]):
        return True
    built = load(PLAYERS, {}).get("built", "")
    return not built or built < (today - dt.timedelta(days=7)).isoformat()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--recent", help="Cricsheet recently-played zip")
    p.add_argument("--all", dest="all_zip", help="Cricsheet all-matches zip")
    p.add_argument("--today", help="override today's date (YYYY-MM-DD) for testing")
    p.add_argument("--window", type=int, default=5, help="days back to look for matches")
    p.add_argument("--max-worms", type=int, default=3)
    p.add_argument("--max-queue", type=int, default=3)
    p.add_argument("--needs-all", action="store_true", help="exit 0 if the full data download is needed")
    a = p.parse_args()
    today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.utcnow().date()

    if a.needs_all:
        sys.exit(0 if needs_full_data(a.recent, today) else 1)

    def usable(path):
        return path and os.path.exists(path) and zipfile.is_zipfile(path)

    manifest = load(MANIFEST, {"items": []})
    queue = load(QUEUE, {"items": []})
    recent = a.recent if usable(a.recent) else (a.all_zip if usable(a.all_zip) else None)
    if not recent:
        sys.exit("No usable Cricsheet data was downloaded.")
    log(f"Today {today}; recent data: {os.path.basename(recent)}")
    expire(manifest, today)
    plan_worms(recent, manifest, today, a.window, a.max_worms)
    if usable(a.all_zip):
        plan_queue(a.all_zip, queue, manifest, today, a.max_queue)
        built = load(PLAYERS, {}).get("built", "")
        if not built or built < (today - dt.timedelta(days=7)).isoformat():
            build_players_index(a.all_zip, today)
    save(MANIFEST, manifest)
    save(QUEUE, queue)
    ready = [it["id"] for it in manifest["items"] if it.get("status") == "ready"]
    log(f"Ready to schedule: {len(ready)} {ready}")


if __name__ == "__main__":
    main()
