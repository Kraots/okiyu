import time
import random
import wikipedia
from datetime import datetime, timezone

import disnake
from disnake.ext import commands

import utils
from utils import (
    Context,
    Rules,
    AFK,
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
        """See the bot's ping.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await utils.check_channel(ctx) is False:
            return

        ping = disnake.Embed(title="Pong!", description="_Pinging..._", color=utils.blurple)
        start = time.time() * 1000
        msg = await ctx.better_reply(embed=ping)
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
        """See how long the bot has been online for.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await utils.check_channel(ctx) is False:
            return

        uptime = disnake.Embed(
            description=f"Bot has been online since {utils.format_dt(self.bot.uptime, 'F')} "
                        f"(`{utils.human_timedelta(dt=self.bot.uptime, suffix=False)}`)",
            color=utils.blurple
        )
        uptime.set_footer(text=f'Bot made by: {self.bot._owner}')
        await ctx.better_reply(embed=uptime)

    @commands.command(name='invite', aliases=('inv',))
    async def _invite(self, ctx: Context):
        """Sends an invite that never expires.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await utils.check_channel(ctx) is False:
            return

        await ctx.better_reply('https://discord.gg/fQ6Nb4ac9x')

    @commands.command(aliases=('ad',))
    async def serverad(self, ctx: Context):
        """See the server's ad.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await utils.check_channel(ctx) is False:
            return

        await ctx.message.delete()
        ad = disnake.Embed(color=utils.blurple, title='Here\'s the ad to the server:', description=SERVER_AD)
        ad.set_footer(text=f'Requested by: {ctx.author}')

        await ctx.better_reply(embed=ad)

    @commands.group(
        name='rules', invoke_without_command=True, case_insensitive=True, aliases=('rule',)
    )
    async def server_rules(self, ctx: Context, rule: int = None):
        """Sends the server's rules. If ``rule`` is given, it will only send that rule.

        `rule` **->** The number of the rule you wish to see.
        """

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'{ctx.denial} There are currently no rules set. Please contact an admin about this!')
        em = disnake.Embed(title='Rules', color=utils.blurple)

        if rule is None:
            for index, rule in enumerate(rules.rules):
                if em.description == disnake.embeds.EmptyEmbed:
                    em.description = f'`{index + 1}.` {rule}'
                else:
                    em.description += f'\n\n`{index + 1}.` {rule}'
        else:
            if rule <= 0:
                return await ctx.reply(f'{ctx.denial} Rule cannot be equal or less than `0`')
            try:
                _rule = rules.rules[rule - 1]
                em.description = f'`{rule}.` {_rule}'
            except IndexError:
                return await ctx.reply(f'{ctx.denial} Rule does not exist!')
        em.set_footer(text='NOTE: Breaking any of these rules will result in a mute, or in the worst case, a ban.')

        await ctx.better_reply(embed=em)

    @server_rules.command(name='add')
    @utils.is_admin()
    async def server_rules_add(self, ctx: Context, *, rule: str):
        """Adds a rule to the server's rules.

        `rule` **->** The rule to add.
        """

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

    @server_rules.command(name='edit')
    @utils.is_admin()
    async def server_rules_edit(self, ctx: Context, rule: int, *, new_rule: str):
        """Edits an existing rule.

        `rule` **->** The number of the rule to edit.
        `new_rule` **->** The new rule to replace it with.
        """

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'{ctx.denial} There are currently no rules set.')
        elif rule == 0:
            return await ctx.reply('Rule cannot be ``0``')

        rule -= 1
        try:
            rules.rules[rule] = new_rule
        except IndexError:
            return await ctx.reply('Rule does not exist!')
        await rules.commit()

        await ctx.reply(f'> 👌 📝 Successfully **edited** rule `{rule + 1}` to `{new_rule}`.')

    @server_rules.command(name='remove', aliases=('delete',))
    @utils.is_admin()
    async def server_rules_remove(self, ctx: Context, rule: int):
        """Removes a rule from the server's rules by its number.

        `rule` **->** The number of the rule to remove.
        """

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'{ctx.denial} There are currently no rules set.')
        else:
            if rule <= 0:
                return await ctx.reply(f'{ctx.denial} Rule cannot be equal or less than `0`')
            try:
                rules.rules.pop(rule - 1)
            except IndexError:
                return await ctx.reply(f'{ctx.denial} Rule does not exist!')
            await rules.commit()

        await ctx.reply(f'> 👌 Successfully **removed** rule `{rule}`.')

    @server_rules.command(name='clear')
    @utils.is_owner()
    async def server_rules_clear(self, ctx: Context):
        """Deletes all the rules."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'{ctx.denial} There are currently no rules set.')
        else:
            await rules.delete()

        await ctx.reply('> 👌 Successfully **cleared** the rules.')

    @commands.group(
        name='nick', invoke_without_command=True, case_insensitive=True, aliases=('nickname',)
    )
    async def change_nick(self, ctx: Context, *, new_nickname: str):
        """Change your nickname to your desired one.

        `new_nickname` **->** The new nickname you wish to change to.
        """

        res = await utils.check_username(self.bot, word=new_nickname)
        if res is True:
            return await ctx.reply(
                f'{ctx.denial} Cannot change your nickname because the nickname you chose '
                'has too less pingable characters, is a bad word or is too short.'
            )
        elif len(new_nickname) > 32:
            return await ctx.reply('Nickname has too many characters! (maximum is **32**)')

        await ctx.author.edit(nick=new_nickname)
        await ctx.reply(f'I have changed your nickname to `{new_nickname}`')

    @change_nick.command(name='reset', aliases=('remove',))
    async def remove_nick(self, ctx: Context):
        """Removes your nickname."""

        res = await utils.check_username(self.bot, word=ctx.author.name)
        if res is True:
            return await ctx.reply(
                f'{ctx.denial} Cannot remove your nickname because your username '
                'has too less pingable characters, is a bad word or is too short.'
            )
        await ctx.author.edit(nick=None)
        await ctx.reply('I have removed your nickname.')

    @commands.command(name='avatar', aliases=('av',))
    async def _av(self, ctx: Context, *, member: disnake.Member = None):
        """Check the avatar ``member`` has.

        `member` **->** The member that you want to see the avatar of. If you want to see your own avatar, you can ignore this since it defaults to you if you don't provide this argument.

        **NOTE:** This command can only be used in <#913330644875104306>
        """  # noqa

        if await utils.check_channel(ctx) is False:
            return

        member = member or ctx.author
        em = disnake.Embed(colour=utils.blurple, title=f'`{member.display_name}`\'s avatar')
        em.set_image(url=member.display_avatar)
        em.set_footer(text=f'Requested By: {ctx.author}')
        await ctx.better_reply(embed=em)

    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def created(self, ctx: Context, *, user: disnake.User = None):
        """Check the date when the ``user`` created their account.

        `user` **->** The user that you want to see the date of when they created their discord account. If you want to see your own account creation date, you can ignore this since it defaults to you if you don't provide this argument.

        **NOTE:** This command can only be used in <#913330644875104306>
        """  # noqa

        if await utils.check_channel(ctx) is False:
            return

        user = user or ctx.author
        em = disnake.Embed(
            colour=utils.blurple,
            title='Creation Date',
            description=f'{user.mention} created their account '
                        f'on {utils.format_dt(user.created_at, "F")} '
                        f'(`{utils.human_timedelta(user.created_at)}`)'
        )
        await ctx.better_reply(embed=em)

    @created.command(name='server')
    async def created_server(self, ctx: Context):
        """
        See the date when the server got created at and when it was made public.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await utils.check_channel(ctx) is False:
            return

        guild = self.bot.get_guild(913310006814859334)
        created_date = guild.created_at
        publiced_date = guild.get_member(302050872383242240).joined_at
        members = [m for m in guild.members if not m.bot]
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
        em.set_footer(text=f'There are currently {len(members)} members in the server')
        await ctx.better_reply(embed=em)

    @commands.command()
    async def joined(self, ctx: Context, *, member: disnake.Member = None):
        """Check the date when the ``member`` joined the server.

        `member` **->** The member that you want to see the date of when they joined this server. If you want to see your own join date, you can ignore this since it defaults to you if you don't provide this argument.

        **NOTE:** This command can only be used in <#913330644875104306>
        """  # noqa

        if await utils.check_channel(ctx) is False:
            return

        member = member or ctx.author
        em = disnake.Embed(
            colour=utils.blurple,
            title='Join Date',
            description=f'{member.mention} joined the server '
                        f'on {utils.format_dt(member.joined_at, "F")} '
                        f'(`{utils.human_timedelta(member.joined_at)}`)'
        )
        await ctx.better_reply(embed=em)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data: AFK = await AFK.find_one({'_id': member.id})
        if data is not None:
            await data.delete()

    @commands.command(name='checkmute', aliases=('checkmutes', 'mutescheck', 'mutecheck',))
    async def check_mute(self, ctx: Context, *, member: disnake.Member = None):
        """
        Check all the current muted members and their time left. If ``member`` is specified, it will only show for that member, including the reason they got muted.

        `user` **->** The user that you want to see the date of when they joined discord. If you want to see all the currently muted members, you can ignore this since it defaults to yourself.
        """  # noqa

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
                return await ctx.reply(f'{ctx.denial} There are no current mutes.')

            source = FieldPageSource(entries, per_page=5)
            source.embed.color = utils.blurple
            source.embed.title = 'Here are all the currently muted members'
            paginator = RoboPages(source, ctx=ctx, compact=True)
            await paginator.start()
        else:
            mute: Mutes = await Mutes.find_one({'_id': member.id})
            if mute is None:
                if member == ctx.author:
                    return await ctx.reply(f'{ctx.denial} You are not muted.')
                else:
                    return await ctx.better_reply(f'{ctx.denial} `{member}` is not muted.')
            em = disnake.Embed(colour=utils.blurple)
            em.set_author(name=member, icon_url=member.display_avatar)
            em.description = f'**Muted By:** {guild.get_member(mute.muted_by)}\n' \
                             f'**Reason:** {mute.reason}\n' \
                             f'**Mute Duration:** `{mute.duration}`\n' \
                             f'**Expires At:** {utils.format_dt(mute.muted_until, "F")}\n' \
                             f'**Remaining:** `{utils.human_timedelta(mute.muted_until, suffix=False)}`'
            em.set_footer(text=f'Requested By: {ctx.author}')
            await ctx.better_reply(embed=em)

    def append_choices(
        self,
        choices: list,
        bi_bool: bool,
        author_gender: str,
        data1: utils.Intro,
        data2: utils.Intro
    ) -> list:
        if (
            (data2.status.lower() != 'taken') and
            (data2.id != data1.id) and
            (data2.looking.lower() == 'yes')
        ):
            if bi_bool is True and author_gender is not None:
                if author_gender == 'male':
                    if data2.gender.lower() in ('male', 'm', 'boy', 'trans-male', 'trans male', 'make'):
                        if data2.sexuality.lower() not in ('bi', 'bisexual', 'pans', 'pansexual', 'omni', 'omnisexual', 'gay'):
                            return choices

                elif author_gender == 'female':
                    if data2.gender.lower() in ('female', 'f', 'girl', 'trans-female', 'trans female'):
                        if data2.sexuality.lower() not in ('bi', 'bisexual', 'pans', 'pansexual', 'omni', 'omnisexual', 'lesbian'):
                            return choices

            if data1.age == 14 and data2.age == 15:
                choices.append(self.bot.get_user(data2.id))
            elif data1.age == 15 and data2.age in (14, 16):
                choices.append(self.bot.get_user(data2.id))
            elif data1.age == 16 and data2.age in (15, 17):
                choices.append(self.bot.get_user(data2.id))
            elif data1.age == 17 and data2.age in (16, 18):
                choices.append(self.bot.get_user(data2.id))
            elif data1.age == 18 and data2.age in (17, 19):
                choices.append(self.bot.get_user(data2.id))
            elif data1.age == 19 and data2.age == 18:
                choices.append(self.bot.get_user(data2.id))

        return choices

    @commands.command(name='match')
    async def match_people(self, ctx: Context):
        """
        Matches you with another person, based on the sexuality, gender, relationship status of what the both of you have in your intros and if they are looking.

        **NOTE:** This command can only be used in <#913330644875104306>
        """  # noqa

        if await utils.check_channel(ctx) is False:
            return

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
                    f'{ctx.denial} Couldn\'t find a match because you don\'t have an intro. '
                    'Please contact a staff member to unverify you! This is a bug.'
                )
        elif data.status.lower() == 'taken':
            return await ctx.reply('You\'re already taken!')
        _sexuality = None
        _gender = None
        _bi_bool = False
        _author_gender = None
        if data.gender.lower() in ('male', 'm', 'boy', 'trans-male', 'trans male', 'make'):
            if data.sexuality.lower() == 'straight':
                _sexuality = ('straight', 'bisexual', 'bi', 'Straight', 'Bisexual', 'Bi')
                _gender = ('female', 'Female', 'girl', 'Girl', 'F', 'f')
            elif data.sexuality.lower() == 'gay':
                _sexuality = ('gay', 'bisexual', 'bi', 'Gay', 'Bisexual', 'Bi')
                _gender = ('male', 'Male', 'boy', 'Boy', 'M', 'm', 'make', 'Make')
            elif data.sexuality.lower() in ('bi', 'bisexual', 'pans', 'pansexual', 'omni', 'omnisexual'):
                _gender = ('male', 'Male', 'boy', 'Boy', 'M', 'm', 'female', 'Female', 'girl', 'Girl', 'F', 'f', 'make', 'Make')
                _author_gender = 'male'
                _bi_bool = True

        elif data.gender.lower() in ('female', 'f', 'girl', 'trans-female', 'trans female'):
            if data.sexuality.lower() == 'straight':
                _sexuality = ('straight', 'bisexual', 'bi', 'Straight', 'Bisexual', 'Bi')
                _gender = ('male', 'Male', 'boy', 'Boy', 'M', 'm', 'make', 'Make')
            elif data.sexuality.lower() == 'lesbian':
                _sexuality = ('lesbian', 'bisexual', 'bi', 'Lesbian', 'Bisexual', 'Bi')
                _gender = ('female', 'Female', 'girl', 'Girl', 'F', 'f')
            elif data.sexuality.lower() in ('bi', 'bisexual', 'pans', 'pansexual', 'omni', 'omnisexual'):
                _gender = ('male', 'Male', 'boy', 'Boy', 'M', 'm', 'female', 'Female', 'girl', 'Girl', 'F', 'f', 'make', 'Make')
                _author_gender = 'female'
                _bi_bool = True

        if _gender is not None:
            for gender in _gender:
                if _sexuality is not None:
                    for sexuality in _sexuality:
                        async for mem in utils.Intro.find({'gender': gender, 'sexuality': sexuality}):
                            choices = self.append_choices(choices, _bi_bool, _author_gender, data, mem)
                else:
                    async for mem in utils.Intro.find({'gender': gender}):
                        choices = self.append_choices(choices, _bi_bool, _author_gender, data, mem)
        else:
            async for mem in utils.Intro.find():
                choices = self.append_choices(choices, _bi_bool, _author_gender, data, mem)

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
    async def check_staff(self, ctx: Context):
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

        await ctx.better_reply(message)

    @commands.group(name='afk', invoke_without_command=True, case_insensitive=True)
    async def _afk(self, ctx: Context, *, reason: str = None):
        """Set yourself on ``AFK``. While being ``AFK``, anybody who pings you will be told by the bot that you are ``AFK`` with the reason you provided.

        `reason` **->** The reason you are ``AFK``. You can set a default by using `!afk default set`. For a list of commands for that, you can type `!help afk default`.
        """  # noqa

        data: AFK = await AFK.find_one({'_id': ctx.author.id})
        if data is None:
            if reason is None:
                return await ctx.reply('You must give the reason!')
            await AFK(
                id=ctx.author.id,
                reason=reason,
                date=ctx.message.created_at,
                message_id=ctx.message.id,
                is_afk=True
            ).commit()

        elif data is not None:
            if data.is_afk is True:
                return await ctx.reply('You are already ``AFK``!')
            reason = f'{reason} | {data.default}' if reason is not None else data.default
            data.reason = reason
            data.date = ctx.message.created_at
            data.message_id = ctx.message.id
            data.is_afk = True
            await data.commit()

        await ctx.reply(f'You are now ``AFK`` **->** **"{reason}"**')

    @_afk.group(name='default', invoke_without_command=True, case_insensitive=True)
    async def _afk_default(self, ctx: Context):
        """See your default ``AFK`` reason, if you set any."""

        data: AFK = await AFK.find_one({'_id': ctx.author.id})
        if data is None or data.default is None:
            return await ctx.reply('You don\'t have a default ``AFK`` reason set!')

        await ctx.reply(f'Your default ``AFK`` reason is: **"{data.default}"**')

    @_afk_default.command(name='set')
    async def _afk_default_set(self, ctx: Context, *, default: str):
        """Sets your default ``AFK`` reason.

        `default` **->** The default reason you want to set for your ``AFK``.
        """

        data: AFK = await AFK.find_one({'_id': ctx.author.id})
        if data is None:
            await AFK(
                id=ctx.author.id,
                default=default
            ).commit()
        else:
            data.default = default
            await data.commit()

        await ctx.reply(f'Successfully set your default ``AFK`` reason to: **"{default}"**')

    @_afk_default.command(name='remove')
    async def _afk_default_remove(self, ctx: Context):
        """Removes your default ``AFK`` reason."""

        data: AFK = await AFK.find_one({'_id': ctx.author.id})
        if data is None:
            return await ctx.reply('You don\'t have a default ``AFK`` reason set!')
        await data.delete()

        await ctx.reply('Successfully removed your default ``AFK`` reason.')

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        data: AFK = await AFK.find_one({'_id': message.author.id})
        if data is not None:
            if data.is_afk is True and message.id != data.message_id:
                await message.reply(
                    'Welcome back! Removed your ``AFK``\nYou have been ``AFK`` '
                    f'since {utils.format_dt(data.date, "F")} '
                    f'(`{utils.human_timedelta(dt=data.date)}`)'
                )
                if data.default is None:
                    await data.delete()
                else:
                    data.is_afk = False
                    data.reason = None
                    data.date = None
                    data.message_id = None
                    await data.commit()
                return

        for user in message.mentions:
            data: AFK = await AFK.find_one({'_id': user.id})
            if data is not None and data.is_afk is True:
                await message.reply(
                    f'**{user}** is ``AFK`` **->** **"{data.reason}"** '
                    f'*since {utils.format_dt(data.date, "F")} '
                    f'(`{utils.human_timedelta(dt=data.date)}`)*')

    @utils.run_in_executor
    def search_wiki(self, query):
        return wikipedia.page(query, auto_suggest=False)

    @commands.command(name='wikipedia', aliases=('wiki',))
    async def _wikipedia(self, ctx: Context, *, query: str):
        """Search something on wikipedia.

        `query` **->** What to search on wikipedia for.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await utils.check_channel(ctx) is False:
            return

        try:
            res: wikipedia.WikipediaPage = await self.search_wiki(query)
        except Exception:
            return await ctx.reply('Failed to find what you were looking for.')

        menu = utils.WikiView(utils.FrontPageSource(), ctx)
        menu.clear_items()
        menu.add_item(utils.WikiSelect(ctx, res))
        menu.fill_items()

        await menu.start(ref=True)

    @commands.command()
    async def urban(self, ctx: Context, *, query):
        """Searches using urban dictionary for the given query.

        `query` **->** What to search for using the urban dictionary.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await utils.check_channel(ctx) is False:
            return

        url = 'http://api.urbandictionary.com/v0/define'
        resp = await ctx.session.get(url, params={'term': query})
        if resp.status != 200:
            await self.bot._owner.send(
                embed=disnake.Embed(
                    description=f"[`{ctx.command}`]({ctx.message.jump_url}) gave an error:\n\n"
                                f"Query: **{query}**\nStatus: **{resp.status}**\nReason: **{resp.reason}**"
                )
            )
            return await ctx.send('An error occurred. Please try again later.')

        js: dict = await resp.json()
        data = js.get('list', [])
        if not data:
            return await ctx.send('No results found.')

        pages = RoboPages(source=utils.UrbanDictionaryPageSource(data), ctx=ctx, compact=True)
        await pages.start()


def setup(bot: Ukiyo):
    bot.add_cog(Misc(bot))
