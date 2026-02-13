"""
File-based memory system for agents.

No vector databases. No embeddings. Just markdown files.

How it works:
- Each agent reads MEMORY.md (long-term) + today/yesterday daily files on startup
- Interactions are logged to daily files
- During quiet periods, agents promote important bits to MEMORY.md
- Old daily files naturally age out of context
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

MEMORY_DIR = Path("memory")
DAILY_DIR = MEMORY_DIR / "daily"


class MemoryManager:
    """Manages markdown-based memory for agents."""

    def __init__(self, memory_dir: Path = MEMORY_DIR):
        self.memory_dir = memory_dir
        self.daily_dir = memory_dir / "daily"
        self.daily_dir.mkdir(parents=True, exist_ok=True)

    def get_context(self, agent: dict) -> str:
        """Build memory context for an agent's session."""
        parts = []

        # Long-term memory
        long_term = self.memory_dir / "MEMORY.md"
        if long_term.exists():
            content = long_term.read_text().strip()
            if content:
                parts.append(f"## Long-term Memory\n{content}")

        # Today's daily log
        today = datetime.now().strftime("%Y-%m-%d")
        today_file = self.daily_dir / f"{today}.md"
        if today_file.exists():
            content = today_file.read_text().strip()
            if content:
                parts.append(f"## Today ({today})\n{content}")

        # Yesterday's daily log
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_file = self.daily_dir / f"{yesterday}.md"
        if yesterday_file.exists():
            content = yesterday_file.read_text().strip()
            if content:
                parts.append(f"## Yesterday ({yesterday})\n{content}")

        return "\n\n---\n\n".join(parts) if parts else "No memory context available."

    def log_interaction(
        self,
        agent: str,
        channel: str,
        user: str,
        message: str,
        response: str,
    ):
        """Log an interaction to today's daily file."""
        today = datetime.now().strftime("%Y-%m-%d")
        today_file = self.daily_dir / f"{today}.md"

        timestamp = datetime.now().strftime("%H:%M")
        entry = (
            f"\n### {timestamp} — {agent} in #{channel}\n"
            f"**{user}:** {message[:200]}\n"
            f"**{agent}:** {response[:200]}\n"
        )

        with open(today_file, "a") as f:
            if not today_file.exists() or today_file.stat().st_size == 0:
                f.write(f"# {today}\n")
            f.write(entry)

    def read_file(self, path: str) -> str:
        """Read a memory file."""
        file_path = self.memory_dir / path
        if not file_path.exists():
            return f"File not found: {path}"
        return file_path.read_text()

    def write_file(self, path: str, content: str):
        """Write to a memory file."""
        file_path = self.memory_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        logger.info(f"Memory updated: {path}")
