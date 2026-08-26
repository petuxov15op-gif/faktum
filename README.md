# Faktum: Personal Telegram AI Assistant

Faktum is a Python Telegram bot built with aiogram. It can chat, search for up-to-date information with sources, process voice messages, images, and documents, and help with everyday planning.

## Features

- Context-aware AI chat
- Web search for news, weather, prices, events, and other current information
- Source links in search-based answers
- Voice transcription for messages up to three minutes
- Image, PDF, DOCX, and text-file analysis
- Persistent user facts and conversation history
- Tasks, recurring reminders, and expense tracking
- Personal morning and evening digests
- English level assessment and personalized lessons
- Per-user rate limits to control API usage

## Interface

`/start` and `/menu` open a compact inline menu without replacing the phone keyboard.

The menu includes chat, planning, finance, learning, memory, and settings. Full deletion of user data requires a separate confirmation.

## Commands

| Command | Purpose |
| --- | --- |
| `/start` | Start the bot and open the main menu |
| `/menu` | Open the menu |
| `/help` | Show available features |
| `/search query` | Force a web search |
| `/new` | Clear the current chat history |
| `/memory` | Show saved facts |
| `/remember text` | Save a fact |
| `/task text` | Add a task |
| `/tasks` | Show open tasks |
| `/done number` | Complete a task |
| `/remind time text` | Create a reminder |
| `/reminders` | Show reminders |
| `/expense amount category note` | Record an expense |
| `/expenses` | Show expenses for the last 30 days |
| `/buy query` | Find and compare products |
| `/digest` | Create a personal digest |
| `/english` | Start the English-level test |
| `/lesson` | Start the next English lesson |
| `/progress` | Show learning progress |
| `/settings` | Open assistant settings |
| `/forget` | Delete user data after confirmation |

## Technology

- Python 3.12
- aiogram 3 with Telegram long polling
- Mistral and OpenRouter
- Tavily for web search
- SQLite with WAL for persistent storage
- faster-whisper for voice transcription
- Docker Compose for deployment

## Setup

1. Copy `env.example` to `.env`.
2. Add your own credentials to `.env`.
3. Never share or commit `.env`.

```env
TELEGRAM_BOT_TOKEN=
AI_PROVIDER=openrouter
MISTRAL_API_KEY=
MISTRAL_MODEL=mistral-small-latest
TAVILY_API_KEY=
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-oss-20b:free
MEMORY_DB_PATH=data/bot_memory.sqlite3
REQUESTS_PER_MINUTE=6
REQUESTS_PER_DAY=100
WEB_SEARCHES_PER_DAY=25
STRICT_FACT_MODE=true
LOG_LEVEL=INFO
```

## Local run

Use Python 3.12 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

## Docker

```sh
docker compose up -d --build
docker compose logs --tail=50
```

User data is stored in the named Docker volume `bot-memory`. Do not run `docker compose down -v` unless you explicitly want to erase that data.

## GitHub sync

After completing a change, run:

```sh
bash sync_github.sh "Brief description of the change"
```

The script stages non-ignored files, creates a commit, rebases on the remote branch, and pushes the result to GitHub. It does not publish `.env`, the VPN configuration, the local database, or logs. Configure GitHub authentication in your terminal before the first run.

## Privacy

User messages and saved facts are stored in SQLite and may be sent to the configured AI provider to generate replies. Reflect this in your privacy policy before distributing the bot.
