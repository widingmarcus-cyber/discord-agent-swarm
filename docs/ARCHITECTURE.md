# Architecture

## Overview

The Discord Agent Swarm is a framework for running multiple AI agents
that coordinate through Discord channels. Each agent has its own
personality, tools, and memory — but they share a common knowledge base.

## Design Principles

### 1. Model Split (Economic)

Not all tasks need expensive models. The framework supports mixing
providers and models per agent:

- **Coordinator** (Claude Opus): Strategic decisions, approvals
- **Workers** (Claude Sonnet): Research, execution, monitoring
- **Verifier** (Gemini): Cross-provider fact-checking

### 2. Discord as Control Plane

Discord provides threading, mentions, reactions, and channels for free.
Every agent decision is logged in a human-readable conversation.
You can scroll back and see exactly what happened.

### 3. Markdown Memory

No vector databases. No embeddings. Agents read markdown files:

- `MEMORY.md`: Curated long-term knowledge
- `daily/YYYY-MM-DD.md`: Raw daily event logs
- Custom files for projects, tasks, etc.

This works because agents need *continuity* (what happened yesterday),
not *similarity search* (find something like X).

### 4. Cron as Metabolism

Agents run scheduled tasks independently:
- Memory consolidation (nightly)
- Health checks (every 30 min)
- Custom monitoring tasks

This makes them autonomous services, not reactive chatbots.

## Data Flow

```
Discord Message
    → Bot receives message
    → Route to appropriate agent (by mention/channel)
    → Load agent config + memory context
    → Send to LLM with system prompt + tools
    → Execute any tool calls
    → Log interaction to daily memory
    → Send response to Discord
```

## Adding Agents

Create a YAML file in `config/`. The bot discovers agents on startup.
Each agent config defines:

- `name`: How to address the agent
- `model`: Which LLM to use
- `channels`: Which Discord channels to monitor
- `system_prompt`: The agent's personality and instructions
- `tools`: Available tool functions
- `memory`: Memory file paths

## Security

- Agents can only access files in the `memory/` directory
- Shell commands have a 30-second timeout
- API keys are never stored in memory files
- Discord permissions control who can interact with agents
