# project-master-control Usage Guide

This repository contains a Codex skill. It is designed for Codex Desktop / Codex environments that support skills, local file access, shell commands, and optionally Codex thread tools.

## Install

Ask Codex to install the skill from this path:

```text
Install the Codex skill from:
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/project-master-control
```

Restart Codex after installation so the skill can be discovered.

## Core Idea

`project-master-control` turns one Codex conversation into a Product Manager control thread.

The Product Manager thread owns:

- requirements and acceptance criteria;
- task decomposition;
- child thread / worktree dispatch;
- file boundary control through `ALLOWLIST.md`;
- progress tracking through `.agents/**`;
- review, rework, merge, and stage acceptance decisions.

Child threads own only their assigned task package:

- `.agents/threads/<thread>/AGENTS.md`
- `.agents/threads/<thread>/TASK.md`
- `.agents/threads/<thread>/STATUS.md`
- `.agents/threads/<thread>/ALLOWLIST.md`
- `.agents/threads/<thread>/HANDOFF.md`

Child threads must not expand scope, write outside their allowlist, or merge directly.

When a child thread finishes, blocks, or needs a Product Manager decision, it must prepare one `PM_FEEDBACK` message for the Product Manager thread:

```text
PM_FEEDBACK
Thread: <thread-name>
Status: completed | blocked | needs-product-manager-decision | rework-complete
Summary: <one-line result>
Verification: <pass/fail/not-run and command summary>
Risks: <none or concise risk>
Handoff: .agents/threads/<thread-name>/HANDOFF.md
Next: review | rework | user-decision | unblock-next
```

If `send_message_to_thread` is available and the Product Manager thread id is known, the child thread should send this message back directly. Otherwise it should write the message in `HANDOFF.md` and include it in its final response.

## When To Use

Use this skill for:

- new software projects;
- major project stages;
- multi-module implementation;
- parallel child-thread development;
- existing project takeover and second development;
- UI-heavy SaaS, CRM, dashboard, admin, desktop, or operational tools;
- work requiring explicit merge gates, file locks, and resumable state.

Do not use it for tiny single-file changes where normal Codex execution is faster.

## Starting A New Project Or Stage

In the Product Manager conversation, say:

```text
Enable project-master-control
```

The Product Manager thread should then:

1. confirm the project goal, boundaries, priorities, and acceptance criteria;
2. create or update root `AGENTS.md`;
3. create `.agents/**`;
4. split bounded child task packages;
5. validate packages;
6. generate child startup prompts;
7. create real Codex child threads or worktrees when tools are available;
8. record returned `threadId` or `pendingWorktreeId`;
9. enter the Product Manager loop until accepted, blocked, or waiting for child feedback.

## Taking Over An Existing Project

For an existing project, say:

```text
Enable project-master-control and take over the current existing project for second development
```

The Product Manager thread should treat the current implementation as the baseline. It should not automatically refactor, redesign, upgrade dependencies, or rewrite behavior just because the workflow is enabled.

The first step should usually be `phase-00-current-state-audit`, which records:

- project structure;
- git or non-git state;
- dirty files;
- existing run/build/test commands;
- completed, partial, and missing features;
- known failures and risk files;
- recommended next child tasks.

## UI/UX Design Gate

For CRM, SaaS, dashboard, admin, desktop, or complex workflow UI, the Product Manager should usually create a UI/UX design child thread before frontend implementation.

The design handoff should cover:

- users and workflows;
- page inventory and information architecture;
- layout, navigation, tables, filters, forms, drawers, modals, charts;
- design tokens and stack-specific constraints;
- skeleton loading states;
- overflow text strategies;
- empty states with clear actions;
- disabled, error, permission, loading, success, hover, focus states;
- frontend acceptance criteria.

Frontend implementation should wait for design confirmation when major UI direction is involved.

## Product Manager Loop

The Product Manager loop reads child state, reviews handoffs, and decides the next action:

```text
python scripts/pmc.py status --project-root .
python scripts/pmc.py resume --project-root . --stage <stage>
python scripts/pmc.py loop --project-root . --stage <stage>
```

Possible outcomes:

- wait for child feedback;
- accept a handoff;
- send a rework prompt;
- ask the user for a high-impact decision;
- unblock the next phase;
- create more child threads;
- run stage acceptance.

`waiting_for_child_feedback` is a valid pause state. It means child threads are still running and no handoff is ready.

A received `PM_FEEDBACK` message is a wake signal. The Product Manager should run the loop, review the referenced `HANDOFF.md`, and decide accept, rework, ask user, unblock the next phase, create more threads, or stage acceptance.

## Review And Merge

A passing child handoff does not mean unconditional merge.

The Product Manager must check:

- allowlist boundary;
- changed files;
- required verification;
- cleanup;
- conflicts;
- documentation;
- high-impact risk.

Local same-directory child threads do not have a real merge step; their work is already in the shared workspace and must be accepted or reworked through PM review.

Worktree child threads require a merge gate. High-impact changes require user confirmation before merge.

## Post-Merge Completion Consolidation

After child work is accepted or merged, run:

```text
python scripts/pmc.py post-merge --project-root . --stage <stage> --write-report
```

This generates `.agents/POST_MERGE_CLEANUP.md`.

The report helps the Product Manager decide:

- whether completion records are updated;
- whether durable conclusions should be merged into formal project docs;
- whether `.agents/**` audit records should be kept, archived, or pruned;
- whether accepted child Codex windows can be archived/closed.

Accepted child windows can be closed only when no blocker, rework, pending decision, unresolved verification, or follow-up task remains.

## Common Commands

Run these from the project root after the skill has generated or copied the scripts into the project:

```text
python scripts/pmc.py takeover --project-root . --stage existing-project-takeover
python scripts/pmc.py bootstrap --project-root . --stage stage-01 --thread backend-core --thread frontend-shell
python scripts/pmc.py validate --project-root .
python scripts/pmc.py prompts --project-root .
python scripts/pmc.py status --project-root .
python scripts/pmc.py resume --project-root . --stage stage-01
python scripts/pmc.py loop --project-root . --stage stage-01
python scripts/pmc.py boundary --thread .agents/threads/<thread-name>
python scripts/pmc.py review --thread .agents/threads/<thread-name>
python scripts/pmc.py post-merge --project-root . --stage stage-01 --write-report
```

On Windows PowerShell, prefer `npm.cmd` and `npx.cmd` for Node commands.

## Repository Files Created In A Project

Typical generated project structure:

```text
.agents/
  CONTROL.md
  PROGRESS.md
  THREADS.md
  DECISIONS.md
  HANDOFF_SUMMARY.md
  POST_MERGE_CLEANUP.md
  thread-prompts/
  threads/
    <thread-name>/
      AGENTS.md
      TASK.md
      STATUS.md
      ALLOWLIST.md
      HANDOFF.md
```

These files are coordination and audit records. Keep them by default unless the Product Manager decides they are no longer needed and the user agrees to prune them.

## Important Limitations

- This skill coordinates Codex behavior; it is not a package manager or CI tool.
- Real child-thread creation depends on available Codex thread tools.
- If thread tools are unavailable, the Product Manager should generate `.agents/thread-prompts/*.txt` for manual startup.
- The Product Manager should not write production code unless explicitly authorized.
- High-impact changes require user confirmation.
