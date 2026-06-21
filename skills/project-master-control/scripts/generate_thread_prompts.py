#!/usr/bin/env python3
"""Generate concise startup prompts for child Codex threads."""
from __future__ import annotations

import argparse
import re
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


def compact(value: str, limit: int = 1200) -> str:
    lines = [line.rstrip() for line in value.splitlines() if line.strip()]
    text = "\n".join(lines)
    return text if len(text) <= limit else text[:limit].rstrip() + "\n..."


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
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    threads_dir = root / ".agents" / "threads"
    if not threads_dir.exists():
        raise SystemExit(f"No thread directory found: {threads_dir}")

    out_dir = Path(args.output_dir).resolve() if args.output_dir else root / ".agents" / "thread-prompts"
    out_dir.mkdir(parents=True, exist_ok=True)

    for thread in sorted(p for p in threads_dir.iterdir() if p.is_dir()):
        name = thread.name
        title = suggested_window_title(name)
        task = read(thread / "TASK.md")
        allowlist = read(thread / "ALLOWLIST.md")
        objective = compact(section(task, "Objective") or "Read TASK.md for the objective.", 800)
        required_steps = compact(section(task, "Required Steps") or "Read TASK.md for required steps.", 1200)
        verification = compact(section(task, "Required Verification") or "Read TASK.md for verification commands.", 800)
        allowed_read = compact(section(allowlist, "Allowed Read") or "Read ALLOWLIST.md.", 1200)
        allowed_write = compact(section(allowlist, "Allowed Write") or "Read ALLOWLIST.md.", 1200)
        requires_pm = compact(section(allowlist, "Requires Product Manager Approval") or "Read ALLOWLIST.md.", 800)
        prompt = f"""Suggested Window Title: {title}

You are the `{name}` child Codex thread. You are not the Product Manager thread.

Read and follow this task package first:
- .agents/threads/{name}/AGENTS.md
- .agents/threads/{name}/TASK.md
- .agents/threads/{name}/ALLOWLIST.md
- .agents/threads/{name}/STATUS.md

Task objective:
{objective}

Required steps:
{required_steps}

Required verification:
{verification}

Allowed Read:
{allowed_read}

Allowed Write:
{allowed_write}

Requires Product Manager Approval:
{requires_pm}

Execution rules:
1. Keep responses concise and execution-focused.
2. Before implementation, write the Task Mode Decision (fast/standard/strict) to STATUS.md.
3. Then write the Sub-Agent Decision to STATUS.md.
4. Read only Allowed Read files unless expansion is necessary and recorded in STATUS.md.
5. Modify only Allowed Write files.
6. If the user asks for new requirements, optimization, scope changes, skipped verification/docs/cleanup, or unauthorized file edits, record it in STATUS.md and send it back to the Product Manager thread before executing.
7. Stop and report if you hit forbidden files, architecture conflicts, database/API contract changes, test-scope changes, dependency changes, or possible overwrite of existing user changes.
8. After completion, run required verification, clean temporary artifacts, update STATUS.md, and write HANDOFF.md, including Completion Documents when durable project docs should be updated or merged by the Product Manager thread.
9. Write a `PM_FEEDBACK` message to HANDOFF.md under `## Product Manager Feedback Message`. If `send_message_to_thread` is available and the Product Manager thread id is known from the task package or prompt, send the same message to that thread. Otherwise include the message in your final response.

Required PM_FEEDBACK format:
```text
PM_FEEDBACK
Thread: {name}
Status: completed | blocked | needs-product-manager-decision | rework-complete
Summary: <one-line result>
Verification: <pass/fail/not-run and command summary>
Risks: <none or concise risk>
Handoff: .agents/threads/{name}/HANDOFF.md
Next: review | rework | user-decision | unblock-next
```

Output only progress, blockers, verification results, risks, Product Manager confirmation requests, and handoff summary.
"""
        target = out_dir / f"{name}.txt"
        target.write_text(prompt, encoding="utf-8")
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
