import asyncio
from typing import Union
from datetime import datetime

import disnake
from disnake.ext import commands, tasks

import utils
from utils import (
    Context,
    is_mod,
    is_admin,
    is_owner,
    UserFriendlyTime,
    Mutes,
    format_dt,
    human_timedelta,
    RoboPages,
    FieldPageSource,
    AnnouncementView
)

from main import Ukiyo


class Moderation(commands.Cog):
    """Staff related commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.ignored_channels = (
            913331371282423808, 913331459673178122, 913331535170637825, 913336089492717618,
            913331502761271296, 913331578606854184, 913332335473205308, 913332408537976892,
            913332431417925634, 913332511789178951, 913425733567799346, 913445987102654474
        )
        self.webhook = None

        self.check_mutes.start()

    async def ensure_webhook(self):
        if self.webhook is None:
            self.webhook = await self.bot.get_webhook(
                self.bot.get_channel(914257049456607272),
                avatar=self.bot.user.display_avatar
            )

    @property
    def display_emoji(self) -> str:
        return '🛠️'

    @commands.command()
    @is_admin()
    async def announce(self, ctx):
        """Make an announcement in <#913331371282423808>"""

        view = AnnouncementView(self.bot, ctx.author)
        view.message = await ctx.send(embed=view.prepare_embed(), view=view)

    @commands.command(name='purge', aliases=('clear',))
    @is_mod()
    async def chat_purge(self, ctx: Context, *, amount: int):
        """Clear the ``amount`` of messages from the chat."""

        await ctx.message.delete()
        purged = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f'> {ctx.agree} Deleted `{len(purged):,}` messages')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[CHAT PURGE]',
            fields=[
                ('Channel', ctx.channel.mention),
                ('Amount', f'`{utils.plural(len(purged)):message}`'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )
        await asyncio.sleep(5.0)
        try:
            await msg.delete()
        except disnake.HTTPException:
            pass

    @commands.group(name='lock', invoke_without_command=True, case_insensitive=True)
    @is_mod()
    async def lock_channel(self, ctx: Context, channel: disnake.TextChannel = None):
        """
        Locks the channel.
        No one will be able to talk in that channel except the mods, but everyone will still see the channel.
        """

        channel = channel or ctx.channel

        role = channel.guild.default_role
        if channel.id not in self.ignored_channels:
            overwrites = channel.overwrites_for(role)
            overwrites.send_messages = False
            await channel.set_permissions(role, overwrite=overwrites, reason=f'Channel locked by: "{ctx.author}"')
        else:
            return await ctx.reply(f'> {ctx.disagree} That channel cannot be unlocked.')
        await ctx.reply('> 🔒 Channel Locked!')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[CHANNEL LOCK]',
            fields=[
                ('Channel', channel.mention),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @lock_channel.command(name='all')
    @is_mod()
    async def lock_all_channels(self, ctx: Context):
        """
        Locks *all* the channels that are have not been locked, but omits the channels that the users can't see or talk in already.
        """

        _channels = []
        role = ctx.guild.default_role
        for channel in ctx.guild.text_channels:
            if channel.id not in self.ignored_channels:
                if channel.overwrites_for(role).send_messages is not False:
                    overwrites = channel.overwrites_for(role)
                    overwrites.send_messages = False
                    await channel.set_permissions(
                        role,
                        overwrite=overwrites,
                        reason=f'Channel locked by: "{ctx.author}"'
                    )
                    _channels.append(channel.mention)
        await ctx.reply('> 🔒 All the unlocked channels have been locked!')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[CHANNEL LOCK]',
            fields=[
                ('Channel', ' '.join(_channels)),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.group(name='unlock', invoke_without_command=True, case_insensitive=True)
    @is_mod()
    async def unlock_channel(self, ctx: Context, channel: disnake.TextChannel = None):
        """
        Unlocks the channel.
        """

        channel = channel or ctx.channel

        role = channel.guild.default_role
        if channel.id not in self.ignored_channels:
            overwrites = channel.overwrites_for(role)
            overwrites.send_messages = None
            await channel.set_permissions(role, overwrite=overwrites, reason=f'Channel unlocked by: "{ctx.author}"')
        else:
            return await ctx.reply(f'> {ctx.disagree} That channel cannot be unlocked.')
        await ctx.reply('> 🔓 Channel Unlocked!')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[CHANNEL UNLOCK]',
            fields=[
                ('Channel', channel.mention),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @unlock_channel.command(name='all')
    @is_mod()
    async def unlock_all_channels(self, ctx: Context):
        """
        Unlocks *all the already locked* channels, but omits the channels that the users can't see or talk in already.
        """

        _channels = []
        role = ctx.guild.default_role
        for channel in ctx.guild.text_channels:
            if channel.id not in self.ignored_channels:
                if channel.overwrites_for(role).send_messages is not None:
                    overwrites = channel.overwrites_for(role)
                    overwrites.send_messages = None
                    await channel.set_permissions(
                        role,
                        overwrite=overwrites,
                        reason=f'Channel unlocked by: "{ctx.author}"'
                    )
                    _channels.append(channel.mention)
        await ctx.reply('> 🔓 All locked channels have been unlocked!')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[CHANNEL UNLOCK]',
            fields=[
                ('Channel', ' '.join(_channels)),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.command(name='ban')
    @is_admin()
    async def _ban(self, ctx: Context, member: Union[disnake.Member, disnake.User], *, reason: str):
        """Bans an user."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        try:
            await member.send('> Hello! Sadly, you have been **banned** from `Ukiyo`. Goodbye 👋')
        except disnake.Forbidden:
            pass
        await member.ban(reason=f'[BAN] {ctx.author} ({ctx.author.id}): {reason}', delete_message_days=0)
        await ctx.send(f'> 👌🔨 Banned {member.mention} for **{reason}**')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[BAN]',
            fields=[
                ('Member', f'{member.mention} (`{member.id}`)'),
                ('Reason', reason),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.command(name='kick')
    @is_mod()
    async def _kick(self, ctx: Context, member: disnake.Member, *, reason: str):
        """Kicks a member."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        try:
            await member.send('> Hello! Sadly, you have been **kicked** from `Ukiyo`. Goodbye 👋')
        except disnake.Forbidden:
            pass
        await member.kick(reason=f'[KICK] {ctx.author} ({ctx.author.id}): {reason}')
        await ctx.send(f'> 👌 Kicked {member.mention} for **{reason}**')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[KICK]',
            fields=[
                ('Member', f'{member.mention} (`{member.id}`)'),
                ('Reason', reason),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

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
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        usr = await Mutes.find_one({'_id': member.id})
        if usr is not None:
            return await ctx.reply(f'`{member}` is already muted.')

        time = time_and_reason.dt
        reason = time_and_reason.arg
        duration = human_timedelta(time, suffix=False)
        data = Mutes(
            id=member.id,
            muted_by=ctx.author.id,
            muted_until=time,
            reason=reason,
            duration=duration
        )
        if 913310292505686046 in (r.id for r in member.roles):  # Checks for owner
            data.is_owner = True
        elif 913315033134542889 in (r.id for r in member.roles):  # Checks for admin
            data.is_admin = True
        elif 913315033684008971 in (r.id for r in member.roles):  # Checks for mod
            data.is_mod = True
        await data.commit()

        guild = self.bot.get_guild(913310006814859334)
        muted_role = guild.get_role(913376647422545951)
        new_roles = [role for role in member.roles
                     if role.id not in (913310292505686046, 913315033134542889, 913315033684008971)
                     ] + [muted_role]
        await member.edit(roles=new_roles, reason=f'[MUTE] {ctx.author} ({ctx.author.id}): {reason}')
        try:
            await member.send(
                f'Hello, you have been muted in `Ukiyo` by **{ctx.author}** for **{reason}** '
                f'until {format_dt(time, "F")} (`{human_timedelta(time, suffix=False)}`)'
            )
        except disnake.Forbidden:
            pass
        await ctx.reply(
            f'> 👌 📨 Applied mute to {member.mention} '
            f'until {format_dt(time, "F")} (`{human_timedelta(time, suffix=False)}`)'
        )
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[MUTE]',
            fields=[
                ('Member', f'{member.mention} (`{member.id}`)'),
                ('Reason', reason),
                ('Mute Duration', f'`{duration}`'),
                ('Expires At', format_dt(time, "F")),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.command(name='unmute')
    @is_mod()
    async def unmute_cmd(self, ctx: Context, *, member: disnake.Member):
        """Unmute somebody that is currently muted."""

        data: Mutes = await Mutes.find_one({'_id': member.id})
        if data is None:
            return await ctx.reply(f'`{member}` is not muted!')
        await data.delete()

        guild = self.bot.get_guild(913310006814859334)
        muted_by = guild.get_member(data.muted_by)
        if data.filter is False:
            if ctx.author.id not in (muted_by, self.bot._owner_id):
                if muted_by.top_role > ctx.author.top_role:
                    return await ctx.reply(
                        f'{member.mention} was muted by `{muted_by}` which is in a higher role hierarcy than you. '
                        'Only staff members of the same role or above can unmute that person.'
                    )

        new_roles = [role for role in member.roles if role.id != 913376647422545951]
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
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[UNMUTE]',
            fields=[
                ('Member', f'{member.mention} (`{member.id}`)'),
                ('Mute Duration', f'`{data.duration}`'),
                ('Left', human_timedelta(data.muted_until, suffix=False)),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.command(name='checkmute', aliases=('checkmutes', 'mutescheck', 'mutecheck',))
    async def check_mute(self, ctx: Context, *, member: disnake.Member = None):
        """
        Check all the current muted members and their time left. If ``member`` is specified,
        it will only show for that member, including the reason they got muted.
        """

        if isinstance(ctx.channel, disnake.DMChannel):
            member = ctx.author

        guild = self.bot.get_guild(913310006814859334)
        if member is None:
            entries = []
            index = 0
            async for mute in Mutes.find():
                mute: Mutes
                index += 1
                key = guild.get_member(mute.id)
                if key is None:
                    key = f'[LEFT] {mute.id}'
                value = f'**Muted By:** {guild.get_member(mute.muted_by)}\n' \
                        f'**Reason:** {mute.reason}\n' \
                        f'**Mute Duration:** `{mute.duration}`' \
                        f'**Expires At:** {format_dt(mute.muted_until, "F")}\n' \
                        f'**Left:** `{human_timedelta(mute.muted_until, suffix=False)}`\n\n'
                entries.append((f'`{index}`. {key}', value))
            if len(entries) == 0:
                return await ctx.reply(f'> {ctx.disagree} There are no current mutes.')

            source = FieldPageSource(entries, per_page=5)
            source.embed.color = utils.blurple
            source.embed.title = 'Here are all the currently muted members'
            paginator = RoboPages(source, ctx=ctx, compact=True)
            await paginator.start()
        else:
            mute: Mutes = await Mutes.find_one({'_id': member.id})
            if mute is None:
                if member == ctx.author:
                    return await ctx.reply(f'> {ctx.disagree} You are not muted.')
                else:
                    return await ctx.reply(f'> {ctx.disagree} `{member}` is not muted.')
            em = disnake.Embed(colour=utils.blurple)
            em.set_author(name=member, icon_url=member.display_avatar)
            em.description = f'**Muted By:** {guild.get_member(mute.muted_by)}\n' \
                             f'**Reason:** {mute.reason}\n' \
                             f'**Mute Duration:** `{mute.duration}`' \
                             f'**Expires At:** {format_dt(mute.muted_until, "F")}\n' \
                             f'**Left:** `{human_timedelta(mute.muted_until, suffix=False)}`'
            em.set_footer(text=f'Requested By: {ctx.author}')
            await ctx.reply(embed=em)

    @mute_cmd.error
    async def mute_cmd_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.reply(f'> {ctx.disagree} {error}')
        await self.bot.reraise(ctx, error)

    @tasks.loop(seconds=15.0)
    async def check_mutes(self):
        await self.bot.wait_until_ready()
        mutes: list[Mutes] = await Mutes.find().sort('muted_until', 1).to_list(5)
        for mute in mutes:
            if datetime.utcnow() >= mute.muted_until:
                guild = self.bot.get_guild(913310006814859334)
                member = guild.get_member(mute.id)
                if member:
                    new_roles = [role for role in member.roles if role.id != 913376647422545951]
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
                await self.ensure_webhook()
                await utils.log(
                    self.webhook,
                    title='[MUTE EXPIRED]',
                    fields=[
                        ('Member', f'{member.mention} (`{member.id}`)'),
                        ('Mute Duration', f'`{mute.duration}`'),
                        ('At', format_dt(datetime.now(), 'F')),
                    ]
                )

    @commands.group(name='make', invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    @is_admin()
    async def staff_make(self, ctx: Context):
        """Shows the help for the `!make` command, used to add more staff members."""

        await ctx.send_help('make')

    @staff_make.command(name='admin')
    @is_owner()
    async def staff_make_admin(self, ctx: Context, *, member: disnake.Member):
        """Make somebody an admin."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        guild = self.bot.get_guild(913310006814859334)
        if 913315033134542889 in (r.id for r in member.roles):
            return await ctx.reply(f'> {ctx.disagree} `{member}` is already an admin!')
        admin_role = guild.get_role(913315033134542889)
        await member.edit(roles=[r for r in member.roles if r.id != 913315033684008971] + [admin_role])
        await ctx.reply(f'> 👌 Successfully made `{member}` an admin.')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[ADMIN ADDED]',
            fields=[
                ('Member', f'{member.mention} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @staff_make.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def staff_make_mod(self, ctx: Context, *, member: disnake.Member):
        """Make somebody a moderator."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        guild = self.bot.get_guild(913310006814859334)
        if 913315033684008971 in (r.id for r in member.roles):
            return await ctx.reply(f'> {ctx.disagree} `{member}` is already a moderator!')
        mod_role = guild.get_role(913315033684008971)
        await member.edit(roles=[r for r in member.roles if r.id != 913315033134542889] + [mod_role])
        await ctx.reply(f'> 👌 Successfully made `{member}` a moderator.')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[MODERATOR ADDED]',
            fields=[
                ('Member', f'{member.mention} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.group(name='remove', invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    @is_admin()
    async def staff_remove(self, ctx: Context):
        """Shows the help for the `!remove` command, used to remove a staff member from their position."""

        await ctx.send_help('remove')

    @staff_remove.command(name='admin')
    @is_owner()
    async def staff_remove_admin(self, ctx: Context, *, member: disnake.Member):
        """Remove an admin."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        if 913315033134542889 not in (r.id for r in member.roles):
            return await ctx.reply(f'> {ctx.disagree} `{member}` is not an admin!')
        await member.edit(roles=[r for r in member.roles if r.id != 913315033134542889])
        await ctx.reply(f'> 👌 Successfully removed `{member}` from being an admin.')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[ADMIN REMOVED]',
            fields=[
                ('Member', f'{member.mention} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )

    @staff_remove.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def staff_remove_mod(self, ctx: Context, *, member: disnake.Member):
        """Remove a moderator."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        if 913315033684008971 not in (r.id for r in member.roles):
            return await ctx.reply(f'> {ctx.disagree} `{member}` is not a moderator!')
        await member.edit(roles=[r for r in member.roles if r.id != 913315033684008971])
        await ctx.reply(f'> 👌 Successfully removed `{member}` from being a moderator.')
        await self.ensure_webhook()
        await utils.log(
            self.webhook,
            title='[MODERATOR REMOVED]',
            fields=[
                ('Member', f'{member.mention} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ]
        )


def setup(bot: Ukiyo):
    bot.add_cog(Moderation(bot))
