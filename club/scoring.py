"""Compute a weekly, opt-in participation board from GitHub issue records.

The score measures self-reported follow-through and reflection. It does not
measure exercise quality, physical fitness, effort, or health. This module does
not call a model, execute member-supplied content, or infer completed exercise.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import re
from typing import Any
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
_HANDLE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
_HEADING = re.compile(r"^###[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_SESSION = re.compile(
    r"(?:-[ \t]+(?:\[[ xX]\][ \t]+)?)?"
    r"(S[1-9][0-9]?)[ \t]*\|[ \t]*([A-Za-z]+)[ \t]*\|[ \t]*(.+)\Z",
    re.IGNORECASE,
)
_DONE = re.compile(
    r"/done[ \t]+(S[1-9][0-9]?)[ \t]+(\d{4}-\d{2}-\d{2})"
    r"(?:[ \t]*\|[^\r\n]*)?[ \t]*\Z",
    re.IGNORECASE,
)
_WEEKDAYS = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
}


@dataclass(frozen=True)
class _Plan:
    handle: str
    number: int
    url: str
    created_at: datetime
    time_zone: ZoneInfo
    mode: str
    public: bool
    sessions: frozenset[str]
    comments: tuple[Any, ...]


def _iso_date(value: Any) -> date | None:
    if not isinstance(value, str) or not _DATE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def _handle(record: Mapping[str, Any]) -> str | None:
    user = record.get("user")
    value = user.get("login") if isinstance(user, Mapping) else None
    return value if isinstance(value, str) and _HANDLE.fullmatch(value) else None


def _labels(issue: Mapping[str, Any]) -> set[str]:
    labels = issue.get("labels", [])
    if not isinstance(labels, list):
        return set()
    return {
        label["name"]
        for label in labels
        if isinstance(label, Mapping) and isinstance(label.get("name"), str)
    }


def _sections(body: Any) -> dict[str, str] | None:
    if not isinstance(body, str):
        return None
    # GitHub form submissions may use CRLF, including on the heading lines.
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    matches = list(_HEADING.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(1)
        if heading in sections:
            return None
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[heading] = body[match.end():end].strip()
    return sections


def _issue_url(value: Any, number: int) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or parsed.netloc != "github.com"
            or parsed.query
            or parsed.fragment
            or not re.fullmatch(
                rf"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/{number}", parsed.path
            )
        ):
            return None
    except ValueError:
        return None
    return value


def _plan(issue: Mapping[str, Any], week: str, as_of: datetime) -> _Plan | None:
    sections = _sections(issue.get("body"))
    if sections is None or sections.get("Week starting") != week:
        return None
    handle = _handle(issue)
    number = issue.get("number")
    created = _timestamp(issue.get("created_at"))
    if (
        handle is None
        or not isinstance(number, int)
        or isinstance(number, bool)
        or number < 1
        or created is None
        or created > as_of
    ):
        return None
    url = _issue_url(issue.get("html_url"), number)
    if url is None:
        return None
    zone_name = sections.get("Time zone", "")
    if not zone_name or len(zone_name) > 100:
        return None
    try:
        zone = ZoneInfo(zone_name)
    except (ZoneInfoNotFoundError, ValueError):
        return None
    mode = sections.get("Participation mode")
    visibility = sections.get("Public leaderboard")
    if mode not in {"Active", "Recovery"} or visibility not in {"Yes", "No"}:
        return None
    sessions: set[str] = set()
    if mode == "Active":
        raw_sessions = sections.get("Planned sessions", "")
        for line in raw_sessions.splitlines():
            if not line.strip():
                continue
            match = _SESSION.fullmatch(line.strip())
            if not match or match.group(2).casefold() not in _WEEKDAYS:
                return None
            session_id = match.group(1).upper()
            if session_id in sessions or not match.group(3).strip():
                return None
            sessions.add(session_id)
        if not 1 <= len(sessions) <= 14:
            return None
    raw_comments = issue.get("comments_data", [])
    comments = tuple(raw_comments) if isinstance(raw_comments, list) else ()
    return _Plan(
        handle, number, url, created, zone, mode, visibility == "Yes",
        frozenset(sessions), comments,
    )


def _activity(plan: _Plan, start: date, as_of: datetime) -> tuple[set[str], bool, bool]:
    completed: set[str] = set()
    reviewed = False
    paused = False
    local_today = as_of.astimezone(plan.time_zone).date()
    for comment in plan.comments:
        if not isinstance(comment, Mapping):
            continue
        author = _handle(comment)
        created = _timestamp(comment.get("created_at"))
        body = comment.get("body")
        if (
            author is None
            or author.casefold() != plan.handle.casefold()
            or created is None
            or created > as_of
            or created < plan.created_at
            or not isinstance(body, str)
        ):
            continue
        body = body.replace("\r\n", "\n").replace("\r", "\n").strip()
        lines = body.splitlines()
        if not lines:
            continue
        # One command per comment. Ordinary trailing notes and photo Markdown
        # are welcome, but a second command line makes the whole comment
        # ambiguous and must not grant extra points or pause participation.
        if any(
            re.match(r"/(?:done|review|pause)(?:\s|$)", line.strip(), re.IGNORECASE)
            for line in lines[1:]
        ):
            continue
        if re.match(r"/pause(?:\s|$)", body):
            paused = True
        if re.fullmatch(r"/review[ \t]*\n[\s\S]+", body):
            reflection = body.split("\n", 1)[1].strip()
            if reflection and reflection != "_No response_":
                reviewed = True
        done = _DONE.fullmatch(lines[0].strip())
        if done:
            session_id = done.group(1).upper()
            logged_day = _iso_date(done.group(2))
            if (
                session_id in plan.sessions
                and logged_day is not None
                and start <= logged_day < start + timedelta(days=7)
                and logged_day <= local_today
                and logged_day <= created.astimezone(plan.time_zone).date()
            ):
                completed.add(session_id)
    return completed, reviewed, paused


def build_week(
    issues: Iterable[Any], week_start: str, as_of: datetime,
) -> dict[str, Any]:
    """Return a JSON-serializable weekly board and anonymous participation counts.

    ``as_of`` must be a timezone-aware UTC datetime. Only valid plans for the
    selected Monday are considered. A member's earliest valid plan wins; later
    duplicates never add points. All dates in check-ins are interpreted in the
    participant's declared IANA time zone. Future-dated declarations are ignored
    both relative to ``as_of`` and to the comment's actual creation date.
    A command must be on the first nonempty comment line; trailing notes and
    image Markdown are allowed. Comments with additional command lines are
    ignored rather than interpreting multiple actions from one comment.

    ``completion_rate`` is a fraction in [0, 1]. ``participants_count`` includes
    valid opt-outs and recovery/paused participants; ``recovery_count`` includes
    both Recovery mode and an author-issued ``/pause``. Only explicitly opted-in
    active participants appear in ``leaderboard``. Warnings contain no names,
    issue numbers, URLs, or member-provided text.
    """
    start = _iso_date(week_start)
    if start is None or start.weekday() != 0:
        raise ValueError("week_start must be a Monday in YYYY-MM-DD format")
    if (
        not isinstance(as_of, datetime)
        or as_of.tzinfo is None
        or as_of.utcoffset() != timedelta(0)
    ):
        raise ValueError("as_of must be a timezone-aware UTC datetime")
    as_of = as_of.astimezone(timezone.utc)
    warnings: list[str] = []

    def warn(message: str) -> None:
        if message not in warnings:
            warnings.append(message)

    plans: dict[str, _Plan] = {}
    contributions: set[str] = set()
    for issue in issues:
        if not isinstance(issue, Mapping) or "pull_request" in issue:
            continue
        labels = _labels(issue)
        sections = _sections(issue.get("body"))
        if "weekly-plan" in labels:
            # Ignore other weeks, but report malformed records generically.
            if sections is not None and sections.get("Week starting") != week_start:
                continue
            plan = _plan(issue, week_start, as_of)
            if plan is None:
                warn("A weekly plan was skipped because required fields were invalid.")
            else:
                key = plan.handle.casefold()
                previous = plans.get(key)
                if previous is not None:
                    warn("Duplicate weekly plans were found; only the earliest valid plan counts.")
                if previous is None or (plan.created_at, plan.number) < (
                    previous.created_at, previous.number
                ):
                    plans[key] = plan
        if {"experience", "points-approved"}.issubset(labels):
            handle = _handle(issue)
            created = _timestamp(issue.get("created_at"))
            if (
                handle is not None
                and sections is not None
                and sections.get("Week starting") == week_start
                and created is not None
                and created <= as_of
            ):
                contributions.add(handle.casefold())

    rows: list[dict[str, Any]] = []
    recovery_count = 0
    for key, plan in plans.items():
        completed, reviewed, paused = _activity(plan, start, as_of)
        if plan.mode == "Recovery" or paused:
            recovery_count += 1
            continue
        if not plan.public:
            continue
        count = len(completed)
        planned = len(plan.sessions)
        execution = (Decimal(6) * count / planned).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        review = 2 if reviewed else 0
        contribution = 1 if key in contributions else 0
        total = Decimal(1 + review + contribution) + execution
        rows.append({
            "rank": 0,
            "handle": plan.handle,
            "issue_number": plan.number,
            "issue_url": plan.url,
            "planned": planned,
            "completed": count,
            "completion_rate": round(count / planned, 6),
            "plan_points": 1,
            "execution_points": float(execution),
            "review_points": review,
            "contribution_points": contribution,
            "total_points": float(total),
        })
    rows.sort(key=lambda row: (
        -row["total_points"], -row["completion_rate"], row["handle"].casefold()
    ))
    previous_score: float | None = None
    rank = 0
    for position, row in enumerate(rows, 1):
        if row["total_points"] != previous_score:
            rank = position
        row["rank"] = rank
        previous_score = row["total_points"]
    return {
        "week_start": week_start,
        "generated_at": as_of.isoformat().replace("+00:00", "Z"),
        "participants_count": len(plans),
        "recovery_count": recovery_count,
        "leaderboard": rows,
        "warnings": warnings,
    }
