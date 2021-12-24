import asyncio
import functools
from typing import Callable
from weakref import WeakValueDictionary

import disnake
from disnake.ext import commands

from .context import Context

__all__ = (
    'is_owner',
    'is_admin',
    'is_mod',
    'lock',
)


def _is_owner(ctx: Context, *, owner_only: bool = True):
    if ctx.author.id == 374622847672254466:
        return True
    elif 913310292505686046 in (role.id for role in ctx.author.roles):
        return True
    return False


def is_owner(*, owner_only: bool = True):
    """
    A special check for checking if the author has the owner role.

    If ``owner_only`` is set to `True` it will only check if the owner is the bot owner.
    """

    async def pred(ctx: Context):
        return _is_owner(ctx, owner_only=owner_only)
    return commands.check(pred)


def _is_admin_or_owner(ctx):
    res = _is_owner(ctx)
    if res is False:
        if 913315033134542889 in (role.id for role in ctx.author.roles):
            return True
    else:
        return res
    return False


def is_admin():
    """A special check for checking if the author is an admin."""

    async def pred(ctx: Context):
        return _is_admin_or_owner(ctx)
    return commands.check(pred)


def is_mod():
    """A special check for checking if the author is a moderator."""

    async def pred(ctx: Context):
        res = _is_admin_or_owner(ctx)
        if res is False:
            if 913315033684008971 in (role.id for role in ctx.author.roles):
                return True
        else:
            return res
        return False
    return commands.check(pred)


def lock() -> Callable | None:
    """
    Allows the user to only run one instance of the decorated command at a time.

    Subsequent calls to the command from the same author are ignored until the command has completed invocation.

    This decorator has to go before (below) the `command` decorator.
    """

    def wrap(func: Callable) -> Callable | None:
        func.__locks = WeakValueDictionary()

        @functools.wraps(func)
        async def inner(self: Callable, ctx: Context, *args, **kwargs) -> Callable | None:
            lock = func.__locks.setdefault(ctx.author.id, asyncio.Lock())
            if lock.locked():
                try:
                    await ctx.message.delete(delay=5.0)
                except disnake.HTTPException:
                    pass
                await ctx.reply(
                    'You are already using this command! Please wait until you complete it first.',
                    delete_after=5.0
                )
                return

            async with func.__locks.setdefault(ctx.author.id, asyncio.Lock()):
                return await func(self, ctx, *args, **kwargs)

        return inner

    return wrap
