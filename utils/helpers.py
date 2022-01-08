from __future__ import annotations

import re
import base64
import asyncio
import binascii
import functools
import string as st
from pathlib import Path
from typing import Callable
from datetime import datetime

import disnake
from disnake.ext import commands

import utils

__all__ = (
    'time_phaser',
    'clean_code',
    'check_profanity',
    'check_string',
    'check_username',
    'run_in_executor',
    'clean_inter_content',
    'fail_embed',
    'format_amount',
    'escape_markdown',
    'remove_markdown',
    'FIRST_JANUARY_1970',
    'CooldownByContent',
    'validate_token',
)

FIRST_JANUARY_1970 = datetime(1970, 1, 1, 0, 0, 0, 0)
ALLOWED_LETTERS = tuple(list(st.ascii_letters) + list(st.digits) + list(st.punctuation) + ['♡', ' '])
BAD_WORDS = Path('./bad_words.txt').read_text().splitlines()
EDGE_CASES = {
    '@': 'a',
    '0': 'o',
    '1': 'i',
    '$': 's',
    '!': 'i',
    '9': 'g',
    '()': 'o',
}
EDGE_TABLE = str.maketrans(EDGE_CASES)
PUNCTUATIONS_AND_DIGITS = tuple(list(st.punctuation) + list(st.digits))
PAD_TABLE = str.maketrans({k: '' for k in PUNCTUATIONS_AND_DIGITS})


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


def check_profanity(string: str, *, bad_words: list = None) -> bool:
    """
    If the return type is of bool ``True`` then it means that the
    string contains a bad word, otherwise ``False`` if it's safe.

    Parameters
    ----------
        string: :class:`str`
            The string to check if it contains a bad word.

        bad_words: :class:`list`
            A list of the bad words to check for. If ``None``, will use the hardcoded ones from bad_words.txt

    Return
    ------
        True | False
    """

    bad_words = bad_words or BAD_WORDS
    string = str(string).lower().replace(' ', '').replace('\n', '')
    res = any(w for w in bad_words if w in string)

    if res is False:
        string = string.translate(EDGE_TABLE)  # Replace each edge character to its corresponding letter.
        res = any(w for w in bad_words if w in string)

        if res is False:
            string = string.translate(PAD_TABLE)  # Remove every punctuation and digit character.
            res = any(w for w in bad_words if w in string)

    return res


def check_string(string: str, *, limit: str = 4) -> bool:
    """
    If the return type of bool is ``True`` then it means that the word has
    less allowed characters in a row than the limit, otherwise ``False``
    if the string meets the required limit.

    Parameters
    ----------
        string: :class:`str`
            The string to check if it has enough allowed characters in a row.

        limit: :class:`int`
            The limit for which to check the lenght of the allowed letters in a row within the string.
            Defaults to 4.

    Return
    ------
        True | False
    """

    count = 0
    for letter in string:
        if count < limit:
            if letter not in ALLOWED_LETTERS:
                count = 0
            else:
                count += 1
        else:
            break

    return count < limit


async def check_username(member: disnake.Member):
    """
    Check the ``member``'s display name, if all the checks pass,
    he's ignored, otherwise, his nickname gets changed.

    Parameters
    ----------
        member: :class:`disnake.Member`
            The member to check if their display name is shorter
            than ``limit`` and if they have any bad word in it.
    """

    if member.id == 374622847672254466 or member.bot:
        return
    name = member.display_name.lower()
    res = check_string(name) or check_profanity(name)
    if res is False:
        return

    kraots: utils.InvalidName = await utils.InvalidName.get(374622847672254466)
    kraots.last_pos += 1
    await kraots.commit()
    new_nick = f'UnpingableName{kraots.last_pos}'
    await member.edit(nick=new_nick, reason='username not pingable, is a bad word or is too short')
    try:
        return await member.send(
            'Your name has too few pingable letters in a row, '
            f'is a bad word or is too short (minimum is **4**) so I changed it to `{new_nick}`\n'
            'You can always change your nickname by using the command `!nick new_nick` in <#913330644875104306>'
        )
    except disnake.Forbidden:
        return


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


def format_amount(num: str) -> str:
    return num \
        .replace(',', '') \
        .replace(' ', '') \
        .replace('.', '')


def escape_markdown(text: str) -> str:
    r"""Escapes the markdown from the text. That means **hello** becomes \\*\\*hello\\*\\*

    Parameters
    ----------
        text: :class:`str`
            The text to escape the markdown from.

    Return
    ------
        :class:`str`
            The new string with the escaped markdown.
    """

    return disnake.utils.escape_markdown(text)


def remove_markdown(text: str) -> str:
    r"""Removes the markdown from the text. That means **hello** becomes hello

    Parameters
    ----------
        text: :class:`str`
            The text to remove the markdown from.

    Return
    ------
        :class:`str`
            The new string with the removed markdown.
    """

    return disnake.utils.remove_markdown(text)


class CooldownByContent(commands.CooldownMapping):
    def _bucket_key(ctx, message):
        return (message.channel.id, message.content.lower())


def validate_token(token):
    try:
        # Just check if the first part validates as a user ID
        (user_id, _, _) = token.split('.')
        user_id = int(base64.b64decode(user_id, validate=True))
    except (ValueError, binascii.Error):
        return False
    else:
        return True
