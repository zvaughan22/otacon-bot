import discord
from discord.ext import commands
import os
import random
import aiohttp

class Roleplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tenor_api_key = os.getenv("TENOR_API_KEY")
        if not self.tenor_api_key:
            print("Warning: TENOR_API_KEY not set in environment!")

    async def get_gif(self, search_term: str) -> str:
        """
        Retrieve a random anime gif URL from Tenor based on the search term.
        """
        url = "https://g.tenor.com/v2/search"
        params = {
            "q": search_term,
            "key": self.tenor_api_key,
            "limit": 20,
            "media_filter": "minimal",
            "contentfilter": "off"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results")
                    if results:
                        chosen = random.choice(results)
                        gif_url = chosen["media_formats"]["gif"]["url"]
                        return gif_url
        return None

    async def send_action_embed(self, ctx, member: discord.Member, display_action: str, search_term: str):
        """
        Helper to retrieve a gif and send an embed message.
        The display_action parameter is the text to show (e.g., "punches", "hugs", "gives a high five to").
        """
        if member is None:
            # Use the first word from display_action as the action for the error message.
            action_word = display_action.split()[0]
            await ctx.send(f"Please mention a user to {action_word}!")
            return
        gif_url = await self.get_gif(search_term)
        if not gif_url:
            await ctx.send("Sorry, couldn't find a gif right now.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name} {display_action} {member.display_name}!")
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

    @commands.command(name="punch")
    async def punch(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "punches", "anime punch")

    @commands.command(name="shoot")
    async def shoot(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "shoots", "anime shoot")
    
    @commands.command(name="hug")
    async def hug(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "hugs", "anime hug")

    @commands.command(name="kiss")
    async def kiss(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "kisses", "anime kiss")

    @commands.command(name="slap")
    async def slap(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "slaps", "anime slap")

    @commands.command(name="poke")
    async def poke(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "pokes", "anime finger poke")

    @commands.command(name="dance")
    async def dance(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "dances with", "anime dance")

    @commands.command(name="cry")
    async def cry(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "cries", "anime cry")

    @commands.command(name="laugh")
    async def laugh(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "laughs with", "anime laugh")

    @commands.command(name="highfive")
    async def highfive(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "gives a high five to", "anime high five")

    @commands.command(name="pat")
    async def pat(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "pats", "anime pat")

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "kicks", "anime kick")

    @commands.command(name="tickle")
    async def tickle(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "tickles", "anime tickle")

    @commands.command(name="cuddle")
    async def cuddle(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "cuddles with", "anime cuddle")

    @commands.command(name="wink")
    async def wink(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "winks at", "anime wink")

    @commands.command(name="bonk")
    async def bonk(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "bonks", "anime bonk")

    @commands.command(name="nuzzle")
    async def nuzzle(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "nuzzles", "anime nuzzle")
    
    @commands.command(name="gaykiss")
    async def rkiss(self, ctx, member: discord.Member = None):
        await self.send_action_embed(ctx, member, "kisses", "gay kiss")

async def setup(bot):
    await bot.add_cog(Roleplay(bot))
