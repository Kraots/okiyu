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

        await utils.check_username(self.bot, member=member)
        unverified_role = guild.get_role(913329062347423775)
        await member.add_roles(unverified_role)

        welcome_channel = guild.get_channel(913331535170637825)
        member_count = len([m for m in guild.members if not m.bot])

        welcome = disnake.Embed(
            description="\n\n***Please read the rules at*** <#913331459673178122>\n"
                        "***You can always get a colour from*** <#913331502761271296>\n"
                        "***Don't forget to get your roles from*** <#913336089492717618>\n"
                        "***For bot commands please use*** <#913330644875104306>\n\n"
                        "> Enjoy your stay ^-^\n\n",
            color=utils.pastel
        )
        welcome.set_thumbnail(url=member.display_avatar)
        welcome.set_footer(text=f"Created: {utils.human_timedelta(member.created_at)}", icon_url=member.display_avatar)
        msg = f'Hey {member.mention}, welcome to **Ukiyo!** \nYou are our **{member_count}** member.\n\n\n_ _'
        await welcome_channel.send(msg, embed=welcome)

        mute: utils.Mutes = await utils.Mutes.find_one({'_id': member.id})
        if mute is not None:
            muted_role = guild.get_role(913376647422545951)
            await member.add_roles(muted_role, reason='[MUTE EVASION] user joined but was still muted in the database')


def setup(bot: Ukiyo):
    bot.add_cog(Welcome(bot))
