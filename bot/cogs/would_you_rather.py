import discord
from discord.ext import commands
import os
import random
import asyncpraw

class WouldYouRather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize the Async PRAW Reddit instance using credentials from the environment.
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="otacon bot",
            password=os.getenv("REDDIT_PASSWORD"),
            username=os.getenv("REDDIT_USERNAME"),
        )

    @commands.command(name="wouldyourather", aliases=["wyr"])
    async def would_you_rather(self, ctx):
        """
        Presents a "Would You Rather?" question sourced from r/wouldyourather on Reddit.
        
        The bot fetches a random question from the HOT category, posts it in an embed,
        and adds two reactions: 🔴 for option 1 and 🔵 for option 2.
        """
        try:
            # Get the r/wouldyourather subreddit.
            subreddit = await self.reddit.subreddit("wouldyourather")
            posts = []
            # Retrieve up to 20 hot posts.
            async for post in subreddit.hot(limit=100):
                # Skip stickied posts.
                if not post.stickied and post.title:
                    posts.append(post)
            if not posts:
                await ctx.send("Couldn't find any 'Would You Rather' questions right now. Try again later!")
                return

            chosen = random.choice(posts)
            question = chosen.title

            # Create an embed to display the question.
            embed = discord.Embed(
                title="Would You Rather?",
                description=question,
                color=discord.Color.blue()
            )
            embed.set_footer(text="React with ⬅️ for option 1 or ➡️ for option 2!")

            # Send the embed and add reaction emojis.
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")

        except Exception as e:
            await ctx.send("An error occurred while fetching a 'Would You Rather' question.")
            print(f"Error in would_you_rather command: {e}")

async def setup(bot):
    await bot.add_cog(WouldYouRather(bot))
