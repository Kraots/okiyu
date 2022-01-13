from datetime import datetime

import disnake
from disnake.ext import commands

import utils
from utils import Context, Restrictions

from main import Ukiyo


class Confesscord(commands.Cog):
    """Commands related to the confesscord bot."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '🕵️‍♂️'

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.author.id == self.bot._owner_id:
            return True
        return any(r.id for r in ctx.author.roles if r in (913310292505686046, 913315033134542889, 913315033684008971))

    @commands.group(
        name='confesscord',
        aliases=('confessions', 'confess'),
        invoke_without_command=True,
        case_insensitive=True,
        hidden=True
    )
    async def base_command(self, ctx: Context):
        """Base command for all confesscord commands."""

        await ctx.send_help('Confesscord')

    @base_command.command(name='restrict')
    async def confesscord_restrict(self, ctx: Context, *, member: disnake.Member):
        """Restrict a member from using confesscord.

        `member` **->** The member you want to restrict from using confesscord.
        """

        if await ctx.check_perms(member) is False:
            return

        data: Restrictions = await Restrictions.get(member.id)
        if data is not None:
            return await ctx.reply(
                f'{ctx.denial} {member.mention} is already restricted from using confesscord.'
            )

        await Restrictions(
            id=member.id,
            restricted_by=ctx.author.id
        ).commit()

        await ctx.reply(f'Successfully restricted the access for {member.mention} from using confesscord.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CONFESSCORD RESTRICTION]',
            fields=[
                ('Member', f'{utils.format_name(member)} (`{member.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', utils.format_dt(datetime.now(), 'F')),
            ],
            view=utils.UrlButton('Jump!', ctx.message.jump_url)
        )

    @base_command.command(name='unrestrict')
    async def confesscord_unrestrict(self, ctx: Context, *, user: disnake.User):
        """Unrestrict an user from using confesscord.

        `user` **->** The user you want to give back access for using confesscord.
        """

        data: Restrictions = await Restrictions.get(user.id)
        if data is None:
            return await ctx.reply(f'{ctx.denial} {user.mention} is not restricted.')

        if data.restricted_by == self.bot._owner_id:
            if ctx.author.id != self.bot._owner_id:
                return await ctx.reply(
                    f'{ctx.denial} That user was restricted by my master, so no, you noob <:kek:913339277939720204>'
                )
        await data.delete()

        await ctx.reply(f'Successfully unrestricted {user.mention} from using confesscord.')
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[CONFESSCORD UNRESTRICTION]',
            fields=[
                ('User', f'{utils.format_name(user)} (`{user.id}`)'),
                ('By', f'{ctx.author.mention} (`{ctx.author.id}`)'),
                ('At', utils.format_dt(datetime.now(), 'F')),
            ],
            view=utils.UrlButton('Jump!', ctx.message.jump_url)
        )

    @base_command.command(name='restrictions')
    async def confesscord_restrictions(self, ctx: Context):
        """See all the currently restricted members."""

        entries = []
        to_append = '{} (`{}`) by {}'
        async for data in Restrictions.find():
            data: Restrictions
            restricted_by = ctx.ukiyo.get_member(data.restricted_by)
            mem = ctx.ukiyo.get_member(data.id)
            restricted_by = restricted_by.mention if restricted_by is not None else '**[LEFT]**'
            mem = mem.mention if mem is not None else '**[LEFT]**'
            entries.append(to_append.format(mem, data.id, restricted_by))

        paginator = utils.SimplePages(ctx, entries, compact=True)
        paginator.embed.title = 'Here are all the currently restricted members'
        await paginator.start(ref=True)


def setup(bot: Ukiyo):
    bot.add_cog(Confesscord(bot))
