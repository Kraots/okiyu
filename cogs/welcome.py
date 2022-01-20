from datetime import datetime, timezone

import disnake
from disnake.ext import commands

import utils

from main import Ukiyo


class Welcome(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @commands.Cog.listener('on_member_join')
    async def on_member_join(self, member: disnake.Member):
        guild = self.bot.get_guild(913310006814859334)

        if member.bot:
            bot_role = guild.get_role(913459676962770944)
            await member.add_roles(bot_role, reason='Bot Account.')
            return

        await utils.check_username(member=member)
        unverified_role = guild.get_role(913329062347423775)
        await member.add_roles(unverified_role)

        welcome_channel = guild.get_channel(913331535170637825)
        welcome_webhook = await self.bot.get_webhook(welcome_channel, avatar=self.bot.user.display_avatar)
        member_count = len([m for m in guild.members if not m.bot])

        welcome = disnake.Embed(
            description="***Please read the rules at*** <#913331459673178122>\n"
                        "***You can always get a colour from*** <#913331502761271296>\n"
                        "***Don't forget to get your roles from*** <#913336089492717618>\n"
                        "***For bot commands please use*** <#913330644875104306>\n\n"
                        "> Enjoy your stay ^-^",
            color=utils.pastel
        )
        welcome.set_thumbnail(url=member.display_avatar)
        welcome.set_footer(text=f"Joined discord {utils.human_timedelta(member.created_at)}", icon_url=member.display_avatar)
        msg = f'Hey {member.mention}, welcome to **Ukiyo!** \nYou are our **{utils.format_position(member_count)}** member.\n\n\n_ _'
        await welcome_webhook.send(msg, embed=welcome)

        mute: utils.Mutes = await utils.Mutes.get(member.id)
        if mute is not None:
            if mute.blocked is True:
                action = 'block'
                fmt = 'blocked'
            elif mute.muted is True:
                action = 'mute'
                fmt = 'muted'

            muted_role_id = 913376647422545951
            blocked_role_id = 924941473089224784
            role = guild.get_role(muted_role_id) if action == 'mute' else guild.get_role(blocked_role_id)
            mem = guild.get_member(mute.muted_by)
            await member.add_roles(role, reason=f'[{action.title()} EVASION] user joined but was still {fmt} in the database')
            em = disnake.Embed(title=f'You have been {fmt}!', color=utils.red)
            em.description = f'**{fmt.title()} By:** {self.bot.user}\n' \
                             f'**Reason:** {action.title} Evasion.\n' \
                             f'**Expire Date:** {utils.format_dt(mute.muted_until, "F")}\n' \
                             f'**Remaining:** `{utils.human_timedelta(mute.muted_until, suffix=False, accuracy=6)}`'
            em.set_footer(text=f'{fmt.title()} in `Ukiyo`')
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


def setup(bot: Ukiyo):
    bot.add_cog(Welcome(bot))
