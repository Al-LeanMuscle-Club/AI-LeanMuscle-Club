"""Generate opt-in reports from GitHub Issues or an explicitly supplied local fixture."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from club.scoring import build_week  # noqa: E402
from scripts.github_api import GitHubReader, validate_repository  # noqa: E402

START = "<!-- CLUB:START -->"
END = "<!-- CLUB:END -->"


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
    if report_links:
        lines += ["", f"[Weekly report](reports/{board['week_start']}.md) · [Public data](reports/{board['week_start']}.json)"]
    return "\n".join(lines) + "\n"


def replace_readme(text: str, boards: list[dict]) -> str:
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
        raise ValueError("README needs exactly one correctly ordered CLUB:START / CLUB:END block.")
    start = text.index(START) + len(START)
    end = text.index(END)
    block = "\n\n" + "\n".join(board_markdown(board, True) for board in boards) + "\n"
    return text[:start] + block + text[end:]


def write_reports(root: Path, boards: list[dict]) -> None:
    """Validate the README before writing anything; never save raw issue bodies."""
    readme = root / "README.md"
    updated_readme = replace_readme(readme.read_text(encoding="utf-8"), boards)
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    for board in boards:
        name = board["week_start"]
        markdown = "# AI Lean Muscle Club — weekly participation\n\n" + board_markdown(board)
        markdown += "\nScores are revisable snapshots. See [scoring rules](../docs/SCORING.md).\n"
        (reports / f"{name}.md").write_text(markdown, encoding="utf-8")
        (reports / f"{name}.json").write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    readme.write_text(updated_readme, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "Al-LeanMuscle-Club/AI-Lean-Muscle-Club"))
    parser.add_argument("--week", help="A Monday YYYY-MM-DD; otherwise current and previous Asia/Shanghai weeks.")
    parser.add_argument("--fixture", type=Path, help="Offline list of synthetic GitHub issue records; never use as real community data.")
    parser.add_argument("--as-of", help="ISO-8601 instant for reproducible offline tests; live runs use current UTC.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root containing README markers.")
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
            issues = GitHubReader(args.repository, token).records(weeks)
        boards = [build_week(issues, week, as_of) for week in weeks]
        if args.dry_run:
            print(json.dumps(boards, indent=2, ensure_ascii=False))
        else:
            write_reports(args.root, boards)
            print(f"Updated {len(boards)} weekly snapshot(s); public rows: " + str(sum(len(b['leaderboard']) for b in boards)))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Report update failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
