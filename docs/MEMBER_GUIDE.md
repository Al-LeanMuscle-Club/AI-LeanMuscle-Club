# Member guide

**English** | [简体中文](MEMBER_GUIDE.zh-CN.md)

Start with a free activity record, a meal record, or a conversation. A weekly plan is optional; use one weekly Issue for planned check-ins and reflection if you choose it. Daily pull requests, body photos, exercise measurements, and leaderboard participation are never required.

All examples below are fictional templates, not prescribed training plans or actual member activity. Choose your own activities, schedule, and amount of detail.

## Choose how to take part

- [Activity record](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=activity-record.yml): record what you did without a plan or scoring commands; these Issues do not enter standings.
- [Meal record](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=meal-record.yml): record food without a plan, calories, or photographs; these Issues do not enter standings or the weekly-plan meal-day summary.
- [Discussions](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/discussions): introduce yourself, ask questions, share, or find a partner once maintainers enable the categories.
- **Weekly training plan**: choose the structured plan below if you want to follow your own commitments and optionally join the weekly participation board.

See [six short sets of fictional examples](../examples/README.md). Original Issues and Discussions are public whichever route you choose.

## 1. Make a plan that fits this research week

Open the **Weekly training plan** Issue form. Set the Monday starting the week, your IANA time zone, participation mode, and leaderboard choice. Add an optional **Primary goal** and **Research week** to help members find relevant plans.

| Field | Choices | Meaning |
| --- | --- | --- |
| Primary goal | `fat-loss`, `muscle-gain`, `cardio`, `skill`, `habit` | The main focus for this stage; you can change it in a future week's plan. |
| Research week | `regular`, `deadline`, `travel` | Context for your schedule, not a score multiplier. |
| Participation mode | `Active`, `Recovery` | Recovery weeks stay outside scored standings. |
| Public leaderboard | `No`, `Yes` | Explicit consent to include your handle and permitted summary fields in generated reports. |

Missing optional classifications use `habit` and `regular`. Your goal does not restrict which activities you can do. For example, a member focused on muscle gain can plan strength training and basketball in the same week.

In **Planned sessions**, write one line per session:

```text
S1 | Tuesday | strength | A short session I chose | My at-home alternative
S2 | Thursday | basketball | Practice with a friend
S3 | Saturday | running | My chosen route
```

The columns are `ID | weekday | sport | description`, with an optional fifth column for that session's busy-week alternative. Use full English weekdays, `Monday` through `Sunday`, and stable, unique IDs from `S1` through `S99`. An Active plan has 1–14 sessions. Rest days go in Notes.

Sport choices are `strength`, `basketball`, `running`, `swimming`, `cycling`, `walking`, `mobility`, and `other`. Choose one primary sport per session; describe a mixed session in its notes. Different sessions in the same week can have different sports.

The older three-column format `S1 | Tuesday | My activity` still works and is classified as `other`. Use four columns when you want activity filtering. Do not put extra `|` characters inside a description or alternative; they separate columns.

Write any session-specific alternative in advance. The general **Busy-week fallback** field remains useful context, but a `/fallback` completion requires an alternative in the fifth column of that particular session. Keep the original plan and explain changes rather than rewriting past commitments to manufacture a score.

The first successful report sync confirms a scoring snapshot of the week’s sessions. Later edits can update your current schedule, but deleting unfinished activities does not shrink the confirmed scoring denominator; added sessions can be recorded without adding execution points. Reports distinguish the current plan from the confirmed plan. Leave an explanation for changes and keep completed session IDs stable. See [scoring and corrections](SCORING.md) for the confirmation boundary.

## 2. Record a session in a short comment

Put one command on the first nonempty line of a comment on your own weekly Issue. Use the actual local activity date in the time zone declared in the plan. You may backfill a past date within that Monday–Sunday week; future dates do not count.

| Command | Meaning | Execution credit |
| --- | --- | --- |
| `/done S1 2026-10-27` | Completed the planned session | Yes |
| `/fallback S1 2026-10-27` | Completed S1's predeclared fifth-column alternative | Yes, at most once for S1 |
| `/partial S1 2026-10-27` | Did some of the session | Half a session of execution credit; not a full completion |
| `/skip S1 2026-10-27` | Did not do this session | Recorded, no completion credit |

Add optional notes after `|` or on later lines:

```text
/done S2 2026-10-29 | Basketball practice with a friend.
Focus: the skill I wanted to work on.
Energy afterward: felt more settled.
```

For one session, the latest valid status replaces earlier status records; statuses are not added together. If you accidentally record the wrong state, correct it with a later valid record or edit/remove the incorrect comment. A full session and its alternative never count as two sessions.

Only your own records on your own plan count. Keep different commands in different comments; a comment containing a second command line is ambiguous and is not counted. Ordinary discussion and optional notes are welcome. Missing records mean **unrecorded**, not proof that someone did not exercise.

### Optional details for different sports

| Activity | Details you may find useful |
| --- | --- |
| Strength | Exercise names, sets, repetitions, load, adjustments |
| Basketball | Skill practice or game, focus, duration, observations |
| Running | Duration, distance, pace, perceived effort |
| Swimming or cycling | Duration, distance, observations |
| Walking or mobility | Duration, chosen activities, how the session fitted the day |

These are optional personal observations, not required measurements or ranking criteria. Free-text details and health measurements are not copied into generated report data. They remain public in the source Issue if you choose to post them.

## 3. Add food records only if they help you

A food record is an optional comment on the same weekly Issue:

```text
/meal 2026-10-28 | Lunch
Food and portion: my description; photo optional.
Estimate source: package label / weighed recipe / personal estimate / model estimate.
Estimated energy range: optional; leave blank when unknown.
Assumptions or unknowns: portion size, cooking oil, sauce, or other missing context.
What I want to learn: one observation about meal planning during this research week.
```

Use your declared local time zone and a date within that plan's week. You can log without calories, a photo, or a complete recipe. If you record numbers, keep the source and uncertainty beside them and correct estimates when you learn more. A model estimate is not a measurement.

The report can show the number of distinct valid meal-record dates on your weekly plan: two meals on the same date count as one day. This is a record count, not a meal rating. Independent Meal record Issues stay outside that summary.

The repository does not run an automatic calorie estimator or meal-health grader. Food records earn no separate points, and eating less or posting more photos cannot increase a score. A thoughtful food reflection can form part of your ordinary weekly reflection or an experience Issue; existing weekly limits still apply. Raw food notes, images, and calorie numbers are not exported to the generated public index or report JSON.

## 4. Reflect, including on an incomplete week

Post `/review` followed by a few sentences:

```text
/review
What fitted this week: the session I reserved before starting experiments.
What got in the way: a deadline changed my evening schedule.
Next week: keep the realistic alternative and adjust one time slot.
Optional Agent note: task delegated, checking/rework, net time saved,
and whether I actually used that time for movement or rest.
```

Reflection receives the same two points after an incomplete week. Research output, citation counts, body measurements, and health outcomes are not scored.

The weekly maximum stays **10**: plan 1, execution 0–6, reflection 2, and an approved experience contribution 0–1. Execution uses full/fallback = 1 and partial = 0.5 against confirmed sessions. The full-completion percentage still counts only full/fallback sessions. Scores measure participation, not athletic ability. See [the full scoring rules](SCORING.md) and [fictional ranking examples](../examples/ranking.md).

Discussion replies do not automatically grant contribution points. An experience Issue needs both `points-approved` and a trusted repository approval entry matching its current body, author, and week. Editing an approved body requires review again; labels alone do not grant credit. Maintainers prepare approval records for review using the process in [setup](SETUP.md).

To step away from scoring, choose `Recovery` or comment `/pause`. A pause stays in effect until you edit or remove that pause comment; posting it again does not toggle participation back on.

## Browser helper

The [member helper](../tools/index.html) prepares search links, check-in text, and reusable plan drafts without asking for credentials or submitting posts. The GitHub file viewer shows the HTML source and does not run the page. Download the repository and open `tools/index.html` locally. If your browser restricts local-file data loading, run this from the repository root:

```bash
python3 -m http.server 8000
```

Then open [the local helper](http://localhost:8000/tools/). A hosted copy becomes available only after maintainers configure Pages and enable its deployment workflow; see [setup](SETUP.md). Review generated text and paste it into GitHub yourself.

In **My public records**, enter your full GitHub username to view the loaded public weekly-plan summaries. Below those summaries, **Review my free records** prepares separate links to your `activity-record` and `meal-record` Issues, including open and closed records, in the selected repository. These search links work even without a weekly plan or published reports. Open them on GitHub to read your records; free records do not add points or enter the weekly-plan day counts, and the helper does not download them or ask for a token.

The selected weekly report and each personal-history row show their recorded scoring-rule version. **v2** uses half credit for partial sessions, a confirmed plan denominator, and content-bound contribution approvals. If a historical report has no version, the page says the version was not recorded and preserves its original scores; it does not guess an older version or recalculate it with today's formula. A declared version without a supported explanation retains its own version number and source scores. The website shows its latest published snapshot; see [setup](SETUP.md) for manual publication and optional automatic publication after report updates.

## Command-line tools

Command-line tools are also available from the repository root. Global options go **before** `find`, `carry`, or `check`. For live reads, use the read credentials described in [setup](SETUP.md); do not paste tokens into an Issue or the browser helper.

Find this week's plan:

```bash
python scripts/member_tools.py --repository Al-LeanMuscle-Club/AI-LeanMuscle-Club find --handle YOUR-HANDLE --week 2026-10-26
```

Draft a later week's plan from an existing Issue:

```bash
python scripts/member_tools.py --repository Al-LeanMuscle-Club/AI-LeanMuscle-Club carry --issue 123 --week 2026-11-02 --output next-week.md
```

This writes a draft only. It resets public leaderboard consent to **No**. Review the new week, goal, schedule, alternatives, and visibility before opening an Issue; do not create a duplicate if you already have a plan for that week.

Check a plan or a proposed comment before posting:

```bash
python scripts/member_tools.py --repository Al-LeanMuscle-Club/AI-LeanMuscle-Club check --issue 123
python scripts/member_tools.py --repository Al-LeanMuscle-Club/AI-LeanMuscle-Club check --issue 123 --comment-file check-in.txt
```

For offline work, use the global `--fixture /path/to/synthetic-issues.json` option before the subcommand. Synthetic data is for testing only, not a source for a real community report.

## Public sharing

All Issues, comments, and attached photos in this public repository are public, including posts by people who select **No** for the leaderboard. The generated index and report rows include only consenting Active participants; this does not change the visibility of the original posts. Opted-in rows can include goal and research-week classifications, sports, session status/dates, completion counts, execution credit, confirmed/current plan summaries, meal-record day counts, and points. They exclude free-text descriptions, calorie numbers, and personal notes.

Body photos, exact weight, health history, precise location, and confidential research information are never required. Keep any information you want private outside the public repository. For reusable resources and examples, see [the examples directory](../examples/README.md); for questions and finding partners, see [community discussions](COMMUNITY.md).
