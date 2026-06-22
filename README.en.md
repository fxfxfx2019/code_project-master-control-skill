# Codex Skills

This repository publishes reusable Codex skills.

This repository is for **Codex skill installation**. It is not a normal npm, Python, or application package.

## Included Skills

- `project-master-control`: product-manager-led multi-thread software project coordination.
- `gpt-chat`: ask a local GPT-CHAT / ChatGPT web-wrapper service for second-opinion analysis with normal ChatGPT context.
- `gpt-chat-temp`: ask the same GPT-CHAT service in temporary-chat mode for isolated analysis.

## project-master-control

`project-master-control` helps Codex run a bounded project workflow with:

- a Product Manager thread for requirements, planning, dispatch, review, and merge decisions;
- child Codex threads or worktrees for scoped implementation tasks;
- `.agents/**` control files for progress, thread state, decisions, and handoffs;
- per-thread `TASK.md`, `STATUS.md`, `ALLOWLIST.md`, and `HANDOFF.md`;
- UI/UX design gates for SaaS, CRM, dashboard, admin, and complex workflow projects;
- existing-project takeover mode for second development and optimization;
- validation, boundary checks, handoff review, product-manager loop scripts, and post-merge completion consolidation.

## Install

Ask Codex to install a skill from one of these repository paths:

```text
Install the Codex skill from:
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/project-master-control

Install the Codex skill from:
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/gpt-chat

Install the Codex skill from:
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/gpt-chat-temp
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

For the full workflow, command reference, and operating model, see [Detailed usage guide](docs/USAGE.en.md).
For GPT-CHAT setup and usage, see [GPT-CHAT guide](docs/GPT_CHAT.en.md).

After child work is accepted or merged, use:

```text
python scripts/pmc.py post-merge --project-root . --stage <stage> --write-report
```

This helps the Product Manager thread update completion records, decide whether durable conclusions should be merged into formal project docs, and decide whether accepted child windows can be archived.

## Repository Layout

```text
skills/
  project-master-control/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
  gpt-chat/
    SKILL.md
    agents/openai.yaml
    scripts/
  gpt-chat-temp/
    SKILL.md
    agents/openai.yaml
    scripts/
```

## Notes

- Child threads are scoped by task/function boundaries, not staffing roles.
- Visible child thread titles default to English, for example `Child - Frontend - ui-01-web-productization`.
- Product Manager threads should not directly edit production code unless explicitly authorized.
- High-impact changes such as schema/API, architecture, dependency, security, permission, payment, and major UI direction require user confirmation.
