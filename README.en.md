# project-master-control

`project-master-control` is a Codex skill for product-manager-led multi-thread software project coordination.

This repository is for **Codex skill installation**. It is not a normal npm, Python, or application package.

## What It Does

This skill helps Codex run a bounded project workflow with:

- a Product Manager thread for requirements, planning, dispatch, review, and merge decisions;
- child Codex threads or worktrees for scoped implementation tasks;
- `.agents/**` control files for progress, thread state, decisions, and handoffs;
- per-thread `TASK.md`, `STATUS.md`, `ALLOWLIST.md`, and `HANDOFF.md`;
- UI/UX design gates for SaaS, CRM, dashboard, admin, and complex workflow projects;
- existing-project takeover mode for second development and optimization;
- validation, boundary checks, handoff review, and product-manager loop scripts.

## Install

Ask Codex to install the skill from this repository path:

```text
Install the Codex skill from:
https://github.com/<owner>/<repo>/tree/main/skills/project-master-control
```

After installation, restart Codex so the skill can be discovered.

## Usage

For a new project or major stage:

```text
Enable project-master-control
```

For an existing in-progress project:

```text
Enable project-master-control and take over the current existing project for second development
```

The Product Manager thread should then create or update `AGENTS.md`, generate `.agents/**`, validate task packages, create real child threads or worktrees when thread tools are available, and continue the manager loop until the stage is accepted, blocked, or waiting for child feedback.

## Repository Layout

```text
skills/
  project-master-control/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
```

## Notes

- Child threads are scoped by task/function boundaries, not staffing roles.
- Visible child thread titles default to English, for example `Child - Frontend - ui-01-web-productization`.
- Product Manager threads should not directly edit production code unless explicitly authorized.
- High-impact changes such as schema/API, architecture, dependency, security, permission, payment, and major UI direction require user confirmation.

