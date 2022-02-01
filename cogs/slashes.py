from disnake.ext import commands
from disnake import AppCmdInter

import utils

from main import Okiyu


class SlashCommands(commands.Cog):
    def __init__(self, bot: Okiyu):
        self.bot = bot

    @commands.slash_command(name='colours', description='Change your colour!')
    async def change_colour(self, inter: AppCmdInter):
        if inter.author.id == self.bot._owner_id:
            view = utils.SlashColours(inter, is_owner=True)
            await inter.response.send_message('**Please use me master 😩**', view=view, ephemeral=True)
        else:
            view = utils.SlashColours(inter)
            await inter.response.send_message('**Please use the select menu below:**', view=view, ephemeral=True)


def setup(bot: Okiyu):
    bot.add_cog(SlashCommands(bot))
