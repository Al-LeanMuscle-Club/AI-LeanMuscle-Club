"""Behavioral tests for transparent, opt-in community points."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import unittest

from club.scoring import build_week
from club.ranking_state import approve_contribution, new_state


WEEK = "2026-10-26"
AS_OF = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)


def plan(handle="alice", number=1, sessions=3, public="Yes", mode="Active", zone="UTC"):
    rows = "\n".join(f"S{i} | Monday | Session {i}" for i in range(1, sessions + 1))
    return {
        "number": number,
        "title": "Weekly plan",
        "body": (
            f"### Week starting\n\n{WEEK}\n\n"
            f"### Time zone\n\n{zone}\n\n"
            f"### Participation mode\n\n{mode}\n\n"
            f"### Public leaderboard\n\n{public}\n\n"
            f"### Planned sessions\n\n{rows}\n\n"
            "### Busy-week fallback\n\nA short walk.\n\n### Notes\n\nOptional."
        ),
        "labels": [{"name": "weekly-plan"}],
        "user": {"login": handle},
        "html_url": f"https://github.com/example/club/issues/{number}",
        "created_at": "2026-10-25T12:00:00Z",
        "comments_data": [],
    }


def comment(body, author="alice", created="2026-11-01T12:00:00Z"):
    return {"body": body, "user": {"login": author}, "created_at": created}


def contribution(handle="alice", number=100, approved=True):
    return {
        "number": number,
        "body": f"### Week starting\n\n{WEEK}\n\n### Experience\n\nUseful advice.",
        "user": {"login": handle},
        "labels": [{"name": "experience"}] + (
            [{"name": "points-approved"}] if approved else []
        ),
        "created_at": "2026-10-30T12:00:00Z",
    }


def approved_state(*issues, now=AS_OF):
    state = new_state()
    for issue in issues:
        approve_contribution(issue, state, now)
    return state


class ScoringTests(unittest.TestCase):
    def test_full_score_and_fractional_completion(self):
        p = plan()
        p["comments_data"] = [
            comment("/done S1 2026-10-26 | Felt good."),
            comment("/done S2 2026-10-28"),
            comment("/review\nMissed one session; next week I will move it earlier."),
        ]
        state = approved_state(contribution())
        board = build_week([p, contribution()], WEEK, AS_OF, ranking_state=state)
        row = board["leaderboard"][0]
        self.assertEqual(row["completed"], 2)
        self.assertEqual(row["planned"], 3)
        self.assertAlmostEqual(row["completion_rate"], 2 / 3, places=6)
        self.assertEqual(row["execution_points"], 4)
        self.assertEqual(row["total_points"], 8)
        p["comments_data"].append(comment("/done S3 2026-10-31"))
        self.assertEqual(build_week([p, contribution()], WEEK, AS_OF, ranking_state=state)["leaderboard"][0]["total_points"], 10)

    def test_crlf_issue_form_and_multiline_review_are_parsed(self):
        p = plan()
        p["body"] = p["body"].replace("\n", "\r\n")
        p["comments_data"] = [
            comment("/done S1 2026-10-26 | First session.\r\n"),
            comment("/done S2 2026-10-28 | Second session.\r\n"),
            comment(
                "/review\r\nCompleted two sessions.\r\n"
                "Missed one during a deadline.\r\nNext week I will shorten it.\r\n"
            ),
        ]
        board = build_week([p], WEEK, AS_OF)
        self.assertEqual(board["participants_count"], 1)
        self.assertEqual(board["warnings"], [])
        row = board["leaderboard"][0]
        self.assertEqual(row["completed"], 2)
        self.assertEqual(row["review_points"], 2)
        self.assertEqual(row["total_points"], 7)

    def test_crlf_multiline_done_cannot_embed_extra_commands(self):
        p = plan(sessions=1)
        p["comments_data"] = [
            comment("/done S1 2026-10-26\r\n/review\r\nAutomatic extra points."),
            comment("An example follows:\r\n/done S1 2026-10-26"),
            comment("/review\r\n  \r\n"),
        ]
        row = build_week([p], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual(row["completed"], 0)
        self.assertEqual(row["review_points"], 0)
        self.assertEqual(row["total_points"], 1)

    def test_done_first_nonempty_line_allows_photo_and_ordinary_notes(self):
        p = plan(sessions=1)
        p["comments_data"] = [comment(
            "\r\n\r\n/done S1 2026-10-26 | Short strength session.\r\n\r\n"
            "![Optional training photo](https://github.com/user-attachments/assets/example.png)\r\n"
            "Felt tired, so I reduced the final set.\r\n"
            "A note mentioning /review inline is ordinary prose.\r\n"
        )]
        row = build_week([p], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual(row["completed"], 1)
        self.assertEqual(row["total_points"], 7)

    def test_multiple_command_lines_reject_whole_comment_without_stacking(self):
        ambiguous = [
            "/done S1 2026-10-26\n/done S2 2026-10-28",
            "/done S1 2026-10-26\nSome notes.\n/review\nA reflection.",
            "/review\nA reflection.\n/done S1 2026-10-26",
            "/pause\nTaking a break.\n/review\nA reflection.",
            "/done S1 2026-10-26\n  /PAUSE\nTaking a break.",
        ]
        for body in ambiguous:
            with self.subTest(body=body):
                p = plan(sessions=2)
                p["comments_data"] = [comment(body)]
                board = build_week([p], WEEK, AS_OF)
                self.assertEqual(board["recovery_count"], 0)
                row = board["leaderboard"][0]
                self.assertEqual(row["completed"], 0)
                self.assertEqual(row["review_points"], 0)
                self.assertEqual(row["total_points"], 1)

    def test_crlf_author_pause_with_explanation_is_respected(self):
        p = plan()
        p["comments_data"] = [comment("/pause\r\nTaking recovery time.\r\n")]
        board = build_week([p], WEEK, AS_OF)
        self.assertEqual(board["recovery_count"], 1)
        self.assertEqual(board["leaderboard"], [])

    def test_impersonation_and_embedded_commands_do_not_count(self):
        p = plan(sessions=1)
        p["comments_data"] = [
            comment("/done S1 2026-10-26", "mallory"),
            comment("/review\nAll done.", "mallory"),
            comment("/pause", "mallory"),
            comment("> /done S1 2026-10-26"),
            comment("Here is an example: /done S1 2026-10-26"),
        ]
        board = build_week([p], WEEK, AS_OF)
        self.assertEqual(board["recovery_count"], 0)
        self.assertEqual(board["leaderboard"][0]["total_points"], 1)

    def test_duplicate_logs_and_multiple_contributions_are_capped(self):
        p = plan(sessions=1)
        p["comments_data"] = [
            comment("/done S1 2026-10-26"),
            comment("/done S1 2026-10-27 | Again"),
            comment("/done S99 2026-10-27"),
            comment("/review\nFirst reflection."),
            comment("/review\nAnother reflection."),
        ]
        board = build_week([p, contribution(), contribution(number=101)], WEEK, AS_OF,
                           ranking_state=approved_state(contribution(), contribution(number=101)))
        row = board["leaderboard"][0]
        self.assertEqual(row["completed"], 1)
        self.assertEqual(row["contribution_points"], 1)
        self.assertEqual(row["total_points"], 10)

    def test_duplicate_plans_use_earliest_valid_record(self):
        first = plan(sessions=3)
        duplicate = plan(handle="ALICE", number=2, sessions=1)
        duplicate["created_at"] = "2026-10-26T12:00:00Z"
        duplicate["comments_data"] = [comment("/done S1 2026-10-26", "ALICE")]
        board = build_week([duplicate, first], WEEK, AS_OF)
        self.assertEqual(board["participants_count"], 1)
        self.assertEqual(board["leaderboard"][0]["issue_number"], 1)
        self.assertEqual(board["leaderboard"][0]["completed"], 0)
        self.assertTrue(board["warnings"])

    def test_tied_creation_uses_lower_issue_number(self):
        a, b = plan(number=9), plan(number=2)
        board = build_week([a, b], WEEK, AS_OF)
        self.assertEqual(board["leaderboard"][0]["issue_number"], 2)

    def test_invalid_duplicate_cannot_displace_valid_plan(self):
        invalid = plan(number=1, sessions=0)
        valid = plan(number=2)
        board = build_week([invalid, valid], WEEK, AS_OF)
        self.assertEqual(board["leaderboard"][0]["issue_number"], 2)

    def test_opt_out_has_no_public_identifiers(self):
        private = plan(handle="secret-member", public="No")
        private["comments_data"] = [comment("/done S1 2026-10-26", "secret-member")]
        duplicate = deepcopy(private)
        duplicate["number"] = 2
        duplicate["html_url"] = "https://github.com/example/club/issues/2"
        board = build_week([private, duplicate], WEEK, AS_OF)
        self.assertEqual(board["participants_count"], 1)
        self.assertEqual(board["leaderboard"], [])
        serialized = json.dumps(board)
        self.assertNotIn("secret-member", serialized)
        self.assertNotIn("https://github.com", serialized)

    def test_recovery_and_author_pause_excluded_without_penalty(self):
        recovery = plan(handle="resting", sessions=0, mode="Recovery")
        paused = plan(handle="paused", number=2)
        paused["comments_data"] = [comment("/pause\nTaking a break.", "paused")]
        active = plan(handle="active", number=3)
        board = build_week([recovery, paused, active], WEEK, AS_OF)
        self.assertEqual(board["participants_count"], 3)
        self.assertEqual(board["recovery_count"], 2)
        self.assertEqual([r["handle"] for r in board["leaderboard"]], ["active"])

    def test_future_comments_future_declarations_and_other_weeks_ignored(self):
        p = plan(sessions=1)
        p["comments_data"] = [
            comment("/done S1 2026-11-02"),
            comment("/done S1 2026-10-25"),
            comment("/done S1 2026-10-26", created="2026-11-03T00:00:00Z"),
            comment("/review\nReflection.", created="2026-11-03T00:00:00Z"),
            comment("/pause", created="2026-11-03T00:00:00Z"),
            comment("/done S1 2026-10-30", created="2026-10-27T00:00:00Z"),
        ]
        board = build_week([p], WEEK, AS_OF)
        self.assertEqual(board["recovery_count"], 0)
        self.assertEqual(board["leaderboard"][0]["total_points"], 1)

    def test_participant_time_zone_controls_date_boundary(self):
        now = datetime(2026, 10, 26, 2, tzinfo=timezone.utc)
        tokyo = plan(handle="tokyo", sessions=1, zone="Asia/Tokyo")
        la = plan(handle="la", number=2, sessions=1, zone="America/Los_Angeles")
        tokyo["comments_data"] = [comment("/done S1 2026-10-26", "tokyo", "2026-10-26T01:00:00Z")]
        la["comments_data"] = [comment("/done S1 2026-10-26", "la", "2026-10-26T01:00:00Z")]
        rows = {r["handle"]: r for r in build_week([tokyo, la], WEEK, now)["leaderboard"]}
        self.assertEqual(rows["tokyo"]["completed"], 1)
        self.assertEqual(rows["la"]["completed"], 0)

    def test_unapproved_wrong_week_or_future_experience_not_scored(self):
        wrong = contribution(number=102)
        wrong["body"] = wrong["body"].replace(WEEK, "2026-10-19")
        future = contribution(number=103)
        future["created_at"] = "2026-11-03T00:00:00Z"
        other_author = contribution(handle="bob", number=104)
        state = approved_state(wrong, other_author)
        approve_contribution(future, state, AS_OF + timedelta(days=2))
        row = build_week([
            plan(), contribution(approved=False), wrong, future, other_author,
        ], WEEK, AS_OF, ranking_state=state)["leaderboard"][0]
        self.assertEqual(row["contribution_points"], 0)

    def test_malformed_data_is_skipped_safely(self):
        invalid = [None, "not an issue", {}, {"labels": "weekly-plan"}]
        bad_cases = []
        for field, value in [
            ("Time zone", "Not/AZone"),
            ("Participation mode", "Unknown"),
            ("Public leaderboard", "Maybe"),
            ("Planned sessions", "S1 | Monday | First\nS1 | Tuesday | Duplicate"),
            ("Planned sessions", "S0 | Monday | Bad ID"),
            ("Planned sessions", "S1 | Someday | Bad day"),
        ]:
            p = plan()
            old = p["body"].split(f"### {field}\n\n", 1)[1].split("\n\n### ", 1)[0]
            p["body"] = p["body"].replace(f"### {field}\n\n{old}", f"### {field}\n\n{value}")
            bad_cases.append(p)
        malicious_url = plan()
        malicious_url["html_url"] = "javascript:alert(1)"
        bad_cases.append(malicious_url)
        bad_cases.append({**plan(), "number": True})
        bad_cases.append({**plan(), "created_at": "not-a-date"})
        board = build_week(invalid + bad_cases, WEEK, AS_OF)
        self.assertEqual(board["participants_count"], 0)
        self.assertEqual(board["leaderboard"], [])
        self.assertTrue(board["warnings"])

    def test_only_selected_week_and_actual_issues_count(self):
        other = plan(handle="other", number=2)
        other["body"] = other["body"].replace(WEEK, "2026-10-19")
        pr = {**plan(handle="pr", number=3), "pull_request": {"url": "https://example.com"}}
        board = build_week([plan(), other, pr], WEEK, AS_OF)
        self.assertEqual(board["participants_count"], 1)

    def test_same_scores_share_competition_rank_and_sort_deterministically(self):
        a = plan(handle="alpha", sessions=1)
        b = plan(handle="beta", number=2, sessions=1)
        c = plan(handle="charlie", number=3, sessions=1)
        a["comments_data"] = [comment("/done S1 2026-10-26", "alpha")]
        b["comments_data"] = [comment("/done S1 2026-10-26", "beta")]
        rows = build_week([c, b, a], WEEK, AS_OF)["leaderboard"]
        self.assertEqual([r["handle"] for r in rows], ["alpha", "beta", "charlie"])
        self.assertEqual([r["rank"] for r in rows], [1, 1, 3])

    def test_same_total_shares_rank_even_with_different_completion_rates(self):
        a = plan(handle="alpha", sessions=1)
        b = plan(handle="beta", number=2, sessions=3)
        a["comments_data"] = [comment("/review\nI need a smaller plan next week.", "alpha")]
        b["comments_data"] = [comment("/done S1 2026-10-26", "beta")]
        rows = build_week([a, b], WEEK, AS_OF)["leaderboard"]
        self.assertEqual([r["handle"] for r in rows], ["beta", "alpha"])
        self.assertEqual([r["total_points"] for r in rows], [3, 3])
        self.assertEqual([r["rank"] for r in rows], [1, 1])

    def test_as_of_must_be_aware_utc_and_week_must_be_monday(self):
        for invalid in [
            datetime(2026, 11, 2), None, "2026-11-02",
            datetime(2026, 11, 2, tzinfo=timezone(timedelta(hours=8))),
        ]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                build_week([], WEEK, invalid)
        for invalid in ["2026-10-27", "2026-02-30", "2026-1-1", None]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                build_week([], invalid, AS_OF)


if __name__ == "__main__":
    unittest.main()
