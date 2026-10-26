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


def imported_activity(day=WEEK, **overrides):
    issue = journal(**{"created_at": "2026-10-26T12:00:00Z", **overrides})
    issue["body"] += (
        f"\n### Activity date\n\n{day}\n\n### Activity details\n\nSYNTHETIC_PRIVATE_NOTE\n"
        f"\n### Imported exercise date\n\n{day}\n\n### Migration notes\n\n"
        "<!-- club-import:activity-v1 -->\n\nImport of the explicit exercise date only.\n")
    return issue


def imported_work_activity(work_dates=None, exercise_date="2026-10-28", **overrides):
    if work_dates is None:
        work_dates = ["2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30"]
    issue = imported_activity(exercise_date, **{"created_at": "2026-10-31T12:00:00Z", **overrides})
    issue["body"] = issue["body"].replace(
        "### Migration notes", "### Imported work dates\n\n" + "\n".join(work_dates) + "\n\n### Migration notes")
    issue["body"] = issue["body"].replace(
        "<!-- club-import:activity-v1 -->", "<!-- club-import:activity-v1 -->\n<!-- club-import:work-v1 -->")
    return issue


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


class ImportedActivityTests(unittest.TestCase):
    def test_marked_activity_without_comments_adds_exercise_but_no_work_credit(self):
        issue = imported_activity()
        del issue["comments_data"]
        original = deepcopy(issue)
        result = build_week([issue], WEEK, AS_OF, repository="example/club")
        self.assertEqual(issue, original)
        self.assertEqual(result["participants_count"], 1)
        row = result["leaderboard"][0]
        self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"], row["score"]),
                         (0, 1, 1, 0))
        self.assertEqual(row["issue_url"], "https://github.com/example/club/issues/1")
        for private in ("SYNTHETIC_PRIVATE_NOTE", "Activity date", "Imported exercise date", "Migration notes", "body"):
            self.assertNotIn(private, json.dumps(result))

    def test_import_requires_exact_standalone_marker_in_migration_notes_and_matching_dates(self):
        body = imported_activity()["body"]
        marker = "<!-- club-import:activity-v1 -->"
        invalid = [
            body.replace(marker, ""),
            body.replace(marker, "<!-- club-import:activity-v2 -->"),
            body.replace(marker, "Example: " + marker),
            body.replace("### Migration notes", "### Other notes"),
            body.replace("### Activity date", "### Some date"),
            body.replace("### Imported exercise date", "### Some imported date"),
            body.replace("### Imported exercise date\n\n2026-10-26", "### Imported exercise date\n\n2026-10-25"),
            body.replace("### Imported exercise date\n\n2026-10-26", "### Imported exercise date\n\n2026-10-26 extra"),
            body + "\n### Imported exercise date\n\n2026-10-26\n",
            body + "\n### Activity date\n\n2026-10-26\n",
        ]
        for value in invalid:
            with self.subTest(body=value):
                issue = imported_activity()
                issue["body"] = value
                self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"], [])
        issue = imported_activity()
        issue["body"] = issue["body"].replace("\n", "\r\n")
        self.assertEqual(build_week([issue], WEEK, AS_OF)["participants_count"], 1)

    def test_invalid_out_of_week_and_future_activity_dates_never_import(self):
        for day in ("2026-02-30", "2026-1-1", "2026-10-25", "2026-11-02", "2026-10-27"):
            with self.subTest(day=day):
                # October 27 is within the week, but is later than the original
                # Issue's October 26 creation day even after the sync advances.
                self.assertEqual(build_week([imported_activity(day)], WEEK, AS_OF)["leaderboard"], [])
        future = imported_activity("2026-11-03", created_at="2026-11-03T12:00:00Z")
        self.assertEqual(build_week([future], "2026-11-02", AS_OF)["leaderboard"], [])
        before_creation = datetime(2026, 10, 26, 11, tzinfo=timezone.utc)
        self.assertEqual(build_week([imported_activity()], WEEK, before_creation)["leaderboard"], [])

    def test_creation_day_and_cutoff_use_the_members_local_calendar(self):
        instant = datetime(2026, 10, 25, 12, tzinfo=timezone.utc)
        issue = imported_activity(zone="Pacific/Kiritimati", created_at="2026-10-25T10:30:00Z")
        self.assertEqual(build_week([issue], WEEK, instant)["participants_count"], 1)
        issue["body"] = issue["body"].replace("Pacific/Kiritimati", "UTC")
        self.assertEqual(build_week([issue], WEEK, instant)["leaderboard"], [])
        issue = imported_activity(zone="America/Los_Angeles", created_at="2026-10-26T00:30:00Z")
        self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"], [])
        issue = imported_activity("2026-10-25", zone="America/Los_Angeles", created_at="2026-10-26T00:30:00Z")
        instant = datetime(2026, 10, 26, 1, tzinfo=timezone.utc)
        self.assertEqual(build_week([issue], "2026-10-19", instant)["participants_count"], 1)

    def test_owner_comment_replaces_both_imported_flags_and_never_duplicates_the_date(self):
        for work, exercise in ((0, 0), (1, 0), (1, 1)):
            with self.subTest(work=work, exercise=exercise):
                issue = imported_activity(comments_data=[
                    checkin(work=0, exercise=1, id=1, created_at="2026-10-26T18:00:00Z"),
                    checkin(work=work, exercise=exercise, id=2, created_at="2026-10-26T19:00:00Z"),
                ])
                row = build_week([issue], WEEK, AS_OF)["leaderboard"][0]
                self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"]),
                                 (work, exercise, 1))
                self.assertEqual(row["score"], score_days(work, exercise))

    def test_other_days_combine_with_import_and_repeated_input_cannot_add_credit(self):
        issue = imported_activity(comments_data=[checkin(day="2026-10-27")])
        issue["comments_data"].append(deepcopy(issue["comments_data"][0]))
        row = build_week([issue, deepcopy(issue)], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"], row["score"]),
                         (1, 2, 2, 31.62))

    def test_stranger_bot_and_invalid_comments_cannot_override_or_extend_import(self):
        comments = [checkin(work=1, exercise=0, handle="other-member"),
                    checkin(day="2026-10-27", handle="other-member"),
                    checkin(user={"login": "member-one", "type": "Bot"}),
                    checkin(body="/checkin 2026-10-26 W=2 E=0"),
                    checkin(created_at="2026-10-26T11:00:00Z"),
                    checkin(updated_at="2026-11-03T00:00:00Z")]
        row = build_week([imported_activity(comments_data=comments)], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"]), (0, 1, 1))

    def test_imports_keep_optout_closed_timezone_example_and_bot_exclusions(self):
        variants = [{"public": "No"}, {"state": "closed"}, {"zone": "Unknown/Zone"},
                    {"labels": [{"name": "example"}]}, {"pull_request": {}},
                    {"title": "[Check-in] [Fictional example] Activity import"},
                    {"title": "[Check-in] [虚构演示｜打卡] Activity import"},
                    {"title": "[Activity] Unmigrated activity"},
                    {"user": {"login": "robot", "type": "Bot"}},
                    {"user": {"login": "robot[bot]"}}]
        for overrides in variants:
            with self.subTest(overrides=overrides):
                self.assertEqual(build_week([imported_activity(**overrides)], WEEK, AS_OF)["leaderboard"], [])
        issue = imported_activity()
        issue["body"] += "\n<!-- club-example:daily -->\n"
        self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"], [])

    def test_latest_canonical_journal_supersedes_import_without_reactivating_it(self):
        older = imported_activity()
        for overrides in ({}, {"public": "No"}, {"state": "closed"}, {"zone": "Unknown/Zone"}):
            newer = journal(number=2, created_at="2026-10-27T12:00:00Z", **overrides)
            for records in ([older, newer], [newer, older]):
                with self.subTest(overrides=overrides):
                    self.assertEqual(build_week(records, WEEK, AS_OF)["leaderboard"], [])
        newer = journal(number=2, created_at="2026-10-27T12:00:00Z", comments_data=[checkin("2026-10-28")])
        row = build_week([older, newer], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((row["issue_number"], row["exercise_days"], row["checkin_days"]), (2, 1, 1))


class ImportedWorkTests(unittest.TestCase):
    def test_five_work_dates_and_one_exercise_score_fifty_without_duplicate_days(self):
        for exercise_day, counted_days in (("2026-10-28", 5), ("2026-10-31", 6)):
            with self.subTest(exercise_day=exercise_day):
                issue = imported_work_activity(exercise_date=exercise_day)
                row = build_week([issue], WEEK, AS_OF)["leaderboard"][0]
                self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"], row["score"]),
                                 (5, 1, counted_days, 50))

    def test_work_marker_and_field_are_both_required_without_inference(self):
        body = imported_work_activity()["body"]
        marker = "<!-- club-import:work-v1 -->"
        invalid = [body.replace(marker, ""),
                   body.replace(marker, "<!-- club-import:work-v2 -->"),
                   body.replace(marker, "Example: " + marker),
                   body.replace("### Imported work dates", "### Work dates in prose"),
                   body.replace(marker, "") + "\n### Other notes\n\n" + marker]
        for value in invalid:
            with self.subTest(body=value):
                issue = imported_work_activity()
                issue["body"] = value
                row = build_week([issue], WEEK, AS_OF)["leaderboard"][0]
                self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"]), (0, 1, 1))
        issue = imported_activity("2026-10-28", created_at="2026-10-31T12:00:00Z")
        issue["body"] += "\nWorked Monday through Friday.\n"
        self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"][0]["work_days"], 0)

    def test_work_import_requires_a_valid_original_activity_import_in_the_same_week(self):
        body = imported_work_activity()["body"]
        invalid = [body.replace("<!-- club-import:activity-v1 -->", ""),
                   body.replace("### Activity date", "### Unverified date"),
                   body.replace("### Imported exercise date\n\n2026-10-28", "### Imported exercise date\n\n2026-10-29")]
        for value in invalid:
            issue = imported_work_activity()
            issue["body"] = value
            self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"], [])
        self.assertEqual(build_week([imported_work_activity()], "2026-11-02", AS_OF)["leaderboard"], [])

    def test_only_explicit_nonempty_work_date_lines_count(self):
        issue = imported_work_activity(["2026-10-27", "", "  2026-10-31  ", " "])
        issue["body"] = issue["body"].replace("\n", "\r\n")
        row = build_week([issue], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"], row["score"]), (2, 1, 3, 31.62))

    def test_bad_duplicate_cross_week_or_future_value_rejects_all_work_but_keeps_exercise(self):
        invalid = [[], ["2026-10-26", "not-a-date"], ["2026-02-30"], ["2026-1-1"],
                   ["2026-10-26", "2026-10-26"], ["2026-10-26", "2026-10-26T12:00:00Z"],
                   ["2026-10-26", "2026-10-25"], ["2026-10-26", "2026-11-02"],
                   ["2026-10-26", "2026-11-01"], ["- 2026-10-26"],
                   ["2026-10-26, 2026-10-27"], ["2026-10-26"] * 8]
        for dates in invalid:
            with self.subTest(dates=dates):
                row = build_week([imported_work_activity(dates)], WEEK, AS_OF)["leaderboard"][0]
                self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"], row["score"]),
                                 (0, 1, 1, 0))
        # All seven explicit dates are accepted when the source was created on
        # Sunday; the weekly formula still caps work credit at five days.
        dates = ["2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29",
                 "2026-10-30", "2026-10-31", "2026-11-01"]
        row = build_week([imported_work_activity(dates, created_at="2026-11-01T10:00:00Z")], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((row["work_days"], row["checkin_days"], row["score"]), (7, 7, 50))

    def test_work_date_boundaries_use_local_creation_day_and_cutoff(self):
        instant = datetime(2026, 10, 26, 13, tzinfo=timezone.utc)
        issue = imported_work_activity(["2026-10-27"], exercise_date=WEEK,
                                       zone="Pacific/Kiritimati", created_at="2026-10-26T12:00:00Z")
        self.assertEqual(build_week([issue], WEEK, instant)["leaderboard"][0]["work_days"], 1)
        issue["body"] = issue["body"].replace("Pacific/Kiritimati", "UTC")
        row = build_week([issue], WEEK, instant)["leaderboard"][0]
        self.assertEqual((row["work_days"], row["exercise_days"]), (0, 1))
        issue = imported_work_activity(["2026-10-27"], exercise_date=WEEK,
                                       zone="America/Los_Angeles", created_at="2026-10-27T00:30:00Z")
        self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"][0]["work_days"], 0)
        issue["body"] = issue["body"].replace("America/Los_Angeles", "UTC")
        self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"][0]["work_days"], 1)
        before_creation = datetime(2026, 10, 27, 0, tzinfo=timezone.utc)
        self.assertEqual(build_week([issue], WEEK, before_creation)["leaderboard"], [])

    def test_owner_comments_override_both_imported_flags_and_deduplicate_dates(self):
        for day, work, exercise, expected in [
            ("2026-10-26", 0, 0, (4, 1, 5)), ("2026-10-28", 0, 0, (4, 0, 5)),
            ("2026-10-28", 1, 0, (5, 0, 5)), ("2026-10-26", 0, 1, (4, 2, 5)),
        ]:
            with self.subTest(day=day, work=work, exercise=exercise):
                comment = checkin(day, work, exercise)
                issue = imported_work_activity(comments_data=[comment, deepcopy(comment)])
                row = build_week([issue, deepcopy(issue)], WEEK, AS_OF)["leaderboard"][0]
                self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"]), expected)

    def test_stranger_bot_and_invalid_comments_do_not_change_imported_work(self):
        comments = [checkin("2026-10-26", 0, 0, handle="other-member"),
                    checkin("2026-10-31", handle="other-member"),
                    checkin(work=0, user={"login": "member-one", "type": "Bot"}),
                    checkin(body="/checkin 2026-10-26 W=2 E=0"),
                    checkin(work=0, updated_at="2026-11-03T00:00:00Z")]
        row = build_week([imported_work_activity(comments_data=comments)], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual((row["work_days"], row["exercise_days"], row["checkin_days"]), (5, 1, 5))

    def test_work_import_keeps_withdrawal_and_canonical_journal_rules(self):
        for overrides in ({"public": "No"}, {"state": "closed"}, {"zone": "Unknown/Zone"},
                          {"labels": [{"name": "example"}]}, {"user": {"login": "robot", "type": "Bot"}}):
            with self.subTest(overrides=overrides):
                self.assertEqual(build_week([imported_work_activity(**overrides)], WEEK, AS_OF)["leaderboard"], [])
        newer = journal(number=2, created_at="2026-11-01T10:00:00Z", public="No")
        self.assertEqual(build_week([imported_work_activity(), newer], WEEK, AS_OF)["leaderboard"], [])

    def test_work_import_public_output_contains_only_aggregates_and_keeps_input_unchanged(self):
        issue = imported_work_activity()
        original = deepcopy(issue)
        board = build_week([issue], WEEK, AS_OF)
        self.assertEqual(issue, original)
        serialized = json.dumps(board)
        for private in ("SYNTHETIC_PRIVATE_NOTE", "Imported work dates", "club-import:work-v1", "2026-10-27", "body"):
            self.assertNotIn(private, serialized)


if __name__ == "__main__":
    unittest.main()
