"""Post one editable format-status comment from a trusted Actions workflow.

Event data is parsed as JSON, never interpolated into a shell or evaluated.
This job has Issues write permission only; it cannot publish repository code.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from club.scoring import validate_submission  # noqa: E402
from scripts.github_api import GitHubReader, validate_repository  # noqa: E402

MARKER = "<!-- club-format-status:v2 -->"


def feedback_body(issue: dict, comment: dict | None = None, now: datetime | None = None) -> str | None:
    """Return fixed, safe feedback; ordinary conversation and bot events skip."""
    if not isinstance(issue, dict) or "pull_request" in issue:
        return None
    labels = {item.get("name") for item in issue.get("labels", []) if isinstance(item, dict)}
    if "weekly-plan" not in labels:
        return None
    author = issue.get("user", {}).get("login", "")
    if comment is not None:
        user = comment.get("user", {})
        if user.get("type") == "Bot" or str(user.get("login", "")).casefold() != str(author).casefold():
            return None
        if not re.match(r"\s*/", comment.get("body", "")):
            return None
    errors = validate_submission(issue, comment, now=now)
    lines = [MARKER, "### Record format check", ""]
    if errors:
        lines += ["Please edit the plan or your check-in, then try again:", ""]
        lines += [f"- {error}" for error in errors]
    else:
        lines += ["Format valid. Your latest record passed the format checks."]
    lines += ["", "This checks format, ownership, and dates. It does not verify exercise or assess health.",
              "Weekly scores refresh in the scheduled report; they are not updated by this check.",
              "All Issue content is public. Meals earn no extra points; partial/skipped sessions earn no execution points.",
              "", "格式检查只确认记录是否可识别，不代表训练或健康评价。积分由定时报告更新。"]
    return "\n".join(lines) + "\n"


def upsert_feedback(reader: GitHubReader, number: int, body: str) -> None:
    existing = next((comment for comment in reader._pages(f"issues/{number}/comments")
                     if isinstance(comment, dict)
                     and comment.get("user", {}).get("type") == "Bot"
                     and comment.get("user", {}).get("login") == "github-actions[bot]"
                     and str(comment.get("body", "")).startswith(MARKER)), None)
    if existing and existing.get("body") == body:
        return
    if existing:
        identifier = existing.get("id")
        if not isinstance(identifier, int) or isinstance(identifier, bool) or identifier < 1:
            raise ValueError("The existing format-status comment has invalid metadata.")
        path, method = f"issues/comments/{identifier}", "PATCH"
    else:
        path, method = f"issues/{number}/comments", "POST"
    request = Request(
        f"https://api.github.com/repos/{reader.repository}/{path}",
        data=json.dumps({"body": body}).encode(), method=method,
        headers={"Authorization": f"Bearer {reader._token}", "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            response.read()
    except HTTPError as error:
        raise RuntimeError(f"GitHub refused the format-status update (HTTP {error.code}).") from None
    except (URLError, TimeoutError):
        raise RuntimeError("Could not update the format-status comment.") from None


def main() -> int:
    try:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        issue = event.get("issue")
        if not isinstance(issue, dict) or event.get("sender", {}).get("type") == "Bot":
            return 0
        repository = validate_repository(os.environ["GITHUB_REPOSITORY"])
        number = issue.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            raise ValueError("Invalid Issue number.")
        if feedback_body(issue, event.get("comment")) is None:
            return 0
        reader = GitHubReader(repository, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "")
        # A queued event may contain stale form/comment text. Always validate live state.
        current = reader.get_issue(number)
        comment = event.get("comment")
        if comment is not None:
            identifier = comment.get("id")
            if not isinstance(identifier, int) or isinstance(identifier, bool) or identifier < 1:
                raise ValueError("Invalid comment number.")
            comment = reader._get(f"issues/comments/{identifier}")
        body = feedback_body(current, comment)
        if body is not None:
            upsert_feedback(reader, number, body)
        return 0
    except (OSError, KeyError, ValueError, TypeError, RuntimeError) as error:
        print(f"Format check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
