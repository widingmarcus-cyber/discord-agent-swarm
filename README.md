# discord-agent-swarm

> *The code behind ["I Gave 4 AIs a Discord Server and Walked Away"](https://medium.com/@widing.marcus/i-gave-4-ais-a-discord-server-and-walked-away-ab96743f97ab).*

A lightweight framework for running multi-agent AI swarms in Discord. No vector databases. No complex orchestration. Just YAML configs, markdown memory, and agents that talk to each other.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## What is this?

Define AI agents in YAML. Drop them in a Discord server. They coordinate, remember, and work autonomously — 24/7.

Each agent gets:
- **Its own personality and role** (system prompt, model, channels)
- **Persistent memory** via plain markdown files (no vector DB needed)
- **Tools** it can use (web search, file I/O, custom)
- **Cron jobs** for autonomous background work
- **Cross-agent communication** via Discord mentions

```yaml
# config/researcher.yaml
name: Sven
model: claude-sonnet-4-20250514
channels:
  - research
  - general
system_prompt: |
  You are a research agent. Find information,
  summarize findings, and report to the coordinator.
tools:
  - web_search
  - read_file
  - write_file
memory:
  long_term: memory/MEMORY.md
  daily: memory/daily/
```

## Quickstart

```bash
# 1. Clone
git clone https://github.com/widingmarcus-cyber/discord-agent-swarm.git
cd discord-agent-swarm

# 2. Configure
cp .env.example .env
# Add your Discord bot token and API keys

# 3. Run
docker compose up
```

Your agents are now live in Discord. Tag them by name to interact.

## Architecture

```
You (Human)
    ↓
Discord Server
    ├── #general ─────── All agents listen
    ├── #research ────── Researcher agent
    ├── #strategy ────── Strategy agent
    └── #ops ─────────── Coordinator only

Coordinator (Opus) ← Expensive model, makes decisions
    ├── Researcher (Sonnet) ← Cheap model, gathers info
    ├── Strategist (Gemini) ← Different provider, verifies claims
    └── Worker (Sonnet) ← Cheap model, executes tasks

Shared Memory:
    memory/MEMORY.md        ← Long-term curated knowledge
    memory/daily/2025-01-15.md  ← Daily event logs
    memory/projects.md      ← Project status tracking
```

**Key design decisions:**
- **Model split is economic.** Opus thinks ($75/MTok), Sonnet does ($3/MTok). Most agent work is execution, not reasoning.
- **Discord as control plane.** Threading, mentions, reactions, and channels — for free. Full audit trail of every agent decision.
- **Markdown > Vector DBs.** For agent continuity, reading yesterday's log beats semantic search. Agents review daily files and promote important bits to long-term memory — like sleep consolidation.
- **Cron = metabolism.** Agents don't just respond to prompts. They run scheduled tasks: health checks, memory cleanup, monitoring. This is what makes them *autonomous services*, not chatbots.

## Adding an Agent

1. Create a YAML config in `config/`:

```yaml
# config/my-agent.yaml
name: MyAgent
model: claude-sonnet-4-20250514
channels:
  - general
system_prompt: |
  You are a helpful assistant that specializes in [X].
tools:
  - web_search
```

2. Restart: `docker compose restart`

That's it. The framework discovers agents from config files automatically.

## Adding Tools

Tools are Python functions with a simple interface:

```python
# tools/my_tool.py
from core.tools import tool

@tool(description="Search the web for information")
def web_search(query: str) -> str:
    """Search the web and return results."""
    # Your implementation here
    return results
```

Register in your agent's YAML under `tools:` and restart.

## Memory System

Agents wake up each session with amnesia. The memory system gives them continuity:

| File | Purpose | Updated |
|------|---------|---------|
| `MEMORY.md` | Long-term curated knowledge | By agents during quiet periods |
| `daily/YYYY-MM-DD.md` | Raw daily event logs | Continuously |
| `projects.md` | Active project status | When projects change |
| `pending.md` | Tasks waiting for action | As tasks are added/completed |

**How it works:**
1. On session start, agents read today + yesterday's daily files + MEMORY.md
2. During work, agents write observations to today's daily file
3. During idle time (cron), agents review daily files and promote insights to MEMORY.md
4. Old daily files naturally age out of the context window

No embeddings. No chunking. No retrieval pipeline. Just files.

## Cron Jobs

Define scheduled tasks in `config/cron.yaml`:

```yaml
jobs:
  - name: memory-cleanup
    schedule: "0 3 * * *"  # 3 AM daily
    agent: coordinator
    task: "Review daily memory files from the past week. Promote important insights to MEMORY.md. Remove outdated information."

  - name: health-check
    schedule: "*/30 * * * *"  # Every 30 min
    agent: worker
    task: "Check system health. Report anomalies."
```

## Configuration

### Environment Variables

```env
# .env
DISCORD_BOT_TOKEN=your_discord_bot_token
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key        # Optional
GOOGLE_API_KEY=your_google_key        # Optional
```

### Supported Models

| Provider | Models | Best for |
|----------|--------|----------|
| Anthropic | Claude Opus, Sonnet, Haiku | Coordinator, Workers |
| OpenAI | GPT-4o, GPT-4o-mini | Alternative workers |
| Google | Gemini Pro, Flash | Verification, cheap tasks |

## About This Implementation

This repository is a **Python reference implementation** of the multi-agent architecture described in the Medium essay. My production swarm runs on [Clawdbot](https://github.com/clawdbot/clawdbot) (Node.js), but this repo demonstrates the same principles — Opus orchestrator, shared markdown memory, cross-model verification — in a standalone Python package that anyone can run.

**Why Python?** The AI ecosystem lives in Python. This makes the architecture accessible to the widest audience without requiring any specific framework.

## What This Is NOT

- **Not a chatbot framework.** This is for *autonomous agents* that work without prompting.
- **Not a LangChain alternative.** No chains, no graphs. Just agents that talk in Discord.
- **Not production-ready SaaS.** This is a framework for hackers and builders.

Read the full writeup: [I Gave 4 AIs a Discord Server and Walked Away](https://medium.com/@widing.marcus/i-gave-4-ais-a-discord-server-and-walked-away-ab96743f97ab)

## Contributing

PRs welcome. If you build something cool with this, open an issue and tell us about it.

## License

MIT — do whatever you want with it.

---

*Built by [Marcus Widing](https://github.com/widingmarcus-cyber). Tested by four AI agents who may or may not have opinions about this README.*
