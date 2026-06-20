#!/usr/bin/env python3
"""Validate child thread task packages before dispatch."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED_FILES = ["AGENTS.md", "TASK.md", "STATUS.md", "ALLOWLIST.md", "HANDOFF.md"]
REQUIRED_TASK_SECTIONS = ["Thread", "Objective", "Background Summary", "In Scope", "Out Of Scope", "Required Steps", "Required Verification", "Completion Criteria"]
REQUIRED_ALLOWLIST_SECTIONS = ["Allowed Read", "Allowed Write", "Requires Product Manager Approval", "Forbidden"]
PLACEHOLDERS = {"TBD", "TODO", "<path>", "<objective>", "<thread-name>", "<item>", "<step>", "<command>", "<criterion>"}
PM_ONLY_WRITES = {"agents.md", ".agents/control.md", ".agents/progress.md", ".agents/threads.md", ".agents/decisions.md", ".agents/handoff_summary.md"}
IMPLEMENTATION_PREFIXES = ("apps/", "src/", "packages/", "backend/", "frontend/", "server/", "client/")
UI_THREAD_HINT_RE = re.compile(r"(^|[^a-z0-9])(ui|frontend|front-end|page|screen|component|design-system)([^a-z0-9]|$)")
DESIGN_THREAD_HINT_RE = re.compile(r"(^|[^a-z0-9])(ui-ux|design|prototype|wireframe)([^a-z0-9]|$)")
FROZEN_MARKERS = ("status: frozen", "status: draft", "draft only", "not dispatched", "do not dispatch")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def section(text: str, name: str) -> str:
    marker = f"## {name}"
    start = text.find(marker)
    if start < 0:
        return ""
    start += len(marker)
    end = text.find("\n## ", start)
    if end < 0:
        end = len(text)
    return text[start:end].strip()


def has_placeholder(text: str) -> list[str]:
    return sorted(token for token in PLACEHOLDERS if token in text)


def section_has_real_list(value: str) -> bool:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    meaningful = []
    for line in lines:
        stripped = line.lstrip("- ").strip()
        if stripped and stripped.upper() not in {"TBD", "TODO"} and not (stripped.startswith("<") and stripped.endswith(">")):
            meaningful.append(stripped)
    return bool(meaningful)


def list_items(value: str) -> list[str]:
    items: list[str] = []
    for line in value.splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        item = stripped.lstrip("- ").strip().replace("\\", "/")
        if not item or item.upper() in {"TBD", "TODO"}:
            continue
        items.append(item.rstrip("/"))
    return items


def is_frozen_or_draft(thread: Path) -> bool:
    text = (read(thread / "STATUS.md") + "\n" + read(thread / "TASK.md")).lower()
    return any(marker in text for marker in FROZEN_MARKERS)


def looks_active(thread: Path) -> bool:
    text = (read(thread / "STATUS.md") + "\n" + read(thread / "TASK.md")).lower()
    if is_frozen_or_draft(thread):
        return False
    return any(marker in text for marker in ["active", "ready_for_dispatch", "in progress", "in-progress", "waiting_for_child_feedback", "thread id:", "pending-real-thread-creation"])


def validate_thread(thread: Path, all_threads: list[Path] | None = None) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []

    for name in REQUIRED_FILES:
        path = thread / name
        if not path.exists():
            issues.append(f"missing {name}")
        elif not read(path).strip():
            issues.append(f"empty {name}")

    task = read(thread / "TASK.md")
    allowlist = read(thread / "ALLOWLIST.md")
    status = read(thread / "STATUS.md")
    combined = f"{thread.name}\n{task}\n{allowlist}\n{status}".lower()

    for name in REQUIRED_TASK_SECTIONS:
        value = section(task, name)
        if not value:
            issues.append(f"TASK.md missing section: {name}")
        elif not section_has_real_list(value):
            issues.append(f"TASK.md section not filled: {name}")

    for name in REQUIRED_ALLOWLIST_SECTIONS:
        value = section(allowlist, name)
        if not value:
            issues.append(f"ALLOWLIST.md missing section: {name}")
        elif name in {"Allowed Read", "Allowed Write"} and not section_has_real_list(value):
            issues.append(f"ALLOWLIST.md section not filled: {name}")

    # Placeholder warnings only apply to dispatch-critical instruction files.
    # STATUS.md and HANDOFF.md may contain command logs such as rg 'TODO|TBD'.
    for file_name in ["AGENTS.md", "TASK.md", "ALLOWLIST.md"]:
        path = thread / file_name
        placeholders = has_placeholder(read(path))
        if placeholders:
            warnings.append(f"{file_name} contains placeholder(s): {', '.join(placeholders)}")

    allowed_writes = list_items(section(allowlist, "Allowed Write"))
    if is_frozen_or_draft(thread) and looks_active(thread):
        issues.append("thread is marked frozen/draft/not-dispatched but also appears active")

    if "product-manager" in combined or "????" in combined:
        for item in allowed_writes:
            normalized = item.lower().lstrip("./")
            if normalized not in PM_ONLY_WRITES and not normalized.startswith(".agents/"):
                warnings.append(f"possible product-manager package writes outside coordination files: {item}")

    if UI_THREAD_HINT_RE.search(combined) and not DESIGN_THREAD_HINT_RE.search(combined):
        if "waiting_for_design_confirmation" not in combined and "design handoff" not in combined:
            warnings.append("UI/frontend-looking task does not mention waiting_for_design_confirmation or design handoff")

    if any(prefix in item.lower().lstrip("./") for item in allowed_writes for prefix in IMPLEMENTATION_PREFIXES):
        if any(hint in combined for hint in ("audit", "current-state", "design", "prototype", "wireframe")) and "production implementation" not in combined:
            warnings.append("audit/design-looking task has implementation directories in Allowed Write")

    if all_threads:
        this_active = looks_active(thread)
        if this_active:
            this_writes = set(allowed_writes)
            for other in all_threads:
                if other == thread or not looks_active(other):
                    continue
                other_writes = set(list_items(section(read(other / "ALLOWLIST.md"), "Allowed Write")))
                overlap = sorted(this_writes & other_writes)
                if overlap:
                    issues.append(f"write lock conflict with {other.name}: {', '.join(overlap)}")

    return issues, warnings


def iter_threads(path: Path) -> list[Path]:
    if (path / "TASK.md").exists():
        return [path]
    threads = path / ".agents" / "threads"
    if threads.exists():
        return sorted(p for p in threads.iterdir() if p.is_dir())
    if path.name == "threads":
        return sorted(p for p in path.iterdir() if p.is_dir())
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--thread", help="Path to one .agents/threads/<thread-name> package")
    parser.add_argument("--project-root", default=".", help="Project root, used when --thread is omitted")
    args = parser.parse_args()

    target = Path(args.thread).resolve() if args.thread else Path(args.project_root).resolve()
    threads = iter_threads(target)
    if not threads:
        raise SystemExit(f"No thread package found from: {target}")

    all_threads = threads if not args.thread else None
    any_issues = False
    any_warnings = False
    for thread in threads:
        issues, warnings = validate_thread(thread, all_threads)
        print(f"# {thread.name}")
        if issues:
            any_issues = True
            print("Status: invalid")
            print("Issues:")
            for item in issues:
                print(f"- {item}")
        else:
            print("Status: valid")
        if warnings:
            any_warnings = True
            print("Warnings:")
            for item in warnings:
                print(f"- {item}")
        print()

    return 2 if any_issues else (1 if any_warnings else 0)


if __name__ == "__main__":
    raise SystemExit(main())
