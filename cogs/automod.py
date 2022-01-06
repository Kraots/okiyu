import re
import datetime

import disnake
from disnake.ext import commands

import utils

from main import Ukiyo


class AutoMod(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.muted_amount_count = {}

        # (messages, seconds, user/member/channel)
        self.messages_cooldown = utils.CooldownByContent.from_cooldown(
            15, 45.0, commands.BucketType.user)  # Checks for same content (15msg per 45s)
        self.user_cooldown = commands.CooldownMapping.from_cooldown(
            10, 13.0, commands.BucketType.user)  # Checks for member spam (10msg per 13s)
        self.words_cooldown = commands.CooldownMapping.from_cooldown(
            3, 86400.0, commands.BucketType.user)  # Checks for bad words (3msg per 24h)
        self.invite_cooldown = commands.CooldownMapping.from_cooldown(
            5, 18000.0, commands.BucketType.user)  # Checks for invites (5msg per 5h)

    def get_mute_time(self, user_id) -> str:
        try:
            curr_amount = self.muted_amount_count[user_id]
            curr_amount += 1
            self.muted_amount_count[user_id] = curr_amount
        except KeyError:
            curr_amount = 1
            self.muted_amount_count[user_id] = 1

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

    async def apply_action(self, message: disnake.Message, reason: str):
        user = message.author
        ctx = await self.bot.get_context(message, cls=utils.Context)
        time = self.get_mute_time(user.id)

        action = 'muted'
        _action = 'mute'
        kwargs = {'muted': True}
        role = ctx.ukiyo.get_role(913376647422545951)  # Mute
        if self.muted_amount_count[user.id] >= 3:  # Block if this is the user's 3rd time they get punished
            action = 'blocked'
            _action = 'block'
            kwargs = {'blocked': True}
            role = ctx.ukiyo.get_role(924941473089224784)

        _data = await utils.UserFriendlyTime(commands.clean_content).convert(ctx, f'{time} {reason.title()}')
        duration = utils.human_timedelta(_data.dt, suffix=False)
        data = utils.Mutes(
            id=user.id,
            muted_by=self.bot.user.id,
            muted_until=_data.dt,
            reason=_data.arg,
            duration=duration,
            filter=True,
            **kwargs
        )
        if 913315033134542889 in (r.id for r in user.roles):  # Checks for admin
            data.is_admin = True
        elif 913315033684008971 in (r.id for r in message.author.roles):  # Checks for mod
            data.is_mod = True
        new_roles = [role for role in user.roles
                     if role.id not in (913310292505686046, 913315033134542889, 913315033684008971)
                     ] + [role]
        await user.edit(roles=new_roles, reason=f'[AUTOMOD: {reason.upper()}]')

        try:
            em = disnake.Embed(title=f'You have been {action}!', color=utils.red)
            em.description = f'**{action.title()} By:** {self.bot.user}\n' \
                             f'**Reason:** Automod: {_data.arg}\n' \
                             f'**{_action.title()} Duration:** `{duration}`\n' \
                             f'**Expire Date:** {utils.format_dt(_data.dt, "F")}\n' \
                             f'**Remaining:** {utils.human_timedelta(data.muted_until, suffix=False, accuracy=6)}'
            em.set_footer(text=f'{action.title()} in `Ukiyo`')
            em.timestamp = datetime.datetime.now(datetime.timezone.utc)
            await user.send(embed=em)
        except disnake.Forbidden:
            pass
        _msg = await message.channel.send(
            f'> ⚠️ **[AUTOMOD: {reason.upper()}]** {user.mention} has been **{action}** for **{reason.lower()}** '
            f'until {utils.format_dt(_data.dt, "F")} (`{duration}`)'
        )
        data.jump_url = _msg.jump_url
        await data.commit()

        view = utils.UrlButton('Jump!', _msg.jump_url)
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title=f'[AUTOMOD {_action.upper()}]',
            fields=[
                ('Member', f'{user} (`{user.id}`)'),
                ('Reason', reason.title()),
                (f'{_action.title()} Duration', f'`{duration}`'),
                ('Expires At', utils.format_dt(_data.dt, "F")),
                ('Remaining', f'`{utils.human_timedelta(data.muted_until, suffix=False, accuracy=6)}`'),
                ('By', f'{self.bot.user.mention} (`{self.bot.user.id}`)'),
                ('At', utils.format_dt(datetime.datetime.now(), 'F')),
            ],
            view=view
        )

    async def anti_raid(self, message: disnake.Message):
        current = message.created_at.timestamp()

        content_bucket = self.messages_cooldown.get_bucket(message)
        if content_bucket.update_rate_limit(current):
            content_bucket.reset()
            return await self.apply_action(message, 'anti raid (repeated messages)')

        user_bucket = self.user_cooldown.get_bucket(message)
        if user_bucket.update_rate_limit(current):
            user_bucket.reset()
            return await self.apply_action(message, 'anti raid (spam)')

    async def anti_bad_words(self, message: disnake.Message):
        current = message.created_at.timestamp()

        if utils.check_profanity(message.content):
            await message.delete()

            words_bucket = self.words_cooldown.get_bucket(message)
            if words_bucket.update_rate_limit(current):
                words_bucket.reset()
                return await self.apply_action(message, 'bad words')

    async def anti_invites(self, message: disnake.Message):
        current = message.created_at.timestamp()

        matches = re.findall(utils.invite_regex, message.content.lower())
        if matches:
            guild = self.bot.get_guild(913310006814859334)
            if len(matches) == 1:
                _inv = matches[0].split('/')
                inv = _inv[-1]
                if any(invite for invite in await guild.invites() if invite.code.lower() == inv):
                    return

            invite_logs = guild.get_channel(913332511789178951)
            em = disnake.Embed(
                title='New Invite Found!!',
                description=f'`{message.author}` sent an invite in {message.channel.mention}'
            )
            em.set_footer(text=f'User ID: {message.author.id}')
            v = disnake.ui.View()
            v.add_item(disnake.ui.Button(label='Jump!', url=message.jump_url))
            await invite_logs.send(embed=em, view=v)

            invite_bucket = self.invite_cooldown.get_bucket(message)
            if invite_bucket.update_rate_limit(current):
                invite_bucket.reset()
                return await self.apply_action(message, 'invite found')

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot or message.author.id == self.bot._owner_id or \
                913310292505686046 in (r.id for r in message.author.roles) or \
                not message.content:
            return

        for coro in self.coros.copy():
            if await coro(self, message):
                break

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if after.author.bot or after.author.id == self.bot._owner_id or \
                913310292505686046 in (r.id for r in after.author.roles) or \
                not after.content:
            return

        for coro in self.coros.copy():
            if await coro(self, after):
                break

    coros = [anti_bad_words, anti_invites, anti_raid]


def setup(bot: Ukiyo):
    bot.add_cog(AutoMod(bot))
