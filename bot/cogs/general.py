from discord.ext import commands

import discord
from discord.ext import commands

class PaginatorView(discord.ui.View):
    def __init__(self, embeds, author, timeout=60):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.author = author

    async def update_message(self, interaction: discord.Interaction):
        embed = self.embeds[self.current_page]
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You are not allowed to use these buttons.", ephemeral=True)
            return
        self.current_page = (self.current_page - 1) % len(self.embeds)
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You are not allowed to use these buttons.", ephemeral=True)
            return
        self.current_page = (self.current_page + 1) % len(self.embeds)
        await self.update_message(interaction)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You are not allowed to use these buttons.", ephemeral=True)
            return
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

class BetterHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Remove the default help command to avoid conflicts.
        bot.remove_command("help")
        
    @commands.command(name="help")
    async def help_command(self, ctx, *, category: str = None):
        """
        A better help command with pagination and formatting.
        Optionally, pass a category to view only commands from that cog.
        Example: !help Moderation
        """
        embeds = []
        # If a category (cog) is specified, filter commands to that cog.
        if category:
            cog = None
            for cog_name, cog_obj in self.bot.cogs.items():
                if cog_name.lower() == category.lower():
                    cog = cog_obj
                    break
            if not cog:
                await ctx.send(f"No category found with name '{category}'.")
                return
            commands_list = [cmd for cmd in cog.get_commands() if not cmd.hidden]
            title = f"Help for {cog.__class__.__name__}"
        else:
            commands_list = [cmd for cmd in self.bot.commands if not cmd.hidden]
            title = "Help for All Commands"

        # Determine pagination parameters.
        per_page = 6
        pages = [commands_list[i:i + per_page] for i in range(0, len(commands_list), per_page)]
        if not pages:
            pages = [[]]

        # Build an embed for each page.
        for i, page in enumerate(pages):
            embed = discord.Embed(
                title=title,
                description=f"Page {i + 1} of {len(pages)}",
                color=discord.Color.blurple()
            )
            for command in page:
                signature = command.signature or ""
                help_text = command.help or "No description provided."
                embed.add_field(
                    name=f"{ctx.clean_prefix}{command.name} {signature}",
                    value=help_text,
                    inline=False
                )
            embeds.append(embed)

        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            view = PaginatorView(embeds, author=ctx.author)
            await ctx.send(embed=embeds[0], view=view)

async def setup(bot):
    await bot.add_cog(BetterHelp(bot))



async def setup(bot):
    await bot.add_cog(BetterHelp(bot))