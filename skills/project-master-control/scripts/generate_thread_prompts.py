#!/usr/bin/env python3
"""Generate concise startup prompts for child Codex threads."""
from __future__ import annotations

import argparse
from pathlib import Path


def suggested_window_title(name: str) -> str:
    lower = name.lower()
    rules = [
        ("current-state-audit", "Audit"),
        ("ui-ux", "UI/UX Design"),
        ("design", "UI/UX Design"),
        ("frontend", "Frontend"),
        ("ui", "Frontend"),
        ("backend", "Backend"),
        ("platform", "Platform"),
        ("knowledge", "Knowledge AI"),
        ("data", "Data Connectors"),
        ("connector", "Data Connectors"),
        ("outbound", "Outbound"),
        ("wecom", "WeCom"),
        ("growth", "Growth Analytics"),
        ("analytics", "Growth Analytics"),
        ("delivery", "Delivery Hardening"),
        ("hardening", "Delivery Hardening"),
        ("test", "QA"),
        ("acceptance", "QA"),
        ("planning", "Planning"),
        ("implementation", "Implementation"),
    ]
    label = "Task"
    for token, title in rules:
        if token in lower:
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
        prompt = f"""Suggested Window Title: {title}\n\n你是 {name} 子线程，不是产品经理线程。\n\n先读取并严格遵守：\n- .agents/threads/{name}/AGENTS.md\n- .agents/threads/{name}/TASK.md\n- .agents/threads/{name}/ALLOWLIST.md\n- .agents/threads/{name}/STATUS.md\n\n执行要求：\n1. 少废话，高效执行。\n2. 实现前先判断本线程任务模式 fast/standard/strict，并写入 STATUS.md。\n3. 再判断是否需要派发子 Agent，并写入 STATUS.md。\n4. 只读取 Allowed Read，除非必要并记录到 STATUS.md。\n5. 只修改 Allowed Write。\n6. 用户在本线程提出新需求、优化、范围变化、跳过测试/文档/清理、或修改未授权文件时，写入 STATUS.md 并回传产品经理线程确认，不能直接执行。\n7. 遇到越权文件、架构冲突、数据库/接口契约变化、测试口径变化、依赖变化、已有用户改动可能被覆盖时，停止并上报。\n8. 完成后运行指定验证，清理临时产物，更新 STATUS.md，写 HANDOFF.md。\n\n输出只包含：当前进度、阻塞、验证结果、风险、需要产品经理确认的问题、交付摘要。\n"""
        target = out_dir / f"{name}.txt"
        target.write_text(prompt, encoding="utf-8")
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
