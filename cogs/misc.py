import time

import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Ukiyo


class Misc(commands.Cog):
    """Miscellaneous commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '🔧'

    @commands.command()
    async def ping(self, ctx: Context):
        """See the bot's ping."""

        ping = disnake.Embed(title="Pong!", description="_Pinging..._", color=utils.blurple)
        start = time.time() * 1000
        msg = await ctx.send(embed=ping)
        end = time.time() * 1000
        ping = disnake.Embed(
            title="Pong!",
            description=f"Websocket Latency: `{(round(self.bot.latency * 1000, 2))}ms`"
            f"\nBot Latency: `{int(round(end-start, 0))}ms`"
            f"\nResponse Time: `{(msg.created_at - ctx.message.created_at).total_seconds()/1000}` ms",
            color=utils.blurple
        )
        ping.set_footer(text=f"Online for {utils.human_timedelta(dt=self.bot.uptime, suffix=False)}")
        await msg.edit(embed=ping)

    @commands.command()
    async def uptime(self, ctx: Context):
        """See how long the bot has been online for."""

        uptime = disnake.Embed(
            description=f"Bot has been online for: `{utils.human_timedelta(dt=self.bot.uptime, suffix=False)}`",
            color=utils.blurple
        )
        uptime.set_footer(text=f'Bot made by: {self.bot._owner}', icon_url=self.bot.user.display_avatar)
        await ctx.send(embed=uptime)


def setup(bot: Ukiyo):
    bot.add_cog(Misc(bot))
