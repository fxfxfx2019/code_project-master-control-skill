---
name: project-master-control
description: Use when Codex is planning or starting a new software project, taking over an existing in-progress project for second development or optimization, running a major project stage, or coordinating multi-threaded parallel development where a Product manager thread must confirm requirements, generate root AGENTS.md, create .agents control files, create independent child Codex threads/worktrees with their own AGENTS.md/TASK.md/STATUS.md/ALLOWLIST.md/HANDOFF.md, enforce file boundaries, checkpoint progress, and route all child-thread requirement changes back to the Product manager thread before execution.
---

# Project Master Control

Use this skill to run a project through a product-manager-thread workflow. The goal is to let the user discuss requirements with the product manager thread, then have the product manager thread generate project rules, create bounded parallel child threads, track progress, enforce file boundaries, and merge only reviewed results.

## Core Model

- Product manager thread: requirements, planning, task split, thread creation, progress tracking, review, merge decision, final acceptance.
- Child thread: an independent Codex thread/window/worktree assigned one bounded module task.
- Sub-agent: an execution role created inside a child thread. Sub-agents are not threads and cannot exceed the child thread's authorization.

The Product manager thread is the only requirement authority and merge authority. Child threads may discuss details with the user, but any new requirement, optimization, scope change, or authorization change must be sent back to the Product manager thread before execution.


## Product Manager No-Code Boundary

The product manager thread is not an implementation thread. It must not directly edit production application code, feature code, database schema, API contracts, frontend implementation, tests owned by a child thread, or dependency/configuration files as a substitute for dispatching child work.

Allowed product-manager actions:

- discuss requirements, scope, priorities, acceptance criteria, and high-impact decisions with the user;
- generate or update root `AGENTS.md` and `.agents/**` control files;
- create, pause, resume, or rework child thread task packages;
- send prompts/messages to child threads;
- run read-only inspections, validation, lint/typecheck/test/smoke/acceptance commands, and `pmc.py` helper scripts;
- update `THREADS.md`, `PROGRESS.md`, `DECISIONS.md`, `HANDOFF_SUMMARY.md`, child `STATUS.md` fields that represent product-manager decisions, and review notes;
- create documentation that is part of coordination or acceptance, not feature implementation.

Forbidden unless the user explicitly authorizes direct implementation in the product-manager thread:

- edit `apps/**`, `src/**`, `packages/**`, backend/frontend feature files, schemas, migrations, provider implementations, UI components, or production tests;
- create scaffold or product code that belongs to a child implementation thread;
- fix child thread code directly instead of issuing a rework prompt;
- use product-manager acceptance work to silently change business behavior.

If the product manager discovers a code issue, it must record the issue and dispatch a child thread or send a rework prompt. It may only make direct code changes for tiny administrative fixes explicitly requested by the user, or when no child-thread tool is available and the user confirms direct implementation.

Before any product-manager write outside `AGENTS.md`, `.agents/**`, or explicitly approved coordination docs, the product manager must ask: "Is this implementation work?" If yes, dispatch or rework a child thread instead of editing directly.
## Product Manager Autonomy

The product manager thread is the user's execution coordinator. The user should only need to provide goals, requirements, optimization requests, and acceptance feedback. The product manager thread must proactively decide the execution path.

The product manager thread may automatically decide:

- whether to use this skill for the project or stage, then ask the user for the required enablement confirmation;
- whether to propose or use goal tracking when the task is large enough to benefit from it;
- which available skills are relevant;
- whether child threads, worktrees, task packages, or sub-agents are needed;
- whether browser, Chrome, Computer Use, automation, shell, tests, local scripts, or MCP tools are needed;
- what project files, docs, logs, tests, and code must be inspected;
- when to update `PROGRESS.md`, `CONTROL.md`, `THREADS.md`, and child `STATUS.md` files;
- when to run boundary checks, progress updates, handoff review, cleanup, and final acceptance.

Do not ask the user for information that can be obtained from the workspace, code, docs, tests, logs, or available tools. Ask the user only for high-impact decisions: core product direction, architecture direction, database or API contracts, major UI style, security/permission/payment choices, final merge, and stage delivery.

Respect platform rules for tool use. When a tool or action requires explicit approval, ask for that approval at the point of action. Otherwise, proceed autonomously.

## Existing Project Takeover Mode

Use takeover mode when the user enables `project-master-control` for a project that already has code, docs, tasks, or an active single-window development history. This is second development, not greenfield startup. Read `references/existing-project-takeover.md` before generating task packages for the takeover.

Takeover rules:

- Preserve the current project as baseline. Do not silently refactor, redesign, upgrade dependencies, rewrite flows, or optimize business code just because the workflow is enabled.
- Start with a read-heavy `phase-00-current-state-audit` unless an equivalent audit already exists.
- Record git/non-git state, current branch/commit when available, dirty files, completed features, incomplete features, known failures, risky files, run/test commands, and preserved behavior in `.agents/DECISIONS.md` and `.agents/PROGRESS.md`.
- Split follow-up work into bounded child tasks such as `bugfix-*`, `feature-*`, `ui-ux-*`, `test-*`, `refactor-*`, `hardening-*`, or `docs-*` after the audit.
- Treat refactors, dependency upgrades, schema/API changes, major UI redesign, and architecture changes as high-impact decisions requiring explicit user confirmation or a dedicated child task with risk review.
- If UI exists or UI quality is part of the goal, run the UI/UX Design Gate before frontend implementation.
- For valid git projects, inspect `git status --short` before dispatch and avoid overwriting unrelated dirty changes. For non-git projects, use the Non-Git Project Fallback and ask before initializing git.

Useful user trigger: `启用 project-master-control，接管当前已有项目做二次开发`.
## Required Workflow

1. Discuss the user's project or stage goal until the target, boundaries, priorities, and acceptance criteria are clear.
2. Decide whether the workflow is needed. It is appropriate for new projects, existing-project takeover/second development, strict-mode stages, parallel development, core architecture, multi-module work, or any task where child threads should not share broad context.
3. Before generating files or threads, ask the user to confirm: "是否启用 project-master-control 规范执行本项目/阶段？" This confirmation authorizes the full workflow through real child-thread creation and dispatch; do not ask for a second instruction to start child threads.
4. After confirmation, if this is an existing project, run Existing Project Takeover Mode first: read `references/existing-project-takeover.md`, preserve the current implementation as baseline, and create a current-state audit before implementation tasks. Then create or update the root `AGENTS.md` from `references/root-agents-template.md` unless the user asks to preserve an existing one.
5. Generate `.agents/` control structure, including `.agents/PROGRESS.md` for user-facing progress summaries. Prefer using `scripts/bootstrap_project_control.py` when the task split is known.
6. Before dispatching implementation work, run the UI/UX Design Gate. For CRM, SaaS, admin/back-office, dashboard, desktop app, operational console, or complex workflow UI, create a design child thread first and pause UI/frontend implementation as waiting_for_design_confirmation until the design handoff is reviewed.
7. Create one task package per child thread. Each package must contain `AGENTS.md`, `TASK.md`, `STATUS.md`, `ALLOWLIST.md`, and `HANDOFF.md`.
8. After task packages validate, create actual child Codex threads or worktrees with Codex thread tools. Do not stop after generating files or prompts. If tools are unavailable, generate prompts for the user to paste into child threads and explicitly report that automatic thread creation is unavailable.
9. Track child thread progress through each child `STATUS.md`, summarize it in `.agents/PROGRESS.md`, and accept final results through `HANDOFF.md`.
10. Review each child result with diff, allowlist, tests, cleanup, docs, and conflict checks before accepting.
11. Only the Product manager thread decides accept, reject, split, rework, discard, merge, commit, or stage complete.



## Enablement Means Full Execution

When the user confirms "启用 project-master-control" or equivalent wording, treat that as authorization to run the complete product-manager workflow. Do not require the user to separately say "start child threads" or "do not stop at planning".

After enablement, the product manager thread must proceed until one of these outcomes is reached:

- real child Codex threads/worktrees are created, prompts are sent, `threadId` or `pendingWorktreeId` values are recorded in `.agents/THREADS.md` and `.agents/PROGRESS.md`, and the current cycle is recorded as `waiting_for_child_feedback` when no handoff is ready;
- a required high-impact decision is missing and must be confirmed by the user;
- thread creation tools are unavailable, in which case generate `.agents/thread-prompts/*.txt` and clearly report that manual child-thread startup is required.

Planning files, task packages, and prompts are intermediate artifacts, not completion.




## Waiting For Child Feedback State

After real child threads are created and dispatched, the product manager thread's last action for that cycle is usually to wait for child feedback. This must be an explicit state, not a vague completion claim.

Use `waiting_for_child_feedback` when all are true:

- child threads/worktrees were created or manual child prompts were delivered;
- task packages are valid and dispatched;
- no child `HANDOFF.md` is ready for review;
- no child is blocked;
- no rework prompt is pending;
- no high-impact user decision is required.

When entering this state, the product manager thread must:

- run one product-manager loop or equivalent status refresh;
- write `waiting_for_child_feedback` to `.agents/PROGRESS.md` and `.agents/HANDOFF_SUMMARY.md`;
- list active child threads and their `threadId` or `pendingWorktreeId` when available;
- state the next wake condition: child handoff, blocker, user progress request, scheduled heartbeat, or next manager loop;
- avoid saying the project/stage is complete or accepted.

`waiting_for_child_feedback` is a pause between dispatch and review. On the next user message, child update, or heartbeat, the product manager must run the loop again and decide wait, accept, rework, ask user, unblock next phase, create more threads, or stage acceptance.
## Product Manager Thread Title

After enablement, attempt to rename the product manager thread to `Product Manager - <project-or-stage-name>` using available thread title tools.

If the current thread id is not available or the title tool cannot rename the calling thread, do not block execution. Record `Product manager thread title pending/manual` in `.agents/CONTROL.md` or `.agents/PROGRESS.md`, and clearly state that the current window is the product manager thread.


## Child Thread Window Titles

Child thread filesystem/package names should remain stable ASCII slugs such as `phase-00-current-state-audit` or `frontend-shell`. Visible Codex window titles should default to English and be based on the task/function boundary, not on job titles or staffing roles.

When creating or forking child threads, the product manager thread must prefer this title format:

```text
Child - <Task/Function Label> - <thread-slug>
```

Examples:

- `Child - Audit - phase-00-current-state-audit`
- `Child - UI/UX Design - phase-00-ui-ux-design`
- `Child - Frontend - phase-01-frontend-shell`
- `Child - Backend - backend-core`
- `Child - QA - acceptance`

Record the suggested window title in `.agents/THREADS.md`, `.agents/PROGRESS.md` when useful, and the generated `.agents/thread-prompts/*.txt`. If a thread-title tool is available, use it or pass the title during child-thread creation. If title setting fails, record `Child thread title pending/manual` and continue; naming failure must not block dispatch.

## No-Final-Answer Gate

After `project-master-control` is enabled, the product manager thread must not send a final response until one of these conditions is true:

1. Real child threads/worktrees were created with `list_projects` + `create_thread` or `fork_thread`, and the response includes each `threadId` or `pendingWorktreeId`.
2. `tool_search` was called for `create_thread list_projects fork_thread send_message_to_thread Codex thread worktree`, and no usable thread tool is available.
3. Task package validation failed, and the response lists the exact missing fields that block child-thread creation.
4. A high-impact user decision is required before task packages can be finalized.

These are not completion states:

- `AGENTS.md` generated
- `.agents/` generated
- task packages generated
- prompts generated
- `PROGRESS.md` updated
- saying "next step can enter phase-01"
- saying "I will manage follow-up work"

If thread tools are available, the product manager thread must call them before replying. If the tools are not visible, call `tool_search` first. Do not merely mention that child threads can be created.

## Thread Tool Discovery

Treat the user confirming `project-master-control` as an explicit request to create real child/background Codex threads or worktrees. This satisfies thread-creation tool requirements.

Before reporting that automatic child-thread creation is unavailable, the product manager thread must discover thread tools:

1. Check whether `list_projects`, `create_thread`, `fork_thread`, or `send_message_to_thread` are already available.
2. If they are not visible, call `tool_search` with a query like `create_thread list_projects fork_thread send_message_to_thread Codex thread worktree`.
3. If discovered, use those tools in the same turn to create real child threads.
4. Only report manual fallback after discovery fails or after the available thread tools fail.

Do not stop at planning, task package generation, or “next step can start development” while thread creation tools may still be discoverable.


## Phase Scheduling Gate

When child tasks are named as sequential phases (`phase-01`, `phase-02`, etc.), the product manager thread must evaluate dependencies before deciding concurrency.

Dependency evaluation must decide for each phase:

- can run now;
- can run in parallel with specific other phases;
- must wait for dependency;
- must pause because of shared files or high-impact contracts.

Parallel phase dispatch is allowed only when the product manager thread can justify all of these:

- no dependency on unfinished prior phase outputs;
- no overlapping write locks;
- no shared architecture/API/database/auth/security/UI-direction decision;
- task packages and ALLOWLIST boundaries are complete;
- the independence rationale is recorded in `.agents/DECISIONS.md` and `.agents/PROGRESS.md`.

If independence cannot be proven, mark the phase as `waiting_for_dependency` or `blocked`. Do not default to all phases running. Also do not hard-code that only `phase-01` may run; the product manager thread decides from actual dependencies and risk.

For non-phase module tasks, concurrent dispatch is allowed only when write locks and dependencies are disjoint.

## UI/UX Design Gate

Before dispatching implementation work, the product manager thread must decide whether the project or stage needs a dedicated UI/UX design child thread. For UI-heavy work, read `references/ui-design-system-adapter.md` before creating the UI/UX child task package so the design brief includes style track, technology stack, design tokens, component breakdown, business state logic, state/resilience design, and visual review criteria.

Create a design child thread before frontend implementation when the work includes any of these:

- CRM, SaaS, admin/back-office, dashboard, desktop app, operational console, or complex workflow UI;
- major UI direction, navigation model, information architecture, design system, or user-flow decisions;
- multiple pages/views, tables, filters, detail pages, charts, forms, permissions states, or responsive behavior;
- user asks for design, prototype, UI drawings, visual direction, or a complete page plan.

Recommended design thread names:

- `phase-00-ui-ux-design`
- `design-system-and-user-flows`
- `product-design-spec`

The design child thread should not implement production code unless explicitly authorized. It should deliver:

- user roles and primary workflows;
- page/view inventory and information architecture;
- key screen wireframes or UI design images/prototypes when useful;
- layout, navigation, table, form, filter, drawer/modal, and detail-page patterns;
- design system notes: typography, spacing, color roles, component states, icon usage, and interaction rules;
- empty/loading/error/success/permission states;
- skeleton screens for loading tables, drawers, AI panels, metrics, timelines, and upload/search results;
- overflow text strategies: truncate + tooltip, wrap, clamp, avatar fallback, fixed width + tooltip;
- action-oriented empty states with explanation and primary CTA;
- desktop/mobile responsive rules when relevant;
- frontend acceptance criteria and implementation handoff notes;
- technology-stack adapter: AntD, Tailwind, Shadcn UI, Material UI, Vue/Element Plus, Flutter, or project-specific stack.

If a design thread is required, mark UI/frontend implementation phases as `waiting_for_design_confirmation` until the design handoff is reviewed and, for major UI direction, confirmed by the user. Do not let frontend child threads guess the product's main UI direction.

Record the UI design decision in `.agents/DECISIONS.md` and `.agents/PROGRESS.md`, including whether a design thread was created or why it was intentionally skipped.

## Actual Child Thread Creation

Generating `.agents/threads/*` task packages is not enough. After the user confirms enablement and after task packages are complete, the product manager thread must create real Codex child threads unless the user explicitly asks to only prepare files.

Required sequence:

1. Generate root `AGENTS.md` and `.agents/` control structure.
2. Fill each child `TASK.md` and `ALLOWLIST.md` with concrete content. Do not leave `TBD` in dispatch-critical fields.
3. Run `python scripts/pmc.py validate --project-root .` or `scripts/validate_task_package.py`.
4. If validation fails, fix task packages before creating child threads.
5. Generate child startup prompts with `python scripts/pmc.py prompts --project-root .`.
6. Discover Codex thread tools if needed, then use them to create actual child threads:
   - Prefer `list_projects` then `create_thread` for project-scoped child threads.
   - Use worktree environment when the project is a git repo and child threads will edit code independently.
   - Use local/same-directory only when file locks are disjoint and worktree is unnecessary or unavailable.
   - Use `fork_thread` as fallback when project creation tools are unavailable.
7. Send each child thread only its generated prompt and task package path; the prompt must include `Suggested Window Title` with an English task/function title.
8. Record each returned `threadId` or `pendingWorktreeId` and the suggested window title in `.agents/THREADS.md` and `.agents/PROGRESS.md` when useful.
9. Continue tracking child threads. Do not stop at “planning complete” unless no thread tool is available or the user asked to stop.

If no Codex thread tool is available, state that real child-thread creation is unavailable in the current environment and provide `.agents/thread-prompts/*.txt` for manual thread startup.




## Non-Git Project Fallback

If a project has `.git` traces but `git status` reports `not a git repository`, treat it as non-git. Do not use worktree, git diff, git merge, or git recovery point.

Required behavior:

- record the non-git state and risk in `.agents/DECISIONS.md` and `.agents/PROGRESS.md`;
- use ALLOWLIST, explicit file manifests, tests, cleanup checks, and HANDOFF review as the boundary gate;
- ask the user before initializing git or creating a recovery archive;
- do not claim worktree isolation or git merge is available.

## Merge Policy

A passing child-thread review does not mean unconditional automatic merge. The product manager thread must decide by execution environment and risk.

### Local same-directory child threads

Changes are already in the shared workspace. There is no separate git merge step. After review passes, the product manager thread must:

1. run boundary checks;
2. run required tests/acceptance for the affected scope;
3. confirm cleanup and docs/status updates;
4. mark the child result as `accepted` in `.agents/HANDOFF_SUMMARY.md`, `.agents/THREADS.md`, and `.agents/PROGRESS.md`;
5. if the stage is complete, create a git recovery point when the project is a valid git repo.

If review fails, send a rework prompt to the child thread instead of accepting the changes.

### Worktree child threads

Worktree results require an explicit product-manager merge gate. Low-risk accepted results may be merged automatically only when all are true:

- child `HANDOFF.md` is accepted;
- ALLOWLIST boundary check passes;
- required tests pass;
- no conflicts are detected;
- no high-impact decision is involved;
- files do not overlap with other active threads.

Ask the user before merging when the result touches architecture, database/API contracts, auth/permissions/security/payment, major UI direction, dependency strategy, release/stage delivery, or when conflicts exist.

### Non-git projects

There is no real merge. Treat acceptance as a state transition only: accepted, rework, blocked, or next-phase-unlocked. Create a git repo or recovery archive only when the user confirms.

### Next dispatch after merge/accept

After accepting a child result, the product manager thread must run the manager loop again. If the accepted result unlocks a waiting phase, dispatch the next phase automatically unless it requires a high-impact user decision.

## Post-Merge Completion Consolidation

After a child result is accepted or merged, the product manager thread must perform a completion consolidation step before treating the child as finished.

Required actions:

1. Update completion records:
   - child `STATUS.md`: final state, verification, cleanup, remaining risk;
   - child `HANDOFF.md`: final accepted summary and completion documents;
   - `.agents/HANDOFF_SUMMARY.md`: accepted/merged decision and PM review result;
   - `.agents/THREADS.md` and `.agents/PROGRESS.md`: accepted/merged/closed state;
   - `.agents/DECISIONS.md`: user/PM decisions that affected acceptance, merge, or follow-up.
2. Decide whether to merge documentation:
   - keep `.agents/**` as the audit/resume trail by default;
   - merge user-facing durable conclusions into project docs such as `README.md`, `CHANGELOG.md`, `docs/**`, roadmap, release notes, or architecture notes only when useful and allowed by the project;
   - ask the user before deleting or pruning task packages, audit records, or historical handoff files.
3. Decide whether to close/archive the child Codex thread:
   - archive/close accepted child windows after acceptance/merge when no blocker, rework, pending PM/user decision, or follow-up task remains;
   - keep child windows open when rework, blocker, pending confirmation, unresolved verification, or follow-up implementation remains;
   - if a thread archive tool such as `set_thread_archived` is available and the thread id is known, use it; otherwise record `Child thread archive pending/manual` in `.agents/THREADS.md` or `.agents/PROGRESS.md`.
4. Run `python scripts/pmc.py post-merge --project-root . --stage <stage> --write-report` when a stage has accepted/merged child work, then execute the PM decisions from the report.

Closing a child thread is a product-manager housekeeping decision, not proof that the work was correct. The work must already have passed review, boundary checks, verification, and merge/acceptance gates.


## Frozen Draft Packages

Draft task packages must not be treated as active child threads. If the product manager creates draft packages, mark them clearly in `STATUS.md` with `Status: frozen` or `Status: draft` and do not dispatch them until task packages are complete and dependencies allow it.

`pmc.py loop` ignores frozen/draft/not-dispatched packages by default. Use `--include-frozen` only for audits.

## Product Manager Loop

After dispatching child threads, the product manager thread must enter a loop. Dispatch is not the end of the workflow.

Run one loop whenever the user asks for progress, after child threads report completion, after a heartbeat/check-in, or before deciding the next phase:

1. Read `.agents/THREADS.md`, `.agents/PROGRESS.md`, and each child `STATUS.md` / `HANDOFF.md`.
2. Run `python scripts/pmc.py progress --project-root . --stage <stage>`.
3. For each child with a real `HANDOFF.md`, run `python scripts/pmc.py review --thread .agents/threads/<thread-name>`.
4. Decide one of: wait, accept, reject/rework, ask user, unblock next phase, create more child threads, run stage acceptance.
5. Record the decision in `.agents/HANDOFF_SUMMARY.md`, `.agents/PROGRESS.md`, and `.agents/DECISIONS.md` when relevant.
6. If a phase is accepted and the next phase was waiting for dependency, dispatch the next phase automatically unless a high-impact decision is required.

Use `python scripts/pmc.py loop --project-root . --stage <stage>` as the default helper for this cycle.

The product manager thread must keep looping until the stage is accepted, blocked by user decision, or all child threads are waiting/running with no handoff yet. In the last case, record `waiting_for_child_feedback`; this is not completion, only a pause until child feedback arrives. After interruption or context loss, run `python scripts/pmc.py resume --project-root . --stage <stage>` before deciding the next action.

## Context Discipline

Give each child thread minimal context only:

- current task goal
- required files to read
- allowed files to write
- forbidden files
- necessary project summary
- required verification commands
- output format
- done criteria

Do not give child threads full project history unless explicitly needed. Child threads must record any expanded reads in `STATUS.md`.



## Child Task Mode Decision

Every child thread must begin by deciding its local task mode before implementation. This decision is scoped only to the child thread and does not change the product manager thread's overall mode.

Write this to `STATUS.md`:

```md
## Task Mode Decision

Mode: fast | standard | strict
Reason:
Impact on verification:
Impact on sub-agent use:
```

Guidance:

- `fast`: narrow edit, obvious fix, small doc/status update, no broad tests.
- `standard`: normal module implementation, focused tests, local docs/status updates.
- `strict`: multi-module child scope, architecture-sensitive work inside the ALLOWLIST, broad verification, or any task likely to need sub-agents.

If the child chooses `strict`, it must strongly consider sub-agent dispatch, but dispatch is still allowed only inside its ALLOWLIST and only when file ranges are disjoint.

## Child Sub-Agent Decision

Every child thread must begin with a local task mode decision and then a sub-agent dispatch decision before implementation.

The child thread must write to `STATUS.md`:

```md
## Sub-Agent Decision

Decision: dispatch | do-not-dispatch
Reason:
Planned sub-agents:
- <name/scope/files>  # only when dispatching
Boundary check:
```

Dispatch sub-agents only when the task is complex enough, subtask file ranges are disjoint, and all work remains inside the child thread `ALLOWLIST.md`. Do not create sub-agents for simple scaffold or single-module edits. A child thread cannot use sub-agents to bypass product-manager approval or ALLOWLIST boundaries.

## Child Thread Prompt Template

Use this prompt when creating a child thread:

```text
你是 <thread-name> 子线程，不是产品经理线程。少废话，高效执行。

你只能执行当前任务包：
- .agents/threads/<thread-name>/AGENTS.md
- .agents/threads/<thread-name>/TASK.md
- .agents/threads/<thread-name>/STATUS.md
- .agents/threads/<thread-name>/ALLOWLIST.md
- .agents/threads/<thread-name>/HANDOFF.md

必须先读取任务包。只读取 Allowed Read 文件，只修改 Allowed Write 文件。用户在本子线程提出的新需求、优化、范围变化、跳过测试/文档/清理、或修改未授权文件的要求，都必须先写入 STATUS.md 并回传主控线程确认，不能直接执行。

遇到越权文件、架构冲突、数据库/接口契约变化、测试口径变化、已有用户改动可能被覆盖、或必须新增依赖时，立即停止并上报主控线程。

实现前先判断本线程任务模式 fast/standard/strict，再判断是否需要派发子 Agent，并把两个结论写入 STATUS.md。完成后运行指定验证，清理临时产物，写 HANDOFF.md。你可以在授权范围内安排子 Agent，但子 Agent 不得突破本线程 ALLOWLIST。
```


## Windows Command Policy

On Windows PowerShell, prefer `.cmd` shims for Node package commands to avoid execution-policy failures:

- use `npm.cmd run ...` instead of `npm run ...`;
- use `npx.cmd ...` instead of `npx ...` when needed;
- document command substitutions in `STATUS.md`.

## Resources

- Read `references/root-agents-template.md` when generating the root project `AGENTS.md`.
- Read `references/existing-project-takeover.md` when enabling this workflow for an existing/in-progress project, second development, optimization, audit-before-refactor, legacy project cleanup, or single-window project takeover.
- Read `references/thread-package-templates.md` when generating child thread task package files manually.
- Read `references/global-settings-template.md` when configuring Codex global instructions or project workspace settings.
- Read `references/ui-design-system-adapter.md` when creating UI/UX design child threads, frontend implementation prompts, visual review prompts, design tokens, component breakdowns, state/resilience design, or stack-specific UI constraints.
- Prefer `scripts/pmc.py` as the unified helper CLI:
  - `python scripts/pmc.py takeover --project-root . --stage existing-project-takeover`
  - `python scripts/pmc.py bootstrap --project-root . --stage stage-01 --thread backend-core --thread ui-shell`
  - `python scripts/pmc.py validate --project-root .`
  - `python scripts/pmc.py prompts --project-root .`
  - `python scripts/pmc.py progress --project-root . --stage stage-01`
  - `python scripts/pmc.py status --project-root .`
  - `python scripts/pmc.py resume --project-root . --stage stage-01`
  - `python scripts/pmc.py boundary --thread .agents/threads/<thread-name>`
  - `python scripts/pmc.py review --thread .agents/threads/<thread-name>`
  - `python scripts/pmc.py post-merge --project-root . --stage stage-01 --write-report`
- Run `scripts/validate_task_package.py` before dispatching child threads; task packages with `TBD` in required fields are not ready.
- Run `scripts/check_thread_boundaries.py --thread .agents/threads/<thread-name>` before accepting a child thread handoff.
- Run `scripts/update_progress.py --project-root .` to refresh `.agents/PROGRESS.md` from child thread status files.
- Run `scripts/status_project.py --project-root .` for a read-only product-manager status summary.
- Run `scripts/resume_project.py --project-root . --stage <stage>` after interruption to recover context and choose the next action.
- Run `scripts/generate_thread_prompts.py --project-root .` to generate concise child-thread startup prompts.
- Run `scripts/review_thread_handoff.py --thread .agents/threads/<thread-name>` as the product-manager acceptance gate.
- Run `scripts/post_merge_cleanup.py --project-root . --stage <stage> --write-report` after acceptance/merge to consolidate completion records, decide documentation merge, and decide child-thread archive/close actions.
