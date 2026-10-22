# AI Lean Muscle Club 💪🤖

**English** | [简体中文](README.zh-CN.md)

**Train models. Train your body.**

A community for AI researchers to make room for exercise, recovery, and a life alongside research.

[Plan your week](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml) · [Browse weekly plans](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues?q=label%3Aweekly-plan) · [Share an experience](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) · [Scoring rules](docs/SCORING.md) · [Maintainer setup](docs/SETUP.md)

<p align="center">
  <a href="assets/club-poster.png"><img src="assets/club-poster.png" alt="AI Lean Muscle Club: For AI Researchers to Keep Healthy. Train models. Train your body. Includes a WeChat group invitation QR code." width="1000"></a>
</p>

The supplied WeChat invitation is marked valid **before October 29, 2026**. If it has expired, ask an existing member for a current invitation. Maintainers can replace `assets/club-poster.png` when the invitation changes.

## Why this club exists

AI research moves quickly. There is always another paper to read, experiment to run, result to check, or deadline to meet. Under pressure, exercise and rest can become the first things we postpone.

I started this club to find fellow researchers who want to take both their research and their health seriously. After ten years of fitness practice alongside AI research, I am still learning how to make that balance sustainable. The original idea was simple: a chat group where we could share experiences, find training partners, and encourage each other to keep going.

More than 200 people joined within a few hours. This repository gives those conversations somewhere to live: a place to share realistic plans, keep lightweight records, learn from missed sessions, and collect useful research-and-fitness workflows.

Our questions are practical:

- How can we protect time for exercise when AI and our research schedules keep changing?
- What training arrangements fit around demanding intellectual work, and how do they affect our own energy and recovery?
- Which tasks can agents actually take off our hands, after checking and rework, and can we use that time for exercise and life?

The goal is a routine we can keep returning to. Good research, health, rest, and life all deserve time.

— Yukang Chen, founder

## Who this is for

AI researchers in universities, research institutes, and industry, including students actively doing AI research. Fitness beginners and experienced athletes are equally welcome. There is no citation threshold, physique requirement, or obligation to join the scoreboard.

"Lean Muscle" is our club name, not a required body type. Members choose their own activities, goals, and level of public participation. Reading, chatting, sharing, or taking a recovery week are valid ways to belong.

## Start in three small steps

### 1. Propose next week's plan

On the weekend, open **one weekly-plan Issue** using the link above. Enter the Monday that starts the week, your IANA time zone, and a few planned sessions with stable IDs:

```text
Week starting: 2026-10-26
Time zone: Asia/Shanghai
Participation mode: Active
Public leaderboard: No

S1 | Tuesday | Strength training, about 30 minutes
S2 | Thursday | Basketball or a brisk walk
S3 | Saturday | Strength training, about 30 minutes

Busy-week fallback: One short session; adjust the remaining plan if needed.
```

Use the Issue form; the example above illustrates its fields. `S1`, `S2`, and `S3` identify your own planned sessions, not prescribed exercises. An Active plan accepts 1–14 unique IDs from `S1` through `S99`. Use full English weekday names, `Monday` through `Sunday`. Write rest days in Notes instead of counting them as training sessions.

Make commitments that fit your week. A lighter deadline-week plan is welcome. Choose **Recovery** if you want to step back from scoring while keeping a place to reflect.

### 2. Leave a short check-in after a planned session

Comment on your own weekly Issue:

```text
/done S1 2026-10-27 | Strength, 30 minutes. Felt tired, so I kept it easy.
```

That is enough. Photos, exercise details, weights, and durations are optional and may follow the command on additional lines. Put one command in each comment. Each planned session counts at most once. Use the session's actual date in your declared time zone; backfilled records are welcome. Future dates and dates outside that plan's week do not count.

No daily PRs, proof photos, or daily workouts are required. A missing check-in means **unrecorded**, not proof that someone did not exercise. You can still share unplanned activity in a normal comment; it does not add extra execution points.

### 3. Reflect on the weekend

Add one comment beginning with `/review`, followed by a short reflection:

```text
/review
What worked: Two short sessions were easier to protect than one long session.
What got in the way: An experiment ran late on Thursday.
Next week: Move that session earlier and keep the fallback realistic.
```

Reflection earns the same credit whether the week went to plan or not. You can optionally note energy, fatigue, sleep, or an agent workflow that freed time. We do not score research output or personal health outcomes.

## Weekly points: a small encouragement

Scores describe **recorded participation and follow-through on a personal plan**. They are not a fitness assessment, a health score, or a comparison of training ability.

| Component | Weekly points | Rule |
| --- | ---: | --- |
| Valid Active plan | 1 | One valid weekly Issue per person |
| Recorded plan execution | 0–6 | `6 × completed planned sessions / planned sessions`, rounded to two decimals |
| Weekly reflection | 2 | One nonempty author `/review` comment, independent of success |
| Helpful contribution | 0–1 | One eligible experience Issue approved by a maintainer |
| **Maximum** | **10** | No extra credit for more training or more posts |

**Example:** Plan three sessions, record two, and write a reflection: `1 + 6 × 2/3 + 2 = 7` points. An approved contribution makes it `8`.

Weights lifted, distance, workout duration, calories burned, weight loss, appearance, photos, likes, and citation counts do not earn points. Different personal commitments can receive the same score. An easy plan can earn full completion credit, so the board should be read with that context.

Scores reset every week. Leaderboard participation is **opt-in**; select `Yes` in the form to display your GitHub handle. Equal totals share a rank. The earliest valid weekly Issue is used if someone submits duplicates. Recovery mode or an author `/pause` comment removes that week's score from the leaderboard. To resume after `/pause`, edit or remove that pause comment; it is not a toggle command.

Plans may change. Explain changes in a comment, keep completed session IDs stable, and avoid rewriting past commitments simply to increase a score. This first version evaluates the **current declared plan**, not a frozen historical snapshot. It is an honor-based community with no monetary prizes. See the [full scoring and edge-case rules](docs/SCORING.md).

## Experiences, food, and research workflows

Share something specific that other members can use: a realistic training plan, an inexpensive meal idea, a return-to-training experience, or an agent-assisted research workflow. Include what you tried, what changed, and the limits of the experience.

For an agent workflow, a useful format is:

> Task before automation → agent's role → checking/rework needed → time actually saved → whether that made room for exercise or life.

An experience Issue is eligible for at most one contribution point in its stated week when a maintainer adds `points-approved`. Multiple posts and approval labels cannot exceed the weekly cap. Ordinary peer encouragement is welcome without requiring points.

Food sharing is optional. A photo plus a little context about ingredients, portions, and preparation can start a useful conversation. In this version, there is **no automatic meal health score or separate food-point system**. An agent may describe visible food, ask clarifying questions, and suggest an optional improvement; it should acknowledge what it cannot infer. A single meal image does not establish someone's overall diet quality, and image-based estimates can be inaccurate. See [WHO's healthy-diet principles](https://www.who.int/news-room/fact-sheets/detail/healthy-diet) and [a meal-photo evaluation study](https://doi.org/10.3390/nu17040607).

## What automation does

| Function | First version |
| --- | --- |
| Weekly plan and check-in collection | GitHub Issue forms and author comments |
| Completion and score arithmetic | Deterministic Python rules, no LLM or paid API required |
| Public weekly board | GitHub Actions updates this README and `reports/` |
| Useful-experience approval | Human maintainer assigns `points-approved` |
| AI-written summaries and workflow suggestions | Optional, human-reviewed process described in [Agent guide](docs/AGENT_GUIDE.md) |
| Automatic medical advice or meal-health ranking | Not included |

The included workflow is scheduled for **09:15 Asia/Shanghai daily** and can also be run manually. It refreshes the current and previous reporting weeks, which allows recent backfills; a manual run with a specific week date displays and refreshes that week instead. The next normal run restores the current-and-previous-week view. Reporting-week selection uses Asia/Shanghai, while check-in dates are interpreted in each participant's declared time zone. Reports remain editable snapshots rather than irreversible settlements. Scheduled runs can be delayed by GitHub.

Automation starts only after the files are in the repository's default branch and the [setup steps](docs/SETUP.md) are completed. This repository does not contain a configured external AI agent or credentials.

## Weekly community board

<!-- CLUB:START -->
The weekly board has not been generated yet. After setup, the scheduled or manual workflow will replace this section with real participation data. No example members or scores are presented as real activity.
<!-- CLUB:END -->

## Community rules

1. **Keep participation voluntary.** Joining the chat does not commit anyone to public logging or ranking. Recovery and restarting are welcome.
2. **Support realistic plans.** Respect different starting points, activities, work schedules, and recovery needs. Avoid pressure to train through pain or illness.
3. **Record honestly and briefly.** Log your own sessions, use actual dates, and explain plan adjustments. No photo verification or elaborate anti-cheating system.
4. **Help without judging bodies.** No appearance shaming, unsolicited physique ratings, credential competitions, or claims that one routine fits everyone.
5. **Keep shared material yours to share.** Do not post someone else's private information, identifiable photos, or confidential research material without permission. No advertising or spam.
6. **Treat public participation as public.** Issues, comments, images, and committed history may be visible and retained. Opting out of ranking does not make an Issue private. Photos, weight, body-fat measurements, and health history are never required.
7. **Use agents with clear limits.** Suggestions and summaries are references, not diagnoses. Exact score arithmetic follows public rules. Keep human judgment for disputes and contribution approval.

See [Code of Conduct](CODE_OF_CONDUCT.md), [Contributing](CONTRIBUTING.md), and [Scoring](docs/SCORING.md) for details and corrections.

## How we will improve it

Start with a two-week pilot of willing participants. Keep the chat useful for everyone, including people who do not use GitHub for check-ins. Review whether people return, whether logging stays quick, and whether they actually find time for exercise and recovery.

Small voluntary training-partner groups can provide encouragement that a scoreboard cannot. With participants' consent, reusable lessons can be curated into training resources and agent workflow examples. New features should earn their place by reducing effort or improving support.

Feature proposals, corrections, and code contributions are welcome. Daily training records belong in weekly Issue comments; reusable documentation and tooling improvements belong in PRs.
