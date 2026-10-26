"""Render a deterministic fictional leaderboard, never live community data.

Run ``python scripts/render_demo_board.py`` to rebuild the four demo artifacts
under examples/, including standalone Chinese and English board pages.
Repository homepages are never read or generated. ``--check`` is read-only and
returns 1 when an output is missing or stale. ``--root`` selects the repository
containing the fixture, which also permits isolated local checks.

Only examples/demo-training-records.json is read. Scoring
uses build_week with a fixed week/cutoff and temporary in-memory confirmations;
no GitHub API, cache, trusted ledger, or reports directory is accessed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import sys
from typing import Any

sys.dont_write_bytecode = True
SOURCE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_ROOT))

from club.scoring import build_week  # noqa: E402

WEEK = "2026-10-12"
AS_OF = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)
FIXTURE = Path("examples/demo-training-records.json")
HANDLES = {"demo-aurora", "demo-birch", "demo-cedar", "demo-delta", "demo-ember", "demo-finch"}
SPORTS = {
    "strength": ("Strength", "力量"), "basketball": ("Basketball", "篮球"),
    "running": ("Running", "跑步"), "swimming": ("Swimming", "游泳"),
    "cycling": ("Cycling", "骑行"), "walking": ("Walking", "步行"),
    "mobility": ("Mobility", "活动度"), "other": ("Other", "其他"),
}
STATUS = {
    "completed": "Full / 完整完成", "fallback": "Fallback / 替代完成",
    "partial": "Partial / 部分完成", "skipped": "Skipped / 跳过",
    "planned": "Unrecorded / 尚未记录",
}


def read_text(path: Path) -> str:
    # Decode bytes directly for deterministic generated output checks.
    return path.read_bytes().decode("utf-8")


def sections(body: str) -> dict[str, str]:
    headings = list(re.finditer(r"^###[ \t]+(.+?)[ \t]*$", body, re.MULTILINE))
    return {heading.group(1): body[heading.end():headings[index + 1].start()
                                  if index + 1 < len(headings) else len(body)].strip()
            for index, heading in enumerate(headings)}


def number(value: int | float) -> str:
    return f"{value:g}"


def cell(value: Any) -> str:
    return html.escape(str(value), quote=False).replace("|", "\\|").replace("\n", "<br>")


def code_block(value: str) -> str:
    longest = max((len(run) for run in re.findall(r"`+", value)), default=0)
    fence = "`" * max(3, longest + 1)
    return fence + "text\n" + value.rstrip() + "\n" + fence


def validate_fixture(records: Any) -> list[dict[str, Any]]:
    if not isinstance(records, list) or len(records) != 7 or not all(isinstance(item, dict) for item in records):
        raise ValueError("The demo fixture must contain six Active plans and one Recovery plan.")
    active = set()
    recovery = []
    seen = set()
    for issue in records:
        handle = issue.get("user", {}).get("login", "")
        if not re.fullmatch(r"demo-[a-z0-9-]+", handle) or handle in seen:
            raise ValueError("Every demo plan needs a distinct fictional demo- handle.")
        seen.add(handle)
        fields = sections(issue.get("body", ""))
        labels = {item.get("name") for item in issue.get("labels", []) if isinstance(item, dict)}
        if "weekly-plan" not in labels or labels & {"experience", "points-approved"}:
            raise ValueError("Only fictional weekly plans belong in this demo; contribution approvals are forbidden.")
        if fields.get("Week starting") != WEEK:
            raise ValueError(f"Every fictional plan must use week {WEEK}.")
        if fields.get("Participation mode") == "Active" and fields.get("Public leaderboard") == "Yes":
            active.add(handle)
        elif fields.get("Participation mode") == "Recovery" and fields.get("Public leaderboard") == "No":
            recovery.append(handle)
        else:
            raise ValueError("Use six Active/Yes plans and one Recovery/No plan.")
    if active != HANDLES or len(recovery) != 1:
        raise ValueError("The demo must contain its six declared fictional members and one Recovery member.")
    return records


def score(records: list[dict[str, Any]]) -> dict[str, Any]:
    # Omitting ranking_state intentionally creates temporary confirmations and
    # prevents reading or modifying any trusted contribution approval ledger.
    board = build_week(records, WEEK, AS_OF)
    if (board["warnings"] or len(board["leaderboard"]) != 6
            or board["participants_count"] != 7 or board["recovery_count"] != 1
            or {row["handle"] for row in board["leaderboard"]} != HANDLES
            or any(row["contribution_points"] != 0 for row in board["leaderboard"])):
        raise ValueError("The scorer rejected a fictional plan or found an unexpected contribution.")
    return board


def demo_board(board: dict[str, Any], chinese: bool) -> str:
    if chinese:
        lines = ["# 虚拟用户演示榜 — 2026-10-12 周", "",
                 "**简体中文** | [English](demo-board.en.md)", "",
                 "**以下是静态虚构演示，不是真实成员、打卡或成绩，不计入真实社区人数或排名。** "
                 "演示截止时间为 2026-10-19 12:00 UTC；六位参榜虚拟用户和一位恢复周虚拟用户均来自离线示例。", "",
                 "| 名次 | 虚拟用户 | 运动项目 | 完整 / 计划 | 部分完成 | 训练日 | 饮食日 | 参与分 / 10 |",
                 "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    else:
        lines = ["# Fictional demo leaderboard — week of 2026-10-12", "",
                 "[简体中文](demo-board.md) | **English**", "",
                 "**Static fictional examples, not real members, check-ins, or results. These do not enter the live community counts or standings.** "
                 "The demo cutoff is 2026-10-19 12:00 UTC, with six ranked fictional members and one fictional Recovery member from offline sample data.", "",
                 "| Rank | Fictional member | Sports | Full / planned | Partial | Training days | Meal days | Points / 10 |",
                 "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in board["leaderboard"]:
        sports = ("、" if chinese else ", ").join(SPORTS[sport][1 if chinese else 0] for sport in row["sports"])
        member = f"[{row['handle']}](demo-training-records.md#{row['handle']})"
        lines.append(f"| {row['rank']} | {member} | {sports} | {row['completed']} / {row['planned']} | "
                     f"{row['partial']} | {row['recorded_training_days']} | {row['meal_days']} | **{number(row['total_points'])}** |")
    lines += ["", ("完整与替代完成各计 1 次执行额度，部分完成计 0.5；训练日和饮食日不额外加分。恢复周不参榜。" if chinese else
                    "Full/fallback completion earns 1 execution unit; partial earns 0.5. Training and meal-record days add no points. Recovery is outside the board."), "",
              ("[查看每位虚拟用户的完整计划、原始记录与积分组成](demo-training-records.md) · "
               "[虚构榜单数据](demo-leaderboard.json) · [返回社区首页](../README.md)" if chinese else
               "[Full fictional plans, raw records, and score components](demo-training-records.md) · "
               "[Synthetic leaderboard data](demo-leaderboard.json) · [Community home](../README.en.md)")]
    return "\n".join(lines) + "\n"


def session_details(raw: str) -> dict[str, tuple[str, str]]:
    details = {}
    for line in raw.splitlines():
        parts = [part.strip() for part in re.sub(r"^(?:-[ \t]+(?:\[[ xX]\][ \t]+)?)?", "", line.strip()).split("|")]
        if len(parts) in (3, 4, 5):
            description = parts[2] if len(parts) == 3 else parts[3]
            fallback = parts[4] if len(parts) == 5 else "—"
            details[parts[0].upper()] = (description, fallback or "—")
    return details


def record_markdown(records: list[dict[str, Any]], board: dict[str, Any]) -> str:
    lines = ["# Fictional training records / 虚拟用户训练记录", "",
             "> **Synthetic demo only / 仅为虚构演示。** These people, plans, meals, and reflections are invented. "
             "They are not real members or activity and never enter live community statistics. "
             "人物、计划、餐食和复盘均属虚构，不是真实成员或活动，不写入真实周报或统计。", "",
             f"Demo week / 演示周：**{WEEK}** · Cutoff / 截止：**2026-10-19 12:00 UTC**", "",
             "The six Active/Yes demo plans below are scored by the repository's unchanged `build_week` function, "
             "with temporary in-memory confirmations and no trusted contribution approvals. "
             "Six fictional score rows appear on the [demo board](demo-board.en.md); the Recovery member is documented separately below.", "",
             "以下六份 Active/Yes 虚构计划直接使用现有计分器，以临时内存确认计算，不读取真实审批 ledger。"
             "[演示榜](demo-board.md)展示六位虚拟用户的演示积分；恢复周成员在文末单独说明。", "",
             "Full/fallback = 1, partial = 0.5, skipped/unrecorded = 0. "
             "Execution points = `6 × (full + 0.5 × partial) / confirmed planned`. "
             "The full-completion rate does not count partial as full. Meal days count distinct dates and add no points.", "",
             "完整或替代完成计 1 次额度，部分完成计 0.5，跳过或尚未记录计 0。"
             "执行积分按已确认活动数计算；部分完成不计作完整完成。饮食天数按不同日期统计，不加分。", "",
             "[Fixture / 原始虚构数据](demo-training-records.json) · [Computed board / 计算结果](demo-leaderboard.json) · "
             "[Scoring rules / 积分规则](../docs/SCORING.md)", ""]
    by_handle = {issue["user"]["login"]: issue for issue in records}
    for row in board["leaderboard"]:
        handle = row["handle"]
        issue = by_handle[handle]
        fields = sections(issue["body"])
        lines += [f"## {handle}", "", "**Fictional member / 虚拟用户；not a GitHub profile / 不代表 GitHub 账号。**", "",
                  f"Demo rank / 演示名次：**{row['rank']}** · Full / 完整：**{row['completed']} / {row['planned']}** · "
                  f"Partial / 部分：**{row['partial']}** · Training days / 训练日：**{row['recorded_training_days']}** · "
                  f"Meal days / 饮食日：**{row['meal_days']}**", "",
                  f"Points / 积分：plan / 计划 **{number(row['plan_points'])}** + execution / 执行 **{number(row['execution_points'])}** + "
                  f"review / 复盘 **{number(row['review_points'])}** + contribution / 贡献 **{number(row['contribution_points'])}** "
                  f"= **{number(row['total_points'])} / 10**", "",
                  "### Plan and final status / 周计划与最终状态", "",
                  f"Week / 周次：{WEEK} · Time zone / 时区：{cell(fields['Time zone'])} · "
                  f"Goal / 目标：{cell(fields.get('Primary goal', 'habit'))} · "
                  f"Research week / 科研节奏：{cell(fields.get('Research week', 'regular'))}", "",
                  "| ID | Planned day / 计划日 | Sport / 项目 | Plan / 内容 | Fallback / 替代 | Final status / 最终状态 | Actual date / 实际日期 |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        details = session_details(fields["Planned sessions"])
        for session in row["sessions"]:
            description, fallback = details.get(session["id"], ("—", "—"))
            sport = SPORTS[session["sport"]]
            values = [session["id"], session["day"], " / ".join(sport), description, fallback,
                      STATUS[session["status"]], session["date"] or "—"]
            lines.append("| " + " | ".join(cell(value) for value in values) + " |")
        lines += ["", "### Original plan / 原始周计划", "", code_block(issue["body"]), ""]
        lines += raw_comments(issue)
    recovery = [issue for issue in records if issue["user"]["login"] not in HANDLES]
    lines += ["## Recovery member / 恢复周成员", "",
              "This fictional Recovery/No plan is excluded from scored standings, with no points debt. "
              "It appears here only as an example of taking a recovery week. "
              "以下 Recovery/No 虚构计划不参加计分，也不产生欠分，仅演示如何记录恢复周。", ""]
    for issue in recovery:
        lines += [f"### {issue['user']['login']}", "", code_block(issue["body"]), ""]
        lines += raw_comments(issue)
    return "\n".join(lines).rstrip() + "\n"


def raw_comments(issue: dict[str, Any]) -> list[str]:
    lines = ["### Original check-ins, meal logs, and reflection / 原始打卡、饮食与复盘", ""]
    for index, comment in enumerate(issue.get("comments_data", []), 1):
        lines += [f"#### Record {index} / 原始记录 {index}", "",
                  f"Recorded at / 评论时间：`{comment.get('created_at', 'unknown')}`", "",
                  code_block(comment["body"]), ""]
    if not issue.get("comments_data"):
        lines += ["No comments / 没有评论。", ""]
    return lines


def generated_files(root: Path) -> dict[Path, str]:
    records = validate_fixture(json.loads(read_text(root / FIXTURE)))
    board = score(records)
    payload = {"synthetic": True, "purpose": "Fictional offline examples, never live participation.",
               "source_fixture": FIXTURE.as_posix(), "week_start": WEEK,
               "as_of": AS_OF.isoformat().replace("+00:00", "Z"), "board": board}
    outputs = {
        Path("examples/demo-leaderboard.json"): json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        Path("examples/demo-training-records.md"): record_markdown(records, board),
        Path("examples/demo-board.md"): demo_board(board, True),
        Path("examples/demo-board.en.md"): demo_board(board, False),
    }
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=SOURCE_ROOT, help="Repository containing the fictional fixture.")
    parser.add_argument("--check", action="store_true", help="Read-only check; return 1 for missing or stale generated content.")
    args = parser.parse_args(argv)
    try:
        outputs = generated_files(args.root)
        stale = [path for path, expected in outputs.items()
                 if not (args.root / path).is_file() or read_text(args.root / path) != expected]
        if args.check:
            if stale:
                print("Stale fictional demo output: " + ", ".join(path.as_posix() for path in stale), file=sys.stderr)
                return 1
            print("Fictional demo artifacts and standalone board pages are up to date.")
            return 0
        for path in stale:
            (args.root / path).write_bytes(outputs[path].encode("utf-8"))
        print("Rendered fictional demo artifacts and standalone board pages.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Demo generation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
