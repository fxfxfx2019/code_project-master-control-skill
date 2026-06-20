#!/usr/bin/env python3
"""Bootstrap project-master-control .agents structure.

Example:
  python bootstrap_project_control.py --project-root . --stage "stage-01" \
    --thread backend-core --thread ui-shell --thread acceptance
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


def write_if_missing(path: Path, content: str, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def safe_thread_name(name: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in name.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "thread"


def suggested_window_title(name: str) -> str:
    lower = name.lower()
    tokens = set(re.split(r"[^a-z0-9]+", lower))
    rules = [
        (lambda: "build" in tokens or "build-gate" in lower, "Build Gate"),
        (lambda: "current-state-audit" in lower or {"current", "state", "audit"} <= tokens, "Audit"),
        (lambda: "ui-ux" in lower or ("ui" in tokens and "ux" in tokens) or "design" in tokens, "UI/UX Design"),
        (lambda: "frontend" in tokens or "front-end" in lower or "web" in tokens or "ui" in tokens, "Frontend"),
        (lambda: "backend" in tokens, "Backend"),
        (lambda: "platform" in tokens, "Platform"),
        (lambda: "knowledge" in tokens, "Knowledge AI"),
        (lambda: "data" in tokens or "connector" in tokens or "connectors" in tokens, "Data Connectors"),
        (lambda: "outbound" in tokens, "Outbound"),
        (lambda: "wecom" in tokens, "WeCom"),
        (lambda: "growth" in tokens or "analytics" in tokens, "Growth Analytics"),
        (lambda: "delivery" in tokens or "hardening" in tokens, "Delivery Hardening"),
        (lambda: "test" in tokens or "acceptance" in tokens or "qa" in tokens, "QA"),
        (lambda: "planning" in tokens, "Planning"),
        (lambda: "implementation" in tokens, "Implementation"),
    ]
    label = "Task"
    for matches, title in rules:
        if matches():
            label = title
            break
    return f"Child - {label} - {name}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--stage", default="stage-01")
    parser.add_argument("--thread", action="append", default=[], help="Thread name. Repeat for multiple threads.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    agents = root / ".agents"
    threads_root = agents / "threads"
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    thread_names = [safe_thread_name(t) for t in args.thread] or ["planning", "implementation", "acceptance"]

    write_if_missing(
        agents / "CONTROL.md",
        f"""# CONTROL\n\n## Stage\n\n{args.stage}\n\n## Product Manager Thread\n\nCurrent thread.\n\n## Goal\n\nPending user-confirmed project goal.\n\n## Status\n\ninitialized\n\n## Active Threads\n\n""" + "".join(f"- {name}: pending\n" for name in thread_names) + f"\n## Last Updated\n\n{now}\n",
        args.overwrite,
    )

    write_if_missing(
        agents / "PROGRESS.md",
        f"""# PROGRESS\n\n## Stage\n\n{args.stage}\n\n## Overall Status\n\ninitialized\n\n## Thread Progress\n\n""" + "".join(f"- {name}: pending\n" for name in thread_names) + f"\n## Completed\n\n- Product manager control structure initialized.\n\n## In Progress\n\n- Waiting for task details.\n\n## Blockers\n\n- None.\n\n## Risks\n\n- Thread task packages are placeholders until filled by the product manager thread.\n\n## User Confirmations Needed\n\n- Confirm task split and thread boundaries.\n\n## Next Steps\n\n- Fill TASK.md and ALLOWLIST.md for each child thread.\n\n## Last Updated\n\n{now}\n",
        args.overwrite,
    )

    write_if_missing(
        agents / "THREADS.md",
        "# THREADS\n\n" + "\n".join(f"## {name}\n\nStatus: pending\nSuggested Window Title: {suggested_window_title(name)}\nThread ID: pending-real-thread-creation\nWorktree: pending\n\nWrite Lock:\n- TBD\n" for name in thread_names) + "\n",
        args.overwrite,
    )

    write_if_missing(
        agents / "DECISIONS.md",
        f"# DECISIONS\n\n## {now}\n\n- Initialized project-master-control structure.\n",
        args.overwrite,
    )

    write_if_missing(
        agents / "HANDOFF_SUMMARY.md",
        "# HANDOFF SUMMARY\n\nNo child handoffs accepted yet.\n",
        args.overwrite,
    )

    for name in thread_names:
        base = threads_root / name
        write_if_missing(
            base / "AGENTS.md",
            f"""# AGENTS.md - {name}\n\nYou are `{name}`, a child Codex thread. You are not the product manager thread.\n\nSuggested Window Title: {suggested_window_title(name)}\n\nIf a thread-title tool is available, rename this window to the suggested title before implementation. If unavailable, continue and keep the suggested title in STATUS.md.\n\n## Authority\n\n- Execute only this task package.\n- Use minimal context.\n- Read only Allowed Read files unless expansion is justified and recorded in STATUS.md.\n- Modify only Allowed Write files.\n- Do not execute user-provided requirement changes until the product manager thread confirms.\n- Do not merge, commit to main, or alter global project direction.\n\n## Required Files\n\nRead in order:\n\n1. `.agents/threads/{name}/AGENTS.md`\n2. `.agents/threads/{name}/TASK.md`\n3. `.agents/threads/{name}/ALLOWLIST.md`\n4. `.agents/threads/{name}/STATUS.md`\n\n## Stop And Report\n\nStop when you need forbidden files, architecture changes, database/interface contract changes, dependency changes, test-scope changes, or when the user asks for scope changes.\n\n## Completion\n\nRun required verification, clean temporary artifacts, update STATUS.md, write HANDOFF.md, and list any durable project documents that should be updated or merged by the product manager thread.\n""",
            args.overwrite,
        )
        write_if_missing(
            base / "TASK.md",
            f"""# TASK\n\n## Thread\n\n{name}\n\n## Objective\n\nTBD by product manager thread.\n\n## Background Summary\n\nTBD.\n\n## In Scope\n\n- TBD\n\n## Out Of Scope\n\n- TBD\n\n## Required Steps\n\n1. Wait for the product manager thread to fill this task.\n\n## Required Verification\n\n- TBD\n\n## Completion Criteria\n\n- HANDOFF.md completed.\n- No ALLOWLIST violation.\n- Required verification completed or documented as blocked.\n""",
            args.overwrite,
        )
        write_if_missing(
            base / "STATUS.md",
            f"""# STATUS\n\n## Thread\n\n{name}\n\n## Current Goal\n\nTBD.\n\n## Current Step\n\nWaiting for product manager thread task details.\n\n## Task Mode Decision\n\nMode: pending\nReason:\nImpact on verification:\nImpact on sub-agent use:\n\n## Sub-Agent Decision\n\nDecision: pending\nReason:\nPlanned sub-agents:\nBoundary check:\n\n## Completed\n\n- Task package initialized.\n\n## In Progress\n\n- None.\n\n## Pending\n\n- Product manager thread task details.\n\n## Files Read\n\n- None yet.\n\n## Files Changed\n\n- None yet.\n\n## Commands Run\n\n- None yet.\n\n## Temporary Artifacts\n\n- None known.\n\n## Blockers\n\n- Task not filled.\n\n## Pending Product Manager Confirmation\n\n- None.\n\n## Decisions\n\n- None.\n\n## Next Resume Step\n\nRead task package after product manager thread fills TASK.md and ALLOWLIST.md.\n\n## Last Updated\n\n{now}\n""",
            args.overwrite,
        )
        write_if_missing(
            base / "ALLOWLIST.md",
            """# ALLOWLIST\n\n## Allowed Read\n\n- TBD\n\n## Allowed Write\n\n- TBD\n\n## Requires Product Manager Approval\n\n- README.md\n- AGENTS.md\n- package.json\n- pyproject.toml\n- global config files\n- database models or migrations unless explicitly assigned\n\n## Forbidden\n\n- .env\n- runtime data directories\n- build output\n- cache directories\n- files assigned to other active threads\n- unrelated modules\n""",
            args.overwrite,
        )
        write_if_missing(
            base / "HANDOFF.md",
            f"""# HANDOFF\n\n## Task\n\n{name}\n\n## Summary\n\nNot completed yet.\n\n## Changed Files\n\n- None yet.\n\n## Added Files\n\n- None yet.\n\n## Deleted Files\n\n- None.\n\n## Verification\n\nNot run yet.\n\n## Cleanup\n\nNot completed yet.\n\n## Completion Documents\n\n- None yet.\n\n## Boundary Check\n\nNot checked yet.\n\n## Risks\n\n- None known.\n\n## Open Questions\n\n- None.\n\n## Suggested Next Step\n\nProduct manager thread review after completion.\n""",
            args.overwrite,
        )

    print(f"Initialized {agents} with {len(thread_names)} thread package(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
