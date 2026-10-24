"""Point README helper links at the URL returned by a successful Pages deploy."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit


def helper_url(page_url: str) -> str:
    parsed = urlsplit(page_url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or re.search(r"[\s<>\[\]\\]", page_url)):
        raise ValueError("Use the HTTPS site URL returned by the Pages deployment.")
    path = parsed.path.rstrip("/") + "/tools/"
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def update_entry(text: str, url: str) -> str:
    pattern = r"^\[member-helper\]: .*?$"
    if len(re.findall(pattern, text, flags=re.MULTILINE)) != 1:
        raise ValueError("README needs exactly one member-helper link definition.")
    return re.sub(pattern, lambda _: "[member-helper]: " + url, text, flags=re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    url = helper_url(os.environ.get("MEMBER_PAGE_URL", ""))
    paths = [args.root / "README.md", args.root / "README.en.md"]
    # Validate both before changing either README.
    updates = [(path, update_entry(path.read_text(encoding="utf-8"), url)) for path in paths]
    for path, text in updates:
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
