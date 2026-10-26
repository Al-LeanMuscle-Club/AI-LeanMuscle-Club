"""The fictional renderer must never repopulate the newcomer homepage."""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import re
from shutil import copyfile
from tempfile import TemporaryDirectory
import unittest

from scripts.render_demo_board import FIXTURE, SOURCE_ROOT, generated_files, main


class StandaloneDemoTests(unittest.TestCase):
    def test_generate_and_check_only_example_artifacts_preserve_homepages(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "examples").mkdir()
            copyfile(SOURCE_ROOT / FIXTURE, root / FIXTURE)
            homes = {
                "README.md": "# 社区\n<!-- README:COMMUNITY-FIRST -->\n## News\n真实文章\n<!-- CLUB:START -->\n真实概况\n<!-- CLUB:END -->\n",
                "README.en.md": "# Community\n## News\nA real story\n",
                "README.zh-CN.md": "[首页](README.md)\n",
            }
            for name, text in homes.items():
                (root / name).write_text(text)
            outputs = generated_files(root)
            self.assertEqual(set(outputs), {
                Path("examples/demo-training-records.md"), Path("examples/demo-leaderboard.json"),
                Path("examples/demo-board.md"), Path("examples/demo-board.en.md"),
            })
            with redirect_stdout(StringIO()):
                self.assertEqual(main(["--root", str(root)]), 0)
                self.assertEqual(main(["--root", str(root), "--check"]), 0)
            for name, text in homes.items():
                self.assertEqual((root / name).read_text(), text)
            for name in ("demo-board.md", "demo-board.en.md"):
                page = root / "examples" / name
                text = page.read_text()
                self.assertNotIn("<!-- DEMO:", text)
                self.assertIn("demo-aurora", text)
                for link in re.findall(r"\]\(([^)]+)\)", text):
                    self.assertTrue((page.parent / link.split("#")[0]).is_file(), link)
            payload = json.loads((root / "examples/demo-leaderboard.json").read_text())
            self.assertIs(payload["synthetic"], True)
            self.assertEqual(len(payload["board"]["leaderboard"]), 6)
            self.assertEqual(payload["board"]["recovery_count"], 1)

    def test_rendering_requires_no_readme_or_live_report_files(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "examples").mkdir()
            copyfile(SOURCE_ROOT / FIXTURE, root / FIXTURE)
            outputs = generated_files(root)
            self.assertTrue(all(path.parts[0] == "examples" for path in outputs))
            self.assertFalse((root / "reports").exists())
            self.assertFalse((root / "data").exists())


if __name__ == "__main__":
    unittest.main()
