import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Ukiyo


class Nsfw(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @staticmethod
    async def check_marriage(
        command_name: str,
        ctx: Context,
        member: disnake.Member
    ):
        """
        Checks whether the ``author`` is married to the ``member`` or not.

        If one of them is married, it will return ``False``, if none of them are married or
        author is married to the member they're trying to do a nsfw command on, returns ``True``.

        Parameters
        ----------
            command_name: :class:`str`
                The name of the command invoked. This is used when sending the feedback
                letting the author know they cannot do that action with that member
                because of specific marriage reasons.

            ctx: :class:`.Context`
                The context object to get the author from.

            member: :class:`.Member`
                The member to compare the context's author with.

        Return
        ------
            ``True`` | ``False``
        """

        author_entry: utils.Marriage = await utils.Marriage.get(ctx.author.id)
        member_entry: utils.Marriage = await utils.Marriage.get(member.id)

        if (
            (author_entry is None or author_entry.married_to == 0) and
            (member_entry is None or member_entry.married_to == 0)
        ):
            return True

        elif author_entry.married_to != 0 and author_entry.married_to != member.id:
            mem = ctx.ukiyo.get_member(author_entry.married_to)
            await mem.send(
                f'`{utils.format_name(ctx.author)}` has tried to cheat on you.\n'
                f'They wanted to **{command_name}** {member.mention} ({utils.format_name(member)})'
            )
            await ctx.reply(
                f'{ctx.denial} You cannot **{command_name}** `{utils.format_name(member)}`, '
                f'you can only **{command_name}** {mem.mention}\nYour partner has been notified '
                'about your cheating behaviour.'
            )
            return False

        elif member_entry != 0 and member_entry.married_to != ctx.author.id:
            await ctx.reply(
                f'{ctx.denial} You cannot **{command_name}** that person '
                'because they are married with somebody else!'
            )
            return False

        return True

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
