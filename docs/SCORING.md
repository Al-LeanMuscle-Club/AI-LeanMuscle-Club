# Daily check-in scoring · v3

The weekly board counts recorded work days and exercise days from each member's own daily check-in comments, with the narrow legacy Activity import described below. It measures participation, not hours worked, exercise intensity, physical condition, or productivity. Experience posts and replies do not add points.

## The 100-point formula

For a Monday–Sunday week, let $W$ be distinct dates with work recorded and $E$ be distinct dates with exercise recorded:

$$
S = 100 \sqrt{\min(W/5, 1) \cdot \min(E/4, 1)}
$$

| Work days $W$ | Exercise days $E$ | Score |
| ---: | ---: | ---: |
| 5 | 4 | 100.00 |
| 5 | 1 | 50.00 |
| 4 | 3 | 77.46 |
| 0 | 4 | 0.00 |
| 5 | 0 | 0.00 |
| 7 | 7 | 100.00 |

The two counts remain visible even when one exceeds its scoring cap. Scores are rounded to two decimal places. Equal published scores share a rank; the next rank skips the tied positions, such as 1, 1, 3. A zero in either count produces zero points. There are no plan, reflection, meal, or contribution bonuses.

## One journal per member

Create a long-running Issue with the [daily check-in form](../.github/ISSUE_TEMPLATE/daily-checkin.yml). Keep the `[Check-in]` title prefix and these form fields:

- **Time zone**: a valid IANA time zone, such as `Asia/Shanghai`, `America/Los_Angeles`, or `UTC`.
- **Public leaderboard**: `Yes` or `No`. The default is `No`.

Only an open journal with `Public leaderboard` set to `Yes` can appear on the board. The author normally makes this choice; an explicit maintainer instruction may authorize it for the existing public Activity posts being migrated below. At least one valid check-in or validated imported exercise record in the selected week is needed. An empty journal is not evidence of work or exercise.

If an author creates several journals, the one with the latest creation time is used; Issue number breaks a creation-time tie. Closing that journal, selecting `No`, or leaving its settings invalid does not reactivate an older journal. Edit or reopen the current journal, or intentionally create a replacement. Renaming a journal outside the accepted form can stop it being recognized; use `No` or close the Issue to withdraw clearly.

## Authorized legacy Activity import

An explicit maintainer instruction may migrate specified existing public Activity posts into their original authors' `[Check-in]` journals and enable public standings. Preserve the original post and its time zone, and include a migration note identifying the maintainer who enabled public standings. This does not represent confirmation by the original author. It is a narrow import of an exercise record already supplied by that author, not permission to generate new member activity or work records.

An imported journal must contain `<!-- club-import:activity-v1 -->` as a standalone line under `### Migration notes` and exactly one `### Imported exercise date` field. Its date must exactly match the preserved original `### Activity date`, be valid, and be no later than the original Issue's creation date in its original time zone. Bots, fictional examples, malformed imports, and future records are excluded.

The valid imported date contributes **one exercise day** to its week. No work day is inferred: $W$ counts only registered work days, so an absent work record contributes zero to the count without asserting that the author did not work. The formula stays unchanged; a journal with an imported exercise day and no work record is visible with a score of **0.00**.

A valid check-in comment by the author for the imported date overrides both daily flags, including a `W=0 E=0` correction. Duplicate dates never add extra days. The usual latest-journal selection, `No`, and closed-journal withdrawal rules still apply.

## A daily comment

Post this as the first non-empty line of a comment on your own journal:

```text
/checkin 2026-10-26 W=1 E=0
```

`W=1` means you worked on that date; `E=1` means you exercised. Use `0` for no. `W=0 E=0` is a valid rest-day record. The member reports whether the day qualifies; there is no shared hourly or intensity threshold. Additional notes may follow on later lines. Use one check-in per comment, and do not surround the command with a code fence when posting.

Only the journal author's comments count. Another person's encouragement is welcome but cannot change the score. Bots, pull requests, explicitly fictional examples, malformed commands, invalid dates, and future-dated records are excluded. A date cannot be later than either the reporting cutoff or the comment's effective creation/edit time in the journal's time zone.

## Dates and corrections

Weeks run Monday–Sunday using the journal's local calendar dates. The same date can contribute at most one work day and one exercise day. If several valid comments refer to that date, the latest effective creation/edit time wins and replaces **both** flags; the values are not combined across comments. A higher comment ID breaks an effective-time tie. Editing a valid comment updates its effective time. Write a new valid `W=0 E=0` correction to clear a day's flags. Deleting a comment removes it from the next calculation; an earlier valid record for the same date can then become the latest remaining one.

All comments are read again at each calculation. Members can backfill or correct the current and preceding week; an older week needs a maintainer to request that week explicitly. Changing a journal's time zone affects how its date and timestamp checks are interpreted, so choose the time zone that applies to your records.

## Daily publication and privacy

The scheduled calculation runs at 01:15 UTC each day, or 09:15 Beijing time, and refreshes the current and preceding week. GitHub can delay scheduled runs. Maintainers can also run it manually. The job reads GitHub records and computes the formula with fixed code; no LLM decides whether a member worked, exercised, or deserves points.

Published v3 reports live in [`reports/daily/`](../reports/daily/README.md). They contain usernames with public standings enabled, source journal links, weekly counts, scores, and report timestamps; they do not copy comment bodies or daily notes. Selecting `No` or closing the current journal removes the member from later generated v3 reports, including saved v3 history when the next sync reconciles visibility. Previously committed Git history, the source Issue, and its comments remain public.

Old 10-point reports retain their original scores and are never recalculated with this formula. See [historical rules](SCORING.v2.md), [migration notes](UPGRADE.md), and [maintainer setup](SETUP.md).
