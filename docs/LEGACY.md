# Historical features and records

The current club workflow is [daily check-ins](MEMBER_GUIDE.md) with a [100-point weekly formula](SCORING.md), plus experience sharing and conversation. This page explains what was retained for history.

- **Old weekly reports** remain in [`reports/`](../reports/README.md). Their original scores stay unchanged; they are not converted into the new 100-point board.
- **The v2 scoring explanation** is preserved in [SCORING.v2.md](SCORING.v2.md). Its plan, execution, reflection, and contribution points apply only to those historical reports.
- **Old Issue templates** are stored in [`legacy-issue-templates/`](legacy-issue-templates/) for reference. They no longer appear in GitHub's new-Issue chooser.
- **Old automatic format replies and label setup** are archived in `docs/legacy-workflows/`. They are not part of the daily report schedule.
- **Legacy calculation and member scripts** remain available for compatibility and tests. The current scheduled job uses `scripts/sync_daily.py`; do not run old report publishing or contribution-approval tools as part of the new workflow.
- **The trusted ranking ledger** at `data/ranking-state.json` is historical state. Do not delete, reset, migrate, or write it when calculating daily-check-in scores.
- **Old examples** demonstrate historical formats and scoring. They are fictional, not live activity, and do not enter the new board.

Existing Issues and comments remain accessible. To start using the new board, create one journal with the [daily check-in form](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=daily-checkin.yml) and explicitly choose whether to appear publicly. Do not convert old session records into new work/exercise days without the member's own record.

[Upgrade checklist](UPGRADE.md) · [Current member guide](MEMBER_GUIDE.md)
