from __future__ import annotations

import re
import string
import asyncio
import functools
from pathlib import Path
from traceback import format_exception
from typing import TYPE_CHECKING, Optional, Callable

import disnake
from disnake.ext import commands

import utils

if TYPE_CHECKING:
    from main import Ukiyo

__all__ = (
    'time_phaser',
    'clean_code',
    'reraise',
    'ConfirmView',
    'ConfirmViewDMS',
    'check_word',
    'check_username',
    'run_in_executor',
    'clean_inter_content',
)

allowed_letters = tuple(list(string.ascii_lowercase) + list(string.digits) + list(string.punctuation) + ['♡', ' ', '\\'])
BAD_WORDS = Path('./bad_words.txt').read_text().splitlines()


def time_phaser(seconds):
    output = ""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    mo, d = divmod(d, 30)
    if mo > 0:
        output = output + str(int(round(m, 0))) + " months "
    if d > 0:
        output = output + str(int(round(d, 0))) + " days "
    if h > 0:
        output = output + str(int(round(h, 0))) + " hours "
    if m > 0:
        output = output + str(int(round(m, 0))) + " minutes "
    if s > 0:
        output = output + str(int(round(s, 0))) + " seconds"
    return output


def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content


async def reraise(ctx: utils.Context, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send(f'> {ctx.disagree} You do not own this bot, this is an owner only command.', delete_after=8)
        await asyncio.sleep(7.5)
        await ctx.message.delete()

    elif isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(
            f'> {ctx.disagree} You are on cooldown, **`{time_phaser(error.retry_after)}`** remaining.'
        )

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        return await ctx.send(
            f"> {ctx.disagree} You are missing an argument! See `!help {ctx.command}` "
            "if you do not know how to use this."
        )

    elif isinstance(error, commands.errors.MemberNotFound):
        await ctx.send(f"> {ctx.disagree} Could not find member.")
        ctx.command.reset_cooldown(ctx)
        return

    elif isinstance(error, commands.errors.UserNotFound):
        await ctx.send(f"> {ctx.disagree} Could not find user.")
        ctx.command.reset_cooldown(ctx)
        return

    elif isinstance(error, commands.errors.CheckFailure):
        ctx.command.reset_cooldown(ctx)
        return

    elif (
        isinstance(error, commands.TooManyArguments) or
        isinstance(error, commands.BadArgument) or
        isinstance(error, commands.CommandNotFound)
    ):
        return

    else:
        get_error = "".join(format_exception(error, error, error.__traceback__))
        em = disnake.Embed(description=f'```py\n{get_error}\n```')
        if ctx.guild.id == 913310006814859334:
            await ctx.bot._owner.send(
                content=f"**An error occurred with the command `{ctx.command}`, "
                        "here is the error:**",
                embed=em
            )
            await ctx.send(f'> {ctx.disagree} An error occurred')
        else:
            await ctx.send(embed=em)


class ConfirmView(disnake.ui.View):
    """
    This class is a view with `Confirm` and `Cancel` buttons,
    this checks which button the user has pressed and returns
    True via the self.response if the button they clicked was
    Confirm else False if the button they clicked is Cancel.
    """

    def __init__(self, ctx, new_message: str = 'Time Expired.', react_user: disnake.Member = None, *, timeout=180.0):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.new_message = new_message
        self.member = react_user
        self.response = None

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        check_for = self.ctx.author.id if self.member is None else self.member.id
        if interaction.author.id != check_for:
            await interaction.response.send_message(
                f'Only {self.ctx.author.display_name if self.member is None else self.member.display_name} can use the buttons on this message!',
                ephemeral=True
            )
            return False
        return True

    async def on_error(self, error: Exception, item, interaction):
        if isinstance(self.ctx, disnake.ApplicationCommandInteraction):
            return await self.ctx.bot.slash_reraise(self.ctx, error)
        return await self.ctx.bot.reraise(self.ctx, error)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
        await self.message.edit(content=self.new_message, embed=None, view=self)

    @disnake.ui.button(label='Confirm', style=disnake.ButtonStyle.green)
    async def yes_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        self.response = True
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
            if item.label == button.label:
                item.style = disnake.ButtonStyle.blurple
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label='Cancel', style=disnake.ButtonStyle.red)
    async def no_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        self.response = False
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
            if item.label == button.label:
                item.style = disnake.ButtonStyle.blurple
        await self.message.edit(view=self)
        self.stop()


class ConfirmViewDMS(disnake.ui.View):
    """
    This class is a view with `Confirm` and `Cancel` buttons
    which only works in dms, this checks which button the user
    has pressed and returns True via the self.response if the
    button they clicked was Confirm else False if the button
    they clicked is Cancel.
    """

    def __init__(self, ctx, *, timeout=180.0, new_message: str = 'Time Expired.'):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.new_message = new_message
        self.response = None

    async def on_error(self, error: Exception, item, interaction):
        return await self.ctx.bot.reraise(self.ctx, error)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
        await self.message.edit(content=self.new_message, embed=None, view=self)

    @disnake.ui.button(label='Confirm', style=disnake.ButtonStyle.green)
    async def yes_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        self.response = True
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
            if item.label == button.label:
                item.style = disnake.ButtonStyle.blurple
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label='Cancel', style=disnake.ButtonStyle.red)
    async def no_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        self.response = False
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
            if item.label == button.label:
                item.style = disnake.ButtonStyle.blurple
        await self.message.edit(view=self)
        self.stop()


def check_word(word: str = None) -> bool:
    """
    If the return type is of bool ``True`` then it means that the word is a bad word, otherwise it's safe.
    """

    if word in BAD_WORDS:
        return True
    return False


async def check_username(bot: Ukiyo, *, member: disnake.Member = None, word: str = None) -> Optional[bool]:
    """
    If the return type is of bool ``True`` then it means that the word is invalid, otherwise it's good.
    """

    if member:
        if member.id == bot._owner_id or member.bot:
            return
    name = word or member.display_name.lower()
    count = 0
    for letter in name:
        if count < 4:
            if letter not in allowed_letters:
                count = 0
            else:
                count += 1
        else:
            break
    if count < 4:
        for word in name.split():
            if check_word(word) is True:
                count = 0
    else:
        if word is not None and member is not None:
            if count < 4:
                usr: utils.InvalidName = await utils.InvalidName.find_one({'_id': member.id})
                if usr is not None:
                    new_nick = f'UnpingableName{usr.pos}'
                    await member.edit(nick=new_nick, reason='username not pingalbe or too short')
                    return await member.send(
                        f'Your name has too few pingable letters, is a bad word or is too short so I changed it to `{new_nick}`\n'
                        'You can always change your nickname by using the command `!nick new_nick` in <#913330644875104306>'
                    )
                kraots: utils.InvalidName = await utils.InvalidName.find_one({'_id': bot._owner_id})
                kraots.last_pos += 1
                await kraots.commit()
                await utils.InvalidName(id=member.id, pos=kraots.last_pos).commit()
                new_nick = f'UnpingableName{kraots.last_pos}'
                await member.edit(nick=new_nick, reason='username not pingalbe or too short')
                return await member.send(
                    f'Your name has too few pingable letters or is too short so I changed it to `{new_nick}`\n'
                    'You can always change your nickname by using the command `!nick new_nick` in <#913330644875104306>'
                )
        else:
            if count < 4:
                return True
            else:
                return False


def run_in_executor(func: Callable):
    """Decorator that runs the sync function in the executor."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        to_run = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, to_run)

    return wrapper


def clean_inter_content(
    *,
    fix_channel_mentions: bool = False,
    use_nicknames: bool = True,
    escape_markdown: bool = False,
    remove_markdown: bool = False,
):
    async def convert(inter: disnake.ApplicationCommandInteraction, argument: str):
        if inter.guild:
            def resolve_member(id: int) -> str:
                m = inter.guild.get_member(id)
                return f'@{m.display_name if use_nicknames else m.name}' if m else '@deleted-user'

            def resolve_role(id: int) -> str:
                r = inter.guild.get_role(id)
                return f'@{r.name}' if r else '@deleted-role'
        else:
            def resolve_member(id: int) -> str:
                m = inter.bot.get_user(id)
                return f'@{m.name}' if m else '@deleted-user'

            def resolve_role(id: int) -> str:
                return '@deleted-role'

        if fix_channel_mentions and inter.guild:
            def resolve_channel(id: int) -> str:
                c = inter.guild.get_channel(id)
                return f'#{c.name}' if c else '#deleted-channel'
        else:
            def resolve_channel(id: int) -> str:
                return f'<#{id}>'

        transforms = {
            '@': resolve_member,
            '@!': resolve_member,
            '#': resolve_channel,
            '@&': resolve_role,
        }

        def repl(match: re.Match) -> str:
            type = match[1]
            id = int(match[2])
            transformed = transforms[type](id)
            return transformed

        result = re.sub(r'<(@[!&]?|#)([0-9]{15,20})>', repl, argument)
        if escape_markdown:
            result = disnake.utils.escape_markdown(result)
        elif remove_markdown:
            result = disnake.utils.remove_markdown(result)

        # Completely ensure no mentions escape:
        return disnake.utils.escape_mentions(result)

    return convert
