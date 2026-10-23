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

from club.taxonomy import GOALS, RESEARCH_WEEKS, SPORTS


_DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
_HANDLE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
_HEADING = re.compile(r"^###[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_SESSION_PREFIX = re.compile(r"^(?:-[ \t]+(?:\[[ xX]\][ \t]+)?)?")
_SESSION_ID = re.compile(r"S[1-9][0-9]?\Z", re.IGNORECASE)
_CHECK_IN = re.compile(
    r"/(done|fallback|partial|skip)[ \t]+(S[1-9][0-9]?)[ \t]+(\d{4}-\d{2}-\d{2})"
    r"(?:[ \t]*\|[^\r\n]*)?[ \t]*\Z",
    re.IGNORECASE,
)
_MEAL = re.compile(
    r"/meal[ \t]+(\d{4}-\d{2}-\d{2})(?:[ \t]*\|[^\r\n]*)?[ \t]*\Z",
    re.IGNORECASE,
)
_COMMAND = re.compile(r"/(?:done|fallback|partial|skip|meal|review|pause)(?:\s|$)", re.IGNORECASE)
_WEEKDAYS = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
}


@dataclass(frozen=True)
class _Session:
    id: str
    day: str
    sport: str
    fallback: bool


@dataclass(frozen=True)
class _Plan:
    handle: str
    number: int
    url: str
    created_at: datetime
    time_zone: ZoneInfo
    mode: str
    public: bool
    sessions: tuple[_Session, ...]
    comments: tuple[Any, ...]
    goal: str
    research_week: str


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


def _session_rows(raw: str) -> tuple[_Session, ...] | None:
    """Parse legacy three-column rows or explicit sport/fallback rows.

    Free-form descriptions and fallback text never leave the input record.
    The stored fallback boolean confirms only a declared alternative exists;
    this honor-based pilot does not freeze historical edits to a plan.
    """
    sessions: list[_Session] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        if not line.strip():
            continue
        columns = [part.strip() for part in _SESSION_PREFIX.sub("", line.strip(), count=1).split("|")]
        if len(columns) not in {3, 4, 5}:
            return None
        session_id, day = columns[:2]
        if not _SESSION_ID.fullmatch(session_id) or day.casefold() not in _WEEKDAYS:
            return None
        session_id = session_id.upper()
        if session_id in seen:
            return None
        sport, description = ("other", columns[2]) if len(columns) == 3 else (columns[2].casefold(), columns[3])
        if sport not in SPORTS or not description:
            return None
        fallback = len(columns) == 5 and bool(columns[4]) and columns[4] != "_No response_"
        seen.add(session_id)
        sessions.append(_Session(session_id, day.title(), sport, fallback))
    if not 1 <= len(sessions) <= 14:
        return None
    return tuple(sessions)


def _parse_plan(issue: Mapping[str, Any], week: str, as_of: datetime) -> tuple[_Plan | None, list[str]]:
    sections = _sections(issue.get("body"))
    if sections is None:
        return None, ["Use unique Issue form headings; duplicate headings are ambiguous."]
    if sections.get("Week starting") != week:
        return None, ["Week starting must match the selected Monday in YYYY-MM-DD format."]
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
        or "pull_request" in issue
    ):
        return None, ["A plan needs valid GitHub Issue metadata and a creation time no later than now."]
    url = _issue_url(issue.get("html_url"), number)
    if url is None:
        return None, ["The plan must have a valid HTTPS GitHub Issue URL."]
    zone_name = sections.get("Time zone", "")
    if not zone_name or len(zone_name) > 100:
        return None, ["Time zone must be an IANA name, such as Asia/Shanghai."]
    try:
        zone = ZoneInfo(zone_name)
    except (ZoneInfoNotFoundError, ValueError):
        return None, ["Time zone must be an IANA name, such as Asia/Shanghai."]
    mode = sections.get("Participation mode")
    visibility = sections.get("Public leaderboard")
    if mode not in {"Active", "Recovery"}:
        return None, ["Participation mode must be Active or Recovery."]
    if visibility not in {"Yes", "No"}:
        return None, ["Public leaderboard must be Yes or No; all Issue content remains public."]
    goal = sections.get("Primary goal", "habit").casefold()
    research_week = sections.get("Research week", "regular").casefold()
    if goal in {"", "_no response_"}:
        goal = "habit"
    if research_week in {"", "_no response_"}:
        research_week = "regular"
    if goal not in GOALS:
        return None, ["Primary goal must be fat-loss, muscle-gain, cardio, skill, or habit."]
    if research_week not in RESEARCH_WEEKS:
        return None, ["Research week must be regular, deadline, or travel."]
    sessions: tuple[_Session, ...] = ()
    if mode == "Active":
        parsed = _session_rows(sections.get("Planned sessions", ""))
        if parsed is None:
            return None, [
                "Use 1–14 unique sessions: S1 | Monday | sport | description | optional fallback. "
                "Sport must be strength, basketball, running, swimming, cycling, walking, mobility, or other. "
                "Legacy S1 | Monday | description rows are also accepted."
            ]
        sessions = parsed
    raw_comments = issue.get("comments_data", [])
    comments = tuple(raw_comments) if isinstance(raw_comments, list) else ()
    return _Plan(
        handle, number, url, created, zone, mode, visibility == "Yes", sessions,
        comments, goal, research_week,
    ), []


def _plan(issue: Mapping[str, Any], week: str, as_of: datetime) -> _Plan | None:
    return _parse_plan(issue, week, as_of)[0]


def _parse_comment(
    plan: _Plan, comment: Mapping[str, Any], start: date, as_of: datetime,
) -> tuple[dict[str, Any] | None, list[str]]:
    author = _handle(comment)
    created = _timestamp(comment.get("created_at"))
    effective = _timestamp(comment.get("updated_at")) if "updated_at" in comment else created
    body = comment.get("body")
    if author is None or author.casefold() != plan.handle.casefold():
        return None, ["Only the plan author can record its training, meals, reflection, or pause."]
    if (
        created is None or effective is None or created < plan.created_at
        or effective < created or created > as_of or effective > as_of
    ):
        return None, ["The comment creation and edit times must be valid and no later than now."]
    if not isinstance(body, str):
        return None, ["Write one command on the first nonempty line of the comment."]
    body = body.replace("\r\n", "\n").replace("\r", "\n").strip()
    lines = body.splitlines()
    if not lines or any(_COMMAND.match(line.strip()) for line in lines[1:]):
        return None, ["Write exactly one command per comment, on its first nonempty line."]
    first = lines[0].strip()
    event: dict[str, Any] = {"effective_at": effective, "id": comment.get("id")}
    if re.fullmatch(r"/pause(?:[ \t]+.*)?", first, re.IGNORECASE):
        return {**event, "kind": "pause"}, []
    if re.fullmatch(r"/review[ \t]*", first, re.IGNORECASE):
        reflection = "\n".join(lines[1:]).strip()
        if not reflection or reflection == "_No response_":
            return None, ["Add a short reflection on a new line after /review."]
        return {**event, "kind": "review"}, []
    check_in = _CHECK_IN.fullmatch(first)
    meal = _MEAL.fullmatch(first)
    if check_in is None and meal is None:
        return None, [
            "Use /done, /fallback, /partial, or /skip followed by a session ID and YYYY-MM-DD; "
            "or /meal YYYY-MM-DD, /review, or /pause."
        ]
    kind = check_in.group(1).casefold() if check_in else "meal"
    logged_day = _iso_date(check_in.group(3) if check_in else meal.group(1))
    if (
        logged_day is None or not start <= logged_day < start + timedelta(days=7)
        or logged_day > as_of.astimezone(plan.time_zone).date()
        or logged_day > effective.astimezone(plan.time_zone).date()
    ):
        return None, ["The actual date must be within the plan week and not in the future in the plan's time zone."]
    if check_in:
        session_id = check_in.group(2).upper()
        session = next((s for s in plan.sessions if s.id == session_id), None)
        if session is None:
            return None, ["Use a session ID that exists in your current plan."]
        if kind == "fallback" and not session.fallback:
            return None, ["Declare that session's fallback in the fifth plan column before using /fallback."]
        event["session_id"] = session_id
    return {**event, "kind": kind, "date": logged_day.isoformat()}, []


def validate_submission(
    issue: Mapping[str, Any], comment_body: str | Mapping[str, Any] | None = None,
    *, now: datetime | None = None,
) -> list[str]:
    """Validate a plan and optionally a proposed or actual comment.

    A string comment is a preview, attributed to the plan author at ``now``.
    Pass the actual GitHub comment Mapping to validate ownership and its true
    timestamps. Messages are fixed text and never echo member-provided content.
    Existing comments and leaderboard consent do not restrict this preflight.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() != timedelta(0):
        return ["Validation needs a timezone-aware UTC time."]
    if not isinstance(issue, Mapping):
        return ["A valid GitHub weekly-plan Issue is required."]
    sections = _sections(issue.get("body"))
    week = sections.get("Week starting") if sections else None
    start = _iso_date(week)
    if start is None or start.weekday() != 0:
        return ["Week starting must be a Monday in YYYY-MM-DD format."]
    plan, errors = _parse_plan(issue, week, now)
    if errors or plan is None:
        return errors
    if comment_body is None:
        return []
    if isinstance(comment_body, str):
        comment: Mapping[str, Any] = {
            "body": comment_body, "user": {"login": plan.handle},
            "created_at": now.isoformat(),
        }
    elif isinstance(comment_body, Mapping):
        comment = comment_body
    else:
        return ["A comment must be text or a GitHub comment record."]
    return _parse_comment(plan, comment, start, now)[1]


def _activity(
    plan: _Plan, start: date, as_of: datetime,
) -> tuple[list[dict[str, Any]], bool, bool]:
    states: dict[str, dict[str, Any]] = {}
    latest: dict[str, tuple[datetime, int]] = {}
    reviewed = False
    paused = False
    for index, comment in enumerate(plan.comments):
        if not isinstance(comment, Mapping):
            continue
        event, _ = _parse_comment(plan, comment, start, as_of)
        if event is None:
            continue
        if event["kind"] == "pause":
            paused = True
        elif event["kind"] == "review":
            reviewed = True
        elif event["kind"] != "meal":
            session_id = event["session_id"]
            identifier = event.get("id")
            order = (event["effective_at"], identifier if isinstance(identifier, int) and not isinstance(identifier, bool) else index)
            if session_id not in latest or order > latest[session_id]:
                latest[session_id] = order
                states[session_id] = {
                    "status": {"done": "completed", "fallback": "fallback", "partial": "partial", "skip": "skipped"}[event["kind"]],
                    "date": event["date"],
                    "used_fallback": event["kind"] == "fallback",
                }
    return [
        {"id": session.id, "day": session.day, "sport": session.sport,
         **states.get(session.id, {"status": "planned", "date": None, "used_fallback": False})}
        for session in plan.sessions
    ], reviewed, paused


def build_week(
    issues: Iterable[Any], week_start: str, as_of: datetime,
) -> dict[str, Any]:
    """Return a JSON-serializable weekly board and anonymous participation counts.

    ``as_of`` must be a timezone-aware UTC datetime. Only valid plans for the
    selected Monday are considered. A member's earliest valid plan wins; later
    duplicates never add points. All dates in check-ins are interpreted in the
    participant's declared IANA time zone. Future-dated declarations are ignored
    both relative to ``as_of`` and to the comment's effective date (its edit
    timestamp when provided, otherwise its creation timestamp). A current body
    edited after ``as_of`` is ignored because its past text is unavailable.
    A command must be on the first nonempty comment line; trailing notes and
    image Markdown are allowed. Comments with additional command lines are
    ignored rather than interpreting multiple actions from one comment.

    ``completion_rate`` is a fraction in [0, 1]. ``participants_count`` includes
    valid opt-outs and recovery/paused participants; ``recovery_count`` includes
    both Recovery mode and an author-issued ``/pause``. Only explicitly opted-in
    active participants appear in ``leaderboard`` and category summaries. Raw
    descriptions, food logs, and training metrics are never republished. Warnings
    contain no names, issue numbers, URLs, or member-provided text. The latest
    valid session status wins; full and fallback completions share one cap.
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
        sessions, reviewed, paused = _activity(plan, start, as_of)
        if plan.mode == "Recovery" or paused:
            recovery_count += 1
            continue
        if not plan.public:
            continue
        count = sum(s["status"] in {"completed", "fallback"} for s in sessions)
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
            "goal": plan.goal,
            "research_week": plan.research_week,
            "sports": sorted({s.sport for s in plan.sessions}),
            "partial": sum(s["status"] == "partial" for s in sessions),
            "skipped": sum(s["status"] == "skipped" for s in sessions),
            "sessions": sessions,
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
    sports = []
    for sport in SPORTS:
        selected = [session for row in rows for session in row["sessions"] if session["sport"] == sport]
        if selected:
            sports.append({"sport": sport, "planned": len(selected),
                           "completed": sum(session["status"] in {"completed", "fallback"} for session in selected)})
    return {
        "schema_version": 2,
        "summary": {
            "public_members": len(rows),
            "planned_sessions": sum(row["planned"] for row in rows),
            "completed_sessions": sum(row["completed"] for row in rows),
            "partial_sessions": sum(row["partial"] for row in rows),
            "skipped_sessions": sum(row["skipped"] for row in rows),
            "reviewed_members": sum(bool(row["review_points"]) for row in rows),
        },
        "sports": sports,
        "week_start": week_start,
        "generated_at": as_of.isoformat().replace("+00:00", "Z"),
        "participants_count": len(plans),
        "recovery_count": recovery_count,
        "leaderboard": rows,
        "warnings": warnings,
    }
