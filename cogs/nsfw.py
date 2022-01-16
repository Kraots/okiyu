import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Ukiyo


class Nsfw(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @commands.group(name='nsfw', invoke_without_command=True, case_insensitive=True, hidden=True)
    async def base_nsfw(self, ctx: Context):
        """Base command for all nsfw commands."""

        await ctx.send_help('Nsfw')

    @base_nsfw.command(name='toggle')
    async def nsfw_toggle(self, ctx: Context):
        """Toggle the visibilty of the nsfw channel for you."""

        nsfw_channel = ctx.ukiyo.get_channel(932226719593672714)
        overwrite = nsfw_channel.overwrites_for(ctx.author)
        if overwrite.read_messages is True:
            ternary = 'off'
            await nsfw_channel.set_permissions(
                ctx.author,
                overwrite=None,
                reason='Member toggled off the visibility of the nsfw channel.'
            )
        else:
            ternary = 'on'
            await nsfw_channel.set_permissions(
                ctx.author,
                read_messages=True,
                reason='Member toggled on the visibility of the nsfw channel.'
            )

        await ctx.reply(f'Successfully toggled **{ternary}** the visibility of the nsfw channel for you.')


def setup(bot: Ukiyo):
    bot.add_cog(Nsfw(bot))
