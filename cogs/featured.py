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
    async def display_emoji(self) -> str:
        return '💡'

    @commands.command(name='timediff')
    async def time_difference(self, ctx: Context, time1: str, time2: str):
        """Compare 2 dates. The format in which you give this must be **day/month/year**.

        `time1` **->** The greater time you want to compare time2 to. That means that this must be younger(later) than **time2**.
        `time2` **->** The earliest time you want to compare time1 to. That means that this must be the older(earlier) than **time1**

        **Example:**
        `!timediff 24/08/2005 23/12/2021` **->** This will show the exact difference (not hour/sec precise) between 23rd of December 2021 and 25th of August 2005 (also the owner's birthday :flushed:)
        """  # noqa

        time1: datetime = datetime.strptime(time1, '%d/%m/%Y')
        time2: datetime = datetime.strptime(time2, '%d/%m/%Y')
        diff = utils.human_timedelta(time2, source=time1, suffix=False)

        _time1 = time1.strftime('%d %B %Y')
        _time2 = time2.strftime('%d %B %Y')

        em = disnake.Embed(
            color=utils.blurple,
            description=f'The difference between **{_time1}** and **{_time2}** is `{diff}`'
        )

        await ctx.send(embed=em, reference=ctx.replied_reference)


def setup(bot: Ukiyo):
    bot.add_cog(Featured(bot))
