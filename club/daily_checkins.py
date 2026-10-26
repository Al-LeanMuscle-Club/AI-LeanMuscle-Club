"""Deterministic weekly scores from an owner's daily work/exercise check-ins.

This module interprets explicit check-in commands and marked legacy exercise
dates, never prose or model output. Only weekly counts from publicly enabled
journals leave the calculation; bodies, notes, individual dates and comment
metadata are not part of public reports.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP, localcontext
import re
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from club.community import is_example, label_names


SCORING_VERSION = 3
SCHEMA_VERSION = 3
DEFAULT_REPOSITORY = "Al-LeanMuscle-Club/AI-LeanMuscle-Club"
_PREFIX = re.compile(r"^\s*\[Check-in\]", re.IGNORECASE)
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
_HANDLE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
_REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_HEADING = re.compile(r"^###[ \t]+([^\n]+?)[ \t]*$", re.MULTILINE)
_COMMAND = re.compile(
    r"/checkin[ \t]+(\d{4}-\d{2}-\d{2})[ \t]+W=([01])[ \t]+E=([01])[ \t]*\Z",
    re.IGNORECASE,
)
_COMMAND_LINE = re.compile(r"^/checkin(?:\s|$)", re.IGNORECASE)
_ACTIVITY_IMPORT = "<!-- club-import:activity-v1 -->"


@dataclass(frozen=True)
class _User:
    handle: str
    user_id: int | None


@dataclass(frozen=True)
class _Journal:
    issue: Mapping[str, Any]
    owner: _User
    number: int
    created: datetime


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if instant.tzinfo is None or instant.utcoffset() is None:
            return None
        return instant.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def _date(value: object) -> date | None:
    if not isinstance(value, str) or not _DATE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _user(record: Mapping[str, Any]) -> _User | None:
    user = record.get("user")
    if not isinstance(user, Mapping):
        return None
    handle = user.get("login")
    if (not isinstance(handle, str) or not _HANDLE.fullmatch(handle)
            or user.get("type") not in (None, "User")):
        return None
    user_id = user.get("id")
    if user_id is not None and (type(user_id) is not int or user_id < 1):
        return None
    return _User(handle, user_id)


def is_journal(issue: object) -> bool:
    """Recognize a declared journal, including one with invalid configuration.

    A newer invalid, private or closed journal must still supersede its owner's
    old journal. Configuration validation therefore happens after selection.
    A template title is sufficient for discovery; labels are not required.
    """
    if not isinstance(issue, dict) or "pull_request" in issue or _user(issue) is None:
        return False
    title = issue.get("title")
    stripped = dict(issue)
    if isinstance(title, str):
        stripped["title"] = _PREFIX.sub("", title, count=1)
    if is_example(issue) or is_example(stripped):
        return False
    return bool(isinstance(title, str) and _PREFIX.match(title)
                or "daily-checkin" in label_names(issue))


def _form_fields(issue: Mapping[str, Any]) -> dict[str, str] | None:
    body = issue.get("body")
    if not isinstance(body, str):
        return None
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    matches = list(_HEADING.finditer(body))
    fields: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(1)
        if heading in fields:
            return None
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        fields[heading] = body[match.end():end].strip()
    return fields


def _configuration(issue: Mapping[str, Any]) -> tuple[ZoneInfo, bool] | None:
    fields = _form_fields(issue)
    if fields is None:
        return None
    public = fields.get("Public leaderboard", "").casefold()
    if public not in {"yes", "no"}:
        return None
    try:
        zone = ZoneInfo(fields.get("Time zone", ""))
    except (ZoneInfoNotFoundError, ValueError):
        return None
    return zone, public == "yes"


def _canonical_journals(records: Iterable[object]) -> list[_Journal]:
    candidates = []
    for issue in records:
        if not is_journal(issue):
            continue
        number, created = issue.get("number"), _timestamp(issue.get("created_at"))
        if type(number) is not int or number < 1 or created is None:
            continue
        candidates.append(_Journal(issue, _user(issue), number, created))
    # A GitHub response has one record per Issue. The final keys also make
    # repeated fixture snapshots deterministic, preferring withdrawal on ties.
    def key(journal: _Journal) -> tuple:
        config = _configuration(journal.issue)
        withdrawn = journal.issue.get("state") != "open" or not config or not config[1]
        return (journal.created, journal.number,
                _timestamp(journal.issue.get("updated_at")) or journal.created,
                withdrawn, str(journal.issue.get("body") or ""))

    seen_ids: set[int] = set()
    seen_handles: set[str] = set()
    selected = []
    for journal in sorted(candidates, key=key, reverse=True):
        owner = journal.owner
        handle = owner.handle.casefold()
        if handle in seen_handles or owner.user_id is not None and owner.user_id in seen_ids:
            continue
        seen_handles.add(handle)
        if owner.user_id is not None:
            seen_ids.add(owner.user_id)
        selected.append(journal)
    return selected


def public_handles(records: Iterable[object]) -> set[str]:
    """Current publicly enabled owners, including those without a check-in this week.

    Report writers use this allowlist to remove withdrawn members from stored
    public snapshots. Closing a journal or changing Yes to No withdraws it.
    """
    eligible = set()
    for journal in _canonical_journals(records):
        config = _configuration(journal.issue)
        if journal.issue.get("state") == "open" and config and config[1]:
            eligible.add(journal.owner.handle.casefold())
    return eligible


def score_days(work_days: int, exercise_days: int) -> float:
    """100 * sqrt(min(W / 5, 1) * min(E / 4, 1)), rounded half up to 0.01."""
    if any(type(days) is not int or days < 0 for days in (work_days, exercise_days)):
        raise ValueError("Work and exercise days must be nonnegative integers.")
    with localcontext() as context:
        context.prec = 28
        work = Decimal(min(work_days, 5)) / 5
        exercise = Decimal(min(exercise_days, 4)) / 4
        score = (Decimal(100) * (work * exercise).sqrt()).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(score)


def _owned_comment(comment: Mapping[str, Any], owner: _User) -> bool:
    author = _user(comment)
    if author is None:
        return False
    if owner.user_id is not None and author.user_id is not None:
        return owner.user_id == author.user_id
    return owner.handle.casefold() == author.handle.casefold()


def _imported_exercise_date(journal: _Journal, zone: ZoneInfo, start: date,
                            end: date, as_of: datetime) -> date | None:
    fields = _form_fields(journal.issue)
    if fields is None or _ACTIVITY_IMPORT not in {
            line.strip() for line in fields.get("Migration notes", "").splitlines()}:
        return None
    imported = _date(fields.get("Imported exercise date"))
    original = _date(fields.get("Activity date"))
    if (imported is None or imported != original or not start <= imported <= end
            or imported > journal.created.astimezone(zone).date()
            or imported > as_of.astimezone(zone).date()):
        return None
    return imported


def _checkins(journal: _Journal, zone: ZoneInfo, start: date, end: date,
              as_of: datetime) -> dict[date, tuple[int, int]]:
    days = {}
    imported = _imported_exercise_date(journal, zone, start, end, as_of)
    if imported is not None:
        # Legacy Activity forms establish exercise only. Zero here grants no
        # work credit; it does not claim that the member did not work that day.
        days[imported] = (0, 1)
    comments = journal.issue.get("comments_data")
    if not isinstance(comments, list):
        return days
    latest: dict[date, tuple[tuple, int, int]] = {}
    today = as_of.astimezone(zone).date()
    for comment in comments:
        if not isinstance(comment, Mapping) or not _owned_comment(comment, journal.owner):
            continue
        body = comment.get("body")
        if not isinstance(body, str):
            continue
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or sum(bool(_COMMAND_LINE.match(line)) for line in lines) != 1:
            continue
        match = _COMMAND.fullmatch(lines[0])
        if match is None:
            continue
        day = _date(match.group(1))
        created = _timestamp(comment.get("created_at"))
        updated = _timestamp(comment.get("updated_at", comment.get("created_at")))
        comment_id = comment.get("id", 0)
        if (day is None or created is None or updated is None
                or created < journal.created or updated < created or updated > as_of
                or type(comment_id) is not int or comment_id < 0
                or not start <= day <= end or day > today
                or day > updated.astimezone(zone).date()):
            continue
        work, exercise = int(match.group(2)), int(match.group(3))
        # IDs resolve same-second edits deterministically. Old fixture records
        # without IDs use the explicit command as a stable final tie-breaker.
        key = (updated, created, comment_id, lines[0])
        previous = latest.get(day)
        if previous is None or key > previous[0]:
            latest[day] = key, work, exercise
    # The owner's explicit daily flags always supersede the imported exercise,
    # including E=0 corrections, without counting the same local date twice.
    days.update({day: (work, exercise) for day, (_, work, exercise) in latest.items()})
    return days


def build_week(records: Iterable[object], week_start: str, as_of: datetime,
               repository: str = DEFAULT_REPOSITORY) -> dict:
    """Build a public board from owner check-ins and marked Activity imports.

    Dates refer to each journal's chosen IANA time zone. Latest valid state for
    a given day replaces both W and E, so corrections can also remove credit.
    Imported exercise dates grant no work credit. Old 10-point plans and
    experience approval labels never enter this score.
    """
    start = _date(week_start)
    if start is None or start.weekday() != 0:
        raise ValueError("week_start must be a Monday in YYYY-MM-DD format.")
    if (not isinstance(as_of, datetime) or as_of.tzinfo is None
            or as_of.utcoffset() is None):
        raise ValueError("as_of must be a timezone-aware datetime.")
    if not isinstance(repository, str) or not _REPOSITORY.fullmatch(repository):
        raise ValueError("repository must have the form owner/repository.")
    as_of = as_of.astimezone(timezone.utc)
    end = start + timedelta(days=6)
    rows = []
    for journal in _canonical_journals(records):
        config = _configuration(journal.issue)
        if (journal.created > as_of or journal.issue.get("state") != "open"
                or not config or not config[1]):
            continue
        zone, _ = config
        days = _checkins(journal, zone, start, end, as_of)
        if not days:
            continue
        work = sum(value[0] for value in days.values())
        exercise = sum(value[1] for value in days.values())
        rows.append({
            "handle": journal.owner.handle,
            "issue_number": journal.number,
            "issue_url": f"https://github.com/{repository}/issues/{journal.number}",
            "work_days": work,
            "exercise_days": exercise,
            "checkin_days": len(days),
            "score": score_days(work, exercise),
            "time_zone": zone.key,
        })
    rows.sort(key=lambda row: (-row["score"], row["handle"].casefold(), row["issue_number"]))
    previous_score = None
    rank = 0
    for position, row in enumerate(rows, 1):
        if row["score"] != previous_score:
            rank = position
        row["rank"] = rank
        previous_score = row["score"]
    return {
        "schema_version": SCHEMA_VERSION,
        "scoring_version": SCORING_VERSION,
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "generated_at": as_of.isoformat().replace("+00:00", "Z"),
        "participants_count": len(rows),
        "leaderboard": rows,
    }
