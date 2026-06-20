#!/usr/bin/env python3
"""Unified CLI for project-master-control helper scripts."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def run_script(name: str, args: list[str]) -> int:
    script = script_dir() / name
    if not script.exists():
        raise SystemExit(f"Script not found: {script}")
    return subprocess.call([sys.executable, str(script), *args])


def main() -> int:
    parser = argparse.ArgumentParser(prog="pmc.py", description="Project Master Control helper CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    boot = sub.add_parser("bootstrap", help="Create .agents control structure and child thread packages")
    boot.add_argument("--project-root", default=".")
    boot.add_argument("--stage", default="stage-01")
    boot.add_argument("--thread", action="append", default=[])
    boot.add_argument("--overwrite", action="store_true")

    takeover = sub.add_parser("takeover", help="Initialize existing-project takeover with a current-state audit package")
    takeover.add_argument("--project-root", default=".")
    takeover.add_argument("--stage", default="existing-project-takeover")
    takeover.add_argument("--overwrite", action="store_true")

    prompts = sub.add_parser("prompts", help="Generate child thread startup prompts")
    prompts.add_argument("--project-root", default=".")
    prompts.add_argument("--output-dir", default=None)

    progress = sub.add_parser("progress", help="Update .agents/PROGRESS.md")
    progress.add_argument("--project-root", default=".")
    progress.add_argument("--stage", default="current")

    status = sub.add_parser("status", help="Print a read-only project-manager status summary")
    status.add_argument("--project-root", default=".")
    status.add_argument("--json", action="store_true")

    resume = sub.add_parser("resume", help="Recover product-manager context and recommend next action")
    resume.add_argument("--project-root", default=".")
    resume.add_argument("--stage", default="current")

    validate = sub.add_parser("validate", help="Validate child thread task packages before dispatch")
    validate.add_argument("--project-root", default=".")
    validate.add_argument("--thread", default=None)

    boundary = sub.add_parser("boundary", help="Check current diff against a child thread ALLOWLIST")
    boundary.add_argument("--thread", required=True)
    boundary.add_argument("--base", default=None)

    review = sub.add_parser("review", help="Review child thread HANDOFF.md for acceptance")
    review.add_argument("--thread", required=True)
    review.add_argument("--base", default=None)

    loop = sub.add_parser("loop", help="Run one product-manager manager loop")
    loop.add_argument("--project-root", default=".")
    loop.add_argument("--stage", default="current")
    loop.add_argument("--accept-reviewed", action="store_true")
    loop.add_argument("--include-frozen", action="store_true")

    args = parser.parse_args()

    if args.command == "takeover":
        forwarded = ["--project-root", args.project_root, "--stage", args.stage]
        if args.overwrite:
            forwarded.append("--overwrite")
        return run_script("audit_existing_project.py", forwarded)

    if args.command == "bootstrap":
        forwarded = ["--project-root", args.project_root, "--stage", args.stage]
        for thread in args.thread:
            forwarded.extend(["--thread", thread])
        if args.overwrite:
            forwarded.append("--overwrite")
        return run_script("bootstrap_project_control.py", forwarded)

    if args.command == "prompts":
        forwarded = ["--project-root", args.project_root]
        if args.output_dir:
            forwarded.extend(["--output-dir", args.output_dir])
        return run_script("generate_thread_prompts.py", forwarded)

    if args.command == "progress":
        return run_script("update_progress.py", ["--project-root", args.project_root, "--stage", args.stage])

    if args.command == "status":
        forwarded = ["--project-root", args.project_root]
        if args.json:
            forwarded.append("--json")
        return run_script("status_project.py", forwarded)

    if args.command == "resume":
        return run_script("resume_project.py", ["--project-root", args.project_root, "--stage", args.stage])

    if args.command == "validate":
        forwarded = ["--project-root", args.project_root]
        if args.thread:
            forwarded = ["--thread", args.thread]
        return run_script("validate_task_package.py", forwarded)

    if args.command == "boundary":
        forwarded = ["--thread", args.thread]
        if args.base:
            forwarded.extend(["--base", args.base])
        return run_script("check_thread_boundaries.py", forwarded)

    if args.command == "review":
        forwarded = ["--thread", args.thread]
        if args.base:
            forwarded.extend(["--base", args.base])
        return run_script("review_thread_handoff.py", forwarded)

    if args.command == "loop":
        forwarded = ["--project-root", args.project_root, "--stage", args.stage]
        if args.accept_reviewed:
            forwarded.append("--accept-reviewed")
        if args.include_frozen:
            forwarded.append("--include-frozen")
        return run_script("manager_loop.py", forwarded)

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())