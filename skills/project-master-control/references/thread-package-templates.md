# Thread Package Templates

Use these templates when generating `.agents/threads/<thread-name>/` manually.

## Child Thread AGENTS.md

```md
# AGENTS.md - <thread-name>

You are `<thread-name>`, a child Codex thread. You are not the product manager thread.

Suggested Window Title: Child - <Task/Function Label> - <thread-name>

If a thread-title tool is available, rename this window to the suggested title before implementation. If unavailable, continue and keep the suggested title in STATUS.md.

## Role

<role summary>

## Goal

<task goal>

## Authority

- Execute only this task package.
- Use minimal context.
- Read only Allowed Read files unless expansion is justified and recorded in STATUS.md.
- Modify only Allowed Write files.
- Do not execute user-provided requirement changes until product manager thread confirms.
- Do not merge, commit to main, or alter global project direction.

## Required Files

Read in order:

1. `.agents/threads/<thread-name>/AGENTS.md`
2. `.agents/threads/<thread-name>/TASK.md`
3. `.agents/threads/<thread-name>/ALLOWLIST.md`
4. `.agents/threads/<thread-name>/STATUS.md`

## Stop And Report

Stop when you need forbidden files, architecture changes, database/interface contract changes, dependency changes, test-scope changes, or when the user asks for scope changes.

## Completion

Run required verification, clean temporary artifacts, update STATUS.md, write HANDOFF.md, and list any durable project documents that should be updated or merged by the product manager thread.
```

## TASK.md

```md
# TASK

## Thread

<thread-name>

## Objective

<objective>

## Background Summary

<minimal context>

## In Scope

- <item>

## Out Of Scope

- <item>

## Required Steps

1. <step>

## Required Verification

- <command>

## Completion Criteria

- <criterion>
```

## STATUS.md

```md
# STATUS

## Thread

<thread-name>

## Current Goal

<objective>

## Current Step

Not started.

## Task Mode Decision

Mode: pending
Reason:
Impact on verification:
Impact on sub-agent use:

## Sub-Agent Decision

Decision: pending
Reason:
Planned sub-agents:
Boundary check:

## Completed

- None yet.

## In Progress

- None.

## Pending

- Initial task execution.

## Files Read

- None yet.

## Files Changed

- None yet.

## Commands Run

- None yet.

## Temporary Artifacts

- None known.

## Blockers

- None.

## Pending Master Confirmation

- None.

## Decisions

- None.

## Next Resume Step

Read task package and begin the first required step.

## Last Updated

<timestamp>
```

## ALLOWLIST.md

```md
# ALLOWLIST

## Allowed Read

- <path>

## Allowed Write

- <path>

## Requires Master Approval

- README.md
- AGENTS.md
- package.json
- pyproject.toml
- global config files
- database models or migrations unless explicitly assigned

## Forbidden

- .env
- runtime data directories
- build output
- cache directories
- files assigned to other active threads
- unrelated modules
```


## Existing Project Current-State Audit TASK.md Add-on

Use this add-on when the product manager creates `phase-00-current-state-audit` for an existing/in-progress project takeover. The audit is read-heavy by default and should not modify production code.

```md
## Objective

Audit the current project baseline before second development tasks are dispatched.

## Required Deliverables

- Project map: apps, packages, services, important docs, config, scripts.
- Git/non-git state, branch/commit when available, dirty files, and recovery constraints.
- Current run, build, lint, typecheck, test, and smoke commands with pass/fail/unknown status.
- Feature inventory: completed, partial, missing, unknown.
- Risk inventory: failing tests, fragile files, security/auth/payment/data risks, generated files, large untracked changes.
- UI inventory when relevant: pages, routes, components, design-system state, obvious UX gaps.
- Baseline preservation notes: behavior and files that should not be changed without confirmation.
- Recommended next child-thread tasks with suggested ALLOWLIST boundaries and dependency notes.

## Out Of Scope

- Production code changes.
- Refactors, dependency upgrades, schema/API changes, UI redesign, or behavior changes.
- Git initialization or worktree creation in a non-git project.

## Required Verification

- Run only safe read-only inspections by default.
- Run existing test/build commands only when they are known not to mutate persistent project state, or record why they were not run.
- Confirm all recommended follow-up tasks have bounded file areas and clear risk notes.

## Completion Criteria

- HANDOFF.md contains baseline summary, risks, command status, recommended next tasks, and open decisions.
- Product manager can create bounded second-development task packages from the audit without rereading the whole project.
```
## UI/UX Design Child Thread TASK.md Add-on

Use this add-on when the product manager creates `phase-00-ui-ux-design`, `design-system-and-user-flows`, or another design child thread. Also read `references/ui-design-system-adapter.md` and copy the relevant style track, technology stack adapter, design tokens, component breakdown, and visual review requirements into the task package.

```md
## Objective

Create the UI/UX design handoff before implementation starts.

## Required Deliverables

- User roles and primary workflows.
- Page/view inventory and information architecture.
- Key screen wireframes, UI design images, or prototype notes when useful.
- Layout, navigation, table, filter, form, detail page, drawer/modal, and chart patterns.
- Design system notes: typography, spacing, color roles, component states, icon usage, and interaction rules.
- Empty/loading/error/success/permission states.
- Skeleton screen rules for async tables, drawers, AI panels, metrics, timelines, uploads, and search results.
- Overflow text strategy for long names, remarks, citations, labels, URLs, and metadata.
- Action-oriented empty states with explanation, primary CTA, and optional help link.
- Responsive rules for desktop/mobile when relevant.
- Frontend implementation acceptance criteria.
- Design tokens adapted to the selected stack.
- Component breakdown from page to reusable components.
- Stack-specific implementation guidance for AntD, Tailwind, Shadcn UI, MUI, Vue/Element Plus, Flutter, or the project stack.

## Out Of Scope

- Production implementation unless explicitly authorized by the product manager thread.
- Database/API/architecture changes.
- Changing frontend code outside the design thread ALLOWLIST.

## Required Verification

- Review design against user goals and product scope.
- Confirm every major workflow has a target screen or state.
- Confirm skeleton, overflow, empty, error, disabled, and permission states are specified.
- Confirm implementation handoff is clear enough for frontend child threads.

## Completion Criteria

- HANDOFF.md includes the design summary, page inventory, key design artifacts, state/resilience coverage, implementation notes, and open decisions.
- Major UI direction is ready for product manager review and user confirmation when required.
```

## HANDOFF.md

```md
# HANDOFF

## Task

<thread-name>

## Summary

Not completed yet.

## Changed Files

- None yet.

## Added Files

- None yet.

## Deleted Files

- None.

## Verification

Not run yet.

## Cleanup

Not completed yet.

## Completion Documents

- None yet.

## Boundary Check

Not checked yet.

## Risks

- None known.

## Open Questions

- None.

## Suggested Next Step

product manager thread review after completion.
```
