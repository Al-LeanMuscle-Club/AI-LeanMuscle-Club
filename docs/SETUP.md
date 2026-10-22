# Maintainer setup

This starter contains English community documentation, the supplied poster, Issue forms, a tested score calculator, and GitHub Actions workflows. It does not contain real member records or a connected AI model. Committing it to GitHub and enabling the repository settings below is what activates the live workflow.

## 1. Put the files in the intended repository

Use the existing `Al-LeanMuscle-Club/AI-Lean-Muscle-Club` repository if that is still the club's home. Clone it, copy this starter's files into the checkout, inspect the diff, and commit through your usual workflow. Preserve existing content you want to keep.

If you choose a different repository, replace the `Al-LeanMuscle-Club/AI-Lean-Muscle-Club` links in README.md. The live script and workflow take their repository name from `GITHUB_REPOSITORY`, so scoring itself works after a rename or transfer. Use an Organization if you want the Maintain repository role.

The poster is already stored at `assets/club-poster.png`, with the supplied QR pattern preserved. Its invitation is marked valid before October 29, 2026; replace the asset and the date note when the invitation changes.

## 2. Enable Issues and create labels

Enable **Settings → General → Features → Issues**. Create these labels before members use the forms:

| Label | Suggested color | Purpose |
| --- | --- | --- |
| `weekly-plan` | `0759FF` | Weekly commitments and comment check-ins |
| `experience` | `0E8A16` | Reusable experiences and research/fitness workflows |
| `points-approved` | `FBCA04` | A maintainer's approval for an eligible contribution |

You can use the Issues label interface or, with GitHub CLI authenticated, run:

```bash
gh label create weekly-plan --repo Al-LeanMuscle-Club/AI-Lean-Muscle-Club --color 0759FF --description "Weekly plans and check-ins"
gh label create experience --repo Al-LeanMuscle-Club/AI-Lean-Muscle-Club --color 0E8A16 --description "Community experiences and workflows"
gh label create points-approved --repo Al-LeanMuscle-Club/AI-Lean-Muscle-Club --color FBCA04 --description "Maintainer-approved weekly contribution"
```

Skip labels that already exist. Only trusted maintainers should decide which experience Issues receive `points-approved`. Members do not need repository write access to open Issues and comment on public Issues.

## 3. Enable and test Actions

1. Commit the workflow files to the repository's **default branch**.
2. Enable GitHub Actions for this repository and allow `actions/checkout` and `actions/setup-python` if your organization restricts Actions.
3. The report job requests `contents: write` and `issues: read` using GitHub's built-in token. No personal token or paid model key needs to be stored in the repository.
4. Open **Actions → Update weekly participation reports → Run workflow** on the default branch. An empty `week_start` uses the current and previous Asia/Shanghai reporting weeks. For one older week, supply its Monday as `YYYY-MM-DD`. A specific-week run also displays that week in the README; the next empty-input or scheduled run restores the usual current-and-previous-week view.
5. Confirm the run finishes and commits only README.md and reports/. With no real members, it should show an empty board.

The scheduled run is **01:15 UTC / 09:15 Asia/Shanghai daily**. It is a daily refresh of weekly scores, not an LLM-written report. GitHub may delay scheduled runs, and inactive public repositories can have scheduled workflows disabled; a manual run is available.

If a branch rule requires PRs or rejects the bot push, the job will fail without force-pushing. Use a reviewed PR publishing approach for that repository, or keep local/manual report generation and commit through the normal review path. Do not weaken branch rules just to make the starter pass.

## 4. Run locally

Python **3.12+**, a GitHub token with read access to repository Issues, and network access to api.github.com are enough for a live report. There are no pip dependencies.

```bash
python -m unittest discover -s tests -v
python -m compileall -q club scripts tests
# Set GH_TOKEN securely in your shell or credential environment first.
python scripts/sync_github.py --repository Al-LeanMuscle-Club/AI-Lean-Muscle-Club
```

Do not commit credentials or raw downloaded Issue records. The script saves only public opt-in rows and anonymous aggregate counts. The current and previous weeks are refreshed by default; past reports remain historical snapshots unless refreshed manually.

For an **offline test only**, supply synthetic issue data and an explicit time:

```bash
python scripts/sync_github.py --fixture /path/to/synthetic-issues.json --week 2026-10-26 --as-of 2026-11-01T12:00:00Z --dry-run
```

Never publish test fixture results as real participation.

## 5. Run a small pilot

Invite willing members to try the forms for two weeks. Check whether a training record takes about 30 seconds, whether members return the next week, and whether they find useful encouragement. Explain that GitHub Issues and images are public, including records of people who do not join the scoreboard.

Keep the chat available for members who do not want public tracking. Add nutrition tooling, badges, or model integrations only after the core process is useful. Review the rules with participants; the score is encouragement, not a health measurement.

## References

- [GitHub Issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository)
- [GitHub's built-in workflow token](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
- [Workflow schedule syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule)
- [Repository roles](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization)
