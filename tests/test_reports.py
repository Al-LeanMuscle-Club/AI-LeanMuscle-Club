"""Integration tests for public report generation and its live API boundary."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from github_api import GitHubReader, validate_repository
from sync_github import replace_readme, reporting_weeks, write_reports
from club.scoring import build_week

AS_OF = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)


def plan(number=1, handle="member-one", public="Yes"):
    return {
        "number": number, "user": {"login": handle},
        "labels": [{"name": "weekly-plan"}],
        "html_url": f"https://github.com/example/club/issues/{number}",
        "created_at": "2026-10-25T10:00:00Z",
        "body": "\n\n".join([
            "### Week starting\n\n2026-10-26",
            "### Time zone\n\nAsia/Shanghai",
            "### Participation mode\n\nActive",
            f"### Public leaderboard\n\n{public}",
            "### Planned sessions\n\nS1 | Monday | Walk\nS2 | Wednesday | Strength\nS3 | Friday | Basketball",
            "### Busy-week fallback\n\nOne short session",
            "### Notes\n\nPRIVATE_DETAIL_NOT_FOR_REPORTS",
        ]),
        "comments_data": [
            {"user": {"login": handle}, "created_at": "2026-10-26T12:00:00Z", "body": "/done S1 2026-10-26 | Felt good."},
            {"user": {"login": handle}, "created_at": "2026-10-28T12:00:00Z", "body": "/done S2 2026-10-28 | Kept it short."},
            {"user": {"login": handle}, "created_at": "2026-11-01T12:00:00Z", "body": "/review\nTwo sessions fit this week. Try again next week."},
        ],
    }


class ReportingTests(unittest.TestCase):
    def test_china_monday_rollover_and_year_boundary(self):
        instant = datetime(2026, 10, 25, 16, tzinfo=timezone.utc)
        self.assertEqual(reporting_weeks(instant), ["2026-10-26", "2026-10-19"])
        instant = datetime(2027, 1, 1, 0, tzinfo=timezone.utc)
        self.assertEqual(reporting_weeks(instant), ["2026-12-28", "2026-12-21"])
        with self.assertRaises(ValueError):
            reporting_weeks(instant, "2026-10-27")

    def test_reports_preserve_prose_and_do_not_publish_optouts_or_raw_notes(self):
        records = [plan(), plan(2, "private-member", "No")]
        board = build_week(records, "2026-10-26", AS_OF)
        self.assertEqual(board["participants_count"], 2)
        self.assertEqual(board["leaderboard"][0]["total_points"], 7)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("Important intro\n<!-- CLUB:START -->\nold board\n<!-- CLUB:END -->\nImportant footer\n", encoding="utf-8")
            write_reports(root, [board])
            text = (root / "README.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("Important intro\n"))
            self.assertTrue(text.endswith("Important footer\n"))
            public_text = "\n".join(p.read_text(encoding="utf-8") for p in root.rglob("*.md"))
            public_text += (root / "reports/2026-10-26.json").read_text(encoding="utf-8")
            self.assertIn("member-one", public_text)
            self.assertNotIn("private-member", public_text)
            self.assertNotIn("PRIVATE_DETAIL_NOT_FOR_REPORTS", public_text)
            self.assertNotIn("Felt good", public_text)

    def test_invalid_readme_cannot_silently_replace_content_or_write_reports(self):
        board = build_week([], "2026-10-26", AS_OF)
        for text in ("No markers", "<!-- CLUB:END --><!-- CLUB:START -->", "<!-- CLUB:START --><!-- CLUB:START --><!-- CLUB:END -->"):
            with self.assertRaises(ValueError):
                replace_readme(text, [board])
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("Keep this", encoding="utf-8")
            with self.assertRaises(ValueError):
                write_reports(root, [board])
            self.assertFalse((root / "reports").exists())
            self.assertEqual((root / "README.md").read_text(), "Keep this")

    def test_complete_offline_cli_without_network_or_credentials(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Test\n<!-- CLUB:START -->\n<!-- CLUB:END -->\n", encoding="utf-8")
            fixture = root / "synthetic.json"
            fixture.write_text(json.dumps([plan()]), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/sync_github.py"),
                "--fixture", str(fixture), "--week", "2026-10-26",
                "--as-of", AS_OF.isoformat(), "--root", str(root),
            ], capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((root / "reports/2026-10-26.json").read_text())
            self.assertEqual(data["leaderboard"][0]["total_points"], 7)
            self.assertIn("member-one", (root / "README.md").read_text())


class ApiBoundaryTests(unittest.TestCase):
    def test_pagination_collects_all_records_and_comments_only_for_target_week(self):
        calls = []
        first_page = [dict(plan(i + 1, f"member-{i+1}"), comments_data=[]) for i in range(100)]
        # Only two plans are in the target week; old history needs no comment fetch.
        for issue in first_page[2:]:
            issue["body"] = issue["body"].replace("2026-10-26", "2026-10-19")

        def fake_get(self, path, params=None):
            calls.append((path, dict(params or {})))
            if path == "issues":
                if params["labels"] == "experience,points-approved":
                    return []
                return first_page if params["page"] == 1 else []
            return []

        with patch.object(GitHubReader, "_get", fake_get):
            records = GitHubReader("example/club", "test-token").records(["2026-10-26"])
        self.assertEqual(len(records), 100)
        self.assertEqual([path for path, _ in calls if path.endswith("/comments")], ["issues/1/comments", "issues/2/comments"])
        self.assertTrue(any(path == "issues" and params["page"] == 2 for path, params in calls))

    def test_repository_validation_prevents_url_or_path_injection(self):
        self.assertEqual(validate_repository("Al-LeanMuscle-Club/AI-Lean-Muscle-Club"), "Al-LeanMuscle-Club/AI-Lean-Muscle-Club")
        for invalid in ("https://example.com/repo", "../repo/other", "a/b?token=oops", "a/b\ncommand", "a/b/c"):
            with self.assertRaises(ValueError):
                validate_repository(invalid)


if __name__ == "__main__":
    unittest.main()
