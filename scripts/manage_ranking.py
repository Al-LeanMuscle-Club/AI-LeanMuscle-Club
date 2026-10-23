"""Prepare local contribution approval changes for maintainer review in a PR.

This command reads GitHub and updates only a local allowlisted ledger. It does
not add labels, post comments, push commits, or change any remote repository.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from club.ranking_state import approve_contribution, load_state, save_state  # noqa: E402
from scripts.github_api import GitHubReader, validate_repository  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("approve", "revoke"))
    parser.add_argument("--issue", type=int, required=True, help="Experience Issue number.")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "Al-LeanMuscle-Club/AI-LeanMuscle-Club"))
    parser.add_argument("--state", type=Path, help="Trusted ledger; fixture runs require an explicit, isolated test path.")
    parser.add_argument("--fixture", type=Path, help="Offline synthetic Issue object; requires an isolated --state path.")
    args = parser.parse_args(argv)
    try:
        if args.issue < 1:
            raise ValueError("Issue number must be a positive integer.")
        validate_repository(args.repository)
        live_state = ROOT / "data" / "ranking-state.json"
        state_path = args.state or live_state
        if args.fixture and (args.state is None or state_path.resolve() == live_state.resolve()):
            raise ValueError("--fixture requires an explicit --state path separate from the live ranking ledger.")
        state = load_state(state_path)
        if args.action == "approve":
            if args.fixture:
                issue = json.loads(args.fixture.read_text(encoding="utf-8"))
                if not isinstance(issue, dict) or issue.get("number") != args.issue:
                    raise ValueError("Fixture must contain the selected synthetic Issue object.")
            else:
                token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
                issue = GitHubReader(args.repository, token).get_issue(args.issue)
            approve_contribution(issue, state, datetime.now(timezone.utc))
        else:
            state["contribution_approvals"].pop(str(args.issue), None)
        save_state(state_path, state)
        print(f"Prepared local {args.action} for Issue #{args.issue}. Review and commit the ledger through a maintainer PR.")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Ranking update failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
