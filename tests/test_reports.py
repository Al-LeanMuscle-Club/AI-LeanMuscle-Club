"""Integration tests for public report generation and its live API boundary."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from github_api import GitHubReader, validate_repository
from sync_github import replace_readme, reporting_weeks, write_reports
from club.scoring import build_week

AS_OF = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)


def plan(number=1, handle="member-one", public="Yes"):
    return {
        "number": number, "user": {"login": handle},
        "labels": [{"name": "weekly-plan"}],
        "html_url": f"https://github.com/example/club/issues/{number}",
        "created_at": "2026-10-25T10:00:00Z",
        "body": "\n\n".join([
            "### Week starting\n\n2026-10-26",
            "### Time zone\n\nAsia/Shanghai",
            "### Participation mode\n\nActive",
            f"### Public leaderboard\n\n{public}",
            "### Planned sessions\n\nS1 | Monday | Walk\nS2 | Wednesday | Strength\nS3 | Friday | Basketball",
            "### Busy-week fallback\n\nOne short session",
            "### Notes\n\nPRIVATE_DETAIL_NOT_FOR_REPORTS",
        ]),
        "comments_data": [
            {"user": {"login": handle}, "created_at": "2026-10-26T12:00:00Z", "body": "/done S1 2026-10-26 | Felt good."},
            {"user": {"login": handle}, "created_at": "2026-10-28T12:00:00Z", "body": "/done S2 2026-10-28 | Kept it short."},
            {"user": {"login": handle}, "created_at": "2026-11-01T12:00:00Z", "body": "/review\nTwo sessions fit this week. Try again next week."},
        ],
    }


class ReportingTests(unittest.TestCase):
    def test_identical_results_do_not_change_report_or_readme_timestamps(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "<!-- CLUB:START -->\n<!-- CLUB:END -->\n", encoding="utf-8"
            )
            records = [plan()]
            before = build_week(records, "2026-10-26", AS_OF)
            write_reports(root, [before])
            old_readme = (root / "README.md").read_bytes()
            old_report = (root / "reports/2026-10-26.json").read_bytes()
            old_index = (root / "reports/index.json").read_bytes()
            unchanged = build_week(records, "2026-10-26", AS_OF + timedelta(hours=3))
            write_reports(root, [unchanged])
            self.assertEqual(old_readme, (root / "README.md").read_bytes())
            self.assertEqual(old_report, (root / "reports/2026-10-26.json").read_bytes())
            self.assertEqual(old_index, (root / "reports/index.json").read_bytes())
            changed = deepcopy(unchanged)
            changed["participants_count"] += 1
            write_reports(root, [changed])
            self.assertNotEqual(old_report, (root / "reports/2026-10-26.json").read_bytes())


    def test_china_monday_rollover_and_year_boundary(self):
        instant = datetime(2026, 10, 25, 16, tzinfo=timezone.utc)
        self.assertEqual(reporting_weeks(instant), ["2026-10-26", "2026-10-19"])
        instant = datetime(2027, 1, 1, 0, tzinfo=timezone.utc)
        self.assertEqual(reporting_weeks(instant), ["2026-12-28", "2026-12-21"])
        with self.assertRaises(ValueError):
            reporting_weeks(instant, "2026-10-27")

    def test_reports_preserve_prose_and_do_not_publish_optouts_or_raw_notes(self):
        records = [plan(), plan(2, "private-member", "No")]
        board = build_week(records, "2026-10-26", AS_OF)
        self.assertEqual(board["participants_count"], 2)
        self.assertEqual(board["leaderboard"][0]["total_points"], 7)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("Important intro\n<!-- CLUB:START -->\nold board\n<!-- CLUB:END -->\nImportant footer\n", encoding="utf-8")
            write_reports(root, [board])
            text = (root / "README.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("Important intro\n"))
            self.assertTrue(text.endswith("Important footer\n"))
            public_text = "\n".join(p.read_text(encoding="utf-8") for p in root.rglob("*.md"))
            public_text += (root / "reports/2026-10-26.json").read_text(encoding="utf-8")
            self.assertIn("member-one", public_text)
            self.assertNotIn("private-member", public_text)
            self.assertNotIn("PRIVATE_DETAIL_NOT_FOR_REPORTS", public_text)
            self.assertNotIn("Felt good", public_text)

    def test_chinese_readme_marker_localizes_counts_rules_links_and_warnings(self):
        recovery = plan(3, "recovery-member")
        recovery["body"] = recovery["body"].replace("### Participation mode\n\nActive", "### Participation mode\n\nRecovery")
        invalid = plan(5, "invalid-member")
        invalid["body"] = invalid["body"].replace("Asia/Shanghai", "Invalid/Zone")
        board = build_week([plan(), plan(2, "private-member", "No"), recovery,
                            plan(4), invalid], "2026-10-26", AS_OF)
        saved = deepcopy(board)
        text = replace_readme("<!-- README:LANG=zh-CN -->\n<!-- CLUB:START -->\nold\n<!-- CLUB:END -->\n", [board])
        self.assertIn("### 周次：2026-10-26 起", text)
        self.assertIn("参与人数：**3** · 恢复/暂停人数：**1**", text)
        self.assertIn("公开参与人数：**1** · 已记录完成：**2/3** · 周复盘：**1**", text)
        self.assertIn("计分规则：v2", text)
        self.assertIn("部分完成计 0.5 次", text)
        self.assertIn("[完整周报](reports/2026-10-26.md)", text)
        self.assertIn("[公开数据](reports/2026-10-26.json)", text)
        self.assertIn("[查找计划与打卡助手](tools/index.html)", text)
        self.assertIn("更新时间：2026-11-02T12:00:00Z", text)
        self.assertIn("发现重复周计划，仅统计最早的有效计划。", text)
        self.assertIn("有周计划因必填字段无效而被跳过。", text)
        self.assertNotIn("Some records need attention", text)
        self.assertNotIn("private-member", text)
        self.assertEqual(board, saved)

    def test_chinese_readme_preserves_unknown_and_legacy_rules_without_current_formula(self):
        original = build_week([plan()], "2026-10-26", AS_OF)
        for version in (None, 1, 3, True, "2"):
            with self.subTest(version=version):
                board = deepcopy(original)
                if version is None:
                    board.pop("scoring_version")
                else:
                    board["scoring_version"] = version
                saved = deepcopy(board)
                text = replace_readme("<!-- README:LANG=zh-CN -->\n<!-- CLUB:START --><!-- CLUB:END -->", [board])
                if type(version) is int:
                    self.assertIn(f"计分规则：v{version}", text)
                    self.assertIn("保留该快照所记录规则下的分数", text)
                else:
                    self.assertIn("计分规则：未记录", text)
                    self.assertIn("不将当前公式追溯用于旧记录", text)
                self.assertNotIn("0.5", text)
                self.assertNotIn("已确认计划固定计分分母", text)
                self.assertEqual(board, saved)

    def test_live_report_write_preserves_prose_demo_english_readme_and_navigation_stub(self):
        record = plan()
        board = build_week([record], "2026-10-26", AS_OF)
        prefix = "<!-- README:LANG=zh-CN -->\n# 中文首页\n\n正文保留：中文、English 与 `code`。\n\n"
        suffix = ("\n\n正文尾部保持原样。\n<!-- DEMO:START -->\n"
                  "### 虚构示例 / Fictional demo\n\n| 成员 | 分数 |\n| --- | ---: |\n| Demo | 7.5 |\n"
                  "<!-- DEMO:END -->\n")
        english = b"# English home\n\n[Live overview](README.md)\n<!-- DEMO:START -->\nFictional demo\n<!-- DEMO:END -->\n"
        stub = "# 导航\n\n[中文主页](README.md) · [English](README.en.md)\n".encode("utf-8")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(prefix + "<!-- CLUB:START -->\nold\n<!-- CLUB:END -->" + suffix, encoding="utf-8")
            (root / "README.en.md").write_bytes(english)
            (root / "README.zh-CN.md").write_bytes(stub)
            write_reports(root, [board], source_records=[record], as_of=AS_OF)
            changed = (root / "README.md").read_text(encoding="utf-8")
            self.assertEqual(changed.split("<!-- CLUB:START -->", 1)[0], prefix)
            self.assertEqual(changed.split("<!-- CLUB:END -->", 1)[1], suffix)
            self.assertEqual(changed.count("<!-- CLUB:START -->"), 1)
            self.assertEqual(changed.count("<!-- CLUB:END -->"), 1)
            self.assertIn("公开参与人数：**1**", changed)
            self.assertEqual((root / "README.en.md").read_bytes(), english)
            self.assertEqual((root / "README.zh-CN.md").read_bytes(), stub)
            weekly = (root / "reports/2026-10-26.md").read_text(encoding="utf-8")
            self.assertIn("### Week starting 2026-10-26", weekly)
            self.assertIn("Scoring rules: v2", weekly)
            self.assertNotIn("计分规则", weekly)
            self.assertEqual(json.loads((root / "reports/2026-10-26.json").read_text()), board)

    def test_readme_without_explicit_language_marker_keeps_english_overview(self):
        board = build_week([], "2026-10-26", AS_OF)
        text = replace_readme("# 中文介绍也不自动改变语言\n<!-- CLUB:START --><!-- CLUB:END -->", [board])
        self.assertIn("### Week starting 2026-10-26", text)
        self.assertIn("Scoring rules: v2", text)
        self.assertNotIn("计分规则", text)

    def test_rule_versions_preserve_legacy_scores_during_historical_count_refresh(self):
        visible = plan()
        hidden = plan(2, "private-member", "No")
        old = build_week([visible, hidden], "2026-10-26", AS_OF)
        old.pop("scoring_version")  # Both earlier rule sets shipped unversioned reports.
        for row in old["leaderboard"]:
            for field in ("confirmed_planned", "current_planned", "recorded_training_days", "meal_days"):
                row.pop(field)
        old_score = old["leaderboard"][0]["total_points"]
        current = build_week([], "2026-11-02", AS_OF)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("<!-- CLUB:START -->\n<!-- CLUB:END -->\n")
            write_reports(root, [old])
            write_reports(root, [current], source_records=[visible], as_of=AS_OF)

            archived = json.loads((root / "reports/2026-10-26.json").read_text())
            self.assertEqual(archived["participants_count"], 1)
            self.assertEqual(archived["leaderboard"][0]["total_points"], old_score)
            self.assertNotIn("scoring_version", archived)
            old_markdown = (root / "reports/2026-10-26.md").read_text()
            self.assertIn("Scoring rules: not recorded", old_markdown)
            self.assertNotIn("partial = 0.5", old_markdown)
            self.assertIn("| — | — | — / — |", old_markdown)
            self.assertIn("Scoring rules: v2", (root / "reports/2026-11-02.md").read_text())
            self.assertIn("Scoring rules: v2", (root / "README.md").read_text())

            index = json.loads((root / "reports/index.json").read_text())
            weeks = {week["week_start"]: week for week in index["weeks"]}
            self.assertNotIn("scoring_version", weeks["2026-10-26"])
            self.assertEqual(weeks["2026-11-02"]["scoring_version"], 2)

    def test_unknown_rule_version_keeps_its_label_without_claiming_current_formula(self):
        board = build_week([plan()], "2026-10-26", AS_OF)
        board["scoring_version"] = 3
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("<!-- CLUB:START -->\n<!-- CLUB:END -->\n")
            write_reports(root, [board])
            markdown = (root / "reports/2026-10-26.md").read_text()
            self.assertIn("Scoring rules: v3", markdown)
            self.assertNotIn("partial = 0.5", markdown)
            self.assertEqual(json.loads((root / "reports/index.json").read_text())["weeks"][0]["scoring_version"], 3)

    def test_invalid_readme_cannot_silently_replace_content_or_write_reports(self):
        board = build_week([], "2026-10-26", AS_OF)
        for text in ("No markers", "<!-- CLUB:END --><!-- CLUB:START -->", "<!-- CLUB:START --><!-- CLUB:START --><!-- CLUB:END -->"):
            with self.assertRaises(ValueError):
                replace_readme(text, [board])
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("Keep this", encoding="utf-8")
            with self.assertRaises(ValueError):
                write_reports(root, [board])
            self.assertFalse((root / "reports").exists())
            self.assertEqual((root / "README.md").read_text(), "Keep this")

    def test_complete_offline_cli_without_network_or_credentials(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Test\n<!-- CLUB:START -->\n<!-- CLUB:END -->\n", encoding="utf-8")
            fixture = root / "synthetic.json"
            fixture.write_text(json.dumps([plan()]), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/sync_github.py"),
                "--fixture", str(fixture), "--week", "2026-10-26",
                "--as-of", AS_OF.isoformat(), "--root", str(root),
            ], capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((root / "reports/2026-10-26.json").read_text())
            self.assertEqual(data["leaderboard"][0]["total_points"], 7)
            self.assertNotIn("member-one", (root / "README.md").read_text())
            self.assertIn("member-one", (root / "reports/2026-10-26.md").read_text())
            self.assertEqual(json.loads((root / "reports/index.json").read_text())["schema_version"], 2)

    def test_homepage_stays_short_and_browser_index_excludes_unapproved_fields(self):
        records = [plan(number=i, handle=f"member-{i}") for i in range(1, 251)]
        board = build_week(records, "2026-10-26", AS_OF)
        board["leaderboard"][0]["food_notes"] = "DO_NOT_REPUBLISH"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Club\n<!-- CLUB:START -->\n<!-- CLUB:END -->\n")
            write_reports(root, [board])
            home = (root / "README.md").read_text()
            self.assertLess(len(home), 2000)
            self.assertIn("250", home)
            self.assertNotIn("member-1", home)
            index = (root / "reports/index.json").read_text()
            self.assertNotIn("DO_NOT_REPUBLISH", index)
            self.assertEqual(len(json.loads(index)["weeks"][0]["leaderboard"]), 250)

    def test_browser_index_window_keeps_older_reports_available(self):
        from datetime import timedelta, date
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Club\n<!-- CLUB:START -->\n<!-- CLUB:END -->\n")
            for offset in range(14):
                week = (date(2026, 10, 26) - timedelta(weeks=offset)).isoformat()
                write_reports(root, [build_week([], week, AS_OF)])
            data = json.loads((root / "reports/index.json").read_text())
            self.assertEqual(len(data["weeks"]), 12)
            self.assertEqual(len(data["available_weeks"]), 14)
            self.assertTrue((root / "reports" / (data["available_weeks"][-1] + ".md")).exists())
            self.assertIn(data["available_weeks"][-1], (root / "reports/README.md").read_text())

    def test_historical_withdrawal_removes_names_from_report_and_new_index(self):
        for reason in ("consent", "label", "deleted"):
            with self.subTest(reason=reason), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "README.md").write_text("# Club\n<!-- CLUB:START -->\n<!-- CLUB:END -->\n")
                original = plan()
                write_reports(root, [build_week([original], "2026-10-26", AS_OF)])
                if reason == "consent":
                    original["body"] = original["body"].replace("### Public leaderboard\n\nYes", "### Public leaderboard\n\nNo")
                elif reason == "label":
                    original["labels"] = []
                records = [] if reason == "deleted" else [original]
                write_reports(root, [build_week([], "2026-11-02", AS_OF)], source_records=records, as_of=AS_OF)
                self.assertNotIn("member-one", (root / "reports/index.json").read_text())
                self.assertNotIn("member-one", (root / "reports/2026-10-26.md").read_text())
                self.assertEqual(json.loads((root / "reports/2026-10-26.json").read_text())["leaderboard"], [])


class ApiBoundaryTests(unittest.TestCase):
    def test_pagination_collects_all_records_and_comments_only_for_target_week(self):
        calls = []
        first_page = [dict(plan(i + 1, f"member-{i+1}"), comments_data=[]) for i in range(100)]
        # Only two plans are in the target week; old history needs no comment fetch.
        for issue in first_page[2:]:
            issue["body"] = issue["body"].replace("2026-10-26", "2026-10-19")

        def fake_get(self, path, params=None):
            calls.append((path, dict(params or {})))
            if path == "issues":
                if params["labels"] == "experience,points-approved":
                    return []
                return first_page if params["page"] == 1 else []
            return []

        with patch.object(GitHubReader, "_get", fake_get):
            records = GitHubReader("example/club", "test-token").records(["2026-10-26"])
        self.assertEqual(len(records), 100)
        self.assertEqual([path for path, _ in calls if path.endswith("/comments")], ["issues/1/comments", "issues/2/comments"])
        self.assertTrue(any(path == "issues" and params["page"] == 2 for path, params in calls))

    def test_repository_validation_prevents_url_or_path_injection(self):
        self.assertEqual(validate_repository("Al-LeanMuscle-Club/AI-LeanMuscle-Club"), "Al-LeanMuscle-Club/AI-LeanMuscle-Club")
        for invalid in ("https://example.com/repo", "../repo/other", "a/b?token=oops", "a/b\ncommand", "a/b/c"):
            with self.assertRaises(ValueError):
                validate_repository(invalid)


if __name__ == "__main__":
    unittest.main()
