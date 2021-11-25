from typing import Union
import asyncio

import disnake
from disnake.ext import commands

from utils import Context, is_mod, is_admin, is_owner

from main import Ukiyo


class Moderation(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @commands.command(name='purge', aliases=('clear',))
    @is_mod()
    async def chat_purge(self, ctx: Context, *, amount: int):
        """Clear the ``amount`` of messages from the chat."""

        await ctx.message.delete()
        purged = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f'> <:agree:913517732249612348> Deleted `{len(purged):,}` messages')
        await asyncio.sleep(5.0)
        try:
            await msg.delete()
        except disnake.HTTPException:
            pass

    @commands.command(name='ban')
    @is_admin()
    async def _ban(self, ctx: Context, member: Union[disnake.Member, disnake.User], *, reason: str):
        """Bans a user."""

        if ctx.author.top_role <= member.top_role:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        try:
            await member.send('> Hello! Sadly, have been **banned** from `Ukiyo`. Goodbye 👋')
        except disnake.Forbidden:
            pass
        await member.ban(reason=f'{ctx.author} ({ctx.author.id}): {reason}')
        await ctx.send(f'> 👌🔨 Banned {member} for **{reason}**')

    @commands.command(name='kick')
    @is_mod()
    async def _kick(self, ctx: Context, member: Union[disnake.Member, disnake.User], *, reason: str):
        """Kicks a user."""

        if ctx.author.top_role <= member.top_role:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        try:
            await member.send('> Hello! Sadly, have been **kicked** from `Ukiyo`. Goodbye 👋')
        except disnake.Forbidden:
            pass
        await member.kick(reason=f'{ctx.author} ({ctx.author.id}): {reason}')
        await ctx.send(f'> 👌 Kicked {member} for **{reason}**')

    @commands.group(name='make', invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    @is_admin()
    async def owner_make(self, ctx: Context):
        """Shows this help."""

        await ctx.send_help('make')

    @owner_make.command(name='admin')
    @is_owner()
    async def owner_make_admin(self, ctx: Context, *, member: disnake.Member):
        """Make somebody an admin."""

        if ctx.author.top_role <= member.top_role:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        guild = self.bot.get_guild(913310006814859334)
        if 913315033134542889 in (r.id for r in member.roles):
            return await ctx.reply(f'`{member}` is already an admin!')
        admin_role = guild.get_role(913315033134542889)
        await member.edit(roles=[r for r in member.roles if r.id != 913315033684008971] + admin_role)
        await ctx.reply(f'> 👌 Successfully made `{member}` an admin.')

    @owner_make.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def owner_make_mod(self, ctx: Context, *, member: disnake.Member):
        """Make somebody a moderator."""

        if ctx.author.top_role <= member.top_role:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        guild = self.bot.get_guild(913310006814859334)
        if 913315033684008971 in (r.id for r in member.roles):
            return await ctx.reply(f'`{member}` is already a moderator!')
        mod_role = guild.get_role(913315033684008971)
        await member.edit(roles=[r for r in member.roles if r.id != 913315033134542889] + mod_role)
        await ctx.reply(f'> 👌 Successfully made `{member}` a moderator.')

    @commands.group(name='remove', invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    @is_admin()
    async def owner_remove(self, ctx: Context):
        """Shows this help."""

        await ctx.send_help('remove')

    @owner_remove.command(name='admin')
    @is_owner()
    async def owner_remove_admin(self, ctx: Context, *, member: disnake.Member):
        """Remove an admin."""

        if ctx.author.top_role <= member.top_role:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        if 913315033134542889 not in (r.id for r in member.roles):
            return await ctx.reply(f'`{member}` is not a moderator!')
        await member.edit(roles=[r for r in member.roles if r.id != 913315033134542889])
        await ctx.reply(f'> 👌 Successfully removed `{member}` from being an admin.')

    @owner_remove.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def owner_remove_mod(self, ctx: Context, *, member: disnake.Member):
        """Remove a moderator."""

        if ctx.author.top_role <= member.top_role:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        if 913315033684008971 not in (r.id for r in member.roles):
            return await ctx.reply(f'`{member}` is not a moderator!')
        await member.edit(roles=[r for r in member.roles if r.id != 913315033684008971])
        await ctx.reply(f'> 👌 Successfully removed `{member}` from being a moderator.')


def setup(bot: Ukiyo):
    bot.add_cog(Moderation(bot))
