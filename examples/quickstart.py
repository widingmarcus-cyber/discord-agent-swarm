"""
Quickstart: Run a single agent in Discord in under 20 lines.

Usage:
    DISCORD_BOT_TOKEN=xxx ANTHROPIC_API_KEY=xxx python examples/quickstart.py
"""

import os
import discord
import anthropic

client = discord.Client(intents=discord.Intents.default() | discord.Intents(message_content=True))
llm = anthropic.Anthropic()

SYSTEM = "You are a helpful AI assistant in a Discord server. Be concise."


@client.event
async def on_message(message):
    if message.author == client.user or not client.user.mentioned_in(message):
        return

    async with message.channel.typing():
        response = llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM,
            messages=[{"role": "user", "content": message.content}],
        )
    await message.channel.send(response.content[0].text[:2000])


client.run(os.environ["DISCORD_BOT_TOKEN"])
