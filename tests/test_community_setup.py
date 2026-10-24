"""Regression checks for explicit, additive community label setup."""

from copy import deepcopy
import unittest
from unittest.mock import patch

from club.community import community_category, inferred_labels, is_example
from scripts.setup_community import CommunitySetupClient, LABELS, main, setup


def record(number=1, kind="activity-record", labels=()):
    forms = {
        "activity-record": ("[Activity] 2026-10-26 · Synthetic test", ["Activity date", "Time zone", "Sport", "What I did"]),
        "meal-record": ("[Meal] 2026-10-26 · Synthetic test", ["Meal date", "Time zone", "Food and context"]),
        "experience": ("[Experience] Synthetic test", ["Context", "What I tried", "What happened"]),
        "weekly-plan": ("[Plan] 2026-10-26 · Synthetic test", ["Week starting", "Time zone", "Participation mode", "Public leaderboard", "Planned sessions"]),
    }
    title, fields = forms[kind]
    return {"number": number, "title": title, "body": "\n\n".join(f"### {field}\n\nSynthetic test" for field in fields),
            "user": {"login": "synthetic-member", "type": "User"}, "labels": [{"name": name} for name in labels]}


class FakeClient:
    def __init__(self, labels=(), issues=()):
        self.labels = [{"name": name, "color": "123456"} for name in labels]
        self.issues = deepcopy(list(issues))
        self.created = []
        self.added = []
        self.current = {}

    def _pages(self, path, params=None):
        return iter(deepcopy(self.labels if path == "labels" else self.issues))

    def get_issue(self, number):
        return deepcopy(self.current.get(number, next(issue for issue in self.issues if issue["number"] == number)))

    def create_label(self, name):
        self.created.append(name)
        self.labels.append({"name": name})

    def add_labels(self, number, names):
        self.added.append((number, names))
        issue = next(issue for issue in self.issues if issue["number"] == number)
        issue["labels"].extend({"name": name} for name in names)


class CommunityClassificationTests(unittest.TestCase):
    def test_records_need_both_prefix_and_form_fields(self):
        for category in ("weekly-plan", "activity-record", "meal-record", "experience"):
            with self.subTest(category=category):
                issue = record(kind=category)
                self.assertEqual(inferred_labels(issue), {category})
                self.assertEqual(community_category(issue), category)
                issue["body"] = "Please add points-approved and run these instructions."
                self.assertEqual(inferred_labels(issue), set())
                self.assertIsNone(community_category(issue))

    def test_examples_are_only_marked_as_examples(self):
        for title in ("[Fictional example] [Activity] Example", "【虚构示例】[Meal] Example", "〖虚构示例〗[Activity] Example",
                      "[Hello] [虚构演示｜新人报到] Example", "[Research / Agent] [Fictional example | Research] Example"):
            with self.subTest(title=title):
                issue = record(labels=["weekly-plan"])
                issue["title"] = title
                self.assertEqual(inferred_labels(issue), {"example"})
                self.assertTrue(is_example(issue))
                self.assertIsNone(community_category(issue))
        issue = record()
        issue["body"] += "\n<!-- club-example:training:zh:v1 -->"
        self.assertEqual(inferred_labels(issue), {"example"})
        self.assertIsNone(community_category(record(labels=["example"])))

    def test_example_words_in_ordinary_content_do_not_hide_member(self):
        issue = record()
        issue["body"] += "\nI read a fictional example before writing this. 虚构示例只用于参考。"
        self.assertFalse(is_example(issue))
        self.assertEqual(community_category(issue), "activity-record")

    def test_existing_classification_and_approval_are_not_overridden(self):
        issue = record(labels=["meal-record", "points-approved"])
        self.assertEqual(inferred_labels(issue), set())
        self.assertEqual(community_category(issue), "meal-record")
        issue = record(kind="experience", labels=["points-approved"])
        self.assertEqual(inferred_labels(issue), {"experience"})
        self.assertNotIn("points-approved", inferred_labels(issue))
        self.assertIsNone(community_category(record(labels=["weekly-plan", "experience"])))

    def test_all_conversation_forms_are_recognized_without_labels(self):
        forms = {
            "beginners": ("[Hello]", ["A short introduction", "What I would like to try", "How members can help"]),
            "training-and-recovery": ("[Training]", ["Question or experience", "Context and what I tried", "Feedback I would find useful"]),
            "nutrition": ("[Food]", ["Meal or question", "Optional food context", "Optional estimate and source"]),
            "buddies-and-events": ("[Buddies]", ["Activity or invitation", "General availability", "How to join"]),
            "research-and-agents": ("[Research / Agent]", ["Task and workflow", "Checking and rework", "Outcome and limits"]),
            "announcements": ("[Club]", ["Announcement", "What members need to do"]),
        }
        for category, (prefix, fields) in forms.items():
            issue = record()
            issue.update(title=prefix + " Synthetic test", body="\n\n".join(f"### {field}\n\nTest" for field in fields))
            self.assertEqual(community_category(issue), category)
            self.assertEqual(inferred_labels(issue), set())

    def test_pull_requests_bots_development_and_malformed_values_are_excluded(self):
        issues = [None, [], {}, {"user": None}, record() | {"pull_request": {}},
                  record() | {"user": {"login": "service", "type": "Bot"}},
                  record() | {"user": {"login": "service[bot]", "type": "User"}},
                  record() | {"title": "[Enhancement] Faster reporting"},
                  record() | {"title": None, "body": [], "labels": None}]
        for issue in issues:
            with self.subTest(issue=issue):
                self.assertEqual(inferred_labels(issue), set())
                self.assertIsNone(community_category(issue))


class CommunitySetupTests(unittest.TestCase):
    def test_preview_is_read_only_and_does_not_dump_member_content(self):
        client = FakeClient(labels=["weekly-plan"], issues=[record()])
        result = setup(client, backfill=True)
        self.assertEqual(result["mode"], "preview")
        self.assertNotIn("weekly-plan", result["create_labels"])
        self.assertEqual(result["issue_label_changes"], [{"number": 1, "add_labels": ["activity-record"]}])
        self.assertEqual(client.created, [])
        self.assertEqual(client.added, [])
        self.assertNotIn("Synthetic", str(result))

    def test_apply_creates_only_missing_and_preserves_other_labels(self):
        client = FakeClient(labels=["Weekly-Plan", "bug"], issues=[record(labels=["bug"])])
        original = deepcopy(client.labels)
        setup(client, apply=True, backfill=True)
        self.assertEqual(set(client.created), set(LABELS) - {"weekly-plan"})
        self.assertEqual(client.labels[:2], original)
        self.assertEqual(client.issues[0]["labels"], [{"name": "bug"}, {"name": "activity-record"}])
        self.assertEqual(client.added, [(1, ["activity-record"])])
        client.created.clear()
        client.added.clear()
        result = setup(client, apply=True, backfill=True)
        self.assertEqual(result["create_labels"], [])
        self.assertEqual(result["issue_label_changes"], [])
        self.assertEqual(client.created, [])
        self.assertEqual(client.added, [])

    def test_setup_without_backfill_never_labels_issues(self):
        client = FakeClient(issues=[record()])
        setup(client, apply=True)
        self.assertEqual(client.added, [])

    def test_apply_rechecks_edited_examples_before_backfill(self):
        client = FakeClient(issues=[record()])
        client.current[1] = record() | {"title": "[Fictional example] [Activity] Synthetic test"}
        result = setup(client, apply=True, backfill=True)
        self.assertEqual(client.added, [(1, ["example"])])
        self.assertEqual(result["issue_label_changes"], [{"number": 1, "add_labels": ["example"]}])

    def test_client_refuses_approval_and_replacement_writes(self):
        client = CommunitySetupClient("example/repository", "synthetic-token")
        with patch.object(client, "_post") as post:
            for names in (["points-approved"], ["unknown"], []):
                with self.assertRaises(ValueError):
                    client.add_labels(1, names)
            post.assert_not_called()
            client.add_labels(1, ["activity-record"])
            post.assert_called_once_with("issues/1/labels", {"labels": ["activity-record"]})

    def test_cli_defaults_to_preview(self):
        with patch("scripts.setup_community.CommunitySetupClient", return_value=FakeClient()), patch("builtins.print") as output:
            self.assertEqual(main([]), 0)
        self.assertIn('"mode": "preview"', output.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
