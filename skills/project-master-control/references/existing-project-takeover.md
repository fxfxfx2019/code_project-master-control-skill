# Existing Project Takeover

Use this reference when the user wants to enable `project-master-control` for a project that already has code, docs, tasks, or an active single-window development history. Treat this as controlled second development, not a greenfield startup.

## Takeover Principle

The product manager thread must preserve the current project as the baseline. Enabling the workflow does not authorize silent refactors, broad rewrites, or automatic product optimization.

Default behavior:

- audit first;
- record the current state;
- keep existing working behavior intact;
- split follow-up optimization, repair, UI redesign, tests, and refactors into bounded child-thread tasks;
- ask the user before high-impact changes, migrations, architecture shifts, or replacing existing flows.

## Required Takeover Sequence

1. Confirm the user wants existing-project takeover, for example: `启用 project-master-control，接管当前已有项目做二次开发`.
2. Identify the project root, git state, package manager, main apps/packages, test commands, and current run commands.
3. Create or update root `AGENTS.md` and `.agents/**` without rewriting business code.
4. Create a `phase-00-current-state-audit` task before implementation tasks unless an equivalent audit already exists.
5. If the project has UI, also create `phase-00-ui-ux-design` or mark why design review is skipped.
6. If the project has weak tests or unknown quality, create `phase-00-test-and-risk-audit` or include test/risk audit inside current-state audit.
7. Record baseline status in `.agents/DECISIONS.md` and `.agents/PROGRESS.md`:
   - current branch/commit or non-git state;
   - known completed features;
   - known incomplete features;
   - known failing tests/build issues;
   - known user-visible behavior that must be preserved;
   - files or directories that are risky to touch.
8. Dispatch only bounded follow-up child threads after task package validation and dependency evaluation.
9. Run product-manager loop after each audit or implementation handoff and decide rework, accept, unblock, or create more child threads.

## What Takeover Must Not Do

Do not treat takeover as permission to:

- re-architect the project;
- rewrite UI globally;
- normalize formatting across the repo;
- upgrade dependencies;
- change database schemas or API contracts;
- replace working flows;
- delete historical docs or local state;
- initialize git or create worktrees in a non-git project;
- merge child work without the normal merge gate.

These actions require explicit user confirmation or a dedicated child task with clear risk review.

## Current-State Audit Child Thread

Recommended name: `phase-00-current-state-audit`.

This child thread is read-heavy by default. It should write only coordination docs unless explicitly authorized.

Required outputs:

- project map: apps, packages, services, important docs, config, scripts;
- current run/test commands and whether they pass;
- feature inventory: done, partial, missing, unknown;
- risk inventory: failing tests, fragile files, security/auth/payment/data risks, generated files, large untracked changes;
- UI inventory when relevant: pages, routes, components, design-system state, obvious UX gaps;
- recommended next child-thread tasks with suggested ALLOWLIST boundaries;
- baseline preservation notes: behavior and files that should not be changed without confirmation.

## Second-Development Task Types

After audit, split work by intent instead of mixing changes:

- `bugfix-*`: narrow repairs for known failures;
- `feature-*`: new product capability;
- `ui-ux-*`: design, visual quality, interaction states, responsive behavior;
- `test-*`: test coverage, smoke tests, fixtures, acceptance gates;
- `refactor-*`: internal cleanup with no behavior change;
- `hardening-*`: reliability, security, permissions, logging, delivery checks;
- `docs-*`: documentation and handoff cleanup.

Refactor tasks must have explicit no-behavior-change acceptance criteria and focused verification. UI redesign tasks must pass the UI/UX Design Gate before implementation.

## Baseline And Recovery

For valid git projects:

- record branch and commit before takeover;
- inspect `git status --short` before generating child tasks;
- do not overwrite unrelated dirty changes;
- prefer worktrees for risky parallel implementation;
- create a recovery point before accepting a major stage.

For non-git projects:

- record that no merge/worktree safety is available;
- do not initialize git without asking the user;
- use explicit file manifests, ALLOWLIST checks, tests, and handoff review as the boundary gate.

## Product Manager Prompt Add-on

When taking over an existing project, include this in the product-manager prompt or first PROGRESS entry:

```text
这是已有开发中项目的二次开发接管，不是新项目从零启动。
先做 current-state audit，只读扫描项目结构、文档、git 状态、功能完成度、测试/启动命令和未完成项。
当前已有实现视为 baseline；不得直接重构、替换 UI、升级依赖、改 schema/API 或修改业务代码。
把后续优化、新需求、修复、UI 设计、测试补齐拆成子线程任务包，经 ALLOWLIST 和依赖评估后再派发。
```