import os
import io
import sys
import time
import textwrap
import contextlib
from traceback import format_exception

import disnake
from disnake.ext import commands

import utils
from utils import Context, TextPage, clean_code

from main import Ukiyo


def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)


class QuitButton(disnake.ui.View):
    def __init__(
        self,
        ctx: Context,
        *,
        timeout: float = 180.0,
        delete_after: bool = False
    ):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.delete_after = delete_after
        self.message = None

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if interaction.author.id != self.ctx.author.id:
            await interaction.response.send_message(
                f'Only **{self.ctx.author.display_name}** can use the buttons on this message!',
                ephemeral=True
            )
            return False
        return True

    async def on_error(self, error, item, inter):
        await self.bot.inter_reraise(self.bot, inter, item, error)

    async def on_timeout(self):
        if self.delete_after is False:
            return await self.message.edit(view=None)

        await self.message.delete()
        await self.ctx.message.delete()

    @disnake.ui.button(label='Quit', style=disnake.ButtonStyle.red)
    async def quit(self, button: disnake.ui.Button, inter: disnake.Interaction):
        """Deletes the user's message along with the bot's message."""

        await inter.response.defer()
        await self.message.delete()
        await self.ctx.message.delete()
        self.stop()


class Developer(commands.Cog):
    """Dev only commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        if ctx.author.id != self.bot._owner_id:
            raise commands.NotOwner
        return True

    @property
    def display_emoji(self) -> str:
        return '⚒️'

    @commands.command(name='eval', aliases=['e'])
    async def _eval(self, ctx: Context, *, code: str = None):
        """Evaluate code."""

        if code is None:
            return await ctx.send("Please give code that you want to evaluate!")

        code = clean_code(code)

        local_variables = {
            "disnake": disnake,
            "commands": commands,
            "_bot": self.bot,
            "_ctx": ctx,
            "_channel": ctx.channel,
            "_author": ctx.author,
            "_guild": ctx.guild,
            "_message": ctx.message,
            "utils": utils
        }
        start = time.perf_counter()

        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n-- {obj}\n"
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))

        end = time.perf_counter()
        took = f"{end-start:.3f}"
        if took == "0.000":
            took = f"{end-start:.7f}"

        if len(result) >= 4000:
            pager = TextPage(
                ctx,
                [result[i: i + 4000] for i in range(0, len(result), 4000)],
                footer=f'Took {took}s',
                quit_delete=True
            )
            return await pager.start()
        em = disnake.Embed(description=f'```py\n{result}\n```')
        em.set_footer(text=f'Took {took}s')
        view = QuitButton(ctx)
        view.message = msg = await ctx.send(embed=em, view=view)
        data = self.bot.execs.get(ctx.author.id)
        if data is None:
            self.bot.execs[ctx.author.id] = {ctx.command.name: msg}
        else:
            self.bot.execs[ctx.author.id][ctx.command.name] = msg

    @commands.command()
    async def shutdown(self, ctx: Context):
        """Closes the bot."""

        await ctx.message.add_reaction(ctx.agree)
        await self.bot.close()

    @commands.command()
    async def restart(self, ctx: Context):
        """Restarts the bot."""

        await ctx.send("*Restarting...*")
        restart_program()


def setup(bot: Ukiyo):
    bot.add_cog(Developer(bot))
