# Maintainer setup

The active workflow has three Issue forms, a deterministic daily-check-in score, a daily report job, and an optional static helper. No model service or paid API key is required.

## 1. Enable the member flow

Merge the new code and `.github/ISSUE_TEMPLATE/` files into the repository's default branch, and enable **Settings → General → Features → Issues**. Members then choose **Daily check-in**, **Experience sharing**, or **Conversation**.

The journal and current reporter do not depend on special labels. Members normally create their own long-running journal and explicitly choose **Yes** for public standings. The default is **No**. The narrow exception is an [explicitly authorized migration of existing public Activity posts](SCORING.md#authorized-legacy-activity-import): identify the maintainer who enabled standings in the migration note, preserve the original record, and do not present this as the author's own confirmation. Specific [work dates](SCORING.md#explicit-work-date-backfill) or [exercise dates](SCORING.md#explicit-exercise-date-backfill) may also be backfilled with explicit information and authorization, identifying the information source and executing maintainer. This does not authorize invented activity, removal of dates without a requested correction, or unrelated opt-ins; a later No or closure still withdraws the member.

`README.md` is the default English homepage and `README.zh-CN.md` is the full Chinese homepage. `README.en.md` is a navigation-only compatibility page for old links. Preserve the language and community markers, one paired `CLUB` block, and a single `[member-helper]:` definition in each full homepage. The reporter automatically updates the live board block in both languages; curated stories stay outside it.

## 2. Enable daily reports

Enable GitHub Actions, allowing the actions referenced by the repository workflows. **Update weekly participation reports** runs at **01:15 UTC daily / 09:15 Beijing time** and can be started manually. Its name is retained so the existing optional Pages workflow can follow successful report runs.

The job uses GitHub's built-in token with `issues: read` and `contents: write`, reads members' journals and comments, and runs `scripts/sync_daily.py`. It refreshes the current and preceding report week, chosen using the Asia/Shanghai calendar. Individual comment dates are validated in each journal's own time zone. Only aggregate v3 rows with public standings enabled are written under `reports/daily/`; raw Issue bodies are not committed. The old ranking ledger is never updated.

After merging, run the workflow manually once and check its output. An empty report is expected until an open journal with public standings enabled has a valid check-in or validated imported exercise date. Do not fill an empty board with fictional examples. GitHub schedules can be delayed; manual runs are available.

For a correction older than the previous week, set the workflow's optional `week_start` input to that week's Monday in `YYYY-MM-DD` format. The script's `--week` option provides the same selection locally.

If branch protection rejects the report push, use a reviewed publishing PR or the repository's permitted update process. Do not weaken branch rules or force-push to make automation pass.

## 3. Run locally

Use Python **3.12+** and the repository's supported Node version for the browser tests. The calculation itself has no pip dependencies.

```bash
python -m unittest discover -s tests -v
python scripts/render_demo_board.py --check
python -m compileall -q club scripts tests
node --test tests/test_member_page.js
# Configure GH_TOKEN securely in your environment first.
python scripts/sync_daily.py --repository Al-LeanMuscle-Club/AI-LeanMuscle-Club
# To refresh one older week:
python scripts/sync_daily.py --repository Al-LeanMuscle-Club/AI-LeanMuscle-Club --week 2026-10-26
```

Do not place credentials in source files, Issue text, or the browser helper. Keep raw API data and local caches out of public artifacts. Source API failures must leave existing reports intact; do not publish a partial read as a complete board.

## 4. Explain visibility and history

New v3 files are separate from the previous reports in `reports/`. Never reinterpret or recalculate a historical 10-point row with the new formula. Old examples and the legacy ledger remain historical references.

At each sync, reconcile saved v3 rows with the current journal's open state and explicit public setting. Closing a journal or choosing No withdraws its author from generated v3 files; prior Git commits and public source Issues remain accessible. [Scoring and correction rules](SCORING.md) · [Migration checklist](UPGRADE.md)

<a id="9-optional-browser-helper-and-pages-deployment"></a>

## 5. Optional browser helper and Pages deployment

In **Settings → Pages**, choose **GitHub Actions** as the publishing source. Manually run **Publish optional member helper**, confirm build and deploy succeeded, and use the real URL returned by the deployment. The site root leads to `/tools/`.

The helper prepares check-in text, finds journals, and shows `reports/daily/index.json`. It never submits member records. Before the first successful deployment, README helper links lead to setup instructions. Once a real Pages URL is available, the deployment's `update-entry` job validates both full homepages before updating their helper links: `README.md` and `README.zh-CN.md`.

For automatic publication after successful report jobs and relevant default-branch changes, set the Actions repository variable `PUBLISH_MEMBER_HELPER=true`. Keep it unset if publication should remain manual. Repositories without this setting do not publish automatically.

Only static tools and public report artifacts belong on the site; never publish the legacy ranking ledger, raw source data, or credentials. If deployment succeeds but branch protection blocks the README link update, copy the deployment's returned helper URL into both full homepages' `[member-helper]:` definitions through the normal reviewed change process.

[Chinese Pages walkthrough](PAGES_QUICKSTART.zh-CN.md) · [Historical features and automation](LEGACY.md)
