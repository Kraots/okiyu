import time
import random
from datetime import datetime, timezone

import disnake
from disnake.ext import commands
from disnake.ui import View, Button

import utils
from utils import (
    Context,
    Rules,
    AFK,
    Ticket,
    TicketView,
    Mutes,
    RoboPages,
    FieldPageSource
)

from main import Ukiyo

SERVER_AD = """
☞ Ukiyo ☜
✯ Looking for a great partner or friendship? This is the perfect server!! ✯

⇨ This server:
➢ Amazing owner, admins and mods ☺︎
➢ Exclusive bot ☻︎
➢ Roles and intros ☺︎
➢ Possible relationships ☻︎
➢ An active and fun server ☺︎
➢ Exclusive emotes ☻︎
➢ And over all an inclusive server for everyone ☺︎


☀︎ Link: https://discord.gg/fQ6Nb4ac9x ☀︎
"""


class ViewIntro(disnake.ui.View):
    def __init__(self, bot: Ukiyo, uid: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.uid = uid

    async def on_error(self, error, item, inter):
        await self.bot.inter_reraise(self.bot, inter, item, error)

    @disnake.ui.button(label='View Intro', style=disnake.ButtonStyle.blurple)
    async def view_intro(self, button: disnake.Button, inter: disnake.MessageInteraction):
        disagree = '<:disagree:913895999125196860>'
        data: utils.Intro = await utils.Intro.find_one({'_id': self.uid})
        guild = self.bot.get_guild(913310006814859334)
        member = guild.get_member(self.uid)
        if data is None:
            return await inter.response.send_message(
                f'> {disagree} `{member}` doesn\'t have an intro. '
                'Please contact a staff member to unverify them! This is a bug.',
                ephemeral=True
            )
        intro_channel = guild.get_channel(913331578606854184)
        msg = await intro_channel.fetch_message(data.message_id)
        if msg:
            view = disnake.ui.View()
            view.add_item(disnake.ui.Button(label='Jump!', url=msg.jump_url))
        else:
            view = None

        em = disnake.Embed(colour=member.color)
        em.set_author(name=member, icon_url=member.display_avatar)
        em.set_thumbnail(url=member.display_avatar)
        em.add_field(name='Name', value=data.name)
        em.add_field(name='Age', value=data.age)
        em.add_field(name='Gender', value=data.gender)
        em.add_field(name='Location', value=data.location, inline=False)
        em.add_field(name='DMs', value=data.dms)
        em.add_field(name='Looking', value=data.looking)
        em.add_field(name='Sexuality', value=data.sexuality)
        em.add_field(name='Relationship Status', value=data.status)
        em.add_field(name='Likes', value=data.likes)
        em.add_field(name='Dislikes', value=data.dislikes)
        await inter.response.send_message(embed=em, view=view, ephemeral=True)


class Misc(commands.Cog):
    """Miscellaneous commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '🔧'

    @commands.command()
    async def ping(self, ctx: Context):
        """See the bot's ping."""

        ping = disnake.Embed(title="Pong!", description="_Pinging..._", color=utils.blurple)
        start = time.time() * 1000
        msg = await ctx.send(embed=ping)
        end = time.time() * 1000
        ping = disnake.Embed(
            title="Pong!",
            description=f"Websocket Latency: `{(round(self.bot.latency * 1000, 2))}ms`"
            f"\nBot Latency: `{int(round(end-start, 0))}ms`"
            f"\nResponse Time: `{(msg.created_at - ctx.message.created_at).total_seconds()/1000}` ms",
            color=utils.blurple
        )
        ping.set_footer(text=f"Online for {utils.human_timedelta(dt=self.bot.uptime, suffix=False)}")
        await msg.edit(embed=ping)

    @commands.command()
    async def uptime(self, ctx: Context):
        """See how long the bot has been online for."""

        uptime = disnake.Embed(
            description=f"Bot has been online since {utils.format_dt(self.bot.uptime, 'F')} "
                        f"(`{utils.human_timedelta(dt=self.bot.uptime, suffix=False)}`)",
            color=utils.blurple
        )
        uptime.set_footer(text=f'Bot made by: {self.bot._owner}')
        await ctx.send(embed=uptime)

    @commands.command(name='invite', aliases=('inv',))
    async def _invite(self, ctx: Context):
        """Sends an invite that never expires."""

        await ctx.send('https://discord.gg/fQ6Nb4ac9x')

    @commands.command(aliases=('ad',))
    async def serverad(self, ctx: Context):
        """See the server's ad."""

        await ctx.message.delete()
        ad = disnake.Embed(color=utils.blurple, title='Here\'s the ad to the server:', description=SERVER_AD)
        ad.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.display_avatar)

        await ctx.send(embed=ad, reference=ctx.replied_reference)

    @commands.group(
        name='rules', invoke_without_command=True, case_insensitive=True, aliases=('rule',)
    )
    async def server_rules(self, ctx: Context, rule: int = None):
        """Sends the server's rules. If ``rule`` is given, it will only send that rule."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'> {ctx.disagree} There are currently no rules set. Please contact an admin about this!')
        em = disnake.Embed(title='Rules', color=utils.blurple)

        if rule is None:
            for index, rule in enumerate(rules.rules):
                if em.description == disnake.embeds.EmptyEmbed:
                    em.description = f'`{index + 1}.` {rule}'
                else:
                    em.description += f'\n\n`{index + 1}.` {rule}'
        else:
            if rule <= 0:
                return await ctx.reply(f'> {ctx.disagree} Rule cannot be equal or less than `0`')
            try:
                _rule = rules.rules[rule - 1]
                em.description = f'`{rule}.` {_rule}'
            except IndexError:
                return await ctx.reply(f'> {ctx.disagree} Rule does not exist!')

        await ctx.send(embed=em, reference=ctx.replied_reference)

    @server_rules.command(name='add')
    @utils.is_admin()
    async def server_rules_add(self, ctx: Context, *, rule: str):
        """Adds a rule to the server's rules."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            await Rules(
                id=self.bot._owner_id,
                rules=[rule]
            ).commit()
        else:
            rules.rules += [rule]
            await rules.commit()

        await ctx.reply(f'> 👌 📝 `{rule}` successfully **added** to the rules.')

    @server_rules.command(name='remove', aliases=('delete',))
    @utils.is_admin()
    async def server_rules_remove(self, ctx: Context, rule: int):
        """Removes a rule from the server's rules by its number."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'> {ctx.disagree} There are currently no rules set.')
        else:
            if rule <= 0:
                return await ctx.reply(f'> {ctx.disagree} Rule cannot be equal or less than `0`')
            try:
                rules.rules.pop(rule - 1)
            except IndexError:
                return await ctx.reply(f'> {ctx.disagree} Rule does not exist!')
            await rules.commit()

        await ctx.reply(f'> 👌 Successfully **removed** rule `{rule}`.')

    @server_rules.command(name='clear')
    @utils.is_owner()
    async def server_rules_clear(self, ctx: Context):
        """Deletes all the rules."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'> {ctx.disagree} There are currently no rules set.')
        else:
            await rules.delete()

        await ctx.reply('> 👌 Successfully **cleared** the rules.')

    @commands.group(
        name='nick', invoke_without_command=True, case_insensitive=True, aliases=('nickname',)
    )
    async def change_nick(self, ctx: Context, *, new_nickname: str):
        """Change your nickname to your desired one."""

        res = await utils.check_username(self.bot, word=new_nickname)
        if res is True:
            return await ctx.reply(f'> {ctx.disagree} That nickname is not pingable, is a bad word or is too short!')
        await ctx.author.edit(nick=new_nickname)
        await ctx.reply(f'I have changed your nickname to `{new_nickname}`')

    @change_nick.command(name='reset', aliases=('remove',))
    async def remove_nick(self, ctx: Context):
        """Removes your nickname."""

        res = await utils.check_username(self.bot, word=ctx.author.display_name)
        if res is True:
            return await ctx.reply(
                f'> {ctx.disagree} Cannot remove your nickname because your username '
                'is unpingable, is a bad word or is too short.'
            )
        await ctx.author.edit(nick=None)
        await ctx.reply('I have removed your nickname.')

    @commands.command(name='avatar', aliases=('av',))
    async def _av(self, ctx: Context, *, member: disnake.Member = None):
        """Check the avatar ``member`` has."""

        member = member or ctx.author
        em = disnake.Embed(colour=utils.blurple, title=f'`{member.display_name}`\'s avatar')
        em.set_image(url=member.display_avatar)
        em.set_footer(text=f'Requested By: {ctx.author}')
        await ctx.send(embed=em, reference=ctx.replied_reference)

    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def created(self, ctx: Context, *, user: disnake.User = None):
        """Check the date when the ``user`` created their account."""

        user = user or ctx.author
        em = disnake.Embed(
            colour=utils.blurple,
            title='Creation Date',
            description=f'{user.mention} created their account '
                        f'on {utils.format_dt(user.created_at, "F")} '
                        f'(`{utils.human_timedelta(user.created_at)}`)'
        )
        await ctx.send(embed=em, reference=ctx.replied_reference)

    @created.command()
    async def server(self, ctx: Context):
        """
        See the date when the server got created at
        and when it was made public.
        """

        guild = self.bot.get_guild(913310006814859334)
        created_date = guild.created_at
        publiced_date = guild.get_member(302050872383242240).joined_at
        em = disnake.Embed(colour=utils.red, title='Server Creation')
        em.add_field(
            name='Created At',
            value=f'{utils.format_dt(created_date, "F")} '
                  f'(`{utils.human_timedelta(created_date)}`)',
            inline=False
        )
        em.add_field(
            name='Publiced At',
            value=f'{utils.format_dt(publiced_date, "F")} '
                  f'(`{utils.human_timedelta(publiced_date)}`)',
            inline=False
        )
        await ctx.send(embed=em, reference=ctx.replied_reference)

    @commands.command()
    async def joined(self, ctx: Context, *, member: disnake.Member = None):
        """Check the date when the ``member`` joined the server."""

        member = member or ctx.author
        em = disnake.Embed(
            colour=utils.blurple,
            title='Join Date',
            description=f'{member.mention} joined the server '
                        f'on {utils.format_dt(member.joined_at, "F")} '
                        f'(`{utils.human_timedelta(member.joined_at)}`)'
        )
        await ctx.send(embed=em, reference=ctx.replied_reference)

    @commands.command(name='ticket')
    @commands.cooldown(1, 60.0, commands.BucketType.member)
    async def ticket_cmd(self, ctx: Context):
        """Create a ticket."""

        total_tickets = await utils.Ticket.find({'user_id': ctx.author.id}).sort('ticket_id', -1).to_list(5)
        if len(total_tickets) == 5:
            return await ctx.reply('You already have a max of `5` tickets created!')
        ticket_id = '1' if not total_tickets else str(int(total_tickets[0].ticket_id) + 1)
        ch_name = f'{ctx.author.name}-ticket #' + ticket_id

        g = self.bot.get_guild(913310006814859334)
        categ = g.get_channel(914082225274912808)
        channel = await g.create_text_channel(
            ch_name,
            category=categ,
            reason=f'Ticket Creation by {ctx.author} (ID: {ctx.author.id})'
        )
        em = disnake.Embed(
            title=f'Ticket #{ticket_id}',
            description='Hello, thanks for creating a ticket. '
                        'Please write out what made you feel like you needed to create a ticket '
                        'and be patient until one of our staff members is available '
                        'to help.'
        )
        m = await channel.send(
            ctx.author.mention,
            embed=em,
            view=TicketView()
        )

        ticket = Ticket(
            channel_id=channel.id,
            message_id=m.id,
            owner_id=ctx.author.id,
            ticket_id=ticket_id,
            created_at=datetime.utcnow()
        )
        await ticket.commit()

        await m.pin()
        await channel.purge(limit=1)
        await channel.set_permissions(ctx.author, read_messages=True)

        v = View()
        v.add_item(Button(label='Jump!', url=m.jump_url))
        await ctx.reply('Ticket created!', view=v)
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[TICKET OPENED]',
            fields=[
                ('Ticket Owner', f'{ctx.author} (`{ctx.author.id}`)'),
                ('Ticket ID', f'`#{ticket_id}`'),
                ('At', utils.format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        async for ticket in Ticket.find({'owner_id': member.id}):
            guild = self.bot.get_guild(913310006814859334)
            ch = guild.get_channel(ticket.id)
            await ch.delete(reason='Member left.')
            await ticket.delete()

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
                        f'**Mute Duration:** `{mute.duration}`\n' \
                        f'**Expires At:** {utils.format_dt(mute.muted_until, "F")}\n' \
                        f'**Remaining:** `{utils.human_timedelta(mute.muted_until, suffix=False)}`\n\n'
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
                             f'**Mute Duration:** `{mute.duration}`\n' \
                             f'**Expires At:** {utils.format_dt(mute.muted_until, "F")}\n' \
                             f'**Remaining:** `{utils.human_timedelta(mute.muted_until, suffix=False)}`'
            em.set_footer(text=f'Requested By: {ctx.author}')
            await ctx.reply(embed=em)

    @commands.command(name='match')
    async def match_people(self, ctx: Context):
        """
        Matches you with another person, based on the sexuality, gender, relationship status
        of what the both of you have in your intros and if they are looking.
        """

        guild = self.bot.get_guild(913310006814859334)
        _ = await utils.Marriage.find_one({'_id': ctx.author.id})
        if _ is not None:
            mem = guild.get_member(_.married_to)
            return await ctx.reply(f'You are already married to {mem.mention}')

        choices = []
        em = disnake.Embed(title='Matching... Please wait...', color=utils.blurple)
        msg = await ctx.reply(embed=em)
        data: utils.Intro = await utils.Intro.find_one({'_id': ctx.author.id})
        if data is None:
            await msg.delete()
            if ctx.author.id == self.bot._owner_id:
                return await ctx.reply('Master, you forgot that you didn\'t make an intro? 🥺 🥺')
            else:
                return await ctx.reply(
                    f'> {ctx.disagree} Couldn\'t find a match because you don\'t have an intro. '
                    'Please contact a staff member to unverify you! This is a bug.'
                )
        elif data.status.lower() == 'taken':
            return await ctx.reply('You\'re already taken!')
        _sexuality = None
        _gender = None
        if data.gender.lower() in ('male', 'm', 'boy'):
            if data.sexuality.lower() == 'straight':
                _sexuality = ('straight', 'bisexual', 'bi', 'Straight', 'Bisexual', 'Bi')
                _gender = ('female', 'Female', 'girl', 'Girl', 'F', 'f')
            elif data.sexuality.lower() == 'gay':
                _sexuality = ('gay', 'bisexual', 'bi', 'Gay', 'Bisexual', 'Bi')
                _gender = ('male', 'Male', 'boy', 'Boy', 'M', 'm')
            elif data.sexuality.lower() in ('bi', 'bisexual', 'pans', 'pansexual', 'omni', 'omnisexual'):
                _gender = ('male', 'Male', 'boy', 'Boy', 'M', 'm', 'female', 'Female', 'girl', 'Girl', 'F', 'f')

        elif data.gender.lower() in ('female', 'f', 'girl'):
            if data.sexuality.lower() == 'straight':
                _sexuality = ('straight', 'bisexual', 'bi', 'Straight', 'Bisexual', 'Bi')
                _gender = ('male', 'Male', 'boy', 'Boy', 'M', 'm')
            elif data.sexuality.lower() == 'lesbian':
                _sexuality = ('lesbian', 'bisexual', 'bi', 'Lesbian', 'Bisexual', 'Bi')
                _gender = ('female', 'Female', 'girl', 'Girl', 'F', 'f')
            elif data.sexuality.lower() in ('bi', 'bisexual', 'pans', 'pansexual', 'omni', 'omnisexual'):
                _gender = ('male', 'Male', 'boy', 'Boy', 'M', 'm', 'female', 'Female', 'girl', 'Girl', 'F', 'f')

        if _gender is not None:
            for gender in _gender:
                if _sexuality is not None:
                    for sexuality in _sexuality:
                        async for mem in utils.Intro.find({'gender': gender, 'sexuality': sexuality}):
                            if (
                                (mem.status.lower() != 'taken') and
                                (mem.id != ctx.author.id) and
                                (mem.looking.lower() == 'yes')
                            ):
                                if data.age == 14 and mem.age < 17:
                                    choices.append(guild.get_member(mem.id))
                                elif data.age == 15 and mem.age < 18:
                                    choices.append(guild.get_member(mem.id))
                                elif data.age == 16 and mem.age < 19:
                                    choices.append(guild.get_member(mem.id))
                                elif data.age == 17 and mem.age > 14:
                                    choices.append(guild.get_member(mem.id))
                                elif data.age == 18 and mem.age > 15:
                                    choices.append(guild.get_member(mem.id))
                                elif data.age == 19 and mem.age > 16:
                                    choices.append(guild.get_member(mem.id))

                else:
                    async for mem in utils.Intro.find({'gender': gender}):
                        if (
                            (mem.status.lower() != 'taken') and
                            (mem.id != ctx.author.id) and
                            (mem.looking.lower() == 'yes')
                        ):
                            if data.age == 14 and mem.age < 17:
                                choices.append(guild.get_member(mem.id))
                            elif data.age == 15 and mem.age < 18:
                                choices.append(guild.get_member(mem.id))
                            elif data.age == 16 and mem.age < 19:
                                choices.append(guild.get_member(mem.id))
                            elif data.age == 17 and mem.age > 14:
                                choices.append(guild.get_member(mem.id))
                            elif data.age == 18 and mem.age > 15:
                                choices.append(guild.get_member(mem.id))
                            elif data.age == 19 and mem.age > 16:
                                choices.append(guild.get_member(mem.id))
        else:
            async for mem in utils.Intro.find():
                if (
                    (mem.status.lower() != 'taken') and
                    (mem.id != ctx.author.id) and
                    (mem.looking.lower() == 'yes')
                ):
                    if data.age == 14 and mem.age < 17:
                        choices.append(guild.get_member(mem.id))
                    elif data.age == 15 and mem.age < 18:
                        choices.append(guild.get_member(mem.id))
                    elif data.age == 16 and mem.age < 19:
                        choices.append(guild.get_member(mem.id))
                    elif data.age == 17 and mem.age > 14:
                        choices.append(guild.get_member(mem.id))
                    elif data.age == 18 and mem.age > 15:
                        choices.append(guild.get_member(mem.id))
                    elif data.age == 19 and mem.age > 16:
                        choices.append(guild.get_member(mem.id))

        if len(choices) == 0:
            em.title = 'Uh oh...'
            em.description = 'Sadly, I couldn\'t find a match for you.'
            em.color = utils.red
            return await msg.edit(embed=em)

        match = random.choice(choices)
        em.title = 'Match Found!'
        em.description = f'You matched with {match.mention}'
        em.color = utils.green
        em.timestamp = datetime.now(timezone.utc)
        em.set_footer(text='Keep in mind that this is just a suggestion! Nothing more!!')
        await msg.edit(embed=em, view=ViewIntro(self.bot, match.id))

    @commands.command(name='staff', aliases=('mods',))
    async def check_staff(self, ctx):
        """Check the staff members current status."""

        guild = self.bot.get_guild(913310006814859334)
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "<:status_online:916642281631670273>"},
            "idle": {"users": [], "emoji": "<:status_idle:916642281665212437>"},
            "dnd": {"users": [], "emoji": "<:status_dnd:916642281665220699>"},
            "offline": {"users": [], "emoji": "<:status_offline:916642281593913354>"}
        }

        for mem in guild.members:
            if 913310292505686046 in (r.id for r in mem.roles):  # Checks for owner
                if not mem.bot:
                    if len(all_status[str(mem.status)]['users']) == 0:
                        all_status[str(mem.status)]["users"].append(f"**{mem}** `(OWNER)`")
                    else:
                        all_status[str(mem.status)]["users"].append(f"<:blank:916776676250234911> **{mem}** `(OWNER)`")
            elif 913315033134542889 in (r.id for r in mem.roles):  # Checks for admin
                if not mem.bot:
                    if len(all_status[str(mem.status)]['users']) == 0:
                        all_status[str(mem.status)]["users"].append(f"**{mem}** `(ADMIN)`")
                    else:
                        all_status[str(mem.status)]["users"].append(f"<:blank:916776676250234911> **{mem}** `(ADMIN)`")
            elif 913315033684008971 in (r.id for r in mem.roles):  # Checks for mod
                if not mem.bot:
                    if len(all_status[str(mem.status)]['users']) == 0:
                        all_status[str(mem.status)]["users"].append(f"**{mem}** `(MODERATOR)`")
                    else:
                        all_status[str(mem.status)]["users"].append(f"<:blank:916776676250234911> **{mem}** `(MODERATOR)`")

        for entry in all_status:
            if all_status[entry]["users"]:
                usrs = '\n'.join(all_status[entry]['users'])
                message += f"{all_status[entry]['emoji']} {usrs}\n\n"

        await ctx.send(message)

    @commands.command(name='afk')
    async def _afk(self, ctx: Context, *, reason: str):
        """Set yourself on ``AFK``. While being ``AFK``, anybody
        who pings you will be told by the bot that you are ``AFK``
        with the reason you provided.
        """

        data: AFK = await AFK.find_one({'_id': ctx.author.id})
        if data is not None:
            return await ctx.reply('You are already ``AFK``!')

        await AFK(
            id=ctx.author.id,
            reason=reason,
            date=datetime.now(timezone.utc)
        ).commit()
        await ctx.reply(f'You are now ``AFK``: **"{reason}"**')

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        data: AFK = await AFK.find_one({'_id': message.author.id})
        if data is not None:
            await data.delete()
            return await message.reply(
                'Welcome back! Removed your ``AFK``\nYou have been ``AFK`` '
                f'since {utils.format_dt(data.date, "F")} '
                f'(`{utils.human_timedelta(dt=data.date)}`)'
            )

        for user in message.mentions:
            data: AFK = await AFK.find_one({'_id': user.id})
            if data is not None:
                await message.reply(
                    f'**{user}** is ``AFK``: **"{data.reason}"** '
                    f'*since {utils.format_dt(data.date, "F")} '
                    f'(`{utils.human_timedelta(dt=data.date)}`)*')


def setup(bot: Ukiyo):
    bot.add_cog(Misc(bot))
