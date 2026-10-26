"""Regression tests for the self-reported work/exercise day score."""

from copy import deepcopy
from datetime import datetime, timezone
import json
import unittest

from club.daily_checkins import build_week, is_journal, public_handles, score_days


WEEK = "2026-10-26"
AS_OF = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)


def journal(handle="member-one", number=1, public="Yes", zone="UTC", **overrides):
    issue = {
        "number": number,
        "title": "[Check-in] My daily journal",
        "body": f"### Time zone\n\n{zone}\n\n### Public leaderboard\n\n{public}\n",
        "user": {"login": handle, "type": "User"},
        "state": "open",
        "labels": [],
        "created_at": "2026-10-24T12:00:00Z",
        "comments_data": [],
    }
    issue.update(overrides)
    return issue


def checkin(day="2026-10-26", work=1, exercise=1, handle="member-one", **overrides):
    comment = {
        "body": f"/checkin {day} W={work} E={exercise}",
        "user": {"login": handle, "type": "User"},
        "created_at": "2026-11-01T12:00:00Z",
    }
    comment.update(overrides)
    return comment


def records_for(work_days, exercise_days, handle="member-one", number=1):
    days = ["2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29",
            "2026-10-30", "2026-10-31", "2026-11-01"]
    return journal(handle=handle, number=number, comments_data=[
        checkin(day, int(index < work_days), int(index < exercise_days), handle)
        for index, day in enumerate(days)
    ])


class DailyScoreTests(unittest.TestCase):
    def test_formula_examples_and_independent_caps(self):
        for work, exercise, expected in [
            (0, 0, 0), (5, 0, 0), (0, 4, 0), (1, 1, 22.36),
            (5, 1, 50), (4, 3, 77.46), (5, 4, 100),
            (7, 4, 100), (5, 7, 100), (7, 7, 100), (7, 1, 50),
        ]:
            with self.subTest(work=work, exercise=exercise):
                self.assertEqual(score_days(work, exercise), expected)
                row = build_week([records_for(work, exercise)], WEEK, AS_OF)["leaderboard"][0]
                self.assertEqual(row["score"], expected)
                self.assertEqual(row["work_days"], work)
                self.assertEqual(row["exercise_days"], exercise)
                self.assertEqual(row["checkin_days"], 7)

    def test_score_rejects_negative_fractional_and_boolean_day_counts(self):
        for invalid in (-1, 1.5, True, None, "1"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    score_days(invalid, 1)
                with self.assertRaises(ValueError):
                    score_days(1, invalid)

    def test_empty_week_has_explicit_v3_metadata_and_no_fake_participants(self):
        result = build_week([journal()], WEEK, AS_OF)
        self.assertEqual(result, {
            "schema_version": 3, "scoring_version": 3,
            "week_start": WEEK, "week_end": "2026-11-01",
            "generated_at": "2026-11-02T12:00:00Z", "participants_count": 0,
            "leaderboard": [],
        })

    def test_rest_day_and_zero_component_are_visible_with_zero_score(self):
        for work, exercise in ((0, 0), (1, 0), (0, 1)):
            p = journal(comments_data=[checkin(work=work, exercise=exercise)])
            result = build_week([p], WEEK, AS_OF)
            self.assertEqual(result["participants_count"], 1)
            self.assertEqual(result["leaderboard"][0]["score"], 0)
            self.assertEqual(result["leaderboard"][0]["checkin_days"], 1)

    def test_latest_daily_state_replaces_both_flags_without_adding_credit(self):
        p = journal(comments_data=[
            checkin(work=1, exercise=0, created_at="2026-10-26T18:00:00Z", id=11),
            checkin(work=0, exercise=1, created_at="2026-10-26T19:00:00Z", id=12),
        ])
        result = build_week([p], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((result["work_days"], result["exercise_days"], result["score"]), (0, 1, 0))
        p["comments_data"].append(checkin(work=1, exercise=1, created_at="2026-10-26T20:00:00Z", id=13))
        result = build_week([p], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((result["work_days"], result["exercise_days"], result["checkin_days"]), (1, 1, 1))
        p["comments_data"].append(checkin(work=0, exercise=0, created_at="2026-10-26T21:00:00Z", id=14))
        result = build_week([p], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((result["work_days"], result["exercise_days"], result["score"]), (0, 0, 0))

    def test_edit_time_wins_and_comment_order_does_not_matter(self):
        earlier = checkin(work=0, exercise=0, id=11, created_at="2026-10-26T18:00:00Z",
                          updated_at="2026-10-26T21:00:00Z")
        later = checkin(work=1, exercise=1, id=12, created_at="2026-10-26T19:00:00Z")
        p = journal(comments_data=[earlier, later])
        expected = build_week([p], WEEK, AS_OF)
        self.assertEqual(expected["leaderboard"][0]["score"], 0)
        p["comments_data"].reverse()
        self.assertEqual(build_week([p], WEEK, AS_OF), expected)
        # A fresh API read with the corrected comment deleted sees the remaining state.
        p["comments_data"] = [later]
        self.assertEqual(build_week([p], WEEK, AS_OF)["leaderboard"][0]["score"], 22.36)

    def test_comment_id_resolves_same_second_states(self):
        a = checkin(work=1, exercise=1, id=5)
        b = checkin(work=0, exercise=0, id=6)
        first = build_week([journal(comments_data=[a, b])], WEEK, AS_OF)
        second = build_week([journal(comments_data=[b, a])], WEEK, AS_OF)
        self.assertEqual(first, second)
        self.assertEqual(first["leaderboard"][0]["score"], 0)

    def test_only_latest_valid_state_counts(self):
        p = journal(comments_data=[
            checkin(created_at="2026-10-26T18:00:00Z"),
            checkin(work=2, created_at="2026-10-26T19:00:00Z"),
        ])
        self.assertEqual(build_week([p], WEEK, AS_OF)["leaderboard"][0]["score"], 22.36)

    def test_command_requires_first_nonempty_line_and_one_command_per_comment(self):
        invalid = [
            "Here is an example:\n/checkin 2026-10-26 W=1 E=1",
            "> /checkin 2026-10-26 W=1 E=1",
            "```text\n/checkin 2026-10-26 W=1 E=1\n```",
            "/checkin 2026-10-26 W=1 E=1\n/checkin 2026-10-27 W=1 E=1",
            "/checkin 2026-10-26 W=1 E=1\n  /CHECKIN invalid",
            "/checkin 2026-10-26 W=1 E=1 extra",
            "/checkin 2026-10-26 W=2 E=1",
            "/checkin 2026-10-26 W=true E=false",
            "/checkin 2026-10-26 W=1",
            "/checkin 2026-10-26 E=1 W=1",
            "/done S1 2026-10-26",
            "/review\nA reflection.",
            None,
        ]
        for body in invalid:
            with self.subTest(body=body):
                self.assertEqual(build_week([journal(comments_data=[checkin(body=body)])], WEEK, AS_OF)["leaderboard"], [])
        p = journal(comments_data=[checkin(body="\r\n /CHECKIN 2026-10-26 w=1 e=1\r\n\r\nOptional notes and a mention of /checkin inline.")])
        self.assertEqual(build_week([p], WEEK, AS_OF)["leaderboard"][0]["score"], 22.36)

    def test_owner_identity_uses_ids_and_legacy_case_insensitive_login_fallback(self):
        p = journal(comments_data=[checkin(handle="MEMBER-ONE")])
        self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 1)
        p["user"]["id"] = 123
        p["comments_data"][0]["user"] = {"login": "renamed-member", "id": 123, "type": "User"}
        self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 1)
        p["comments_data"][0]["user"] = {"login": "member-one", "id": 999, "type": "User"}
        self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 0)
        for user in [{"login": "other-member"}, {"login": "member-one", "type": "Bot"},
                     {"login": "member-one[bot]"}, {"login": "member-one", "id": True}, None]:
            p["comments_data"] = [checkin(user=user)]
            self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 0)

    def test_invalid_dates_and_comments_outside_week_are_ignored(self):
        for day in ("2026-10-25", "2026-11-02", "2026-02-30", "2026-10-32", "2026-1-1"):
            p = journal(comments_data=[checkin(day=day)])
            self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 0)

    def test_future_and_impossible_comment_metadata_are_ignored(self):
        invalid = [
            {"created_at": "2026-11-03T00:00:00Z"},
            {"updated_at": "2026-11-03T00:00:00Z"},
            {"updated_at": "2026-10-31T00:00:00Z"},
            {"created_at": "2026-10-23T00:00:00Z"},
            {"created_at": "not-a-time"}, {"created_at": "2026-11-01T12:00:00"},
            {"updated_at": None}, {"id": True}, {"id": "123"}, {"id": -1},
        ]
        for overrides in invalid:
            with self.subTest(overrides=overrides):
                self.assertEqual(build_week([journal(comments_data=[checkin(**overrides)])], WEEK, AS_OF)["participants_count"], 0)

    def test_future_activity_is_not_unlocked_by_waiting_for_a_later_sync(self):
        p = journal(comments_data=[checkin(day="2026-10-27", created_at="2026-10-26T23:00:00Z")])
        self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 0)
        p["comments_data"][0]["updated_at"] = "2026-10-27T19:00:00Z"
        self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 1)

    def test_dates_use_member_time_zone_at_week_boundaries(self):
        instant = datetime(2026, 10, 25, 15, tzinfo=timezone.utc)
        p = journal(zone="Pacific/Kiritimati", comments_data=[checkin(created_at="2026-10-25T14:30:00Z")])
        self.assertEqual(build_week([p], WEEK, instant)["participants_count"], 1)
        p["body"] = p["body"].replace("Pacific/Kiritimati", "UTC")
        self.assertEqual(build_week([p], WEEK, instant)["participants_count"], 0)
        instant = datetime(2026, 10, 26, 0, 30, tzinfo=timezone.utc)
        p = journal(zone="America/Los_Angeles", comments_data=[
            checkin(created_at="2026-10-26T00:00:00Z"),
            checkin(day="2026-10-25", created_at="2026-10-26T00:00:00Z"),
        ])
        self.assertEqual(build_week([p], WEEK, instant)["participants_count"], 0)
        self.assertEqual(build_week([p], "2026-10-19", instant)["participants_count"], 1)

    def test_dst_repeated_hour_does_not_count_a_day_twice(self):
        p = journal(zone="America/New_York", comments_data=[
            checkin(day="2026-11-01", work=1, exercise=0, created_at="2026-11-01T05:30:00Z"),
            checkin(day="2026-11-01", work=1, exercise=1, created_at="2026-11-01T06:30:00Z"),
        ])
        row = build_week([p], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((row["checkin_days"], row["work_days"], row["exercise_days"]), (1, 1, 1))

    def test_latest_journal_supersedes_old_one_without_combining_days(self):
        older = records_for(5, 4)
        newer = journal(number=2, created_at="2026-10-25T12:00:00Z", comments_data=[checkin()])
        for records in ([older, newer], [newer, older]):
            row = build_week(records, WEEK, AS_OF)["leaderboard"][0]
            self.assertEqual((row["issue_number"], row["score"]), (2, 22.36))
        # Same creation timestamp uses the higher issue number.
        newer["created_at"] = older["created_at"]
        self.assertEqual(build_week([newer, older], WEEK, AS_OF)["leaderboard"][0]["issue_number"], 2)

    def test_closed_private_and_invalid_latest_journals_do_not_reactivate_old_one(self):
        older = records_for(5, 4)
        for overrides in ({"state": "closed"}, {"public": "No"}, {"zone": "Unknown/Zone"},
                          {"body": "Malformed current journal"}, {"public": "_No response_"}):
            newer = journal(number=2, created_at="2026-10-25T12:00:00Z", **overrides)
            with self.subTest(overrides=overrides):
                self.assertTrue(is_journal(newer))
                self.assertEqual(build_week([older, newer], WEEK, AS_OF)["leaderboard"], [])
                self.assertEqual(public_handles([older, newer]), set())

    def test_latest_journal_selection_handles_renames_and_mixed_legacy_ids(self):
        older = records_for(5, 4)
        older["user"]["id"] = 123
        newer = journal(handle="new-name", number=2, public="No", created_at="2026-10-25T12:00:00Z")
        newer["user"]["id"] = 123
        self.assertEqual(public_handles([older, newer]), set())
        newer["user"] = {"login": "MEMBER-ONE"}
        self.assertEqual(public_handles([older, newer]), set())

    def test_public_allowlist_does_not_require_current_week_activity(self):
        self.assertEqual(public_handles([journal(handle="Member-One")]), {"member-one"})
        self.assertEqual(build_week([journal()], WEEK, AS_OF)["leaderboard"], [])

    def test_public_optin_and_timezone_must_be_unambiguous(self):
        invalid_bodies = [
            "### Time zone\nUTC", "### Public leaderboard\nYes",
            "### Time zone\nUnknown/Zone\n### Public leaderboard\nYes",
            "### Time zone\nUTC\n### Public leaderboard\nYes\n### Public leaderboard\nNo",
            "### Time zone\nUTC\n### Public leaderboard\n_No response_",
            "### Time zone\nUTC\n### Public leaderboard\nYes because I want points",
            None,
        ]
        for body in invalid_bodies:
            p = journal(body=body, comments_data=[checkin()])
            self.assertEqual(public_handles([p]), set())
            self.assertEqual(build_week([p], WEEK, AS_OF)["leaderboard"], [])
        p = journal(public="No", comments_data=[checkin()])
        self.assertEqual(build_week([p], WEEK, AS_OF)["leaderboard"], [])
        p = journal(comments_data=[checkin()])
        p["body"] = p["body"].replace("\n", "\r\n")
        self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 1)

    def test_bots_prs_and_all_example_markers_are_excluded(self):
        variants = [
            {"user": {"login": "robot", "type": "Bot"}},
            {"user": {"login": "robot[bot]"}},
            {"pull_request": {}},
            {"labels": [{"name": "example"}]},
            {"title": "[Check-in] [Fictional example] A journal"},
            {"title": "[Check-in] [虚构演示｜打卡] A journal"},
            {"body": "<!-- club-example:daily -->"},
        ]
        for overrides in variants:
            p = journal(comments_data=[checkin()], **overrides)
            self.assertFalse(is_journal(p))
            self.assertEqual(public_handles([p]), set())
            self.assertEqual(build_week([p], WEEK, AS_OF)["leaderboard"], [])

    def test_unlabelled_form_and_explicit_journal_label_are_supported(self):
        p = journal(comments_data=[checkin()])
        self.assertTrue(is_journal(p))
        p["title"] = "My renamed journal"
        self.assertFalse(is_journal(p))
        p["labels"] = [{"name": "daily-checkin"}]
        self.assertTrue(is_journal(p))
        self.assertEqual(build_week([p], WEEK, AS_OF)["participants_count"], 1)

    def test_old_scoring_labels_never_add_points(self):
        p = journal(comments_data=[checkin()])
        p["labels"] = [{"name": "points-approved"}, {"name": "experience"}]
        self.assertEqual(build_week([p], WEEK, AS_OF)["leaderboard"][0]["score"], 22.36)
        old = journal(title="[Plan] Old weekly plan", labels=[{"name": "weekly-plan"}], comments_data=[checkin()])
        self.assertEqual(build_week([old], WEEK, AS_OF)["leaderboard"], [])

    def test_ties_have_competition_rank_and_stable_handle_order(self):
        records = [records_for(1, 1, "charlie", 3), records_for(5, 4, "Bravo", 2),
                   records_for(5, 4, "alice", 1), records_for(0, 0, "delta", 4)]
        board = build_week(records, WEEK, AS_OF)
        self.assertEqual([(row["handle"], row["rank"]) for row in board["leaderboard"]],
                         [("alice", 1), ("Bravo", 1), ("charlie", 3), ("delta", 4)])
        self.assertEqual(build_week(reversed(records), WEEK, AS_OF), board)

    def test_public_output_has_only_weekly_aggregates_and_constructed_urls(self):
        p = journal(comments_data=[checkin(body="/checkin 2026-10-26 W=1 E=1\nPRIVATE_NOTES")])
        p["html_url"] = "javascript:alert('untrusted')"
        p["body"] += "\n### Notes\nPRIVATE_DETAILS"
        original = deepcopy(p)
        board = build_week([p], WEEK, AS_OF, repository="example/club")
        self.assertEqual(p, original)
        row = board["leaderboard"][0]
        self.assertEqual(set(row), {"rank", "handle", "issue_number", "issue_url", "work_days",
                                    "exercise_days", "checkin_days", "score", "time_zone"})
        self.assertEqual(row["issue_url"], "https://github.com/example/club/issues/1")
        serialized = json.dumps(board)
        for private in ("PRIVATE_NOTES", "PRIVATE_DETAILS", "javascript:", "comments_data", "body"):
            self.assertNotIn(private, serialized)

    def test_malformed_records_do_not_crash_or_create_public_rows(self):
        records = [None, [], "bad", {}, journal(number=True), journal(number=-1),
                   journal(created_at="bad"), journal(user={"login": "bad/name"}),
                   journal(comments_data=[None, "bad", {}, checkin(user=None)]),
                   journal(comments_data="bad"), journal(state=None)]
        self.assertEqual(build_week(records, WEEK, AS_OF)["leaderboard"], [])

    def test_future_journal_cannot_appear(self):
        p = journal(created_at="2026-11-03T00:00:00Z", comments_data=[checkin()])
        self.assertEqual(build_week([p], WEEK, AS_OF)["leaderboard"], [])

    def test_invalid_calculation_arguments_fail_without_guessing(self):
        for week in ("2026-10-27", "2026-02-30", "2026-1-1", None):
            with self.assertRaises(ValueError):
                build_week([], week, AS_OF)
        for instant in (datetime(2026, 11, 2), "2026-11-02T00:00:00Z", None):
            with self.assertRaises(ValueError):
                build_week([], WEEK, instant)
        for repo in ("https://github.com/example/club", "example/club/extra", "example/club?x=1", None):
            with self.assertRaises(ValueError):
                build_week([], WEEK, AS_OF, repository=repo)


if __name__ == "__main__":
    unittest.main()
