from disnake.ext import commands
from disnake import AppCmdInter

import utils

from main import Ukiyo


class SlashCommands(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @commands.slash_command(name='colours', description='Change your colour!')
    async def change_colour(self, inter: AppCmdInter):
        if inter.author.id == self.bot._owner_id:
            view = utils.SlashColours(inter, is_owner=True)
            await inter.response.send_message('**Please use me master 😩**', view=view, ephemeral=True)
        else:
            view = utils.SlashColours(inter)
            await inter.response.send_message('**Please use the select menu below:**', view=view, ephemeral=True)


def setup(bot: Ukiyo):
    bot.add_cog(SlashCommands(bot))
