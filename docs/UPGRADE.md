# Moving to daily check-ins · v3

The new member flow keeps two capabilities: daily check-ins with a weekly board, and experience sharing with conversation. It replaces the weekly-plan scoring model for future participation.

## Before merging

Run the checks listed in [AGENTS.md](../AGENTS.md), review the [new formula](SCORING.md), and keep the existing `reports/` history and `data/ranking-state.json` unchanged. The new reporter writes to `reports/daily/`; old 10-point rows must never appear as new 100-point rows.

## Enable the new flow

1. Merge the daily journal form, scoring code, and report workflow into the default branch.
2. Members create their own `[Check-in]` Issue once, choose the correct time zone, and set **Public leaderboard** to **Yes** only if they want to appear publicly.
3. Members add `/checkin YYYY-MM-DD W=1 E=0` comments with their actual daily flags. The calculation does not infer work days from old training plans or convert experience posts into check-ins.
4. Run **Update weekly participation reports** manually once and review the generated v3 reports. The schedule then runs every day at 01:15 UTC.
5. If a helper site was already deployed, publish it again so it uses the simplified interface and `reports/daily/index.json`. [Pages setup](SETUP.md#9-optional-browser-helper-and-pages-deployment)

New-Issue choices are now daily check-in, experience sharing, and conversation. The specialized old templates are archived. Experience posts no longer ask for a scoring week or contribution approval.

## Keep history separate

Old weekly reports, old code, and the trusted ledger remain for historical explanation and compatibility. No old report is rescored automatically. The active page reads only v3 daily-check-in reports. See [historical features](LEGACY.md).

Closing the current journal or changing its public setting to No withdraws rows from generated v3 files at the next sync. It does not erase source Issues, Git history, or old v1/v2 reports.
