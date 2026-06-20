#!/usr/bin/env python3
"""Recommend completion consolidation, documentation merge, and child-thread archive after acceptance/merge."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


EMPTY_MARKERS = {
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
}


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


def first_line(value: str, fallback: str = "") -> str:
    ignored_fragments = [
        "if needed in future",
        "if needed later",
        "future if needed",
        "only if needed",
        "未来如果需要",
        "后续如需",
        "暂无需",
    ]
    for line in value.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        lowered = stripped.lower()
        if not stripped or lowered in EMPTY_MARKERS:
            continue
        if any(fragment in lowered for fragment in ignored_fragments):
            continue
        return stripped
    return fallback


def real(value: str) -> bool:
    return first_line(value, "") != ""


def thread_block(threads_md: str, name: str) -> str:
    marker = f"## {name}"
    start = threads_md.find(marker)
    if start < 0:
        return ""
    end = threads_md.find("\n## ", start + len(marker))
    return threads_md[start:] if end < 0 else threads_md[start:end]


def label_value(block: str, labels: list[str]) -> str:
    for line in block.splitlines():
        stripped = line.strip()
        for label in labels:
            if stripped.lower().startswith(label.lower()):
                return stripped.split(":", 1)[1].strip() if ":" in stripped else ""
    return ""


def handoff_summary_mentions(summary_md: str, name: str) -> bool:
    lower = summary_md.lower()
    name_lower = name.lower()
    markers = ["accepted", "handoff acceptable", "merged", "completed", "closed"]
    return name_lower in lower and any(marker in lower for marker in markers)


def classify_thread(thread: Path, threads_md: str, handoff_summary: str) -> dict[str, str]:
    status = read(thread / "STATUS.md")
    handoff = read(thread / "HANDOFF.md")
    block = thread_block(threads_md, thread.name)
    status_value = label_value(block, ["Status:"]).lower()
    thread_id = label_value(block, ["Thread ID:", "threadId:"])
    pending_worktree_id = label_value(block, ["pendingWorktreeId:", "Worktree:"])
    blockers = section(status, "Blockers")
    pending = section(status, "Pending Product Manager Confirmation") or section(status, "Pending Master Confirmation")
    summary = section(handoff, "Summary")
    temp_artifacts = section(status, "Temporary Artifacts")
    completion_documents = section(handoff, "Completion Documents")
    combined = f"{status_value}\n{block}\n{status}\n{handoff}".lower()

    accepted_statuses = {"accepted", "merged", "completed", "closed", "archived"}
    accepted = (
        status_value in accepted_statuses
        or handoff_summary_mentions(handoff_summary, thread.name)
        or "status: accepted" in combined
        or "status: merged" in combined
    )
    rework = any(marker in combined for marker in ["rework", "rejected", "返工"])
    blocked = real(blockers)
    needs_pm = real(pending)
    handoff_ready = real(summary)

    if accepted and not blocked and not needs_pm and not rework:
        archive_decision = "archive-ready"
        reason = "accepted/merged with no blocker or pending PM confirmation"
    elif rework:
        archive_decision = "keep-open"
        reason = "rework is required"
    elif blocked:
        archive_decision = "keep-open"
        reason = "blocker still exists"
    elif needs_pm:
        archive_decision = "keep-open"
        reason = "pending product-manager/user decision"
    elif handoff_ready:
        archive_decision = "keep-open"
        reason = "handoff is ready but not accepted/merged yet"
    else:
        archive_decision = "keep-open"
        reason = "thread is still running or not handed off"

    identifier = thread_id if thread_id and "pending" not in thread_id.lower() else pending_worktree_id
    return {
        "name": thread.name,
        "archive_decision": archive_decision,
        "reason": reason,
        "thread_identifier": identifier or "unknown",
        "temporary_artifacts": first_line(temp_artifacts, "None"),
        "completion_documents": first_line(completion_documents, "None"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend completion consolidation, documentation merge, and child-thread archive actions.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--stage", default="current")
    parser.add_argument("--write-report", action="store_true", help="Write .agents/POST_MERGE_CLEANUP.md")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    agents = root / ".agents"
    threads_dir = agents / "threads"
    if not threads_dir.exists():
        raise SystemExit(f"No thread packages found: {threads_dir}")

    threads_md = read(agents / "THREADS.md")
    handoff_summary = read(agents / "HANDOFF_SUMMARY.md")
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    items = [classify_thread(thread, threads_md, handoff_summary) for thread in sorted(threads_dir.iterdir()) if thread.is_dir()]
    archive_ready = [item for item in items if item["archive_decision"] == "archive-ready"]
    keep_open = [item for item in items if item["archive_decision"] != "archive-ready"]
    prompt_files = sorted((agents / "thread-prompts").glob("*.txt")) if (agents / "thread-prompts").exists() else []

    lines = [
        "# Completion Consolidation Report",
        "",
        f"Stage: {args.stage}",
        f"Updated: {now}",
        "",
        "## Child Thread Archive Decisions",
        "",
        "| Thread | Decision | Thread/Worktree | Reason |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(f"| {item['name']} | {item['archive_decision']} | {item['thread_identifier']} | {item['reason']} |" for item in items)
    lines.extend([
        "",
        "## Archive Actions",
        "",
    ])
    if archive_ready:
        lines.extend(f"- {item['name']}: archive Codex window if `set_thread_archived` is available; otherwise record manual archive pending. Identifier: {item['thread_identifier']}" for item in archive_ready)
    else:
        lines.append("- None.")
    lines.extend([
        "",
        "## Keep Open",
        "",
    ])
    if keep_open:
        lines.extend(f"- {item['name']}: {item['reason']}" for item in keep_open)
    else:
        lines.append("- None.")
    lines.extend([
        "",
        "## Completion Records",
        "",
        "- Ensure child `STATUS.md` records final state, verification, cleanup, remaining risks, and next resume state.",
        "- Ensure child `HANDOFF.md` records accepted summary, verification, cleanup, boundary check, risks, open questions, and completion documents.",
        "- Ensure `.agents/HANDOFF_SUMMARY.md`, `.agents/THREADS.md`, `.agents/PROGRESS.md`, and `.agents/DECISIONS.md` record the Product Manager acceptance/merge decision.",
        "",
        "## Documentation Merge Decisions",
        "",
        "- Keep audit trail by default: `.agents/THREADS.md`, `.agents/PROGRESS.md`, `.agents/DECISIONS.md`, `.agents/HANDOFF_SUMMARY.md`, and accepted child `STATUS.md` / `HANDOFF.md`.",
        "- Merge durable, user-facing conclusions into formal project docs only when useful and allowed by the project, such as `README.md`, `CHANGELOG.md`, `docs/**`, roadmap, release notes, or architecture notes.",
        "- Do not delete child task packages unless the user explicitly confirms an archive/prune policy.",
    ])
    doc_items = [item for item in items if item["completion_documents"] != "None"]
    if doc_items:
        lines.append("- Review child-suggested completion documents before merging them into formal project docs:")
        lines.extend(f"  - {item['name']}: {item['completion_documents']}" for item in doc_items)
    else:
        lines.append("- No child-suggested completion documents were recorded.")
    if prompt_files:
        lines.append("- Generated startup prompts can be archived or deleted after all corresponding real child threads are dispatched and recorded:")
        lines.extend(f"  - {path.relative_to(root)}" for path in prompt_files)
    else:
        lines.append("- No `.agents/thread-prompts/*.txt` files found.")
    temp_items = [item for item in items if item["temporary_artifacts"] != "None"]
    if temp_items:
        lines.append("- Review temporary artifacts recorded by child threads:")
        lines.extend(f"  - {item['name']}: {item['temporary_artifacts']}" for item in temp_items)
    else:
        lines.append("- No child temporary artifacts were recorded.")
    lines.extend([
        "",
        "## Required Product Manager Decision",
        "",
        "Update completion records, decide whether to merge durable conclusions into formal project docs, archive child windows marked `archive-ready`, and keep all other windows open. Clean or delete coordination docs only after confirming they are transient and not needed for audit/resume.",
        "",
    ])

    report = "\n".join(lines)
    print(report)
    if args.write_report:
        write(agents / "POST_MERGE_CLEANUP.md", report)
        print(f"Wrote {agents / 'POST_MERGE_CLEANUP.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
