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

from club.scoring import _sections, build_week, validate_submission  # noqa: E402
from scripts.github_api import GitHubReader, validate_repository  # noqa: E402

START = "<!-- CLUB:START -->"
END = "<!-- CLUB:END -->"
INDEX_WEEKS = 12


def board_summary(board: dict) -> str:
    """Keep the home page bounded; full member rows live in weekly reports."""
    summary = board.get("summary", {})
    rows = board["leaderboard"]
    planned = summary.get("planned_sessions", sum(row["planned"] for row in rows))
    completed = summary.get("completed_sessions", sum(row["completed"] for row in rows))
    reviewed = summary.get("reviewed_members", sum(bool(row["review_points"]) for row in rows))
    week = board["week_start"]
    lines = [
        f"### Week starting {week}", "",
        f"Participants: **{board['participants_count']}** · Recovery/paused: **{board['recovery_count']}**", "",
        f"Opted-in active members: **{len(rows)}** · Recorded sessions: **{completed}/{planned}** · Weekly reflections: **{reviewed}**", "",
        "Session totals describe opted-in active members' own plans; they are not health or athletic rankings.", "",
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
        "Only opted-in Active participants are named. Completion means recorded sessions, not verified exercise or health outcomes.", "",
    ]
    if board["leaderboard"]:
        lines += [
            "| Rank | Member | Recorded / planned | Plan | Execution | Review | Contribution | Total / 10 |",
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
        lines += ["", "#### Goals and weekly context", "", "| Member | Goal | Research week | Activities | Partial / skipped |", "| --- | --- | --- | --- | ---: |"]
        for row in board["leaderboard"]:
            lines.append(f"| [@{row['handle']}]({row['issue_url']}) | {row.get('goal', 'habit')} | {row.get('research_week', 'regular')} | {', '.join(row.get('sports', []))} | {row.get('partial', 0)} / {row.get('skipped', 0)} |")
    return "\n".join(lines) + "\n"


def public_index_snapshot(board: dict) -> dict:
    """Allowlist fields so the browser index cannot republish notes or meals."""
    snapshot = {key: board[key] for key in (
        "week_start", "generated_at", "participants_count", "recovery_count"
    )}
    snapshot["schema_version"] = 2
    snapshot["summary"] = {key: value for key, value in board.get("summary", {}).items()
                           if key in {"public_members", "planned_sessions", "completed_sessions", "partial_sessions", "skipped_sessions", "reviewed_members"}}
    snapshot["sports"] = [{key: row[key] for key in ("sport", "planned", "completed")}
                          for row in board.get("sports", [])]
    keys = {"rank", "handle", "issue_number", "issue_url", "planned", "completed", "completion_rate",
            "plan_points", "execution_points", "review_points", "contribution_points", "total_points",
            "goal", "research_week", "sports", "partial", "skipped"}
    snapshot["leaderboard"] = []
    for row in board["leaderboard"]:
        clean = {key: value for key, value in row.items() if key in keys}
        clean["sessions"] = [{key: value for key, value in session.items()
                              if key in {"id", "day", "sport", "status", "date", "used_fallback"}}
                             for session in row.get("sessions", [])]
        snapshot["leaderboard"].append(clean)
    return snapshot


def replace_readme(text: str, boards: list[dict]) -> str:
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
        raise ValueError("README needs exactly one correctly ordered CLUB:START / CLUB:END block.")
    start = text.index(START) + len(START)
    end = text.index(END)
    block = "\n\n" + "\n".join(board_markdown(board, True) for board in boards) + "\n"
    return text[:start] + block + text[end:]


def _withdraw_history(board: dict, eligible: set[tuple[int, str, str]]) -> bool:
    """Remove withdrawn historical rows without republishing old source text."""
    original = board["leaderboard"]
    rows = [row for row in original if (row.get("issue_number"), row.get("handle", "").casefold(), board["week_start"]) in eligible]
    if len(rows) == len(original):
        return False
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
            sport = session["sport"]
            item = sports.setdefault(sport, {"sport": sport, "planned": 0, "completed": 0})
            item["planned"] += 1
            item["completed"] += session["status"] in {"completed", "fallback"}
    board["sports"] = [sports[key] for key in sorted(sports)]
    return True


def write_reports(root: Path, boards: list[dict], *, source_records: list | None = None,
                  as_of: datetime | None = None) -> None:
    """Validate the README before writing anything; never save raw issue bodies."""
    readme = root / "README.md"
    updated_readme = replace_readme(readme.read_text(encoding="utf-8"), boards)
    reports = root / "reports"
    snapshots = {}
    rewritten = {}
    eligible = None
    if source_records is not None:
        eligible = set()
        for issue in source_records:
            if not isinstance(issue, dict):
                continue
            labels = {item.get("name") for item in issue.get("labels", []) if isinstance(item, dict)}
            fields = _sections(issue.get("body"))
            if ("weekly-plan" in labels and fields and fields.get("Public leaderboard") == "Yes"
                    and fields.get("Participation mode") == "Active"
                    and not validate_submission(issue, now=as_of)):
                eligible.add((issue["number"], issue["user"]["login"].casefold(), fields["Week starting"]))
    for path in reports.glob("????-??-??.json"):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.stem):
            continue
        old = json.loads(path.read_text(encoding="utf-8"))
        if old.get("week_start") != path.stem:
            raise ValueError("An archived report has an inconsistent week; no reports were changed.")
        if eligible is not None and _withdraw_history(old, eligible):
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
    parser.add_argument("--no-cache", action="store_true", help="Read a complete live snapshot without caching.")
    parser.add_argument("--refresh", action="store_true", help="Rebuild the live cache with a full scan.")
    parser.add_argument("--dry-run", action="store_true", help="Print public report JSON without writing files.")
    args = parser.parse_args(argv)
    try:
        validate_repository(args.repository)
        if args.as_of and not args.fixture:
            raise ValueError("--as-of is only available with an offline fixture.")
        as_of = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")) if args.as_of else datetime.now(timezone.utc)
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("--as-of must include a time-zone offset.")
        as_of = as_of.astimezone(timezone.utc)
        weeks = reporting_weeks(as_of, args.week)
        if args.fixture:
            issues = json.loads(args.fixture.read_text(encoding="utf-8"))
            if not isinstance(issues, list):
                raise ValueError("Fixture must contain a JSON list of GitHub issue records.")
        else:
            token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
            cache = None if args.no_cache else (args.cache or args.root / ".club-cache" / "issues.json")
            issues = GitHubReader(args.repository, token).records(weeks, cache_path=cache, refresh=args.refresh)
        boards = [build_week(issues, week, as_of) for week in weeks]
        if args.dry_run:
            print(json.dumps(boards, indent=2, ensure_ascii=False))
        else:
            write_reports(args.root, boards, source_records=None if args.fixture else issues, as_of=as_of)
            print(f"Updated {len(boards)} weekly snapshot(s); public rows: " + str(sum(len(b['leaderboard']) for b in boards)))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Report update failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
