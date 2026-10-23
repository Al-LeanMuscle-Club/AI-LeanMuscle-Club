# Maintainer setup

This starter contains English and Chinese community documentation, the supplied poster, Issue and Discussion forms, a tested score calculator, member helpers, and GitHub Actions workflows. It does not contain real member records or a connected AI model. Committing it to GitHub and enabling the repository settings below is what activates the live workflow.

## 1. Put the files in the intended repository

Use the existing `Al-LeanMuscle-Club/AI-LeanMuscle-Club` repository if that is still the club's home. Clone it, copy this starter's files into the checkout, inspect the diff, and commit through your usual workflow. Preserve existing content you want to keep.

If you choose a different repository, replace the `Al-LeanMuscle-Club/AI-LeanMuscle-Club` links in README.md. The live script and workflow take their repository name from `GITHUB_REPOSITORY`, so scoring itself works after a rename or transfer. Use an Organization if you want the Maintain repository role.

The poster is already stored at `assets/club-poster.png`, with the supplied QR pattern preserved. Its invitation is marked valid before October 29, 2026; replace the asset and the date note when the invitation changes.

## 2. Enable Issues and create labels

Enable **Settings → General → Features → Issues**. Create these labels before members use the forms:

| Label | Suggested color | Purpose |
| --- | --- | --- |
| `weekly-plan` | `0759FF` | Weekly commitments and comment check-ins |
| `experience` | `0E8A16` | Reusable experiences and research/fitness workflows |
| `points-approved` | `FBCA04` | A maintainer's approval for an eligible contribution |
| `activity-record` | `5319E7` | Free workout records, outside the points board |
| `meal-record` | `D4C5F9` | Free food records, outside the points board |

You can use the Issues label interface or, with GitHub CLI authenticated, run:

```bash
gh label create weekly-plan --repo Al-LeanMuscle-Club/AI-LeanMuscle-Club --color 0759FF --description "Weekly plans and check-ins"
gh label create experience --repo Al-LeanMuscle-Club/AI-LeanMuscle-Club --color 0E8A16 --description "Community experiences and workflows"
gh label create points-approved --repo Al-LeanMuscle-Club/AI-LeanMuscle-Club --color FBCA04 --description "Maintainer-approved weekly contribution"
gh label create activity-record --repo Al-LeanMuscle-Club/AI-LeanMuscle-Club --color 5319E7 --description "Free workout records"
gh label create meal-record --repo Al-LeanMuscle-Club/AI-LeanMuscle-Club --color D4C5F9 --description "Free food records"
```

Skip labels that already exist. Only trusted maintainers should decide which experience Issues receive `points-approved`. The label is necessary but no longer sufficient for points: an approval must also bind the exact content revision, author, and week in the reviewed ledger. Members do not need repository write access to open Issues and comment on public Issues.

## 3. Enable and test Actions

1. Commit the workflow files to the repository's **default branch**.
2. Enable GitHub Actions for this repository and allow `actions/checkout`, `actions/setup-python`, `actions/setup-node`, and `actions/cache` if your organization restricts Actions.
3. The report job requests `contents: write` and `issues: read` using GitHub's built-in token. No personal token or paid model key needs to be stored in the repository.
4. Open **Actions → Update weekly participation reports → Run workflow** on the default branch. An empty `week_start` uses the current and previous Asia/Shanghai reporting weeks. For one older week, supply its Monday as `YYYY-MM-DD`. A specific-week run also displays that week in the README; the next empty-input or scheduled run restores the usual current-and-previous-week view.
5. Confirm the run finishes and commits only README.md, reports/, and data/ranking-state.json. With no real members, it should show an empty board and no synthetic records.

The scheduled run is **01:15 UTC / 09:15 Asia/Shanghai daily**. Relevant human Issue/comment changes also trigger a refresh, including the first successful plan confirmation. Workflows read trusted default-branch code, serialize report jobs, skip bot/PR events, and commit only an explicit output allowlist. They calculate participation scores without an LLM. GitHub may delay scheduled runs; a manual run is available. CI runs the Python and JavaScript tests for pushes and pull requests.

If a branch rule requires PRs or rejects the bot push, the job will fail without force-pushing. Use a reviewed PR publishing approach for that repository, or keep local/manual report generation and commit through the normal review path. Do not weaken branch rules just to make the starter pass.

## 4. Run locally

Python **3.12+**, a GitHub token with read access to repository Issues, and network access to api.github.com are enough for a live report. There are no pip dependencies.

```bash
python -m unittest discover -s tests -v
python -m compileall -q club scripts tests
node --test tests/test_member_page.js
# Set GH_TOKEN securely in your shell or credential environment first.
python scripts/sync_github.py --repository Al-LeanMuscle-Club/AI-LeanMuscle-Club
```

Do not commit credentials or raw downloaded Issue records. Reports save only public opt-in rows and aggregate counts. The separate reviewed data/ranking-state.json file stores structural plan confirmations and content-bound contribution approvals. Commit that state together with real reports so a later sync cannot reset a confirmed plan's denominator. Never delete or recreate a live ledger to resolve a validation error; restore a trusted version. The current and previous weeks are refreshed by default; past scores remain historical snapshots unless refreshed manually.

For an **offline test only**, supply synthetic issue data and an explicit time:

```bash
python scripts/sync_github.py --fixture /path/to/synthetic-issues.json --week 2026-10-26 --as-of 2026-11-01T12:00:00Z --dry-run
```

Never publish test fixture results as real participation.

## 5. Run a small pilot

Invite willing members to try the forms for two weeks. Check whether a training record takes about 30 seconds, whether members return the next week, and whether they find useful encouragement. Explain that GitHub Issues and images are public, including records of people who do not join the scoreboard.

Keep the chat available for members who do not want public tracking. Add nutrition tooling, badges, or model integrations only after the core process is useful. Review the rules with participants; the score is encouragement, not a health measurement.

## 6. Configure the expanded community

Follow [community organization](COMMUNITY.md) to enable Discussions and create the six categories, including newcomer introductions. Category forms do not create or enable categories. Free activity and meal Issues work without a scoring plan. Discussions and free records do not enter the points board automatically. The experience-Issue route needs both the approval label and a matching maintainer-reviewed ledger record.

The plan form now collects independent goals and research-week context. Each training row can specify its own sport and fallback. Old three-column plans and `/done` comments still work. Detailed instructions are in the [member guide](MEMBER_GUIDE.md) and its [Chinese version](MEMBER_GUIDE.zh-CN.md).

## 7. Format feedback and member helpers

`check-submission.yml` runs trusted default-branch code for a `weekly-plan` Issue or an author's command comment. Its token has `contents: read` and `issues: write`. It parses the JSON event rather than interpolating member text into shell commands. Bot comments, PRs, peer comments, and ordinary conversation do not cause reply loops. It maintains one editable format-status comment per thread, so each check-in does not add another bot reply.

Format validation checks fields, authorship, session IDs, fallbacks, and dates. It does not verify physical activity, assess health, or approve an experience. The report workflow separately refreshes on relevant events and on schedule. If your organization blocks Issues writes, members can still validate locally. Free activity/meal records use their own forms and do not need command validation.

From the repository root, with `GH_TOKEN` securely configured for read access:

```bash
python scripts/member_tools.py find --handle YOUR_HANDLE --week 2026-10-26
python scripts/member_tools.py carry --issue 123 --week 2026-11-02 --output draft.md
python scripts/member_tools.py check --issue 123 --comment-file checkin.txt
```

These commands never submit changes. Carry-over writes a local draft and resets public leaderboard consent to `No`; review the schedule, goal, context, and any copied personal notes before submitting it through GitHub. Use `--fixture PATH --as-of TIMESTAMP` for offline synthetic checks.

## 8. Scale reporting without growing the homepage

The README contains aggregate overviews and links. Full weekly Markdown and JSON reports remain in `reports/`. The index includes the latest **12 available report weeks**; the helper can load older public reports on demand. Raw notes, meal contents, calorie estimates, photos, and body measurements are not copied into outputs. Structured weekly rows display meal-record days and training days separately; free activity/meal Issues remain at their original sources and are outside these scoring counts. Live synchronization checks historical eligibility, including withdrawal, Recovery, pause, invalid plans, and removed labels, and updates participation/recovery counts when withdrawing rows. Deleted Issues disappear after full reconciliation, which can be forced with `--refresh`. Git history and previous Pages snapshots may retain older copies; republish Pages after withdrawal. Refresh an older week explicitly to recalculate its training scores or contribution approvals.

Live synchronization defaults to `.club-cache/issues.json`, an ignored local cache containing source Issue/comment data. It stores no token, is written atomically with restricted local permissions, and must never be committed or copied into a website. Scheduled jobs restore it using `actions/cache`, scoped by repository ID. Organizations that do not want source records in Actions caches can remove the restore-cache step and use `--no-cache`.

An initial run scans all plan metadata. Later runs read changed Issues and comments, refreshing affected reporting and archived threads; a full reconciliation runs every seven days. Removed labels and revoked approvals are handled for selected scoring weeks. A failed read retains the previous cache and reports. Historical scores remain snapshots until explicitly refreshed; each weekly report retains its own generation time.

```bash
python scripts/sync_github.py --refresh
python scripts/sync_github.py --no-cache
```

## 9. Optional browser helper and Pages deployment

The Chinese-first `tools/` page provides free workout/meal links, check-in text, carry-over drafts, a weekly leaderboard with score components, and opt-in personal history. Sport filters select members whose plans include that sport; displayed points remain whole-week participation points. History summarizes available public participation weeks, training days, and meal-record days; old rows with unknown counts are not treated as zero. It has no sign-in, stored credential, automatic posting, or food-analysis model.

To run locally, start this command at the repository root and open `http://localhost:8000/tools/`:

```bash
python -m http.server 8000
```

GitHub's source-code view does not run HTML. For a hosted page, choose **Settings → Pages → Build and deployment → Source: GitHub Actions**, allow `actions/upload-pages-artifact` and `actions/deploy-pages`, then manually run **Actions → Publish optional member helper** on the default branch. The workflow publishes only `tools/`, generated `reports/`, and clearly marked `examples/`, excluding source caches and the ranking ledger. Use the deployed URL shown in the successful workflow; repository ownership or custom-domain settings can change its address.

Pages deployment is opt-in and manual. Re-run this publish workflow after reports change to refresh the hosted snapshot. Opening a README link to `tools/index.html` still opens GitHub's code viewer; add your actual deployed URL to the README once deployment succeeds. No Pages settings or repository features are changed by copying these files.

## 10. Confirmed plans and contribution approval

The first successful live report locks the structured sessions of an opted-in Active plan. Confirmations persist in `data/ranking-state.json`; the ledger retains a lookup fingerprint and session structure after withdrawal so rejoining cannot reset the denominator. Fingerprints are not an anonymity guarantee. No descriptions, food text, photos, or tokens are stored there. Changes before the first successful confirmation cannot be reconstructed.

For a useful experience Issue, first review its author, selected week, and current text, then add `points-approved`. With a securely configured read token, prepare the matching local approval:

```bash
python scripts/manage_ranking.py approve --issue 123
```

Review the ledger diff and submit it through a maintainer-reviewed PR. The point is awarded only after that approval record reaches the trusted reporting branch. Editing the Issue text, author, or selected week invalidates the match and needs another review. To withdraw approval, remove the label or prepare and commit a revocation:

```bash
python scripts/manage_ranking.py revoke --issue 123
```

Refresh the relevant week after approval changes. Protect ledger changes with normal maintainer review; a label or unreviewed PR alone must not authorize points. The CLI writes local files only.

The example directory contains six separate topic guides and optional synthetic fixture data. Fixture runs use temporary confirmation state and `--dry-run` prints JSON without publishing it. Keep demonstrations out of `reports/` and out of the live ledger.

## References

- [GitHub Issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository)
- [GitHub's built-in workflow token](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
- [Workflow schedule syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule)
- [Repository roles](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization)
