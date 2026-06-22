# GPT-CHAT Skills 使用说明

这里说明两个 Codex skills：

- `gpt-chat`：通过本地 GPT-CHAT 服务咨询保留上下文和记忆的 ChatGPT。
- `gpt-chat-temp`：通过 temporary-chat 模式咨询隔离上下文的 ChatGPT。

这两个 skill 是给 Codex 用的，不是独立 ChatGPT 客户端。

## 它们做什么

这两个 skill 会调用本地 GPT-CHAT wrapper 服务。该服务通过一个小的可见浏览器窗口驱动已登录的 ChatGPT 网页。

适合让 Codex 向 GPT 询问第二意见：

- 复杂 bug；
- 架构选择；
- UI/UX 评价；
- 产品决策；
- 调试日志；
- 替代实现方案。

Codex 仍然负责最终验证和执行。GPT-CHAT 输出只能作为建议，不能当作事实。

## 安装

让 Codex 安装一个或两个 skill：

```text
从下面路径安装 Codex skill：
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/gpt-chat
```

```text
从下面路径安装 Codex skill：
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/gpt-chat-temp
```

安装后重启 Codex。

## 前置条件

你需要有一个本地 GPT-CHAT wrapper 服务项目。skill 默认期望该服务包含：

- `package.json`
- `src/server.js`
- `scripts/start-chatgpt-browser.ps1`
- 服务启动后生成的 `.runtime/<instance>-service.json`

配置服务目录：

```powershell
Set-Item Env:GPT_CHAT_HOME "C:\path\to\gpt-chat-service"
```

如果要长期生效，可以在 Windows 用户环境变量中设置 `GPT_CHAT_HOME`。

可选环境变量：

```text
GPT_CHAT_HOME
GPT_CHAT_SERVICE_ROOT
GPT_CHAT_API_TOKEN
GPT_CHAT_API_URL
GPT_CHAT_BROWSER_PORT
GPT_CHAT_BROWSER_PROFILE_DIR
GPT_CHAT_SESSION
```

## 普通模式

当你希望保留 ChatGPT 上下文或记忆时，使用 `gpt-chat`。

触发示例：

```text
@gpt analyze this bug
让 GPT-chat 回答一下
Use gpt-chat for a second opinion on this design
```

手动命令：

```powershell
node "$env:USERPROFILE\.codex\skills\gpt-chat\scripts\ask-gpt-chat.mjs" `
  --session codex-second-opinion `
  --question "Analyze this issue and suggest a practical fix."
```

## 临时模式

当你不希望历史 ChatGPT 上下文影响回答时，使用 `gpt-chat-temp`。

触发示例：

```text
@gpt-temp analyze this in isolation
Use GPT temporary mode for this question
```

手动命令：

```powershell
node "$env:USERPROFILE\.codex\skills\gpt-chat-temp\scripts\ask-gpt-chat-temp.mjs" `
  --session codex-temp-opinion `
  --question "Analyze this issue briefly."
```

`gpt-chat-temp` 使用：

- instance：`gpt-chat-temp`
- 浏览器端口：`9224`
- 浏览器 profile：`.chatgpt-browser-profile-temp`
- temporary chat：开启
- fresh conversation：开启

它可以和普通 `gpt-chat` 并行运行。普通模式默认使用端口 `9223`。

## 安全规则

不要发送：

- secrets；
- passwords；
- cookies；
- tokens；
- private keys；
- 无关个人数据。

不要绕过 CAPTCHA、Turnstile、Cloudflare 或登录验证。如果浏览器 profile 需要登录，用户必须在可见浏览器窗口里手动完成。

## Codex 应如何处理 GPT 输出

Codex 应简短转述 GPT 输出：

```text
gpt回复：“...”
```

随后 Codex 必须自己检查代码、验证 GPT 判断，只执行有依据的修改。

## 排错

如果服务目录缺失：

```text
Set GPT_CHAT_HOME or pass --home <service-project-directory>.
```

如果浏览器 profile 被锁或未登录，需要在可见 ChatGPT helper 窗口里解锁或登录。

如果服务已经运行，脚本会通过 `.runtime/<instance>-service.json` 复用它。
