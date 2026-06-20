#!/usr/bin/env python3
"""Check a child thread diff against its ALLOWLIST.

Run from the project root:
  python check_thread_boundaries.py --thread .agents/threads/backend-core
  python check_thread_boundaries.py --thread .agents/threads/backend-core --base main
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


SECTIONS = {
    "allowed read": "read",
    "allowed write": "write",
    "requires master approval": "approval",
    "forbidden": "forbidden",
}


def normalize(path: str) -> str:
    return path.strip().replace("\\", "/").strip("/")


def parse_allowlist(path: Path) -> dict[str, list[str]]:
    current: str | None = None
    result = {"read": [], "write": [], "approval": [], "forbidden": []}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            current = SECTIONS.get(line[3:].strip().lower())
            continue
        if current and line.startswith("- "):
            value = normalize(line[2:])
            if value and value.upper() != "TBD":
                result[current].append(value)
    return result


def matches(path: str, patterns: list[str]) -> bool:
    p = normalize(path)
    for pattern in patterns:
        pat = normalize(pattern)
        if not pat:
            continue
        if pat.endswith("/") and p.startswith(pat):
            return True
        if p == pat or p.startswith(pat.rstrip("/") + "/"):
            return True
        if "*" in pat:
            import fnmatch
            if fnmatch.fnmatch(p, pat):
                return True
    return False


def changed_files(base: str | None) -> list[str]:
    if base:
        cmd = ["git", "diff", "--name-only", base]
    else:
        cmd = ["git", "diff", "--name-only", "HEAD"]
    tracked = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.splitlines()
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], check=True, capture_output=True, text=True).stdout.splitlines()
    return sorted({normalize(x) for x in tracked + untracked if x.strip()})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--thread", required=True, help="Path to .agents/threads/<thread-name>")
    parser.add_argument("--base", help="Optional git diff base, e.g. main or origin/main")
    args = parser.parse_args()

    thread_dir = Path(args.thread)
    allowlist_path = thread_dir / "ALLOWLIST.md"
    if not allowlist_path.exists():
        raise SystemExit(f"ALLOWLIST not found: {allowlist_path}")

    allowlist = parse_allowlist(allowlist_path)
    files = changed_files(args.base)

    violations = []
    needs_approval = []
    for file in files:
        if matches(file, allowlist["forbidden"]):
            violations.append((file, "forbidden"))
        elif matches(file, allowlist["approval"]):
            needs_approval.append(file)
        elif not matches(file, allowlist["write"]):
            violations.append((file, "not in Allowed Write"))

    print(f"Changed files: {len(files)}")
    for file in files:
        print(f"- {file}")

    if needs_approval:
        print("\nRequires master approval:")
        for file in needs_approval:
            print(f"- {file}")

    if violations:
        print("\nBoundary violations:")
        for file, reason in violations:
            print(f"- {file}: {reason}")
        return 2

    print("\nBoundary check passed.")
    return 0 if not needs_approval else 1


if __name__ == "__main__":
    raise SystemExit(main())
