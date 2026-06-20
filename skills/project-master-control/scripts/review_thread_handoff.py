#!/usr/bin/env python3
"""Review a child thread handoff for product-manager acceptance gates."""
from __future__ import annotations

import argparse
import subprocess
import sys
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


def real(value: str) -> bool:
    stripped = value.strip().lower()
    return bool(stripped) and stripped not in {"- none", "- none.", "none", "none.", "not run yet.", "not completed yet.", "- none yet."}


def run_boundary_check(script: Path, thread: Path, base: str | None) -> int:
    cmd = [sys.executable, str(script), "--thread", str(thread)]
    if base:
        cmd += ["--base", base]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--thread", required=True, help="Path to .agents/threads/<thread-name>")
    parser.add_argument("--boundary-script", default=None)
    parser.add_argument("--base", default=None)
    args = parser.parse_args()

    thread = Path(args.thread).resolve()
    status = read(thread / "STATUS.md")
    handoff = read(thread / "HANDOFF.md")
    issues: list[str] = []
    warnings: list[str] = []

    if not status:
        issues.append("STATUS.md missing or empty")
    if not handoff:
        issues.append("HANDOFF.md missing or empty")

    pending = section(status, "Pending Product Manager Confirmation") or section(status, "Pending Master Confirmation")
    if real(pending):
        issues.append("pending product manager confirmation exists")
    if real(section(status, "Blockers")):
        issues.append("STATUS.md reports blockers")

    for required in ["Summary", "Changed Files", "Verification", "Cleanup", "Boundary Check", "Risks"]:
        if not real(section(handoff, required)):
            issues.append(f"HANDOFF.md section not completed: {required}")

    if "not run" in section(handoff, "Verification").lower() or "未运行" in section(handoff, "Verification"):
        issues.append("verification not run")
    if "not completed" in section(handoff, "Cleanup").lower() or "未清理" in section(handoff, "Cleanup"):
        issues.append("cleanup not completed")

    boundary_script = Path(args.boundary_script).resolve() if args.boundary_script else Path(__file__).with_name("check_thread_boundaries.py")
    if boundary_script.exists():
        print("# Boundary Check")
        code = run_boundary_check(boundary_script, thread, args.base)
        if code == 2:
            issues.append("ALLOWLIST boundary violation")
        elif code == 1:
            warnings.append("changes require product manager approval")
    else:
        warnings.append(f"boundary script not found: {boundary_script}")

    print("\n# Handoff Review")
    if issues:
        print("Status: reject")
        print("\nIssues:")
        for item in issues:
            print(f"- {item}")
    else:
        print("Status: acceptable" if not warnings else "Status: acceptable-with-warnings")

    if warnings:
        print("\nWarnings:")
        for item in warnings:
            print(f"- {item}")

    return 2 if issues else (1 if warnings else 0)


if __name__ == "__main__":
    raise SystemExit(main())