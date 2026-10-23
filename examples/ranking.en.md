[简体中文](ranking.md) | English

> **Fictional examples.** The people, activities, and numbers below illustrate formats only. They do not represent real members, check-ins, rankings, or prescribed training plans. These examples earn no points and do not enter live rankings. Do not post these examples as real community activity; borrow only the format that suits you.

# Ranking examples

**This file is an offline demonstration, not a community weekly report.** The fictional names do not correspond to members or link to real Issues. Its data is not written to `reports/` or the homepage participation counts.

The current weekly **participation score** has a maximum of 10: plan 1, execution 0–6, reflection 2, and approved contribution 0–1. Scores do not compare fitness, training difficulty, or body changes.

## Example 1: Displaying full and partial completion separately

Two fictional members each have 3 scoring sessions confirmed by the first successful sync. Both have written a reflection, and neither has an approved contribution.

| Fictional member | Fully completed | Partially completed | Execution credit | Full-completion rate | Execution points | Total points | Rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Demo Birch | 2 | 0 | 2 / 3 | 66.67% | 4 | 7 | 1 |
| Demo Aster | 1 | 1 | 1.5 / 3 | 33.33% | 3 | 6 | 2 |

A full completion or completion of a declared fallback each counts as 1 session of credit; partial counts as 0.5. Execution points are `6 × execution credit / confirmed sessions`, rounded to two decimal places. The full-completion rate does not count partial as full completion.

Demo Aster posts two valid `/meal` comments on the same day. This shows only 1 meal-record day, and the total score remains 6. If Demo Birch and another fictional member both receive 7 points, they share the same rank; the ranking does not compare whose training was heavier or longer.

## Example 2: Deleting sessions from an adjusted plan does not raise the score

Demo Cedar initially confirms `S1–S4`, fully completes 2 sessions, and writes a reflection: execution points are `6 × 2/4 = 3`, for a total of **6**.

After a change of schedule, the current plan is edited to retain the completed `S1` and `S2`, and add `S5`:

| Item | Before adjustment | After adjustment |
| --- | --- | --- |
| Confirmed scoring sessions | S1, S2, S3, S4 | S1, S2, S3, S4 |
| Current plan sessions | S1, S2, S3, S4 | S1, S2, S5 |
| Fully completed / confirmed sessions | 2 / 4 | 2 / 4 |
| Execution points | 3 | 3 |
| Total points, including plan and reflection | 6 | 6 |

S5 can still be recorded, but it does not add execution points for this week. The explanation for the adjustment and the current schedule can still be displayed. Recovery or `/pause` can withdraw a member from this week's scoring without creating a points debt.

Scores start afresh each week. The number of participation weeks in recent history is for looking back; participation does not have to be uninterrupted. Contribution points require both the `points-approved` label and a trusted approval record matching the body, author, and week. A label alone does not automatically award points to this demonstration or a real post.

See [SCORING](../docs/SCORING.md) for the full boundaries and correction rules.

## Running a separate synthetic-data demonstration

[ranking-fixture.json](ranking-fixture.json) in this directory contains 5 fictional plans: 3 demonstration members on the board, 1 recovery member, and 1 member who opted out. Its example links are placeholders and do not correspond to real posts.

Run the following command from the repository directory to print JSON only, without writing real reports, caches, or approval records:

```bash
python scripts/sync_github.py --fixture examples/ranking-fixture.json --week 2026-10-26 --as-of 2026-11-02T12:00:00Z --dry-run
```

This demonstration uses different fictional data from the two worked examples above: demonstration member B receives 9 points, A receives 6.75, and C receives 6. A's 3 meal comments cover 2 dates, so 2 meal-record days are displayed. Recovery and opted-out members are included only in anonymous counts and do not appear in the demonstration ranking. The JSON itself contains no real contribution approvals.
