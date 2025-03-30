import discord
from discord.ext import commands
from database.models import ReactionRoleMapping
import re

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="reactionrole", aliases=["rr"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def reactionrole(self, ctx):
        """Manage reaction roles. Subcommands: add, remove, list."""
        await ctx.send("Available subcommands: add, remove, list.\nUsage: `,reactionrole add <message link> <emoji> <role>`")

    @reactionrole.command(name="add")
    @commands.has_permissions(administrator=True)
    async def reactionrole_add(self, ctx, message_link: str, emoji: str, role: discord.Role):
        pattern = r"https?://(?:canary\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)"
        match = re.match(pattern, message_link)
        if not match:
            await ctx.send("Invalid message link format.")
            return

        guild_id, channel_id, message_id = match.groups()
        channel_id = int(channel_id)
        message_id = int(message_id)

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            await ctx.send("Channel not found or bot doesn't have access.")
            return

        try:
            message = await channel.fetch_message(message_id)
        except Exception:
            await ctx.send("Failed to fetch the message. Make sure the bot can access the channel.")
            return

        try:
            await message.add_reaction(emoji)
        except Exception as e:
            await ctx.send(f"Failed to add reaction: {e}")
            return

        existing = await ReactionRoleMapping.get_or_none(message_id=message_id, emoji=emoji)
        if existing:
            existing.role_id = role.id
            await existing.save()
        else:
            await ReactionRoleMapping.create(
                guild_id=ctx.guild.id,
                message_id=message_id,
                emoji=emoji,
                role_id=role.id
            )

        await ctx.send(f"Mapping added: React with {emoji} on [this message]({message_link}) to receive the **{role.name}** role.")

    @reactionrole.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def reactionrole_remove(self, ctx, message_link: str, emoji: str):
        pattern = r"https?://(?:canary\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)"
        match = re.match(pattern, message_link)
        if not match:
            await ctx.send("Invalid message link format.")
            return

        _, _, message_id = match.groups()
        message_id = int(message_id)

        await ReactionRoleMapping.filter(message_id=message_id, emoji=emoji).delete()
        await ctx.send("Mapping removed.")

    @reactionrole.command(name="list")
    @commands.has_permissions(administrator=True)
    async def reactionrole_list(self, ctx):
        rows = await ReactionRoleMapping.filter(guild_id=ctx.guild.id).all()
        if not rows:
            await ctx.send("No reaction role mappings set.")
            return
        lines = []
        for row in rows:
            role_obj = ctx.guild.get_role(row.role_id)
            role_name = role_obj.name if role_obj else "Unknown Role"
            lines.append(f"Message ID {row.message_id}: {row.emoji} => {role_name}")
        await ctx.send("\n".join(lines))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        row = await ReactionRoleMapping.get_or_none(message_id=payload.message_id, emoji=str(payload.emoji))
        if not row:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        role = guild.get_role(row.role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        try:
            await member.add_roles(role)
            print(f"Added role {role.name} to {member.display_name}")
        except Exception as e:
            print(f"Failed to add role: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        row = await ReactionRoleMapping.get_or_none(message_id=payload.message_id, emoji=str(payload.emoji))
        if not row:
            return

        role = guild.get_role(row.role_id)
        if role is None:
            return

        try:
            await member.remove_roles(role)
            print(f"Removed role {role.name} from {member.display_name}")
        except Exception as e:
            print(f"Failed to remove role: {e}")

async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
