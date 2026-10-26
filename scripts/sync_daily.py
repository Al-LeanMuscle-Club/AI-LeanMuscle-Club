"""Publish the 100-point daily-check-in board from a complete GitHub snapshot.

Only self-reported work/exercise flags are counted. No model, raw member text,
plan ledger, or legacy 10-point report is used to calculate these reports.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from club.daily_checkins import build_week, public_handles, score_days  # noqa: E402
from scripts.github_api import GitHubReader, validate_repository  # noqa: E402

START = "<!-- CLUB:START -->"
END = "<!-- CLUB:END -->"
VERSION = 3
WINDOW = 12
ROW_FIELDS = ("rank", "handle", "issue_number", "issue_url", "work_days",
              "exercise_days", "checkin_days", "score", "time_zone")


def monday(value: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Report week must be a Monday YYYY-MM-DD.")
    parsed = date.fromisoformat(value)
    if parsed.weekday() != 0:
        raise ValueError("Report week must start on Monday.")
    return parsed


def reporting_weeks(as_of: datetime, explicit: str | None = None) -> list[str]:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("The report cutoff needs an explicit time zone.")
    today = as_of.astimezone(ZoneInfo("Asia/Shanghai")).date()
    if explicit:
        week = monday(explicit)
        if week > today:
            raise ValueError("Cannot publish a future report week.")
        return [week.isoformat()]
    week = today - timedelta(days=today.weekday())
    return [week.isoformat(), (week - timedelta(days=7)).isoformat()]


def ranked(rows: list[dict]) -> list[dict]:
    result = sorted((dict(row) for row in rows), key=lambda row: (-row["score"], row["handle"].casefold()))
    previous = None
    rank = 0
    for index, row in enumerate(result, 1):
        if previous is None or row["score"] != previous:
            rank = index
        row["rank"] = rank
        previous = row["score"]
    return result


def public_snapshot(board: dict, repository: str) -> dict:
    """Validate and project a public-only schema before writing any output."""
    validate_repository(repository)
    if board.get("schema_version") != VERSION or board.get("scoring_version") != VERSION:
        raise ValueError("Daily reports must use the v3 100-point schema.")
    week = monday(board["week_start"])
    generated = board["generated_at"]
    instant = datetime.fromisoformat(generated.replace("Z", "+00:00"))
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Report timestamp must include its time zone.")
    if not isinstance(board.get("leaderboard"), list):
        raise ValueError("Report leaderboard must be a list.")
    rows, seen = [], set()
    for original in board["leaderboard"]:
        row = {key: original[key] for key in ROW_FIELDS}
        handle = row["handle"]
        if not isinstance(handle, str) or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", handle):
            raise ValueError("Invalid public member handle.")
        if handle.casefold() in seen:
            raise ValueError("Each member may appear once per week.")
        seen.add(handle.casefold())
        if type(row["issue_number"]) is not int or row["issue_number"] < 1:
            raise ValueError("Invalid journal number.")
        for key in ("work_days", "exercise_days", "checkin_days"):
            if type(row[key]) is not int or not 0 <= row[key] <= 7:
                raise ValueError("Day counts must be integers from zero to seven.")
        if row["checkin_days"] < max(row["work_days"], row["exercise_days"]):
            raise ValueError("Work/exercise days cannot exceed check-in days.")
        if isinstance(row["score"], bool) or not isinstance(row["score"], (int, float)) or not math.isfinite(row["score"]) or not 0 <= row["score"] <= 100:
            raise ValueError("Invalid 100-point score.")
        if row["score"] != score_days(row["work_days"], row["exercise_days"]):
            raise ValueError("Saved score does not match the declared work/exercise days.")
        ZoneInfo(row["time_zone"])
        row["issue_url"] = f"https://github.com/{repository}/issues/{row['issue_number']}"
        rows.append(row)
    return {"schema_version": VERSION, "scoring_version": VERSION,
            "week_start": week.isoformat(), "week_end": (week + timedelta(days=6)).isoformat(),
            "generated_at": instant.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "participants_count": len(rows), "leaderboard": ranked(rows)}


def board_markdown(board: dict) -> str:
    lines = [f"# 每周打卡榜 · {board['week_start']} — {board['week_end']}", "",
             "100 分制 v3 · 每人每个本地日期最多计一天；同分并列。", "",
             "`S = 100 × sqrt(min(W / 5, 1) × min(E / 4, 1))`", "",
             "W 为工作天数，E 为运动天数；任何一项为 0 时总分为 0。工作 5 天、运动 4 天分别封顶。", "",
             "| 名次 | 成员 | 工作天数 W | 运动天数 E | 分数 / 100 | 打卡帖 |",
             "| ---: | --- | ---: | ---: | ---: | --- |"]
    for row in board["leaderboard"]:
        lines.append(f"| {row['rank']} | @{row['handle']} | {row['work_days']} | {row['exercise_days']} | "
                     f"{row['score']:.2f} | [#{row['issue_number']}]({row['issue_url']}) |")
    if not board["leaderboard"]:
        lines += ["", "本周暂无选择公开排名且有有效打卡的成员。"]
    lines += ["", f"数据更新：{board['generated_at']}。日期按各成员打卡帖所填时区解释。", "",
              "仅展示明确选择 Yes 的成员；经验交流不加分。原始 Issue 和评论始终公开。", "",
              "[计分规则](../../docs/SCORING.md) · [历史周榜](README.md) · [返回首页](../../README.md)"]
    return "\n".join(lines) + "\n"


def replace_readme(text: str, board: dict) -> str:
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise ValueError("README must retain exactly one correctly ordered CLUB marker pair.")
    week = board["week_start"]
    block = (f"{week} 起的一周：**{board['participants_count']}** 位成员进入公开打卡榜。\n\n"
             f"[查看本周 100 分榜单](reports/daily/{week}.md) · [历史周榜](reports/daily/README.md)\n\n"
             f"每日定时更新；数据更新：{board['generated_at']}。\n")
    return text[:text.index(START) + len(START)] + "\n\n" + block + "\n" + text[text.index(END):]


def write_reports(root: Path, boards: list[dict], records: list[dict], repository: str) -> None:
    """Keep v3 snapshots separate and withdraw opted-out rows from v3 history."""
    if not boards:
        raise ValueError("At least one report is required.")
    current = {board["week_start"]: public_snapshot(board, repository) for board in boards}
    reports = root / "reports" / "daily"
    snapshots = {}
    for path in reports.glob("????-??-??.json"):
        saved = public_snapshot(json.loads(path.read_text(encoding="utf-8")), repository)
        if path.stem != saved["week_start"]:
            raise ValueError("Report filename and week do not match.")
        snapshots[path.stem] = saved
    snapshots.update(current)
    allowed = public_handles(records)
    for board in snapshots.values():
        rows = [row for row in board["leaderboard"] if row["handle"].casefold() in allowed]
        if len(rows) != len(board["leaderboard"]):
            board["leaderboard"] = ranked(rows)
            board["participants_count"] = len(rows)
            board["generated_at"] = max(item["generated_at"] for item in current.values())
    weeks = sorted(snapshots, reverse=True)
    index = {"schema_version": VERSION, "scoring_version": VERSION,
             "available_weeks": weeks, "weeks": [snapshots[week] for week in weeks[:WINDOW]]}
    readme = replace_readme((root / "README.md").read_text(encoding="utf-8"), snapshots[weeks[0]])
    archive = ["# 每周打卡榜 · 100 分制", "",
               "按个人打卡帖中的日期统计自然周；每天由 GitHub Actions 更新本周与上周。", "",
               "[计分规则](../../docs/SCORING.md) · [返回首页](../../README.md)", ""]
    archive += [f"- [{week} 起的一周]({week}.md)" for week in weeks]
    archive += ["", "旧的 10 分制报告单独保留为[历史档案](../README.md)，与新榜不混算。"]
    outputs = {root / "README.md": readme, reports / "README.md": "\n".join(archive) + "\n",
               reports / "index.json": json.dumps(index, ensure_ascii=False, indent=2) + "\n"}
    for week, board in snapshots.items():
        outputs[reports / f"{week}.json"] = json.dumps(board, ensure_ascii=False, indent=2) + "\n"
        outputs[reports / f"{week}.md"] = board_markdown(board)
    # All parsing and validation finish before the first write. Raw API content
    # never becomes an output file, and v2 reports / the trusted ledger are untouched.
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        temporary = None
        try:
            with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(content)
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "Al-LeanMuscle-Club/AI-LeanMuscle-Club"))
    parser.add_argument("--week", help="Explicit Monday YYYY-MM-DD; otherwise refresh this week and last week.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--fixture", type=Path, help="Synthetic offline input, only with --dry-run.")
    parser.add_argument("--as-of", help="Aware ISO cutoff, only with an offline fixture.")
    parser.add_argument("--dry-run", action="store_true", help="Print public JSON without writing files.")
    args = parser.parse_args(argv)
    try:
        validate_repository(args.repository)
        if args.fixture and not args.dry_run:
            raise ValueError("Synthetic fixtures require --dry-run and cannot publish reports.")
        if args.as_of and not args.fixture:
            raise ValueError("--as-of is only available with a synthetic fixture.")
        as_of = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")) if args.as_of else datetime.now(timezone.utc)
        weeks = reporting_weeks(as_of, args.week)
        if args.fixture:
            records = json.loads(args.fixture.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                raise ValueError("Fixture must contain a JSON list.")
        else:
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
            records = GitHubReader(args.repository, token).daily_checkins()
        boards = [build_week(records, week, as_of, repository=args.repository) for week in weeks]
        if args.dry_run:
            print(json.dumps([public_snapshot(board, args.repository) for board in boards], ensure_ascii=False, indent=2))
        else:
            write_reports(args.root, boards, records, args.repository)
            print(f"Updated {len(boards)} daily-check-in weekly report(s).")
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        print(f"Daily report update failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
