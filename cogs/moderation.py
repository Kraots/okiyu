import asyncio
from datetime import datetime, timezone

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
            913332431417925634, 913332511789178951, 913425733567799346, 913445987102654474,
            914257049456607272, 913329436953296917
        )

        self.check_mutes.start()

    def jump_view(self, url: str) -> disnake.ui.View:
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label='Jump!', url=url))
        return view

    @property
    def display_emoji(self) -> str:
        return '🛠️'

    @commands.command()
    @is_admin()
    async def announce(self, ctx: Context):
        """Make an announcement in <#913331371282423808>"""

        view = AnnouncementView(self.bot, ctx.author)
        view.message = await ctx.send(embed=view.prepare_embed(), view=view)

    @commands.command(name='purge', aliases=('clear',))
    @is_mod()
    async def chat_purge(self, ctx: Context, amount: int):
        """Clear the ``amount`` of messages from the chat.

        `amount` **->** The amount of messages to delete from the current channel.
        """

        await ctx.message.delete()
        purged = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f'> {ctx.agree} Deleted `{len(purged):,}` messages')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHAT PURGE]',
            fields=[
                ('Channel', ctx.channel.mention),
                ('Amount', f'`{utils.plural(len(purged)):message}`'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
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

        `channel` **->** The channel to lock. If you want to lock the current channel you use the command, you can ignore this since it defaults to the current channel.
        """  # noqa

        channel = channel or ctx.channel

        role = channel.guild.default_role
        if channel.id not in self.ignored_channels:
            overwrites = channel.overwrites_for(role)
            overwrites.send_messages = False
            await channel.set_permissions(
                role,
                overwrite=overwrites,
                reason=f'Channel locked by {ctx.author} ({ctx.author.id})'
            )
        else:
            return await ctx.reply(f'> {ctx.disagree} That channel cannot be unlocked.')
        await ctx.reply('> 🔒 Channel Locked!')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHANNEL LOCK]',
            fields=[
                ('Channel', channel.mention),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
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
                        reason=f'Channel locked by {ctx.author} ({ctx.author.id})'
                    )
                    _channels.append(channel.mention)
        await ctx.reply('> 🔒 All the unlocked channels have been locked!')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHANNEL LOCK]',
            fields=[
                ('Channel', ' '.join(_channels)),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @commands.group(name='unlock', invoke_without_command=True, case_insensitive=True)
    @is_mod()
    async def unlock_channel(self, ctx: Context, channel: disnake.TextChannel = None):
        """
        Unlocks the channel.

        `channel` **->** The channel to unlock. If you want to unlock the current channel you use the command, you can ignore this since it defaults to the current channel.
        """  # noqa

        channel = channel or ctx.channel

        role = channel.guild.default_role
        if channel.id not in self.ignored_channels:
            overwrites = channel.overwrites_for(role)
            overwrites.send_messages = None
            await channel.set_permissions(
                role,
                overwrite=overwrites,
                reason=f'Channel unlocked by {ctx.author} ({ctx.author.id})'
            )
        else:
            return await ctx.reply(f'> {ctx.disagree} That channel cannot be unlocked.')
        await ctx.reply('> 🔓 Channel Unlocked!')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHANNEL UNLOCK]',
            fields=[
                ('Channel', channel.mention),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
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
                        reason=f'Channel unlocked by {ctx.author} ({ctx.author.id})'
                    )
                    _channels.append(channel.mention)
        await ctx.reply('> 🔓 All locked channels have been unlocked!')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CHANNEL UNLOCK]',
            fields=[
                ('Channel', ' '.join(_channels)),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @commands.command(name='ban')
    @is_admin()
    async def _ban(self, ctx: Context, member: disnake.User, *, reason: str):
        """Bans an user.

        `member` **->** The member to ban. If the member is not in the server you must provide their discord id.
        `reason` **->** The reason you're banning the member.
        """

        if isinstance(member, disnake.Member):
            if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
                return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        try:
            await member.send(f'> ⚠️ Hello! Sadly, you have been **banned** from `Ukiyo` for **{reason}**. Goodbye 👋')
        except disnake.Forbidden:
            pass
        guild = self.bot.get_guild(913310006814859334)
        await guild.ban(
            member,
            reason=f'{ctx.author} ({ctx.author.id}): "{reason}"',
            delete_message_days=0
        )
        await ctx.send(f'> 👌 🔨 Banned `{member}` for **{reason}**')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[BAN]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('Reason', reason),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @commands.command(name='unban')
    @is_admin()
    async def _unban(self, ctx: Context, *, user: disnake.User):
        """Unbans an user.

        `user` **->** The user to unban. Must be their discord id.
        """

        guild = self.bot.get_guild(913310006814859334)
        try:
            await guild.unban(user, reason=f'Unban by {ctx.author} ({ctx.author.id})')
        except disnake.NotFound:
            return await ctx.reply(f'> {ctx.disagree} The user is not banned.')
        else:
            await ctx.reply(f'> 👌 Successfully unbanned `{user}`')
            await utils.log(
                self.bot.webhooks['mod_logs'],
                title='[UNBAN]',
                fields=[
                    ('Member', f'{user.mention} (`{user.id}`)'),
                    ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                    ('At', format_dt(datetime.now(), 'F')),
                ],
                view=self.jump_view(ctx.message.jump_url)
            )

    @commands.command(name='kick')
    @is_mod()
    async def _kick(self, ctx: Context, member: disnake.Member, *, reason: str):
        """Kicks a member.

        `member` **->** The member to kick.
        `reason` **->** The reason you're kicking the member.
        """

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        try:
            await member.send(f'> ⚠️ Hello! Sadly, you have been **kicked** from `Ukiyo` for **{reason}**. Goodbye 👋')
        except disnake.Forbidden:
            pass
        await member.kick(reason=f'{ctx.author} ({ctx.author.id}): "{reason}"')
        await ctx.send(f'> 👌 Kicked `{member}` for **{reason}**')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[KICK]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('Reason', reason),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
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

        `member` **->** The member you want to mute.
        `time_and_reason` **->** The time and the reason why you're muting the member.

        **Example:**
        `!mute @carrot 2m coolest person alive`
        `!mute @carrot 1 Jan coolest person alive` (will mute them until 1 January, next year, or this one, depending whether this date has passed. You can also directly specify the year.)
        """  # noqa

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(
                f'> {ctx.disagree} That member is above or equal to you. '
                'Cannot do that.'
            )
        elif member.id == self.bot._owner_id and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(
                f'> {ctx.disagree} That member is above or equal to you. '
                'Cannot do that. (above in this case you bottom sub <:kek:913339277939720204>)'
            )

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
            duration=duration,
        )
        if 913310292505686046 in (r.id for r in member.roles):  # Checks for owner
            data.is_owner = True
        elif 913315033134542889 in (r.id for r in member.roles):  # Checks for admin
            data.is_admin = True
        elif 913315033684008971 in (r.id for r in member.roles):  # Checks for mod
            data.is_mod = True

        guild = self.bot.get_guild(913310006814859334)
        muted_role = guild.get_role(913376647422545951)
        new_roles = [role for role in member.roles
                     if role.id not in (913310292505686046, 913315033134542889, 913315033684008971)
                     ] + [muted_role]
        await member.edit(roles=new_roles, reason=f'[MUTE] {ctx.author} ({ctx.author.id}): "{reason}"')
        try:
            em = disnake.Embed(title='You have been muted!', color=utils.red)
            em.description = f'**Muted By:** {ctx.author}\n' \
                             f'**Reason:** {reason}\n' \
                             f'**Mute Duration:** `{human_timedelta(time, suffix=False)}`\n' \
                             f'**Expire Date:** {format_dt(time, "F")}'
            em.set_footer(text='Muted in `Ukiyo`')
            em.timestamp = datetime.now(timezone.utc)
            await member.send(embed=em)
        except disnake.Forbidden:
            pass
        _msg = await ctx.reply(
            f'> 👌 📨 Applied mute to {member.mention} '
            f'until {format_dt(time, "F")} (`{human_timedelta(time, suffix=False)}`)'
        )
        data.jump_url = _msg.jump_url
        await data.commit()
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[MUTE]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('Reason', reason),
                ('Mute Duration', f'`{duration}`'),
                ('Expires At', format_dt(time, "F")),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(_msg.jump_url)
        )

    @commands.command(name='unmute')
    @is_mod()
    async def unmute_cmd(self, ctx: Context, *, member: disnake.Member):
        """Unmute somebody that is currently muted.

        `member` **->** The member you want to unmute. If the member was muted by carrot then you can't do shit about it <:lipbite:914193306416742411> <:kek:913339277939720204>
        """  # noqa

        data: Mutes = await Mutes.find_one({'_id': member.id})
        if data is None:
            return await ctx.reply(f'`{member}` is not muted!')

        guild = self.bot.get_guild(913310006814859334)
        muted_by = guild.get_member(data.muted_by)
        if data.filter is False:
            if ctx.author.id not in (data.muted_by, self.bot._owner_id):
                if data.muted_by == self.bot._owner_id:
                    return await ctx.reply(
                        f'{member.mention} was muted by `{muted_by}` which is in a higher role hierarcy than you. '
                        'Only staff members of the same role or above can unmute that person.'
                    )

        await data.delete()
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
            await member.send(f'Hello, you have been **unmuted** in `Ukiyo` by **{ctx.author}**')
        except disnake.Forbidden:
            pass

        await ctx.reply(f'> 👌 Successfully unmuted {member.mention}')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[UNMUTE]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('Mute Duration', f'`{data.duration}`'),
                ('Left', f'`{human_timedelta(data.muted_until, suffix=False)}`'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @mute_cmd.error
    async def mute_cmd_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.reply(f'> {ctx.disagree} {error}')
        await self.bot.reraise(ctx, error)

    @tasks.loop(seconds=15.0)
    async def check_mutes(self):
        mutes: list[Mutes] = await Mutes.find().sort('muted_until', 1).to_list(5)
        for mute in mutes:
            if datetime.utcnow() >= mute.muted_until:
                guild = self.bot.get_guild(913310006814859334)
                member = guild.get_member(mute.id)
                _mem = f'**[LEFT]** (`{mute.id}`)'
                if member:
                    _mem = f'{member} (`{member.id}`)'
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
                mem = guild.get_member(mute.muted_by)
                await utils.log(
                    self.bot.webhooks['mod_logs'],
                    title='[MUTE EXPIRED]',
                    fields=[
                        ('Member', _mem),
                        ('Reason', mute.reason),
                        ('Mute Duration', f'`{mute.duration}`'),
                        ('By', mem.mention),
                        ('At', format_dt(datetime.now(), 'F')),
                    ],
                    view=self.jump_view(mute.jump_url)
                )

    @check_mutes.before_loop
    async def wait_until_ready(self):
        await self.bot.wait_until_ready()

    @commands.group(name='make', invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    @is_admin()
    async def staff_make(self, ctx: Context):
        """Shows the help for the `!make` command, used to add more staff members."""

        await ctx.send_help('make')

    @staff_make.command(name='admin')
    @is_owner()
    async def staff_make_admin(self, ctx: Context, *, member: disnake.Member):
        """Make somebody an admin.

        `member` **->** The member you want to make an admin.
        """

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        guild = self.bot.get_guild(913310006814859334)
        if 913315033134542889 in (r.id for r in member.roles):
            return await ctx.reply(f'> {ctx.disagree} `{member}` is already an admin!')
        admin_role = guild.get_role(913315033134542889)
        await member.edit(roles=[r for r in member.roles if r.id != 913315033684008971] + [admin_role])
        await ctx.reply(f'> 👌 Successfully made `{member}` an admin.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[ADMIN ADDED]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_make.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def staff_make_mod(self, ctx: Context, *, member: disnake.Member):
        """Make somebody a moderator.

        `member` **->** The member you want to make a moderator.
        """

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        guild = self.bot.get_guild(913310006814859334)
        if 913315033684008971 in (r.id for r in member.roles):
            return await ctx.reply(f'> {ctx.disagree} `{member}` is already a moderator!')
        mod_role = guild.get_role(913315033684008971)
        await member.edit(roles=[r for r in member.roles if r.id != 913315033134542889] + [mod_role])
        await ctx.reply(f'> 👌 Successfully made `{member}` a moderator.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[MODERATOR ADDED]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @commands.group(name='remove', invoke_without_command=True, case_insensitive=True, ignore_extra=False)
    @is_admin()
    async def staff_remove(self, ctx: Context):
        """Shows the help for the `!remove` command, used to remove a staff member from their position."""

        await ctx.send_help('remove')

    @staff_remove.command(name='admin')
    @is_owner()
    async def staff_remove_admin(self, ctx: Context, *, member: disnake.Member):
        """Remove an admin.

        `member` **->** The member you want to remove admin from.
        """

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        if 913315033134542889 not in (r.id for r in member.roles):
            return await ctx.reply(f'> {ctx.disagree} `{member}` is not an admin!')
        await member.edit(roles=[r for r in member.roles if r.id != 913315033134542889])
        await ctx.reply(f'> 👌 Successfully removed `{member}` from being an admin.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[ADMIN REMOVED]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )

    @staff_remove.command(name='moderator', aliases=('mod',))
    @is_admin()
    async def staff_remove_mod(self, ctx: Context, *, member: disnake.Member):
        """Remove a moderator.

        `member` **->** The member you want to remove the moderator from.
        """

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'> {ctx.disagree} That member is above or equal to you. Cannot do that.')

        if 913315033684008971 not in (r.id for r in member.roles):
            return await ctx.reply(f'> {ctx.disagree} `{member}` is not a moderator!')
        await member.edit(roles=[r for r in member.roles if r.id != 913315033684008971])
        await ctx.reply(f'> 👌 Successfully removed `{member}` from being a moderator.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[MODERATOR REMOVED]',
            fields=[
                ('Member', f'{member} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', format_dt(datetime.now(), 'F')),
            ],
            view=self.jump_view(ctx.message.jump_url)
        )


def setup(bot: Ukiyo):
    bot.add_cog(Moderation(bot))
