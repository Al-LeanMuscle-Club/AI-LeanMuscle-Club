"""Decide whether an event can change public participation reports.

This guard is intentionally conservative: scheduled/manual runs and Issue
deletions always reconcile. A format change or label removal must not be
silently filtered out. Untrusted Issue text is never executed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


RELEVANT_LABELS = {"weekly-plan", "experience", "points-approved"}


def should_refresh(event_name: str, event: dict) -> bool:
    if event_name not in {"issues", "issue_comment"}:
        return True
    issue = event.get("issue")
    if not isinstance(issue, dict) or "pull_request" in issue:
        return False
    labels = {
        label.get("name") for label in issue.get("labels", [])
        if isinstance(label, dict)
    }
    if event_name == "issue_comment":
        # Only weekly-plan comment commands affect reports; a normal
        # conversation/experience Issue reply does not.
        return "weekly-plan" in labels
    if event.get("action") == "deleted":
        # The removed Issue's previous labels may be unavailable.
        return True
    changed = event.get("label") or {}
    return bool(RELEVANT_LABELS & labels) or changed.get("name") in RELEVANT_LABELS


def main() -> None:
    path = os.environ["GITHUB_EVENT_PATH"]
    event = json.loads(Path(path).read_text(encoding="utf-8"))
    result = "true" if should_refresh(os.environ.get("GITHUB_EVENT_NAME", ""), event) else "false"
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
        stream.write(f"run={result}\n")


if __name__ == "__main__":
    main()
