from datetime import datetime

import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Ukiyo


class Featured(commands.Cog):
    """Featured cool commands."""

    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '⭐'

    @commands.command(name='timediff')
    async def time_difference(self, ctx: Context, date1: str, date2: str):
        """Compare 2 dates. The format in which you give this must be **day/month/year**.

        `time1` **->** The first date you want to compare the second date to.
        `time2` **->** The second date you want to compare the first date to.

        **Example:**
        `!timediff 24/08/2005 23/12/2021` **->** This will show the exact difference (not hour/sec precise) between 23rd December 2021 and 25th August 2005 (also the owner's birthday :flushed:)
        """  # noqa

        try:
            time1 = datetime.strptime(date1, '%d/%m/%Y')
            time2 = datetime.strptime(date2, '%d/%m/%Y')
        except ValueError:
            return await ctx.reply(
                'One of the dates you have given does not match the format in which a date should be given.'
            )
        diff = utils.human_timedelta(time2, source=time1, suffix=False, accuracy=4)

        _time1 = time1.strftime('%d %B %Y')
        _time2 = time2.strftime('%d %B %Y')

        em = disnake.Embed(
            color=utils.blurple,
            description=f'The difference between **{_time1}** and **{_time2}** is `{diff}`'
        )

        await ctx.better_reply(embed=em)


def setup(bot: Ukiyo):
    bot.add_cog(Featured(bot))
