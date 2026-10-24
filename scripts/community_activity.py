"""Anonymous counts of genuine community posts and replies, independent of points.

A week is Monday 00:00 through the next Monday 00:00 UTC. New posts use the
Issue creation time, not an activity date in its body; replies use their own
creation time, including replies to older threads. No member text or identity
is included in the returned public snapshot.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import re

from club.community import community_category

COUNT_FIELDS = (
    "participants_count", "posts_count", "replies_count", "responded_posts_count",
    "activity_records", "meal_records", "experiences", "conversations", "weekly_plan_posts",
)
CATEGORY_FIELDS = {
    "activity-record": "activity_records", "meal-record": "meal_records",
    "experience": "experiences", "weekly-plan": "weekly_plan_posts",
}


def _instant(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if result.tzinfo is None or result.utcoffset() is None:
        return None
    return result.astimezone(timezone.utc)


def _human(user: object) -> tuple[str, object] | None:
    if not isinstance(user, dict) or user.get("type") not in (None, "User"):
        return None
    login = user.get("login")
    if not isinstance(login, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", login):
        return None
    identifier = user.get("id")
    if type(identifier) is int and identifier > 0:
        return ("id", identifier)
    return ("login", login.casefold())


def build_community_activity(records: list, week_start: str, as_of: datetime) -> dict:
    monday = date.fromisoformat(week_start)
    if monday.isoformat() != week_start or monday.weekday() != 0:
        raise ValueError("Community activity week must be a Monday YYYY-MM-DD.")
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("Community activity cutoff must include a time zone.")
    start = datetime.combine(monday, time.min, timezone.utc)
    end = start + timedelta(days=7)
    result = {"schema_version": 1, "timezone": "UTC", **dict.fromkeys(COUNT_FIELDS, 0)}
    participants = set()
    seen_issues = set()
    for issue in records:
        if not isinstance(issue, dict):
            continue
        number = issue.get("number")
        if type(number) is not int or number < 1 or number in seen_issues:
            continue
        seen_issues.add(number)
        category = community_category(issue)
        author = _human(issue.get("user"))
        created = _instant(issue.get("created_at"))
        if category is None or author is None or created is None or created > as_of:
            continue
        posted_this_week = start <= created < end
        if posted_this_week:
            participants.add(author)
            result["posts_count"] += 1
            result[CATEGORY_FIELDS.get(category, "conversations")] += 1
        responded = False
        seen_comments = set()
        comments = issue.get("comments_data", [])
        if not isinstance(comments, list):
            comments = []
        for comment in comments:
            if not isinstance(comment, dict):
                continue
            identifier = comment.get("id")
            if type(identifier) is int and identifier > 0:
                if identifier in seen_comments:
                    continue
                seen_comments.add(identifier)
            commenter = _human(comment.get("user"))
            sent = _instant(comment.get("created_at"))
            body = comment.get("body")
            if (commenter is None or sent is None or sent < created or sent > as_of
                    or not isinstance(body, str) or not body.strip()):
                continue
            if commenter != author:
                responded = True
            if start <= sent < end:
                participants.add(commenter)
                result["replies_count"] += 1
        if posted_this_week and responded:
            result["responded_posts_count"] += 1
    result["participants_count"] = len(participants)
    return result


def public_community_activity(value: object) -> dict | None:
    """Allowlist complete aggregate snapshots; legacy data has no false zeros."""
    if not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("timezone") != "UTC":
        return None
    if any(type(value.get(key)) is not int or value[key] < 0 for key in COUNT_FIELDS):
        return None
    return {"schema_version": 1, "timezone": "UTC", **{key: value[key] for key in COUNT_FIELDS}}
