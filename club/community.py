"""Recognize declared community records without inferring activity from prose.

Classification is for discovery and aggregate participation, never scoring or
approval. Published examples, pull requests, and bot posts are not members.
"""

from __future__ import annotations

import re


RECORD_LABELS = frozenset({"weekly-plan", "activity-record", "meal-record", "experience"})
_FORMS = {
    "weekly-plan": ("[Plan]", {"Week starting", "Time zone", "Participation mode", "Public leaderboard", "Planned sessions"}),
    "activity-record": ("[Activity]", {"Activity date", "Time zone", "Sport", "What I did"}),
    "meal-record": ("[Meal]", {"Meal date", "Time zone", "Food and context"}),
    "experience": ("[Experience]", {"Context", "What I tried", "What happened"}),
    "beginners": ("[Hello]", {"A short introduction", "What I would like to try", "How members can help"}),
    "training-and-recovery": ("[Training]", {"Question or experience", "Context and what I tried", "Feedback I would find useful"}),
    "nutrition": ("[Food]", {"Meal or question", "Optional food context", "Optional estimate and source"}),
    "buddies-and-events": ("[Buddies]", {"Activity or invitation", "General availability", "How to join"}),
    "research-and-agents": ("[Research / Agent]", {"Task and workflow", "Checking and rework", "Outcome and limits"}),
    "announcements": ("[Club]", {"Announcement", "What members need to do"}),
}
_EXAMPLE_PREFIX = re.compile(
    r"^\s*(?:\[(?:Plan|Activity|Meal|Experience|Hello|Training|Food|Buddies|Research / Agent|Club)\]\s*)?"
    r"(?:\[Fictional example(?:\s*\||\])|[\[【〖](?:虚构示例|虚构演示)(?:[｜|\]】〗]))",
    re.IGNORECASE,
)
_EXAMPLE_MARKER = re.compile(r"<!--\s*club-example:[A-Za-z0-9:_-]+\s*-->")


def label_names(issue: dict) -> set[str]:
    labels = issue.get("labels", [])
    if not isinstance(labels, list):
        return set()
    return {label["name"].casefold() for label in labels
            if isinstance(label, dict) and isinstance(label.get("name"), str)}


def is_example(issue: object) -> bool:
    if not isinstance(issue, dict):
        return False
    title, body = issue.get("title"), issue.get("body")
    return ("example" in label_names(issue)
            or bool(isinstance(title, str) and _EXAMPLE_PREFIX.search(title))
            or bool(isinstance(body, str) and _EXAMPLE_MARKER.search(body)))


def _human_issue(issue: object) -> bool:
    if not isinstance(issue, dict) or "pull_request" in issue:
        return False
    user = issue.get("user")
    if not isinstance(user, dict):
        return False
    login = user.get("login")
    return (isinstance(login, str) and bool(login.strip())
            and user.get("type") != "Bot" and not login.casefold().endswith("[bot]"))


def _form_category(issue: dict) -> str | None:
    title, body = issue.get("title"), issue.get("body")
    if not isinstance(title, str) or not isinstance(body, str):
        return None
    # Headings preserve the GitHub form's stable field names. We do not parse
    # free text as commands, read external links, or infer exercise outcomes.
    headings = set(re.findall(r"^### ([^\r\n]+?)\s*$", body, re.MULTILINE))
    for category, (prefix, required) in _FORMS.items():
        if title.lstrip().startswith(prefix) and required <= headings:
            return category
    return None


def inferred_labels(issue: object) -> set[str]:
    """Conservative additive labels for a maintainer-requested backfill.

    A form title alone is insufficient. Examples receive only `example`, even
    when their text includes a scoring form. Existing record classifications
    are not overridden, and contribution approval is never inferred.
    """
    if not _human_issue(issue):
        return set()
    if is_example(issue):
        return {"example"}
    category = _form_category(issue)
    existing = label_names(issue) & RECORD_LABELS
    if category in RECORD_LABELS and (not existing or existing == {category}):
        return {category}
    return set()


def community_category(issue: object) -> str | None:
    """Return one declared category for aggregate community statistics."""
    if not _human_issue(issue) or is_example(issue):
        return None
    existing = label_names(issue) & RECORD_LABELS
    if existing:
        return next(iter(existing)) if len(existing) == 1 else None
    return _form_category(issue)
