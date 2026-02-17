# Engram — Memory Skill for Discord Agent Swarm

Persistent wiki-style memory with surprise-driven consolidation.

## Setup

```bash
pip install agent-engram
# or use the bundled source in this directory
```

## Usage in Agent Config

Add to your agent's tools or cron:

```yaml
# Nightly sleep cycle (in cron)
- name: engram-sleep
  schedule: "0 3 * * *"
  command: "engram extract && engram surprise && engram consolidate"

# Context retrieval (in agent prompt)
# "Before answering questions about people/projects, run: engram recall 'topic'"
```

## Shared Brain

All agents can share the same `memory/entities/` directory. Symlink it:

```bash
ln -s /path/to/shared/memory/entities /agent/memory/entities
```
