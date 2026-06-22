# GPT-CHAT Skills Guide

This guide covers two Codex skills:

- `gpt-chat`: ask the user's local GPT-CHAT service with normal ChatGPT context and memory.
- `gpt-chat-temp`: ask the same service in temporary-chat mode for isolated second-opinion analysis.

These skills are for Codex. They are not standalone ChatGPT clients.

## What They Do

The skills call a local GPT-CHAT wrapper service that drives the logged-in ChatGPT web UI through a small visible browser window.

Use them when Codex should ask GPT for a second opinion on:

- hard bugs;
- architecture choices;
- UI/UX critique;
- product decisions;
- debugging logs;
- alternative implementation plans.

Codex remains responsible for verification. GPT-CHAT output is advice, not ground truth.

## Install

Ask Codex to install one or both skills:

```text
Install the Codex skill from:
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/gpt-chat
```

```text
Install the Codex skill from:
https://github.com/fxfxfx2019/code_project-master-control-skill/tree/main/skills/gpt-chat-temp
```

Restart Codex after installation.

## Prerequisites

You need a local GPT-CHAT wrapper service project. The skill expects that service to expose:

- `package.json`
- `src/server.js`
- `scripts/start-chatgpt-browser.ps1`
- `.runtime/<instance>-service.json` after the service starts

Configure the service location:

```powershell
Set-Item Env:GPT_CHAT_HOME "C:\path\to\gpt-chat-service"
```

For persistent Windows configuration, set a user environment variable named `GPT_CHAT_HOME`.

Optional environment variables:

```text
GPT_CHAT_HOME
GPT_CHAT_SERVICE_ROOT
GPT_CHAT_API_TOKEN
GPT_CHAT_API_URL
GPT_CHAT_BROWSER_PORT
GPT_CHAT_BROWSER_PROFILE_DIR
GPT_CHAT_SESSION
```

## Normal Mode

Use `gpt-chat` when preserving ChatGPT context or memory is helpful.

Trigger examples:

```text
@gpt analyze this bug
让 GPT-chat 回答一下
Use gpt-chat for a second opinion on this design
```

Manual command:

```powershell
node "$env:USERPROFILE\.codex\skills\gpt-chat\scripts\ask-gpt-chat.mjs" `
  --session codex-second-opinion `
  --question "Analyze this issue and suggest a practical fix."
```

## Temporary Mode

Use `gpt-chat-temp` when prior ChatGPT context should not affect the answer.

Trigger examples:

```text
@gpt-temp analyze this in isolation
Use GPT temporary mode for this question
```

Manual command:

```powershell
node "$env:USERPROFILE\.codex\skills\gpt-chat-temp\scripts\ask-gpt-chat-temp.mjs" `
  --session codex-temp-opinion `
  --question "Analyze this issue briefly."
```

`gpt-chat-temp` uses:

- instance: `gpt-chat-temp`
- browser port: `9224`
- browser profile: `.chatgpt-browser-profile-temp`
- temporary chat: enabled
- fresh conversation: enabled

It can run alongside normal `gpt-chat`, which defaults to port `9223`.

## Safety

Do not send:

- secrets;
- passwords;
- cookies;
- tokens;
- private keys;
- unrelated personal data.

Do not bypass CAPTCHA, Turnstile, Cloudflare, or login verification. If the browser profile needs login, the user must complete it manually in the visible browser window.

## Expected Codex Behavior

Codex should relay GPT output compactly:

```text
gpt回复：“...”
```

Then Codex should independently inspect the codebase, verify GPT claims, and only execute justified changes.

## Troubleshooting

If the service root is missing:

```text
Set GPT_CHAT_HOME or pass --home <service-project-directory>.
```

If the browser profile is locked or not logged in, unlock/login in the visible ChatGPT helper window.

If the service is already running, the scripts reuse it through `.runtime/<instance>-service.json`.
