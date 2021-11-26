import asyncio
from typing import Union
from datetime import datetime

import disnake
from disnake.ext import commands, tasks

from utils import (
    Context,
    is_mod,
    is_admin,
    is_owner,
    UserFriendlyTime,
    Mutes,
    format_dt,
    human_timedelta
)

from main import Ukiyo


class Moderation(commands.Cog):
    """Staff related commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '⚙️'

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
        """Bans an user."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        try:
            await member.send('> Hello! Sadly, you have been **banned** from `Ukiyo`. Goodbye 👋')
        except disnake.Forbidden:
            pass
        await member.ban(reason=f'[BAN] {ctx.author} ({ctx.author.id}): {reason}')
        await ctx.send(f'> 👌🔨 Banned {member} for **{reason}**')

    @commands.command(name='kick')
    @is_mod()
    async def _kick(self, ctx: Context, member: Union[disnake.Member, disnake.User], *, reason: str):
        """Kicks a member."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        try:
            await member.send('> Hello! Sadly, you have been **kicked** from `Ukiyo`. Goodbye 👋')
        except disnake.Forbidden:
            pass
        await member.kick(reason=f'[KICK] {ctx.author} ({ctx.author.id}): {reason}')
        await ctx.send(f'> 👌 Kicked {member} for **{reason}**')

    @commands.group(name='make', invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    @is_admin()
    async def staff_make(self, ctx: Context):
        """Shows this help."""

        await ctx.send_help('make')

    @staff_make.command(name='admin')
    @is_owner()
    async def staff_make_admin(self, ctx: Context, *, member: disnake.Member):
        """Make somebody an admin."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        guild = self.bot.get_guild(913310006814859334)
        if 913315033134542889 in (r.id for r in member.roles):
            return await ctx.reply(f'`{member}` is already an admin!')
        admin_role = guild.get_role(913315033134542889)
        await member.edit(roles=[r for r in member.roles if r.id != 913315033684008971] + [admin_role])
        await ctx.reply(f'> 👌 Successfully made `{member}` an admin.')

    @staff_make.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def staff_make_mod(self, ctx: Context, *, member: disnake.Member):
        """Make somebody a moderator."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        guild = self.bot.get_guild(913310006814859334)
        if 913315033684008971 in (r.id for r in member.roles):
            return await ctx.reply(f'`{member}` is already a moderator!')
        mod_role = guild.get_role(913315033684008971)
        await member.edit(roles=[r for r in member.roles if r.id != 913315033134542889] + [mod_role])
        await ctx.reply(f'> 👌 Successfully made `{member}` a moderator.')

    @commands.group(name='remove', invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    @is_admin()
    async def staff_remove(self, ctx: Context):
        """Shows this help."""

        await ctx.send_help('remove')

    @staff_remove.command(name='admin')
    @is_owner()
    async def staff_remove_admin(self, ctx: Context, *, member: disnake.Member):
        """Remove an admin."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        if 913315033134542889 not in (r.id for r in member.roles):
            return await ctx.reply(f'`{member}` is not a moderator!')
        await member.edit(roles=[r for r in member.roles if r.id != 913315033134542889])
        await ctx.reply(f'> 👌 Successfully removed `{member}` from being an admin.')

    @staff_remove.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def staff_remove_mod(self, ctx: Context, *, member: disnake.Member):
        """Remove a moderator."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        if 913315033684008971 not in (r.id for r in member.roles):
            return await ctx.reply(f'`{member}` is not a moderator!')
        await member.edit(roles=[r for r in member.roles if r.id != 913315033684008971])
        await ctx.reply(f'> 👌 Successfully removed `{member}` from being a moderator.')

    @commands.command(name='mute')
    @is_mod()
    async def mute_cmd(
        self,
        ctx: Context,
        member: disnake.Member,
        *,
        time_and_reason: UserFriendlyTime(commands.clean_content)
    ):
        """
        Mute somebody.

        Example:
        `!mute @carrot 2m coolest person alive`
        `!mute @carrot coolest person alive 2m`
        """

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply('That member is above or equal to you. Cannot do that.')

        is_staff = False
        time = time_and_reason.dt
        reason = time_and_reason.arg
        data = Mutes(
            id=member.id,
            muted_by=ctx.author.id,
            muted_until=time
        )
        if 913310292505686046 in member.roles:  # Checks for owner
            data.is_owner = True
            is_staff = True
        elif 913315033134542889 in member.roles:  # Checks for admin
            data.is_admin = True
            is_staff = True
        elif 913315033684008971 in member.roles:  # Checks for mod
            data.is_mod = True
            is_staff = True
        await data.commit()

        guild = self.bot.get_guild(913310006814859334)
        muted_role = guild.get_role(913376647422545951)
        if is_staff is True:
            new_roles = [role for role in member.roles
                         if role.id not in (913310292505686046, 913315033134542889, 913315033684008971)
                         ] + muted_role
        else:
            new_roles = [role for role in member.roles
                         if role.id not in (913310292505686046, 913315033134542889, 913315033684008971)]

        await member.edit(roles=new_roles, reason=f'[MUTE] {ctx.author} ({ctx.author.id}): {reason}')
        try:
            await member.send(
                f'Hello, you have been muted in `Ukiyo` by **{ctx.author}** for **{reason}** '
                f'until {format_dt(time, "F")} (`{human_timedelta(time, suffix=False)}`)'
            )
        except disnake.Forbidden:
            pass
        await ctx.reply(
            f'> 👌📨 Applied mute to {member.mention} for **{reason}** '
            f'until {format_dt(time, "F")} (`{human_timedelta(time, suffix=False)}`)'
        )

    @commands.command(name='unmute')
    async def unmute_cmd(self, ctx: Context, *, member: disnake.Member):
        """Unmute somebody that is currently muted."""

        data: Mutes = await Mutes.find_one({'_id': member.id})
        if not data:
            return await ctx.reply(f'`{member}` is not muted!')
        await data.delete()

        guild = self.bot.get_guild(913310006814859334)
        new_roles = [role for role in member.roles if not role.id == 913376647422545951]
        if data.is_owner is True:
            owner_role = guild.get_role(913310292505686046)  # Check for owner
            new_roles += [owner_role]
        elif data.is_admin is True:
            admin_role = guild.get_role(913315033134542889)  # Check for admin
            new_roles += [admin_role]
        elif data.is_mod is True:
            mod_role = guild.get_role(913315033684008971)  # Check for mod
            new_roles += [mod_role]
        await member.edit(roles=new_roles, reason=f'[UNMUTE] Unmuted by {ctx.author} ({ctx.author.id})')
        try:
            await member.send(f'Hello, you have been **unmuted** in `Ukiyo` by {ctx.author}')
        except disnake.Forbidden:
            pass

        await ctx.reply(f'> 👌 Successfully unmuted {member.mention}')

    @mute_cmd.error
    async def mute_cmd_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.reply(error)
        await self.bot.reraise(ctx, error)

    @tasks.loop(seconds=15.0)
    async def check_unmutes(self):
        mutes: list[Mutes] = await Mutes.find().sort('muted_until', 1).to_list(5)
        for mute in mutes:
            if datetime.utcnow() >= mute.muted_until:
                guild = self.bot.get_guild(913310006814859334)
                member = guild.get_member(mute.id)
                if member:
                    new_roles = [role for role in member.roles if not role.id == 913376647422545951]
                    if mute.is_owner is True:
                        owner_role = guild.get_role(913310292505686046)  # Check for owner
                        new_roles += [owner_role]
                    elif mute.is_admin is True:
                        admin_role = guild.get_role(913315033134542889)  # Check for admin
                        new_roles += [admin_role]
                    elif mute.is_mod is True:
                        mod_role = guild.get_role(913315033684008971)  # Check for mod
                        new_roles += [mod_role]
                    await member.edit(roles=new_roles, reason='[UNMUTE] Mute Expired.')
                    try:
                        await member.send('Hello, your mute in `Ukiyo` has expired. You have been unmuted.')
                    except disnake.Forbidden:
                        pass
                await mute.delete()


def setup(bot: Ukiyo):
    bot.add_cog(Moderation(bot))
