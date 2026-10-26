from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.member_entry import helper_url, main, update_entry


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

    def test_main_updates_both_full_homepages_and_leaves_compatibility_page_untouched(self):
        originals = {
            "README.md": "# Club\n[Helper][member-helper]\n\n[member-helper]: docs/SETUP.md\n"
                         "<!-- CLUB:START -->English board<!-- CLUB:END -->\n",
            "README.zh-CN.md": "# 俱乐部\n[辅助页][member-helper]\n\n[member-helper]: docs/PAGES_QUICKSTART.zh-CN.md\n"
                               "<!-- CLUB:START -->中文榜单<!-- CLUB:END -->\n",
            "README.en.md": "# Navigation\n[English home](README.md)\n",
        }
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name, text in originals.items():
                (root / name).write_text(text, encoding="utf-8")
            with patch.dict("os.environ", {"MEMBER_PAGE_URL": "https://members.example.org/club/"}), \
                    patch("sys.argv", ["member_entry.py", "--root", str(root)]):
                self.assertEqual(main(), 0)
            url = "https://members.example.org/club/tools/"
            for name, previous in (("README.md", "docs/SETUP.md"),
                                   ("README.zh-CN.md", "docs/PAGES_QUICKSTART.zh-CN.md")):
                self.assertEqual((root / name).read_text(encoding="utf-8"),
                                 originals[name].replace(previous, url))
            self.assertEqual((root / "README.en.md").read_text(encoding="utf-8"), originals["README.en.md"])

    def test_main_validates_both_homepages_before_writing_either(self):
        for bad_name in ("README.md", "README.zh-CN.md"):
            for invalid in (None, "No helper definition\n", "[member-helper]: a\n[member-helper]: b\n"):
                with self.subTest(file=bad_name, content=invalid), TemporaryDirectory() as directory:
                    root = Path(directory)
                    for name in ("README.md", "README.zh-CN.md"):
                        (root / name).write_text("Keep this board.\n[member-helper]: docs/setup.md\n", encoding="utf-8")
                    if invalid is None:
                        (root / bad_name).unlink()
                    else:
                        (root / bad_name).write_text(invalid, encoding="utf-8")
                    before = {path.name: path.read_bytes() for path in root.iterdir()}
                    error = FileNotFoundError if invalid is None else ValueError
                    with patch.dict("os.environ", {"MEMBER_PAGE_URL": "https://members.example.org/"}), \
                            patch("sys.argv", ["member_entry.py", "--root", str(root)]), \
                            self.assertRaises(error):
                        main()
                    self.assertEqual({path.name: path.read_bytes() for path in root.iterdir()}, before)


if __name__ == "__main__":
    unittest.main()
