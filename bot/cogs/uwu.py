import discord
from discord.ext import commands
from uwuipy import Uwuipy

def has_specific_role(role_id: int):
    def predicate(ctx):
        return any(role.id == role_id for role in ctx.author.roles)
    return commands.check(predicate)

class Uwuifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uwu = Uwuipy(None, 0.3, 0.05, 0.3, 1, True, 4)
        self.webhook_targets = set()  # Users being uwu'd via webhook

    @commands.command(name="uwu")
    async def uwu(self, ctx, *, text: str):
        """Transforms the provided text into uwu-speak."""
        uwu_text = self.uwu.uwuify(text)
        await ctx.send(uwu_text)

    @commands.command(name="uwuyou")
    @has_specific_role(775781718644752436)
    async def toggle_webhook_mode(self, ctx, action: str, member: discord.Member):
        """Toggle webhook uwu-mode for another user: !uwuyou start @user"""
        if action.lower() == "start":
            self.webhook_targets.add(member.id)
            await ctx.send(f"Webhook uwu mode activated for {member.display_name}~!")
        elif action.lower() == "stop":
            self.webhook_targets.discard(member.id)
            await ctx.send(f"Webhook uwu mode deactivated for {member.display_name}~!")
        else:
            await ctx.send("Usage: `!uwuyou start @user` or `!uwuyou stop @user`")

    @toggle_webhook_mode.error
    async def toggle_webhook_mode_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            # Log the user's roles for debugging purposes.
            user_roles = [role.id for role in ctx.author.roles]
            print(f"User {ctx.author} roles: {user_roles}")
            await ctx.send("You don't have the required role to use this command!")
        else:
            raise error

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Process webhook uwu mode if the author is in webhook_targets.
        if message.author.id in self.webhook_targets:
            uwu_text = self.uwu.uwuify(message.content)

            # Get or create webhook for this channel.
            webhooks = await message.channel.webhooks()
            webhook = discord.utils.get(webhooks, name="Otacon-UwU")
            if webhook is None:
                webhook = await message.channel.create_webhook(name="Otacon-UwU")

            await message.delete()
            await webhook.send(
                uwu_text,
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url,
                allowed_mentions=discord.AllowedMentions.none()
            )

async def setup(bot):
    await bot.add_cog(Uwuifier(bot))
