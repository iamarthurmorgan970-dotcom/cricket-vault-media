# The Cricket Vault: Shorts pipeline

Automated data-driven cricket Shorts for [@thecricketvault](https://www.youtube.com/@thecricketvault-x1c).

**How it works**

1. **Every morning (07:00 IST)** the *Make Shorts* GitHub Action downloads fresh ball-by-ball data from
   [Cricsheet](https://cricsheet.org), picks matches worth a Short (India games, IPL, close finishes between
   the big teams), renders them, and renders any ideas waiting in `queue.json`.
2. Finished videos land in `shorts/ready/` with a facts file, and are listed in `manifest.json`.
3. **Every day** Claude reads `manifest.json`, writes the title and description from the facts, and schedules
   the best video on YouTube through Metricool (7:30 pm IST), keeping within Metricool's free 20 posts a month.
   Posts are logged in `schedule_log.json`. Once a week Claude adds new comparison ideas to `queue.json`.

**Formats**

- `thriller`: a last-over finish, opening on the equation ("11 OFF 6"), ball-by-ball final over.
- `worm`: any other notable match, run by run.
- `compare`: two players after the same number of innings.
- `card`: a 6-second static leaderboard card. In the pipeline, cards use **verified specs only**
  (`cards/*.json`, numbers from a cited source), never raw Cricsheet totals.

**Content standard (from 3 Nov 2026): every upload needs a "no way!" fact**

The headline number must make a casual fan stop scrolling. It has to be one of:
a record or first (fastest, fewest, most, youngest, only player ever); an extreme single-match event
(a collapse, a huge chase, a hat-trick, a spell like 5 for 7); or a counter-intuitive twist (the less famous
player is ahead, a gap that's enormous, a bowler who "owns" a great batter, identical numbers across eras).
"X vs Y" with close numbers and no twist fails, and is `parked` instead of posted. If nothing passes on a
given day, nothing is posted that day. Filler hurts a new channel more than a gap does.

**Accuracy rules (learned 31 Oct 2026)**

Cricsheet is missing some matches, especially recent ones (e.g. India v Afghanistan T20Is, Sept 2026; some
Babar Azam ODIs), and its Test/ODI coverage starts around 2002. So:

- Single-match videos (thriller, worm) are safe: if a match is in the data, it is complete.
- Any career number for a player who has played in the last ~2 years must be checked against an official
  source (ESPNcricinfo, Wikipedia citing it, ICC, or a news report) before posting. If it doesn't match,
  the video is blocked (`status: blocked` in `manifest.json`).
- Comparisons are safest when anchored to a verified milestone (e.g. "Root 10,000 runs in 218 innings").
- Record cards are written from sources, cited on screen, with a `sources` list in the manifest.

**Files**

| File | What it is |
| --- | --- |
| `cricket_videos.py` | Renders the videos (worm, compare, race, player) with original music |
| `planner.py` | Chooses what to render each day and updates the manifest |
| `queue.json` | Ideas waiting to be rendered |
| `cards/` | Verified card specs (numbers + source) |
| `data/aliases.json` | Cricsheet name → on-screen name |
| `fonts/` | Anton display font (SIL Open Font License) |
| `manifest.json` | Every rendered video and its status |
| `schedule_log.json` | What has been scheduled on YouTube |
| `logs/last_run.log` | Output of the latest GitHub Action run |

To stop a post, delete it in Metricool's planner before its time. To pause everything, disable the
*Make Shorts* workflow under the Actions tab and pause the scheduled task in Claude.

Data: Cricsheet (cricsheet.org), free ball-by-ball records, credited in every video.
