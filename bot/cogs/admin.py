import discord
from discord.ext import commands

class Shutdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shutdown")
    async def shutdown(self, ctx):
        """Shuts down the bot. (Only usable by the bot owner.)"""
        # Check if the author is the designated owner.
        if ctx.author.id != 295589647340273665:
            await ctx.send("You are not authorized to use this command.")
            return

        await ctx.send("Shutting down gracefully...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Shutdown(bot))
