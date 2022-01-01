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
    async def _eval(self, ctx: Context, *, code: str):
        """Evaluate code.

        `code` **->** The code to evaluate.

        **Local Variables**
        \u2800 • ``disnake`` **->** The disnake module.
        \u2800 • ``commands`` **->** The disnake.ext.commands module.
        \u2800 • ``_bot`` **->** The bot instance. (`Ukiyo`)
        \u2800 • ``_ctx`` **->** The ``Context`` object of the command.
        \u2800 • ``_channel`` **->** The ``disnake.abc.GuildChannel`` the command is invoked in.
        \u2800 • ``_author`` **->** The ``disnake.Member`` of the command.
        \u2800 • ``_guild`` **->** The ``disnake.Guild`` object the command is invoked in.
        \u2800 • ``_message`` **->** The ``disnake.Message`` object of the command.
        \u2800 • ``utils`` **->** The bot's ``utils`` custom package.
        """

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
        view = utils.QuitButton(ctx)
        view.message = await ctx.send(embed=em, view=view)
        data = self.bot.execs.get(ctx.author.id)
        if data is None:
            self.bot.execs[ctx.author.id] = {ctx.command.name: view.message}
        else:
            self.bot.execs[ctx.author.id][ctx.command.name] = view.message

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

    @commands.command(name='toggle')
    async def toggle_cmd(self, ctx: Context, *, command: str):
        """Toggle a command on and off.

        `command` **->** The command to disable.
        """

        cmd = self.bot.get_command(command)
        if cmd is None:
            return await ctx.reply('Command not found.')
        elif cmd.qualified_name == 'toggle':
            return await ctx.reply('This command cannot be disabled.')
        cmd.enabled = not cmd.enabled

        await ctx.reply(
            f'Successfully **{"enabled" if cmd.enabled is True else "disabled"}** the command `{cmd.qualified_name}`'
        )


def setup(bot: Ukiyo):
    bot.add_cog(Developer(bot))
