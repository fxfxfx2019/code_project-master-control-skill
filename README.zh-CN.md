# project-master-control

`project-master-control` 是一个给 Codex 使用的 skill，用于“产品经理线程 + 子线程/worktree”的多线程项目协作。

这个仓库用于 **Codex skill 安装**。它不是普通的 npm 包、Python 包或应用项目。

## 它解决什么问题

这个 skill 帮助 Codex 按受控方式推进项目：

- 由 Product Manager 线程负责需求、规划、派发、验收、返工和合并判断；
- 由子 Codex 线程或 worktree 执行有边界的模块任务；
- 使用 `.agents/**` 记录进度、线程状态、决策和交付；
- 每个子线程都有 `TASK.md`、`STATUS.md`、`ALLOWLIST.md` 和 `HANDOFF.md`；
- 对 SaaS、CRM、dashboard、后台管理、复杂业务流项目增加 UI/UX 设计门禁；
- 支持已有项目接管、二次开发和优化；
- 提供任务包校验、边界检查、handoff review、产品经理循环脚本和汇聚后的完成记录处理。

## 安装

让 Codex 从这个 GitHub 路径安装 skill：

```text
从下面路径安装 Codex skill：
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/project-master-control
```

安装后需要重启 Codex，新的 skill 才会被发现。

## 使用方式

新项目或大型阶段开发：

```text
启用 project-master-control
```

已有项目接管、二次开发或优化：

```text
启用 project-master-control，接管当前已有项目做二次开发
```

启用后，Product Manager 线程应该创建或更新 `AGENTS.md`，生成 `.agents/**`，校验任务包，在线程工具可用时创建真实子线程或 worktree，并持续执行产品经理 loop，直到阶段验收、阻塞或进入等待子线程反馈状态。

完整流程、命令参考和运行原理见：[详细使用手册](docs/USAGE.zh-CN.md)。

子线程结果被接收或合并后，可以运行：

```text
python scripts/pmc.py post-merge --project-root . --stage <stage> --write-report
```

它会帮助 Product Manager 线程更新完成记录，判断是否把长期有效结论合并到正式项目文档，并判断已接收的子线程窗口是否可以归档关闭。

## 仓库结构

```text
skills/
  project-master-control/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
```

## 说明

- 子线程按任务/功能边界拆分，不按岗位拆分。
- 子线程窗口标题默认英文，例如 `Child - Frontend - ui-01-web-productization`。
- Product Manager 线程默认不直接写业务代码，除非用户明确授权。
- schema/API、架构、依赖、安全、权限、支付、大型 UI 方向等高影响变更，需要用户确认。
