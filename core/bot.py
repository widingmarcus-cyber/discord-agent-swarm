"""
Discord Agent Swarm — Core Bot

Connects agents to Discord, routes messages, handles mentions.
Each agent defined in config/ becomes a listener in its assigned channels.
"""

import os
import asyncio
import logging
from pathlib import Path

import discord
import yaml

from core.llm import LLMClient
from core.memory import MemoryManager

logger = logging.getLogger(__name__)


class AgentBot(discord.Client):
    """A Discord bot that hosts multiple AI agents."""

    def __init__(self, config_dir: str = "config"):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)

        self.config_dir = Path(config_dir)
        self.agents: dict[str, dict] = {}
        self.llm = LLMClient()
        self.memory = MemoryManager()
        self._load_agents()

    def _load_agents(self):
        """Load agent configurations from YAML files."""
        for config_file in self.config_dir.glob("*.yaml"):
            if config_file.name == "cron.yaml":
                continue
            with open(config_file) as f:
                config = yaml.safe_load(f)
            name = config["name"].lower()
            self.agents[name] = config
            logger.info(f"Loaded agent: {config['name']} ({config['model']})")

    async def on_ready(self):
        logger.info(f"Swarm online: {self.user} with {len(self.agents)} agents")
        for name, agent in self.agents.items():
            logger.info(f"  → {agent['name']} listening on: {agent.get('channels', ['all'])}")

    async def on_message(self, message: discord.Message):
        # Don't respond to ourselves
        if message.author == self.user:
            return

        # Determine which agent(s) should respond
        channel_name = message.channel.name if hasattr(message.channel, "name") else "dm"
        content = message.content.lower()

        for name, agent in self.agents.items():
            if self._should_respond(agent, channel_name, content):
                await self._handle_message(agent, message)
                break  # One agent per message

    def _should_respond(self, agent: dict, channel: str, content: str) -> bool:
        """Determine if an agent should respond to a message."""
        agent_name = agent["name"].lower()

        # Direct mention of agent name
        if agent_name in content:
            return True

        # Agent is assigned to this channel and is the primary responder
        agent_channels = agent.get("channels", [])
        if channel in agent_channels:
            # Only coordinator responds to general unless specifically mentioned
            if channel == "general" and agent.get("role") != "coordinator":
                return False
            return True

        return False

    async def _handle_message(self, agent: dict, message: discord.Message):
        """Process a message with the specified agent."""
        # Load memory context
        context = self.memory.get_context(agent)

        # Build the prompt
        system = agent.get("system_prompt", "You are a helpful assistant.")
        system += f"\n\nMemory context:\n{context}"

        # Get response from LLM
        async with message.channel.typing():
            response = await self.llm.chat(
                model=agent["model"],
                system=system,
                message=message.content,
                tools=agent.get("tools", []),
            )

        # Save to daily memory
        self.memory.log_interaction(
            agent=agent["name"],
            channel=message.channel.name if hasattr(message.channel, "name") else "dm",
            user=str(message.author),
            message=message.content,
            response=response,
        )

        # Send response (split if too long for Discord)
        for chunk in self._split_message(response):
            await message.channel.send(chunk)

    @staticmethod
    def _split_message(text: str, limit: int = 2000) -> list[str]:
        """Split a message into chunks that fit Discord's character limit."""
        if len(text) <= limit:
            return [text]
        chunks = []
        while text:
            if len(text) <= limit:
                chunks.append(text)
                break
            # Find a good split point
            split_at = text.rfind("\n", 0, limit)
            if split_at == -1:
                split_at = limit
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip("\n")
        return chunks


def main():
    logging.basicConfig(level=logging.INFO)
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN not set. Copy .env.example to .env and add your token.")

    bot = AgentBot()
    bot.run(token)


if __name__ == "__main__":
    main()
