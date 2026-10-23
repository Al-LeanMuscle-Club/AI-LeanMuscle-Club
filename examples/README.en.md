[简体中文](README.md) | English

# Optional record templates

These are fictional examples of record formats, not actual participation, training prescriptions, or nutrition targets. Copy only fields you find useful. Do not publish these examples as real community activity.

See [the member guide](../docs/MEMBER_GUIDE.md) for accepted commands and scoring. Put each command in its own comment on your weekly Issue. Optional prose after it does not add points or enter generated report data; it remains public in the source Issue.

## Six community examples

Every file contains two short fictional scenarios. They are reference material, not real participation data.

| Topic | English examples | Chinese examples | Where to participate |
| --- | --- | --- | --- |
| Newcomer introductions | [Beginners](beginners.en.md) | [中文](beginners.md) | [Newcomer introduction Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=beginners.yml) · `[Hello]` |
| Training conversations and activity records | [Training and recovery](training-and-recovery.en.md) | [中文](training-and-recovery.md) | [Training Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=training-and-recovery.yml) / [Activity record](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=activity-record.yml) |
| Food records and sharing | [Nutrition](nutrition.en.md) | [中文](nutrition.md) | [Nutrition-sharing Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=nutrition.yml) / [Meal record](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=meal-record.yml) |
| Finding partners | [Buddies and events](buddies-and-events.en.md) | [中文](buddies-and-events.md) | [Buddies Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=buddies-and-events.yml) · `[Buddies]` |
| Research and Agents | [Research and Agents](research-and-agents.en.md) | [中文](research-and-agents.md) | [Research and Agents Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=research-and-agents.yml) / [Experience sharing Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) |
| Participation rankings | [Ranking](ranking.en.md) | [中文](ranking.md) | Isolated offline examples; never `reports/`. Use a [weekly-plan Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml) for real scored records. |

All community conversations use Issue forms. Topics are identified by title prefixes such as `[Hello]`, `[Training]`, `[Food]`, `[Buddies]`, and `[Research / Agent]`; no additional category setup or new community labels are required. Maintainers use the [announcement Issue form](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=announcements.yml) with `[Club]`.

Templates do not create live posts or fake members. A published demonstration must remain clearly marked as fictional and must not be submitted for scoring. Research/Agent community Issues do not automatically earn points. Request contribution recognition through a separate experience Issue and the existing approval-label plus trusted-ledger review process.

## Fictional training-record demo

The README demo shows participation points for 6 fictional users, plus a separate recovery record. Its fixed demonstration week is **October 12–18, 2026**. All people and activities are fictional.

[Full training records and reflections](demo-training-records.md) · [Synthetic input](demo-training-records.json) · [Demo standings data](demo-leaderboard.json)

Demo files live in `examples/` and use a separate `DEMO` block in each README. The existing `CLUB` block continues to refresh the real community overview. After editing the fictional records, regenerate both language versions from the repository root:

```bash
python scripts/render_demo_board.py
python scripts/render_demo_board.py --check
```

## A mixed-sport week

Enter these lines in the **Planned sessions** field, after choosing your own activities and schedule:

```text
S1 | Tuesday | strength | My chosen gym session | My chosen at-home alternative
S2 | Thursday | basketball | Practice with a friend
S3 | Saturday | running | My chosen route
```

The fifth column belongs only to that session. A `/fallback S1 ...` can count once for S1 because this example declares an alternative for S1. The general Busy-week fallback note alone does not declare an alternative for S2 or S3. The same session cannot earn completion credit twice.

## Strength

```text
/done S1 2026-10-27 | Completed the session I planned.
Optional exercise notes:
- Exercise:
- Sets and repetitions:
- Load, if I want to share:
- Adjustment or observation:
```

## Basketball

```text
/done S2 2026-10-29 | Practice or game.
Focus:
Duration, optional:
What I noticed:
How it fitted the workday:
```

## Running

```text
/done S3 2026-10-31 | My planned run.
Duration, optional:
Distance or pace, optional:
Perceived effort:
Energy afterward:
```

Use the same light structure for swimming, cycling, walking, mobility, or other activities. No detailed metric is required.

## An honest partial session

```text
/partial S1 2026-10-27 | Did part of the session before my schedule changed.
What I did:
What I will adjust:
```

`partial` gives half a session of execution credit while remaining separate from full completion. The latest valid status wins if you later correct the record. An incomplete week can still receive reflection points.

## A food record without calorie counting

```text
/meal 2026-10-28 | Lunch
What I ate:
Portion context, if known:
What helped during a busy day:
What I might change:
Photo: optional
```

## A food record with an optional estimate

```text
/meal 2026-10-28 | Dinner
Food and portion:
Estimate source: label, weighed recipe, personal estimate, or model estimate
Estimated range: leave blank if unknown
Assumptions:
Unknowns: oil, sauce, portion size, or mixed ingredients
Correction later, if needed:
```

There is no automatic model service behind this template. Calories and nutrient numbers are optional estimates, not health grades, meal rankings, or point multipliers. No extra points come from eating less or logging more food photos.

## Weekly reflection and Agent time savings

```text
/review
Research context: regular, deadline, or travel
What worked:
What got in the way:
Next week's adjustment:

Optional Agent workflow:
Original task:
What the Agent handled:
Setup, checking, and rework:
Net time saved, if known:
Did I use it for exercise or rest?:
Limits:
```

Keep claims about time savings grounded in what you observed. A personal observation about energy or work does not establish that an activity causes better research performance for everyone. Reusable experiences can be submitted through the experience Issue form; contribution credit requires a maintainer's `points-approved` label plus a trusted repository approval entry matching the current body, author, and week, and stays capped at one point per member per week.
