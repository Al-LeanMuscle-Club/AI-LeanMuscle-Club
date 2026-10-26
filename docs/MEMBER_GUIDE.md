# Member guide: check-ins and scoring

**English** | [简体中文](MEMBER_GUIDE.zh-CN.md)

Use the club to record work and exercise, and exchange experiences.

## 1. Create one long-running journal

Open the [daily check-in form](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=daily-checkin.yml). Choose your IANA time zone; the default is `Asia/Shanghai`, and alternatives include `America/Los_Angeles` and `UTC`.

Keep one Issue across weeks and retain its `[Check-in]` title prefix. Set **Public leaderboard** to **Yes** to appear on the public board. The default **No** still allows you to keep your own records.

## 2. Comment on your journal each day

```text
/checkin 2026-10-26 W=1 E=0
```

Replace the date with the actual local date. `W` means whether you worked and `E` means whether you exercised: `1` for yes, `0` for no. Use `W=1 E=1` for both or `W=0 E=0` for a rest day. Hours, exercise types, photos, and body measurements are not required.

Put one check-in on the first non-empty line of each comment, without the surrounding code-fence backticks. Optional notes may follow on later lines. Dates use your journal's time zone; future dates are invalid.

For repeated records of the same date, the latest valid comment replaces both flags. Editing a comment also corrects it. A new `W=0 E=0` record clears both flags for that day. Deleting the latest comment can make an older valid comment the latest remaining record.

Only the journal author's comments count. Other members' replies are conversations. If you create multiple journals, the latest-created one is used; closing it or selecting No does not reactivate an older journal.

## 3. Follow the weekly board

Each Monday–Sunday week counts distinct work and exercise dates. Let $W$ be the week's work days and $E$ its exercise days:

$$
S = 100 \sqrt{\min(W/5, 1) \cdot \min(E/4, 1)}
$$

Work and exercise contributions cap at five and four days respectively. Either count at zero yields zero. Scores are rounded to two decimal places, and equal scores share a rank.

| Work days W | Exercise days E | Weekly score |
| ---: | ---: | ---: |
| 5 | 4 | 100.00 |
| 5 | 1 | 50.00 |
| 0 | 4 | 0.00 |

These are calculation examples, not member records. The score measures self-reported participation, not work hours, exercise volume, or physical condition. [Full rules and corrections](SCORING.md)

The board updates daily at **01:15 UTC / 09:15 Beijing time**, though GitHub may delay a scheduled run. The current and preceding weeks refresh automatically, so you can backfill genuine records for those weeks. Ask a maintainer to refresh an older week after correcting it. [Reports and history](../reports/daily/README.md)

An existing public Activity post can also appear on the board after a maintainer-authorized migration. Its original exercise date counts once; no work day is inferred. A zero work count means no work days are registered, so the score may initially be zero. A maintainer can also backfill specific work dates explicitly supplied and authorized by a member or maintainer, noting the source and who made the change. Add your own dated check-ins to record or correct work and exercise, and the next refresh updates the score; a same-day check-in replaces both imported flags. The migration note identifies who enabled standings; you can still select No or close the journal to withdraw.

## Share experiences and talk

Use [experience sharing](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) for context, what you tried, results, and limits. Use [a short conversation](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=community-chat.yml) for a question or everyday note, or reply to an existing thread. Posts and replies add no leaderboard points.

## Browser helper

The [check-in helper](../README.en.md#member-helper) finds your journal, prepares comment text, and displays published standings. It never posts for you or requests a GitHub token. Its date defaults to your device's local date; check that it matches your journal's time zone.

For local preview, run `python -m http.server 8000` from the repository root and open `http://localhost:8000/tools/`. A hosted version needs [Pages setup](SETUP.md#9-optional-browser-helper-and-pages-deployment) first.

## Public sharing

All source Issues, comments, and photos are public. **No** only excludes you from named standings. Setting the current journal to No or closing it removes your rows from generated v3 reports at the next sync, including saved v3 history; prior Git commits remain public.

Only share information you want public. Exact weight, health history, photos, precise location, and confidential research information are never required.

See [historical features](LEGACY.md) for migration from weekly plans, meal records, and the old 10-point board.
