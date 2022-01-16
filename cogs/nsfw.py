import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Ukiyo


class Nsfw(commands.Cog):
    """Nsfw commands."""
    LIP_BITE = '<:lipbite:914193306416742411>'

    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @staticmethod
    async def check_marriage(
        action: str,
        ctx: Context,
        member: disnake.Member
    ) -> bool:
        """
        Checks whether the ``author`` is married to the ``member`` or not.

        If one of them is married, it will return ``False``, if none of them are married or
        author is married to the member they're trying to do a nsfw command on, returns ``True``.

        Parameters
        ----------
            action: :class:`str`
                The name of the action they are doing. This is used when sending the feedback
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
                f'They wanted to **{action}** {member.mention} ({utils.format_name(member)})'
            )
            await ctx.reply(
                f'{ctx.denial} You cannot **{action}** `{utils.format_name(member)}`, '
                f'you can only **{action}** {mem.mention}\nYour partner has been notified '
                'about your cheating behaviour.'
            )
            return False

        elif member_entry != 0 and member_entry.married_to != ctx.author.id:
            await ctx.reply(
                f'{ctx.denial} You cannot **{action}** that person '
                'because they are married with somebody else!'
            )
            return False

        return True

    async def check_channel(self, ctx: Context) -> bool:
        if ctx.author.id != self.bot._owner_id:
            if ctx.channel.id != 932226719593672714:
                await ctx.reply(f'{ctx.denial} This command can only be used in the nsfw channel!')
                return False

        return True

    async def get_link(self, endpoint: str) -> str | None:
        """Gets and returns a nsfw gif from https://purrbot.site/api/img/nsfw/`endpoint`/gif

        Parameters
        ----------
            endpoint: :class:`str`
                The nsfw endpoint from which to take the gif from.

        Return
        ------
            The link of the gif returned by the API or ``None``.
        """

        BASE_URL = 'https://purrbot.site/api/img/nsfw/{}/gif'
        data = await self.bot.session.get(BASE_URL.format(endpoint))
        js = await data.json()

        return js.get('link')

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

    @base_nsfw.command(name='fuck')
    async def nsfw_fuck(self, ctx: Context, *, member: disnake.Member):
        """Fuck someone.

        `member` **->** The member you wish to fuck.
        """

        if await self.check_channel(ctx) is True:
            if await self.check_marriage('fuck', ctx, member) is True:
                url = await self.get_link('fuck')
                em = disnake.Embed(color=utils.blurple)
                em.set_image(url)
                await ctx.send(
                    f'{ctx.author.mention} is fucking you {member.mention} {self.LIP_BITE}',
                    embed=em
                )

    @base_nsfw.command(name='cum')
    async def nsfw_cum(self, ctx: Context, *, member: disnake.Member):
        """Cum in/on someone.

        `member` **->** The member you wish to cum in/on.
        """

        if await self.check_channel(ctx) is True:
            if await self.check_marriage('cum in/on', ctx, member) is True:
                url = await self.get_link('cum')
                em = disnake.Embed(color=utils.blurple)
                em.set_image(url)
                await ctx.send(
                    f'{ctx.author.mention} is cumming in/on you {member.mention} {self.LIP_BITE}',
                    embed=em
                )

    @base_nsfw.command(name='blowjob', aliases=('bj',))
    async def nsfw_blowjob(self, ctx: Context, *, member: disnake.Member):
        """Give someone a blowjob.

        `member` **->** The member you wish to give a blowjob to.
        """

        if await self.check_channel(ctx) is True:
            if await self.check_marriage('give a blowjob to', ctx, member) is True:
                url = await self.get_link('blowjob')
                em = disnake.Embed(color=utils.blurple)
                em.set_image(url)
                await ctx.send(
                    f'{ctx.author.mention} is giving you a blowjob {member.mention} {self.LIP_BITE}',
                    embed=em
                )

    @base_nsfw.command(name='anal')
    async def nsfw_anal(self, ctx: Context, *, member: disnake.Member):
        """Have anal sex with someone.

        `member` **->** The member you wish to have anal with.
        """

        if await self.check_channel(ctx) is True:
            if await self.check_marriage('have anal sex with', ctx, member) is True:
                url = await self.get_link('anal')
                em = disnake.Embed(color=utils.blurple)
                em.set_image(url)
                await ctx.send(
                    f'{ctx.author.mention} is having anal sex with you {member.mention} {self.LIP_BITE}',
                    embed=em
                )

    @base_nsfw.command(name='pussylick', aliases=('lick',))
    async def nsfw_pussylick(self, ctx: Context, *, member: disnake.Member):
        """Lick someone's pussy.

        `member` **->** The member you wish to lick the pussy of.
        """

        if await self.check_channel(ctx) is True:
            if await self.check_marriage('pussy lick', ctx, member) is True:
                url = await self.get_link('pussylick')
                em = disnake.Embed(color=utils.blurple)
                em.set_image(url)
                await ctx.send(
                    f'{ctx.author.mention} is licking your pussy {member.mention} {self.LIP_BITE}',
                    embed=em
                )


def setup(bot: Ukiyo):
    bot.add_cog(Nsfw(bot))
