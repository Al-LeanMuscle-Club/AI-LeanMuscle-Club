# Weekly reports

The summary workflow writes one public Markdown report and one public JSON snapshot per reporting week here. Only people who opt in to the leaderboard are named in generated reports. Aggregate participation counts can include people who opt out.

There are no real reports yet. Run the workflow after configuring the repository; do not publish fixture results as community activity.

The [browser helper](../tools/index.html) reads the latest 12 available report weeks from [the public index](index.json). Older weekly files remain available here.

Reports are recalculated snapshots, not immutable final results. The default run refreshes the current and preceding week; use the manual `week_start` input to refresh older points. Live synchronization also removes historical rows when current source metadata no longer permits their publication. Changing or deleting a record does not guarantee removal from already-published Git history or previously deployed website copies.
