#!/usr/bin/env python3
"""Update .agents/PROGRESS.md from child thread STATUS.md and HANDOFF.md files."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


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


def first_line(value: str, fallback: str = "Unknown") -> str:
    for line in value.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        if stripped and stripped.lower() not in {"none", "none.", "none yet.", "not completed yet."}:
            return stripped
    return fallback


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def flat(value: str) -> str:
    return "; ".join(line.strip() for line in value.splitlines() if line.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--stage", default="current")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    agents = root / ".agents"
    threads_dir = agents / "threads"
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    if not threads_dir.exists():
        raise SystemExit(f"No thread directory found: {threads_dir}")

    rows: list[str] = []
    completed: list[str] = []
    in_progress: list[str] = []
    blockers: list[str] = []
    risks: list[str] = []
    confirmations: list[str] = []
    next_steps: list[str] = []

    for thread in sorted(p for p in threads_dir.iterdir() if p.is_dir()):
        status = read(thread / "STATUS.md")
        handoff = read(thread / "HANDOFF.md")
        goal = first_line(section(status, "Current Goal"), thread.name)
        step = first_line(section(status, "Current Step"), "Unknown")
        blocker = section(status, "Blockers")
        pending = section(status, "Pending Product Manager Confirmation") or section(status, "Pending Master Confirmation")
        summary = section(handoff, "Summary")
        verification = section(handoff, "Verification")
        handoff_risks = section(handoff, "Risks")
        next_resume = first_line(section(status, "Next Resume Step"), "Continue assigned task")

        if summary and "Not completed yet" not in summary:
            state = "handoff-ready"
            completed.append(f"- {thread.name}: {first_line(summary)}")
        elif blocker and "None" not in blocker:
            state = "blocked"
        elif "Waiting" in step or "Not started" in step:
            state = "pending"
        else:
            state = "in-progress"
            in_progress.append(f"- {thread.name}: {step}")

        rows.append(f"| {thread.name} | {state} | {goal} | {step} |")
        if blocker and "None" not in blocker:
            blockers.append(f"- {thread.name}: {flat(blocker)}")
        if pending and "None" not in pending:
            confirmations.append(f"- {thread.name}: {flat(pending)}")
        if handoff_risks and "None" not in handoff_risks:
            risks.append(f"- {thread.name}: {flat(handoff_risks)}")
        if verification and "Not run" in verification:
            risks.append(f"- {thread.name}: verification not run")
        next_steps.append(f"- {thread.name}: {next_resume}")

    if rows and not completed and not blockers and not confirmations:
        overall_status = "waiting_for_child_feedback"
    elif rows:
        overall_status = "in-progress"
    else:
        overall_status = "initialized"

    content = "\n".join([
        "# PROGRESS", "", "## Stage", "", args.stage, "",
        "## Overall Status", "", overall_status, "",
        "## Thread Progress", "", "| Thread | Status | Goal | Current Step |", "| --- | --- | --- | --- |", *rows, "",
        "## Completed", "", *(completed or ["- None yet."]), "",
        "## In Progress", "", *(in_progress or ["- None."]), "",
        "## Blockers", "", *(blockers or ["- None."]), "",
        "## Risks", "", *(risks or ["- None known."]), "",
        "## User Confirmations Needed", "", *(confirmations or ["- None."]), "",
        "## Next Steps", "", *(next_steps or ["- Fill task packages."]), "",
        "## Last Updated", "", now, "",
    ])
    (agents / "PROGRESS.md").write_text(content, encoding="utf-8")
    print(f"Updated {agents / 'PROGRESS.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())