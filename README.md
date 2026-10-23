# AI Lean Muscle Club 💪🤖

**English** | [简体中文](README.zh-CN.md)

**Train models. Train your body.**

A community for AI researchers to make room for exercise, recovery, and a life alongside research.

[Log a workout](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=activity-record.yml) · [Share a meal](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=meal-record.yml) · [Meet the community](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new/choose) · [Weekly participation board](reports/README.md)

## Choose how to join today

| I want to… | Start here |
| --- | --- |
| Record today's movement without making a plan | [Quick workout record](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=activity-record.yml) |
| Save a meal, a photo, or a food-preparation idea | [Food record](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=meal-record.yml) |
| Introduce myself, ask a question, or find a partner | [Community conversations](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new/choose) · [Examples](examples/README.en.md) |
| Make a weekly plan and optionally join the board | [Weekly plan](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml) · [Participation rules](docs/SCORING.md) |

A photo or one sentence is welcome. Free workout and food records do not require a weekly plan and do not enter the ranking. All records posted here are public. Structured weekly records can also show training days, meal-record days, and partial completions without awarding points for food quantities or body metrics.

[Member helper and weekly standings](tools/index.html) · [Newcomer, training, food, partner, Agent, and ranking examples](examples/README.en.md). The helper runs locally or after [Pages setup](docs/SETUP.md#9-optional-browser-helper-and-pages-deployment); GitHub's source viewer displays its HTML. Community Issue forms become available after they are merged into the default branch.

<p align="center">
  <a href="assets/club-poster.png"><img src="assets/club-poster.png" alt="AI Lean Muscle Club: For AI Researchers to Keep Healthy. Train models. Train your body. Includes a WeChat group invitation QR code." width="1000"></a>
</p>

The supplied WeChat invitation is marked valid **before October 29, 2026**. If it has expired, ask an existing member for a current invitation. Maintainers can replace `assets/club-poster.png` when the invitation changes.

Read about [why this club exists](docs/ABOUT.md#why-this-club-exists) and [who this is for](docs/ABOUT.md#who-this-is-for).

## Optional weekly plan in three small steps

1. [Open one weekly plan](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml). Choose your time zone, current goal, research-week rhythm, and a realistic set of sessions. Public standings are **off by default**.
2. Comment on that Issue after a session. A short command is enough; photos and exercise details are optional.
3. At the weekend, add `/review` followed by a few sentences about what worked, what changed, and how you will adjust.

An illustrative plan, not an exercise prescription:

```text
S1 | Tuesday | strength | Gym session | Short home session
S2 | Thursday | basketball | Shooting practice
S3 | Saturday | running | Easy run
```

Use full English weekdays and stable IDs `S1`–`S99`. The optional fifth column declares that session's busy-week fallback. Old three-column plans still work. Descriptions, comments, and reflections may be in any language.

```text
/done S1 2026-10-27 | Kept the session short.
```

Use `/fallback S1 YYYY-MM-DD` when completing S1's confirmed fallback; `/partial` earns half of that session's execution credit and `/skip` earns none. Each session counts once, using its latest valid status. The first successful report confirms the scored sessions; later edits are shown separately and deleting unfinished sessions cannot raise the score. Put each command in a separate comment. [Full instructions, meal logs, and examples →](docs/MEMBER_GUIDE.md)

**Quick tools:** [Find my plan / prepare a check-in](tools/index.html) ([open locally or configure hosting](docs/MEMBER_GUIDE.md#browser-helper)) · [Reuse last week's plan](docs/MEMBER_GUIDE.md#command-line-tools) · [Browse opt-in report data](reports/index.json)

## Find your people

| Filter | Available values |
| --- | --- |
| Activity, per session | `strength`, `basketball`, `running`, `swimming`, `cycling`, `walking`, `mobility`, `other` |
| Primary goal, per week | `fat-loss`, `muscle-gain`, `cardio`, `skill`, `habit` |
| Research week | `regular`, `deadline`, `travel` |

A member can lift, play basketball, and run in the same week. Goals and sports are independent; beginners and mixed plans are welcome. Weight, sets, pace, distance, energy, and fatigue are optional notes, never points multipliers. [Example templates →](examples/README.en.md)

## Weekly community board

<!-- DEMO:START -->

### Fictional demo leaderboard — week of 2026-10-12

**Static fictional examples, not real members, check-ins, or results. These do not enter the live community counts or standings below.** The demo cutoff is 2026-10-19 12:00 UTC, with six ranked fictional members and one fictional Recovery member from offline sample data.

| Rank | Fictional member | Sports | Full / planned | Partial | Training days | Meal days | Points / 10 |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | [demo-aurora](examples/demo-training-records.md#demo-aurora) | Running, Strength, Swimming | 3 / 3 | 0 | 3 | 3 | **9** |
| 2 | [demo-birch](examples/demo-training-records.md#demo-birch) | Basketball, Cycling, Mobility | 2 / 3 | 1 | 3 | 2 | **8** |
| 3 | [demo-cedar](examples/demo-training-records.md#demo-cedar) | Basketball, Cycling, Running, Strength | 2 / 4 | 2 | 4 | 1 | **7.5** |
| 4 | [demo-ember](examples/demo-training-records.md#demo-ember) | Basketball, Swimming, Walking | 2 / 3 | 1 | 3 | 2 | **6** |
| 4 | [demo-delta](examples/demo-training-records.md#demo-delta) | Mobility, Walking | 1 / 2 | 0 | 1 | 1 | **6** |
| 6 | [demo-finch](examples/demo-training-records.md#demo-finch) | Mobility, Strength, Walking | 0 / 3 | 2 | 2 | 2 | **5** |

Full/fallback completion earns 1 execution unit; partial earns 0.5. Training and meal-record days add no points. Recovery is outside the board.

[Full fictional plans, raw records, and score components](examples/demo-training-records.md) · [Synthetic leaderboard data](examples/demo-leaderboard.json)

<!-- DEMO:END -->

<!-- CLUB:START -->

### Week starting 2026-10-19

Participants: **0** · Recovery/paused: **0**

Opted-in active members: **0** · Recorded sessions: **0/0** · Weekly reflections: **0**

Session totals describe opted-in active members' own plans; they are not health or athletic rankings.

Scoring rules: v2. Full/fallback = 1, partial = 0.5; the confirmed plan fixes the denominator.

[Full weekly report](reports/2026-10-19.md) · [Public data](reports/2026-10-19.json) · [Find my plan / browser helper](tools/index.html)

Updated: 2026-10-23T08:53:35.471818Z

### Week starting 2026-10-12

Participants: **0** · Recovery/paused: **0**

Opted-in active members: **0** · Recorded sessions: **0/0** · Weekly reflections: **0**

Session totals describe opted-in active members' own plans; they are not health or athletic rankings.

Scoring rules: v2. Full/fallback = 1, partial = 0.5; the confirmed plan fixes the denominator.

[Full weekly report](reports/2026-10-12.md) · [Public data](reports/2026-10-12.json) · [Find my plan / browser helper](tools/index.html)

Updated: 2026-10-23T08:53:35.471818Z

<!-- CLUB:END -->

The homepage stays short as participation grows. Full opt-in standings and session-status records live in [weekly reports](reports/README.md); free-text notes, meal contents, body measurements, and raw comments are not copied into generated reports. Selecting `No` hides your identity from generated standings and indexes, **not from your original public Issue**.

## A small encouragement: 10 points per week

| Component | Maximum points |
| --- | ---: |
| One valid Active weekly plan | 1 |
| Personal plan execution: `6 × (completed + 0.5 × partial) / confirmed planned`, rounded to two decimals | 6 |
| A nonempty weekly `/review`, including an incomplete week | 2 |
| A useful experience Issue approved by a maintainer | 1 |
| **Weekly maximum** | **10** |

A confirmed fallback counts as completion of the same session; partial completion receives half credit and skipping receives none. The participation board shows each component separately and recognizes each person's declared commitment. More training, calorie burn, weight loss, photographs, or posts cannot raise the cap. Scores reset weekly; participation is voluntary and equal totals share a rank. Recovery mode or an author `/pause` removes the week from standings without a penalty. Contribution approval is bound to its author, week, and exact content in a maintainer-reviewed ledger; a label alone cannot grant a point. [Scoring and correction rules →](docs/SCORING.md)

## Keep conversations useful

Use [community Issues](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new/choose) for newcomer introductions, training and recovery, food sharing, research and Agents, partners and events, and announcements. Choose the matching form and continue in its comments. Keep lasting resources in documentation or PRs. Community posts and replies do not automatically earn contribution points; use an [experience Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) for the existing approval process. [Community organization →](docs/COMMUNITY.md)

Optional `/meal YYYY-MM-DD` comments can contain food descriptions, photographs, portions, and calorie estimates with their source and uncertainty. No food-photo bonus, calorie target, automatic model estimate, or meal-health score is configured. Detailed food and body records are always optional. [Food-log examples →](docs/MEMBER_GUIDE.md#3-add-food-records-only-if-they-help-you)

For agent workflows, share **the task → agent's role → checking/rework → net time saved → whether it made room for exercise or rest**. The included Python tools calculate scores; optional AI summaries need human review. [Agent guide →](docs/AGENT_GUIDE.md)

## Participation and setup

Be honest, kind, and respectful of different bodies and schedules. Recovery and restarting belong here. Do not pressure others to train, demand photographs, post private research, share someone else's information without permission, or advertise. Public Issues, comments, images, and committed history may be copied and retained. Opting out of standings does not make records private.

The reporting workflow refreshes the current and previous Asia/Shanghai reporting weeks on relevant Issue/comment changes and at **09:15 Asia/Shanghai daily**, once enabled on the default branch. Session dates use each member's declared time zone. Reports are revisable snapshots, and scheduled runs may be delayed. Repository settings, scoring labels, and default-branch Issue forms require [maintainer setup](docs/SETUP.md). There is no connected external AI model or WeChat collector.

[Member guide](docs/MEMBER_GUIDE.md) · [Contributing](CONTRIBUTING.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Maintainer setup](docs/SETUP.md)
