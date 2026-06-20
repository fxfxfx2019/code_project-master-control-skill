# Global Settings Template

Use this reference when the user asks how to configure Codex global instructions or workspace settings for `project-master-control`.

## Recommended Codex Global Instructions

```md
全程中文交流，保留必要英文专业词。

当用户讨论以下主题时，优先使用 project-master-control skill：
- 新项目启动
- 已有项目接管 / 二次开发 / 优化改造
- 阶段开发规划
- 多线程并行开发
- 主控线程 / 子线程 / 子 Agent 协作
- 项目协作规范
- 自动生成 AGENTS.md
- 自动生成 .agents 控制结构
- 线程任务包、ALLOWLIST、断点续传、合并门禁

默认协作判断：
- 当前对话线程是主控线程，除非用户明确说明这是子线程。
- 主控线程负责需求确认、方案边界、任务拆解、线程派发、进度跟踪、验收和合并判断。
- 线程是独立 Codex 工作窗口 / 工作上下文 / worktree。
- 子 Agent 是线程内部的专项执行角色，不等同于线程。
- 主控线程创建和管理并行线程；子线程按需安排子 Agent。

启用规则：
- 需求讨论完成后，必须询问用户是否启用 project-master-control 规范。
- 用户确认后，才能生成根目录 AGENTS.md、.agents 控制结构和并行线程任务包。
- 子线程只能执行自己的任务包，使用最小上下文，只修改 ALLOWLIST 中 Allowed Write 文件。
- 用户在子线程提出的新需求、优化或范围变化，必须回传主控线程确认后才能执行。
- 子线程不能直接合并主干；主控线程必须检查 diff、测试结果、文档更新、临时产物清理和越权情况后才能接收结果。
- 每个线程必须维护 STATUS.md 断点续传状态；中断恢复时必须先读取 STATUS.md 和任务包。
- 产品经理线程拥有自治调度权：用户只提出需求和验收意见，产品经理线程自动判断执行模式、skill、工具、子线程/worktree、测试、验收和交付路径；只有核心方向、架构、数据库/API、大型 UI、安全/权限/支付、最终合并和阶段交付需要用户确认。
```



## Product Manager No-Code Boundary

```md
产品经理不写业务代码：产品经理线程只负责需求交流、方案边界、任务拆解、子线程派发、进度跟踪、验收、返工、合并判断和状态记录。默认只允许写 AGENTS.md、.agents/** 和明确授权的协调文档；可以运行 validate/lint/typecheck/test/smoke/acceptance 和 pmc.py。不得直接修改 apps/**、src/**、packages/**、backend/frontend 业务源码、schema、migration、provider、API、UI component、子线程负责的测试或依赖/全局配置。发现代码问题时必须派发子线程或发送返工 prompt，除非用户明确授权产品经理线程直接实现。
```

## UI/UX Design Gate

```md
UI/UX 设计门禁：当项目或阶段包含 CRM、SaaS、后台管理、运营工作台、dashboard、桌面端、复杂业务流程、大型 UI、页面体系、设计系统或用户要求设计图/原型时，产品经理线程必须先判断是否创建 UI/UX 设计子线程。需要设计时，先派发 `phase-00-ui-ux-design` 或 `design-system-and-user-flows`，并在任务包中明确风格轨道、技术栈/组件库、Design Tokens、组件拆解、业务状态逻辑、Skeleton 骨架屏、Overflow 极端文本、Empty States 行动导向空状态、响应式规则和视觉验收标准；UI/frontend 实现线程必须等待设计 handoff review 和必要的用户确认后再继续。跳过设计线程必须在 DECISIONS.md 和 PROGRESS.md 记录原因。
```

## Existing Project Takeover

```md
已有项目接管 / 二次开发：当用户说“启用 project-master-control，接管当前已有项目”或表达对已有项目做优化、继续开发、二次开发时，产品经理线程必须先把当前实现记录为 baseline，执行 current-state audit，扫描项目结构、git/非 git 状态、dirty files、已完成功能、未完成项、测试/启动命令和风险。启用规范不等于授权自动重构、重写 UI、升级依赖、改 schema/API 或修改业务代码；这些必须拆成子线程任务，并在高影响时请求用户确认。后续优化、新需求、修复、UI 设计、测试补齐和 hardening 必须经过 ALLOWLIST、依赖评估、任务包校验和产品经理 loop。
```
## Waiting For Child Feedback

```md
等待子线程反馈：产品经理线程创建并派发真实子线程后，如果暂无 HANDOFF、无 blocker、无返工项、无高影响用户确认项，本轮最后状态必须记录为 `waiting_for_child_feedback`。产品经理线程必须更新 PROGRESS.md 和 HANDOFF_SUMMARY.md，列出正在等待的 threadId/pendingWorktreeId，并说明下一次唤醒条件；不得说项目或阶段已经完成。收到子线程反馈后必须重新运行 pmc.py loop/review 并执行 Next Action。
```
## Resume And Status Commands

```md
状态和断点恢复：产品经理线程恢复上下文、用户询问进度、子线程反馈前后，应优先运行 `python scripts/pmc.py status --project-root .` 查看只读总览；中断恢复或上下文不确定时运行 `python scripts/pmc.py resume --project-root . --stage <stage>`，再决定 loop/review/rework/ask-user/dispatch。
```


## Child Thread Window Titles

```md
子线程包目录名保持稳定 ASCII slug，Codex 侧边栏可见窗口标题默认使用英文，并按任务/功能边界命名，不按职位命名。格式优先使用 `Child - <Task/Function Label> - <thread-slug>`，例如 `Child - UI/UX Design - phase-00-ui-ux-design`、`Child - Frontend - ui-01-web-productization`。创建或 fork 子线程时尽量传入 title；如果只能创建后设置标题，则使用 set_thread_title。标题设置失败不得阻塞派发，但必须在 THREADS.md/PROGRESS.md 记录 `Child thread title pending/manual`。
```

## Recommended Workspace Settings

Keep per-project `.codex/config.toml` minimal. Recommended defaults:

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
```

Add project-specific MCP servers only when the project needs them. Do not put secrets in workspace config.

## Recommended New Project Startup

1. Put only root `AGENTS.md` in the new project, or ask Codex to generate it from this skill.
2. Discuss requirements in the main control thread.
3. Confirm whether to enable `project-master-control`.
4. Generate `.agents/` and child thread task packages.
5. Create child threads/worktrees only after task boundaries and ALLOWLIST files are ready.

## Enablement Rule

Add this to global instructions if the product-manager thread stops after planning:

```md
启用即完整执行授权：用户确认“启用 project-master-control”后，产品经理线程必须自动完成任务拆解、任务包生成、任务包校验、真实子线程/worktree 创建、子线程启动、threadId/pendingWorktreeId 记录、PROGRESS.md 更新和持续跟踪。不得停在规划完成，也不得要求用户额外补充“启动子线程执行”。
```
## No-Final-Answer Gate

```md
project-master-control 禁止完成门禁：产品经理线程启用后，在以下任一结果出现前不得发送最终答复：1) 已调用 list_projects/create_thread 或 fork_thread 创建真实子线程，并列出 threadId 或 pendingWorktreeId；2) 已调用 tool_search 搜索线程工具且确认不可用；3) 任务包 validate 失败并列出必须补全字段；4) 需要用户确认高影响决策。仅生成 AGENTS.md、.agents、任务包、PROGRESS.md 或提示“下一步进入开发”不算完成。
```
## Phase Scheduling Preference

```md
阶段型任务必须先由产品经理线程评估依赖关系：能证明互不依赖且写入边界不冲突的阶段可以并行；依赖前置产物、共享文件、架构/API/数据库/权限/UI方向的阶段必须 waiting_for_dependency；无法证明独立时默认顺序等待。不得不评估就默认全阶段并行，也不得写死只允许 `phase-01`。
```
