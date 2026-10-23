"""Member drafts, preflight checks, and bot feedback stay read-only and bounded."""

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from club.scoring import validate_submission
from scripts.member_tools import carry_plan, find_plans
from scripts.check_submission import feedback_body, upsert_feedback, MARKER
from scripts.github_api import GitHubReader

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)


def record(number=1):
    return {
        "number": number, "user": {"login": "alice"},
        "html_url": f"https://github.com/example/club/issues/{number}",
        "created_at": "2026-10-25T12:00:00Z", "labels": [{"name": "weekly-plan"}],
        "body": "\n\n".join([
            "### Week starting\n\n2026-10-26", "### Time zone\n\nUTC",
            "### Participation mode\n\nActive", "### Public leaderboard\n\nYes",
            "### Primary goal\n\nmuscle-gain", "### Research week\n\ndeadline",
            "### Planned sessions\n\n- [x] S1 | Monday | strength | Gym | Home session",
            "### Busy-week fallback\n\nKeep it short", "### Notes\n\nOptional",
        ]),
    }


class MemberToolTests(unittest.TestCase):
    def test_carry_retains_intent_but_resets_consent_and_checkboxes(self):
        p = record()
        draft = carry_plan(p["body"], "2026-11-02")
        self.assertIn("### Public leaderboard\n\nNo", draft)
        self.assertIn("- [ ] S1 | Monday | strength | Gym | Home session", draft)
        self.assertIn("### Primary goal\n\nmuscle-gain", draft)
        copied = deepcopy(p)
        copied["body"] = draft
        self.assertEqual(validate_submission(copied, now=NOW), [])
        self.assertIn("### Public leaderboard\n\nYes", p["body"])
        with self.assertRaises(ValueError):
            carry_plan(p["body"], "2026-11-03")

    def test_find_uses_earliest_valid_plan_for_user_and_selected_week(self):
        later = record(2)
        later["created_at"] = "2026-10-26T10:00:00Z"
        invalid = record(3)
        invalid["body"] = invalid["body"].replace("muscle-gain", "unknown-goal")
        self.assertEqual([p["number"] for p in find_plans([later, invalid, record()], "ALICE", "2026-10-26", NOW)], [1, 2])
        self.assertEqual(find_plans([record()], "bob", "2026-10-26", NOW), [])

    def test_offline_cli_generates_draft_and_validates_checkin_without_credentials(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "synthetic.json"
            fixture.write_text(json.dumps([record()]))
            output = root / "draft.md"
            command = [sys.executable, str(ROOT / "scripts/member_tools.py"), "--fixture", str(fixture), "--as-of", NOW.isoformat()]
            result = subprocess.run(command + ["carry", "--issue", "1", "--week", "2026-11-02", "--output", str(output)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("### Public leaderboard\n\nNo", output.read_text())
            comment = root / "comment.txt"
            comment.write_text("/fallback S1 2026-10-26 | Used the home plan")
            result = subprocess.run(command + ["check", "--issue", "1", "--comment-file", str(comment)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            comment.write_text("/done S99 2026-10-26")
            result = subprocess.run(command + ["check", "--issue", "1", "--comment-file", str(comment)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn("session ID", result.stderr)


class FeedbackTests(unittest.TestCase):
    def test_errors_are_fixed_text_and_do_not_echo_untrusted_body(self):
        p = record()
        p["body"] = p["body"].replace("UTC", "DO_NOT_ECHO_$(secret)")
        body = feedback_body(p, now=NOW)
        self.assertIn("IANA", body)
        self.assertNotIn("DO_NOT_ECHO", body)
        self.assertIn(MARKER, body)

    def test_bot_peer_chat_and_pull_requests_do_not_trigger_feedback(self):
        p = record()
        for comment in [
            {"user": {"login": "bob"}, "body": "/done S1 2026-10-26"},
            {"user": {"login": "alice", "type": "Bot"}, "body": "/done S1 2026-10-26"},
            {"user": {"login": "alice"}, "body": "Good week!"},
        ]:
            self.assertIsNone(feedback_body(p, comment, now=NOW))
        self.assertIsNone(feedback_body({**p, "pull_request": {}}, now=NOW))

    def test_unchanged_bot_status_does_not_post_again(self):
        body = feedback_body(record(), now=NOW)
        reader = GitHubReader("example/club", "test-only")
        comments = [{"id": 10, "user": {"login": "github-actions[bot]", "type": "Bot"}, "body": body}]
        with patch.object(reader, "_pages", return_value=iter(comments)), patch("scripts.check_submission.urlopen") as request:
            upsert_feedback(reader, 1, body)
            request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
