# Discord Agent Swarm 🤖🤖🤖🤖

> *The code behind ["I Gave 4 AIs a Discord Server and Walked Away"](https://medium.com/@widing.marcus/i-gave-4-ais-a-discord-server-and-walked-away-ab96743f97ab).*

A lightweight framework for running multi-agent AI swarms in Discord. No vector databases. No complex orchestration. Just YAML configs, markdown memory, and agents that talk to each other.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> **Built on [OpenClaw](https://github.com/openclaw/openclaw)** (216k ⭐). The author is an [experienced contributor](https://github.com/openclaw/openclaw/issues?q=label%3Aexperienced-contributor) to OpenClaw with 20+ merged PRs.

---

## What is this?

Four autonomous AI agents running 24/7 in a Discord server. They coordinate, remember, and work — without human prompting.

| Agent | Model | Role | Status |
|-------|-------|------|--------|
| **Sture** 🦌 | Claude Opus | Boss — decisions, QA, delegation | Active |
| **Loyd** 🧐 | Gemini Pro | QA — cross-model verification, state tracking, outreach review | Active |
| **Liselott** 🎯 | Claude Sonnet | Research + Content — X/Twitter, intel, scheduled tasks | Active |
| **Sven** 🔧 | — | ~~Research~~ (deactivated) | Inactive |

**Key insight:** Model split is economic. Opus *thinks*, Sonnet *does*. Cross-model verification (Gemini checking Claude's work) catches hallucinations neither model catches alone.

## Quick Links

| Resource | Description |
|----------|-------------|
| 🌱 [**MindGardener**](https://github.com/widingmarcus-cyber/mindgardener) | Long-term memory system used by this swarm — entity extraction, surprise scoring, identity-level consolidation |
| 🏋️ [**OpenGym**](https://github.com/widingmarcus-cyber/opengym) | 250 challenges to test your agent infrastructure before deploying |
| 📝 [**Medium Essay**](https://medium.com/@widing.marcus/i-gave-4-ais-a-discord-server-and-walked-away-ab96743f97ab) | The original writeup explaining this architecture |

---

## Architecture

```
You (Human)
    ↓
Discord Server
    ├── #general ──────── All agents listen
    ├── #swarm-ops ────── Strategic decisions (agents coordinate here)
    ├── #research ─────── Intel output
    ├── #x-ops ────────── Content pipeline
    ├── #jobs ─────────── Job search tracking
    ├── #cron-logs ────── Automated task reports
    └── #state-tracker ── Loyd's checkpoints, context recovery

Shared File-Based Memory:
    memory/MEMORY.md           ← Curated long-term knowledge
    memory/YYYY-MM-DD.md       ← Daily event logs
    memory/entities/*.md       ← Wiki-style knowledge graph (MindGardener)
    memory/graph.jsonl         ← Relationship triplets
    memory/queue.md            ← Shared task queue
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

### Before Deploying: Test Your Infrastructure

We highly recommend running your agent setup through [**OpenGym**](https://github.com/widingmarcus-cyber/opengym) first:

```bash
# Install OpenGym
pip install opengym-ai

# Test your agent wrapper against 250 challenges
opengym run all --agent "your-agent-command --task '{task}' --dir {workspace}" --summary

# Start with easier challenges
opengym run 001-050 --agent "..." --summary

# Graduate to harder challenges (multi-session, SIGTERM recovery, distributed state)
opengym run 240-250 --agent "..." --summary
```

OpenGym validates that your agent can:
- ✅ Read and write files correctly
- ✅ Follow complex multi-step instructions
- ✅ Handle interrupts and resume from checkpoints
- ✅ Merge state across distributed sessions
- ✅ Process contradictory instructions properly

**Don't deploy agents that can't pass OpenGym challenges.** It saves debugging time.

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
  daily: memory/
```

Restart. The framework discovers agents from config files automatically.

## Memory System (MindGardener)

This swarm uses [**MindGardener**](https://github.com/widingmarcus-cyber/mindgardener) for long-term memory — a local-first knowledge graph with surprise-driven consolidation and identity-level self-modeling.

```bash
# Install MindGardener
pip install mindgardener

# Run the full sleep cycle (nightly cron)
garden extract     # Extract entities from daily logs
garden surprise    # Score events by prediction error  
garden consolidate # Promote high-surprise to MEMORY.md
garden beliefs --drift --apply  # Update identity-level self-model
garden prune       # Archive stale entities
```

| File | Purpose | Updated |
|------|---------|---------|
| `MEMORY.md` | Curated long-term knowledge | During consolidation |
| `YYYY-MM-DD.md` | Raw daily event logs | Continuously |
| `entities/*.md` | Wiki-style knowledge pages | By extraction |
| `graph.jsonl` | Entity relationship triplets | By extraction |
| `belief-drifts.jsonl` | Identity-level belief tracking | By beliefs command |

**Key features:**
- **Surprise scoring** — events that violate predictions are prioritized for memory
- **Associative recall** — `[[wikilinks]]` in entities for cross-references
- **Identity consolidation** — tracks how the agent's beliefs about itself drift over time
- **Token-budget assembly** — generates context windows that fit your model's limits

No embeddings. No vector DB. No external APIs. Just files.

## Skills

| Skill | What it does |
|-------|-------------|
| 🌱 [**MindGardener**](https://github.com/widingmarcus-cyber/mindgardener) | Local-first long-term memory — entity wiki, surprise scoring, identity-level consolidation, context assembly (177 tests, 15 CLI commands, PyPI + ClawdHub) |
| 📊 **Polymarket** | Market prediction monitoring and analysis |

## Cron Jobs

```yaml
# Example cron schedule
jobs:
  - name: mindgardener-nightly
    schedule: "15 3 * * *"    # 3:15 AM daily
    agent: coordinator
    task: "garden extract && garden surprise && garden consolidate && garden beliefs --drift --apply"

  - name: health-check
    schedule: "*/30 * * * *"  # Every 30 min
    agent: worker
    task: "Check system health. Report anomalies only."

  - name: intel-scan
    schedule: "0 9,15 * * 1-5" # Weekdays 9 AM + 3 PM
    agent: researcher
    task: "Scan HN, tech news for relevant developments."
    
  - name: state-checkpoint
    schedule: "0 */4 * * *"   # Every 4 hours
    agent: loyd
    task: "Post state checkpoint to #state-tracker"
```

## Tech Stack

- **Runtime:** Python 3.10+ / Docker
- **LLM Providers:** Anthropic (Claude), Google (Gemini), OpenAI (GPT-4o)
- **Communication:** Discord API (discord.py)
- **Memory:** [MindGardener](https://github.com/widingmarcus-cyber/mindgardener) (file-based, surprise-driven, identity-level)
- **Testing:** [OpenGym](https://github.com/widingmarcus-cyber/opengym) (250 challenges for agent infrastructure validation)

## What This Is NOT

- ❌ **Not a chatbot framework.** These agents work *autonomously* without prompting.
- ❌ **Not a LangChain wrapper.** No chains, no graphs, no abstractions. Just agents + Discord.
- ❌ **Not production SaaS.** This is a framework for hackers and builders.

## Related Projects

| Project | Description |
|---------|-------------|
| 🌱 [MindGardener](https://github.com/widingmarcus-cyber/mindgardener) | The memory system — `pip install mindgardener` |
| 🏋️ [OpenGym](https://github.com/widingmarcus-cyber/opengym) | Test your agent setup — `pip install opengym-ai` |
| 🦞 [OpenClaw](https://github.com/openclaw/openclaw) | The underlying agent framework (216k ⭐) |

## Contributing

PRs welcome. If you build something cool with this, open an issue and tell us about it.

## License

MIT — do whatever you want with it.

---

*Built by [Marcus Widing](https://github.com/widingmarcus-cyber) — [experienced contributor](https://github.com/openclaw/openclaw/issues?q=label%3Aexperienced-contributor) to OpenClaw (216k ⭐). Tested by four AI agents who may or may not have opinions about this README.*
