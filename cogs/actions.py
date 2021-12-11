import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Ukiyo


class Actions(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '<:hug:914072588886614027>'

    @commands.command(name='huggles')
    async def _huggles(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Give somebody a hug ❤️

        `members` **->** The people you want to hug. Can be more than just one, or none.
        """

        mems = ' '.join([m.mention for m in members]) if members else None
        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://media.discordapp.net/attachments/737981297212915712/751115114106585243/374622847672254466.gif'
        )

        await ctx.reply(mems, embed=em)


def setup(bot: Ukiyo):
    bot.add_cog(Actions(bot))
