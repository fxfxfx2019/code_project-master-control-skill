#!/usr/bin/env python3
"""Initialize project-master-control takeover files for an existing project."""
from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def write_if_missing(path: Path, content: str, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def run_git(root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=10,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        return f"unavailable: {exc}"
    value = result.stdout.strip()
    return value if value else f"exit={result.returncode}"


def top_level_map(root: Path) -> str:
    names: list[str] = []
    ignored = {".git", ".agents", "node_modules", ".next", "dist", "build", ".venv", "venv", "__pycache__"}
    try:
        for item in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if item.name in ignored:
                continue
            suffix = "/" if item.is_dir() else ""
            names.append(f"- {item.name}{suffix}")
            if len(names) >= 80:
                names.append("- ...")
                break
    except Exception as exc:  # pragma: no cover - environment dependent
        names.append(f"- unable to list project root: {exc}")
    return "\n".join(names) if names else "- No top-level files found."


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
    parser = argparse.ArgumentParser(description="Create existing-project takeover control files.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--stage", default="existing-project-takeover")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    agents = root / ".agents"
    thread_name = "phase-00-current-state-audit"
    thread = agents / "threads" / thread_name
    window_title = suggested_window_title(thread_name)
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    rev_parse = run_git(root, ["rev-parse", "--show-toplevel"])
    branch = run_git(root, ["branch", "--show-current"])
    commit = run_git(root, ["rev-parse", "--short", "HEAD"])
    status = run_git(root, ["status", "--short"])
    git_summary = f"Root: {rev_parse}\nBranch: {branch}\nCommit: {commit}\nStatus:\n{status}"

    write_if_missing(
        agents / "CONTROL.md",
        f"""# CONTROL\n\n## Stage\n\n{args.stage}\n\n## Product Manager Thread\n\nCurrent thread.\n\n## Goal\n\nExisting project takeover for controlled second development.\n\n## Status\n\ninitialized_takeover\n\n## Baseline\n\n```text\n{git_summary}\n```\n\n## Active Threads\n\n- {thread_name}: ready_for_dispatch\n\n## Last Updated\n\n{now}\n""",
        args.overwrite,
    )

    write_if_missing(
        agents / "PROGRESS.md",
        f"""# PROGRESS\n\n## Stage\n\n{args.stage}\n\n## Overall Status\n\nexisting_project_takeover_initialized\n\n## Thread Progress\n\n- {thread_name}: ready_for_dispatch\n\n## Completed\n\n- Product manager control structure initialized for existing-project takeover.\n- Baseline git/non-git state captured.\n\n## In Progress\n\n- Current-state audit task package is ready for validation and dispatch.\n\n## Blockers\n\n- None.\n\n## Risks\n\n- Existing project behavior is baseline; implementation changes must wait for bounded child tasks.\n\n## User Confirmations Needed\n\n- High-impact changes such as refactor, dependency upgrade, schema/API change, architecture change, or major UI redesign require confirmation.\n\n## Next Steps\n\n- Validate and dispatch `{thread_name}`.\n- Use audit handoff to create follow-up bugfix, feature, UI/UX, test, refactor, hardening, or docs threads.\n\n## Last Updated\n\n{now}\n""",
        args.overwrite,
    )

    write_if_missing(
        agents / "THREADS.md",
        f"""# THREADS\n\n## {thread_name}\n\nStatus: ready_for_dispatch\nSuggested Window Title: {window_title}\nThread ID: pending-real-thread-creation\nWorktree: pending\n\nWrite Lock:\n- .agents/threads/{thread_name}/STATUS.md\n- .agents/threads/{thread_name}/HANDOFF.md\n""",
        args.overwrite,
    )

    write_if_missing(
        agents / "DECISIONS.md",
        f"""# DECISIONS\n\n## {now}\n\n- Initialized existing-project takeover mode.\n- Current implementation is the baseline; no business code changes are authorized by takeover initialization.\n- High-impact changes require explicit user confirmation or bounded child-thread tasks.\n\n## Baseline Git State\n\n```text\n{git_summary}\n```\n""",
        args.overwrite,
    )

    write_if_missing(agents / "HANDOFF_SUMMARY.md", "# HANDOFF SUMMARY\n\nNo child handoffs accepted yet.\n", args.overwrite)

    write_if_missing(
        thread / "AGENTS.md",
        f"""# AGENTS.md - {thread_name}\n\nYou are `{thread_name}`, a child Codex thread. You are not the product manager thread.\n\nSuggested Window Title: {window_title}\n\nIf a thread-title tool is available, rename this window to the suggested title before implementation. If unavailable, continue and keep the suggested title in STATUS.md.\n\n## Authority\n\n- Audit the existing project baseline before second development.\n- Use minimal context, but read broadly enough to map the current project.\n- Do not modify production code.\n- Only update your own STATUS.md and HANDOFF.md.\n- Do not refactor, upgrade dependencies, alter schemas/APIs, redesign UI, or change behavior.\n\n## Required Files\n\nRead in order:\n\n1. `.agents/threads/{thread_name}/AGENTS.md`\n2. `.agents/threads/{thread_name}/TASK.md`\n3. `.agents/threads/{thread_name}/ALLOWLIST.md`\n4. `.agents/threads/{thread_name}/STATUS.md`\n\n## Stop And Report\n\nStop if audit requires mutating project state, credentials, network access, database writes, dependency installs, or high-impact decisions.\n\n## Completion\n\nUpdate STATUS.md and write HANDOFF.md with baseline summary, risks, command status, recommended next tasks, and open decisions.\n""",
        args.overwrite,
    )

    write_if_missing(
        thread / "TASK.md",
        f"""# TASK\n\n## Thread\n\n{thread_name}\n\n## Objective\n\nAudit the current project baseline before second-development tasks are dispatched.\n\n## Background Summary\n\nThis is an existing in-progress project takeover. The current implementation is baseline. The audit must not change production code or product behavior.\n\n## In Scope\n\n- Map apps, packages, services, important docs, config, scripts, and top-level structure.\n- Identify git/non-git state, branch/commit when available, dirty files, and recovery constraints.\n- Identify run, build, lint, typecheck, test, and smoke commands with pass/fail/unknown status.\n- Inventory completed, partial, missing, and unknown features from available docs and code.\n- Inventory risks: failing tests, fragile files, security/auth/payment/data risks, generated files, large untracked changes.\n- Inventory UI routes/pages/components and obvious UX/design-system gaps when relevant.\n- Recommend next child-thread tasks with suggested ALLOWLIST boundaries and dependencies.\n\n## Out Of Scope\n\n- Production code changes.\n- Refactors, dependency upgrades, schema/API changes, UI redesign, or behavior changes.\n- Git initialization or worktree creation in a non-git project.\n- Deleting files or normalizing formatting.\n\n## Required Steps\n\n1. Read this task package and write Task Mode Decision plus Sub-Agent Decision to STATUS.md.\n2. Inspect project structure and key docs/configs.\n3. Inspect git/non-git state without modifying it.\n4. Identify safe verification commands and run only commands that do not mutate persistent project state; otherwise document why not run.\n5. Write HANDOFF.md with baseline summary, risks, recommended next tasks, and open decisions.\n\n## Required Verification\n\n- Confirm no production files were changed.\n- Confirm recommended next tasks have bounded file areas and dependency notes.\n- Confirm command results are recorded as pass/fail/unknown/not-run with reasons.\n\n## Completion Criteria\n\n- HANDOFF.md contains project map, baseline state, feature inventory, risk inventory, command status, recommended child tasks, and open decisions.\n- STATUS.md records files read, commands run, task mode, sub-agent decision, and next resume step.\n""",
        args.overwrite,
    )

    write_if_missing(
        thread / "STATUS.md",
        f"""# STATUS\n\n## Thread\n\n{thread_name}\n\n## Current Goal\n\nAudit the current project baseline.\n\n## Current Step\n\nNot started.\n\n## Task Mode Decision\n\nMode: pending\nReason:\nImpact on verification:\nImpact on sub-agent use:\n\n## Sub-Agent Decision\n\nDecision: pending\nReason:\nPlanned sub-agents:\nBoundary check:\n\n## Completed\n\n- Task package initialized.\n\n## In Progress\n\n- None.\n\n## Pending\n\n- Initial audit execution.\n\n## Files Read\n\n- None yet.\n\n## Files Changed\n\n- None yet.\n\n## Commands Run\n\n- None yet.\n\n## Temporary Artifacts\n\n- None known.\n\n## Blockers\n\n- None.\n\n## Pending Product Manager Confirmation\n\n- None.\n\n## Decisions\n\n- Existing implementation is baseline.\n\n## Next Resume Step\n\nRead task package and begin current-state audit.\n\n## Last Updated\n\n{now}\n""",
        args.overwrite,
    )

    write_if_missing(
        thread / "ALLOWLIST.md",
        f"""# ALLOWLIST\n\n## Allowed Read\n\n- .\n\n## Allowed Write\n\n- .agents/threads/{thread_name}/STATUS.md\n- .agents/threads/{thread_name}/HANDOFF.md\n\n## Requires Product Manager Approval\n\n- AGENTS.md\n- .agents/CONTROL.md\n- .agents/PROGRESS.md\n- .agents/THREADS.md\n- .agents/DECISIONS.md\n- package.json\n- pyproject.toml\n- lockfiles\n- global config files\n- database models or migrations\n- API contracts\n- UI component implementation files\n\n## Forbidden\n\n- .env\n- credentials and secrets\n- runtime data directories\n- build output\n- cache directories\n- production source changes\n- dependency installation or upgrade output\n- files assigned to other active threads\n""",
        args.overwrite,
    )

    write_if_missing(
        thread / "HANDOFF.md",
        f"""# HANDOFF\n\n## Task\n\n{thread_name}\n\n## Summary\n\nNot completed yet.\n\n## Changed Files\n\n- None yet.\n\n## Added Files\n\n- None yet.\n\n## Deleted Files\n\n- None.\n\n## Verification\n\nNot run yet.\n\n## Cleanup\n\nNot completed yet.\n\n## Boundary Check\n\nNot checked yet.\n\n## Risks\n\n- None known.\n\n## Open Questions\n\n- None.\n\n## Suggested Next Step\n\nProduct manager thread review after completion.\n""",
        args.overwrite,
    )

    print(f"Initialized existing-project takeover at {agents}")
    print(f"Created task package: {thread}")
    print("Next: python scripts/pmc.py validate --project-root <project-root>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
