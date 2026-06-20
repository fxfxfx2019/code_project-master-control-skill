#!/usr/bin/env python3
"""Run one product-manager control loop over child thread packages.

This script does not contact Codex threads directly. It reads the on-disk contract files
(STATUS.md, HANDOFF.md, THREADS.md), refreshes PROGRESS.md, and reports decisions the
product manager thread must take: wait, review, accept, rework, unblock next phase, or ask user.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def real(value: str) -> bool:
    lines = [line.strip().lstrip("- ").strip().lower() for line in value.splitlines() if line.strip()]
    meaningful: list[str] = []
    empty_markers = {
        "none",
        "none.",
        "none yet.",
        "n/a",
        "na",
        "not completed yet.",
        "not run yet.",
        "no blocker",
        "no blockers",
        "no blockers.",
        "暂无",
        "无",
        "无。",
        "没有",
        "没有。",
    }
    ignored_fragments = [
        "if needed in future",
        "if needed later",
        "future if needed",
        "only if needed",
        "未来如果需要",
        "后续如需",
        "暂无需",
    ]
    for line in lines:
        if line in empty_markers:
            continue
        if any(fragment in line for fragment in ignored_fragments):
            continue
        meaningful.append(line)
    return bool(meaningful)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def phase_number(name: str) -> int | None:
    match = re.match(r"phase-(\d+)", name)
    return int(match.group(1)) if match else None


def is_frozen_or_draft(thread: Path) -> bool:
    text = (read(thread / "STATUS.md") + "\n" + read(thread / "TASK.md")).lower()
    markers = [
        "status: frozen",
        "status: draft",
        "frozen",
        "draft only",
        "not dispatched",
        "do not dispatch",
        "waiting for product manager dispatch",
    ]
    return any(marker in text for marker in markers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--stage", default="current")
    parser.add_argument("--accept-reviewed", action="store_true", help="Mark acceptable handoffs as accepted in HANDOFF_SUMMARY.md")
    parser.add_argument("--include-frozen", action="store_true", help="Include frozen/draft/not-dispatched task packages")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    agents = root / ".agents"
    threads_dir = agents / "threads"
    if not threads_dir.exists():
        raise SystemExit(f"No thread packages found: {threads_dir}")

    script_dir = Path(__file__).resolve().parent
    update_progress = script_dir / "update_progress.py"
    review = script_dir / "review_thread_handoff.py"
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    run([sys.executable, str(update_progress), "--project-root", str(root), "--stage", args.stage], root)

    decisions: list[str] = []
    accepted: list[str] = []
    rework: list[str] = []
    waiting: list[str] = []
    blocked: list[str] = []
    confirmations: list[str] = []

    threads = sorted((p for p in threads_dir.iterdir() if p.is_dir() and (args.include_frozen or not is_frozen_or_draft(p))), key=lambda p: (phase_number(p.name) or 9999, p.name))
    for thread in threads:
        status = read(thread / "STATUS.md")
        handoff = read(thread / "HANDOFF.md")
        pending = section(status, "Pending Product Manager Confirmation") or section(status, "Pending Master Confirmation")
        blockers = section(status, "Blockers")
        summary = section(handoff, "Summary")

        if real(pending):
            confirmations.append(thread.name)
            decisions.append(f"- {thread.name}: needs product-manager decision ({pending.replace(chr(10), '; ')})")
            continue
        if real(blockers):
            blocked.append(thread.name)
            decisions.append(f"- {thread.name}: blocked ({blockers.replace(chr(10), '; ')})")
            continue
        if real(summary):
            proc = run([sys.executable, str(review), "--thread", str(thread)], root)
            if proc.returncode == 0:
                accepted.append(thread.name)
                decisions.append(f"- {thread.name}: handoff acceptable")
            elif proc.returncode == 1:
                accepted.append(thread.name)
                decisions.append(f"- {thread.name}: handoff acceptable with warnings")
            else:
                rework.append(thread.name)
                decisions.append(f"- {thread.name}: handoff rejected; send rework prompt")
        else:
            waiting.append(thread.name)
            decisions.append(f"- {thread.name}: still running or not handed off")

    summary_path = agents / "HANDOFF_SUMMARY.md"
    existing = read(summary_path)
    overall_state = "active"
    if confirmations:
        overall_state = "needs_product_manager_decision"
    elif rework:
        overall_state = "rework_required"
    elif accepted:
        overall_state = "handoff_reviewed"
    elif waiting and not blocked:
        overall_state = "waiting_for_child_feedback"
    elif blocked:
        overall_state = "blocked"

    append = [f"\n## Manager Loop {now}\n", "\n### Overall State\n", f"{overall_state}\n", "\n### Decisions\n", *[d + "\n" for d in decisions]]
    append += ["\n### Accepted\n", *(f"- {x}\n" for x in accepted)] if accepted else ["\n### Accepted\n- None.\n"]
    append += ["\n### Rework\n", *(f"- {x}\n" for x in rework)] if rework else ["\n### Rework\n- None.\n"]
    append += ["\n### Waiting\n", *(f"- {x}\n" for x in waiting)] if waiting else ["\n### Waiting\n- None.\n"]
    append += ["\n### Blocked\n", *(f"- {x}\n" for x in blocked)] if blocked else ["\n### Blocked\n- None.\n"]
    append += ["\n### Needs User Confirmation\n", *(f"- {x}\n" for x in confirmations)] if confirmations else ["\n### Needs User Confirmation\n- None.\n"]
    write(summary_path, existing.rstrip() + "\n" + "".join(append))

    print("# Manager Loop")
    print(f"Project: {root}")
    print(f"Updated: {now}")
    print("\n## Decisions")
    for item in decisions:
        print(item)
    print("\n## Overall State")
    print(overall_state)
    print("\n## Next Action")
    if confirmations:
        print("Ask user/product manager decision for listed threads.")
    elif rework:
        print("Send rework prompts to rejected child threads.")
    elif accepted:
        phase_threads = [t.name for t in threads if phase_number(t.name) is not None]
        if phase_threads:
            print("If accepted phase unlocks the next phase, update THREADS.md/PROGRESS.md and dispatch the next waiting phase.")
        else:
            print("Dispatch next ready module task or run stage acceptance.")
    elif waiting:
        print("State: waiting_for_child_feedback")
        print("Wait for child thread feedback; no handoff is ready yet. Re-run pmc.py loop after a child handoff, blocker, heartbeat, or user progress request.")
    elif blocked:
        print("Resolve blockers before dispatching or accepting child work.")
    else:
        print("No active threads found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
