import disnake
from disnake.ext import commands

from utils import (
    Context,
    Intro,
    create_intro,
    is_mod
)

from main import Ukiyo


class Intros(commands.Cog):
    """Intro related commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '🙌'

    @commands.command()
    async def intro(self, ctx: Context):
        """Create/Edit your intro."""

        await create_intro(ctx, self.bot)

    @commands.command(aliases=('wi',))
    async def whois(self, ctx: Context, *, member: disnake.Member = None):
        """Check somebody's intro!"""

        member = member or ctx.author
        data: Intro = await Intro.find_one({'_id': member.id})
        if data is None:
            if member.id == self.bot._owner_id:
                return await ctx.reply('User is mysterious.')
            if member == ctx.author:
                return await ctx.reply(
                    'You don\'t have an intro. Please contact a staff member to unverify you! This is a bug.'
                )
            else:
                return await ctx.reply(
                    f'`{member}` doesn\'t have an intro. Please contact a staff member to unverify them! This is a bug.'
                )

        em = disnake.Embed()
        em.set_author(name=member, icon_url=member.display_avatar)
        em.set_thumbnail(url=member.display_avatar)
        em.add_field(name='Name', value=data.name)
        em.add_field(name='Age', value=data.age)
        em.add_field(name='Gender', value=data.gender)
        em.add_field(name='Location', value=data.location, inline=False)
        em.add_field(name='DMs', value=data.dms)
        em.add_field(name='Looking', value=data.looking)
        em.add_field(name='Sexuality', value=data.sexuality)
        em.add_field(name='Relationship Status', value=data.status)
        em.add_field(name='Likes', value=data.likes)
        em.add_field(name='Dislikes', value=data.dislikes)
        em.set_footer(text=f'Requested by: {ctx.author}')
        await ctx.reply(embed=em)

    @commands.command(name='unverify')
    @is_mod()
    async def intro_unverify(self, ctx: Context, *, member: disnake.Member):
        """Unverify a member if their intro is a troll or if you
        consider that their intro is inappropriate."""

        if ctx.author.top_role <= member.top_role and ctx.author.id != self.bot._owner_id:
            return await ctx.reply('You cannot unverify somebody that is a higher or equal role than you.')

        guild = self.bot.get_guild(913310006814859334)
        unverified_role = guild.get_role(913329062347423775)
        data = await Intro.find_one({'_id': member.id})
        if data:
            await data.delete()
        await member.edit(roles=[unverified_role])
        await ctx.reply(f'`{member}` has been successfully unverified.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data = await Intro.find_one({'_id': member.id})
        if data:
            await data.delete()


def setup(bot: Ukiyo):
    bot.add_cog(Intros(bot))
