# Upgrade notes

This update expands the original weekly-plan pilot while keeping its 10-point cap and voluntary public board.

## What changes

- Independent weekly goals and research-week context; per-session sports for mixed plans.
- Optional per-session fallback and explicit `/partial` / `/skip` records; the latest valid status determines completion.
- Optional `/meal` records with estimate source and uncertainty; no calorie or food-health scoring.
- A short README overview, full weekly reports, and a recent-12-week public index.
- Read-only member CLI tools, a mobile-friendly browser helper, and editable format feedback.
- Six community Issue forms, detailed English/Chinese instructions, and reusable examples.
- A Simplified Chinese default README, an English companion, and Chinese live-overview updates; older Chinese README links remain usable.
- Optional private sync caching with incremental reads and weekly reconciliation.
- Stable GitHub user-ID confirmations that survive username changes, with migration of matching legacy username entries.
- Explicit scoring-rule versions in reports, indexes, and member history, without relabeling unversioned snapshots.
- Search links for a member's free activity and meal records, separate from scored weekly plans.
- Optional automatic Pages publishing after successful reports and relevant default-branch changes.

## Compatibility and rollout

Old `S1 | Monday | description` plans, `/done`, `/review`, and `/pause` remain valid. Legacy activities use `other` until the author adds a sport. Missing goal/context fields default to `habit` / `regular`.

The latest valid status replaces a session's previous status, so a later `/partial` or `/skip` can correct an earlier `/done`. Edit/delete an erroneous record to correct it. Scoring rules v2 give a partial session half credit, retain the confirmed scoring denominator, and require a matching trusted approval for contribution points. Fallbacks use the current declared fifth column for IDs still in the plan; descriptions and actual exercise remain honor based.

Keep `data/ranking-state.json` when upgrading. A live sync migrates a matching current-username confirmation to a stable GitHub user-ID fingerprint without changing its sessions. Existing stable confirmations survive username changes. The migration also preserves existing confirmations while members are opted out, in Recovery, or paused. If an account was renamed before its old username entry could be linked to a stable ID, verify and migrate that specific confirmation manually before refreshing its week; automatic matching cannot recover the old identity from a one-way fingerprint. Offline records without a valid user ID keep the legacy username fallback.

New snapshots record `scoring_version: 2` while retaining JSON `schema_version: 2`. Missing rule versions stay unknown, even if an old snapshot already used some v2 rules. Historical withdrawal/count refreshes preserve both the saved score and its original rule-version metadata. Decide explicitly which old weeks to recalculate with the current rules using `--week YYYY-MM-DD`; do not stamp a version onto unchanged historical scores.

Copy the updated files into a checkout of your existing repository and review the diff. Preserve unrelated changes, existing reports, and member data. Commit through the repository's normal process. Make sure `.github/` is included when copying; it can be hidden in file pickers.

Run Python and browser-helper checks, enable the required settings in [SETUP.md](SETUP.md), then manually regenerate the current/previous-week report. Existing report snapshots are not rewritten merely by replacing code. `--refresh` rebuilds source caches; use `--week YYYY-MM-DD` to regenerate a specific historical report.

After copying this package into an existing repository, avoid overwriting a populated `reports/index.json` with the starter's empty index; let the report workflow regenerate it from your existing reports. The included empty index has no synthetic participants.

Pages hosting requires initial manual setup. Community Issue forms are available after merging `.github/ISSUE_TEMPLATE/` into the default branch with Issues enabled; no separate community categories or new labels are required. Existing manual Pages publishing remains available. To enable automatic publishing after successful report runs and relevant changes on the default branch, set the repository Actions variable `PUBLISH_MEMBER_HELPER` to `true` after reviewing the site's visibility; see [SETUP](SETUP.md#9-optional-browser-helper-and-pages-deployment). Forks and repositories without this opt-in do not publish automatically. The included AI guidance is a workflow specification, not a connected model or automatic nutrition analysis service.
