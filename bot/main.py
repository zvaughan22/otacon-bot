# otacon-bot/main.py

import discord
from discord.ext import commands
from tortoise import Tortoise
from database.tortoise_config import TORTOISE_ORM
from database.models import GuildSettings
import os, random, signal, asyncio
from dotenv import load_dotenv
import asyncpg
import time


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=",", intents=intents)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        exists = await GuildSettings.get_or_none(guild_id=guild.id)
        if not exists:
            await GuildSettings.create(guild_id=guild.id)
            print(f"[DB] Backfilled: {guild.name} ({guild.id})")
    status = random.choice([
        "Eating my own code",
        "Chasing bugs",
        "Procrastinating... again",
        "Compiling jokes",
        "Counting bits",
        "Hacking the planet... not really",
        "Riding the digital highway",
        "Dreaming in binary",
        "Breaking things so you don't have to",
        "Living the high life in Discord"
    ])
    await bot.change_presence(activity=discord.Game(name=status))
    print(f"{bot.user} is online with status: {status}")

@bot.event
async def on_guild_join(guild):
    # Check if guild already exists
    existing = await GuildSettings.get_or_none(guild_id=guild.id)
    if not existing:
        await GuildSettings.create(guild_id=guild.id)
        print(f"[DB] Added new guild to database: {guild.name} ({guild.id})")
    else:
        print(f"[DB] Guild already exists: {guild.name} ({guild.id})")

@bot.event
async def on_message(message):
    if not message.author.bot:
        await bot.process_commands(message)

async def load_cogs():
    cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded cog: {filename}")


async def init_db(retries=10, delay=2):
    for attempt in range(retries):
        try:
            await Tortoise.init(config=TORTOISE_ORM)
            await Tortoise.generate_schemas()
            print("Connected to database and ensured schema.")
            return
        except (asyncpg.exceptions.CannotConnectNowError, ConnectionRefusedError) as e:
            print(f"[DB] Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database after multiple attempts.")

async def close_db():
    await Tortoise.close_connections()
    print("Database connections closed.")

async def main():
    await init_db()

    loop = asyncio.get_running_loop()
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.close()))
    except NotImplementedError:
        pass

    try:
        async with bot:
            await load_cogs()
            for ext in ["cogs.sentiment", "cogs.RoleCycler"]:
                try:
                    await bot.unload_extension(ext)
                    print(f"Unloaded cog: {ext}")
                except commands.ExtensionNotLoaded:
                    print(f"Cog not loaded, skipping: {ext}")
            await bot.start(TOKEN)
    finally:
        await close_db()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
