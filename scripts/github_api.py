"""Small GitHub REST reader; no third-party dependencies or member code execution."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def validate_repository(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("Repository must have the form owner/repository.")
    return value


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if instant.tzinfo is None or instant.utcoffset() is None:
        return None
    return instant.astimezone(timezone.utc)


def _iso(instant: datetime) -> str:
    return instant.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _names(issue: dict) -> set[str]:
    labels = issue.get("labels", [])
    if not isinstance(labels, list):
        return set()
    return {label.get("name") for label in labels if isinstance(label, dict) and isinstance(label.get("name"), str)}


def _number(issue: object) -> int:
    number = issue.get("number") if isinstance(issue, dict) else None
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        raise RuntimeError("Malformed GitHub issue response.")
    return number


def _week(issue: dict) -> str | None:
    body = issue.get("body") or ""
    if not isinstance(body, str):
        return None
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    match = re.search(r"^### Week starting[ \t]*\n\s*(\d{4}-\d{2}-\d{2})[ \t]*(?:\n|$)", body, re.MULTILINE)
    return match.group(1) if match else None


def _load_cache(path: Path, repository: str, now: datetime) -> dict | None:
    """A missing, corrupt, incompatible, or foreign cache triggers a fresh read."""
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(cached, dict) or cached.get("schema_version") != 1 or cached.get("repository") != repository:
        return None
    last = _timestamp(cached.get("last_sync"))
    full = _timestamp(cached.get("full_sync"))
    if last is None or full is None or full > last or last > now:
        return None
    issues, comments = cached.get("issues"), cached.get("comments")
    if not isinstance(issues, dict) or not isinstance(comments, dict):
        return None
    for key, issue in issues.items():
        try:
            if key != str(_number(issue)):
                return None
        except RuntimeError:
            return None
    for key, value in comments.items():
        if key not in issues or not isinstance(value, dict) or not isinstance(value.get("data"), list):
            return None
    return cached


def _save_cache(path: Path, cache: dict) -> None:
    """Publish only complete reads, with private file permissions and no token."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary: str | None = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=".club-cache-", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            json.dump(cache, stream, ensure_ascii=False, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


class GitHubReader:
    def __init__(self, repository: str, token: str):
        self.repository = validate_repository(repository)
        if not token:
            raise ValueError("Set GH_TOKEN or GITHUB_TOKEN locally; Actions supplies its own token.")
        self._token = token

    def _get(self, path: str, params: dict | None = None):
        url = f"https://api.github.com/repos/{self.repository}/{path}"
        if params:
            url += "?" + urlencode(params)
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AI-Lean-Muscle-Club-participation-reports",
        }
        for attempt in range(3):
            try:
                with urlopen(Request(url, headers=headers), timeout=30) as response:
                    try:
                        return json.load(response)
                    except (ValueError, UnicodeDecodeError):
                        raise RuntimeError("GitHub returned invalid JSON; existing reports were not replaced.") from None
            except HTTPError as error:
                if error.code in (429, 502, 503, 504) and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                # Do not include tokens, member bodies, or response payloads in CI logs.
                raise RuntimeError(
                    f"GitHub returned HTTP {error.code}. Check repository access, token permissions, and rate limits."
                ) from None
            except (URLError, TimeoutError):
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError("Could not reach GitHub; existing reports were not replaced.") from None

    def _pages(self, path: str, params: dict | None = None):
        params = dict(params or {})
        params["per_page"] = 100
        for page in range(1, 1001):
            params["page"] = page
            batch = self._get(path, params)
            if not isinstance(batch, list):
                raise RuntimeError("GitHub returned an unexpected response; reports were not replaced.")
            yield from batch
            if len(batch) < 100:
                return
        raise RuntimeError("Pagination safety limit reached; no partial report will be published.")

    def get_issue(self, number: int, include_comments: bool = False) -> dict:
        """Read one issue and, optionally, its full comments; never write to GitHub."""
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            raise ValueError("Issue number must be a positive integer.")
        issue = self._get(f"issues/{number}")
        if _number(issue) != number or "pull_request" in issue:
            raise RuntimeError("Expected a GitHub issue, not a pull request.")
        issue = dict(issue)
        if include_comments:
            issue["comments_data"] = list(self._pages(f"issues/{number}/comments"))
        return issue

    def records(self, weeks: list[str], cache_path: Path | None = None, refresh: bool = False,
                deleted_issue: int | None = None) -> list[dict]:
        """Read metadata and selected-week comments, optionally using a local cache.

        The no-cache route retains the original full-scan behavior. Cached runs
        use overlapping Issue and comment `since` queries, refetch changed
        target-week comment threads, and fully reconcile every seven days.
        The cache contains raw public content and must never be published.
        API failures do not update its synchronization cursor or replace it.
        """
        if deleted_issue is not None and (type(deleted_issue) is not int or deleted_issue < 1):
            raise ValueError("Deleted issue number must be a positive integer.")
        if cache_path is not None:
            return self._cached_records(weeks, Path(cache_path), refresh, deleted_issue)
        records: dict[int, dict] = {}
        for label in ("weekly-plan", "experience,points-approved"):
            for issue in self._pages("issues", {"state": "all", "labels": label}):
                if not isinstance(issue, dict):
                    raise RuntimeError("Malformed GitHub issue response.")
                if "pull_request" in issue:
                    continue
                records[_number(issue)] = dict(issue)
        wanted = set(weeks)
        for issue in records.values():
            if "weekly-plan" in _names(issue) and _week(issue) in wanted:
                issue["comments_data"] = list(self._pages(f"issues/{issue['number']}/comments"))
        return list(records.values())

    def _cached_records(self, weeks: list[str], cache_path: Path, refresh: bool,
                        deleted_issue: int | None = None) -> list[dict]:
        now = _now()
        previous = None if refresh else _load_cache(cache_path, self.repository, now)
        full = previous is None or now - _timestamp(previous["full_sync"]) >= timedelta(days=7)
        issues: dict[str, dict] = {} if full else dict(previous["issues"])
        comment_cache: dict[str, dict] = {} if full else dict(previous["comments"])
        changed_comments: set[str] = set()
        if full:
            # Read all experience metadata, including unapproved experiences:
            # removing approval later must remove that week's contribution.
            for label in ("weekly-plan", "experience"):
                for issue in self._pages("issues", {"state": "all", "labels": label}):
                    _number(issue)
                    if "pull_request" not in issue:
                        issues[str(issue["number"])] = dict(issue)
        else:
            # No label filter: an update that removes a relevant label must
            # evict the old cached issue too. The overlap covers API timing.
            since = _iso(_timestamp(previous["last_sync"]) - timedelta(minutes=5))
            for issue in self._pages("issues", {"state": "all", "since": since, "sort": "updated", "direction": "asc"}):
                key = str(_number(issue))
                if "pull_request" not in issue and _names(issue) & {"weekly-plan", "experience"}:
                    issues[key] = dict(issue)
                else:
                    issues.pop(key, None)
                    comment_cache.pop(key, None)
            # A comment edit need not change issue metadata on every API
            # surface. A repository-wide comment delta detects those edits
            # without requesting every unchanged issue's full thread.
            prefix = f"https://api.github.com/repos/{self.repository}/issues/"
            for comment in self._pages("issues/comments", {"since": since, "sort": "updated", "direction": "asc"}):
                if not isinstance(comment, dict):
                    raise RuntimeError("Malformed GitHub comment response.")
                url = comment.get("issue_url")
                if isinstance(url, str) and url[:len(prefix)].casefold() == prefix.casefold():
                    key = url[len(prefix):]
                    if re.fullmatch(r"[1-9][0-9]*", key):
                        changed_comments.add(key)

        # A deleted Issue does not appear in GitHub's incremental 'since' query.
        # Evict it explicitly when handling the trusted issues.deleted webhook.
        # Apply this after deltas so a stale API response cannot resurrect it.
        if deleted_issue is not None:
            key = str(deleted_issue)
            issues.pop(key, None)
            comment_cache.pop(key, None)

        wanted = set(weeks)
        result: list[dict] = []
        retained_comments: dict[str, dict] = {}
        for key, metadata in sorted(issues.items(), key=lambda item: int(item[0])):
            issue = dict(metadata)
            # Never retain injected comments_data in metadata; full threads
            # have their own validated freshness signature below.
            issue.pop("comments_data", None)
            issues[key] = dict(issue)
            if "weekly-plan" in _names(issue) and _week(issue) in wanted:
                cached = comment_cache.get(key)
                count = issue.get("comments")
                updated = issue.get("updated_at")
                reliable = (
                    isinstance(count, int) and not isinstance(count, bool) and count >= 0
                    and _timestamp(updated) is not None
                )
                unchanged = (
                    reliable and cached is not None and key not in changed_comments
                    and cached.get("updated_at") == updated and cached.get("count") == count
                    and len(cached["data"]) == count
                )
                data = cached["data"] if unchanged else list(self._pages(f"issues/{key}/comments"))
                if not all(isinstance(comment, dict) for comment in data):
                    raise RuntimeError("Malformed GitHub comment response.")
                retained_comments[key] = {"updated_at": updated, "count": count, "data": data}
                issue["comments_data"] = data
            result.append(issue)
        cache = {
            "schema_version": 1,
            "repository": self.repository,
            "last_sync": _iso(now),
            "full_sync": _iso(now) if full else previous["full_sync"],
            "issues": issues,
            "comments": retained_comments,
        }
        _save_cache(cache_path, cache)
        return result
