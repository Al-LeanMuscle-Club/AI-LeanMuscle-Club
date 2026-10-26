"""Report-change event filter regression checks."""
import unittest
from scripts.report_event import should_refresh


def issue(labels, action="edited", changed=None):
    return {
        "action": action,
        "issue": {"number": 12, "labels": [{"name": name} for name in labels]},
        "label": {"name": changed} if changed else {},
    }


class ReportEventTests(unittest.TestCase):
    def test_simple_chat_and_replies_refresh_without_labels(self):
        event = issue([])
        event["issue"].update(user={"login": "member"}, title="[Chat] 一起聊聊",
                              body="### 我想说的话\n\nSynthetic question.")
        self.assertTrue(should_refresh("issues", event))
        self.assertTrue(should_refresh("issue_comment", event))
        event["issue"]["title"] = "[Chat] [Fictional example] Example"
        self.assertFalse(should_refresh("issue_comment", event))

    def test_unrelated_community_events_are_ignored(self):
        self.assertFalse(should_refresh("issues", issue([])))
        self.assertFalse(should_refresh("issue_comment", issue(["bug"])))

    def test_genuine_community_posts_and_replies_refresh_without_scoring(self):
        for category in ("activity-record", "meal-record", "experience"):
            event = issue([category])
            event["issue"]["user"] = {"login": "member", "type": "User"}
            self.assertTrue(should_refresh("issues", event))
            self.assertTrue(should_refresh("issue_comment", event))
        form = issue([])
        form["issue"].update(user={"login": "member"}, title="[Activity] Walk", body=(
            "### Activity date\n\n2026-10-26\n### Time zone\n\nUTC\n"
            "### Sport\n\nwalking\n### What I did\n\nA walk."
        ))
        self.assertTrue(should_refresh("issues", form))
        self.assertTrue(should_refresh("issue_comment", form))
        form["changes"] = {"title": {"from": form["issue"]["title"]}}
        form["issue"]["title"] = "An unrelated topic"
        self.assertTrue(should_refresh("issues", form))
        form.pop("changes")
        self.assertFalse(should_refresh("issues", form))

    def test_examples_and_bot_replies_do_not_create_genuine_conversations(self):
        event = issue(["example", "activity-record"])
        event["issue"]["user"] = {"login": "member"}
        self.assertFalse(should_refresh("issue_comment", event))
        # Changing the example flag must still remove earlier real counts.
        self.assertTrue(should_refresh("issues", event))
        self.assertTrue(should_refresh("issues", issue([], action="unlabeled", changed="example")))

    def test_scored_plans_and_contributions_run(self):
        self.assertTrue(should_refresh("issues", issue(["weekly-plan"])))
        self.assertTrue(should_refresh("issue_comment", issue(["weekly-plan"])))
        self.assertTrue(should_refresh("issues", issue(["experience", "points-approved"])))
        self.assertTrue(should_refresh("issues", issue([], action="unlabeled", changed="weekly-plan")))
        self.assertTrue(should_refresh("issues", issue([], action="unlabeled", changed="points-approved")))

    def test_deletion_and_reconciliation_remain_conservative(self):
        self.assertTrue(should_refresh("issues", issue([], action="deleted")))
        self.assertTrue(should_refresh("schedule", {}))
        self.assertTrue(should_refresh("workflow_dispatch", {}))
        self.assertFalse(should_refresh("issues", {"issue": {"pull_request": {}, "labels": []}}))


if __name__ == "__main__":
    unittest.main()
