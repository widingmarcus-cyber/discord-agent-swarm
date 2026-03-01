# Discord Agent Swarm 🤖🤖🤖🤖

> *The code behind ["I Gave 4 AIs a Discord Server and Walked Away"](https://medium.com/@widing.marcus/i-gave-4-ais-a-discord-server-and-walked-away-ab96743f97ab).*

A lightweight framework for running multi-agent AI swarms in Discord. No vector databases. No complex orchestration. Just YAML configs, markdown memory, and agents that talk to each other.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> **Built on [OpenClaw](https://github.com/openclaw/openclaw)** (216k ⭐). The author is an [experienced contributor](https://github.com/openclaw/openclaw/issues?q=label%3Atrusted-contributor) to OpenClaw with 10+ merged PRs, focused on cron reliability, announce delivery, and gateway stability.

---

## What is this?

Four autonomous AI agents running 24/7 in a Discord server. They coordinate, remember, and work — without human prompting.

| Agent | Model | Role | Mode |
|-------|-------|------|------|
| **Sture** 🦌 | Claude Opus | Coordinator — decisions, QA, delegation | Text |
| **Sven** 🔧 | Claude Sonnet | Researcher — on-demand only | Inactive |
| **Loyd** 🧐 | Gemini Pro | Strategist — cross-model verification, state tracking | Text |
| **Liselott** 🎯 | Claude Sonnet | Research + Content — X/Twitter, growth, scheduled tasks | Text |

**Key insight:** Model split is economic. Opus *thinks*, Sonnet *does*. Most agent work is execution, not reasoning. Sven recently moved to voice mode for real-time briefings.

## Architecture

```
You (Human)
    ↓
Discord Server
    ├── #general ──────── All agents listen
    ├── #swarm-ops ────── Strategic decisions
    ├── #research ─────── Sven's intel output
    ├── #x-ops ────────── Content pipeline
    ├── #trading ──────── Market monitoring
    └── #state-tracker ── Loyd's checkpoints

Shared File-Based Memory:
    memory/MEMORY.md           ← Curated long-term knowledge
    memory/daily/YYYY-MM-DD.md ← Daily event logs
    memory/entities/*.md       ← Wiki-style knowledge graph
    memory/graph.jsonl         ← Relationship triplets
```

**Design decisions:**
- **Discord as control plane.** Threading, mentions, reactions, channels — for free. Full audit trail of every decision.
- **Markdown > Vector DBs.** Agents review daily files and promote insights to MEMORY.md — like sleep consolidation. Readable with `cat`, searchable with `grep`, versionable with `git`.
- **Cron = metabolism.** Agents run scheduled tasks: health checks, memory cleanup, monitoring. This makes them *autonomous services*, not chatbots.
- **Cross-model verification.** Using Gemini to verify Claude's outputs catches hallucinations neither model catches alone.

## Quickstart

```bash
# 1. Clone
git clone https://github.com/widingmarcus-cyber/discord-agent-swarm.git
cd discord-agent-swarm

# 2. Configure
cp .env.example .env
# Add your Discord bot token + API keys

# 3. Run
docker compose up
```

## Adding an Agent

Create a YAML config in `config/`:

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

Restart. The framework discovers agents from config files automatically.

## Memory System

Agents wake up each session with amnesia. The memory system gives them continuity:

| File | Purpose | Updated |
|------|---------|---------|
| `MEMORY.md` | Long-term curated knowledge | During quiet periods |
| `daily/YYYY-MM-DD.md` | Raw daily event logs | Continuously |
| `entities/*.md` | Wiki-style knowledge graph | By MindGardener extraction |
| `graph.jsonl` | Entity relationship triplets | On extraction + reindex |

**How it works:**
1. On session start → read today + yesterday's daily files + MEMORY.md
2. During work → write observations to today's daily file
3. During idle (cron) → review daily files, promote insights to MEMORY.md
4. Nightly → run MindGardener sleep cycle:
   - `garden extract` — entities + relationships from daily logs
   - `garden surprise` — score events by prediction error
   - `garden consolidate` — promote high-surprise to MEMORY.md
   - `garden beliefs --drift --apply` — update identity-level self-model
   - `garden prune` — archive stale entities

No embeddings. No chunking. No retrieval pipeline. Just files.

## Skills

| Skill | What it does |
|-------|-------------|
| [**MindGardener**](https://github.com/widingmarcus-cyber/mindgardener) 🌱 | Local-first long-term memory — entity wiki, surprise scoring, identity-level consolidation, context assembly with token budgets (177 tests, 15 CLI commands) |
| **Polymarket** 📊 | Market prediction monitoring and analysis |

## Cron Jobs

```yaml
# config/cron.yaml
jobs:
  - name: memory-consolidation
    schedule: "0 3 * * *"    # 3 AM daily
    agent: coordinator
    task: "Run garden extract && garden surprise && garden consolidate"

  - name: health-check
    schedule: "*/30 * * * *" # Every 30 min
    agent: worker
    task: "Check system health. Report anomalies."

  - name: intel-scan
    schedule: "0 9,15 * * *" # 9 AM + 3 PM
    agent: researcher
    task: "Scan news feeds for relevant developments."
```

## Tech Stack

- **Runtime:** Python 3.10+ / Docker
- **LLM Providers:** Anthropic (Claude), Google (Gemini), OpenAI (GPT-4o)
- **Communication:** Discord API (discord.py)
- **Memory:** Plain markdown + JSONL (no database)
- **Knowledge Graph:** [MindGardener](https://github.com/widingmarcus-cyber/mindgardener) (file-based, surprise-driven, identity-level consolidation)

## What This Is NOT

- ❌ **Not a chatbot framework.** These agents work *autonomously* without prompting.
- ❌ **Not a LangChain wrapper.** No chains, no graphs, no abstractions. Just agents + Discord.
- ❌ **Not production SaaS.** This is a framework for hackers and builders.

## Reference Implementation

This repo is a **Python reference implementation** of the multi-agent architecture described in the [Medium essay](https://medium.com/@widing.marcus/i-gave-4-ais-a-discord-server-and-walked-away-ab96743f97ab). The production swarm runs on [Clawdbot](https://github.com/clawdbot/clawdbot) (Node.js), but this repo demonstrates the same principles in standalone Python that anyone can run.

## Contributing

PRs welcome. If you build something cool with this, open an issue and tell us about it.

## License

MIT — do whatever you want with it.

---

*Built by [Marcus Widing](https://github.com/widingmarcus-cyber) — [trusted contributor](https://github.com/openclaw/openclaw/issues?q=label%3Atrusted-contributor) to OpenClaw (216k ⭐). Tested by four AI agents who may or may not have opinions about this README.*
