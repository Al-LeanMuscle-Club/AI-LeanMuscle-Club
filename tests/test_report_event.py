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
    def test_unrelated_community_events_are_ignored(self):
        self.assertFalse(should_refresh("issues", issue([])))
        self.assertFalse(should_refresh("issue_comment", issue(["meal-record"])))
        self.assertFalse(should_refresh("issue_comment", issue(["experience"])))

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
