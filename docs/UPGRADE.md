# Upgrade notes

This update expands the original weekly-plan pilot while keeping its 10-point cap and voluntary public board.

## What changes

- Independent weekly goals and research-week context; per-session sports for mixed plans.
- Optional per-session fallback and explicit `/partial` / `/skip` records; the latest valid status determines completion.
- Optional `/meal` records with estimate source and uncertainty; no calorie or food-health scoring.
- A short README overview, full weekly reports, and a recent-12-week public index.
- Read-only member CLI tools, a mobile-friendly browser helper, and editable format feedback.
- Discussion category forms, detailed English/Chinese instructions, and reusable examples.
- Optional private sync caching with incremental reads and weekly reconciliation.

## Compatibility and rollout

Old `S1 | Monday | description` plans, `/done`, `/review`, and `/pause` remain valid. Legacy activities use `other` until the author adds a sport. Missing goal/context fields default to `habit` / `regular`.

The latest valid status replaces a session's previous status, so a later `/partial` or `/skip` can correct an earlier `/done`. Edit/delete an erroneous record to correct it. Fallbacks use the current declared fifth column; this remains an honor-based system without a frozen historical plan.

Copy the updated files into a checkout of your existing repository and review the diff. Preserve unrelated changes, existing reports, and member data. Commit through the repository's normal process. Make sure `.github/` is included when copying; it can be hidden in file pickers.

Run Python and browser-helper checks, enable the required settings in [SETUP.md](SETUP.md), then manually regenerate the current/previous-week report. Existing report snapshots are not rewritten merely by replacing code. `--refresh` rebuilds source caches; use `--week YYYY-MM-DD` to regenerate a specific historical report.

After copying this package into an existing repository, avoid overwriting a populated `reports/index.json` with the starter's empty index; let the report workflow regenerate it from your existing reports. The included empty index has no synthetic participants.

Pages hosting and Discussion categories require manual setup. The included AI guidance is a workflow specification, not a connected model or automatic nutrition analysis service.
