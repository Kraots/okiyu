import disnake
from disnake.ext import commands

import utils
from utils import Intro, Context

from main import Ukiyo


class Intros(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @commands.command()
    async def intro(self, ctx: Context):
        """Create/Edit your intro."""

        await utils.create_intro(ctx, self.bot)

    @commands.command(aliases=('wi',))
    async def whois(self, ctx: Context, *, member: disnake.Member = None):
        """Check somebody's intro!"""

        member = member or ctx.author
        data: Intro = await Intro.find_one({'_id': member.id})
        if data is None:
            if member == ctx.author:
                return await ctx.reply(
                    'You don\'t have an intro. Please contact a staff member to unverify you! This is a bug.'
                )
            else:
                return await ctx.reply(
                    f'`{member}` doesn\'t have an intro. Please contact a staff member to unverify them! This is a bug.'
                )

        em = disnake.Embed()
        em.set_thumbnail(url=ctx.author.display_avatar)
        em.add_field(name='Name', value=data.name)
        em.add_field(name='Age', value=data.age)
        em.add_field(name='Gender', value=data.gender)
        em.add_field(name='Location', value=data.location)
        em.add_field(name='DMs', value=data.dms)
        em.add_field(name='Looking', value=data.looking)
        em.add_field(name='Sexuality', value=data.sexuality)
        em.add_field(name='Relationship Status', value=data.status)
        em.add_field(name='Likes', value=data.likes)
        em.add_field(name='Dislikes', value=data.dislikes)
        em.set_footer(text=f'Requested by: {ctx.author}')
        await ctx.reply(embed=em)


def setup(bot: Ukiyo):
    bot.add_cog(Intros(bot))
