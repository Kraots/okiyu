from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

import disnake
from disnake.ext import commands, tasks

import utils

from main import Okiyu


class Welcome(commands.Cog):
    def __init__(self, bot: Okiyu):
        self.bot = bot
        self.files = {}
        self.send_welc.start()

    @tasks.loop(seconds=15.0)
    async def send_welc(self):
        webhook = self.bot.webhooks.get('welcome_webhook')
        if webhook is not None:
            if len(self.files) == 10:
                await webhook.send(files=self.files.values())
            else:
                files = []
                count = 0
                for file in self.files.values():
                    count += 1
                    files.append(file)
                    if count == 10:
                        await webhook.send(files=files)
                        count = 0
                        files = []
                if len(files) != 0:
                    await webhook.send(files=files)
                    files = []
            self.files = {}

    @commands.Cog.listener('on_member_join')
    async def on_member_join(self, member: disnake.Member):
        entry: utils.Constants = await utils.Constants.get()
        days_ago = datetime.now(timezone.utc) - relativedelta(days=entry.min_account_age)
        if member.created_at > days_ago:
            await utils.try_dm(member, 'Your account is too new to be allowed in the server.')
            await member.ban(reason='Account too new.')
            return await utils.log(
                self.bot.webhooks['mod_logs'],
                title='[BAN]',
                fields=[
                    ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                    ('Reason', 'Account too new.'),
                    ('Account Created', utils.human_timedelta(member.created_at, accuracy=7)),
                    ('By', f'{self.bot.user.mention} (`{self.bot.user.id}`)'),
                    ('At', utils.format_dt(datetime.now(), 'F')),
                ]
            )

        if member.guild.id != 938115625073639425:  # Only continue if it's actual okiyu server.
            return

        guild = self.bot.get_guild(938115625073639425)

        alt_guild = self.bot.get_guild(938886845314510978)  # The 2nd okiyu guild just for bumping to get members
        mem = alt_guild.get_member(member.id)
        if mem is not None:
            await mem.ban()

        if member.bot:
            bot_role = guild.get_role(utils.ExtraRoles.bot)
            await member.add_roles(bot_role, reason='Bot Account.')
            return

        await utils.check_username(member=member)
        unverified_role = guild.get_role(utils.ExtraRoles.unverified)
        await member.add_roles(unverified_role)

        member_count = len([m for m in guild.members if not m.bot])
        file = await utils.create_welcome_card(member, member_count)
        self.files[member.id] = file

        mute: utils.Mutes = await utils.Mutes.get(member.id)
        if mute is not None:
            if mute.blocked is True:
                action = 'block'
                fmt = 'blocked'
            elif mute.muted is True:
                action = 'mute'
                fmt = 'muted'

            role = guild.get_role(utils.ExtraRoles.muted) if action == 'mute' else guild.get_role(utils.ExtraRoles.blocked)
            mem = guild.get_member(mute.muted_by)
            await member.add_roles(role, reason=f'[{action.title()} EVASION] user joined but was still {fmt} in the database')
            em = disnake.Embed(title=f'You have been {fmt}!', color=utils.red)
            em.description = f'**{fmt.title()} By:** {self.bot.user}\n' \
                             f'**Reason:** {action.title} Evasion.\n' \
                             f'**Expire Date:** {utils.format_dt(mute.muted_until, "F")}\n' \
                             f'**Remaining:** `{utils.human_timedelta(mute.muted_until, suffix=False, accuracy=6)}`'
            em.set_footer(text=f'{fmt.title()} in `Okiyu`')
            em.timestamp = datetime.now(timezone.utc)
            await utils.try_dm(member, embed=em)

            view = disnake.ui.View()
            view.add_item(disnake.ui.Button(label='Jump!', url=mute.jump_url))
            await utils.log(
                self.bot.webhooks['mod_logs'],
                title=f'[{action.upper()} EVASION]',
                fields=[
                    ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                    ('Reason', f'{action.title()} Evasion.'),
                    ('Expires At', utils.format_dt(mute.muted_until, 'F')),
                    ('Remaining', f'`{utils.human_timedelta(mute.muted_until, suffix=False)}`'),
                    ('By', f'{mem.mention} (`{mem.id}`)'),
                    ('At', utils.format_dt(datetime.now(), 'F')),
                ],
                view=view
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.guild.id == 938886845314510978:
            return

        if member.id in self.files:
            del self.files[member.id]


def setup(bot: Okiyu):
    bot.add_cog(Welcome(bot))
