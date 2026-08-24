# Project instructions for Codex

Before changing this project, read `CODEX_HANDOFF.md` and `MIGRATION_TO_NEW_PC.md`.

- This is a Python Telegram bot using aiogram and direct Mistral API calls.
- The current provider is Mistral only. Do not reintroduce OpenRouter, Qwen, Tavily, or n8n unless the user explicitly asks.
- Never request or print API keys, tokens, passwords, or `.env` contents. `.env` is local-only and must not be committed.
- Preserve the persistent Docker volume `bot-memory`; never use `docker compose down -v` unless the user explicitly asks to erase all bot memory.
- The user prefers concrete actions, simple Russian explanations, and as little manual work as possible.
- Verify code with local tests appropriate to the change. Docker is deployed on the VPS; it may not be installed on the development PC.
