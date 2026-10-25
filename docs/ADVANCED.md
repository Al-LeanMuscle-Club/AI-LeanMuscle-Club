# Optional advanced features: plans, records, and participation points

[简体中文](ADVANCED.zh-CN.md) · [Back to the community](../README.en.md)

Use these tools when a weekly plan helps you. Conversations, free activity records, and meal records do not require one; choose only the parts you find useful.

## Keep one plan for the week

1. [Create a weekly plan](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml) with the week's Monday, your time zone, and realistic activities. Use one Issue per person per week; public standings default to **No**.
2. Comment on your own plan after an activity. The [member helper](../README.en.md#member-helper) can prepare the text.
3. At the weekend, add `/review` followed by what worked, what got in the way, and what you might adjust. An incomplete week is worth reflecting on too.

This is a format example, not real activity or a training prescription:

```text
S1 | Tuesday | strength | My chosen session | My chosen busy-week alternative
S2 | Thursday | basketball | Practice with a friend
```

Each row is `ID | full English weekday | sport | description | optional alternative`. Use unique IDs from `S1` through `S99` and 1–14 activities for an Active plan. Older three-column rows remain supported. Descriptions and reflections can use any language.

Sport, personal goal, and research-week context are separate choices; you can include several sports in one plan. [Full field and category guide](MEMBER_GUIDE.md#1-make-a-plan-that-fits-this-research-week)

## Record what happened

Use one command per comment and the actual activity date in the declared local time zone:

| Example command | Meaning |
| --- | --- |
| `/done S1 2026-10-27` | Completed S1's planned activity |
| `/fallback S1 2026-10-27` | Completed S1's alternative declared in its fifth column |
| `/partial S1 2026-10-27` | Did part of the activity; half a session of execution credit |
| `/skip S1 2026-10-27` | Recorded a skipped activity; no execution credit |
| `/meal 2026-10-27` | Recorded a meal; no extra points |

Each activity counts once using its latest valid status. Notes and photos are optional. The first successful sync confirms the scored sessions; deleting unfinished sessions afterward cannot improve the score, and extra activities can still be recorded. [Commands, dates, and corrections](MEMBER_GUIDE.md#2-record-a-session-in-a-short-comment)

## Optional weekly participation points

| Component | Maximum points |
| --- | ---: |
| One valid Active weekly plan | 1 |
| Execution: `6 × (completed + 0.5 × partial) / confirmed planned`, rounded to two decimals | 6 |
| A nonempty `/review`, including an incomplete week | 2 |
| A maintainer-approved experience contribution | 1 |
| **Weekly maximum** | **10** |

Full completion and a declared alternative each earn one execution unit. Scores reset weekly and equal totals share a rank. Exercise volume, body weight, calories, photos, and post counts add no extra points. Choose Recovery or comment `/pause` on your plan to leave that week's standings; the pause remains until you edit or remove the comment.

Experience sharing does not require points. When requested, contribution approval must match the author, week, and exact body; a label alone is insufficient. [Full scoring and correction rules](SCORING.md) · [Fictional demo board](../examples/demo-board.en.md)

Choosing **No** keeps your identity out of generated standings; your original Issue, comments, and photos remain public. Body measurements, food details, and photos are always optional. [Public sharing details](MEMBER_GUIDE.md#public-sharing)

## Review, reuse, and tools

The [member helper](../README.en.md#member-helper) starts with conversations and free records. Open its optional weekly-plan tools to find a plan, prepare comments, browse standings and history, or draft next week's plan. Reusing a plan resets public standings to **No** so you can review that choice again.

[Full member guide](MEMBER_GUIDE.md) · [Past reports](../reports/README.md) · [Command-line tools](MEMBER_GUIDE.md#command-line-tools) · [Record examples](../examples/README.en.md)

Deployment and label configuration are maintainer tasks described in [setup](SETUP.md). Members do not need to configure the repository to take part.
