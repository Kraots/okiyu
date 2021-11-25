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

        unverified_role = guild.get_role(913329062347423775)
        await member.add_roles(unverified_role)

        welcome_channel = guild.get_channel(913331535170637825)
        member_count = len([m for m in guild.members if not m.bot])

        def format_date(dt):
            return f'{dt:%Y-%m-%d %H:%M} ({utils.human_timedelta(dt, accuracy=3)})'

        welcome = disnake.Embed(
            description="\n\n***Please read the rules at*** <#750160850303582236>\n***You can always get a colour from*** <#779388444304211991>\n"
                        "***For bot commands please use*** <#750160851822182486>\n\n"
                        "Enjoy your stay and don't forget to do your intro by typing `!intro` in a bots channel ^-^\n\n",
            color=utils.pastel
        )
        welcome.set_thumbnail(url=member.display_avatar)
        welcome.set_footer(text=f"Created: {format_date(member.created_at.replace(tzinfo=None))}", icon_url=member.display_avatar)
        msg = f'Hey {member.mention}, welcome to **ViHill Corner!** \nYou are our **{member_count}** member.\n\n\n'
        await welcome_channel.send(msg, embed=welcome)


def setup(bot: Ukiyo):
    bot.add_cog(Welcome(bot))
