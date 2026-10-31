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

**Files**

| File | What it is |
| --- | --- |
| `cricket_videos.py` | Renders the videos (worm, compare, race, player) with original music |
| `planner.py` | Chooses what to render each day and updates the manifest |
| `queue.json` | Ideas waiting to be rendered |
| `manifest.json` | Every rendered video and its status |
| `schedule_log.json` | What has been scheduled on YouTube |
| `logs/last_run.log` | Output of the latest GitHub Action run |

To stop a post, delete it in Metricool's planner before its time. To pause everything, disable the
*Make Shorts* workflow under the Actions tab and pause the scheduled task in Claude.

Data: Cricsheet (cricsheet.org), free ball-by-ball records, credited in every video.
