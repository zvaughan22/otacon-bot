import discord
from discord.ext import commands
import asyncio
import time

class RoleCycler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_id = 223584043348918272
        self.role_ids = [
            1065799110503972904,
            1355652652582572042,
            1355650922121793616,
            1355650913884176515,
            1355650835220271325,
            1355651018351710500,
            1355651018351710500,
            1355650789716005047,
            1355649349132226631,
            1355650740856819884,
            1355650740856819884,
            1355649492031901757
        ]
        self.current_index = 0
        self.guild_id = 687015840989577268  # Replace with your guild/server ID.
        # Start the custom background task.
        self.task = self.bot.loop.create_task(self.role_cycle_loop())

    def cog_unload(self):
        # Cancel the background task when the cog is unloaded.
        self.task.cancel()

    async def role_cycle_loop(self):
        while True:
            start_time = time.perf_counter()
            guild = self.bot.get_guild(self.guild_id)
            if guild is None:
                await asyncio.sleep(0.5)
                continue

            member = guild.get_member(self.user_id)
            if member is None:
                await asyncio.sleep(0.5)
                continue

            # Get the role to add this cycle.
            role_id = self.role_ids[self.current_index]
            new_role = guild.get_role(role_id)
            if new_role is None:
                print(f"Role with ID {role_id} not found in guild {guild.name}.")
            else:
                # Remove any roles from our list that the member already has.
                roles_to_remove = [guild.get_role(rid) for rid in self.role_ids if guild.get_role(rid) in member.roles]
                try:
                    if roles_to_remove:
                        await member.remove_roles(*roles_to_remove, reason="Cycling color roles")
                    await member.add_roles(new_role, reason="Cycling color roles")
                except discord.Forbidden:
                    print("Missing permissions to modify roles for", member)
                except Exception as e:
                    print("Error while cycling roles:", e)

            # Move to the next role in the list.
            self.current_index = (self.current_index + 1) % len(self.role_ids)

            # Calculate the elapsed time and wait for the remaining interval.
            elapsed = time.perf_counter() - start_time
            sleep_time = max(0.5 - elapsed, 0)
            await asyncio.sleep(sleep_time)

async def setup(bot):
    await bot.add_cog(RoleCycler(bot))
