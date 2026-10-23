"""Read-only member helpers: find a plan, carry it forward, and check a record."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from club.scoring import _sections, validate_submission  # noqa: E402
from scripts.github_api import GitHubReader, validate_repository  # noqa: E402

HANDLE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")


def monday(value: str) -> str:
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value or parsed.weekday() != 0:
        raise ValueError("Choose a Monday in YYYY-MM-DD format.")
    return value


def carry_plan(body: str, week: str) -> str:
    """Create a reviewable draft; never copy a leaderboard opt-in or check-in."""
    monday(week)
    fields = _sections(body)
    if fields is None or not {"Week starting", "Time zone", "Participation mode", "Planned sessions"}.issubset(fields):
        raise ValueError("Use an existing weekly plan with unique form headings.")
    sessions = re.sub(r"(?m)^(\s*-\s+)\[[xX]\]", r"\1[ ]", fields["Planned sessions"])
    values = [
        ("Week starting", week),
        ("Time zone", fields["Time zone"]),
        ("Participation mode", fields["Participation mode"]),
        ("Public leaderboard", "No"),
        ("Primary goal", fields.get("Primary goal", "habit")),
        ("Research week", fields.get("Research week", "regular")),
        ("Planned sessions", sessions),
        ("Busy-week fallback", fields.get("Busy-week fallback", "")),
        ("Notes", fields.get("Notes", "")),
    ]
    return "\n\n".join(f"### {key}\n\n{value}" for key, value in values) + "\n"


def find_plans(records: list, handle: str, week: str, now: datetime) -> list[dict]:
    monday(week)
    if not HANDLE.fullmatch(handle):
        raise ValueError("Enter a valid GitHub username without @.")
    found = []
    for issue in records:
        if not isinstance(issue, dict) or "pull_request" in issue:
            continue
        if str(issue.get("user", {}).get("login", "")).casefold() != handle.casefold():
            continue
        labels = {item.get("name") for item in issue.get("labels", []) if isinstance(item, dict)}
        sections = _sections(issue.get("body"))
        if "weekly-plan" in labels and sections and sections.get("Week starting") == week and not validate_submission(issue, now=now):
            found.append(issue)
    return sorted(found, key=lambda issue: (issue["created_at"], issue["number"]))


def _common(parser: argparse.ArgumentParser, suppress: bool = False) -> None:
    default = argparse.SUPPRESS if suppress else os.environ.get("GITHUB_REPOSITORY", "Al-LeanMuscle-Club/AI-LeanMuscle-Club")
    parser.add_argument("--repository", default=default)
    parser.add_argument("--fixture", type=Path, default=argparse.SUPPRESS if suppress else None,
                        help="Local synthetic Issue records; no credentials or network required.")
    parser.add_argument("--as-of", default=argparse.SUPPRESS if suppress else None,
                        help="Explicit timestamp for offline fixture checks only.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    _common(parser)
    commands = parser.add_subparsers(dest="command", required=True)
    find = commands.add_parser("find", help="Find your earliest valid plan, including closed Issues.")
    _common(find, True)
    find.add_argument("--handle", required=True)
    find.add_argument("--week", required=True)
    carry = commands.add_parser("carry", help="Generate a draft only; review and submit it yourself.")
    _common(carry, True)
    carry.add_argument("--issue", required=True, type=int)
    carry.add_argument("--week", required=True)
    carry.add_argument("--output", type=Path)
    check = commands.add_parser("check", help="Validate a plan and optionally a proposed comment.")
    _common(check, True)
    check.add_argument("--issue", required=True, type=int)
    check.add_argument("--comment-file", type=Path)
    args = parser.parse_args(argv)
    try:
        repository = validate_repository(args.repository)
        if args.as_of and not args.fixture:
            raise ValueError("--as-of is only available with an offline fixture.")
        now = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")) if args.as_of else datetime.now(timezone.utc)
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("--as-of must contain a UTC offset.")
        now = now.astimezone(timezone.utc)
        records = None
        reader = None
        if args.fixture:
            records = json.loads(args.fixture.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                raise ValueError("The fixture must be a list of synthetic Issue records.")
        else:
            reader = GitHubReader(repository, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "")
        if args.command == "find":
            if not HANDLE.fullmatch(args.handle):
                raise ValueError("Enter a valid GitHub username without @.")
            monday(args.week)
            if records is None:
                records = list(reader._pages("issues", {"state": "all", "labels": "weekly-plan", "creator": args.handle}))
            found = find_plans(records, args.handle, args.week, now)
            if found:
                print(found[0]["html_url"])
                if len(found) > 1:
                    print("Duplicate plans exist; only the earliest valid plan counts.", file=sys.stderr)
            else:
                query = f"is:issue label:weekly-plan author:{args.handle} in:body {args.week}"
                print("No valid matching plan found. Check the form fields or search:")
                print(f"https://github.com/{repository}/issues?" + urlencode({"q": query}))
            return 0
        if args.issue < 1:
            raise ValueError("Issue number must be positive.")
        issue = next((record for record in records if isinstance(record, dict) and record.get("number") == args.issue), None) if records is not None else reader.get_issue(args.issue)
        if issue is None or "pull_request" in issue:
            raise ValueError("That weekly-plan Issue was not found.")
        errors = validate_submission(issue, now=now)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        if args.command == "carry":
            draft = carry_plan(issue["body"], args.week)
            if args.output:
                args.output.write_text(draft, encoding="utf-8")
                print(f"Draft written to {args.output}. Review its schedule and goals before posting; leaderboard opt-in is reset to No.")
            else:
                print(draft, end="")
                print("Draft only. Review before posting; leaderboard opt-in is reset to No.", file=sys.stderr)
            return 0
        proposed = args.comment_file.read_text(encoding="utf-8") if args.comment_file else None
        errors = validate_submission(issue, proposed, now=now)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("Format valid. This checks a self-reported record, not exercise quality or health. No changes were submitted.")
        return 0
    except (OSError, ValueError, RuntimeError, TypeError) as error:
        print(f"Member helper failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
