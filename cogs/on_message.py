import re
import asyncio
import datetime

import disnake
from disnake.ext import commands

import utils

from main import Ukiyo

muted_amount_count = {}


def get_mute_time(user_id) -> str:
    try:
        curr_amount = muted_amount_count[user_id]
        curr_amount += 1
        muted_amount_count[user_id] = curr_amount
    except KeyError:
        curr_amount = 1
        muted_amount_count[user_id] = 1

    if curr_amount == 1:
        return '15 minutes'
    elif curr_amount == 2:
        return '30 minutes'
    elif curr_amount == 3:
        return '45 minutes'
    elif curr_amount == 4:
        return '1 hour'
    elif curr_amount == 5:
        return '12 hours'
    elif curr_amount == 6:
        return '1 day'
    else:
        return '1 month'  # This shouldn't really even happen, but just in case it really gets that bad.


class OnMessage(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.bad_words_filter = {}

    async def check_bad_word(self, message: disnake.Message):
        if 913310292505686046 in (r.id for r in message.author.roles):  # Checks for owner
            return
        guild = self.bot.get_guild(913310006814859334)
        for word in message.content.split():
            if utils.check_word(word) is True:
                ctx = await self.bot.get_context(message, cls=utils.Context)
                await message.delete()

                _ = self.bad_words_filter.get(message.author.id)
                if _ is None:
                    self.bad_words_filter[message.author.id] = 1
                else:
                    self.bad_words_filter[message.author.id] += 1
                if self.bad_words_filter[message.author.id] >= 4:
                    self.bad_words_filter[message.author.id] = 0
                    time = get_mute_time(message.author.id)
                    _data = await utils.UserFriendlyTime(commands.clean_content).convert(ctx, f'{time} Bad Words.')
                    muted_role = guild.get_role(913376647422545951)
                    duration = utils.human_timedelta(_data.dt, suffix=False)
                    data = utils.Mutes(
                        id=message.author.id,
                        muted_by=self.bot.user.id,
                        muted_until=_data.dt,
                        reason=_data.arg,
                        duration=duration,
                        filter=True
                    )
                    if 913315033134542889 in (r.id for r in message.author.roles):  # Checks for admin
                        data.is_admin = True
                    elif 913315033684008971 in (r.id for r in message.author.roles):  # Checks for mod
                        data.is_mod = True
                    new_roles = [role for role in message.author.roles
                                 if role.id not in (913310292505686046, 913315033134542889, 913315033684008971)
                                 ] + [muted_role]
                    await message.author.edit(roles=new_roles, reason=f'[BAD WORD FILTER]: "{word}"')

                    try:
                        em = disnake.Embed(title='You have been muted!', color=utils.red)
                        em.description = f'**Muted By:** {self.bot.user}\n' \
                                         f'**Reason:** {_data.arg}\n' \
                                         f'**Mute Duration:** `{duration}`\n' \
                                         f'**Expire Date:** {utils.format_dt(_data.dt, "F")}'
                        em.set_footer(text='Muted in `Ukiyo`')
                        em.timestamp = datetime.datetime.now(datetime.timezone.utc)
                        await message.author.send(embed=em)
                    except disnake.Forbidden:
                        pass
                    _msg = await message.channel.send(
                        f'> ⚠️ **[BAD WORD]** {message.author.mention} has been muted for saying a bad word '
                        f'until {utils.format_dt(_data.dt, "F")} (`{duration}`)'
                    )
                    data.jump_url = _msg.jump_url
                    await data.commit()
                    view = disnake.ui.View()
                    view.add_item(disnake.ui.Button(label='Jump!', url=_msg.jump_url))
                    await utils.log(
                        self.bot.webhooks['mod_logs'],
                        title='[MUTE]',
                        fields=[
                            ('Member', f'{message.author} (`{message.author.id}`)'),
                            ('Reason', 'Bad Words.'),
                            ('Mute Duration', f'`{duration}`'),
                            ('Expires At', utils.format_dt(_data.dt, "F")),
                            ('By', f'{self.bot.user.mention} (`{self.bot.user.id}`)'),
                            ('At', utils.format_dt(datetime.datetime.now(), 'F')),
                        ],
                        view=view
                    )

    async def check_invite(self, message: disnake.Message):
        guild = self.bot.get_guild(913310006814859334)
        matches = re.findall(utils.invite_regex, message.content.lower())
        if matches and message.author.id != self.bot._owner:
            is_staff = False
            if 913310292505686046 in (r.id for r in message.author.roles):  # Check for owner
                is_staff = True
            elif 913315033134542889 in (r.id for r in message.author.roles):  # Check for admin
                is_staff = True

            if is_staff is False:
                await message.delete()
                invite_logs = guild.get_channel(913332511789178951)
                em = disnake.Embed(
                    title='New Invite Found!!',
                    description=f'`{message.author}` sent an invite in {message.channel.mention}'
                )
                em.set_footer(text=f'User ID: {message.author.id}')
                v = disnake.ui.View()
                v.add_item(disnake.ui.Button(label='Jump!', url=message.jump_url))
                await invite_logs.send(embed=em, view=v)
                return await message.channel.send(
                    f'Invites are not allowed! {message.author.mention}', delete_after=5.0
                )

    @commands.Cog.listener('on_message_delete')
    async def on_message_delete(self, message: disnake.Message):
        if message.author.bot or not message.guild:
            return
        if message.author.id == self.bot._owner_id:
            return

        else:
            if not message.attachments and not message.content:
                return

            content = f'```{message.content}```' if message.content else 'No content.'
            em = disnake.Embed(
                color=utils.red,
                description=f'Message deleted in <#{message.channel.id}> \n\n'
                            f'**Content:** \n{content}',
                timestamp=datetime.datetime.utcnow()
            )
            em.set_author(name=f'{message.author}', icon_url=f'{message.author.display_avatar}')
            em.set_footer(text=f'User ID: {message.author.id}')
            if message.attachments:
                em.set_image(url=message.attachments[0].proxy_url)
            ref = message.reference
            if ref and isinstance(ref.resolved, disnake.Message):
                em.add_field(
                    name='Replying to...',
                    value=f'[{ref.resolved.author}]({ref.resolved.jump_url})',
                    inline=False
                )

            await asyncio.sleep(0.5)
            try:
                btn = disnake.ui.View()
                btn.add_item(disnake.ui.Button(label='Jump!', url=message.jump_url))
                await self.bot.webhooks['message_logs'].send(embed=em, view=btn)
            except Exception as e:
                ctx = await self.bot.get_context(message, cls=utils.Context)
                await self.bot.reraise(ctx, e)

    @commands.Cog.listener('on_message_edit')
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if before.author.bot or not after.guild:
            return
        if before.author.id == self.bot._owner_id:
            return
        else:
            if before.content == after.content:
                return

            em = disnake.Embed(
                color=utils.yellow,
                description=f'Message edited in <#{before.channel.id}>\n\n**Before:**\n```{before.content}```\n\n**After:**\n```{after.content}```',  # noqa
                timestamp=datetime.datetime.utcnow()
            )
            em.set_author(name=f'{before.author}', icon_url=f'{before.author.display_avatar}')
            em.set_footer(text=f'User ID: {before.author.id}')
            ref = after.reference
            if ref and isinstance(ref.resolved, disnake.Message):
                em.add_field(
                    name='Replying to...',
                    value=f'[{ref.resolved.author}]({ref.resolved.jump_url})',
                    inline=False
                )

            await self.check_bad_word(after)
            await self.check_invite(after)
            await utils.check_username(self.bot, member=after.author)
            await asyncio.sleep(0.5)
            try:
                btn = disnake.ui.View()
                btn.add_item(disnake.ui.Button(label='Jump!', url=after.jump_url))
                await self.bot.webhooks['message_logs'].send(embed=em, view=btn)
            except Exception as e:
                ctx = await self.bot.get_context(after, cls=utils.Context)
                await self.bot.reraise(ctx, e)

    @commands.Cog.listener('on_message')
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        if message.author.id != self.bot._owner_id:
            if message.guild and message.content != '':
                await self.check_bad_word(message)
                await self.check_invite(message)
                await utils.check_username(self.bot, member=message.author)

    @commands.Cog.listener('on_message_edit')
    async def repeat_command(self, before: disnake.Message, after: disnake.Message):
        if after.content.lower().startswith(('!e', '!eval')):
            ctx = await self.bot.get_context(after, cls=utils.Context)
            cmd = self.bot.get_command(after.content.lower().replace('!', ''))
            await after.add_reaction('🔁')
            try:
                await self.bot.wait_for(
                    'reaction_add',
                    check=lambda r, u: str(r.emoji) == '🔁' and u.id == after.author.id,
                    timeout=360.0
                )
            except asyncio.TimeoutError:
                await after.clear_reaction('🔁')
            else:
                curr: disnake.Message = self.bot.execs[after.author.id].get(cmd.name)
                if curr:
                    await curr.delete()
                await after.clear_reaction('🔁')
                await cmd.invoke(ctx)


def setup(bot: Ukiyo):
    bot.add_cog(OnMessage(bot))
