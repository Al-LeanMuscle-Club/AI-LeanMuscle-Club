"""Ranking regressions: trusted approvals, locked baselines, and record counts."""

from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
from datetime import timedelta
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from club.ranking_state import (approve_contribution, load_state, new_state,
                                plan_fingerprint, save_state)
from club.scoring import build_week
from scripts.manage_ranking import ROOT as REPOSITORY_ROOT, main as manage_ranking
from scripts.sync_github import main as sync_main, write_reports
from tests.test_scoring import AS_OF, WEEK, approved_state, comment, contribution, plan


def result(issues, state=None):
    return build_week(issues, WEEK, AS_OF, ranking_state=state)["leaderboard"][0]


class ApprovalTests(unittest.TestCase):
    def test_labels_alone_do_not_grant_contribution_credit(self):
        self.assertEqual(result([plan(), contribution()])["contribution_points"], 0)
        state = approved_state(contribution())
        self.assertEqual(result([plan(), contribution()], state)["contribution_points"], 1)

    def test_body_week_author_and_labels_must_still_match_reviewed_version(self):
        original = contribution()
        state = approved_state(original)
        changed_body = deepcopy(original)
        changed_body["body"] += "\nThe content was edited after approval."
        changed_week = deepcopy(original)
        changed_week["body"] = changed_week["body"].replace(WEEK, "2026-11-02")
        changed_author = {**original, "user": {"login": "bob"}}
        removed_label = {**original, "labels": [{"name": "experience"}]}
        for issue in (changed_body, changed_week, changed_author, removed_label):
            with self.subTest(issue=issue):
                self.assertEqual(result([plan(), issue], state)["contribution_points"], 0)
        # A second approval is an explicit maintainer action and restores credit.
        approve_contribution(changed_body, state, AS_OF)
        self.assertEqual(result([plan(), changed_body], state)["contribution_points"], 1)

    def test_moving_an_approved_issue_does_not_grant_next_week_credit(self):
        original = contribution()
        state = approved_state(original)
        next_week = "2026-11-02"
        next_plan = plan(number=2)
        next_plan["body"] = next_plan["body"].replace(WEEK, next_week)
        moved = deepcopy(original)
        moved["body"] = moved["body"].replace(WEEK, next_week)
        board = build_week([next_plan, moved], next_week, AS_OF + timedelta(days=7), ranking_state=state)
        self.assertEqual(board["leaderboard"][0]["contribution_points"], 0)

    def test_future_approval_is_not_applied_to_earlier_report(self):
        state = approved_state(contribution(), now=AS_OF + timedelta(seconds=1))
        self.assertEqual(result([plan(), contribution()], state)["contribution_points"], 0)

    def test_local_approval_cli_and_revoke_need_no_remote_write(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "issue.json"
            issue = contribution()
            issue["created_at"] = "2020-01-01T00:00:00Z"
            fixture.write_text(json.dumps(issue))
            ledger = root / "ranking-state.json"
            with patch("scripts.manage_ranking.GitHubReader") as reader, redirect_stdout(StringIO()):
                self.assertEqual(manage_ranking(["approve", "--issue", "100", "--fixture", str(fixture),
                                                 "--state", str(ledger)]), 0)
                reader.assert_not_called()
            self.assertIn("100", load_state(ledger)["contribution_approvals"])
            with redirect_stdout(StringIO()):
                self.assertEqual(manage_ranking(["revoke", "--issue", "100", "--state", str(ledger)]), 0)
            self.assertEqual(load_state(ledger)["contribution_approvals"], {})

    def test_fixture_approval_requires_explicit_isolated_ledger_before_any_read(self):
        live = REPOSITORY_ROOT / "data" / "ranking-state.json"
        equivalent = REPOSITORY_ROOT / "data" / ".." / "data" / "ranking-state.json"
        for selected in (None, live, equivalent):
            with self.subTest(selected=selected):
                args = ["approve", "--issue", "100", "--fixture", "synthetic.json"]
                if selected is not None:
                    args += ["--state", str(selected)]
                with patch("scripts.manage_ranking.load_state") as load, \
                        patch("scripts.manage_ranking.save_state") as save, redirect_stderr(StringIO()):
                    self.assertEqual(manage_ranking(args), 1)
                load.assert_not_called()
                save.assert_not_called()

    def test_fixture_approval_cannot_reach_live_ledger_through_symlink(self):
        with TemporaryDirectory() as directory:
            link = Path(directory) / "test-ledger.json"
            link.symlink_to(REPOSITORY_ROOT / "data" / "ranking-state.json")
            with patch("scripts.manage_ranking.load_state") as load, redirect_stderr(StringIO()):
                self.assertEqual(manage_ranking(["approve", "--issue", "100", "--fixture", "synthetic.json",
                                                 "--state", str(link)]), 1)
            load.assert_not_called()


class ConfirmedPlanTests(unittest.TestCase):
    def test_renaming_the_same_github_account_cannot_shrink_a_saved_baseline(self):
        state = new_state()
        issue = plan(sessions=2)
        issue["user"]["id"] = 123456
        issue["comments_data"] = [comment("/done S1 2026-10-26")]
        self.assertEqual(result([issue], state)["execution_points"], 3)
        key = plan_fingerprint(WEEK, "alice", 123456)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "ranking-state.json"
            save_state(path, state)
            self.assertNotIn("123456", path.read_text())
            state = load_state(path)
        issue["user"]["login"] = "alice-renamed"
        issue["body"] = issue["body"].replace("\nS2 | Monday | Session 2", "")
        issue["comments_data"] = [comment("/done S1 2026-10-26", "alice-renamed")]
        row = result([issue], state)
        self.assertEqual(row["handle"], "alice-renamed")
        self.assertEqual((row["confirmed_planned"], row["current_planned"]), (2, 1))
        self.assertEqual(row["execution_points"], 3)
        self.assertEqual(set(state["confirmed_plans"]), {key})

    def test_same_handle_legacy_confirmation_migrates_before_a_later_rename(self):
        state = new_state()
        issue = plan(sessions=3)
        result([issue], state)
        legacy_key = plan_fingerprint(WEEK, "alice")
        original = deepcopy(state["confirmed_plans"][legacy_key])
        issue["user"] = {"login": "ALICE", "id": 123456}
        issue["body"] = issue["body"].replace("\nS2 | Monday | Session 2", "").replace("\nS3 | Monday | Session 3", "")
        issue["comments_data"] = [comment("/done S1 2026-10-26", "ALICE")]
        self.assertEqual(result([issue], state)["execution_points"], 2)
        stable_key = plan_fingerprint(WEEK, "ALICE", 123456)
        self.assertEqual(state["confirmed_plans"], {stable_key: original})
        issue["user"]["login"] = "alice-renamed"
        issue["comments_data"] = [comment("/done S1 2026-10-26", "alice-renamed")]
        self.assertEqual(result([issue], state)["execution_points"], 2)
        self.assertEqual(state["confirmed_plans"], {stable_key: original})

    def test_withdrawal_recovery_or_pause_then_rename_preserves_stable_baseline(self):
        cases = ((reason, legacy) for reason in ("withdrawal", "recovery", "pause")
                 for legacy in (False, True))
        for reason, legacy in cases:
            with self.subTest(reason=reason, legacy=legacy):
                state = new_state()
                issue = plan(sessions=3)
                if not legacy:
                    issue["user"]["id"] = 123456
                result([issue], state)
                original = deepcopy(next(iter(state["confirmed_plans"].values())))
                expected = new_state()
                expected["confirmed_plans"][plan_fingerprint(WEEK, "alice", 123456)] = original
                # Observe the stable ID before a later rename, even if the
                # account is currently excluded from the public standings.
                issue["user"]["id"] = 123456
                if reason == "withdrawal":
                    issue["body"] = issue["body"].replace("### Public leaderboard\n\nYes", "### Public leaderboard\n\nNo")
                elif reason == "recovery":
                    issue["body"] = issue["body"].replace("### Participation mode\n\nActive", "### Participation mode\n\nRecovery")
                else:
                    issue["comments_data"] = [comment("/pause")]
                self.assertEqual(build_week([issue], WEEK, AS_OF, ranking_state=state)["leaderboard"], [])
                self.assertEqual(state, expected)
                issue = plan(handle="alice-renamed", sessions=1)
                issue["user"]["id"] = 123456
                issue["comments_data"] = [comment("/done S1 2026-10-26", "alice-renamed")]
                row = result([issue], state)
                self.assertEqual((row["confirmed_planned"], row["execution_points"]), (3, 2))
                self.assertEqual(state, expected)

    def test_missing_or_invalid_user_ids_remain_compatible_with_legacy_records(self):
        for user_id in (None, 0, -1, True, "123456", 1.5):
            with self.subTest(user_id=user_id):
                state = new_state()
                issue = plan(sessions=2)
                result([issue], state)
                original = deepcopy(state)
                issue["user"]["id"] = user_id
                issue["body"] = issue["body"].replace("\nS2 | Monday | Session 2", "")
                issue["comments_data"] = [comment("/done S1 2026-10-26")]
                self.assertEqual(result([issue], state)["execution_points"], 3)
                self.assertEqual(state, original)

    def test_an_already_renamed_legacy_account_is_not_guessed_from_other_hashes(self):
        state = new_state()
        original_issue = plan(sessions=2)
        result([original_issue], state)
        original_key = plan_fingerprint(WEEK, "alice")
        original = deepcopy(state["confirmed_plans"][original_key])
        issue = plan(handle="renamed-before-migration", sessions=1)
        issue["user"]["id"] = 123456
        row = result([issue], state)
        self.assertEqual(row["confirmed_planned"], 1)
        self.assertEqual(state["confirmed_plans"][original_key], original)
        self.assertEqual(len(state["confirmed_plans"]), 2)

    def test_deleting_unfinished_sessions_does_not_increase_execution_points(self):
        state = new_state()
        issue = plan(sessions=2)
        result([issue], state)  # First successful scored sync confirms both IDs.
        issue["body"] = issue["body"].replace("\nS2 | Monday | Session 2", "")
        issue["comments_data"] = [comment("/done S1 2026-10-26")]
        row = result([issue], state)
        self.assertEqual((row["confirmed_planned"], row["current_planned"], row["planned"]), (2, 1, 2))
        self.assertTrue(row["plan_changed"])
        self.assertEqual(row["execution_points"], 3)
        self.assertEqual(row["completion_rate"], 0.5)
        self.assertEqual([(s["id"], s["status"], s["confirmed"]) for s in row["sessions"]],
                         [("S1", "completed", True), ("S2", "planned", True)])

    def test_extra_sessions_are_visible_without_raising_score_or_denominator(self):
        state = new_state()
        issue = plan(sessions=1)
        result([issue], state)
        issue["body"] = issue["body"].replace("S1 | Monday | Session 1", "S1 | Monday | Session 1\nS2 | Tuesday | Extra")
        issue["comments_data"] = [comment("/done S2 2026-10-27")]
        row = result([issue], state)
        self.assertEqual((row["planned"], row["current_planned"], row["completed"]), (1, 2, 0))
        self.assertEqual(row["execution_points"], 0)
        self.assertEqual(row["recorded_training_days"], 1)
        self.assertEqual(row["sessions"][1]["status"], "completed")
        self.assertFalse(row["sessions"][1]["confirmed"])
        board = build_week([issue], WEEK, AS_OF, ranking_state=state)
        self.assertEqual(sum(item["planned"] for item in board["sports"]), 1)

    def test_partial_receives_half_credit_without_claiming_a_full_completion(self):
        issue = plan(sessions=3)
        issue["comments_data"] = [comment("/done S1 2026-10-26"), comment("/partial S2 2026-10-27")]
        row = result([issue])
        self.assertEqual((row["completed"], row["partial"]), (1, 1))
        self.assertAlmostEqual(row["completion_rate"], 1 / 3, places=6)
        self.assertEqual(row["execution_rate"], 0.5)
        self.assertEqual(row["execution_points"], 3)
        # A later partial replaces a completion, rather than stacking with it.
        issue["comments_data"].append({**comment("/partial S1 2026-10-26"), "id": 99})
        self.assertEqual(result([issue])["execution_points"], 2)

    def test_withdrawal_and_reentry_keep_the_original_denominator(self):
        state = new_state()
        issue = plan(sessions=3)
        result([issue], state)
        fingerprint = plan_fingerprint(WEEK, "alice")
        original = deepcopy(state["confirmed_plans"][fingerprint])
        issue["body"] = issue["body"].replace("### Public leaderboard\n\nYes", "### Public leaderboard\n\nNo")
        board = build_week([issue], WEEK, AS_OF, ranking_state=state)
        self.assertEqual(board["leaderboard"], [])
        self.assertEqual(state["confirmed_plans"][fingerprint], original)
        issue["body"] = issue["body"].replace("### Public leaderboard\n\nNo", "### Public leaderboard\n\nYes")
        issue["body"] = issue["body"].replace("\nS2 | Monday | Session 2", "").replace("\nS3 | Monday | Session 3", "")
        issue["comments_data"] = [comment("/done S1 2026-10-26")]
        self.assertEqual(result([issue], state)["execution_points"], 2)

    def test_optout_recovery_and_pause_do_not_create_new_confirmations(self):
        state = new_state()
        paused = plan(handle="paused", number=3)
        paused["comments_data"] = [comment("/pause", "paused")]
        board = build_week([plan(public="No"), plan(handle="recovering", number=2, mode="Recovery"), paused],
                           WEEK, AS_OF, ranking_state=state)
        self.assertEqual(board["leaderboard"], [])
        self.assertEqual(state["confirmed_plans"], {})

    def test_state_persists_only_structure_and_confirmation_fingerprints(self):
        state = new_state()
        issue = plan(sessions=2)
        result([issue], state)
        entry = next(iter(state["confirmed_plans"].values()))
        entry["raw_notes"] = "PRIVATE_NOTES"
        entry["sessions"][0]["description"] = "PRIVATE_DESCRIPTION"
        state["raw_body"] = "PRIVATE_BODY"
        with TemporaryDirectory() as directory:
            path = Path(directory) / "ranking-state.json"
            save_state(path, state)
            serialized = path.read_text()
            self.assertNotIn("PRIVATE", serialized)
            self.assertNotIn("alice", serialized)
            self.assertNotIn("example/club", serialized)
            loaded = load_state(path)
            self.assertEqual(len(loaded["confirmed_plans"]), 1)
            self.assertEqual(len(next(iter(loaded["confirmed_plans"].values()))["sessions"]), 2)
            path.write_text("{broken")
            with self.assertRaisesRegex(ValueError, "restore"):
                load_state(path)


class RecordCountTests(unittest.TestCase):
    def test_meal_dates_and_training_dates_are_distinct_counts_without_points(self):
        issue = plan(sessions=3)
        issue["comments_data"] = [
            comment("/meal 2026-10-26 | PRIVATE_BREAKFAST"),
            comment("/meal 2026-10-26 | PRIVATE_LUNCH"),
            comment("/meal 2026-10-27 | PRIVATE_DINNER"),
            comment("/meal 2026-11-02 | Outside the week"),
            comment("/meal 2026-10-28", "someone-else"),
            comment("/done S1 2026-10-26"),
            comment("/partial S2 2026-10-26"),
            comment("/skip S3 2026-10-27"),
        ]
        row = result([issue])
        self.assertEqual((row["meal_days"], row["recorded_training_days"]), (2, 1))
        self.assertEqual(row["total_points"], 4)
        self.assertNotIn("PRIVATE", json.dumps(row))

    def test_historical_withdrawal_recomputes_counts_and_respects_pause(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("<!-- CLUB:START -->\n<!-- CLUB:END -->")
            old_plan = plan()
            archived = build_week([old_plan], WEEK, AS_OF)
            write_reports(root, [archived])
            old_plan["comments_data"] = [comment("/pause")]
            later = AS_OF + timedelta(days=7)
            write_reports(root, [build_week([], "2026-11-02", later)], source_records=[old_plan], as_of=later)
            saved = json.loads((root / "reports" / f"{WEEK}.json").read_text())
            self.assertEqual((saved["participants_count"], saved["recovery_count"]), (1, 1))
            self.assertEqual(saved["leaderboard"], [])
            self.assertEqual(saved["generated_at"], archived["generated_at"])
            self.assertEqual(saved["counts_updated_at"], later.isoformat().replace("+00:00", "Z"))
            write_reports(root, [build_week([], "2026-11-02", later)], source_records=[], as_of=later)
            deleted = json.loads((root / "reports" / f"{WEEK}.json").read_text())
            self.assertEqual((deleted["participants_count"], deleted["recovery_count"]), (0, 0))

    def test_anonymous_historical_counts_refresh_without_changing_retained_scores(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("<!-- CLUB:START -->\n<!-- CLUB:END -->")
            visible = plan()
            hidden = plan(number=2, handle="hidden-member", public="No")
            old = build_week([visible, hidden], WEEK, AS_OF)
            write_reports(root, [old])
            later = AS_OF + timedelta(days=7)
            visible["comments_data"] = [comment("/done S1 2026-10-26")]
            write_reports(root, [build_week([], "2026-11-02", later)], source_records=[visible], as_of=later)
            saved = json.loads((root / "reports" / f"{WEEK}.json").read_text())
            self.assertEqual(saved["participants_count"], 1)
            self.assertEqual(saved["leaderboard"][0]["total_points"], old["leaderboard"][0]["total_points"])
            self.assertEqual(saved["leaderboard"][0]["completed"], 0)
            self.assertNotIn("hidden-member", json.dumps(saved))

    def test_live_sync_confirms_but_dry_run_does_not_write_ledger(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("<!-- CLUB:START -->\n<!-- CLUB:END -->")
            issue = plan(sessions=2)
            issue["created_at"] = "2020-01-01T00:00:00Z"
            args = ["--root", str(root), "--week", WEEK]
            with patch("scripts.sync_github.GitHubReader") as reader, redirect_stdout(StringIO()):
                reader.return_value.records.return_value = [issue]
                self.assertEqual(sync_main(args + ["--dry-run"]), 0)
                reader.return_value.records.assert_called_once_with(
                    [WEEK], cache_path=None, refresh=False, deleted_issue=None
                )
                self.assertFalse((root / "data" / "ranking-state.json").exists())
                self.assertFalse((root / ".club-cache").exists())
                reader.return_value.records.reset_mock()
                self.assertEqual(sync_main(args + ["--dry-run", "--cache", str(root / "custom-cache.json")]), 0)
                reader.return_value.records.assert_called_once_with(
                    [WEEK], cache_path=None, refresh=False, deleted_issue=None
                )
                self.assertEqual(sync_main(args), 0)
            state = load_state(root / "data" / "ranking-state.json")
            self.assertEqual(len(state["confirmed_plans"]), 1)

    def test_fixture_sync_uses_temporary_state_and_rejects_the_live_ledger(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("<!-- CLUB:START -->\n<!-- CLUB:END -->")
            fixture = root / "synthetic.json"
            fixture.write_text(json.dumps([plan(sessions=1)]))
            args = ["--root", str(root), "--week", WEEK, "--fixture", str(fixture),
                    "--as-of", AS_OF.isoformat()]
            with patch("scripts.sync_github.load_state") as load, redirect_stdout(StringIO()):
                self.assertEqual(sync_main(args), 0)
                load.assert_not_called()
            self.assertFalse((root / "data" / "ranking-state.json").exists())
            for selected in (root / "data" / ".." / "data" / "ranking-state.json",
                             REPOSITORY_ROOT / "data" / "ranking-state.json"):
                with self.subTest(selected=selected), patch("scripts.sync_github.save_state") as save, \
                        redirect_stderr(StringIO()):
                    self.assertEqual(sync_main(args + ["--ranking-state", str(selected)]), 1)
                    save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
