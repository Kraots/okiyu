from disnake.ext import commands

import utils


def _is_owner(ctx: utils.Context, *, owner_only: bool = True):
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

    async def pred(ctx: utils.Context):
        return await _is_owner(ctx, owner_only=owner_only)
    return commands.check(pred)


def is_mod():
    """A special check for checking if the author is a moderator."""

    async def pred(ctx: utils.Context):
        res = await _is_owner(ctx)
        if res is False:
            if 913315033684008971 in (role.id for role in ctx.author.id):
                return True
        else:
            return res
        return False
    return commands.check(pred)


def is_admin():
    """A special check for checking if the author is an admin."""

    async def pred(ctx: utils.Context):
        res = await _is_owner(ctx)
        if res is False:
            if 913315033134542889 in (role.id for role in ctx.author.id):
                return True
        else:
            return res
        return False
    return commands.check(pred)
