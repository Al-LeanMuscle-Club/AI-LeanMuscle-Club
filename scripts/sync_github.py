"""Generate opt-in reports from GitHub Issues or an explicitly supplied local fixture."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from club.scoring import SCORING_VERSION, build_week  # noqa: E402
from club.ranking_state import load_state, new_state, save_state  # noqa: E402
from scripts.github_api import GitHubReader, validate_repository  # noqa: E402

START = "<!-- CLUB:START -->"
END = "<!-- CLUB:END -->"
INDEX_WEEKS = 12
CHINESE_README = "<!-- README:LANG=zh-CN -->"


def scoring_rules_note(board: dict, language: str = "en") -> str:
    """Describe the saved rules without assigning today's formula to old data."""
    version = board.get("scoring_version")
    if language == "zh-CN":
        if type(version) is int and version == SCORING_VERSION:
            return (f"计分规则：v{version}。整次完成或按预设替代方案完成计 1 次，部分完成计 0.5 次；"
                    "已确认计划固定计分分母。")
        if type(version) is int and version > 0:
            return f"计分规则：v{version}。保留该快照所记录规则下的分数。"
        return "计分规则：未记录。保留快照分数，不将当前公式追溯用于旧记录。"
    if type(version) is int and version == SCORING_VERSION:
        return (f"Scoring rules: v{version}. Full/fallback = 1, partial = 0.5; "
                "the confirmed plan fixes the denominator.")
    if type(version) is int and version > 0:
        return f"Scoring rules: v{version}. Scores retain the rules recorded for this snapshot."
    return ("Scoring rules: not recorded. Snapshot scores are preserved; "
            "do not apply the current formula retroactively.")


def board_summary(board: dict, language: str = "en") -> str:
    """Keep the home page bounded; full member rows live in weekly reports."""
    summary = board.get("summary", {})
    rows = board["leaderboard"]
    planned = summary.get("planned_sessions", sum(row["planned"] for row in rows))
    completed = summary.get("completed_sessions", sum(row["completed"] for row in rows))
    reviewed = summary.get("reviewed_members", sum(bool(row["review_points"]) for row in rows))
    week = board["week_start"]
    if language == "zh-CN":
        lines = [
            f"### 周次：{week} 起", "",
            f"参与人数：**{board['participants_count']}** · 恢复/暂停人数：**{board['recovery_count']}**", "",
            f"公开参与人数：**{len(rows)}** · 已记录完成：**{completed}/{planned}** · 周复盘：**{reviewed}**", "",
            "次数仅汇总选择公开的活跃成员各自的计划，不代表健康或运动能力排名。", "",
            scoring_rules_note(board, language), "",
            f"[完整周报](reports/{week}.md) · [公开数据](reports/{week}.json) · [查找计划与打卡助手](tools/index.html)", "",
            f"更新时间：{board['generated_at']}",
        ]
        if board.get("counts_updated_at"):
            lines += [f"参与/恢复人数更新：{board['counts_updated_at']}（得分快照时间不变）。"]
        if board["warnings"]:
            translated = {
                "A weekly plan was skipped because required fields were invalid.": "有周计划因必填字段无效而被跳过。",
                "Duplicate weekly plans were found; only the earliest valid plan counts.": "发现重复周计划，仅统计最早的有效计划。",
            }
            messages = [translated.get(message, "另有记录提示，请查看完整周报。") for message in board["warnings"]]
            lines += ["", "有些记录需要检查：" + " ".join(messages)]
        return "\n".join(lines) + "\n"
    lines = [
        f"### Week starting {week}", "",
        f"Participants: **{board['participants_count']}** · Recovery/paused: **{board['recovery_count']}**", "",
        f"Opted-in active members: **{len(rows)}** · Recorded sessions: **{completed}/{planned}** · Weekly reflections: **{reviewed}**", "",
        "Session totals describe opted-in active members' own plans; they are not health or athletic rankings.", "",
        scoring_rules_note(board), "",
        f"[Full weekly report](reports/{week}.md) · [Public data](reports/{week}.json) · [Find my plan / browser helper](tools/index.html)", "",
        f"Updated: {board['generated_at']}",
    ]
    if board["warnings"]:
        lines += ["", "Some records need attention: " + " ".join(board["warnings"])]
    return "\n".join(lines) + "\n"


def reporting_weeks(as_of: datetime, explicit: str | None = None) -> list[str]:
    if explicit:
        selected = date.fromisoformat(explicit)
        if selected.isoformat() != explicit or selected.weekday() != 0:
            raise ValueError("--week must be a Monday in YYYY-MM-DD format.")
        return [explicit]
    today = as_of.astimezone(ZoneInfo("Asia/Shanghai")).date()
    monday = today - timedelta(days=today.weekday())
    return [monday.isoformat(), (monday - timedelta(days=7)).isoformat()]


def board_markdown(board: dict, report_links: bool = False) -> str:
    if report_links:
        return board_summary(board)
    lines = [
        f"### Week starting {board['week_start']}", "",
        f"Updated: {board['generated_at']} · Valid weekly participants: {board['participants_count']} · "
        f"Recovery/paused: {board['recovery_count']}", "",
        "Only opted-in Active participants are named. These are self-reported participation points.", "",
        scoring_rules_note(board), "",
    ]
    if board.get("counts_updated_at"):
        lines += [f"Participant/recovery counts refreshed: {board['counts_updated_at']}. "
                  "Remaining members' scores retain the original snapshot above.", ""]
    if board["leaderboard"]:
        plan_heading = "confirmed" if board.get("scoring_version") == SCORING_VERSION else "planned"
        lines += [
            f"| Rank | Member | Full / {plan_heading} | Plan | Execution | Review | Contribution | Total / 10 |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in board["leaderboard"]:
            lines.append(
                f"| {row['rank']} | [@{row['handle']}]({row['issue_url']}) | "
                f"{row['completed']} / {row['planned']} | {row['plan_points']:g} | "
                f"{row['execution_points']:g} | {row['review_points']:g} | "
                f"{row['contribution_points']:g} | **{row['total_points']:g}** |"
            )
    else:
        lines.append("No opted-in Active participants to display for this week yet.")
    if board["warnings"]:
        lines += ["", "Some records need attention: " + " ".join(board["warnings"])]
    if board.get("sports"):
        lines += ["", "#### Activities in opted-in active plans", "", "| Activity | Planned | Recorded complete |", "| --- | ---: | ---: |"]
        for item in board["sports"]:
            lines.append(f"| {item['sport']} | {item['planned']} | {item['completed']} |")
    if board["leaderboard"]:
        lines += ["", "#### Goals and weekly context", "", "| Member | Goal | Research week | Activities | Partial / skipped | Training days | Meal days | Current / confirmed plan |", "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |"]
        for row in board["leaderboard"]:
            changed = " (adjusted)" if row.get("plan_changed") else ""
            counts = {key: row.get(key) if row.get(key) is not None else "—" for key in (
                "partial", "skipped", "recorded_training_days", "meal_days", "current_planned", "confirmed_planned"
            )}
            lines.append(f"| [@{row['handle']}]({row['issue_url']}) | {row.get('goal', 'habit')} | {row.get('research_week', 'regular')} | {', '.join(row.get('sports', []))} | {counts['partial']} / {counts['skipped']} | {counts['recorded_training_days']} | {counts['meal_days']} | {counts['current_planned']} / {counts['confirmed_planned']}{changed} |")
        lines += ["", "A dash means this snapshot did not record that field."]
        if board.get("scoring_version") == SCORING_VERSION:
            lines += ["Training/meal days count distinct recorded dates and add no points. "
                      "Extra sessions remain visible in public data but do not change the confirmed denominator or execution score."]
    return "\n".join(lines) + "\n"


def public_index_snapshot(board: dict) -> dict:
    """Allowlist fields so the browser index cannot republish notes or meals."""
    snapshot = {key: board[key] for key in (
        "week_start", "generated_at", "participants_count", "recovery_count"
    )}
    snapshot["schema_version"] = 2
    version = board.get("scoring_version")
    if type(version) is int and version > 0:
        snapshot["scoring_version"] = version
    if "counts_updated_at" in board:
        snapshot["counts_updated_at"] = board["counts_updated_at"]
    snapshot["summary"] = {key: value for key, value in board.get("summary", {}).items()
                           if key in {"public_members", "planned_sessions", "completed_sessions", "partial_sessions", "skipped_sessions", "reviewed_members"}}
    snapshot["sports"] = [{key: row[key] for key in ("sport", "planned", "completed")}
                          for row in board.get("sports", [])]
    keys = {"rank", "handle", "issue_number", "issue_url", "planned", "completed", "completion_rate",
            "plan_points", "execution_points", "review_points", "contribution_points", "total_points",
            "goal", "research_week", "sports", "partial", "skipped", "confirmed_planned", "current_planned",
            "plan_changed", "execution_rate", "meal_days", "recorded_training_days"}
    snapshot["leaderboard"] = []
    for row in board["leaderboard"]:
        clean = {key: value for key, value in row.items() if key in keys}
        clean["sessions"] = [{key: value for key, value in session.items()
                              if key in {"id", "day", "sport", "status", "date", "used_fallback", "confirmed"}}
                             for session in row.get("sessions", [])]
        snapshot["leaderboard"].append(clean)
    return snapshot


def replace_readme(text: str, boards: list[dict]) -> str:
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
        raise ValueError("README needs exactly one correctly ordered CLUB:START / CLUB:END block.")
    start = text.index(START) + len(START)
    end = text.index(END)
    language = "zh-CN" if CHINESE_README in text else "en"
    block = "\n\n" + "\n".join(board_summary(board, language) for board in boards) + "\n"
    return text[:start] + block + text[end:]


def _withdraw_history(board: dict, eligible: set[tuple[int, str, str]], *, current: dict | None = None) -> bool:
    """Remove withdrawn historical rows without republishing old source text."""
    original = board["leaderboard"]
    rows = [row for row in original if (row.get("issue_number"), row.get("handle", "").casefold(), board["week_start"]) in eligible]
    counts_changed = current is not None and any(board.get(key) != current[key]
                                                for key in ("participants_count", "recovery_count"))
    if len(rows) == len(original) and not counts_changed:
        return False
    if current is not None:
        for key in ("participants_count", "recovery_count"):
            board[key] = current[key]
        # Scores and their generation time remain the archived snapshot. Counts
        # are explicitly a newer view of currently valid plans and withdrawals.
        board["counts_updated_at"] = current["generated_at"]
    board["leaderboard"] = rows
    rows.sort(key=lambda row: (-row["total_points"], -row["completion_rate"], row["handle"].casefold()))
    previous = None
    rank = 0
    for position, row in enumerate(rows, 1):
        if row["total_points"] != previous:
            rank = position
        row["rank"] = rank
        previous = row["total_points"]
    board["summary"] = {
        "public_members": len(rows), "planned_sessions": sum(row["planned"] for row in rows),
        "completed_sessions": sum(row["completed"] for row in rows),
        "partial_sessions": sum(row.get("partial", 0) for row in rows),
        "skipped_sessions": sum(row.get("skipped", 0) for row in rows),
        "reviewed_members": sum(bool(row["review_points"]) for row in rows),
    }
    sports: dict[str, dict] = {}
    for row in rows:
        for session in row.get("sessions", []):
            if not session.get("confirmed", True):
                continue
            sport = session["sport"]
            item = sports.setdefault(sport, {"sport": sport, "planned": 0, "completed": 0})
            item["planned"] += 1
            item["completed"] += session["status"] in {"completed", "fallback"}
    board["sports"] = [sports[key] for key in sorted(sports)]
    return True


def write_reports(root: Path, boards: list[dict], *, source_records: list | None = None,
                  as_of: datetime | None = None, ranking_state: dict | None = None) -> None:
    """Validate the README before writing anything; never save raw issue bodies."""
    readme = root / "README.md"
    updated_readme = replace_readme(readme.read_text(encoding="utf-8"), boards)
    reports = root / "reports"
    snapshots = {}
    rewritten = {}
    current_by_week = {board["week_start"]: board for board in boards}
    for path in reports.glob("????-??-??.json"):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.stem):
            continue
        old = json.loads(path.read_text(encoding="utf-8"))
        if old.get("week_start") != path.stem:
            raise ValueError("An archived report has an inconsistent week; no reports were changed.")
        if source_records is not None:
            current = current_by_week.get(path.stem)
            if current is None:
                current = build_week(source_records, path.stem, as_of or datetime.now(timezone.utc),
                                     ranking_state=ranking_state)
            eligible = {(row["issue_number"], row["handle"].casefold(), path.stem)
                        for row in current["leaderboard"]}
            if _withdraw_history(old, eligible, current=current):
                rewritten[path.stem] = old
        snapshots[path.stem] = public_index_snapshot(old)
    rewritten.update({board["week_start"]: board for board in boards})
    for board in rewritten.values():
        snapshots[board["week_start"]] = public_index_snapshot(board)
    weeks = sorted(snapshots, reverse=True)
    index = {"schema_version": 2, "window_weeks": INDEX_WEEKS,
             "available_weeks": weeks, "weeks": [snapshots[week] for week in weeks[:INDEX_WEEKS]]}
    archive = "# Weekly participation reports\n\nOnly opted-in active members are named. Raw notes, food logs, and photos are not copied here.\n\n"
    archive += "The [browser helper](../tools/index.html) loads the latest 12 report weeks. Older reports remain available below.\n\n"
    archive += "\n".join(f"- [{week}]({week}.md) · [JSON]({week}.json)" for week in weeks) + "\n"
    reports.mkdir(parents=True, exist_ok=True)
    for board in rewritten.values():
        name = board["week_start"]
        markdown = "# AI Lean Muscle Club — weekly participation\n\n" + board_markdown(board)
        markdown += "\nScores are revisable snapshots. See [scoring rules](../docs/SCORING.md).\n"
        (reports / f"{name}.md").write_text(markdown, encoding="utf-8")
        (reports / f"{name}.json").write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (reports / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (reports / "README.md").write_text(archive, encoding="utf-8")
    readme.write_text(updated_readme, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "Al-LeanMuscle-Club/AI-LeanMuscle-Club"))
    parser.add_argument("--week", help="A Monday YYYY-MM-DD; otherwise current and previous Asia/Shanghai weeks.")
    parser.add_argument("--fixture", type=Path, help="Offline list of synthetic GitHub issue records; never use as real community data.")
    parser.add_argument("--as-of", help="ISO-8601 instant for reproducible offline tests; live runs use current UTC.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root containing README markers.")
    parser.add_argument("--cache", type=Path, help="Private local sync cache; defaults to ROOT/.club-cache/issues.json.")
    parser.add_argument("--ranking-state", type=Path, help="Trusted ledger; defaults to ROOT/data/ranking-state.json.")
    parser.add_argument("--no-cache", action="store_true", help="Read a complete live snapshot without caching.")
    parser.add_argument("--refresh", action="store_true", help="Rebuild the live cache with a full scan.")
    parser.add_argument("--deleted-issue", type=int, help="Trusted issues.deleted webhook Issue number to evict from the incremental cache.")
    parser.add_argument("--dry-run", action="store_true", help="Print public report JSON without writing files.")
    args = parser.parse_args(argv)
    try:
        validate_repository(args.repository)
        if args.as_of and not args.fixture:
            raise ValueError("--as-of is only available with an offline fixture.")
        if args.deleted_issue is not None and (args.deleted_issue < 1 or args.fixture):
            raise ValueError("--deleted-issue requires a positive Issue number and live GitHub data.")
        as_of = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")) if args.as_of else datetime.now(timezone.utc)
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("--as-of must include a time-zone offset.")
        as_of = as_of.astimezone(timezone.utc)
        weeks = reporting_weeks(as_of, args.week)
        live_state = args.root / "data" / "ranking-state.json"
        state_path = args.ranking_state or live_state
        if args.fixture and args.ranking_state and state_path.resolve() in {
            live_state.resolve(), (ROOT / "data" / "ranking-state.json").resolve()
        }:
            raise ValueError("A fixture --ranking-state must be separate from the live ranking ledger.")
        # A damaged or incompatible ledger must fail before any API/cache/report
        # writes. A missing ledger is a deliberate first-time confirmation.
        ranking_state = new_state() if args.fixture and not args.ranking_state else load_state(state_path)
        if args.fixture:
            issues = json.loads(args.fixture.read_text(encoding="utf-8"))
            if not isinstance(issues, list):
                raise ValueError("Fixture must contain a JSON list of GitHub issue records.")
        else:
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
            cache = None if args.no_cache or args.dry_run else (args.cache or args.root / ".club-cache" / "issues.json")
            archived = [path.stem for path in (args.root / "reports").glob("????-??-??.json")
                        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.stem)]
            read_weeks = sorted(set(weeks + archived))
            issues = GitHubReader(args.repository, token).records(
                read_weeks, cache_path=cache, refresh=args.refresh, deleted_issue=args.deleted_issue
            )
        boards = [build_week(issues, week, as_of, ranking_state=ranking_state) for week in weeks]
        if args.dry_run:
            print(json.dumps(boards, indent=2, ensure_ascii=False))
        else:
            write_reports(args.root, boards, source_records=None if args.fixture else issues,
                          as_of=as_of, ranking_state=ranking_state)
            # Fixture runs remain isolated unless a ledger path is explicitly
            # selected. A dry-run never confirms or persists a live baseline.
            if not args.fixture or args.ranking_state:
                save_state(state_path, ranking_state)
            print(f"Updated {len(boards)} weekly snapshot(s); public rows: " + str(sum(len(b['leaderboard']) for b in boards)))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Report update failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
