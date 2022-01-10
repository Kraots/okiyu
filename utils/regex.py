import re

__all__ = (
    'INVITE_REGEX',
    'LANGUAGE_REGEX',
    'TOKEN_REGEX',
)

INVITE_REGEX = re.compile(
    r"(?:discord(?:[\.,]|dot)gg|"  # Could be discord.gg/
    r"discord(?:[\.,]|dot)com(?:\/|slash)invite|"  # or discord.com/invite/
    r"discordapp(?:[\.,]|dot)com(?:\/|slash)invite|"  # or discordapp.com/invite/
    r"discord(?:[\.,]|dot)me|"  # or discord.me
    r"discord(?:[\.,]|dot)io"  # or discord.io.
    r")(?:[\/]|slash)"  # / or 'slash'
    r"([a-zA-Z0-9\-]+)",  # the invite code itself
    flags=re.IGNORECASE,
)
LANGUAGE_REGEX = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
TOKEN_REGEX = re.compile(r'[a-zA-Z0-9_-]{23,28}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27}')
