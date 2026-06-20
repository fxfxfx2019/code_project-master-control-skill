#!/usr/bin/env python3
"""Recover project-manager context and recommend the next action."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_status(project_root: Path) -> dict:
    script = Path(__file__).resolve().parent / "status_project.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--project-root", str(project_root), "--json"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or proc.stdout.strip() or f"status failed: {proc.returncode}")
    return json.loads(proc.stdout)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume product-manager control after interruption.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--stage", default="current")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    agents = root / ".agents"
    status = run_status(root)
    state = status["overall_state"]

    print("# PMC Resume")
    print(f"Project: {root}")
    print(f"Overall State: {state}")
    print("\n## Read First")
    for rel in [".agents/CONTROL.md", ".agents/PROGRESS.md", ".agents/THREADS.md", ".agents/DECISIONS.md", ".agents/HANDOFF_SUMMARY.md"]:
        path = root / rel
        if path.exists():
            print(f"- {rel}")
    print("\n## Thread Snapshot")
    for item in status.get("threads", []):
        print(f"- {item['name']}: {item['state']} ({item.get('thread_id', 'unknown')})")

    print("\n## Recommended Next Action")
    if state == "not_initialized":
        print("Confirm whether to enable project-master-control, then run bootstrap for new work or takeover for an existing project.")
    elif state == "no_thread_packages":
        print("Generate child task packages, fill TASK.md/ALLOWLIST.md, run pmc.py validate, then dispatch real child threads.")
    elif state == "needs_product_manager_decision":
        print("Open the listed child STATUS.md files, resolve pending confirmations, update DECISIONS.md/PROGRESS.md, then run pmc.py loop.")
    elif state == "blocked":
        print("Inspect blocker sections, decide ask-user/rework/unblock, update HANDOFF_SUMMARY.md and send child prompts as needed.")
    elif state == "handoff_ready":
        print(f"Run: python scripts/pmc.py loop --project-root . --stage {args.stage}")
        print("Then review accept/rework decisions, run boundary/test gates, and dispatch the next unlocked task if applicable.")
    elif state == "waiting_for_child_feedback":
        print("Stay in waiting_for_child_feedback. Do not mark the stage complete. Re-run pmc.py loop after a child handoff, blocker, heartbeat, or user progress request.")
    elif state == "no_active_threads":
        print("Review frozen/draft packages, decide which task is ready, validate it, and dispatch a real child thread.")
    else:
        print(f"Run pmc.py status and inspect .agents files; unrecognized state: {state}")

    progress = read(agents / "PROGRESS.md") if agents.exists() else ""
    if "waiting_for_child_feedback" in progress:
        print("\n## Current Waiting State")
        print("PROGRESS.md already records waiting_for_child_feedback.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
