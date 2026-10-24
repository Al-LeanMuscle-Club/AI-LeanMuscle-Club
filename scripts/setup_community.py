"""Preview or apply missing community labels and conservative record backfills.

The default is read-only. --apply performs additive label writes only; it never
posts comments, edits member content, changes settings, or approves points.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from club.community import inferred_labels, label_names  # noqa: E402
from scripts.github_api import GitHubReader  # noqa: E402


LABELS = {
    "weekly-plan": ("0759FF", "Weekly plans and check-ins"),
    "experience": ("0E8A16", "Community experiences and workflows"),
    "points-approved": ("FBCA04", "Maintainer-approved weekly contribution"),
    "activity-record": ("5319E7", "Free workout records"),
    "meal-record": ("D4C5F9", "Free food records"),
    "example": ("BFDADC", "Fictional demonstration, excluded from community participation"),
}


class CommunitySetupClient(GitHubReader):
    def _post(self, path: str, data: dict) -> None:
        request = Request(
            f"https://api.github.com/repos/{self.repository}/{path}",
            data=json.dumps(data).encode(), method="POST",
            headers={"Authorization": f"Bearer {self._token}", "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                response.read()
        except HTTPError as error:
            # A parallel maintainer may have just created this label. Treat
            # that case as success without replacing its chosen metadata.
            if path == "labels" and error.code == 422:
                names = {item.get("name", "").casefold() for item in self._pages("labels")}
                if data["name"].casefold() in names:
                    return
            raise RuntimeError(f"GitHub refused the label update (HTTP {error.code}).") from None
        except (URLError, TimeoutError):
            raise RuntimeError("Could not update GitHub labels; rerunning setup is safe.") from None

    def create_label(self, name: str) -> None:
        color, description = LABELS[name]
        self._post("labels", {"name": name, "color": color, "description": description})

    def add_labels(self, number: int, names: list[str]) -> None:
        if type(number) is not int or number < 1 or not names or set(names) - (set(LABELS) - {"points-approved"}):
            raise ValueError("Only recognized record or example labels may be added.")
        # POST adds the supplied labels; PUT would replace unrelated labels.
        self._post(f"issues/{number}/labels", {"labels": names})


def setup(client: CommunitySetupClient, *, apply: bool = False, backfill: bool = False) -> dict:
    current = list(client._pages("labels"))
    if any(not isinstance(label, dict) or not isinstance(label.get("name"), str) for label in current):
        raise RuntimeError("GitHub returned malformed label data.")
    existing = {label["name"].casefold() for label in current}
    missing = sorted(name for name in LABELS if name.casefold() not in existing)
    changes = []
    if backfill:
        for issue in client._pages("issues", {"state": "all"}):
            if not isinstance(issue, dict):
                raise RuntimeError("GitHub returned malformed issue data.")
            additions = inferred_labels(issue) - label_names(issue)
            if additions:
                number = issue.get("number")
                if type(number) is not int or number < 1:
                    raise RuntimeError("GitHub returned an invalid issue number.")
                changes.append({"number": number, "add_labels": sorted(additions)})
    changes.sort(key=lambda change: change["number"])
    applied = []
    if apply:
        for name in missing:
            client.create_label(name)
        for change in changes:
            # Recheck live state immediately before writing. In particular an
            # edited example must not gain a record label from stale metadata.
            issue = client.get_issue(change["number"])
            names = sorted(inferred_labels(issue) - label_names(issue))
            if names:
                client.add_labels(change["number"], names)
                applied.append({"number": change["number"], "add_labels": names})
    return {"mode": "apply" if apply else "preview", "create_labels": missing,
            "issue_label_changes": applied if apply else changes}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "Al-LeanMuscle-Club/AI-LeanMuscle-Club"))
    parser.add_argument("--backfill", action="store_true", help="Also recognize existing records and explicitly marked examples.")
    parser.add_argument("--apply", action="store_true", help="Apply the additive changes; the default only previews them.")
    args = parser.parse_args(argv)
    try:
        client = CommunitySetupClient(args.repository, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "")
        result = setup(client, apply=args.apply, backfill=args.backfill)
        # Logs contain only label names and Issue numbers, never member bodies.
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, RuntimeError) as error:
        print(f"Community setup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
