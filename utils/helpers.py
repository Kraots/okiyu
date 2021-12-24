from __future__ import annotations

import re
import string as st
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
    'inter_reraise',
    'check_string',
    'check_username',
    'run_in_executor',
    'clean_inter_content',
    'fail_embed',
    'format_amount',
    'check_channel',
)

allowed_letters = tuple(list(st.ascii_letters) + list(st.digits) + list(st.punctuation) + ['♡', ' '])
punctuations_and_digits = tuple(list(st.punctuation) + list(st.digits))
BAD_WORDS = Path('./bad_words.txt').read_text().splitlines()
converted = {
    '!': 'i',
    '@': 'a',
    '$': 's',
    '0': 'o',
    '1': 'i',
    '3': 'e'
}


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

    elif isinstance(error, commands.DisabledCommand):
        return await ctx.reply('This command is currently disabled!')

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        _missing_args = list(ctx.command.clean_params)
        missing_args = [f'`{arg}`' for arg in _missing_args[_missing_args.index(error.param.name):]]
        return await ctx.reply(
            f">>> {ctx.disagree} You are missing the following required arguments for this command:\n "
            f"\u2800\u2800{utils.human_join(missing_args, final='and')}\n\n"
            "If you don't know how to use this command, please type "
            f"`!help {ctx.command.qualified_name}` for more information on how to use it and what each "
            "argument means."
        )

    elif isinstance(error, commands.errors.MemberNotFound):
        await ctx.reply(f"> {ctx.disagree} Could not find member.")
        ctx.command.reset_cooldown(ctx)
        return

    elif isinstance(error, commands.errors.UserNotFound):
        await ctx.reply(f"> {ctx.disagree} Could not find user.")
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
        await ctx.bot._owner.send(
            content=f"**An error occurred with the command `{ctx.command}`, "
                    "here is the error:**",
            embed=em
        )
        await ctx.reply(f'> {ctx.disagree} An error occurred')


async def inter_reraise(bot: Ukiyo, inter, item: disnake.ui.Item, error):
    disagree = '<:disagree:913895999125196860>'
    get_error = "".join(format_exception(error, error, error.__traceback__))
    em = disnake.Embed(description=f'```py\n{get_error}\n```')
    await bot._owner.send(
        content="**An error occurred with a view for the user "
                f"`{inter.author}` (**{inter.author.id}**), "
                "here is the error:**\n"
                f"`View:` **{item.view.__class__}**\n"
                f"`Item Type:` **{item.type}**\n"
                f"`Item Row:` **{item.row or '0'}**",
        embed=em
    )
    fmt = f'> {disagree} An error occurred'
    if inter.response.is_done():
        await inter.followup.send(fmt, ephemeral=True)
    else:
        await inter.response.send_message(fmt, ephemeral=True)


def check_string(string: str) -> bool:
    """
    If the return type is of bool ``True`` then it means that the string contains a bad word, otherwise it's safe.
    """

    string = str(string).lower().replace(' ', '')
    for k, v in converted.items():
        string = string.replace(k, v)

    for pad in punctuations_and_digits:
        string = string.replace(pad, '')

    if any(w for w in BAD_WORDS if w in string):
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
    if count >= 4:
        if name is not None:
            if check_string(name) is True:
                count = 0
    if member is not None:
        if count < 4:
            kraots: utils.InvalidName = await utils.InvalidName.find_one({'_id': bot._owner_id})
            kraots.last_pos += 1
            await kraots.commit()
            new_nick = f'UnpingableName{kraots.last_pos}'
            await member.edit(nick=new_nick, reason='username not pingable, is a bad word or is too short')
            try:
                return await member.send(
                    'Your name has too few pingable letters in a row, '
                    f'is a bad word or is too short so I changed it to `{new_nick}`\n'
                    'You can always change your nickname by using the command `!nick new_nick` in <#913330644875104306>'
                )
            except disnake.Forbidden:
                return
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


def fail_embed(description: str) -> disnake.Embed:
    return disnake.Embed(title='Uh-oh!', color=utils.red, description=description)


def format_amount(num: str):
    return num \
        .replace(',', '') \
        .replace(' ', '') \
        .replace('.', '')


def check_channel(ctx):
    if ctx.channel.id not in (913330644875104306, 913332335473205308, 913445987102654474) \
            and ctx.author.id != 374622847672254466:
        return False
    return True
