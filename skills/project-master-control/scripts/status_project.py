#!/usr/bin/env python3
"""Print a read-only project-master-control status summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def first_line(value: str, fallback: str = "Unknown") -> str:
    for line in value.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        lowered = stripped.lower()
        if stripped and lowered not in {"none", "none.", "none yet.", "n/a", "na", "not completed yet.", "not run yet.", "暂无", "无", "无。"}:
            if any(fragment in lowered for fragment in ["if needed in future", "if needed later", "future if needed", "only if needed", "未来如果需要", "后续如需", "暂无需"]):
                continue
            return stripped
    return fallback


def real(value: str) -> bool:
    return first_line(value, "") != ""


def thread_id_for(threads_md: str, name: str) -> str:
    marker = f"## {name}"
    start = threads_md.find(marker)
    if start < 0:
        return "unknown"
    end = threads_md.find("\n## ", start + len(marker))
    block = threads_md[start:] if end < 0 else threads_md[start:end]
    for label in ["Thread ID:", "threadId:", "pendingWorktreeId:", "Worktree:"]:
        for line in block.splitlines():
            if line.strip().lower().startswith(label.lower()):
                value = line.split(":", 1)[1].strip()
                if value:
                    return value
    return "unknown"


def classify_thread(thread: Path) -> dict[str, str]:
    status = read(thread / "STATUS.md")
    handoff = read(thread / "HANDOFF.md")
    task = read(thread / "TASK.md")
    pending = section(status, "Pending Product Manager Confirmation") or section(status, "Pending Master Confirmation")
    blockers = section(status, "Blockers")
    summary = section(handoff, "Summary")
    current_step = first_line(section(status, "Current Step"), "Unknown")
    goal = first_line(section(status, "Current Goal"), first_line(section(task, "Objective"), thread.name))
    text = (status + "\n" + task).lower()
    frozen = any(marker in text for marker in ["status: frozen", "status: draft", "draft only", "not dispatched", "do not dispatch"])

    if frozen:
        state = "draft_or_frozen"
    elif real(pending):
        state = "needs_product_manager_decision"
    elif real(blockers):
        state = "blocked"
    elif real(summary):
        state = "handoff_ready"
    elif "not started" in current_step.lower() or "waiting" in current_step.lower():
        state = "pending_or_waiting"
    else:
        state = "in_progress"

    return {
        "name": thread.name,
        "state": state,
        "goal": goal,
        "current_step": current_step,
        "blockers": first_line(blockers, "None"),
        "pending_confirmation": first_line(pending, "None"),
    }


def overall_state(items: list[dict[str, str]]) -> str:
    active = [item for item in items if item["state"] != "draft_or_frozen"]
    if not active:
        return "no_active_threads"
    if any(item["state"] == "needs_product_manager_decision" for item in active):
        return "needs_product_manager_decision"
    if any(item["state"] == "blocked" for item in active):
        return "blocked"
    if any(item["state"] == "handoff_ready" for item in active):
        return "handoff_ready"
    return "waiting_for_child_feedback"


def main() -> int:
    parser = argparse.ArgumentParser(description="Print project-master-control status without modifying files.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    agents = root / ".agents"
    threads_dir = agents / "threads"
    if not agents.exists():
        result = {"project": str(root), "overall_state": "not_initialized", "threads": []}
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("# PMC Status")
            print(f"Project: {root}")
            print("Overall State: not_initialized")
            print("Next Action: enable project-master-control or run takeover/bootstrap.")
        return 0
    if not threads_dir.exists():
        result = {"project": str(root), "overall_state": "no_thread_packages", "threads": []}
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("# PMC Status")
            print(f"Project: {root}")
            print("Overall State: no_thread_packages")
            print("Next Action: create and validate child task packages.")
        return 0

    threads_md = read(agents / "THREADS.md")
    items = [classify_thread(p) for p in sorted(threads_dir.iterdir()) if p.is_dir()]
    for item in items:
        item["thread_id"] = thread_id_for(threads_md, item["name"])
    state = overall_state(items)
    result = {"project": str(root), "overall_state": state, "threads": items}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("# PMC Status")
    print(f"Project: {root}")
    print(f"Overall State: {state}")
    print("\n## Threads")
    print("| Thread | State | Thread/Worktree | Current Step |")
    print("| --- | --- | --- | --- |")
    for item in items:
        print(f"| {item['name']} | {item['state']} | {item['thread_id']} | {item['current_step']} |")
    print("\n## Next Action")
    if state == "not_initialized":
        print("Enable project-master-control or run takeover/bootstrap.")
    elif state == "no_thread_packages":
        print("Create child task packages, then validate and dispatch.")
    elif state == "needs_product_manager_decision":
        print("Resolve product-manager/user confirmation requests before continuing.")
    elif state == "blocked":
        print("Resolve blockers or send unblock/rework prompts.")
    elif state == "handoff_ready":
        print("Run pmc.py loop/review and decide accept or rework.")
    elif state == "waiting_for_child_feedback":
        print("Wait for child feedback; re-run pmc.py loop after handoff, blocker, heartbeat, or progress request.")
    else:
        print("Run pmc.py resume for a recovery recommendation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
