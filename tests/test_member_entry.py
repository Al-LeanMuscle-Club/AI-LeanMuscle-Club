import unittest

from scripts.member_entry import helper_url, update_entry


class MemberEntryTests(unittest.TestCase):
    def test_deployment_urls_and_custom_domains(self):
        self.assertEqual(helper_url("https://club.github.io/project/"), "https://club.github.io/project/tools/")
        self.assertEqual(helper_url("https://members.example.org"), "https://members.example.org/tools/")

    def test_reject_unsafe_or_non_site_urls(self):
        for url in ("", "http://example.org", "javascript:alert(1)", "https://a:b@example.org/",
                    "https://example.org/?q=a", "https://example.org/#anchor", "https://example.org/\ntext",
                    "https://example.org/<tag>", "https://example.org/\\path"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                helper_url(url)

    def test_updates_only_reference_and_is_idempotent(self):
        original = "正文\n[打开工具][member-helper]\n\n[member-helper]: docs/setup.md\n<!-- CLUB:START -->\n保留报告\n"
        url = helper_url("https://club.github.io/project/")
        updated = update_entry(original, url)
        self.assertEqual(updated, original.replace("docs/setup.md", url))
        self.assertEqual(update_entry(updated, url), updated)

    def test_missing_or_duplicate_reference_fails(self):
        for text in ("no reference", "[member-helper]: a\n[member-helper]: b\n"):
            with self.assertRaises(ValueError):
                update_entry(text, "https://club.github.io/tools/")


if __name__ == "__main__":
    unittest.main()
