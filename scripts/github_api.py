"""Small GitHub REST reader; no third-party dependencies or member code execution."""

from __future__ import annotations

import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def validate_repository(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("Repository must have the form owner/repository.")
    return value


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
                    return json.load(response)
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

    def records(self, weeks: list[str]) -> list[dict]:
        """Fetch all plan metadata, but comments only for selected reporting weeks."""
        records: dict[int, dict] = {}
        for label in ("weekly-plan", "experience,points-approved"):
            for issue in self._pages("issues", {"state": "all", "labels": label}):
                if "pull_request" in issue:
                    continue
                if not isinstance(issue.get("number"), int):
                    raise RuntimeError("Malformed GitHub issue response.")
                records[issue["number"]] = issue
        wanted = set(weeks)
        for issue in records.values():
            body = issue.get("body") or ""
            match = re.search(r"^### Week starting\s*\n\s*(\d{4}-\d{2}-\d{2})\s*(?:\n|$)", body, re.MULTILINE)
            names = {label.get("name") for label in issue.get("labels", []) if isinstance(label, dict)}
            if "weekly-plan" in names and match and match.group(1) in wanted:
                issue["comments_data"] = list(self._pages(f"issues/{issue['number']}/comments"))
        return list(records.values())
