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
        self.webhook = None
        self.mod_webhook = None

    async def check_bad_word(self, message: disnake.Message):
        if 913310292505686046 in (r.id for r in message.author.roles):  # Checks for owner
            return
        guild = self.bot.get_guild(913310006814859334)
        if self.mod_webhook is None:
            self.mod_webhook = await self.bot.get_webhook(
                guild.get_channel(914257049456607272),
                avatar=self.bot.user.display_avatar
            )
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
                        self.mod_webhook,
                        title='[MUTE]',
                        fields=[
                            ('Member', f'{message.author.mention} (`{message.author.id}`)'),
                            ('Reason', 'Bad Words.'),
                            ('Mute Duration', f'`{duration}`'),
                            ('Expires At', utils.format_dt(_data.dt, "F")),
                            ('By', f'{self.bot.user.mention} (`{self.bot.user.id}`)'),
                            ('At', utils.format_dt(datetime.datetime.now(), 'F')),
                        ],
                        view=view
                    )

    @commands.Cog.listener('on_message_delete')
    async def on_message_delete(self, message: disnake.Message):
        if message.author.bot or not message.guild:
            return
        if message.author.id == self.bot._owner_id:
            return

        else:
            em = disnake.Embed(
                color=utils.red,
                description=f'Message deleted in <#{message.channel.id}> \n\n'
                            f'**Content:** \n```{message.content}```',
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
                if self.webhook is None:
                    self.webhook = await self.bot.get_webhook(
                        self.bot.get_channel(913332431417925634),
                        avatar=self.bot.user.display_avatar
                    )
                await self.webhook.send(embed=em, view=btn)
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
            await asyncio.sleep(0.5)
            try:
                btn = disnake.ui.View()
                btn.add_item(disnake.ui.Button(label='Jump!', url=after.jump_url))
                if self.webhook is None:
                    self.webhook = await self.bot.get_webhook(
                        self.bot.get_channel(913332431417925634),
                        avatar=self.bot.user.display_avatar
                    )
                await self.webhook.send(embed=em, view=btn)
            except Exception as e:
                ctx = await self.bot.get_context(after, cls=utils.Context)
                await self.bot.reraise(ctx, e)

    @commands.Cog.listener('on_message')
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        if message.author.id != self.bot._owner_id:
            if message.guild:
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
                            description=f'{message.author.mention} send an invite in {message.channel.mention}'
                        )
                        v = disnake.ui.View()
                        v.add_item(disnake.ui.Button(label='Jump!', url=message.jump_url))
                        await invite_logs.send(embed=em, view=v)
                        return await message.channel.send(
                            f'Invites are not allowed! {message.author.mention}', delete_after=5.0
                        )
                await self.check_bad_word(message)
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

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data = await utils.InvalidName.find_one({'_id': member.id})
        if data:
            await data.delete()


def setup(bot: Ukiyo):
    bot.add_cog(OnMessage(bot))
