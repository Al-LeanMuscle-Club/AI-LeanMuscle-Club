"""Mixed-sport records, honest alternatives, corrections, and safe validation."""

from copy import deepcopy
from datetime import datetime, timezone
import json
import unittest

from club.scoring import build_week, validate_submission
from tests.test_scoring import AS_OF, WEEK, comment, plan


def mixed_plan(handle="alice", public="Yes"):
    issue = plan(handle=handle, public=public)
    original = "\n".join(f"S{i} | Monday | Session {i}" for i in range(1, 4))
    issue["body"] = issue["body"].replace(original, "\n".join([
        "S1 | Monday | strength | Private workout details | Short home session",
        "S2 | Wednesday | basketball | Private practice details",
        "S3 | Saturday | running | Private route details",
    ]))
    issue["body"] += "\n\n### Primary goal\n\nmuscle-gain\n\n### Research week\n\ndeadline"
    return issue


class MixedRecordTests(unittest.TestCase):
    def test_each_session_has_its_own_sport_and_summary_has_optin_scope(self):
        issue = mixed_plan()
        issue["comments_data"] = [
            comment("/fallback S1 2026-10-26"),
            comment("/partial S2 2026-10-28"),
            comment("/skip S3 2026-10-31"),
            comment("/review\nA deadline changed my schedule."),
        ]
        board = build_week([issue], WEEK, AS_OF)
        row = board["leaderboard"][0]
        self.assertEqual(board["schema_version"], 2)
        self.assertEqual(row["goal"], "muscle-gain")
        self.assertEqual(row["research_week"], "deadline")
        self.assertEqual(row["sports"], ["basketball", "running", "strength"])
        self.assertEqual([s["status"] for s in row["sessions"]], ["fallback", "partial", "skipped"])
        self.assertEqual(row["sessions"][0]["used_fallback"], True)
        self.assertEqual(row["completed"], 1)
        self.assertEqual(row["total_points"], 6)
        self.assertEqual(row["execution_rate"], 0.5)
        self.assertEqual(board["summary"], {
            "public_members": 1, "planned_sessions": 3, "completed_sessions": 1,
            "partial_sessions": 1, "skipped_sessions": 1, "reviewed_members": 1,
        })
        self.assertEqual({s["sport"]: (s["planned"], s["completed"]) for s in board["sports"]}, {
            "strength": (1, 1), "basketball": (1, 0), "running": (1, 0),
        })
        self.assertNotIn("Private", json.dumps(board))
        self.assertNotIn("Short home session", json.dumps(board))

    def test_legacy_plan_is_still_valid_without_category_fields(self):
        issue = plan(sessions=1)
        self.assertEqual(validate_submission(issue, now=AS_OF), [])
        row = build_week([issue], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual(row["goal"], "habit")
        self.assertEqual(row["research_week"], "regular")
        self.assertEqual(row["sessions"], [{
            "id": "S1", "day": "Monday", "sport": "other", "status": "planned",
            "date": None, "used_fallback": False, "confirmed": True,
        }])

    def test_optional_blank_form_fields_use_defaults(self):
        issue = plan(sessions=1)
        issue["body"] += "\n\n### Primary goal\n\n_No response_\n\n### Research week\n\n"
        self.assertEqual(validate_submission(issue, now=AS_OF), [])
        self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"][0]["goal"], "habit")

    def test_fallback_requires_its_own_predeclared_alternative(self):
        issue = mixed_plan()
        self.assertEqual(validate_submission(issue, "/fallback S1 2026-10-26", now=AS_OF), [])
        self.assertTrue(validate_submission(issue, "/fallback S2 2026-10-28", now=AS_OF))
        # A general Busy-week fallback does not declare an alternative for every session.
        legacy = plan(sessions=1)
        legacy["comments_data"] = [comment("/fallback S1 2026-10-26")]
        self.assertEqual(build_week([legacy], WEEK, AS_OF)["leaderboard"][0]["completed"], 0)
        self.assertTrue(validate_submission(legacy, "/fallback S1 2026-10-26", now=AS_OF))

    def test_done_and_fallback_do_not_stack_and_latest_status_can_correct_done(self):
        issue = mixed_plan()
        issue["comments_data"] = [
            {**comment("/fallback S1 2026-10-26"), "id": 1},
            {**comment("/done S1 2026-10-26"), "id": 2},
        ]
        row = build_week([issue], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual(row["completed"], 1)
        self.assertEqual(row["sessions"][0]["status"], "completed")
        issue["comments_data"].append({**comment("/partial S1 2026-10-26"), "id": 3})
        row = build_week([issue], WEEK, AS_OF)["leaderboard"][0]
        self.assertEqual(row["completed"], 0)
        self.assertEqual(row["partial"], 1)

    def test_edit_timestamp_and_comment_id_make_corrections_deterministic(self):
        issue = mixed_plan()
        edited = {
            **comment("/partial S1 2026-10-26", created="2026-10-27T10:00:00Z"),
            "updated_at": "2026-11-01T14:00:00Z", "id": 5,
        }
        newer_original = {**comment("/done S1 2026-10-26"), "id": 10}
        for records in ([edited, newer_original], [newer_original, edited]):
            issue["comments_data"] = records
            self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"][0]["partial"], 1)
        same_time = {**comment("/skip S1 2026-10-26"), "id": 11}
        for records in ([newer_original, same_time], [same_time, newer_original]):
            issue["comments_data"] = records
            self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"][0]["skipped"], 1)

    def test_future_or_invalid_edit_cannot_replace_a_valid_state(self):
        issue = mixed_plan()
        issue["comments_data"] = [
            {**comment("/done S1 2026-10-26"), "id": 1},
            {**comment("/skip S1 2026-10-26"), "id": 2, "updated_at": "2026-11-03T12:00:00Z"},
            {**comment("/partial S1 2026-10-26"), "id": 3, "updated_at": "not-a-date"},
        ]
        self.assertEqual(build_week([issue], WEEK, AS_OF)["leaderboard"][0]["completed"], 1)

    def test_all_new_commands_respect_actual_week_date_and_author(self):
        issue = mixed_plan()
        for command in ("fallback S1", "partial S2", "skip S3", "meal"):
            for day in ("2026-10-25", "2026-11-02", "2026-02-30"):
                with self.subTest(command=command, day=day):
                    self.assertTrue(validate_submission(issue, f"/{command} {day}", now=AS_OF))
            self.assertTrue(validate_submission(issue, comment(f"/{command} 2026-10-26", author="someone-else"), now=AS_OF))
        # UTC Monday is still Sunday in the participant's local zone.
        local = deepcopy(issue)
        local["body"] = local["body"].replace("### Time zone\n\nUTC", "### Time zone\n\nAmerica/Los_Angeles")
        moment = datetime(2026, 10, 26, 2, tzinfo=timezone.utc)
        self.assertTrue(validate_submission(local, "/partial S1 2026-10-26", now=moment))

    def test_mixed_commands_reject_whole_comment_including_meal_and_partial(self):
        issue = mixed_plan()
        for body in (
            "/done S1 2026-10-26\n/meal 2026-10-26 | Lunch",
            "/meal 2026-10-26\n/partial S1 2026-10-26",
            "/review\nReflected.\n/fallback S1 2026-10-26",
            "/skip S1 2026-10-26\n/PAUSE",
        ):
            with self.subTest(body=body):
                self.assertTrue(validate_submission(issue, body, now=AS_OF))
                issue["comments_data"] = [comment(body)]
                board = build_week([issue], WEEK, AS_OF)
                self.assertEqual(board["leaderboard"][0]["total_points"], 1)
                self.assertEqual(board["recovery_count"], 0)

    def test_meals_and_training_notes_are_never_republished_or_scored(self):
        issue = mixed_plan()
        body = "/meal 2026-10-26 | PRIVATE_MEAL_DETAILS\nCalories: 632\nSource: packaging"
        self.assertEqual(validate_submission(issue, body, now=AS_OF), [])
        issue["comments_data"] = [comment(body)]
        board = build_week([issue], WEEK, AS_OF)
        self.assertEqual(board["leaderboard"][0]["total_points"], 1)
        self.assertEqual(board["leaderboard"][0]["meal_days"], 1)
        for text in ("PRIVATE_MEAL_DETAILS", "632", "packaging", "Calories"):
            self.assertNotIn(text, json.dumps(board))

    def test_optouts_and_paused_members_do_not_enter_category_counts(self):
        hidden = mixed_plan(handle="hidden-person", public="No")
        hidden["body"] = hidden["body"].replace("muscle-gain", "fat-loss")
        active = plan(handle="visible-person", number=2, sessions=1)
        board = build_week([hidden, active], WEEK, AS_OF)
        self.assertEqual(board["participants_count"], 2)
        self.assertEqual(board["summary"]["public_members"], 1)
        self.assertEqual(board["sports"], [{"sport": "other", "planned": 1, "completed": 0}])
        self.assertNotIn("hidden-person", json.dumps(board))
        self.assertNotIn("fat-loss", json.dumps(board))
        hidden["body"] = hidden["body"].replace("### Public leaderboard\n\nNo", "### Public leaderboard\n\nYes")
        hidden["comments_data"] = [comment("/pause", author="hidden-person")]
        self.assertEqual(build_week([hidden], WEEK, AS_OF)["sports"], [])

    def test_invalid_categories_have_fixed_feedback_without_echoing_input(self):
        for original, replacement in (
            ("muscle-gain", "PRIVATE_INVALID_GOAL"),
            ("deadline", "PRIVATE_INVALID_CONTEXT"),
            ("| strength |", "| PRIVATE_INVALID_SPORT |"),
        ):
            issue = mixed_plan()
            issue["body"] = issue["body"].replace(original, replacement)
            errors = validate_submission(issue, now=AS_OF)
            self.assertTrue(errors)
            self.assertNotIn("PRIVATE_INVALID", str(errors))
            self.assertEqual(build_week([issue], WEEK, AS_OF)["participants_count"], 0)

    def test_preflight_works_without_leaderboard_optin_and_checks_unknown_session(self):
        issue = mixed_plan(public="No")
        self.assertEqual(validate_submission(issue, "/done S1 2026-10-26\nWeight: optional", now=AS_OF), [])
        self.assertTrue(validate_submission(issue, "/done S99 2026-10-26", now=AS_OF))
        self.assertTrue(validate_submission(issue, "/review", now=AS_OF))
        self.assertTrue(validate_submission(issue, "/unknown PRIVATE_BODY", now=AS_OF))
        self.assertEqual(validate_submission(issue, "/review\nAn honest incomplete week.", now=AS_OF), [])

    def test_recovery_allows_meal_and_reflection_without_score(self):
        issue = plan(mode="Recovery", sessions=0)
        self.assertEqual(validate_submission(issue, "/meal 2026-10-26 | Optional meal", now=AS_OF), [])
        self.assertEqual(validate_submission(issue, "/review\nResting this week.", now=AS_OF), [])
        self.assertTrue(validate_submission(issue, "/done S1 2026-10-26", now=AS_OF))
        board = build_week([issue], WEEK, AS_OF)
        self.assertEqual(board["leaderboard"], [])
        self.assertEqual(board["summary"]["public_members"], 0)


if __name__ == "__main__":
    unittest.main()
