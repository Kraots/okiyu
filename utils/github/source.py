import os
import re
from inspect import getsourcelines, getsourcefile
from textwrap import dedent
from typing import Optional

import disnake
from disnake.ext.commands import (
    Command,
    InvokableSlashCommand,
    SubCommandGroup,
    SubCommand
)

from utils import UrlButton
from utils.views.help_command import PaginatedHelpCommand

doc_reg_class = r'("""|\'\'\')([\s\S]*?)(\1\s*)'

__all__ = ('GithubSource',)


class ReturnData:
    embed: disnake.Embed = None
    view: disnake.ui.View = None


class GithubSource:
    """Displays information about the bot's source code."""

    BOT_REPO_URL = 'https://github.com/Kraots/ukiyo'

    def __init__(
        self, bot_avatar: str, max_lines: int = 20
    ) -> None:
        self.max_lines = max_lines
        self.bot_avatar = bot_avatar

    async def get_source(
        self,
        cmd: Optional[Command | InvokableSlashCommand | SubCommandGroup | SubCommand | str] = None
    ) -> ReturnData:
        """Display information and a GitHub link to the source code of a command."""

        data = ReturnData()
        if cmd is None:
            embed = disnake.Embed(title="Ukiyo's GitHub Repository")
            embed.add_field(name="Repository", value=f"[View on GitHub]({self.BOT_REPO_URL})")
            embed.set_thumbnail(url=self.bot_avatar)
            data.embed = embed
            data.view = UrlButton(label='View on Github', url=self.BOT_REPO_URL)

            return data

        if isinstance(cmd, str):
            src = PaginatedHelpCommand
            filename = getsourcefile(src)
        else:
            src = cmd.callback.__code__
            filename = src.co_filename

        code_lines, firstlineno = getsourcelines(src)
        location = os.path.relpath(filename).replace('\\', '/')
        url = (
            f'{self.BOT_REPO_URL}/blob/master/{location}#L{firstlineno}-L{firstlineno + len(code_lines) - 1}'
        )

        source_code = "".join(code_lines)
        sanitized = source_code.replace("`", "\u200B`")
        sanitized = re.sub(doc_reg_class, "", sanitized)

        # The help argument of commands.command gets changed to `help=`
        sanitized = sanitized.replace("help=", 'help=""')

        # Remove the extra indentation in the code.
        sanitized = dedent(sanitized)

        _lines = sanitized.splitlines()
        lines = []
        for index, line in enumerate(_lines):
            if index + 1 >= self.max_lines:
                lines.append('\n... (truncated - too many lines)')
                break
            lines.append(line)

        lines = '\n'.join(lines)

        embed = disnake.Embed(title="Ukiyo's Source Link", description=f"{url}")
        embed.add_field(
            name="Source Code Snippet", value=f"```python\n{lines}\n```"
        )
        embed.set_thumbnail(url=self.bot_avatar)
        embed.set_footer(text=f'Command has a total of {len(code_lines):,} lines of code')

        data.embed = embed
        data.view = UrlButton(label='View on Github', url=url)

        return data
