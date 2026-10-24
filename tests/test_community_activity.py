"""Community activity is anonymous, factual and separate from score eligibility."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import unittest

from scripts.community_activity import build_community_activity, public_community_activity

WEEK = "2026-10-26"
AS_OF = datetime(2026, 11, 3, 12, tzinfo=timezone.utc)


def post(number=1, category="activity-record", author="member-one", created="2026-10-26T09:00:00Z"):
    return {
        "number": number, "user": {"id": 100 + number, "login": author, "type": "User"},
        "title": "Member record", "body": "PRIVATE_NOTES", "created_at": created,
        "labels": [{"name": category}], "comments_data": [],
    }


def reply(identifier=1, author="member-two", created="2026-10-27T09:00:00Z"):
    return {"id": identifier, "user": {"id": 200, "login": author, "type": "User"},
            "created_at": created, "body": "PRIVATE_REPLY"}


class CommunityActivityTests(unittest.TestCase):
    def test_genuine_categories_and_distinct_people_are_counted_without_copying_data(self):
        records = [post(), post(2, "meal-record"), post(3, "experience")]
        records[1]["user"] = records[0]["user"]
        records[2]["comments_data"] = [reply()]
        summary = build_community_activity(records, WEEK, AS_OF)
        self.assertEqual(summary["participants_count"], 3)
        self.assertEqual(summary["posts_count"], 3)
        self.assertEqual(summary["replies_count"], 1)
        self.assertEqual(summary["responded_posts_count"], 1)
        self.assertEqual([summary[key] for key in ("activity_records", "meal_records", "experiences")], [1, 1, 1])
        self.assertEqual(summary["weekly_plan_posts"], 0)
        text = json.dumps(summary)
        for private in ("PRIVATE_NOTES", "PRIVATE_REPLY", "member-one", "member-two", "title", "user"):
            self.assertNotIn(private, text)

    def test_examples_bots_pull_requests_and_technical_threads_never_count(self):
        examples = [post(i) for i in range(1, 6)]
        examples[0]["title"] = "[Fictional example] [Activity] Walk"
        examples[1]["body"] += "\n<!-- club-example:activity:en:v1 -->"
        examples[2]["user"]["type"] = "Bot"
        examples[3]["pull_request"] = {}
        examples[4]["labels"] = [{"name": "example"}, {"name": "activity-record"}]
        technical = post(6)
        technical.update(title="[Enhancement] Make the helper easier", labels=[])
        for item in examples + [technical]:
            item["comments_data"] = [reply()]
        summary = build_community_activity(examples + [technical], WEEK, AS_OF)
        self.assertEqual(summary["posts_count"], 0)
        self.assertEqual(summary["participants_count"], 0)
        self.assertEqual(summary["replies_count"], 0)

    def test_utc_creation_time_and_later_replies_do_not_rewrite_activity_dates(self):
        old = post(created="2026-10-26T00:30:00+08:00")  # Sunday in UTC.
        old["comments_data"] = [reply(created="2026-10-26T00:30:00Z")]
        next_week = post(2, created="2026-11-02T00:00:00Z")
        future = post(3, created="2026-11-04T00:00:00Z")
        summary = build_community_activity([old, next_week, future], WEEK, AS_OF)
        self.assertEqual(summary["posts_count"], 0)
        self.assertEqual(summary["replies_count"], 1)
        self.assertEqual(summary["participants_count"], 1)
        self.assertEqual(summary["responded_posts_count"], 0)

    def test_response_requires_another_human_and_can_arrive_after_the_post_week(self):
        item = post()
        own = reply()
        own["user"] = item["user"]
        bot = reply(2)
        bot["user"] = {"login": "github-actions[bot]", "type": "Bot"}
        item["comments_data"] = [own, bot]
        first = build_community_activity([item], WEEK, AS_OF)
        self.assertEqual(first["responded_posts_count"], 0)
        self.assertEqual(first["replies_count"], 1)
        item["comments_data"].append(reply(3, created="2026-11-02T01:00:00Z"))
        later = build_community_activity([item], WEEK, AS_OF)
        self.assertEqual(later["responded_posts_count"], 1)
        self.assertEqual(later["replies_count"], 1)

    def test_deleted_or_reclassified_threads_and_replies_disappear(self):
        item = post()
        item["comments_data"] = [reply()]
        self.assertEqual(build_community_activity([item], WEEK, AS_OF)["participants_count"], 2)
        item["comments_data"] = []
        self.assertEqual(build_community_activity([item], WEEK, AS_OF)["participants_count"], 1)
        item["labels"] = []
        self.assertEqual(build_community_activity([item], WEEK, AS_OF)["participants_count"], 0)
        self.assertEqual(build_community_activity([], WEEK, AS_OF)["posts_count"], 0)

    def test_duplicate_ids_and_renamed_authors_do_not_inflate_people_or_responses(self):
        item = post()
        own = reply()
        own["user"] = {**item["user"], "login": "renamed-member"}
        item["comments_data"] = [own, deepcopy(own)]
        summary = build_community_activity([item, deepcopy(item)], WEEK, AS_OF)
        self.assertEqual(summary["posts_count"], 1)
        self.assertEqual(summary["replies_count"], 1)
        self.assertEqual(summary["participants_count"], 1)
        self.assertEqual(summary["responded_posts_count"], 0)

    def test_unlabelled_known_form_is_counted_without_changing_score_labels(self):
        item = post()
        item.update(labels=[], title="[Activity] A real walk", body=(
            "### Activity date\n\n2026-10-20\n\n### Time zone\n\nAsia/Shanghai\n\n"
            "### Sport\n\nwalking\n\n### What I did\n\nPRIVATE_NOTES"
        ))
        summary = build_community_activity([item], WEEK, AS_OF)
        self.assertEqual(summary["activity_records"], 1)
        self.assertEqual(item["labels"], [])

    def test_missing_malformed_and_future_data_does_not_create_participants(self):
        variants = [None, {}, post(), post(2), post(3), post(4)]
        variants[2]["created_at"] = "2026-10-26"  # Unzoned timestamp.
        variants[3]["user"]["login"] = "malformed/name"
        variants[4]["created_at"] = "2026-11-04T00:00:00Z"
        variants[5]["user"] = None
        self.assertEqual(build_community_activity(variants, WEEK, AS_OF)["participants_count"], 0)

    def test_public_snapshot_is_complete_and_allowlisted(self):
        summary = build_community_activity([post()], WEEK, AS_OF)
        summary["body"] = "DO_NOT_COPY"
        self.assertNotIn("body", public_community_activity(summary))
        self.assertIsNone(public_community_activity(None))
        self.assertIsNone(public_community_activity({"schema_version": 1}))
        summary["participants_count"] = True
        self.assertIsNone(public_community_activity(summary))


if __name__ == "__main__":
    unittest.main()
