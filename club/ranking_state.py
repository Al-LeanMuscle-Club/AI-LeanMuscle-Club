"""Trusted, reviewable ranking state; never persist Issue text or food records."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from typing import Any

from club.taxonomy import SPORTS

_HASH = re.compile(r"[0-9a-f]{64}\Z")
_HANDLE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}


def new_state() -> dict[str, Any]:
    return {"schema_version": 1, "confirmed_plans": {}, "contribution_approvals": {}}


def plan_fingerprint(week: str, handle: str, user_id: int | None = None) -> str:
    """Retain a baseline after withdrawal without a public account/Issue index.

    GitHub's numeric user ID survives username changes. Missing or invalid IDs
    retain the legacy handle key for older records and synthetic fixtures.
    This is a lookup fingerprint, not a promise of anonymity: public accounts
    and weeks can be guessed. Never store descriptions or member identifiers.
    """
    if isinstance(user_id, int) and not isinstance(user_id, bool) and user_id > 0:
        identity = f"{week}:github-user-id:{user_id}"
    else:
        identity = f"{week}:{handle.casefold()}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def migrate_plan_confirmation(state: dict[str, Any], week: str, handle: str,
                              user_id: int | None) -> None:
    """Move an existing same-handle baseline to its stable ID, never create one.

    Run this even for withdrawn/recovery plans so a subsequently observed
    username change retains the baseline. An old name not observed with an ID
    cannot be recovered from its hash; do not guess between other entries.
    """
    key = plan_fingerprint(week, handle, user_id)
    legacy_key = plan_fingerprint(week, handle)
    plans = state["confirmed_plans"]
    if key != legacy_key and key not in plans and legacy_key in plans:
        plans[key] = plans.pop(legacy_key)


def body_sha256(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return instant.tzinfo is not None and instant.utcoffset() is not None
    except (ValueError, OverflowError):
        return False


def _week(value: Any) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        return date.fromisoformat(value).weekday() == 0
    except ValueError:
        return False


def clean_state(value: Any) -> dict[str, Any]:
    """Validate trusted fields and copy only an allowlist; fail closed on damage.

    Silently treating a corrupt ledger as empty would reset locked plans and
    allow a smaller denominator. Unexpected fields are deliberately discarded.
    """
    if not isinstance(value, Mapping) or value.get("schema_version") != 1:
        raise ValueError("Ranking state must have schema_version 1; restore the trusted ledger before syncing.")
    result = new_state()
    plans = value.get("confirmed_plans")
    approvals = value.get("contribution_approvals")
    if not isinstance(plans, Mapping) or not isinstance(approvals, Mapping):
        raise ValueError("Ranking state must contain confirmed_plans and contribution_approvals objects.")
    for key, entry in plans.items():
        if (not isinstance(key, str) or not _HASH.fullmatch(key) or not isinstance(entry, Mapping)
                or not _timestamp(entry.get("confirmed_at"))):
            raise ValueError("Ranking state contains an invalid plan confirmation.")
        sessions = entry.get("sessions")
        if not isinstance(sessions, list) or not 1 <= len(sessions) <= 14:
            raise ValueError("A plan confirmation needs 1–14 structured sessions.")
        clean_sessions = []
        seen = set()
        for session in sessions:
            if (not isinstance(session, Mapping) or not isinstance(session.get("id"), str)
                    or not re.fullmatch(r"S[1-9][0-9]?", session["id"])
                    or session["id"] in seen or session.get("day") not in _DAYS
                    or session.get("sport") not in SPORTS or not isinstance(session.get("fallback"), bool)):
                raise ValueError("Ranking state contains an invalid confirmed session.")
            seen.add(session["id"])
            clean_sessions.append({field: session[field] for field in ("id", "day", "sport", "fallback")})
        result["confirmed_plans"][key] = {"confirmed_at": entry["confirmed_at"], "sessions": clean_sessions}
    for key, entry in approvals.items():
        if (not isinstance(key, str) or not re.fullmatch(r"[1-9][0-9]*", key)
                or not isinstance(entry, Mapping) or not isinstance(entry.get("author"), str)
                or not _HANDLE.fullmatch(entry["author"]) or not _week(entry.get("week_start"))
                or not isinstance(entry.get("body_sha256"), str) or not _HASH.fullmatch(entry["body_sha256"])
                or not _timestamp(entry.get("approved_at"))):
            raise ValueError("Ranking state contains an invalid contribution approval.")
        result["contribution_approvals"][key] = {
            field: entry[field] for field in ("author", "week_start", "body_sha256", "approved_at")
        }
    return result


def load_state(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return new_state()
    except (ValueError, UnicodeError):
        raise ValueError("Ranking state is unreadable; restore the trusted ledger before syncing.") from None
    return clean_state(value)


def save_state(path: Path, state: Mapping[str, Any]) -> None:
    """Atomically save the allowlist, leaving an existing ledger intact on error."""
    safe = clean_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                prefix=".ranking-state-", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            json.dump(safe, stream, indent=2, sort_keys=True, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def approve_contribution(issue: Mapping[str, Any], state: dict[str, Any], now: datetime) -> None:
    """Explicit local maintainer action; labels alone never create an approval."""
    from club.scoring import _handle, _labels, _sections, _timestamp as parse_timestamp

    safe = clean_state(state)
    number = issue.get("number")
    author = _handle(issue)
    fields = _sections(issue.get("body"))
    created = parse_timestamp(issue.get("created_at"))
    if (not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None
            or not isinstance(number, int) or isinstance(number, bool) or number < 1
            or "pull_request" in issue or not {"experience", "points-approved"}.issubset(_labels(issue))
            or author is None or fields is None or not _week(fields.get("Week starting"))
            or created is None or created > now):
        raise ValueError("Approve a valid experience Issue with both experience/points-approved labels, an author, and a selected Monday.")
    safe["contribution_approvals"][str(number)] = {
        "author": author.casefold(), "week_start": fields["Week starting"],
        "body_sha256": body_sha256(issue["body"]),
        "approved_at": now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    state.clear()
    state.update(safe)
