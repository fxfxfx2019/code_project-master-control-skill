# project-master-control 使用手册

这个仓库包含一个 Codex skill。它面向支持 skills、本地文件访问、shell 命令，以及可选 Codex 线程工具的 Codex Desktop / Codex 环境。

## 安装

让 Codex 从下面路径安装 skill：

```text
从下面路径安装 Codex skill：
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/project-master-control
```

安装后重启 Codex，让新的 skill 被发现。

## 核心思想

`project-master-control` 会把一个 Codex 会话变成 Product Manager 控制线程。

Product Manager 线程负责：

- 需求和验收标准；
- 任务拆解；
- 子线程 / worktree 派发；
- 通过 `ALLOWLIST.md` 控制文件边界；
- 通过 `.agents/**` 跟踪进度；
- review、返工、合并和阶段验收判断。

子线程只负责自己的任务包：

- `.agents/threads/<thread>/AGENTS.md`
- `.agents/threads/<thread>/TASK.md`
- `.agents/threads/<thread>/STATUS.md`
- `.agents/threads/<thread>/ALLOWLIST.md`
- `.agents/threads/<thread>/HANDOFF.md`

子线程不能自行扩大范围，不能写 ALLOWLIST 之外的文件，不能直接合并主干。

当子线程完成、阻塞或需要 Product Manager 决策时，必须准备一条 `PM_FEEDBACK` 消息回馈给 Product Manager 线程：

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

如果子线程可用 `send_message_to_thread`，并且知道 Product Manager 线程 id，就应该直接把这条消息发回主线程。否则必须把这条消息写入 `HANDOFF.md`，并放在最终回复里。

## 适合什么时候用

适合：

- 新软件项目；
- 大阶段开发；
- 多模块实现；
- 多子线程并行开发；
- 已有项目接管、二次开发和优化；
- SaaS、CRM、dashboard、后台管理、桌面端、运营工作台等 UI 较重项目；
- 需要文件锁、合并门禁、断点续传和审计记录的工作。

不适合：很小的单文件修改。那种情况直接让 Codex 执行通常更快。

## 启动新项目或新阶段

在 Product Manager 会话中发送：

```text
启用 project-master-control
```

Product Manager 线程应该继续完成：

1. 确认项目目标、边界、优先级和验收标准；
2. 创建或更新根目录 `AGENTS.md`；
3. 创建 `.agents/**`；
4. 拆分有边界的子线程任务包；
5. 校验任务包；
6. 生成子线程启动 prompt；
7. 在线程工具可用时创建真实 Codex 子线程或 worktree；
8. 记录返回的 `threadId` 或 `pendingWorktreeId`；
9. 进入 Product Manager loop，直到 accepted、blocked 或 waiting_for_child_feedback。

## 接管已有项目

已有项目可以发送：

```text
启用 project-master-control，接管当前已有项目做二次开发
```

Product Manager 必须把当前实现视为 baseline。启用规范不等于自动重构、改版、升级依赖或重写业务行为。

第一步通常应该是 `phase-00-current-state-audit`，用于记录：

- 项目结构；
- git / 非 git 状态；
- dirty files；
- 现有启动、构建、测试命令；
- 已完成、部分完成和缺失功能；
- 已知失败和风险文件；
- 推荐的下一批子线程任务。

## UI/UX 设计门禁

对 CRM、SaaS、dashboard、后台管理、桌面端或复杂业务流 UI，Product Manager 通常应该先创建 UI/UX 设计子线程，再放行前端实现。

设计 handoff 应覆盖：

- 用户和核心流程；
- 页面清单和信息架构；
- 布局、导航、表格、筛选器、表单、抽屉、弹窗、图表；
- Design Tokens 和技术栈约束；
- Skeleton 骨架屏；
- 极端文本溢出策略；
- 带行动按钮的空状态；
- Disabled、Error、Permission、Loading、Success、Hover、Focus 等状态；
- 前端实现验收标准。

大型 UI 方向未确认前，前端实现线程应保持 `waiting_for_design_confirmation`。

## Product Manager 循环

Product Manager loop 会读取子线程状态、review handoff，并决定下一步：

```text
python scripts/pmc.py status --project-root .
python scripts/pmc.py resume --project-root . --stage <stage>
python scripts/pmc.py loop --project-root . --stage <stage>
```

可能结果：

- 等待子线程反馈；
- 接收 handoff；
- 发送返工 prompt；
- 向用户请求高影响决策；
- 解锁下一阶段；
- 创建更多子线程；
- 进行阶段验收。

`waiting_for_child_feedback` 是有效暂停状态。它表示子线程仍在执行，当前没有可 review 的 handoff。

收到 `PM_FEEDBACK` 消息后，Product Manager 应把它视为唤醒信号：运行 loop，review 对应的 `HANDOFF.md`，然后判断 accept、rework、ask-user、unblock-next-phase、create-more-threads 或 stage-acceptance。

## Review 与合并

子线程 handoff 通过，不等于无条件合并。

Product Manager 必须检查：

- ALLOWLIST 边界；
- 修改文件；
- 指定验证；
- 清理结果；
- 冲突；
- 文档；
- 高影响风险。

local 同目录子线程没有真正 git merge，因为改动已经在共享工作区中，只能通过 PM review 接收或返工。

worktree 子线程需要合并门禁。高影响变更必须先让用户确认。

## 汇聚后的完成记录

子线程工作被接收或合并后，运行：

```text
python scripts/pmc.py post-merge --project-root . --stage <stage> --write-report
```

这会生成 `.agents/POST_MERGE_CLEANUP.md`。

报告会帮助 Product Manager 判断：

- 完成记录是否已更新；
- 长期有效结论是否应该合并到正式项目文档；
- `.agents/**` 审计记录应该保留、归档还是裁剪；
- 已接收的子线程窗口是否可以归档关闭。

只有在无 blocker、无返工、无待确认、无未完成验证、无后续任务时，才应关闭已接收子线程窗口。

## 常用命令

这些命令在 skill 把脚本生成或复制到项目后，从项目根目录执行：

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

Windows PowerShell 下，Node 命令优先使用 `npm.cmd` 和 `npx.cmd`。

## 项目中会生成哪些文件

典型结构：

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

这些文件是协作和审计记录。默认保留，除非 Product Manager 判断不再需要，并且用户同意裁剪。

## 重要限制

- 这个 skill 协调 Codex 行为，不是包管理器或 CI 工具。
- 能否自动创建真实子线程取决于当前 Codex 是否暴露线程工具。
- 如果线程工具不可用，Product Manager 应生成 `.agents/thread-prompts/*.txt` 供手动启动。
- Product Manager 默认不写业务代码，除非用户明确授权。
- 高影响变更必须请求用户确认。
