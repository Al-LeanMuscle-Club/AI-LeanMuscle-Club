"""Behavioral checks for local incremental reads and cache reconciliation."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.github_api import GitHubReader


WEEK = "2026-10-26"
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


def issue(number=1, labels=("weekly-plan",), week=WEEK, count=1):
    return {
        "number": number, "labels": [{"name": label} for label in labels],
        "body": f"### Week starting\n\n{week}\n\n### Notes\n\nRaw note stays local.",
        "updated_at": "2026-10-28T10:00:00Z", "comments": count,
    }


def comment(text="/done S1 2026-10-27"):
    return {
        "id": 7, "body": text, "updated_at": "2026-10-28T10:00:00Z",
        "issue_url": "https://api.github.com/repos/example/club/issues/1",
    }


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.cache = Path(self.temporary.name) / ".club-cache" / "issues.json"
        self.reader = GitHubReader("example/club", "TEST_TOKEN_MUST_NOT_BE_SAVED")
        self.calls = []
        self.initial_issues = [issue(), issue(2, week="2026-10-19")]
        self.experiences = [issue(3, labels=("experience",), count=0)]
        self.updates = []
        self.comment_updates = []
        self.thread = [comment()]
        self.fail_thread = False

    def pages(self, path, params=None):
        self.calls.append((path, dict(params or {})))
        if path == "issues" and "labels" in params:
            return deepcopy(self.initial_issues if params["labels"] == "weekly-plan" else self.experiences)
        if path == "issues":
            return deepcopy(self.updates)
        if path == "issues/comments":
            return deepcopy(self.comment_updates)
        if path == "issues/1/comments":
            if self.fail_thread:
                raise RuntimeError("Simulated temporary API failure")
            return deepcopy(self.thread)
        raise AssertionError(f"Unexpected API request: {path}")

    def read(self, now=NOW, refresh=False, deleted_issue=None):
        with patch.object(GitHubReader, "_pages", self.pages), patch("scripts.github_api._now", return_value=now):
            return self.reader.records([WEEK], cache_path=self.cache, refresh=refresh, deleted_issue=deleted_issue)

    def test_first_read_saves_only_complete_private_cache_and_target_comments(self):
        records = self.read()
        self.assertEqual([record["number"] for record in records], [1, 2, 3])
        self.assertEqual(records[0]["comments_data"][0]["body"], "/done S1 2026-10-27")
        self.assertNotIn("comments_data", records[1])
        self.assertEqual([path for path, _ in self.calls if path.endswith("/comments")], ["issues/1/comments"])
        saved = self.cache.read_text()
        self.assertNotIn("TEST_TOKEN", saved)
        self.assertEqual(self.cache.stat().st_mode & 0o777, 0o600)
        value = json.loads(saved)
        self.assertEqual(value["repository"], "example/club")
        self.assertEqual(set(value["comments"]), {"1"})
        self.assertNotIn("comments_data", value["issues"]["1"])

    def test_unchanged_run_uses_overlapping_unfiltered_delta_and_cached_thread(self):
        first = self.read()
        self.calls.clear()
        second = self.read(NOW + timedelta(hours=1))
        self.assertEqual(first, second)
        self.assertEqual([path for path, _ in self.calls], ["issues", "issues/comments"])
        params = self.calls[0][1]
        self.assertNotIn("labels", params)
        self.assertEqual(params["since"], "2026-10-28T11:55:00Z")

    def test_comment_edit_refetches_thread_even_if_issue_metadata_is_unchanged(self):
        self.read()
        self.calls.clear()
        self.comment_updates = [comment("/partial S1 2026-10-27")]
        self.thread = self.comment_updates
        records = self.read(NOW + timedelta(hours=1))
        self.assertEqual(records[0]["comments_data"][0]["body"], "/partial S1 2026-10-27")
        self.assertIn("issues/1/comments", [path for path, _ in self.calls])

    def test_deleted_comment_count_forces_refetch_and_removes_stale_completion(self):
        self.read()
        self.updates = [issue(count=0)]
        self.thread = []
        records = self.read(NOW + timedelta(hours=1))
        self.assertEqual(records[0]["comments_data"], [])
        self.assertEqual(json.loads(self.cache.read_text())["comments"]["1"]["data"], [])

    def test_removed_label_and_revoked_approval_are_not_retained(self):
        self.experiences = [issue(3, labels=("experience", "points-approved"), count=0)]
        self.read()
        self.updates = [issue(labels=()), issue(3, labels=("experience",), count=0)]
        records = self.read(NOW + timedelta(hours=1))
        self.assertNotIn(1, [record["number"] for record in records])
        contribution = next(record for record in records if record["number"] == 3)
        self.assertEqual(contribution["labels"], [{"name": "experience"}])
        self.assertNotIn("1", json.loads(self.cache.read_text())["comments"])

    def test_missing_reliable_metadata_refetches_comments(self):
        self.initial_issues[0].pop("updated_at")
        self.read()
        self.calls.clear()
        self.thread = [comment("/skip S1 2026-10-27")]
        records = self.read(NOW + timedelta(hours=1))
        self.assertEqual(records[0]["comments_data"][0]["body"], "/skip S1 2026-10-27")
        self.assertIn("issues/1/comments", [path for path, _ in self.calls])

    def test_failure_preserves_entire_cache_and_sync_cursor(self):
        self.read()
        original = self.cache.read_bytes()
        self.updates = [dict(issue(), updated_at="2026-10-28T12:30:00Z")]
        self.fail_thread = True
        with self.assertRaisesRegex(RuntimeError, "temporary"):
            self.read(NOW + timedelta(hours=1))
        self.assertEqual(self.cache.read_bytes(), original)

    def test_deletion_event_immediately_evicts_cached_issue_and_comments(self):
        self.read()
        self.calls.clear()
        # Empty incremental response: GitHub no longer lists the deleted Issue.
        records = self.read(NOW + timedelta(hours=1), deleted_issue=1)
        self.assertEqual([record["number"] for record in records], [2, 3])
        cache = json.loads(self.cache.read_text())
        self.assertNotIn("1", cache["issues"])
        self.assertNotIn("1", cache["comments"])
        # Repeated deletion notifications are safe and do not remove other records.
        again = self.read(NOW + timedelta(hours=2), deleted_issue=1)
        self.assertEqual([record["number"] for record in again], [2, 3])
        self.assertEqual([path for path, _ in self.calls if path == "issues" and "labels" in _], [])

    def test_invalid_deletion_number_fails_before_cache_mutation(self):
        self.read()
        original = self.cache.read_bytes()
        with self.assertRaises(ValueError):
            self.read(NOW + timedelta(hours=1), deleted_issue=0)
        self.assertEqual(original, self.cache.read_bytes())

    def test_deleted_issue_is_not_resurrected_by_stale_incremental_metadata(self):
        self.read()
        self.updates = [issue()]
        self.comment_updates = [comment()]
        self.fail_thread = True
        records = self.read(NOW + timedelta(hours=1), deleted_issue=1)
        self.assertEqual([record["number"] for record in records], [2, 3])
        self.assertNotIn("1", json.loads(self.cache.read_text())["issues"])

    def test_seven_day_full_reconciliation_drops_deleted_issues(self):
        self.read()
        self.calls.clear()
        self.initial_issues = []
        records = self.read(NOW + timedelta(days=7))
        self.assertEqual([record["number"] for record in records], [3])
        self.assertEqual([params["labels"] for path, params in self.calls if path == "issues"], ["weekly-plan", "experience"])
        self.assertEqual(json.loads(self.cache.read_text())["comments"], {})

    def test_refresh_reconciles_before_seven_days(self):
        self.read()
        self.calls.clear()
        self.initial_issues = []
        self.assertEqual([record["number"] for record in self.read(NOW + timedelta(hours=1), refresh=True)], [3])
        self.assertNotIn("since", self.calls[0][1])

    def test_corrupt_foreign_or_future_cache_is_rebuilt_without_reusing_records(self):
        for content in ("{broken", json.dumps({"repository": "other/repo"}), json.dumps({
            "schema_version": 1, "repository": "example/club", "issues": {"999": issue(999)}, "comments": {},
            "last_sync": "2099-01-01T00:00:00Z", "full_sync": "2099-01-01T00:00:00Z",
        })):
            with self.subTest(content=content):
                self.cache.parent.mkdir(parents=True, exist_ok=True)
                self.cache.write_text(content)
                self.calls.clear()
                records = self.read()
                self.assertNotIn(999, [record["number"] for record in records])
                self.assertIn("labels", self.calls[0][1])


class SingleIssueTests(unittest.TestCase):
    def test_positive_issue_number_and_optional_full_thread(self):
        reader = GitHubReader("example/club", "token")
        with patch.object(reader, "_get", return_value=issue()) as get, patch.object(reader, "_pages", return_value=[comment()]) as pages:
            value = reader.get_issue(1, include_comments=True)
        get.assert_called_once_with("issues/1")
        pages.assert_called_once_with("issues/1/comments")
        self.assertEqual(len(value["comments_data"]), 1)

    def test_invalid_numbers_and_pull_requests_are_rejected(self):
        reader = GitHubReader("example/club", "token")
        for number in (0, -1, True, "1", "1/comments"):
            with self.subTest(number=number), self.assertRaises(ValueError):
                reader.get_issue(number)
        with patch.object(reader, "_get", return_value={**issue(), "pull_request": {}}), self.assertRaisesRegex(RuntimeError, "pull request"):
            reader.get_issue(1)


if __name__ == "__main__":
    unittest.main()
