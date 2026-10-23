# Weekly participation points

Our points recognize a small commitment, reported follow-through, reflection, and useful support for other members. They do not measure health, athletic ability, appearance, or research productivity.

The first two weeks are a pilot. We will review whether the rules help people make time for exercise and whether recording takes little effort before adding more features.

## The 10-point model

| Component | Points | What counts |
| --- | ---: | --- |
| Weekly plan | 1 | A valid active plan for the selected week. |
| Reported execution | 0–6 | `round(6 × completed sessions / planned sessions, 2)`, capped at 6. |
| Weekly reflection | 2 | A nonempty `/review` comment by the plan's author, including an honest reflection on an incomplete week. |
| Community contribution | 0–1 | At least one eligible experience issue approved by a maintainer for that week. |
| **Maximum** | **10** | More training or more posts cannot raise the weekly maximum. |

For example, someone plans three sessions, reports two completed sessions, and writes a reflection: `1 + 6 × (2/3) + 2 = 7` points. An approved community contribution raises the total to 8.

There are no extra points for lifting heavier, running farther, training longer, losing weight, eating less, or posting body photographs. A beginner can receive the same execution points as an experienced athlete by following their own declared plan.

## What makes a valid plan

Create one issue using the weekly-plan form. Its fields are:

| Field | Format |
| --- | --- |
| Week starting | An ISO date, `YYYY-MM-DD`, that is a Monday. |
| Time zone | An IANA name such as `Asia/Shanghai`, `America/New_York`, or `Europe/Zurich`. |
| Participation mode | `Active` or `Recovery`. |
| Public leaderboard | `Yes` or `No`; `No` is the form default. |
| Primary goal | Optional: `fat-loss`, `muscle-gain`, `cardio`, `skill`, `habit`; omitted or unanswered defaults to `habit`. |
| Research week | Optional: `regular`, `deadline`, `travel`; omitted or unanswered defaults to `regular`. |
| Planned sessions | For an active week, 1–14 activities with unique IDs from `S1` to `S99`. |
| Busy-week fallback | A practical alternative if research or life changes the week. |
| Notes | Optional context that you are comfortable sharing publicly. |

Write one activity per line, for example:

```text
S1 | Monday | strength | Gym session | Short home session
S2 | Thursday | basketball | Shooting practice
S3 | Saturday | running | Easy run
```

Use four columns: `ID | day | sport | description`. An optional fifth column declares the fallback for that same session. Recognized sports are `strength`, `basketball`, `running`, `swimming`, `cycling`, `walking`, `mobility`, and `other`. Descriptions and fallbacks can be in any language but cannot contain extra pipe (`|`) characters. The old three-column format `ID | day | description` remains valid and uses `other` in generated classifications; no activity is guessed from prose.

Use full English weekday names, Monday through Sunday; abbreviations such as Mon are not accepted. These are examples, not exercise prescriptions. Choose activities and a schedule appropriate for your circumstances. Plan rest days too, but do not add rest days as completed training sessions to increase the score.

The earliest valid weekly-plan issue from a GitHub account is its canonical plan for that week; a lower issue number breaks a creation-time tie. Duplicate plans do not stack points. Use the original issue for corrections rather than opening another plan to improve a score.

## Recording a session

Comment on your own weekly issue:

```text
/done S1 2026-10-26 | Strength, 30 min. Shortened the final set.
```

The note after `|` is optional. Put the command on the first nonempty line; extra notes, exercise details, and image attachments may follow on later lines. Use one command per comment. Comments with additional `/done`, `/fallback`, `/partial`, `/skip`, `/meal`, `/review`, or `/pause` command lines are ignored as ambiguous.

| Command | Meaning | Execution credit |
| --- | --- | --- |
| `/done S1 YYYY-MM-DD` | Completed the planned session | Counts once |
| `/fallback S1 YYYY-MM-DD` | Completed S1's declared fifth-column alternative | Counts once as the same S1 |
| `/partial S1 YYYY-MM-DD` | Partly completed the session | No execution credit |
| `/skip S1 YYYY-MM-DD` | Chose not to complete the session | No execution credit |

The session ID must exist in the plan. A `/fallback` is valid only when that session has a nonempty fifth-column alternative. Text in the general `Busy-week fallback` field is planning context and does not automatically give every session a fallback.

Only the plan author's comments count. The latest valid status for each session replaces its previous status, using `updated_at` when present and otherwise `created_at`; equal timestamps are resolved deterministically. A later `/partial` or `/skip` can therefore correct an earlier completion. A session never counts twice, even if both the full session and its alternative were recorded. Delete, edit, or supersede a mistaken status instead of opening a duplicate plan.

The actual session date must fall in the plan's Monday–Sunday week and must not be later than the effective comment timestamp's local date or the report's current local date. All such dates use the participant's declared IANA time zone. An edit dated after the report's `as_of` instant is ignored rather than reconstructed as a historical comment; an edit cannot precede its creation timestamp. Reports evaluate the data supplied at generation time, not an immutable event history. Honest backfilling is welcome.

A friend's encouragement cannot submit a completion for you. Unsupported commands, unknown session IDs, malformed dates, unrecognized sports in new-format rows, and future-dated records do not grant execution points. The member checker can explain format problems before submission.

An unreported session receives no execution points yet; this is not a statement that the person did not exercise. Honest backfilling with the actual session date is welcome. Missing a day of logging never resets a streak or creates negative points.

## Reflecting and adjusting

A short reflection is enough:

```text
/review
Completed 2 of 3 sessions. A deadline displaced Thursday's plan.
The short session was easier to keep than expected.
Next week I will reserve two shorter windows earlier in the day.
```

Reflection points do not depend on having a successful week. Returning after an interruption is welcome. Optional prompts include the week's research pressure, which scheduling adjustment helped, and an Agent workflow's net time saved after setup, checking, and rework. Neither time savings nor reported health or research outcomes change points.

You may edit a plan when circumstances change. Add a comment explaining the adjustment, keep completed session IDs stable, and make changes to future activities where possible. The scorer uses the **current declared sessions**, not a frozen original plan. This is deliberately an honor-based system: adjusted completion rates are not suitable for comparing how much work different people did. Do not rewrite a past plan simply to manufacture full completion.

Choose `Recovery` for a week focused on recovery, or post `/pause` on your active weekly issue when you need to step away. Recovery and paused weeks are excluded from scored standings. They carry no penalty or debt, and members can still share and support others. A pause persists until you edit or remove that pause comment; posting `/pause` again does not resume scoring.

## Community contribution approval

Use the experience-sharing issue form and specify the same `Week starting` date. Examples of eligible contributions include:

- A practical training adjustment for a deadline week.
- A first-hand lesson about making an exercise habit sustainable.
- A helpful response or reusable resource documented in an experience issue.
- An Agent workflow with an honest account of checking, rework, time saved, and how that time was used.
- A thoughtful food or meal-planning reflection with useful context.

A maintainer can add the `points-approved` label when an experience is relevant, specific, and useful to the community. This approval is not a medical endorsement. Likes, post length, polished photographs, and posting frequency do not determine points. Any number of approved contributions earns at most **one contribution point per author per week**. A contribution can still be valuable without earning points or having an active plan.

## Optional food records

A separate comment may begin with `/meal YYYY-MM-DD`, followed by text, optional photographs, and any context the member wants public. A meal record has the same author and week/date checks as other dated records, adds no execution or contribution points by itself, and never substitutes for a training session or weekly reflection.

Calorie numbers and nutritional details are optional. If included, label the source (packaging, weighed recipe, personal estimate, or model estimate), portion assumptions, unknown ingredients, and any estimated range. Missing or uncertain quantities should stay unknown. There is no configured automatic nutrient-estimation service, shared calorie target, body-weight reward, or meal-health grade. A helpful food-planning reflection can be considered under the ordinary experience-Issue approval process; it does not raise the contribution cap.

Raw meal contents, calorie figures, body measurements, check-in prose, and photographs are not copied into the generated report or personal index. They remain visible in their original public Issue. Members who want private food or body records should keep them outside this public repository.

## Standings, corrections, and automation

- Public standings and named indexes include only active members who selected `Yes` for the public leaderboard. Recovery and paused members are excluded.
- The README contains a compact overview and links; full records and rankings are in weekly reports. Structured per-sport counts, goal filters, and session statuses describe these same opted-in active members, not the whole group. Anonymous overall participant/recovery counts can include other valid plans.
- Optional exercise metrics and primary goals support personal observation. They never multiply the score, define a health outcome, or create a cross-sport calories/distance/weight leaderboard.
- Scores reset for each week. They are not lifetime totals. Equal total scores receive the same rank.
- Completion rates describe each member's own current plan; they are not comparable measures of health or fitness.
- The Python scorer applies the published rules. An optional Agent may summarize experiences and draft a weekly report, but does not invent completions, approve its own contributions, or change scoring rules.
- A score row links to its source issue. Correct an inaccurate record and ask for a report refresh if needed. Maintainers should explain any manual correction publicly without exposing personal information.
- All submitted issues and comments in a public repository remain public, even when leaderboard participation is `No`. Leaderboard consent controls the standings, not access to the underlying thread.

See [the setup guide](SETUP.md) for report generation and [the Agent guide](AGENT_GUIDE.md) for the division of responsibilities.
