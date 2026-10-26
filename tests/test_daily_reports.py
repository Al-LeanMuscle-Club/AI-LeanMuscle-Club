"""Daily-board integration: complete reads, privacy, migration, and publication."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from club.daily_checkins import build_week
from scripts.github_api import GitHubReader
from scripts.sync_daily import main, public_snapshot, reporting_weeks, write_reports

REPO = "sample/club"
WEEK = "2026-10-26"
AS_OF = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)


def journal(number=1, handle="synthetic-one", public="Yes", **changes):
    record = {"number": number, "title": "[Check-in] My journal", "state": "open",
              "user": {"login": handle, "id": number, "type": "User"}, "labels": [],
              "created_at": "2026-10-01T10:00:00Z",
              "body": f"### Time zone\n\nUTC\n\n### Public leaderboard\n\n{public}\n",
              "comments_data": [{"id": number, "user": {"login": handle, "id": number},
                                 "created_at": "2026-10-27T12:00:00Z",
                                 "body": "/checkin 2026-10-27 W=1 E=1\nPRIVATE_NOTE"}]}
    record.update(changes)
    return record


def prepare(root):
    home = "# Club\n## News\nKeep these real stories.\n<!-- CLUB:START -->old overview<!-- CLUB:END -->\nFooter\n"
    (root / "README.md").write_text(home)
    (root / "reports").mkdir()
    (root / "reports/index.json").write_text("LEGACY_REPORT_UNCHANGED")
    (root / "data").mkdir()
    (root / "data/ranking-state.json").write_text("LEGACY_LEDGER_UNCHANGED")
    return home


class SnapshotReader(GitHubReader):
    def __init__(self, issues, comments):
        super().__init__(REPO, "synthetic-test-token")
        self.issues, self.comments, self.calls = issues, comments, []

    def _pages(self, path, params=None):
        self.calls.append((path, params))
        if path == "issues":
            yield from deepcopy(self.issues)
        else:
            number = int(path.split("/")[1])
            batch = self.comments[number]
            if isinstance(batch, Exception):
                raise batch
            yield from deepcopy(batch)


class DailyReaderTests(unittest.TestCase):
    def test_reads_unlabelled_closed_and_opted_out_journals_but_not_other_posts(self):
        issues = [journal(), journal(2, "synthetic-two", "No", state="closed"),
                  journal(3, title="[Experience] Story"), journal(4, pull_request={}),
                  journal(5, title="[Check-in] [虚构演示｜打卡] example")]
        client = SnapshotReader(issues, {1: [{"id": 1}], 2: []})
        records = client.daily_checkins()
        self.assertEqual([r["number"] for r in records], [1, 2])
        self.assertEqual(client.calls, [("issues", {"state": "all"}),
                                        ("issues/1/comments", None), ("issues/2/comments", None)])
        self.assertEqual(records[0]["comments_data"], [{"id": 1}])

    def test_fresh_snapshot_observes_deleted_and_edited_comments(self):
        issue = journal()
        client = SnapshotReader([issue], {1: issue["comments_data"]})
        self.assertEqual(len(client.daily_checkins()[0]["comments_data"]), 1)
        client.comments[1] = []
        self.assertEqual(client.daily_checkins()[0]["comments_data"], [])
        client.comments[1] = [{"id": 1, "body": "/checkin 2026-10-27 W=0 E=0"}]
        self.assertIn("W=0 E=0", client.daily_checkins()[0]["comments_data"][0]["body"])

    def test_failures_never_return_partial_or_malformed_snapshots(self):
        for issues, comments in [([journal(), None], {1: []}),
                                 ([{}], {}), ([{"number": True}], {}),
                                 ([journal()], {1: ["invalid"]}),
                                 ([journal()], {1: RuntimeError("API unavailable")})]:
            with self.subTest(issues=issues), self.assertRaises(RuntimeError):
                SnapshotReader(issues, comments).daily_checkins()

    def test_malformed_issue_batch_cannot_clear_existing_public_history(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            prepare(root)
            records = [journal()]
            write_reports(root, [build_week(records, WEEK, AS_OF, repository=REPO)], records, REPO)
            before = {str(path.relative_to(root)): path.read_bytes()
                      for path in root.rglob("*") if path.is_file()}
            with patch("scripts.sync_daily.GitHubReader", return_value=SnapshotReader([{}], {})), redirect_stderr(StringIO()):
                self.assertEqual(main(["--root", str(root), "--repository", REPO]), 1)
            after = {str(path.relative_to(root)): path.read_bytes()
                     for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)


class DailyPublicationTests(unittest.TestCase):
    def test_week_selection_uses_shanghai_calendar_and_rejects_future_or_non_monday(self):
        sunday_utc = datetime(2026, 10, 25, 16, tzinfo=timezone.utc)
        self.assertEqual(reporting_weeks(sunday_utc), ["2026-10-26", "2026-10-19"])
        self.assertEqual(reporting_weeks(AS_OF, WEEK), [WEEK])
        for value in ("2026-10-27", "2026-11-09", "../../bad", "2026-02-30"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                reporting_weeks(AS_OF, value)
        with self.assertRaises(ValueError):
            reporting_weeks(datetime(2026, 10, 26))

    def test_v3_publication_keeps_legacy_files_and_editorial_content(self):
        records = [journal()]
        board = build_week(records, WEEK, AS_OF, repository=REPO)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            before = prepare(root)
            write_reports(root, [board], records, REPO)
            home = (root / "README.md").read_text()
            self.assertTrue(home.startswith(before.split("<!-- CLUB:START -->")[0]))
            self.assertTrue(home.endswith("<!-- CLUB:END -->\nFooter\n"))
            self.assertIn("reports/daily/2026-10-26.md", home)
            self.assertEqual((root / "reports/index.json").read_text(), "LEGACY_REPORT_UNCHANGED")
            self.assertEqual((root / "data/ranking-state.json").read_text(), "LEGACY_LEDGER_UNCHANGED")
            index = json.loads((root / "reports/daily/index.json").read_text())
            self.assertEqual(index["scoring_version"], 3)
            self.assertEqual(index["weeks"][0]["leaderboard"][0]["score"], 22.36)
            for path in (root / "reports/daily").iterdir():
                self.assertNotIn("PRIVATE_NOTE", path.read_text())
                self.assertNotIn("synthetic-test-token", path.read_text())

    def test_optout_withdraws_saved_history_and_reranks_without_touching_legacy(self):
        records = [journal(), journal(2, "synthetic-two")]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            prepare(root)
            write_reports(root, [build_week(records, WEEK, AS_OF, repository=REPO)], records, REPO)
            records[0]["body"] = records[0]["body"].replace("Yes", "No")
            next_week = build_week(records, "2026-11-02", AS_OF, repository=REPO)
            write_reports(root, [next_week], records, REPO)
            old = json.loads((root / "reports/daily/2026-10-26.json").read_text())
            self.assertEqual(old["participants_count"], 1)
            self.assertEqual(old["leaderboard"][0]["handle"], "synthetic-two")
            self.assertEqual(old["leaderboard"][0]["rank"], 1)
            for path in (root / "reports/daily").iterdir():
                self.assertNotIn("synthetic-one", path.read_text())
            self.assertEqual((root / "data/ranking-state.json").read_text(), "LEGACY_LEDGER_UNCHANGED")

    def test_historical_refresh_cannot_move_homepage_backwards(self):
        records = [journal()]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            prepare(root)
            write_reports(root, [build_week(records, WEEK, AS_OF, repository=REPO),
                                 build_week(records, "2026-11-02", AS_OF, repository=REPO)], records, REPO)
            before = (root / "README.md").read_text()
            write_reports(root, [build_week(records, WEEK, AS_OF, repository=REPO)], records, REPO)
            self.assertEqual((root / "README.md").read_text(), before)
            self.assertIn("2026-11-02", before)

    def test_projection_drops_unapproved_fields_and_reconstructs_source_urls(self):
        board = build_week([journal()], WEEK, AS_OF, repository=REPO)
        board["raw_body"] = "PRIVATE_NOTE"
        board["leaderboard"][0].update(raw_body="PRIVATE_NOTE", issue_url="javascript:alert(1)")
        safe = public_snapshot(board, REPO)
        self.assertNotIn("PRIVATE_NOTE", json.dumps(safe))
        self.assertEqual(safe["leaderboard"][0]["issue_url"], "https://github.com/sample/club/issues/1")
        board["schema_version"] = 2
        with self.assertRaises(ValueError):
            public_snapshot(board, REPO)

    def test_saved_scores_must_match_the_formula_before_publication(self):
        board = build_week([journal()], WEEK, AS_OF, repository=REPO)
        board["leaderboard"][0]["score"] = 100
        with self.assertRaisesRegex(ValueError, "does not match"):
            public_snapshot(board, REPO)

    def test_corrupt_archive_or_readme_fails_before_any_publication(self):
        records = [journal()]
        board = build_week(records, WEEK, AS_OF, repository=REPO)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            prepare(root)
            folder = root / "reports/daily"
            folder.mkdir()
            bad = folder / "2026-10-19.json"
            bad.write_text('{"schema_version":2}')
            before = (root / "README.md").read_bytes()
            with self.assertRaises(ValueError):
                write_reports(root, [board], records, REPO)
            self.assertEqual((root / "README.md").read_bytes(), before)
            self.assertFalse((folder / "2026-10-26.json").exists())
            bad.unlink()
            (root / "README.md").write_text("Missing markers")
            with self.assertRaises(ValueError):
                write_reports(root, [board], records, REPO)
            self.assertEqual(list(folder.iterdir()), [])

    def test_fixture_can_only_dry_run_and_never_touches_output_or_ledger(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            prepare(root)
            fixture = root / "synthetic.json"
            fixture.write_text(json.dumps([journal()]))
            args = ["--root", str(root), "--fixture", str(fixture), "--as-of", "2026-11-02T12:00:00Z", "--week", WEEK]
            with redirect_stderr(StringIO()):
                self.assertEqual(main(args), 1)
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(args + ["--dry-run"]), 0)
            self.assertEqual(json.loads(output.getvalue())[0]["leaderboard"][0]["score"], 22.36)
            self.assertNotIn("PRIVATE_NOTE", output.getvalue())
            self.assertFalse((root / "reports/daily").exists())
            self.assertEqual((root / "data/ranking-state.json").read_text(), "LEGACY_LEDGER_UNCHANGED")

    def test_api_failure_does_not_replace_existing_reports(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            before = prepare(root)
            with patch("scripts.sync_daily.GitHubReader") as reader, redirect_stderr(StringIO()):
                reader.return_value.daily_checkins.side_effect = RuntimeError("Unavailable")
                self.assertEqual(main(["--root", str(root)]), 1)
            self.assertEqual((root / "README.md").read_text(), before)
            self.assertFalse((root / "reports/daily").exists())

    def test_scheduled_publisher_is_limited_to_v3_outputs_and_trusted_code(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/update-reports.yml").read_text()
        self.assertIn("cron: '15 1 * * *'", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("ref: ${{ github.event.repository.default_branch }}", workflow)
        self.assertIn("python scripts/sync_daily.py", workflow)
        self.assertIn("git add -- README.md reports/daily/", workflow)
        for excluded in ("pull_request:", "issue_comment:", "data/ranking-state.json", "--fixture", "actions/cache"):
            self.assertNotIn(excluded, workflow)
        self.assertFalse((root / ".github/workflows/check-submission.yml").exists())
        self.assertFalse((root / ".github/workflows/setup-community.yml").exists())


if __name__ == "__main__":
    unittest.main()
